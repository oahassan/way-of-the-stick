import copy
import pygame

import gamestate
import animationexplorer
import physics
import mathfuncs
import stick
import pulltool

class PlayerTypes:
    HUMAN = 'Human'
    BOT = 'Bot'
    REMOTE = 'Remote'

class AnimationModes():
    PHYSICS = "PHYSICS"
    KEYFRAME = "KEYFRAME"
    HYBRID = "HYBRID"

class PlayerStates():
    FACING_RIGHT = 'FACING_RIGHT'
    FACING_LEFT = 'FACING_LEFT'
    STANDING = 'STANDING'
    WALKING = 'WALKING'
    RUNNING = 'RUNNING'
    JUMPING = 'JUMPING'
    FLOATING = 'FLOATING'
    LANDING = 'LANDING'
    ATTACKING = 'ATTACKING'
    CROUCHING = 'CROUCHING'
    STUNNED = 'STUNNED'
    BLOCKING = 'BLOCKING'
    
    MOVEMENTS = [STANDING,WALKING,RUNNING,JUMPING,FLOATING, \
                 LANDING,CROUCHING]
    
    UNBOUND_MOVEMENTS = [STANDING,FLOATING,LANDING,STUNNED]
    
    PRESSED_KEY_STATE_TRANSITIONS = { \
        STANDING : [WALKING,RUNNING,JUMPING,CROUCHING,ATTACKING], \
        WALKING : [WALKING,STANDING,JUMPING,CROUCHING,ATTACKING], \
        RUNNING : [RUNNING,STANDING,JUMPING,CROUCHING,ATTACKING], \
        CROUCHING : [STANDING,ATTACKING], \
        JUMPING : [FLOATING,LANDING,ATTACKING], \
        LANDING : [STANDING,CROUCHING,ATTACKING,JUMPING,WALKING], \
        FLOATING : [LANDING,ATTACKING], \
        ATTACKING : [STANDING, FLOATING], \
        STUNNED : [FLOATING,LANDING,STANDING], \
        BLOCKING : [STANDING,CROUCHING] \
    }

