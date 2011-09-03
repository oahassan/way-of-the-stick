from random import choice
import copy
import pygame
import gamestate
import physics
import animationexplorer
from mathfuncs import sign
from player import Player, PlayerTypes
from stick import LineNames
from enumerations import PlayerStates, CommandDurations, InputActionTypes, AttackTypes, ApproachTypes
from playerutils import ActionFactory, Transition, Action, Attack
from simulation import HitboxBuilder
from playerconstants import *
import st_versusmode

class Bot(Player):
    """an algorithm controlled player"""
    
    def __init__(self, position):
        Player.__init__(self, position)
        self.actions = {}
        self.player_type = PlayerTypes.BOT
        
        #a dictionary mapping attacks to a list of rects for each frame
        self.attack_prediction_engine = None
        self.attack_landed = False
        self.pre_attack_state = None
        self.approach_selected = False
        self.approach_engine = None
        
    def load_moveset(self, moveset):
        self.approach_engine = ApproachEngine()
        self.approach_engine.init()
        self.moveset = moveset
        
        factory = ActionFactory(self)
        
        #load rest animation
        stand_animation = moveset.movement_animations[PlayerStates.STANDING]
        stand_action = factory.create_stand(stand_animation)
        self.actions[PlayerStates.STANDING] = stand_action
        
        #load walk animation
        walk_animation = moveset.movement_animations[PlayerStates.WALKING]
        walk_action = factory.create_walk(walk_animation)
        self.actions[PlayerStates.WALKING] = walk_action
        
        #load run animation
        run_animation = moveset.movement_animations[PlayerStates.RUNNING]
        run_action = factory.create_run(run_animation)
        self.actions[PlayerStates.RUNNING] = run_action
        
        #load jump animation
        jump_animation = moveset.movement_animations[PlayerStates.JUMPING]
        jump_action = factory.create_jump(jump_animation)
        self.actions[PlayerStates.JUMPING] = jump_action
        
        #load land animation
        land_animation = moveset.movement_animations[PlayerStates.LANDING]
        self.actions[PlayerStates.LANDING] = factory.create_land(land_animation)
        
        #load float animation
        float_animation = moveset.movement_animations[PlayerStates.FLOATING]
        self.actions[PlayerStates.FLOATING] = factory.create_float(float_animation)
        
        #load stunned action
        self.actions[PlayerStates.STUNNED] = factory.create_stun()
        
        #load transition action
        self.actions[PlayerStates.TRANSITION] = Transition()
                
        #load crouch animation
        crouch_animation = moveset.movement_animations[PlayerStates.CROUCHING]
        crouch_action = factory.create_crouch(crouch_animation)
        self.actions[PlayerStates.CROUCHING] = crouch_action
        
        self.actions[PlayerStates.ATTACKING] = []
        
        #load attack actions
        for attack_name in moveset.get_attacks():
            attack_action = None
            if InputActionTypes.JUMP in moveset.attack_key_combinations[attack_name]:
                attack_action = factory.create_jump_attack(
                    moveset.get_attack_type(attack_name),
                    moveset.attack_animations[attack_name],
                    self.model
                )
            else:
                attack_action = factory.create_attack(
                    moveset.get_attack_type(attack_name),
                    moveset.attack_animations[attack_name],
                    self.model
                )
                
            self.actions[PlayerStates.ATTACKING].append(attack_action)
        
        self.actions[PlayerStates.STANDING].set_player_state(self)
        self.attack_prediction_engine = AttackPredictionEngine(
            200, 
            2000, 
            self
        )
    
    def get_foot_actions(self):
        return [
            self.actions[PlayerStates.WALKING],
            self.actions[PlayerStates.RUNNING]
        ]
    
    def handle_attack_end(self):
        """update graph weights and attack data"""
        current_attack_name = self.current_attack.right_animation.name
        if self.attack_landed == False:
            if not self.attack_prediction_engine.last_attack_name is None:
                self.attack_prediction_engine.reduce_attack_weight(
                    self.attack_prediction_engine.combo_graph,
                    self.attack_prediction_engine.last_attack_name,
                    current_attack_name
                )
                
            elif self.attack_prediction_engine.pre_attack_state != None:
                self.attack_prediction_engine.reduce_attack_weight(
                    self.attack_prediction_engine.initial_attack_graph,
                    self.attack_prediction_engine.pre_attack_state,
                    current_attack_name
                )
            
            self.attack_prediction_engine.last_attack_name = None
        
        else:
            if not self.attack_prediction_engine.last_attack_name is None:
                self.attack_prediction_engine.increase_attack_weight(
                    self.attack_prediction_engine.combo_graph,
                    self.attack_prediction_engine.last_attack_name,
                    current_attack_name
                )
                
            elif self.attack_prediction_engine.pre_attack_state != None:
                self.attack_prediction_engine.increase_attack_weight(
                    self.attack_prediction_engine.initial_attack_graph,
                    self.attack_prediction_engine.pre_attack_state,
                    current_attack_name
                )
            
            self.attack_prediction_engine.last_attack_name = current_attack_name
        
        self.pre_attack_state = None
        self.attack_landed = False
        self.current_attack = None
    
    def get_attack_actions(self):
        return self.actions[PlayerStates.ATTACKING]
    
    def update_attack_data(self):
        """indicate that the attack connected"""
        self.attack_landed = True
    
    def handle_events(self, enemy, time_passed):
        self.set_approach(enemy)
        
        if self.handle_input_events:
            self.set_action(enemy)
        
        Player.handle_events(self, time_passed)
    
    def set_approach(self, enemy):
        if (self.action.action_state == PlayerStates.ATTACKING or
        self.action.action_state == PlayerStates.STUNNED or
        self.action.action_state == PlayerStates.LANDING):
            self.approach_selected = False
        
        if self.approach_selected == False:
            self.approach_engine.set_move_towards_enemy(self, enemy)
    
    def get_direction(self, enemy):
        direction = PlayerStates.FACING_LEFT
        
        if enemy.model.center()[0] > self.model.center()[0]:
            direction = PlayerStates.FACING_RIGHT
        
        return direction
    
    def set_action(self, enemy):
        
        attack = None
        
        if (self.action.action_state != PlayerStates.ATTACKING
        and self.action.action_state != PlayerStates.STUNNED):
            attack = self.attack_prediction_engine.get_in_range_attack(enemy)
        
        next_action = None
        
        if attack != None:
            if attack.test_state_change(self):
                next_action = attack
                self.current_attack = attack
        elif self.get_player_state() != PlayerStates.TRANSITION:
            next_action = self.move_towards_enemy(self)
        
        direction = self.get_direction(enemy)
        
        if next_action != None:
            if not self.is_aerial():
                self.direction = direction
                next_action.direction = direction
            else:
                next_action.direction = self.direction
        else:
            if (self.action.action_state != PlayerStates.ATTACKING 
            and self.action.direction != direction):
                next_action = self.action
                
                if not self.is_aerial():
                    self.action.direction = direction
        
        if (next_action != None
        and next_action != self.action):
            self.transition(next_action)
    
    def move_towards_enemy(self, enemy):
        x_distance = abs(enemy.model.position[0] - self.model.position[0])
        y_distance = enemy.model.position[1] - self.model.position[1]
        
        movement = None
        
        if x_distance > 150:
            action = self.actions[PlayerStates.RUNNING]
            
            if self.action != action:
                movement = action
                self.dash_timer = 0
        
        elif x_distance <= 150:
            action = self.actions[PlayerStates.WALKING]
            
            if self.action != action:
                movement = action
        
        if (((self.action.action_state == PlayerStates.STANDING) or
            (self.action.action_state == PlayerStates.WALKING) or
            (self.action.action_state == PlayerStates.RUNNING)) and
            (y_distance < -20) and
            (self.model.velocity[0] > 0)):
            movement = self.actions[PlayerStates.JUMPING]
        
        #jumping player ai
        #if self.model.velocity[0] != 0:
        #    movement = self.actions[PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(self))):
            return movement
        else:
            return None
    
    def get_in_range_attack(self, enemy):
        in_range_attacks = []
        
        if self.is_aerial():
            in_range_attacks = [
                attack 
                for attack in self.actions[PlayerStates.ATTACKING] 
                if self.aerial_attack_in_range(attack, enemy)
            ]
        else:
            in_range_attacks = [
                attack 
                for attack in self.actions[PlayerStates.ATTACKING] 
                if self.attack_in_range(attack, enemy)
            ]
        
        if len(in_range_attacks) > 0:
            return choice(in_range_attacks)
        else:
            return None

