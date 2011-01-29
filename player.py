import copy
import math
from random import choice

import pygame

import gamestate
import animation
import animationexplorer
import physics
import mathfuncs
import stick
import pulltool
from controlsdata import InputActionTypes
import settingsdata

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
    TRANSITION = 'TRANSITION'
    
    MOVEMENTS = [STANDING,WALKING,RUNNING,JUMPING,FLOATING, \
                 LANDING,CROUCHING]
    
    UNBOUND_MOVEMENTS = [STANDING,FLOATING,LANDING,STUNNED, \
                        TRANSITION]
    
    PRESSED_KEY_STATE_TRANSITIONS = {
        STANDING : [WALKING,RUNNING,JUMPING,CROUCHING,ATTACKING],
        WALKING : [WALKING,STANDING,JUMPING,CROUCHING,ATTACKING],
        RUNNING : [RUNNING,STANDING,JUMPING,CROUCHING,ATTACKING],
        CROUCHING : [STANDING,ATTACKING],
        JUMPING : [FLOATING,LANDING,ATTACKING],
        LANDING : [STANDING,CROUCHING,ATTACKING,JUMPING,WALKING],
        FLOATING : [LANDING,ATTACKING],
        ATTACKING : [STANDING, FLOATING],
        STUNNED : [FLOATING,LANDING,STANDING],
        BLOCKING : [STANDING,CROUCHING],
        TRANSITION : [RUNNING]
    }