class Player():
    ANIMATION_HEIGHT = 80
    REFERENCE_HEIGHT = 170
    ACCELERATION = .00200
    
    def __init__(self, position):
        self.player_type = None
        self.current_attack = None
        self.action = None
        self.color = (255,255,255)
        self.current_animation = None
        self.direction = PlayerStates.FACING_RIGHT
        self.stun_timeout = 500
        self.stun_timer = self.stun_timeout
        self.dash_timeout = 500
        self.dash_timer = self.dash_timeout
        self.high_jump_timeout = 500
        self.jump_timer = self.high_jump_timeout
        self.model = physics.Model(position)
        self.walk_speed = .4
        self.run_speed = .75
        self.jump_speed = -1
        self.high_jump_speed = -1.25
        self.aerial_acceleration = .04
        self.actions = {}
        self.knockback_vector = (0,0)
        self.pull_point = None
        self.knockback_multiplier = 4
        self.health_max = 2000
        self.health_meter = self.health_max
        self.health_color = (0,0,100)
        self.moveset = None
        self.point_name_to_point_damage = {} #Point name to PointDamage object
        self.previous_point_positions = {}
    
    def init_state(self):
        self.model.load_points()
        self.model.load_lines()
        self.init_point_damage_dictionary()
    
    def handle_events(self):
        time_passed = gamestate.clock.get_time()
        self.model.time_passed = time_passed
        
        self.set_previous_point_positions()
        
        self.action.move_player(self)
        
        if self.action.action_state == PlayerStates.ATTACKING:
            self.update_point_damage()
        
        draw_model(self)
        
        if self.dash_timer < self.dash_timeout:
            self.dash_timer += time_passed
        
        if self.jump_timer < self.high_jump_timeout:
            self.jump_timer += time_passed
        
        if self.stun_timer < self.stun_timeout:
            self.stun_timer += time_passed
    
    def get_player_point_positions(self):
        """builds a dictionary of point name to point position for each point in the
        model"""
        
        return_dictionary = {}
        
        for point_name, point in self.model.points.iteritems():
            return_dictionary[point_name] = point.pos
        
        return return_dictionary
    
    def set_previous_point_positions(self):
        
        self.previous_point_positions = self.get_player_point_positions()
    
    def get_previous_point_position(self, point_name):
        """Get the previous position of the point from the previous points dictionary.
        If the dictionary doesn't exist yet return the current position of the point."""
        
        if point_name in self.previous_point_positions.keys():
            return self.previous_point_positions[point_name]
            
        else:
            return self.model.points[point_name].pos
    
    def get_point_position_change(self, point_name):
        """Get the change in position of a point between now and the previous 
        game loop"""
        
        current_position = self.model.points[point_name].pos
        previous_position = self.get_previous_point_position(point_name)
        
        return \
            current_position[0] - previous_position[0], \
            current_position[1] - previous_position[1]
    
    def set_action(self):
        pass
    
    def handle_animation_end(self):
        if self.action.action_state == PlayerStates.JUMPING:
            self.actions[PlayerStates.FLOATING].set_player_state(self)
        elif self.action.action_state == PlayerStates.LANDING:
            self.set_neutral_state()
        elif self.action.action_state == PlayerStates.ATTACKING:
            self.current_attack = None
            self.set_neutral_state()
        elif self.action.action_state == PlayerStates.STUNNED:
            if self.action.test_state_change(self):
                self.set_neutral_state()
        elif self.action.action_state == PlayerStates.STANDING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.FLOATING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.CROUCHING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.WALKING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.RUNNING:
            self.action.set_player_state(self)
    
    def set_neutral_state(self):
        if self.is_aerial():
            self.actions[PlayerStates.FLOATING].set_player_state(self)
        else:
            self.actions[PlayerStates.STANDING].set_player_state(self)
    
    def set_velocity(self):
        velocity = self.model.velocity
        friction = self.model.friction
        
        if self.direction == PlayerStates.FACING_RIGHT:
            if self.action.action_state == PlayerStates.WALKING:
                self.model.velocity = (self.walk_speed + friction, velocity[1])
            elif self.action.action_state == PlayerStates.RUNNING:
                self.model.velocity = (self.run_speed + friction, velocity[1])
        elif self.direction == PlayerStates.FACING_LEFT:
            if self.action.action_state == PlayerStates.WALKING:
                self.model.velocity = (-(self.walk_speed + friction), velocity[1])
            elif self.action.action_state == PlayerStates.RUNNING:
                self.model.velocity = (-(self.run_speed + friction), velocity[1])
    
    def get_player_state(self):
        """returns the current state of the player"""
        return self.action.action_state
    
    def set_player_state(self, player_state):
        """sets the current state of the player"""
        self.actions[player_state].set_player_state(self)
    
    def get_attack_lines(self):
        return self.action.attack_lines
    
    def init_point_damage_dictionary(self):
        """initializes the point damage dictionary. NOTE: model must be intialized before
        calling."""
        for line_name in self.model.lines.keys():
            for point_name in stick.LINE_TO_POINTS[line_name]:
                if point_name not in self.point_name_to_point_damage.keys():
                    self.point_name_to_point_damage[point_name] = 0
    
    def update_point_damage(self):
        """updates the damage done by each attacking point"""
        
        current_point_positions_dictionary = self.get_player_point_positions()
        
        for point_name in self.point_name_to_point_damage.keys():
            
            current_relative_position = \
                self.get_point_relative_position(
                    point_name,
                    current_point_positions_dictionary
                )
            
            previous_relative_position = \
                self.get_point_relative_position(
                    point_name,
                    self.previous_point_positions
                )
            
            additional_damage = \
                mathfuncs.distance(
                    current_relative_position,
                    previous_relative_position
                )
            
            self.point_name_to_point_damage[point_name] += additional_damage
    
    def get_point_relative_position(self, point_name, point_position_dictionary):
        """determines the relative position of point based on the positions in the 
        point_position_dictionary"""
        
        point_position = point_position_dictionary[point_name]
        left, top = point_position_dictionary[point_name]
        
        for position in point_position_dictionary.values():
            
            if position[0] < left:
                left = position[0]
                
            if position[1] < top:
                top = position[1]
        
        return point_position[0] - left, point_position[1] - top
    
    def reset_point_damage(self):
        """sets the point damage for each point at the start of an attack"""
        
        for point_name in self.point_name_to_point_damage.keys():
            
            self.point_name_to_point_damage[point_name] = 0
    
    def get_point_damage(self, point_name):
        """Returns the damage dealt when attacked from the given point"""
        return self.point_name_to_point_damage[point_name]
    
    def get_enclosing_rect(self):
        return pygame.Rect(*self.model.get_enclosing_rect())
    
    def attack_in_range(self, attack, enemy):
        bottom_right_top_left = self.model.get_top_left_and_bottom_right()
        bottom_right = bottom_right_top_left[1]
        top_left = bottom_right_top_left[0]
        
        attack_range_point = top_left
        
        if self.direction == PlayerStates.FACING_LEFT:
            attack_range_point = (bottom_right[0] - attack.range[0], \
                                  top_left[1])
        
        attack_rect = pygame.Rect(attack_range_point, (attack.range[0], attack.range[1]))
        enemy_rect = pygame.Rect(enemy.model.position, \
                                 (enemy.model.width, enemy.model.height))
        
        in_range = attack_rect.colliderect(enemy_rect)
        
        return in_range
    
    def is_aerial(self):
        return int(self.model.position[1] + self.model.height) < gamestate.stage.ground.position[1]
    
    def apply_physics(self, duration):
        
        system = []
        
        self.set_velocity()
        self.model.resolve_self(duration)
        
        if self.is_aerial() == False:
            system.append(gamestate.stage.ground)
            
            if ((self.action.action_state == PlayerStates.FLOATING)
            or  (self.action.action_state == PlayerStates.JUMPING)):
                self.actions[PlayerStates.LANDING].set_player_state(self)
        
        if self.model.position[0] + self.model.width > gamestate.stage.right_wall.position[0]:
            system.append(gamestate.stage.right_wall)
        
        if self.model.position[0] < gamestate.stage.left_wall.position[0]:
            system.append(gamestate.stage.left_wall)
        
        self.model.resolve_system(system, duration)

