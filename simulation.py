import math
import pygame
import mathfuncs
from threading import Lock
from wotsprot.rencode import serializable
from enumerations import MatchStates, PlayerTypes, ClashResults, \
PlayerPositions, PlayerStates, LineNames, PointNames

class PlayerState():
    def __init__(
        self,
        animation_run_time,
        keys_pressed,
        reference_position,
        health
    ):
        self.animation_run_time = animation_run_time
        self.keys_pressed = keys_pressed
        self.reference_position = reference_position
        self.health = health
    
    def _pack(self):
        return (self.animation_run_time, self.keys_pressed, 
        self.reference_position, self.health)

class SimulationState():
    def __init__(
        self,
        player_states,
        sequence
    ):
        self.player_states = player_states
        self.sequence = sequence
    
    def _pack(self):
        return (self.player_states, self.sequence)

class SimulationRenderingInfo():
    def __init__(
        self,
        match_state,
        match_time,
        player_rendering_info_dictionary,
        attack_result_rendering_info
    ):
        self.match_state = match_state
        self.match_time = match_time
        self.player_rendering_info_dictionary = player_rendering_info_dictionary
        self.attack_result_rendering_info = attack_result_rendering_info
    
    def _pack(self):
        return (self.match_state, self.match_time,
        self.player_rendering_info_dictionary, self.attack_result_rendering_info)

class AttackResultRenderingInfo():
    def __init__(
        self,
        attack_point,
        knockback_vector,
        attack_damage
    ):
        self.attack_point = attack_point
        self.knockback_vector = knockback_vector
        self.attack_damage = attack_damage
    
    def _pack(self):
        return self.attack_point, self.knockback_vector, self.attack_damage

class PlayerRenderingInfo():
    def __init__(
        self,
        player_model,
        player_state,
        player_outline_color,
        player_health_color,
        health_percentage
    ):
        self.player_model = player_model
        self.player_state = player_state
        self.player_outline_color = player_outline_color
        self.player_health_color = player_health_color
        self.health_percentage = health_percentage
    
    def _pack(self):
        return (self.player_point_positions, self.player_state,
        self.player_outline_color, self.player_health_color, self.health_percentage)

def create_player_state_dictionary(player_dictionary, keys_pressed):
    """creates a dictionary mapping player positions to playerstates"""
    
    return_dictionary = {}
    
    for player_position, player in player_dictionary:
        return_dictionary[player_position] = PlayerState(
            player.model.animation_run_time, 
            keys_pressed, 
            player.model.reference_position,
            player.health_meter
        )
    
    return return_dictionary 