class Player():
    ANIMATION_HEIGHT = 100
    REFERENCE_HEIGHT = 400
    ACCELERATION = .00600
    TRANSITION_ACCELERATION = .006
    STUN_ACCELERATION = .002
    AERIAL_ACCELERATION = .01
    MAX_DRIFT_VELOCITY_COMPONENT = .3
    
    def __init__(self, position):
        self.player_type = None
        self.current_attack = None
        self.action = None
        self.color = (255,255,255)
        self.outline_color = self.color
        self.current_animation = None
        self.direction = PlayerStates.FACING_RIGHT
        self.stun_timeout = 500
        self.stun_timer = self.stun_timeout
        self.dash_timeout = 500
        self.dash_timer = self.dash_timeout
        self.high_jump_timeout = 300
        self.short_jump_timeout = 200
        self.jump_timer = self.high_jump_timeout
        self.aerial_acceleration_timer = 0
        self.drift_velocity_component = 0
        self.model = physics.Model(position)
        self.walk_speed = .4
        self.run_speed = .75
        self.jump_speed = -.5
        self.high_jump_speed = -.75
        self.aerial_acceleration = .005
        self.actions = {}
        self.knockback_vector = (0,0)
        self.interaction_vector = (0,0)
        self.interaction_point = None
        self.knockback_multiplier = 4
        self.health_max = 2000
        self.health_meter = self.health_max
        self.health_color = (0,0,100)
        self.moveset = None
        self.point_name_to_point_damage = {} #Point name to PointDamage object
        self.previous_point_positions = {}
        
        self.play_sound_indicator = True
        self.sound_channel = None
        self.hit_sound_channel = None
        
        self.movement_sounds = {
            PlayerStates.WALKING : [
                pygame.mixer.Sound("sounds/step1-sound.ogg"),
                pygame.mixer.Sound("sounds/step2-sound.ogg"),
                pygame.mixer.Sound("sounds/step3-sound.ogg"),
                pygame.mixer.Sound("sounds/step4-sound.ogg")
            ],
            PlayerStates.RUNNING : [
                pygame.mixer.Sound("sounds/step1-sound.ogg"),
                pygame.mixer.Sound("sounds/step2-sound.ogg"),
                pygame.mixer.Sound("sounds/step3-sound.ogg"),
                pygame.mixer.Sound("sounds/step4-sound.ogg")
            ],
            PlayerStates.JUMPING : [
                pygame.mixer.Sound("sounds/jump-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.movement_sounds)
        self.attack_sounds = {
            InputActionTypes.WEAK_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.MEDIUM_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.STRONG_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.WEAK_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ],
            InputActionTypes.MEDIUM_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ],
            InputActionTypes.STRONG_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.attack_sounds)
        self.hit_sounds = {
            InputActionTypes.WEAK_PUNCH : [
                pygame.mixer.Sound("sounds/hit-sound.ogg")
            ],
            InputActionTypes.MEDIUM_PUNCH : [
                pygame.mixer.Sound("sounds/medium-hit-sound.ogg")
            ],
            InputActionTypes.STRONG_PUNCH : [
                pygame.mixer.Sound("sounds/strong-hit-sound.ogg")
            ],
            InputActionTypes.WEAK_KICK : [
                pygame.mixer.Sound("sounds/hit-sound.ogg")
            ],
            InputActionTypes.MEDIUM_KICK : [
                pygame.mixer.Sound("sounds/medium-hit-sound.ogg")
            ],
            InputActionTypes.STRONG_KICK : [
                pygame.mixer.Sound("sounds/strong-hit-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.hit_sounds)
    
    def set_sound_volumes(self, sound_dict):
        for sound_list in sound_dict.values():
            for sound in sound_list:
                sound.set_volume(settingsdata.get_sound_volume())
    
    def init_state(self):
        self.model.load_points()
        self.model.load_lines()
        self.init_point_damage_dictionary()
    
    def handle_events(self):
        
        self.model.time_passed = gamestate.time_passed
        
        self.set_previous_point_positions()
        
        self.action.move_player(self)
        
        if self.action.action_state == PlayerStates.ATTACKING:
            self.update_point_damage()
        
        self.set_outline_color()
        
        if self.play_sound_indicator:
            self.play_sound()
            self.play_sound_indicator = False
        
        if self.dash_timer < self.dash_timeout:
            self.dash_timer += gamestate.time_passed
        
        if self.jump_timer < self.high_jump_timeout:
            self.jump_timer += gamestate.time_passed
        
        if self.stun_timer < self.stun_timeout:
            self.stun_timer += gamestate.time_passed
    
    def play_sound(self):
        
        player_state = self.get_player_state()
        
        if not self.movement_sound_is_playing():
            if player_state == PlayerStates.ATTACKING:
                sound = choice(self.attack_sounds[self.get_attack_type()])
                self.start_sound(sound)
                
            elif player_state in self.movement_sounds.keys():
                sound = choice(self.movement_sounds[player_state])
                self.start_sound(sound)
    
    def start_sound(self, sound):
        if self.sound_channel == None:
            self.sound_channel = sound.play()
        else:
            self.sound_channel.stop()
            self.sound_channel = sound.play()
    
    def movement_sound_is_playing(self):
        if (self.sound_channel == None or
            self.sound_channel.get_busy() == False):
            return False
        else:
            return True
    
    def hit_sound_is_playing(self):
        if (self.hit_sound_channel == None or
            self.hit_sound_channel.get_busy() == False):
            return False
        else:
            return True
    
    def play_hit_sound(self):
        if self.get_attack_type() in self.hit_sounds.keys():
            self.hit_sound_channel = choice(self.hit_sounds[self.get_attack_type()]).play()
        else:
            self.hit_sound_channel =  pygame.mixer.Sound().play()
    
    def set_outline_color(self):
        if self.get_player_state() == PlayerStates.STUNNED:
            if (self.stun_timer % 30) >= 15:
                self.outline_color = (255, 255, 0)
            else:
                self.outline_color = (255, 0, 0)
        else:
            self.outline_color = self.color
    
    def get_aerial_acceleration(self, direction):
        """returns the acceleration when a player is moving while floating.
        
        direction should -1, 0 or 1 for the direction the acceleration is going in."""
        new_component = self.drift_velocity_component + (direction * Player.AERIAL_ACCELERATION)
        
        if abs(new_component) <= Player.MAX_DRIFT_VELOCITY_COMPONENT:
            
            self.drift_velocity_component = new_component
            
            return direction * Player.AERIAL_ACCELERATION
        
        else:
            
            return 0
    
    def move_to_ground(self):
        
        position = (
            self.model.position[0], 
            int(math.ceil(gamestate.stage.ground.position[1] - self.model.height))
        )
        
        self.model.move_model(position)
    
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
            self.transition(self.actions[PlayerStates.FLOATING])
        elif self.action.action_state == PlayerStates.LANDING:
            self.transition(self.get_neutral_state())
        elif self.action.action_state == PlayerStates.ATTACKING:
            self.current_attack = None
            self.transition(self.get_neutral_state())
        elif self.action.action_state == PlayerStates.TRANSITION:
            self.action.next_action.set_player_state(self)
        elif self.action.action_state == PlayerStates.STUNNED:
            self.transition(self.get_neutral_state())
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
    
    def transition(self, next_state):
        transition = Transition()
        transition.init_transition(self, next_state)
        transition.set_player_state(self)
    
    def set_neutral_state(self):
        self.get_neutral_state().set_player_state(self)
    
    def get_neutral_state(self):
        if self.get_player_state() == PlayerStates.LANDING:
            return self.actions[PlayerStates.STANDING]
        else:
            if self.is_aerial():
                return self.actions[PlayerStates.FLOATING]
            else:
                return self.actions[PlayerStates.STANDING]
    
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
        
        if self.actions[player_state].test_state_change(self):
            self.actions[player_state].set_player_state(self)
    
    def get_attack_lines(self):
        return self.action.attack_lines
    
    def get_point(self, point_name):
        return self.model.points[point_name]
    
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
                ) + self.get_extension_damage(
                    point_name,
                    current_point_positions_dictionary
                )
            
            #use multiplier to adjust damage given the attack type
            self.point_name_to_point_damage[point_name] += \
                additional_damage * self.action.get_damage_multiplier()
    
    def get_extension_damage(self, point_name, current_point_positions):
        if point_name == stick.PointNames.RIGHT_HAND:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.RIGHT_ELBOW,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_ELBOW:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_TOP,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_HAND:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.LEFT_ELBOW,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_ELBOW:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_TOP,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_FOOT:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.RIGHT_KNEE,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_KNEE:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_BOTTOM,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_FOOT:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.LEFT_KNEE,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_KNEE:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_BOTTOM,
                current_point_positions
            )
        else:
            return 0
    
    def get_line_length_change(
        self,
        point1_name,
        point2_name,
        current_point_positions
    ):
        point1_prev_position = self.previous_point_positions[point1_name]
        point2_prev_position = self.previous_point_positions[point2_name]
        
        prev_line_length = mathfuncs.distance(
            point1_prev_position,
            point2_prev_position
        )
        
        point1_position = current_point_positions[point1_name]
        point2_position = current_point_positions[point2_name]
        
        current_line_length = mathfuncs.distance(
            point1_position,
            point2_position
        )
        
        return abs(current_line_length - prev_line_length)
    
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
    
    def get_stun_timeout(self):
        """only call when attacking"""
        return 1 / self.get_attack_acceleration()
    
    def get_attack_type(self):
        return self.action.attack_type
    
    def get_attack_acceleration(self):
        
        if (self.get_attack_type() in 
        [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]):
            return 2 * Player.ACCELERATION
            
        elif (self.get_attack_type() in 
        [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]):
            return Player.ACCELERATION
            
        elif (self.get_attack_type() in 
        [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]):
            return .5 * Player.ACCELERATION
    
    def set_stun_timeout(self, timeout):
        self.stun_timeout = timeout
    
    def set_pull_point(self, point):
        self.pull_point = point
    
    def pull_point(self, deltas):
        pull_point_pos = self.interaction_point.pos
        new_pos = (pull_point_pos[0] + deltas[0],
                   pull_point_pos[1] + deltas[1])
        point_to_lines = self.model.build_point_to_lines(self.model.lines.values())
        
        self.model.pull_point(
            self.interaction_point,
            new_pos,
            self.interaction_point,
            [],
            point_to_lines
        )
        
        self.model.position = self.model.get_reference_position()
        self.model.set_dimensions()
    
    def set_health(self, health_value):
        
        self.health_meter = health_value
    
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
        enemy_rect = pygame.Rect(enemy.model.position, (enemy.model.width, enemy.model.height))
        
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
            
            if (((self.action.action_state == PlayerStates.FLOATING)
            or  (self.action.action_state == PlayerStates.JUMPING)) and
            (mathfuncs.sign(self.model.velocity[1]) > 0)):
                self.transition(self.actions[PlayerStates.LANDING])
        
        if self.model.orientation == physics.Orientations.FACING_RIGHT:
            if self.model.position[0] + self.model.width > gamestate.stage.right_wall.position[0]:
                system.append(gamestate.stage.right_wall)
        elif self.model.orientation == physics.Orientations.FACING_LEFT:
            if self.model.position[0] > gamestate.stage.right_wall.position[0]:
                system.append(gamestate.stage.right_wall)
        
        if self.model.orientation == physics.Orientations.FACING_RIGHT:
            if self.model.position[0] < gamestate.stage.left_wall.position[0]:
                system.append(gamestate.stage.left_wall)
        elif self.model.orientation == physics.Orientations.FACING_LEFT:
            if self.model.position[0] - self.model.width < gamestate.stage.left_wall.position[0]:
                system.append(gamestate.stage.left_wall)
        
        self.model.resolve_system(system, duration)

class Action():
    def __init__(self, action_state):
        self.action_state = action_state
        self.right_animation = None
        self.left_animation = None
        self.animation = None
        self.direction = PlayerStates.FACING_RIGHT
        self.last_frame_index = 0
        self.current_sound_channel = None
    
    def move_player(self, player):
        """place holder for function that sets the new position of the model"""
        start_time = player.model.animation_run_time
        end_time = start_time + player.model.time_passed
        
        if end_time >= self.animation.animation_length:
            end_time = self.animation.animation_length
            player.model.animation_run_time = end_time
            player.model.time_passed = \
                start_time + player.model.time_passed - self.animation.animation_length
            # player.model.time_passed = 0
        else:
            player.model.animation_run_time += player.model.time_passed
        
        frame_index = self.animation.get_frame_index_at_time(end_time)
        player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
        
        #point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        #player.model.set_point_position_in_place(point_deltas)
        
        player.apply_physics(end_time - start_time)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if self.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[player.action.action_state]:
            change_state = True
        
        return change_state
    
    def test_change_to_action(self, action):
        change_state = False
        
        if action.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[self.action_state]:
            change_state = True
        
        return change_state
    
    def set_player_state(self, player, direction):
        self.last_frame_index = 0
        
        player.action = self
        player.direction = direction
        player.model.animation_run_time = 0     
        
        if direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        #Check if the player is in the air.  If not, shift back to the gRound after
        #changing to the new animation.
        if player.is_aerial():
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            
        else:
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            player.move_to_ground()
        
        # if current_x_position != player.model.position[0]:
            # print("start position")
            # print(current_x_position)
            # print("end position")
            # print(player.model.position[0])
        
        if player.model.time_passed > 0:
            self.move_player(player)

class Transition(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.TRANSITION)
        self.next_action = None
        self.last_action = None
    
    def init_transition(self, player, next_action):
        self.set_animation(player, next_action)
        self.next_action = next_action
        self.last_action = player.action
    
    def set_animation(self, player, next_action):
        last_frame_index = len(player.action.animation.frames) - 1
        first_frame = self.create_first_frame(player)
        
        last_frame = self.create_last_frame(first_frame, player.action, next_action)
        
        #when running or walking is the next action state the reference 
        #position may change. So special logic is here to handle correctly
        #orienting the transition animations
        if next_action.action_state in [PlayerStates.WALKING, PlayerStates.RUNNING]:
            if (player.model.orientation == physics.Orientations.FACING_RIGHT and
            next_action.direction == PlayerStates.FACING_LEFT):
                first_frame.flip()
            elif (player.model.orientation == physics.Orientations.FACING_LEFT):
                if (next_action.action_state in [PlayerStates.WALKING, PlayerStates.RUNNING] and
                    next_action.direction == PlayerStates.FACING_RIGHT):
                    pass
                else:
                    first_frame.flip()
        elif player.model.orientation == physics.Orientations.FACING_LEFT:
            first_frame.flip()
        
        last_frame.set_position(first_frame.get_reference_position())
        
        transition_animation = animation.Animation()
        
        transition_animation.point_names = player.action.right_animation.point_names
        transition_animation.frames = [first_frame, last_frame]
        transition_animation.set_frame_deltas()
        transition_animation.set_animation_deltas()
        transition_animation.set_animation_point_path_data(Player.TRANSITION_ACCELERATION)
        
        self.right_animation = transition_animation
        self.left_animation = transition_animation
    
    def create_first_frame(self, player):
        """creates a frame from the model of the player"""
        
        first_frame = \
            copy.deepcopy(
                player.action.animation.frames[0]
            )
        
        for point_name, point_id in player.action.animation.point_names.iteritems():
            position = player.model.points[point_name].pos
            first_frame.point_dictionary[point_id].pos = (position[0], position[1])
        
        return first_frame
    
    def create_last_frame(self, first_frame, current_action, next_action):
        """Creates a frame with ids that match the first frame"""
        
        last_frame = copy.deepcopy(first_frame)
        last_frame_point_positions = next_action.right_animation.frame_deltas[0]
        
        for point_name, point_id in current_action.right_animation.point_names.iteritems():
            position = last_frame_point_positions[point_name]
            last_frame.point_dictionary[point_id].pos = position
        
        return last_frame
        
    def move_player(self, player):
        """place holder for function that sets the new position of the model"""
        start_time = player.model.animation_run_time
        end_time = start_time + player.model.time_passed
        
        if end_time >= self.animation.animation_length:
            end_time = self.animation.animation_length
            player.model.animation_run_time = end_time
            player.model.time_passed = \
                start_time + player.model.time_passed - self.animation.animation_length
            
        else:
            player.model.animation_run_time += player.model.time_passed
        
        point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        player.model.set_point_position_in_place(point_deltas)
        
        if self.last_action.action_state in [PlayerStates.WALKING, PlayerStates.RUNNING, PlayerStates.STANDING, PlayerStates.CROUCHING]:
            player.move_to_ground()
        
        player.apply_physics(end_time - start_time)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        if self.next_action.action_state in [PlayerStates.WALKING, PlayerStates.RUNNING]:
            Action.set_player_state(self, player, self.next_action.direction)
            
        else:
            Action.set_player_state(self, player, player.direction)
        
        #set friction so that stun friction doesn't remain
        player.model.friction = physics.FRICTION
    
class InputAction():
    def __init__(self, action, key_release_action, key):
        self.action = action
        self.key_release_action = key_release_action
        self.key = key

class GroundMovement():
    def __init__(self):
        self.point_on_ground = {
                stick.PointNames.RIGHT_HAND : False,
                stick.PointNames.LEFT_HAND : False,
                stick.PointNames.RIGHT_FOOT : False,
                stick.PointNames.LEFT_FOOT : False
            }
    
    def play_sounds(self, player):
        
        for point_name, on_ground in self.point_on_ground.iteritems():
            if player.model.points[point_name].pos[1] <= gamestate.stage.ground.position[1]:
                if not on_ground:
                    player.play_sound_indicator = True
                    self.point_on_ground[point_name] = True
            else:
                if on_ground:
                    self.point_on_ground[point_name] = False
    
    def init_points_on_ground(self, player):
        for point_name in self.point_on_ground.keys():
            if player.model.points[point_name].pos[1] <= gamestate.stage.ground.position[1]:
                self.point_on_ground[point_name] = True
            else:
                self.point_on_ground[point_name] = False

class Walk(Action, GroundMovement):
    def __init__(self):
        Action.__init__(self, PlayerStates.WALKING)
        GroundMovement.__init__(self)
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
        
        self.play_sounds(player)
    
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
        self.init_points_on_ground(player)

class Run(Action, GroundMovement):
    def __init__(self):
        Action.__init__(self, PlayerStates.RUNNING)
        GroundMovement.__init__(self)
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
        
        self.play_sounds(player)
    
    def test_state_change(self, player):
        change_state = Action.test_state_change(self, player)
        
        if change_state:
            if ((player.action.action_state == PlayerStates.STANDING) and 
                (player.dash_timer < player.dash_timeout)):
                change_state = True
            elif (player.get_player_state() == PlayerStates.TRANSITION and
            player.action.next_action.action_state == PlayerStates.STANDING):
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
        self.init_points_on_ground(player)

class Crouch(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.CROUCHING)
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Jump(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.JUMPING)
    
    def test_state_change(self, player):
        change_state = False
        
        if ((player.action.action_state == PlayerStates.JUMPING) and
            (player.jump_timer < player.high_jump_timeout) and
            (player.jump_timer > player.short_jump_timeout)):
            change_state = True
        else:
            change_state = Action.test_state_change(self, player)
        
        return change_state
    
    def set_player_jump_velocity(self, player):
        player.model.velocity = (player.model.velocity[0], player.jump_speed)
        
        player.drift_velocity_component = 0
        
        player.play_sound_indicator = True
        
        if ((player.jump_timer > player.short_jump_timeout) and
        (player.jump_timer < player.high_jump_timeout)):
            player.model.velocity = (player.model.velocity[0], player.high_jump_speed)
            player.jump_timer = player.high_jump_timeout
        elif player.jump_timer >= player.high_jump_timeout:
            player.jump_timer = 0
    
    def set_player_state(self, player):
        self.set_player_jump_velocity(player)
        Action.set_player_state(self, player, player.direction)

class Stand(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.STANDING)
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, player.direction)

class Land(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.LANDING)
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
    
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
        self.physics_vector = (0,0)
        self.toy_model = physics.Model((0,0))
        self.toy_model.init_stick_data()
    
    def set_animation(self, player):
        """creates a stun animation from the player model."""
        stun_animation = animation.Animation()
        stun_animation.frames = []
        stun_animation.point_names = player.action.animation.point_names
        
        first_frame = copy.deepcopy(player.action.animation.frames[0])
        
        self.init_toy_model_point_positions(player)
        self.physics_vector = (0,0)
        
        new_frame = self.save_model_point_positions_to_frame(first_frame, stun_animation.point_names)
        
        stun_animation.frames.append(new_frame)
        
        for i in range(10):
            self.pull_toy_model(player)
        
        new_frame = self.save_model_point_positions_to_frame(first_frame, stun_animation.point_names)
        stun_animation.frames.append(new_frame)
        
        if player.model.orientation == physics.Orientations.FACING_LEFT:
            stun_animation = stun_animation.flip()
        
        stun_animation.set_frame_deltas()
        stun_animation.set_animation_deltas()
        stun_animation.set_animation_point_path_data(Player.STUN_ACCELERATION)
        
        self.right_animation = stun_animation
        self.left_animation = stun_animation
        self.animation = stun_animation
    
    def init_toy_model_point_positions(self, player):
        """makes the stun action's model match the player model"""
        
        for point_name, point in self.toy_model.points.iteritems():
            position = player.model.points[point_name].pos
            point.pos = (position[0], position[1])
        
        for line in self.toy_model.lines.values():
            line.set_length()
        
        self.toy_model.position = self.toy_model.get_reference_position()
        self.toy_model.set_dimensions()
    
    def save_model_point_positions_to_frame(self, frame, point_names):
        """Creates a frame with ids that match the first frame"""
        
        save_frame = copy.deepcopy(frame)
        
        for point_name, point_id in point_names.iteritems():
            position = self.toy_model.points[point_name].pos
            save_frame.point_dictionary[point_id].pos = (position[0], position[1])
        
        return save_frame
    
    def pull_toy_model(self, player):
        
        self.pull_toy_point(self.toy_model.points[player.interaction_point.name], player.interaction_vector)
        
        #self.toy_model.position = self.toy_model.get_reference_position()
        #self.toy_model.set_dimensions()
    
    def pull_toy_point(self, point, deltas):
        pull_point_pos = point.pos
        
        new_pos = (pull_point_pos[0] + deltas[0],
                   pull_point_pos[1] + deltas[1])
        point_to_lines = self.toy_model.build_point_to_lines(self.toy_model.lines.values())
        
        self.toy_model.pull_point(
            point,
            new_pos,
            point,
            [],
            point_to_lines
        )
        
        #import pdb;pdb.set_trace()
    
    def move_player(self, player):
        """place holder for function that sets the new position of the model"""
        
        if player.model.animation_run_time < self.animation.animation_length:
            start_time = player.model.animation_run_time
            end_time = start_time + player.model.time_passed    
            
            if end_time >= self.animation.animation_length:
                end_time = self.animation.animation_length
                player.model.animation_run_time = end_time
                player.model.time_passed = \
                    start_time + player.model.time_passed - self.animation.animation_length
                
            else:
                player.model.animation_run_time += player.model.time_passed
            
            #frame_index = self.animation.get_frame_index_at_time(end_time)
            #player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
            
            point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
            player.model.set_point_position_in_place(point_deltas)
        else:
            self.set_animation(player)
            player.model.animation_run_time = 0
            
        player.apply_physics(player.model.time_passed)
        
        if player.stun_timer >= player.stun_timeout:
            
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if player.stun_timer >= player.stun_timeout and player.health_meter > 0:
            change_state = True
        
        return change_state
    
    def set_player_state(self, player):
        
        self.set_animation(player)
        if (player.action.current_sound_channel != None and
        player.action.current_sound_channel.get_busy()):
            player.action.current_sound_channel.stop()
        
        player.action = self
        player.model.animation_run_time = 0
        
        player.stun_timeout = 500 #min(500,int(1000 * ((player.health_max - player.health_meter) / player.health_max)) + 200)
        player.stun_timer = 0
        player.model.friction = physics.STUN_FRICTION
        
        if player.model.time_passed > 0:
            self.move_player(player)

class AttackTypes():
    PUNCH = "PUNCH"
    KICK = "KICK"
    
    ATTACK_TYPES = [PUNCH, KICK]

class Elevations():
    GROUNDED = "GROUNDED"
    AERIAL = "AERIAL"

class Attack(Action):
    PUNCH_LINE_NAMES = [
        stick.LineNames.LEFT_UPPER_ARM,
        stick.LineNames.LEFT_FOREARM,
        stick.LineNames.RIGHT_UPPER_ARM,
        stick.LineNames.RIGHT_FOREARM
    ]
    
    KICK_LINE_NAMES = [
        stick.LineNames.LEFT_UPPER_LEG,
        stick.LineNames.LEFT_LOWER_LEG,
        stick.LineNames.RIGHT_UPPER_LEG,
        stick.LineNames.RIGHT_LOWER_LEG
    ]
    
    def __init__(self, attack_type):
        Action.__init__(self, PlayerStates.ATTACKING)
        self.attack_type = attack_type
        self.attack_lines = []
        self.range = (0,0)
        self.use_animation_physics = False
        self.acceleration = Player.ACCELERATION
        self.frame_sounds = []
        self.frame_sound_index = 0
        self.current_sound_channel = None
        self.hit_sound = None
        self.hit_sound_channel = None
        self.elevation = Elevations.GROUNDED
        self.overriden = False
    
    def set_frame_sounds(self):
        """Defines sounds for each frame index of the attack"""
        
        self.frame_sounds.append(True)
        
        for frame_index in range(1, len(self.right_animation.frames) - 1):
            if self.attack_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.MEDIUM_PUNCH, InputActionTypes.STRONG_PUNCH]:
                self.frame_sounds.append(
                    self.test_delta_change(stick.PointNames.RIGHT_HAND, frame_index) or
                    self.test_delta_change(stick.PointNames.LEFT_HAND, frame_index)
                )
            else:
                self.frame_sounds.append(
                    self.test_delta_change(stick.PointNames.RIGHT_FOOT, frame_index) or
                    self.test_delta_change(stick.PointNames.LEFT_FOOT, frame_index)
                )
    
    def test_delta_change(self, point_name, frame_index):
        delta = self.right_animation.animation_deltas[frame_index][point_name]
        last_delta = self.right_animation.animation_deltas[frame_index - 1][point_name]
        
        if (mathfuncs.sign(delta[0]) != mathfuncs.sign(last_delta[0])): #or
        #mathfuncs.sign(delta[1]) != mathfuncs.sign(last_delta[1])):
            return True
        else:
            return False
    
    def set_acceleration(self, action_type):
        """sets the animation acceleration for a given InputActionType.  Only
        attack input action types are valid."""
        
        if action_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]:
            self.acceleration = 2 * Player.ACCELERATION
            
        elif action_type in [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]:
            self.acceleration = Player.ACCELERATION
            
        elif action_type in [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]:
            self.acceleration = .5 * Player.ACCELERATION
    
    def test_state_change(self, player):
        
        if player.get_player_state() == PlayerStates.STUNNED:
            return False
        else:
            return Action.test_state_change(self, player)
    
    def get_damage_multiplier(self):
        return Player.ACCELERATION / (2 * self.acceleration)
    
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
        
        frame_index = self.animation.get_frame_index_at_time(end_time)
        
        if frame_index == self.frame_sound_index:
            player.play_sound_indicator = True
                
            self.frame_sound_index += 1
        
        #apply animation physics first to determine what the player's position 
        #should be.
        if self.use_animation_physics:
            self.apply_animation_physics(player, start_time, end_time)
        else:
            player.apply_physics(end_time - start_time)
        
        #set the point positions affects whether the player is grounded, so 
        #there are extra case statements here
        #if the player was in a grounded state shift back to the ground after 
        #setting the initial point positions
        if (self.use_animation_physics and
        self.animation.get_matching_jump_interval(frame_index) == None):
            player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
            player.model.move_model((player.model.position[0], gamestate.stage.ground.position[1] - player.model.height))
        else:
            player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
        
        #point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        #player.model.set_point_position_in_place(point_deltas)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        previous_action = player.action
        
        if previous_action.action_state == PlayerStates.TRANSITION:
            previous_action = self.get_previous_action(player.action)
        
        player.action = self
        player.model.animation_run_time = 0     
        player.current_attack = self
        self.last_frame_index = 0
        self.frame_sound_index = 0
        
        if player.direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif player.direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        player.model.set_frame_point_pos(self.animation.frame_deltas[0])
        
        #set the point positions affects whether the player is grounded, so there are extra case statements here
        #if the player was in a grounded state shift back to the ground after setting the initial point positions
        if previous_action.action_state in [PlayerStates.WALKING, PlayerStates.STANDING, PlayerStates.CROUCHING, PlayerStates.RUNNING, PlayerStates.LANDING]:
            player.model.move_model((player.model.position[0], gamestate.stage.ground.position[1] - player.model.height))
            self.use_animation_physics = True
            self.elevation = Elevations.GROUNDED
        
        elif (previous_action.action_state == PlayerStates.ATTACKING and
        previous_action.overriden == True and
        previous_action.elevation == Elevations.GROUNDED):
            self.use_animation_physics = True
            self.elevation = Elevations.GROUNDED
        
        elif not player.is_aerial():
            player.model.move_model((player.model.position[0], gamestate.stage.ground.position[1] - player.model.height))
            self.use_animation_physics = True
            self.elevation = Elevations.GROUNDED
            
        else:
            self.use_animation_physics = False
            self.elevation = Elevations.AERIAL
        
        player.reset_point_damage()
        
        if player.model.time_passed > 0:
            self.move_player(player)
    
    def get_previous_action(self, action):
        
        if action.action_state == PlayerStates.TRANSITION:
            return self.get_previous_action(action.last_action)
        else:
            return action
    
    def get_attack_lines(self, model):
        """get the lines that used to attack in the animation"""
        
        attack_lines = {}
        
        if self.attack_type in \
        [
            InputActionTypes.WEAK_PUNCH,
            InputActionTypes.MEDIUM_PUNCH,
            InputActionTypes.STRONG_PUNCH
        ]:
            attack_lines[stick.LineNames.RIGHT_UPPER_ARM] = model.lines[stick.LineNames.RIGHT_UPPER_ARM]
            attack_lines[stick.LineNames.RIGHT_FOREARM] = model.lines[stick.LineNames.RIGHT_FOREARM]
            attack_lines[stick.LineNames.LEFT_UPPER_ARM] = model.lines[stick.LineNames.LEFT_UPPER_ARM]
            attack_lines[stick.LineNames.LEFT_FOREARM] = model.lines[stick.LineNames.LEFT_FOREARM]
            
        elif self.attack_type in \
        [
            InputActionTypes.WEAK_KICK,
            InputActionTypes.MEDIUM_KICK,
            InputActionTypes.STRONG_KICK
        ]:
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
            #Initialize the frame times to match start and end of frame
            displacement_start_time = self.animation.frame_start_times[frame_index]
            displacement_end_time = (displacement_start_time + 
                                     self.animation.frame_times[frame_index])
            elapsed_time = 0
            if frame_index == start_frame_index:
                displacement_start_time = start_time
            
            if displacement_end_time > end_time:
                displacement_end_time = end_time
            
            duration = displacement_end_time - displacement_start_time
            
            x_velocity = self.animation.get_lateral_velocity(displacement_start_time,frame_index)
            y_velocity = self.animation.get_jump_velocity(displacement_start_time,frame_index)
            
            if player.model.orientation == physics.Orientations.FACING_RIGHT:
                player.model.velocity = (x_velocity, y_velocity)
            elif player.model.orientation == physics.Orientations.FACING_LEFT:
                player.model.velocity = (-x_velocity, y_velocity)
            
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
    
    def create_walk(self, animation):
        """create a movement model for the given movement state"""
        return_walk = Walk()
        
        self._set_action_animations(return_walk, animation)
        
        return return_walk
    
    def create_run(self, animation):
        return_run = Run()
        
        self._set_action_animations(return_run, animation)
        
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
    
    def create_attack(self, action_type, animation, model):
        """create an attack model for the given action type"""
        
        return_attack = Attack(action_type)
        
        return_attack.set_acceleration(action_type)
        
        self._set_action_animations(
            return_attack,
            animation,
            return_attack.acceleration
        )
        
        return_attack.set_attack_data(model)
        return_attack.set_frame_sounds()
        
        return return_attack
    
    def _set_action_animations(self, action, animation, acceleration = Player.ACCELERATION):
        
        action.right_animation = self.crte_player_animation(animation)
        action.right_animation.set_animation_point_path_data(Player.ACCELERATION)
        action.right_animation.set_animation_reference_point_path_data(acceleration,
                                                                       physics.GRAVITY)
        action.left_animation = self.crte_player_animation(animation.flip())
        action.left_animation.set_animation_point_path_data(Player.ACCELERATION)
        action.left_animation.set_animation_reference_point_path_data(acceleration,
                                                                      physics.GRAVITY)
    
    def crte_player_animation(self, animation):
        rtn_animation = copy.deepcopy(animation)
        rtn_animation.scale(.7)
        rtn_animation.set_frame_deltas()
        rtn_animation.set_animation_deltas()
        
        return rtn_animation