class ApproachEngine():
    def __init__(self):
        self.approach_functions = {}
        self.approach_timing_functions = {}
    
    def init(self):
        self.approach_functions[ApproachTypes.RUN] = self.run
        self.approach_functions[ApproachTypes.WALK] = self.walk
        self.approach_functions[ApproachTypes.STAND] = self.stand
        self.approach_functions[ApproachTypes.RUN_JUMP] = self.run_jump
        self.approach_functions[ApproachTypes.WALK_JUMP] = self.walk_jump
        self.approach_functions[ApproachTypes.STAND_JUMP] = self.stand_jump
        self.approach_timing_functions[ApproachTypes.RUN] = self.get_run_intersection
        self.approach_timing_functions[ApproachTypes.WALK] = self.get_walk_intersection
        self.approach_timing_functions[ApproachTypes.STAND] = self.get_stand_intersection
        self.approach_timing_functions[ApproachTypes.RUN_JUMP] = self.get_run_jump_intersection
        self.approach_timing_functions[ApproachTypes.WALK_JUMP] = self.get_walk_jump_intersection
        self.approach_timing_functions[ApproachTypes.STAND_JUMP] = self.get_stand_jump_intersection
    
    def get_run_intersection(self, player, enemy):
        
        return self.get_x_intersection(player, player.run_speed, enemy)
    
    def get_walk_intersection(self, player, enemy):
        
        return self.get_x_intersection(player, player.walk_speed, enemy)
    
    def get_stand_intersection(self, player, enemy):
        
        return self.get_x_intersection(player, 0, enemy)
    
    def get_run_jump_intersection(self, player, enemy):
        return self.get_x_y_intersection(player, enemy)
        
    def get_walk_jump_intersection(self, player, enemy):
        return self.get_x_y_intersection(player, enemy)
    
    def get_stand_jump_intersection(self, player, enemy):
        return self.get_x_y_intersection(player, enemy)
    
    def get_x_intersection(self, player, player_v_x, enemy):
        player_x = player.model.position[0]
        player_width = player.model.width
        enemy_x = enemy.model.position[0]
        enemy_v_x = enemy.model.velocity[0]
        
        if player_x > enemy_x:
            player_v_x = -1 * player_v_x
        
        does_intersect = False
        
        for delta_t in range(APPROACH_PREDICTION_DELTA, APPROACH_PREDICTION_INTERVAL, APPROACH_PREDICTION_DELTA):
            if abs((player_x + (player_v_x*delta_t)) - (enemy_x + (enemy_v_x*delta_t))) < (1.5*player_width):
                does_intersect = True
                break
        
        return does_intersect
    
    def get_x_y_intersection(self, player, enemy):
        player_x = player.model.position[0]
        player_v_x = player.model.velocity[0]
        player_width = player.model.width
        enemy_x = enemy.model.position[0]
        enemy_v_x = enemy.model.velocity[0]
        
        if player_x > enemy_x:
            player_v_x = -1 * player_v_x
        
        does_intersect = False
        
        for delta_t in range(APPROACH_PREDICTION_DELTA, APPROACH_PREDICTION_INTERVAL, APPROACH_PREDICTION_DELTA):
            if abs((player_x + (player_v_x*delta_t)) - (enemy_x + (enemy_v_x*delta_t))) < (1.5*player_width) and self.get_y_intersection_at_t(player, enemy, delta_t):
                does_intersect = True
                break
        
        return does_intersect
    
    def get_y_intersection_at_t(self, player, enemy, delta_t):
        player_y = player.model.position[1]
        player_v_y = player.model.velocity[1]
        player_gravity = player.model.gravity
        
        enemy_y = enemy.model.position[1]
        enemy_v_y = enemy.model.velocity[1]
        enemy_gravity = enemy.model.gravity
        
        return abs((player_y + (player_v_y*delta_t) + (player_gravity*(delta_t**2))) - (enemy_y + (enemy_v_y*delta_t) + (enemy_gravity*(delta_t**2)))) < player.model.height
    
    def get_y_intersection(self, player, enemy):
        player_y = player.model.position[1]
        player_v_y = player.model.velocity[1]
        player_gravity = player.model.gravity
        
        enemy_y = enemy.model.position[1]
        enemy_v_y = enemy.model.velocity[1]
        enemy_gravity = enemy.model.gravity
        
        does_intersect = False
        
        for delta_t in range(APPROACH_PREDICTION_DELTA, APPROACH_PREDICTION_INTERVAL, APPROACH_PREDICTION_DELTA):
            if abs((player_y + (player_v_y*delta_t) + (player_gravity*(delta_t**2))) - (enemy_y + (enemy_v_y*delta_t) + (enemy_gravity*(delta_t**2)))) < player.model.height:
                does_intersect = True
                break
        
        return does_intersect
    
    def run(self, player):
        
        movement = None
        
        if ((player.action.action_state == PlayerStates.STANDING) or
            (player.action.action_state == PlayerStates.WALKING)):
            movement = player.actions[PlayerStates.RUNNING]
            player.dash_timer = 0
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def run_jump(self, player):
        
        movement = None
        
        if ((player.action.action_state == PlayerStates.STANDING) or
            (player.action.action_state == PlayerStates.WALKING)):
            movement = player.actions[PlayerStates.RUNNING]
            player.dash_timer = 0
            
        elif (player.action.action_state == PlayerStates.RUNNING and
        abs(player.model.velocity[0]) >= player.run_speed - player.model.friction):
            movement = player.actions[PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def walk(self, player):
        movement = None
        
        if ((player.action.action_state == PlayerStates.STANDING) or
            (player.action.action_state == PlayerStates.RUNNING)):
            movement = player.actions[PlayerStates.WALKING]
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def walk_jump(self, player):
        movement = None
        
        if ((player.action.action_state == PlayerStates.STANDING) or
            (player.action.action_state == PlayerStates.RUNNING)):
            movement = player.actions[PlayerStates.WALKING]
            
        elif (player.action.action_state == PlayerStates.WALKING and
        abs(player.model.velocity[0]) >= player.walk_speed - player.model.friction):
            movement = player.actions[PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def stand_jump(self, player):
        movement = None
        
        if ((player.action.action_state == PlayerStates.WALKING) or
            (player.action.action_state == PlayerStates.RUNNING)):
            movement = player.actions[PlayerStates.STANDING]
            
        elif (player.action.action_state == PlayerStates.STANDING and 
        player.model.velocity[0] == 0):
            movement = player.actions[PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def stand(self, player):
        movement = None
        
        if ((player.action.action_state == PlayerStates.WALKING) or
            (player.action.action_state == PlayerStates.RUNNING)):
            movement = player.actions[PlayerStates.STANDING]
        
        if ((movement != None) and
            (movement.test_state_change(player))):
            return movement
        else:
            return None
    
    def set_move_towards_enemy(self, player, enemy):
        player.approach_selected = True
        
        approach_types = [
            approach_type
            for approach_type, approach_timing_function
            in self.approach_timing_functions.iteritems()
            if approach_timing_function(player, enemy)
        ]
        
        if len(approach_types) == 0:
            player.move_towards_enemy = choice([self.run, self.run_jump, self.walk, self.walk_jump])
        else:
            player.move_towards_enemy = choice([
                self.approach_functions[approach_type]
                for approach_type in approach_types
            ])


class AttackPredictionEngine():
    def __init__(self, timestep, prediction_time_frame, player):
        self.timestep = timestep
        self.prediction_time_frame = prediction_time_frame
        self.player = player
        self.attack_prediction_data = {}
        self.combo_graph = None
        self.initial_attack_graph = None
        self.hitbox_builder = HitboxBuilder()
        self.load_data()
        self.last_attack_name = None
        self.pre_attack_state = None
        self.combo_weight_threshold = .9
        self.attack_weight_increment = .1
        self.last_enemy_rect = None
    
    def load_data(self):
        attack_prediction_data_factory = AttackPredictionDataFactory(self.timestep)
        
        for attack in self.player.actions[PlayerStates.ATTACKING]:
            
            attack_prediction_data = attack_prediction_data_factory.create_attack_prediction_data(
                self.player, 
                attack
            )
            
            if attack_prediction_data != None:
                self.attack_prediction_data[attack.right_animation.name] = attack_prediction_data
        
        graph_factory = AIGraphFactory()
        self.combo_graph = graph_factory.create_combo_graph(self.player)
        self.initial_attack_graph = graph_factory.create_initial_attack_graph(
            self.player
        )
        ##debug code for validating the combo_graph
        #print ('\n'.join([
        #        str(
        #            (name, [edge.end_node.name for edge in node.edges])
        #        )
        #        for name, node in self.combo_graph.iteritems()
        #    ])
        #)
    
    def reduce_attack_weight(self, graph, node_name, attack_name):
        node = graph[node_name]
        edge = node.edge_dictionary[attack_name]
        
        edge.weight = max(0, edge.weight - self.attack_weight_increment)
        
    def increase_attack_weight(self, graph, node_name, attack_name):
        node = graph[node_name]
        edge = node.edge_dictionary[attack_name]
        
        edge.weight = min(1, edge.weight + self.attack_weight_increment)
    
    def get_in_range_attack(self, enemy):
        in_range_attacks = []
        player = self.player
        
        if self.last_enemy_rect is None:
            self.last_enemy_rect = pygame.Rect(
                *enemy.model.get_enclosing_rect()
            )
        
        enemy_rects = self.get_enemy_rects(enemy)
        
        self.last_enemy_rect = enemy_rects[0]
        
        if player.is_aerial():
            in_range_attacks = [
                attack 
                for attack in player.actions[PlayerStates.ATTACKING] 
                if attack.right_animation.name in self.attack_prediction_data
                and attack.is_jump_attack
                and self.aerial_attack_in_range(attack, enemy, enemy_rects)
            ]
            pass
        else:
            in_range_attacks = [
                attack 
                for attack in player.actions[PlayerStates.ATTACKING] 
                if attack.right_animation.name in self.attack_prediction_data
                and self.attack_in_range(attack, enemy, enemy_rects)
            ]
        
        if len(in_range_attacks) > 0:
            if self.last_attack_name is None:            
                player_state = self.player.get_player_state()
                
                if player_state in self.initial_attack_graph:
                    self.pre_attack_state = player_state
                    
                    return self.get_weighted_attack(
                        self.initial_attack_graph, 
                        player_state, 
                        in_range_attacks
                    )
                    
                else:
                    return choice(in_range_attacks)
                
            else:
                
                return self.get_weighted_attack(
                    self.combo_graph, 
                    self.last_attack_name,
                    in_range_attacks
                )
                
        else:
            return None
    
    def get_weighted_attack(self, graph, node_name, in_range_attacks):
        weighted_attacks = [
            node.data
            for node
            in graph[node_name].get_neighbors(
                self.combo_weight_threshold
            )
        ]
        
        if len(weighted_attacks) == 0:
            graph[node_name].reset_edge_weights()
            
            weighted_attacks = [
                node.data
                for node
                in graph[node_name].get_neighbors(
                    self.combo_weight_threshold
                )
            ]
        
        attack_list = [
            attack 
            for attack in in_range_attacks 
            if attack in weighted_attacks
        ]
        
        if len(attack_list) == 0:
            return None
        else:
            return choice(attack_list)
    
    def get_enemy_rects(self, enemy):
        timestep = self.timestep
        
        return_rects = [pygame.Rect(enemy.model.get_enclosing_rect())]
        
        prediction_time_frame = self.prediction_time_frame
        new_rect_position = return_rects[-1].topleft
        old_rect_position = return_rects[-1].topleft
        rect_velocity = enemy.model.velocity
        direction = enemy.direction
        width_delta = return_rects[-1].width - self.last_enemy_rect.width
        height_delta = return_rects[-1].height - self.last_enemy_rect.height
        
        while prediction_time_frame > 0:
            last_rect = return_rects[-1]
            
            x_delta = timestep * rect_velocity[0]
            y_delta = (
                (.5*enemy.model.gravity*(timestep**2)) + 
                (timestep * rect_velocity[1])
            )
            
            new_rect_position = (
                old_rect_position[0] + x_delta,
                old_rect_position[1] + y_delta
            )
            
            if ((new_rect_position[1] + last_rect.height) > 
            gamestate.stage.ground.position[1]):
                new_rect_position = (
                    new_rect_position[0],
                    gamestate.stage.ground.position[1] - last_rect.height
                )
            
            new_rect = pygame.Rect(
                new_rect_position, (last_rect.width, last_rect.height)
            )
            
            #Predict changes in the size of the hitbox
            if direction == PlayerStates.FACING_LEFT:
                new_rect.topleft = (
                    new_rect_position[0] + width_delta,
                    new_rect_position[1] + height_delta
                )
            
            new_rect.width = max(1, new_rect.width + width_delta)
            new_rect.height = max(1, new_rect.height + height_delta)
            
            return_rects.append(
                new_rect
            )
            
            # Set the new aerial velocity
            if ((last_rect.topleft[1] + last_rect.height) < 
            gamestate.stage.ground.position[1]):
                rect_velocity = (
                    rect_velocity[0],
                    rect_velocity[1] + (timestep * enemy.model.gravity)
                )
            else:
                rect_velocity = (
                    rect_velocity[0],
                    0
                )
            
            prediction_time_frame -= self.timestep
        
        return return_rects
    
    def get_aerial_attack_rects(self, attack):
        timestep = self.timestep
        player = self.player
        
        attack_rects = self.attack_prediction_data[attack.right_animation.name].attack_rects
        
        player_rect = pygame.Rect(*player.model.get_enclosing_rect())
        initial_position = (player.model.position[0], player.model.position[1])
        direction = player.direction
        
        if direction == PlayerStates.FACING_LEFT:
            initial_position = (player.model.position[0] - player_rect.width, player.model.position[1])
        
        return_rects = [
            pygame.Rect(
                initial_position, 
                (attack_rects[0].width, attack_rects[0].height)
            )
        ]
        
        attack_rect_index = 1
        prediction_time_frame = self.prediction_time_frame
        new_rect_position = initial_position
        old_rect_position = initial_position
        rect_velocity = player.model.velocity
        
        while (prediction_time_frame > 0 
        and attack_rect_index < len(attack_rects)):
            last_rect = return_rects[-1]
            
            x_delta = timestep * rect_velocity[0]
            y_delta = (
                (.5*player.model.gravity*(timestep**2)) + 
                (timestep * rect_velocity[1])
            )
            
            if direction == PlayerStates.FACING_LEFT:
                new_rect_position = (
                    old_rect_position[0] + x_delta - player_rect.width,
                    old_rect_position[1] + y_delta #+ player_rect.height
                )

            else:
                new_rect_position = (
                    old_rect_position[0] + x_delta,
                    old_rect_position[1] + y_delta
                )
            
            new_rect = pygame.Rect(
                new_rect_position, 
                (
                    attack_rects[attack_rect_index].width, 
                    attack_rects[attack_rect_index].height
                )
            )
            
            if ((new_rect.topleft[1] + new_rect.height) > 
            gamestate.stage.ground.position[1]):
                new_rect_position = (
                    new_rect_position[0],
                    gamestate.stage.ground.position[1] - last_rect.height
                )
                new_rect.topleft = new_rect_position
            
            return_rects.append(new_rect)
            
            #Update Rect Velocity
            if ((last_rect.topleft[1] + last_rect.height) < 
            gamestate.stage.ground.position[1]):
                rect_velocity = (
                    rect_velocity[0],
                    rect_velocity[1] + (timestep * player.model.gravity)
                )
            else:
                rect_velocity = (
                    rect_velocity[0],
                    0
                )
            
            prediction_time_frame -= self.timestep
            attack_rect_index += 1
        
        ##debug code
        #for attack_rect in return_rects:
        #    rect_surface = pygame.Surface(
        #        (attack_rect.width, attack_rect.height)
        #   )
        #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
        #    pygame.draw.rect(rect_surface, (0,255,0), drawing_rect, 2)
        #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
        #        attack_rect.topleft, 
        #        rect_surface
        #   )
        
        return return_rects
    
    def aerial_attack_in_range(self, attack, enemy, enemy_rects):
        
        attack_rects = self.get_aerial_attack_rects(attack)
        
        collision_index = self.get_max_collsion_index(attack_rects, enemy_rects)
        
        in_range = False
        
        if collision_index > -1:
            
            enemy_hitboxes = self.get_enemy_hitboxes_for_rect(
                enemy,
                enemy_rects[collision_index]
            )
            
            attack_hitboxes = self.get_aerial_attack_hitboxes(
                attack, 
                collision_index,
                attack_rects[collision_index]
            )
            
            in_range = self.get_hitbox_collision_indicator(
                attack_hitboxes,
                enemy_hitboxes
            )
            
            ##debugging code
            #for attack_rect in enemy_hitboxes:
            #    rect_surface = pygame.Surface(
            #        (attack_rect.width, attack_rect.height)
            #    )
            #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #    pygame.draw.rect(rect_surface, (255,0,0), drawing_rect, 2)
            #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        attack_rect.topleft, 
            #       rect_surface
            #    )
            # 
            ##debugging code
            #for attack_rect in attack_hitboxes:
            #    rect_surface = pygame.Surface(
            #       (attack_rect.width, attack_rect.height)
            #    )
            #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #    pygame.draw.rect(rect_surface, (255,0,0), drawing_rect, 2)
            #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        attack_rect.topleft, 
            #        rect_surface
            #    )
            
        return in_range
    
    def get_aerial_attack_hitboxes(self, attack, collision_index, attack_rect):
        animation_name = attack.right_animation.name
        animation_prediction_data = self.attack_prediction_data[animation_name]
        attack_hitboxes = animation_prediction_data.attack_hitboxes[collision_index]
        
        top_left_position = self.attack_prediction_data[attack.right_animation.name].attack_rects[0].topleft
        
        for hitbox in attack_hitboxes:
            if top_left_position == None:
                top_left_position = [hitbox.topleft[0], hitbox.topleft[1]]
            else:
                if hitbox.topleft[0] < top_left_position[0]:
                    top_left_position = (hitbox.topleft[0], top_left_position[1])
                
                if hitbox.topleft[1] < top_left_position[1]:
                    top_left_position = (top_left_position[0], hitbox.topleft[1])
        
        position_delta = (
            attack_rect.topleft[0] - top_left_position[0],
            attack_rect.topleft[1] - top_left_position[1]
        )
        
        return_hitboxes = []
        
        for hitbox in attack_hitboxes:
            hitbox_position = [
                hitbox.topleft[0] + position_delta[0],
                hitbox.topleft[1] + position_delta[1]
            ]
            
            #Flip hitbox orientation if facing left
            if self.player.direction == PlayerStates.FACING_LEFT:
                hitbox_position[0] = (
                    attack_rect.topright[0] - 
                    (hitbox_position[0] - attack_rect.topleft[0])
                )
            
            return_hitboxes.append(pygame.Rect(hitbox_position, hitbox.size))
        
        return return_hitboxes
    
    def get_enemy_hitboxes_for_rect(self, enemy, enemy_rect):
        hitboxes = self.hitbox_builder.get_hitboxes(enemy.model.lines)
        
        enemy_position = pygame.Rect(enemy.get_enclosing_rect()).topleft
        
        position_delta = (
            enemy_rect.topleft[0] - enemy_position[0],
            enemy_rect.topleft[1] - enemy_position[1]
        )
        
        for hitbox in hitboxes:
            hitbox.topleft = (
                hitbox.topleft[0] + position_delta[0],
                hitbox.topleft[1] + position_delta[1]
            )
        
        return hitboxes
    
    def attack_in_range(self, attack, enemy, enemy_rects):
        
        animation_name = attack.right_animation.name
        attack_prediction_data = self.attack_prediction_data[animation_name]
        
        initial_position = (
            self.player.model.position[0],
            (gamestate.stage.ground.position[1] - 
            attack_prediction_data.attack_rects[0].height)
        )
        
        attack_rect_deltas = attack_prediction_data.attack_rect_deltas
        attack_rects = self.set_rect_positions(
            initial_position,
            attack_prediction_data.attack_rects,
            attack_rect_deltas
        )
        
        collision_index = self.get_max_collsion_index(attack_rects, enemy_rects)
        in_range = False
        
        if collision_index > -1:
            
            enemy_hitboxes = self.get_enemy_hitboxes_for_rect(
                enemy,
                enemy_rects[collision_index]
            )
            
            attack_hitboxes = self.set_rect_positions(
                initial_position, 
                attack_prediction_data.attack_hitboxes[collision_index],
                attack_prediction_data.attack_hitbox_deltas[collision_index]
            )
            
            #if attack.direction == PlayerStates.FACING_LEFT:
            #    attack_rect_color = (0,255,0)
            #    if in_range:
            #        attack_rect_color = (0,255,0)
            #    
            #    #debugging code
            #    for attack_rect in enemy_hitboxes:
            #        rect_surface = pygame.Surface(
            #            (attack_rect.width, attack_rect.height)
            #        )
            #        drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #        pygame.draw.rect(rect_surface, (255,0,0), drawing_rect, 2)
            #        st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #           attack_rect.topleft, 
            #           rect_surface
            #        )
            #     
            #    #debugging code
            #    for attack_rect in attack_hitboxes:
            #        rect_surface = pygame.Surface(
            #            (attack_rect.width, attack_rect.height)
            #        )
            #        drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #        pygame.draw.rect(rect_surface, attack_rect_color, drawing_rect, 2)
            #        st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #            attack_rect.topleft, 
            #            rect_surface
            #        )
                
            in_range = self.get_hitbox_collision_indicator(
                attack_hitboxes,
                enemy_hitboxes
            )
            
            ##debug code
            #attack_rect_color = (255,0,0)
            #if in_range:
            #    attack_rect_color = (0,255,0)
            #
            ##debugging code
            #for attack_rect in enemy_hitboxes:
            #    rect_surface = pygame.Surface(
            #        (attack_rect.width, attack_rect.height)
            #    )
            #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #    pygame.draw.rect(rect_surface, (255,0,0), drawing_rect, 2)
            #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        attack_rect.topleft, 
            #       rect_surface
            #    )
            # 
            ##debugging code
            #for attack_rect in attack_hitboxes:
            #    rect_surface = pygame.Surface(
            #        (attack_rect.width, attack_rect.height)
            #    )
            #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #    pygame.draw.rect(rect_surface, attack_rect_color, drawing_rect, 2)
            #   st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        attack_rect.topleft, 
            #        rect_surface
            #    )
            #
            #if in_range:
            #    #print(collision_index)
            # 
            #    #debugging code
            #    attack_rect = attack_rects[collision_index]
            #    rect_surface = pygame.Surface(
            #        (attack_rect.width, attack_rect.height)
            #    )
            #    drawing_rect = pygame.Rect((0,0), attack_rect.size)
            #    pygame.draw.rect(rect_surface, (0,255,0), drawing_rect, 2)
            #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        attack_rect.topleft, 
            #        rect_surface
            #    )
            #     
            #    #debugging code
            #    enemy_rect = enemy_rects[collision_index]
            #    rect_surface = pygame.Surface(
            #        (enemy_rect.width, enemy_rect.height)
            #   )
            #    drawing_rect = pygame.Rect((0,0), enemy_rect.size)
            #    pygame.draw.rect(rect_surface, (0,0,255), drawing_rect, 2)
            #    st_versusmode.local_state.surface_renderer.draw_surface_to_screen(
            #        enemy_rect.topleft, 
            #        rect_surface
            #    )
        
        return in_range
    
    def set_rect_positions(
        self,
        initial_position,
        attack_rects,
        attack_rect_deltas
    ): 
        new_rects = []
        
        for i in range(len(attack_rects)):
            rect = attack_rects[i]
            delta = None
            
            if self.player.model.orientation == physics.Orientations.FACING_RIGHT:
                delta = (
                    initial_position[0] - rect.left + attack_rect_deltas[i][0],
                    initial_position[1] - rect.top + attack_rect_deltas[i][1]
                )
            else:
                 delta = (
                    initial_position[0] - rect.right - attack_rect_deltas[i][0],
                    initial_position[1] - rect.top + attack_rect_deltas[i][1]
                )   
            
            new_rect = rect.move(*delta)
            new_rects.append(new_rect)
        
        return new_rects
    
    def get_hitbox_collision_indicator(self, attack_hitboxes, enemy_hitboxes):
        for attack_hitbox in attack_hitboxes:
            if attack_hitbox.collidelist(enemy_hitboxes) > -1:
                return True
        
        return False
    
    def get_max_collsion_index(
        self, 
        attack_rects, 
        enemy_rects
    ):
        
        collision_indices = []
        collision_areas = []
        
        for i in range(min(len(attack_rects), len(enemy_rects))):
            if attack_rects[i].colliderect(enemy_rects[i]):
                collision_indices.append(i)
                collision_areas.append(
                    self.get_collision_area(
                        attack_rects[i],
                        enemy_rects[i]
                    )
                )
                
        max_collision_index = -1
        max_collision_area = 0
        
        for i in range(len(collision_indices)):
            if collision_areas[i] > max_collision_area:
                max_collision_area = collision_areas[i]
                max_collision_index = collision_indices[i]
        
        return max_collision_index
    
    def get_collision_area(self, attack_rect, enemy_rect):
        overlap_rect = attack_rect.clip(enemy_rect)
        
        return overlap_rect.width * overlap_rect.height

class AIGraphFactory():
    """Builds dictionaries that hold a graph"""
    
    def create_combo_graph(self, player):
        """Creates a combo graph that maps the relationships between each attack.  
        The edges of the attack graph are weighted with 1 as the maximum value."""
        
        combo_graph = {}
        attacks = player.actions[PlayerStates.ATTACKING]
        
        for attack in attacks:
            name = attack.right_animation.name
            node = self.get_node(combo_graph, name, attack)
            
            combo_graph[name] = node
            
            #add edges for every other attack
            for neighbor_attack in attacks:
                neighbor_attack_name = neighbor_attack.right_animation.name
                neighbor_attack_node = self.get_node(
                    combo_graph, 
                    neighbor_attack_name,
                    neighbor_attack
                )
                node.add_edge(
                    WeightedEdge(neighbor_attack_node, 1)
                )
        
        return combo_graph
    
    def create_initial_attack_graph(self, player):
        """Creates a graph mapping player states to attacks."""
        
        attack_graph = {}
        attacks = player.actions[PlayerStates.ATTACKING]
        
        stand_node = Node(PlayerStates.STANDING, None, [])
        attack_graph[PlayerStates.STANDING] = stand_node
        
        #add edges for every attack
        for neighbor_attack in attacks:
            neighbor_attack_name = neighbor_attack.right_animation.name
            neighbor_attack_node = self.get_node(
                attack_graph, 
                neighbor_attack_name,
                neighbor_attack
            )
            stand_node.add_edge(
                WeightedEdge(neighbor_attack_node, 1)
            )
        
        walk_node = Node(PlayerStates.WALKING, None, [])
        attack_graph[PlayerStates.WALKING] = walk_node
        
        #add edges for every attack
        for neighbor_attack in attacks:
            neighbor_attack_name = neighbor_attack.right_animation.name
            neighbor_attack_node = self.get_node(
                attack_graph, 
                neighbor_attack_name,
                neighbor_attack
            )
            walk_node.add_edge(
                WeightedEdge(neighbor_attack_node, 1)
            )
        
        run_node = Node(PlayerStates.RUNNING, None, [])
        attack_graph[PlayerStates.RUNNING] = run_node
        
        #add edges for every attack
        for neighbor_attack in attacks:
            neighbor_attack_name = neighbor_attack.right_animation.name
            neighbor_attack_node = self.get_node(
                attack_graph, 
                neighbor_attack_name,
                neighbor_attack
            )
            run_node.add_edge(
                WeightedEdge(neighbor_attack_node, 1)
            )
        
        float_node = Node(PlayerStates.FLOATING, None, [])
        attack_graph[PlayerStates.FLOATING] = float_node
        
        #add edges for every attack
        for neighbor_attack in attacks:
            neighbor_attack_name = neighbor_attack.right_animation.name
            neighbor_attack_node = self.get_node(
                attack_graph, 
                neighbor_attack_name,
                neighbor_attack
            )
            float_node.add_edge(
                WeightedEdge(neighbor_attack_node, 1)
            )
        
        jump_node = Node(PlayerStates.JUMPING, None, float_node.edges)
        attack_graph[PlayerStates.JUMPING] = jump_node
        
        return attack_graph
    
    def get_node(self, graph, name, data):
        """Returns an existing node from the graph with the given name.  If the
        combo node does not a exist a new node is added to the graph and 
        returned."""
        
        if name in graph:
            return graph[name]
        
        else:
            new_node = Node(name, data, [])
            graph[name] = new_node
            
            return new_node

class Node():
    """An attack and its relationships to other attacks.  Weights determine the
    strength of the relationship between to attacks."""
    
    def __init__(
        self,
        name,
        data,
        edges
    ):
        self.name = name
        self.data = data
        
        #A list of edges
        self.edges = edges
        self.edge_dictionary = dict(
            [(edge.end_node.name, edge) for edge in edges]
        )
    
    def add_edge(self, edge):
        self.edges.append(edge)
        self.edge_dictionary[edge.end_node.name] = edge
    
    def get_neighbors(self, weight_threshold = -1):
        if weight_threshold > 0:
            return [
                edge.end_node
                for edge in self.edges
                if edge.weight > weight_threshold
            ]
        else:
            return [edge.end_node for edge in self.edges]
    
    def reset_edge_weights(self):
        for edge in self.edges:
            edge.weight = 1

class WeightedEdge():
    """This represents the relationship between two nodes and the strength of
     the relationship"""
     
    def __init__(self, end_node, weight):
        self.end_node = end_node
        self.weight = weight

class AttackPredictionData():
    """An attack prediction engine can predict whether a particular attack will hit
    a player"""
    def __init__(
        self,
        attack_rects,
        attack_rect_deltas,
        attack_hitboxes,
        attack_hitbox_deltas
    ):
        self.attack_rects = attack_rects
        self.attack_rect_deltas = attack_rect_deltas
        self.attack_hitboxes = attack_hitboxes
        self.attack_hitbox_deltas = attack_hitbox_deltas
        
        self.attack_x_range = 0
        self.attack_y_range = 0
        self.set_attack_range()
    
    def set_attack_range(self):
        start_position = self.attack_rects[0].topleft
        end_position = (
            self.attack_rects[-1].topleft[0] + self.attack_rects[-1].width,
            self.attack_rects[-1].topleft[1] + self.attack_rects[-1].height
        )
        self.attack_x_range = abs(end_position[0] - start_position[0])
        self.attack_y_range = abs(end_position[1] - start_position[1])

class AttackPredictionDataFactory():
    def __init__(self, timestep):
        self.timestep = timestep
        self.hitbox_builder = HitboxBuilder()
    
    def create_attack_prediction_data(self, player, attack):
        attack_rects = self.get_attack_rects(
            player, 
            attack,
            attack.attack_type
        )
        
        if len(attack_rects) > 0:
            attack_rect_deltas = self.get_attack_rect_deltas(attack_rects)
            
            attack_hitboxes = self.get_attack_hitboxes(
                player, 
                attack, 
                attack.attack_type
            )
            attack_hitbox_deltas = self.get_attack_hitbox_deltas(
                attack_rects[0],
                attack_hitboxes
            )
            
            return AttackPredictionData(
                attack_rects,
                attack_rect_deltas,
                attack_hitboxes,
                attack_hitbox_deltas
            )
        else:
            return None
    
    def get_attack_rect_deltas(self, attack_rects):
        initial_position = attack_rects[0].topleft
        attack_rect_deltas = \
            [(rect.left - initial_position[0], rect.top - initial_position[1]) 
            for rect in attack_rects]
        
        return attack_rect_deltas
    
    def get_attack_hitbox_deltas(self, initial_rect, attack_hitboxes):
        initial_position = initial_rect.topleft
        
        attack_hitbox_deltas = []
        
        for time_hitboxes in attack_hitboxes:
            time_hitbox_deltas = \
                [(rect.left - initial_position[0], rect.top - initial_position[1]) 
                for rect in time_hitboxes]
            
            attack_hitbox_deltas.append(time_hitbox_deltas)
        
        return attack_hitbox_deltas
    
    #################### common building functions
    def reset_player(self, player):
        player.model.move_model((100,100))
        player.model.time_passed = 0
        player.model.animation_run_time = 0
        player.direction = PlayerStates.FACING_RIGHT
        player.actions[PlayerStates.STANDING].set_player_state(player)
    
    def get_attack_lines(self, model, attack_type):
        attack_lines = None
        
        if (attack_type in InputActionTypes.PUNCHES or
        attack_type == AttackTypes.PUNCH):
            attack_lines = dict([
                (line_name, model.lines[line_name])
                for line_name in Attack.PUNCH_LINE_NAMES
            ])
        elif (attack_type in InputActionTypes.KICKS or
        attack_type == AttackTypes.KICK):
            attack_lines = dict([
                (line_name, model.lines[line_name]) 
                for line_name in Attack.KICK_LINE_NAMES
            ])
        
        return attack_lines
    
    #################### Attack Rect Building
    def get_attack_rects(self, player, attack, attack_type):
        """creates a rect surrounding the attack lines for each frame in
        the given animation"""
        return_rects = []
        
        self.reset_player(player)
        attack.set_player_state(player)
        
        while (player.model.animation_run_time < 
        (attack.right_animation.animation_length - self.timestep)):
            player.model.time_passed = self.timestep
            attack.move_player(player)
            return_rects.append(pygame.Rect(player.model.get_enclosing_rect()))
        
        self.reset_player(player)
        attack.set_player_state(player)
        initial_position = (player.model.position[0], player.model.position[1])
        
        for frame_rect in return_rects:
            frame_rect.move(-initial_position[0], -initial_position[1])
        
        return return_rects

    #################### Attack Hitbox Building
    def get_attack_hitboxes(self, player, attack, attack_type):
        """gets the hitboxes for each frame in the given animation"""
        time_hitboxes_list = []
        
        self.reset_player(player)
        attack.set_player_state(player)
        
        while (player.model.animation_run_time < 
        (attack.right_animation.animation_length - self.timestep)):
            player.model.time_passed = self.timestep
            attack.move_player(player)
            time_hitboxes_list.append(
                self.get_model_hitboxes(player.model, attack_type)
            )
        
        self.reset_player(player)
        attack.set_player_state(player)
        initial_position = (player.model.position[0], player.model.position[1])
        
        for time_hitboxes in time_hitboxes_list:
            for hitbox in time_hitboxes:
                hitbox.move(-initial_position[0], -initial_position[1])
        
        return time_hitboxes_list
    
    def get_model_hitboxes(self, model, attack_type):
        attack_lines = self.get_attack_lines(model, attack_type)
        
        return self.hitbox_builder.get_hitboxes(attack_lines)