class Action():
    def __init__(self, action_state):
        self.action_state = action_state
        self.right_animation = None
        self.left_animation = None
        self.animation = None
    
    def move_player(self, player):
        """place holder for function that sets the new position of the model"""
        start_time = player.model.animation_run_time
        end_time = start_time + player.model.time_passed
        
        if end_time >= self.animation.animation_length:
            end_time = self.animation.animation_length
            player.model.animation_run_time = end_time
            player.model.time_passed = start_time + player.model.time_passed - self.animation.animation_length
            # player.model.time_passed = 0
        else:
            player.model.animation_run_time += player.model.time_passed
        
        point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        
        player.model.set_point_position_in_place(point_deltas)
        
        player.apply_physics(end_time - start_time)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if self.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[player.action.action_state]:
            change_state = True
        
        return change_state
    
    def set_player_state(self, player, direction):
        player.action = self
        player.direction = direction
        player.model.animation_run_time = 0     
        
        if direction == PlayerStates.FACING_LEFT:
            self.animation = self.left_animation
        elif direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
        
        #Check if the player is in the air.  If not, shift back to the gRound after
        #changing to the new animation.
        if player.is_aerial():
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
        else:
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            player.model.shift((0, (gamestate.stage.ground.position[1] - player.model.height) - player.model.position[1]))
        
        # if current_x_position != player.model.position[0]:
            # print("start position")
            # print(current_x_position)
            # print("end position")
            # print(player.model.position[0])
        
        if player.model.time_passed > 0:
            self.move_player(player)

class InputAction():
    def __init__(self, action, key_release_action, key):
        self.action = action
        self.key_release_action = key_release_action
        self.key = key

class Walk(Action):
    def __init__(self, direction):
        Action.__init__(self, PlayerStates.WALKING)
        self.direction = direction
    
    def test_state_change(self, player):
        change_state = Action.test_state_change(self, player)
        
        if change_state:
            if ((player.action.action_state == PlayerStates.WALKING) and
                (player.action.direction != self.direction)):
                change_state = True
            elif ((player.action.action_state == PlayerStates.STANDING or
                   player.action.action_state == PlayerStates.LANDING) and
                  (player.dash_timer >= player.dash_timeout)):
                change_state = True
            else:
                change_state = False
        
        return change_state
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, self.direction)
        player.dash_timer = 0