def draw_model(player, surface):
    """draws the model to the screen"""
    
    enclosing_rect = pygame.Rect(*player.model.get_enclosing_rect())  
    
    gamestate.new_dirty_rects.append(enclosing_rect)
    
    #pygame.draw.rect(gamestate.screen, (100,100,100),enclosing_rect,1)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_outline_point(point, (0,0,0), surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_outline_circle(line, (0,0,0), surface)
        else:
            draw_outline_line(line, (0,0,0), surface)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_outer_point(point, player.outline_color, surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_outer_circle(line, player.outline_color, surface)
        else:
            draw_outer_line(line, player.outline_color, surface)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_inner_point(point, player.health_color, surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_inner_circle(line, player.health_color, surface)
        else:
            draw_health_line(line, player, surface)

def draw_health_line(line, player, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    health_point1 = point1
    health_level = float(player.health_meter) / player.health_max
    x_delta = health_level * (point2[0] - health_point1[0])
    y_delta = health_level * (point2[1] - health_point1[1])
    health_point2 = (point1[0] + x_delta, point1[1] + y_delta)
    
    pygame.draw.line(surface, \
                    player.health_color, \
                    health_point1, \
                    health_point2, \
                    int(10))

def draw_outline_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    pygame.draw.line(surface, \
                    color, \
                    point1, \
                    point2, \
                    int(18))

def draw_outer_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    pygame.draw.line(surface, \
                    color, \
                    point1, \
                    point2, \
                    int(14))

def draw_outline_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius) + 2)

def draw_outer_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius))