class MatchSimulation():
    def __init__(
        self,
        timestep=20, 
        player_type_dictionary={}, 
        player_dictionary={}
    ):
        self.timestep = timestep
        self.accumulator = 0
        self.player_type_dictionary = player_type_dictionary
        self.player_dictionary = player_dictionary
        self.clock = pygame.time.Clock()
        self.attack_resolver = AttackResolver()
        self.current_attack_result = None
        self.collision_handler = CollisionHandler()
        self.player_lock = Lock()
        self.history = []
        self.match_time = 0
        self.match_state = MatchStates.READY
    
    def step(self, player_keys_pressed, time_passed):
        """update the state of the players in the simulation"""
        
        self.accumulator += time_passed
        
        while self.accumulator > self.timestep:
            
            match_state = self.get_match_state()
            self.match_state = match_state
            self.handle_match_state(match_state)
            self.handle_player_events(player_keys_pressed, self.timestep)
            self.handle_interactions()
            
            #TODO - self.history.append(self.get_simulation_state())
            self.accumulator -= self.timestep
            self.match_time += self.timestep
    
    def handle_match_state(self, match_state):
        
        if (self.match_state == MatchStates.READY or 
        self.match_state == MatchStates.NO_CONTEST):
            for player in self.player_dictionary.values():
                player.handle_input_events = False
            
        elif self.match_state == MatchStates.FIGHT:
            for player in self.player_dictionary.values():
                player.handle_input_events = True
            
        elif self.match_state == MatchStates.PLAYER1_WINS:
            player2 = self.player_dictionary[PlayerPositions.PLAYER2]
            player2.handle_input_events == False
            player2.set_stun_timeout(10000)
            
        elif self.match_state == MatchStates.PLAYER2_WINS:
            player1 = self.player_dictionary[PlayerPositions.PLAYER1]
            player1.handle_input_events == False
            player1.set_stun_timeout(10000)
            
    def get_rendering_info(self):
        return SimulationRenderingInfo(
            self.match_state,
            self.match_time,
            self.get_player_rendering_info_dictionary(),
            self.get_attack_result_rendering_info()
        )
    
    def get_match_state(self):
        match_state = MatchStates.FIGHT
        
        if self.match_time < 3000:
            return MatchStates.READY
        elif self.match_time < 4000:
            return MatchStates.FIGHT
        else:
            #just check if the game is over
            if (self.player_dictionary[PlayerPositions.PLAYER1].health_meter == 0 and
            self.player_dictionary[PlayerPositions.PLAYER2].health_meter == 0):
                match_state = MatchStates.NO_CONTEST
                    
            elif self.player_dictionary[PlayerPositions.PLAYER1].health_meter == 0:
                match_state = MatchStates.PLAYER2_WINS
                
            elif self.player_dictionary[PlayerPositions.PLAYER2].health_meter == 0:
                match_state = MatchStates.PLAYER1_WINS
            else:
                match_state = MatchStates.FIGHT
        
        return match_state
    
    def get_player_rendering_info_dictionary(self):
        return_rendering_dictionary = {}
        
        for player_position, player in self.player_dictionary.iteritems():
            return_rendering_dictionary[player_position] = PlayerRenderingInfo(
                player.model,
                player.get_player_state(),
                player.outline_color,
                player.health_color,
                player.health_meter / player.health_max
            )
        
        return return_rendering_dictionary
    
    def get_attack_result_rendering_info(self):
        if self.current_attack_result != None:
            attack_point = self.current_attack_result.attack_point
            
            return AttackResultRenderingInfo(
                attack_point,
                self.current_attack_result.knockback_vector,
                self.current_attack_result.attacker.get_point_damage(attack_point.name)
            )
        else:
            return None
      
    def handle_player_events(self, player_keys_pressed, timestep):
        """Advance player animations according to the current pygame events"""
        
        for player_position, active_player in self.player_dictionary.iteritems():
            player_type = self.player_type_dictionary[player_position]
            
            if player_type == PlayerTypes.HUMAN:
                active_player.handle_events(
                    player_keys_pressed[player_position],
                    timestep
                )
            elif player_type == PlayerTypes.BOT:
                [active_player.handle_events(other_player, timestep) 
                for other_player_position, other_player 
                in self.player_dictionary.iteritems()
                if not other_player_position == player_position]
            else:
                raise Exception(
                    "Invalid Player Type: " + player_type
                )
    
    def handle_interactions(self):
        """determine the effects of attacks on each player"""
    
        attack_result = self.get_attack_result()
        self.current_attack_result = attack_result
        
        if attack_result != None:
            
            if attack_result.clash_indicator:
                self.collision_handler.handle_blocked_attack_collision(
                    attack_result.attacker,
                    attack_result.receiver
                )
            else:
                self.collision_handler.handle_unblocked_attack_collision(
                    attack_result
                )
    
    def get_attack_result(self):
        attack_result = None
        
        player1 = self.player_dictionary[PlayerPositions.PLAYER1]
        player2 = self.player_dictionary[PlayerPositions.PLAYER2]
        
        if self.test_overlap(
            player1.get_enclosing_rect(), 
            player2.get_enclosing_rect()
        ):
            if player1.get_player_state() == PlayerStates.ATTACKING:
                attack_result = self.attack_resolver.get_attack_result(
                    player1, 
                    player2
                )
                
            elif player2.get_player_state() == PlayerStates.ATTACKING:
                attack_result = self.attack_resolver.get_attack_result(
                    player2, 
                    player1
                )
                
            else:
                pass #no attack result
        
        return attack_result
    
    def test_overlap(self, rect1, rect2):
        """a fast test if two players could possibly be attacking each other"""
        
        overlap = True
        rect1_pos = (rect1.left, rect1.top)
        rect2_pos = (rect2.left, rect2.top)
        
        if ((rect1_pos[0] > (rect2_pos[0] + rect2.width)) or
            ((rect1_pos[0] + rect1.width) < rect2_pos[0]) or
            (rect1_pos[1] > (rect2_pos[1] + rect2.height)) or
            ((rect1_pos[1] + rect1.height) < rect2_pos[1])):
            overlap = False
        
        return overlap