class Run(Action):
    def __init__(self, direction):
        Action.__init__(self, PlayerStates.RUNNING)
        self.direction = direction
    
    def test_state_change(self, player):
        change_state = Action.test_state_change(self, player)
        
        if change_state:
            if ((player.action.action_state == PlayerStates.STANDING) and 
                (player.dash_timer < player.dash_timeout)):
                change_state = True
            elif ((player.action.action_state == PlayerStates.RUNNING) and
                  (player.direction != self.direction)):
                change_state = True
            else:
                change_state = False
        
        return change_state
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, self.direction)
        self.dash_timer = player.dash_timeout

class Crouch(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.CROUCHING)
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Jump(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.JUMPING)
    
    def test_state_change(self, player):
        change_state = False
        
        if ((player.action.action_state == PlayerStates.JUMPING) and
            (player.jump_timer < player.high_jump_timeout)):
            change_state = True
        else:
            change_state = Action.test_state_change(self, player)
        
        return change_state
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)
        player.model.velocity = (player.model.velocity[0], player.jump_speed)
        
        if player.jump_timer < player.high_jump_timeout:
            player.model.velocity = (player.model.velocity[0], player.high_jump_speed)
            player.jump_timer = player.high_jump_timeout
        else:
            player.jump_timer = 0

class Stand(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.STANDING)
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Land(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.LANDING)
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Float(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.FLOATING)
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Stun(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.STUNNED)
    
    def pull_player(self, player):
        pull_point_pos = player.pull_point.pos
        knock_back_vector = player.knockback_vector
        new_pos = (pull_point_pos[0] + knock_back_vector[0],
                   pull_point_pos[1] + knock_back_vector[1])
        point_to_lines = player.model.build_point_to_lines(player.model.lines.values())
        player.model.pull_point(player.pull_point,
                                new_pos,
                                player.pull_point,
                                [],
                                point_to_lines)
        
        #resync position of physics model and model
        player.model.position = player.model.get_reference_position()
        player.model.set_dimensions()
    
    def move_player(self, player):
        """place holder for function that sets the new position of the model"""
        
        if player.stun_timer < 500:
            self.pull_player(player)
        
        player.apply_physics(player.model.time_passed)
        
        if player.stun_timer >= player.stun_timeout:
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if player.stun_timer >= player.stun_timeout and player.health_meter > 0:
            change_state = True
        
        return change_state
    
    def set_player_state(self, player):
        player.action = self
        player.model.animation_run_time = 0
        
        if player.model.time_passed > 0:
            self.move_player(player)
        
        player.stun_timeout = 500 #min(500,int(1000 * ((player.health_max - player.health_meter) / player.health_max)) + 200)
        player.stun_timer = 0

class AttackTypes():
    PUNCH = "PUNCH"
    KICK = "KICK"
    
    ATTACK_TYPES = [PUNCH, KICK]