def draw_inner_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    if radius <= 2:
        radius = 3
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius - 2))


def draw_outline_point(point, color, surface):
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(9))

def draw_outer_point(point, color, surface):
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(7))

def draw_inner_point(point, color, surface):
    """Draws a point on a surface
    
    surface: the pygame surface to draw the point on"""
    
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(5))

def draw_reflection(player, surface):
    """draws the reflection of the player on the given surface"""

    player_rect = pygame.Rect(*player.model.get_enclosing_rect())
    previous_position = (player.model.position[0], player.model.position[1])
    
    if player.model.orientation == physics.Orientations.FACING_RIGHT:
        player.model.move_model((8,8))
    else:
        player.model.move_model((player_rect.width - 8, 8))
    
    #create a surface to perform the reflection on that tightly surounds the player
    reflection_surface = pygame.Surface((player_rect.width, player_rect.height))
    reflection_surface.fill((1,234,25))
    reflection_surface.set_colorkey((1,234,25))
    draw_model(player, reflection_surface)
    
    #flip and scale the surface and decrease its opacity to make the reflection
    reflection_surface = pygame.transform.flip(reflection_surface, False, True)
    reflection_surface = pygame.transform.scale(
        reflection_surface,
        (
            max(int(player_rect.width * player_rect.bottom / gamestate.stage.floor_height), 10),
            max(int(
                (.75 * player_rect.height) *
                player_rect.bottom /
                gamestate.stage.floor_height
            ), 10)
        )
    ).convert()
    reflection_surface.set_alpha(150)
    
    reflection_position = (player_rect.left, gamestate.stage.floor_height - 3)
    surface.blit(reflection_surface, reflection_position)
    
    gamestate.new_dirty_rects.append(
        pygame.Rect(
            reflection_position,
            (reflection_surface.get_width(), reflection_surface.get_height())
        )
    )
    
    player.model.move_model(previous_position)