class CollisionHandler():
    """updates players that are in an attack collision"""
    
    def handle_unblocked_attack_collision(
        self,
        attack_result
    ):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        attack_knockback_vector = attack_result.knockback_vector
        
        if receiver.get_player_state() == PlayerStates.STUNNED:
            
            stun_knockback_vector = receiver.knockback_vector
            
            if self.attacker_is_recoiling(
                attack_knockback_vector, 
                stun_knockback_vector
            ):
                pass
            else:
                self.apply_collision_physics(attack_result)
                self.apply_attack_damage(attack_result)
                
        else:
            self.apply_collision_physics(attack_result)
            receiver.set_player_state(PlayerStates.STUNNED)
            self.apply_attack_damage(attack_result)

    def apply_attack_damage(self, attack_result):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        damage = attacker.get_point_damage(
            attack_result.attack_point.name
        )
        
        if receiver.health_meter > 0:
            receiver.health_meter = max(0, receiver.health_meter - damage)
            receiver.set_stun_timeout(attacker.get_stun_timeout())

    def attacker_is_recoiling(
        self,
        attack_knockback_vector, 
        stun_knockback_vector
    ):
        attack_x_sign = mathfuncs.sign(attack_knockback_vector[0])
        attack_y_sign = mathfuncs.sign(attack_knockback_vector[1])
        stun_x_sign = mathfuncs.sign(stun_knockback_vector[0])
        stun_y_sign = mathfuncs.sign(stun_knockback_vector[1])
        
        if (attack_x_sign != stun_x_sign) or (attack_y_sign != stun_y_sign):
            return True
        else:
            return False
    
    def handle_blocked_attack_collision(
        self,
        attacker, 
        receiver
    ):
        attacker.set_neutral_state()
        receiver.set_neutral_state()
        
        separation_vector = self.get_separation_vector(attacker,receiver)
        receiver.model.shift((.5 * separation_vector[0], .5 * separation_vector[1]))
        attacker.model.shift((-.5 * separation_vector[0], -.5 * separation_vector[1]))

    def apply_collision_physics(
        self,
        attack_result
    ):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        separation_vector = self.get_separation_vector(attacker,receiver)
        receiver.model.shift((.5 * separation_vector[0], .5 * separation_vector[1]))
        
        receiver.knockback_vector = attack_result.knockback_vector
        receiver.interaction_point = attack_result.receive_point
        receiver.interaction_vector = self.get_pull_point_deltas(attack_result)
        receiver.pull_point(receiver.interaction_vector)
        receiver.model.velocity = (0,0)
        receiver.model.accelerate(receiver.knockback_vector[0], \
                                  receiver.knockback_vector[1])
    
    def get_separation_vector(
        self,
        attacker, 
        receiver
    ):
        """Get the relative position between the attack and receiver.  The y 
        delta is always to negative to make sure the receiver moves up"""
        y_delta = receiver.model.position[1] - attacker.model.position[1]
        x_delta = receiver.model.position[0] - attacker.model.position[0]
        
        if y_delta > 0:
            y_delta = -1 * y_delta
        
        return (x_delta, y_delta)
    
    def get_pull_point_deltas(
        self,
        attack_result
    ):
        """gets the knockback applied to the interaction point to move the lines in the
        model"""
        
        knockback_vector = attack_result.knockback_vector
        
        x = knockback_vector[0]
        y = knockback_vector[1]
        hypotenuse = math.hypot(x,y)
        
        knockback = 3
        
        if hypotenuse == 0:
            return 0, 0
        else:
            return knockback * x / hypotenuse, knockback * y / hypotenuse

class AttackResult():
    
    def __init__(
        self,
        attacker,
        receiver,
        attack_point,
        receive_point,
        knockback_vector,
        clash_indicator
    ):
        self.attacker = attacker
        self.receiver = receiver
        self.attack_point = attack_point
        self.receive_point = receive_point
        self.knockback_vector = knockback_vector
        self.clash_indicator = clash_indicator