class Attack(Action):
    def __init__(self, attack_type):
        Action.__init__(self, PlayerStates.ATTACKING)
        self.attack_type = attack_type
        self.attack_lines = []
        self.range = (0,0)
        self.use_animation_physics = False
    
    def set_attack_data(self, model):
        """called after the animations of an attack has been set to intialize other data"""
        self.range = (self.right_animation.get_widest_frame().image_width(), 
                      self.right_animation.get_tallest_frame().image_height())
        self.attack_lines = self.get_attack_lines(model)
    
    def move_player(self, player):
        
        start_time = player.model.animation_run_time
        end_time = start_time + player.model.time_passed
        
        if end_time > self.animation.animation_length:
            end_time = self.animation.animation_length
            player.model.animation_run_time = end_time
            player.model.time_passed = start_time + player.model.time_passed - end_time
            # player.model.time_passed = 0
        else:
            player.model.animation_run_time += player.model.time_passed
        
        point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        
        player.model.set_point_position_in_place(point_deltas)
        
        if self.use_animation_physics:
            self.apply_animation_physics(player, start_time, end_time)
        else:
            player.apply_physics(end_time - start_time)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        player.action = self
        player.model.animation_run_time = 0     
        player.current_attack = self
        
        if player.direction == PlayerStates.FACING_LEFT:
            self.animation = self.left_animation
        elif player.direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
        
        #Check if the player is in the air.  If not, shift back to the gRound after
        #changing to the new animation.
        if player.is_aerial():
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
        else:
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            player.model.shift((0, (gamestate.stage.ground.position[1] - player.model.height) - player.model.position[1]))
        
        player.reset_point_damage()
        
        #print('player bottom')
        #print(player.model.position[1] + player.model.height)
        #print('player height')
        #print(player.model.height)
        #print('ground top')
        #print(gamestate.stage.ground.position[1])
        
        if player.is_aerial():
            self.use_animation_physics = False
        else:
            self.use_animation_physics = True
        
        #print(self.use_animation_physics)
        
        if player.model.time_passed > 0:
            self.move_player(player)
    
    def get_attack_lines(self, model):
        """get the lines that used to attack in the animation"""
        attack_lines = {}
        
        if self.attack_type == AttackTypes.PUNCH:
            attack_lines[stick.LineNames.RIGHT_UPPER_ARM] = model.lines[stick.LineNames.RIGHT_UPPER_ARM]
            attack_lines[stick.LineNames.RIGHT_FOREARM] = model.lines[stick.LineNames.RIGHT_FOREARM]
            attack_lines[stick.LineNames.LEFT_UPPER_ARM] = model.lines[stick.LineNames.LEFT_UPPER_ARM]
            attack_lines[stick.LineNames.LEFT_FOREARM] = model.lines[stick.LineNames.LEFT_FOREARM]
        elif self.attack_type == AttackTypes.KICK:
            attack_lines[stick.LineNames.RIGHT_UPPER_LEG] = model.lines[stick.LineNames.RIGHT_UPPER_LEG]
            attack_lines[stick.LineNames.RIGHT_LOWER_LEG] = model.lines[stick.LineNames.RIGHT_LOWER_LEG]
            attack_lines[stick.LineNames.LEFT_UPPER_LEG] = model.lines[stick.LineNames.LEFT_UPPER_LEG]
            attack_lines[stick.LineNames.LEFT_LOWER_LEG] = model.lines[stick.LineNames.LEFT_LOWER_LEG]
        
        return attack_lines
    
    def apply_animation_physics(self, player, start_time, end_time):
        """returns the displacement of a point given the start time of the movement and
        the end time of the movement.  Time resets to 0 at start of animation and 
        increments in milliseconds.
        
        point_id: id of the point to return deltas for"""
        start_frame_index = self.animation.get_frame_index_at_time(start_time)
        end_frame_index = self.animation.get_frame_index_at_time(end_time)
        
        x_velocity = 0
        y_velocity = 0
        
        for frame_index in range(start_frame_index, end_frame_index + 1):
            displacement_start_time = self.animation.frame_start_times[frame_index]
            displacement_end_time = (displacement_start_time + 
                                     self.animation.frame_times[frame_index])
            elapsed_time = 0
            if frame_index == start_frame_index:
                displacement_start_time = start_time
                elapsed_time = start_time - self.animation.frame_start_times[frame_index]
                displacement_end_time = (displacement_start_time + 
                                         self.animation.frame_times[frame_index] - 
                                         elapsed_time)
            
            if frame_index == end_frame_index:
                displacement_end_time = end_time
            
            duration = displacement_end_time - displacement_start_time
            
            x_velocity = self.animation.get_lateral_velocity(displacement_start_time,frame_index)
            y_velocity = self.animation.get_jump_velocity(displacement_start_time,frame_index)
            
            player.model.velocity = (x_velocity, y_velocity)
            player.apply_physics(duration)

class ActionFactory():
    """factory class for creating attack objects"""
    
    def __init__(self):
        pass
    
    def create_stand(self, animation):
        return_stand = Stand()
        
        self._set_action_animations(return_stand, animation)
        
        return return_stand
    
    def create_land(self, animation):
        return_land = Land()
        
        self._set_action_animations(return_land, animation)
        
        return return_land
    
    def create_float(self, animation):
        return_float = Float()
        
        self._set_action_animations(return_float, animation)
        
        return return_float
    
    def create_walk(self, direction, animation):
        """create a movement model for the given movement state"""
        return_walk = Walk(direction)
        
        if direction == PlayerStates.FACING_RIGHT:
            return_walk.right_animation = self.crte_player_animation(animation)
            return_walk.right_animation.set_animation_point_path_data(Player.ACCELERATION)
        if direction == PlayerStates.FACING_LEFT:
            return_walk.left_animation = self.crte_player_animation(animation.flip())
            return_walk.left_animation.set_animation_point_path_data(Player.ACCELERATION)
        
        return return_walk
    
    def create_run(self, direction, animation):
        return_run = Run(direction)
        
        if direction == PlayerStates.FACING_RIGHT:
            return_run.right_animation = self.crte_player_animation(animation)
            return_run.right_animation.set_animation_point_path_data(Player.ACCELERATION)
        if direction == PlayerStates.FACING_LEFT:
            return_run.left_animation = self.crte_player_animation(animation.flip())
            return_run.left_animation.set_animation_point_path_data(Player.ACCELERATION)
        
        return return_run
    
    def create_jump(self, animation):
        return_jump = Jump()
        
        self._set_action_animations(return_jump, animation)
        
        return return_jump
    
    def create_crouch(self, animation):
        return_crouch = Crouch()
        
        self._set_action_animations(return_crouch, animation)
        
        return return_crouch
    
    def create_stun(self):
        return_stun = Stun()
        
        return return_stun
    
    def create_attack(self, attack_type, animation, model):
        """create an attack model for the given attack type"""
        return_attack = Attack(attack_type)
        
        self._set_action_animations(return_attack, animation)
        
        return_attack.set_attack_data(model)
        
        return return_attack
    
    def _set_action_animations(self, action, animation):
        action.right_animation = self.crte_player_animation(animation)
        action.right_animation.set_animation_point_path_data(Player.ACCELERATION)
        action.right_animation.set_animation_reference_point_path_data(Player.ACCELERATION,
                                                                       physics.GRAVITY)
        action.left_animation = self.crte_player_animation(animation.flip())
        action.left_animation.set_animation_point_path_data(Player.ACCELERATION)
        action.left_animation.set_animation_reference_point_path_data(Player.ACCELERATION,
                                                                      physics.GRAVITY)
    
    def crte_player_animation(self, animation):
        rtn_animation = copy.deepcopy(animation)
        rtn_animation.set_animation_height(Player.ANIMATION_HEIGHT, \
                                           Player.REFERENCE_HEIGHT)
        rtn_animation.set_frame_deltas()
        rtn_animation.set_animation_deltas()
        
        return rtn_animation

def draw_model(player):
    """draws the model to the screen"""
    enclosing_rect = pygame.Rect(*player.model.get_enclosing_rect())
    gamestate.new_dirty_rects.append(enclosing_rect)
    
    pygame.draw.rect(gamestate.screen, (100,100,100),enclosing_rect,1)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_point(point, player.color)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_circle(line, player.color)
        else:
            draw_line(line, player)

def draw_line(line, player):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    pygame.draw.line(gamestate.screen, \
                    player.color, \
                    point1, \
                    point2, \
                    int(7))
    
    health_point1 = point1
    health_level = float(player.health_meter) / player.health_max
    x_delta = health_level * (point2[0] - health_point1[0])
    y_delta = health_level * (point2[1] - health_point1[1])
    health_point2 = (point1[0] + x_delta, point1[1] + y_delta)
    
    pygame.draw.line(gamestate.screen, \
                    player.health_color, \
                    health_point1, \
                    health_point2, \
                    int(5))

def draw_circle(circle, color):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(gamestate.screen, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius))
    
    pygame.draw.circle(gamestate.screen, \
                      (0, 100, 0), \
                      (int(pos[0]), int(pos[1])), \
                      int(radius - 1))

def draw_point(point, color):
    """Draws a point on a surface
    
    surface: the pygame surface to draw the point on"""
    #pygame.draw.rect(gamestate.screen, (100,100,100),point.get_enclosing_rect(),1)
    position = point.pixel_pos()
    
    pygame.draw.circle(gamestate.screen, \
                       color, \
                       position, \
                       int(3))
    
    pygame.draw.circle(gamestate.screen, \
                       (0,0,0), \
                       position, \
                       int(2))