class AttackResolver():
    def __init__(self):
        self.hitbox_builder = HitboxBuilder()
    
    def get_attack_result(self, attacker, receiver):
        attack_result = None
        clash_indicator = False
        
        attacker_attack_hitboxes = self.hitbox_builder.get_hitbox_dictionary(attacker.get_attack_lines())
        
        if receiver.get_player_state() == PlayerStates.ATTACKING:
            receiver_attack_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                receiver.get_attack_lines()
            )
            colliding_line_names = self.test_attack_collision(
                attacker_attack_hitboxes,
                receiver_attack_hitboxes
            )
            
            if colliding_line_names:
                
                clash_result = self.get_clash_result(
                    attacker,
                    receiver,
                    colliding_line_names
                )
                
                if clash_result == ClashResults.TIE:
                    clash_indicator = True
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                elif clash_result == ClashResults.WIN:
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                elif clash_result == ClashResults.LOSS:
                    #swap attacker and receiver
                    temp = attacker
                    attacker = receiver
                    receiver = temp
                    
                    #reverse the order of the colliding line names to math
                    #that player 2 is now the attacker.
                    colliding_line_names = colliding_line_names[::-1]
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
            
            else:
                attacker_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                    attacker.model.lines
                )
                colliding_line_names = self.test_attack_collision(
                    receiver_attack_hitboxes,
                    attacker_hitboxes
                )
                
                if colliding_line_names:
                    #swap attacker and receiver
                    temp = attacker
                    attacker = receiver
                    receiver = temp
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                else:
                    receiver_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                        receiver.model.lines
                    )
                    colliding_line_names = self.test_attack_collision(
                        attacker_attack_hitboxes, receiver_hitboxes
                    )
                    
                    if colliding_line_names:
                        attack_result = self.build_attack_result(
                            attacker,
                            receiver,
                            colliding_line_names, 
                            clash_indicator
                        )
                        
        else:
            receiver_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                receiver.model.lines
            )
            colliding_line_names = self.test_attack_collision(
                attacker_attack_hitboxes,
                receiver_hitboxes
            )
            
            if colliding_line_names:
                
                attack_result = self.build_attack_result(
                    attacker,
                    receiver,
                    colliding_line_names, 
                    clash_indicator
                )
        
        return attack_result
    
    def build_attack_result(
        self, 
        attacker, 
        receiver, 
        colliding_line_names, 
        clash_indicator
    ):
        colliding_lines = (
            attacker.model.lines[colliding_line_names[0]],
            receiver.model.lines[colliding_line_names[1]]
        )
        interaction_points = self.get_interaction_points(
            receiver,
            colliding_lines
        )
        attack_point = interaction_points[0]
        receive_point = interaction_points[1]
        knockback_vector = self.get_knockback_vector(attacker, attack_point)
        
        attack_result = AttackResult(
            attacker,
            receiver,
            attack_point,
            receive_point,
            knockback_vector,
            clash_indicator
        )
        
        return attack_result
    
    def get_clash_result(self, attacker, receiver, colliding_line_names):
        colliding_lines = (
            receiver.model.lines[colliding_line_names[0]],
            attacker.model.lines[colliding_line_names[1]]
        )
        
        interaction_points = self.get_interaction_points(receiver, colliding_lines)
        attack_damage = attacker.get_point_damage(interaction_points[0].name)
        block_damage = receiver.get_point_damage(interaction_points[1].name)
        
        if 5 > abs(attack_damage - block_damage):
            return ClashResults.TIE
        elif attack_damage > block_damage:
            return ClashResults.WIN
        else:
            return ClashResults.LOSS
    
    def get_interaction_points(self, receiver, colliding_lines):
        attacker_line_index = 0
        receiver_line_index = 1
        
        attack_point1 = colliding_lines[attacker_line_index].endPoint1
        attack_point2 = colliding_lines[attacker_line_index].endPoint2
        receiver_point1 = receiver.get_point(PointNames.TORSO_TOP)
        receiver_point2 = receiver.get_point(PointNames.TORSO_BOTTOM)
        
        point_pairs = [
            (attack_point1, receiver_point1),
            (attack_point1, receiver_point2),
            (attack_point2, receiver_point1),
            (attack_point2, receiver_point2)
        ]
        point_distances =  [
            mathfuncs.distance(attack_point1.pos, receiver_point1.pos),
            mathfuncs.distance(attack_point1.pos, receiver_point2.pos),
            mathfuncs.distance(attack_point2.pos, receiver_point1.pos),
            mathfuncs.distance(attack_point2.pos, receiver_point2.pos)
        ]
        
        shortest_distance = min(point_distances)
        
        return point_pairs[point_distances.index(shortest_distance)]

    def test_attack_collision(self, attack_hitbox_dictionary, receiver_hitbox_dictionary):
        colliding_line_names = None
        
        for attack_line_name, attack_hitboxes in attack_hitbox_dictionary.iteritems():
            for receiver_line_name, receiver_hitboxes in receiver_hitbox_dictionary.iteritems():
                for attack_hitbox in attack_hitboxes:
                    if attack_hitbox.collidelist(receiver_hitboxes) > -1:
                        colliding_line_names = (attack_line_name, receiver_line_name)
                        break
                if colliding_line_names:
                    break
            if colliding_line_names:
                break
        
        return colliding_line_names

    def get_knockback_vector(self, attacker, attack_point):
        """get the direction and magnitude of the knockback"""
        
        return self.scale_knockback(attacker.get_point_position_change(attack_point.name))
    
    def scale_knockback(self, knockback_vector):
        """binds the scale of a knockback vector to control stun animation"""
        
        x = knockback_vector[0]
        y = knockback_vector[1]
        hypotenuse = math.hypot(x,y)
        
        knockback = .2
        
        if hypotenuse == 0:
            return 0, 0
        else:
            return 2 * knockback * x / hypotenuse, knockback * y / hypotenuse

class HitboxBuilder():
    """creates a list of rects that lie on a set of lines"""
    def get_hitbox_dictionary(self, lines):
        hitboxes = {}
        
        for name, line in lines.iteritems():
            if name == LineNames.HEAD:
                hitboxes[name] = [self.get_circle_hitbox(line)]
            else:
                hitboxes[name] = self.get_line_hitboxes(line)
        
        return hitboxes

    def get_hitboxes(self, lines):
        hitbox_dictionary = self.get_hitbox_dictionary(lines)
        hitbox_lines = []
        
        for hitbox_list in hitbox_dictionary.values():
            hitbox_lines.extend(hitbox_list)
        
        return hitbox_lines

    def get_circle_hitbox(self, circle):
        circle.set_length()
        radius = int(circle.length / 2)
        hitbox = pygame.Rect((circle.center()[0] - radius, \
                              circle.center()[1] - radius), \
                             (circle.length, circle.length))
        
        return hitbox

    def get_line_hitboxes(self, line):
        line_rects = []
        
        line.set_length()
        box_count = line.length / 7
        
        if box_count > 0:
            for pos in self.get_hitbox_positions(box_count, line):
                line_rects.append(pygame.Rect(pos, (14,14)))
        else:
            line_rects.append(pygame.Rect(line.endPoint1.pos, (14,14)))
        
        return line_rects

    def get_hitbox_positions(self, box_count, line):
            """gets top left of each hitbox on a line.
            
            box_count: the number of hit boxes"""
            hitbox_positions = []
            
            start_pos = line.endPoint1.pixel_pos()
            end_pos = line.endPoint2.pixel_pos()
            
            x_delta = end_pos[0] - start_pos[0]
            y_delta = end_pos[1] - start_pos[1]
            
            length = line.length
            length_to_hit_box_center = 0
            increment = line.length / box_count
            
            hitbox_positions.append((int(end_pos[0] - 7), int(end_pos[1] - 7)))
            
            length_to_hit_box_center += increment
            x_pos = start_pos[0] + x_delta - (
                (x_delta / length) * length_to_hit_box_center
            )
            y_pos = start_pos[1] + y_delta - (
                (y_delta / length) * length_to_hit_box_center
            )
            box_center = (x_pos, y_pos)
            
            for i in range(int(box_count)):
                hitbox_positions.append(
                    (int(box_center[0] - 7), int(box_center[1] - 7))
                )
                
                length_to_hit_box_center += increment
                x_pos = start_pos[0] + x_delta - (
                    (x_delta / length) * length_to_hit_box_center
                )
                y_pos = start_pos[1] + y_delta - (
                    (y_delta / length) * length_to_hit_box_center
                )
                box_center = (x_pos, y_pos)
            
            hitbox_positions.append((int(start_pos[0] - 7), int(start_pos[1] - 7)))
            
            return hitbox_positions

serializable.register(PlayerState)
