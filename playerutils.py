"""
Utility classes used by player modules.
"""
import math
import pygame
import gamestate
import copy
import stick
import animation
import physics
import mathfuncs
import animationmanipulator
import versussound
from animationexplorer import create_WOTS_animation
from enumerations import PlayerStates, AttackTypes, Elevations, InputActionTypes, EventTypes, EventStates, LineLengths, LineNames, PointNames
from playerconstants import *

class Action():
    def __init__(self, action_state):
        self.action_state = action_state
        self.right_animation = None
        self.left_animation = None
        self.animation = None
        self.direction = PlayerStates.FACING_RIGHT
        self.last_frame_index = -1
    
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
        
        if frame_index != self.last_frame_index:
            player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
        
        #point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        #player.model.set_point_position_in_place(point_deltas)
        
        player.apply_physics(end_time - start_time)
        self.last_frame_index = frame_index
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if player.action.action_state == PlayerStates.TRANSITION:
            if self.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[player.action.next_action.action_state]:
                change_state = True
        else:
            if self.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[player.action.action_state]:
                change_state = True
        
        return change_state
    
    def test_change_to_action(self, action):
        change_state = False
        
        if action.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[self.action_state]:
            change_state = True
        
        return change_state
    
    def get_previous_action(self, action):
        
        if action.action_state == PlayerStates.TRANSITION:
            return action.last_action
        else:
            return action
    
    def set_player_state(self, player, direction):
        
        if player.action.action_state != self.action_state:
            player.events.append((EventTypes.START, self.action_state))
        
        player.action = self
        
        if direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        if player.direction != direction:
            player.direction = direction
            player.model.set_spatial_data()
        else:
            player.direction = direction
        
        player.model.animation_run_time = 0     
        
        #Check if the player is in the air.  If not, shift back to the gRound after
        #changing to the new animation.
        if player.is_aerial():
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            
        else:
            #if player.model.bottom() > gamestate.stage.ground.position[1]:
            #    print("below ground")
            #    print("player bottom: " + str(player.model.bottom()))
            #    print("stage position: " + str(gamestate.stage.ground.position[1]))
            #    print("expected position" + str(
            #           (player.model.position[0], 
            #           int(math.ceil(gamestate.stage.ground.position[1] - player.model.height)))
            #        )
            #    )
            #   print("actual position: " + str(player.model.position))
            player.model.set_frame_point_pos(self.animation.frame_deltas[0])
            player.move_to_ground()
        
        # if current_x_position != player.model.position[0]:
            # print("start position")
            # print(current_x_position)
            # print("end position")
            # print(player.model.position[0])
        
        if player.model.time_passed > 0:
            self.move_player(player)

def Continue():
    def test_state_change(self, player):
        if player.model.animation_run_time >= player.action.animation.animation_length:
            return True
    
    def test_change_to_action(self, action):
        return True
    
    def set_player_state(self, player, direction):
        player.action.set_player_state(player, direction)

class GeneratedAction():
    def __init__(self):
        pass
    
    def init_animation(self):
        animation = self.get_new_animation()
        
        self.right_animation = animation
        self.left_animation = animation
        self.animation = animation
    
    def get_new_animation(self):
        animation = create_WOTS_animation()
        animation.frames.append(copy.deepcopy(animation.frames[0]))
        
        return animation
    
    def save_model_point_positions_to_frame(self, frame, point_names, model):
        """Creates a frame with ids that match the first frame"""
        
        for point_name, point_id in point_names.iteritems():
            position = model.points[point_name].pos
            frame.point_dictionary[point_id].pos = (position[0], position[1])
            frame.point_dictionary[point_id].name = point_name

class Transition(Action, GeneratedAction):
    def __init__(self):
        Action.__init__(self, PlayerStates.TRANSITION)
        GeneratedAction.__init__(self)
        self.next_action = None
        self.last_action = None
        self.grounded = False
        self.init_animation()
    
    def init_transition(self, player, next_action):
        self.grounded = not player.is_aerial()
        self.direction = PlayerStates.FACING_RIGHT
        self.last_frame_index = 0
        self.next_action = next_action
        self.last_action = player.action
        #self.init_animation()
        self.set_animation(player, next_action)
    
    def set_animation(self, player, next_action):
        
        transition_animation = self.set_animation_frames(
            self.animation, 
            player, 
            next_action
        )
        transition_animation.set_frame_deltas()
        transition_animation.set_animation_deltas()
        transition_animation.set_animation_point_path_data(TRANSITION_ACCELERATION)
    
    def set_animation_frames(self, animation, player, next_action):
        first_frame = animation.frames[0]
        self.save_model_point_positions_to_frame(
            first_frame, 
            animation.point_names,
            player.model
        )
        last_frame = self.init_last_frame(animation, player.action, next_action)
        
        #when running or walking is the next action state the reference 
        #position may change. So special logic is here to handle correctly
        #orienting the transition animations
        if next_action.action_state in PlayerStates.LATERAL_MOVEMENTS:
            if (player.model.orientation == physics.Orientations.FACING_RIGHT and
            next_action.direction == PlayerStates.FACING_LEFT):
                first_frame.flip()
            elif player.model.orientation == physics.Orientations.FACING_LEFT:
                if next_action.direction == PlayerStates.FACING_RIGHT:
                    pass
                else:
                    first_frame.flip()
        elif player.model.orientation == physics.Orientations.FACING_LEFT:
            first_frame.flip()
        
        return animation
    
    def init_last_frame(self, animation, current_action, next_action):
        """Creates a frame with ids that match the first frame"""
        
        first_frame = animation.frames[0]
        last_frame = animation.frames[1]
        last_frame_point_positions = next_action.right_animation.frame_deltas[0]
        
        for point_name, point_id in animation.point_names.iteritems():
            position = last_frame_point_positions[point_name]
            last_frame.point_dictionary[point_id].pos = position
        
        last_frame.set_position(first_frame.get_reference_position())
        
        if self.grounded:
            frame_bottom_diff = (
                first_frame.get_enclosing_rect().bottom - 
                last_frame.get_enclosing_rect().bottom
            )
            
            if frame_bottom_diff != 0:
                last_frame.move((0,frame_bottom_diff))
        
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
        
        self.last_frame_index = self.animation.get_frame_index_at_time(end_time)
        point_deltas = self.animation.build_point_time_delta_dictionary(start_time, end_time)
        player.model.set_point_position_in_place(point_deltas)
        
        player.apply_physics(end_time - start_time)
        
        if self.grounded:
            player.move_to_ground()
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        #set friction so that stun friction doesn't remain
        player.model.friction = physics.FRICTION
        player.events.append((EventTypes.STOP, self.last_action.action_state))
        
        if self.next_action.action_state in PlayerStates.LATERAL_MOVEMENTS:
            Action.set_player_state(self, player, self.next_action.direction)
            
        else:
            Action.set_player_state(self, player, player.direction)
    
    #def test_state_change(self, player):
    #    change_state = False
    #    
    #    if self.next_action.action_state == PlayerStates.ATTACKING:
    #        pass
    #    elif self.action_state in PlayerStates.PRESSED_KEY_STATE_TRANSITIONS[player.action.action_state]:
    #        change_state = True
    #    
    #    return change_state
    
    def sync(self, direction, animation):
        self.right_animation = animation
        self.direction = direction

class Walk(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.WALKING)
        self.sound_map = None
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
        
        if self.sound_map.frame_sounds[self.last_frame_index]:
            player.events.append((EventTypes.START, EventStates.FOOT_SOUND))
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, self.direction)
        player.dash_timer = 0

class Run(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.RUNNING)
        self.sound_map = None
    
    def move_player(self, player):
        Action.move_player(self, player)
        player.move_to_ground()
        
        if self.sound_map.frame_sounds[self.last_frame_index]:
            player.events.append((EventTypes.START, EventStates.FOOT_SOUND))
    
    def set_player_state(self, player):
        Action.set_player_state(self, player, self.direction)
        self.dash_timer = player.dash_timeout

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
            player.jump_timer = player.high_jump_timeout
        else:
            change_state = Action.test_state_change(self, player)
            if change_state:
                player.jump_timer = 0
        
        return change_state
    
    def set_player_jump_velocity(self, player):
        player.model.velocity = (player.model.velocity[0], player.jump_speed)
        
        player.drift_velocity_component = 0
        
        if ((player.jump_timer > player.short_jump_timeout) and
        (player.jump_timer < player.high_jump_timeout)):
            player.model.velocity = (player.model.velocity[0], player.high_jump_speed)
    
    def set_player_state(self, player):
        self.set_player_jump_velocity(player)
        Action.set_player_state(self, player, player.direction)

class Stand(Action):
    def __init__(self):
        Action.__init__(self, PlayerStates.STANDING)
        self.frame_index = 0
        self.start_position = None
    
    def move_player(self, player):
        
        start_time = player.model.animation_run_time
        end_time = start_time + player.model.time_passed
        
        if end_time > self.animation.animation_length:
            end_time = self.animation.animation_length
            player.model.time_passed -= self.animation.animation_length - player.model.animation_run_time
            player.model.animation_run_time = end_time
        else:
            player.model.animation_run_time += player.model.time_passed
            player.model.time_passed = 0
        
        frame_index = self.animation.get_frame_index_at_time(end_time)
        self.last_frame_index = frame_index
        
        #set the point positions affects whether the player is grounded, so 
        #there are extra case statements here
        #if the player was in a grounded state shift back to the ground after 
        #setting the initial point positions
        if frame_index != self.frame_index:
            #for i in range(self.frame_index, frame_index + 1):
            
            player.model.set_relative_point_positions(
                self.start_position, 
                self.animation.animation_deltas[frame_index]
            )
            
            self.frame_index = frame_index
        
        #apply physics after rendering
        player.apply_physics(end_time - start_time, gravity = False)
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        self.last_frame_index = 0
        self.frame_index = 0
        
        player.model.animation_run_time = 0
        
        if player.direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif player.direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        if (
            player.action == None or 
            player.action.action_state != PlayerStates.STANDING or 
            self.start_position == None
        ):
            self.start_position = (player.model.position[0], player.model.position[1])
        
            player.model.set_relative_point_positions(
                self.start_position, 
                self.animation.animation_deltas[0]
            )
            player.move_to_ground()
            
            self.start_position = (player.model.position[0], player.model.position[1])
        else:
            player.model.move_model(self.start_position)
        
        player.action = self
        
        if player.model.time_passed > 0:
            self.move_player(player)

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

class Stun(Action, GeneratedAction):
    def __init__(self):
        Action.__init__(self, PlayerStates.STUNNED)
        GeneratedAction.__init__(self)
        self.physics_vector = [0,0]
        self.toy_model = physics.Model([0,0])
        self.toy_model.init_stick_data()
        self.grounded = False
        self.aerial = False
        self.init_animation()
    
    def set_animation(self, player):
        """creates a stun animation from the player model."""
        stun_animation = self.animation
        self.init_toy_model_point_positions(player)
        self.physics_vector[0] = 0
        self.physics_vector[1] = 0
        
        self.save_model_point_positions_to_frame(
            stun_animation.frames[0],
            stun_animation.point_names,
            player.model
        )
        
        self.pull_toy_model(player)
        
        self.save_model_point_positions_to_frame(
            stun_animation.frames[1], 
            stun_animation.point_names,
            self.toy_model
        )
        
        if player.model.orientation == physics.Orientations.FACING_LEFT:
            animationmanipulator.flip_animation(stun_animation)
        
        stun_animation.set_frame_deltas()
        stun_animation.set_animation_deltas()
        stun_animation.set_animation_point_path_data(STUN_ACCELERATION)
    
    def init_toy_model_point_positions(self, player):
        """makes the stun action's model match the player model"""
        
        self.toy_model.lines[LineNames.HEAD].max_length = LineLengths.HEAD * player.get_scale()
        self.toy_model.lines[LineNames.TORSO].max_length = LineLengths.TORSO * player.get_scale()
        
        for point_name, point in self.toy_model.points.iteritems():
            position = player.model.points[point_name].pos
            point.pos = (position[0], position[1])
        
        self.correct_model_lengths(player)
        
        for line in self.toy_model.lines.values():
            line.set_length()
    
    def correct_model_lengths(self, player):
        scale = player.get_scale()
        
        torso = self.toy_model.lines[LineNames.TORSO]
        if torso.length > scale * LineLengths.TORSO:
            torso.correct(self.toy_model.points[PointNames.TORSO_TOP])
        
        head = self.toy_model.lines[LineNames.HEAD]
        if head.length > scale * LineLengths.HEAD:
            head.correct(self.toy_model.points[PointNames.TORSO_TOP])
       
    
    def pull_toy_model(self, player):
        
        self.pull_toy_point(
            self.toy_model.points[player.interaction_point.name],
            (10*player.interaction_vector[0],10*player.interaction_vector[1])
        )
    
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
        
        if self.grounded and self.aerial:
            player.move_to_ground()
            player.model.velocity = (0, player.model.velocity[1])
            
        player.apply_physics(player.model.time_passed)
        
        if player.is_aerial() == False:
            if self.grounded == False:
                player.events.append((EventTypes.START, EventStates.STUN_GROUND))
            self.grounded = True
        else:
            self.aerial = True
        
        if player.stun_timer >= player.stun_timeout:
            
            player.handle_animation_end()
    
    def test_state_change(self, player):
        change_state = False
        
        if player.stun_timer >= player.stun_timeout and player.health_meter > 0:
            change_state = True
        
        return change_state
    
    def set_player_state(self, player):
        
        self.set_animation(player)
        self.grounded = False
        self.aerial = False
        
        player.action = self
        player.model.animation_run_time = 0
        
        player.stun_timeout = 500 #min(500,int(1000 * ((player.health_max - player.health_meter) / player.health_max)) + 200)
        player.stun_timer = 0
        player.model.friction = physics.STUN_FRICTION
        
        if player.model.time_passed > 0:
            self.move_player(player)

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
        self.acceleration = ACCELERATION
        self.elevation = Elevations.GROUNDED
        self.overriden = False
        self.is_jump_attack = False
        self.sound_map = None
    
    def set_acceleration(self, action_type):
        """sets the animation acceleration for a given InputActionType.  Only
        attack input action types are valid."""
        
        if action_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]:
            self.acceleration = 2 * ACCELERATION
            
        elif action_type in [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]:
            self.acceleration = ACCELERATION
            
        elif action_type in [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]:
            self.acceleration = .5 * ACCELERATION
    
    def test_state_change(self, player):
        
        if (player.get_player_state() == PlayerStates.STUNNED or
        player.is_aerial()):
            return False
        elif player.get_player_state() == PlayerStates.TRANSITION:
            return player.action.next_action.test_change_to_action(self)
        else:
            return Action.test_state_change(self, player)
    
    def get_damage_multiplier(self):
        return ACCELERATION / (2 * self.acceleration)
    
    def set_attack_data(self, model):
        """called after the animations of an attack has been set to intialize other data"""
        self.range = (self.right_animation.get_widest_frame().image_width(), 
                      self.right_animation.get_tallest_frame().image_height())
        self.attack_lines = self.get_attack_lines(model)
        self.sound_map = versussound.AttackSoundMap(self.right_animation, self.attack_type)
    
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
        self.last_frame_index = frame_index
        
        if self.sound_map.frame_sounds[self.last_frame_index]:
            player.events.append((EventTypes.START, EventStates.ATTACK_SOUND))
        
        #apply animation physics first to determine what the player's position 
        #should be.
        self.apply_animation_physics(player, start_time, end_time)
        
        if self.animation.get_matching_jump_interval(frame_index) == None:
            player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
            player.model.move_model(
                (player.model.position[0], 
                gamestate.stage.ground.position[1] - player.model.height)
            )
        else:
            player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        
        player.action = self
        player.model.animation_run_time = 0     
        player.current_attack = self
        
        if player.direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif player.direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        player.model.set_frame_point_pos(self.animation.frame_deltas[0])
        
        player.model.move_model(
            (player.model.position[0], 
            gamestate.stage.ground.position[1] - player.model.height)
        )
        self.elevation = Elevations.GROUNDED
        
        player.reset_point_damage()
        
        if player.model.time_passed > 0:
            self.move_player(player)
    
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
            
            if player.is_aerial() == False and y_velocity < 0:
                player.events.append((EventTypes.START, PlayerStates.JUMPING))
            
            if player.model.orientation == physics.Orientations.FACING_RIGHT:
                player.model.velocity = (x_velocity, y_velocity)
            elif player.model.orientation == physics.Orientations.FACING_LEFT:
                player.model.velocity = (-x_velocity, y_velocity)
            
            player.apply_physics(duration)

class JumpAttack(Attack):
    def __init__(self, attack_type):
        Attack.__init__(self, attack_type)
        self.is_jump_attack = True
        self.grounded = False
    
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
        self.last_frame_index = frame_index
        
        #apply physics first to determine what the player's position 
        #should be.
        player.apply_physics(end_time - start_time)
        
        if player.is_aerial() == False:
            self.grounded = True
        
        player.model.set_frame_point_pos(self.animation.frame_deltas[frame_index])
        
        if self.grounded:
            player.move_to_ground()
        
        if player.model.animation_run_time >= self.animation.animation_length:
            player.handle_animation_end()
    
    def set_player_state(self, player):
        
        player.action = self
        player.model.animation_run_time = 0     
        player.current_attack = self
        self.grounded = False
        
        if player.direction == PlayerStates.FACING_LEFT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_LEFT
            
        elif player.direction == PlayerStates.FACING_RIGHT:
            self.animation = self.right_animation
            player.model.orientation = physics.Orientations.FACING_RIGHT
        
        player.model.set_frame_point_pos(self.animation.frame_deltas[0])
        
        self.elevation = Elevations.AERIAL
        
        player.reset_point_damage()
        
        if player.model.time_passed > 0:
            self.move_player(player)
    
    def test_state_change(self, player):
        
        if player.get_player_state() == PlayerStates.STUNNED:
            return False
        #elif (player.get_player_state() == PlayerStates.TRANSITION and
        #player.action.grounded == False and
        #player.is_aerial()):
        #    return player.action.get_previous_action(player.action).action_state in [PlayerStates.JUMPING, PlayerStates.FLOATING]
        elif player.is_aerial():
            return player.action.get_previous_action(player.action).action_state in [PlayerStates.JUMPING, PlayerStates.FLOATING]
        else:
            return False

class ActionFactory():
    """factory class for creating attack objects"""
    
    def __init__(self, input_player):
        self.player = input_player
    
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
        return_walk.sound_map = versussound.FootSoundMap(animation)
        
        return return_walk
    
    def create_run(self, animation):
        return_run = Run()
        
        self._set_action_animations(return_run, animation)
        return_run.sound_map = versussound.FootSoundMap(animation)
        
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
        return_attack.sound_map = versussound.AttackSoundMap(animation, action_type)
        
        return return_attack
    
    def create_jump_attack(self, action_type, animation, model):
        return_attack = JumpAttack(action_type)
        
        return_attack.set_acceleration(action_type)
        
        self._set_action_animations(
            return_attack,
            animation,
            return_attack.acceleration
        )
        
        return_attack.set_attack_data(model)
        
        return return_attack
    
    def _set_action_animations(self, action, animation, acceleration = ACCELERATION):
        
        action.right_animation = self.crte_player_animation(animation)
        action.right_animation.set_animation_point_path_data(ACCELERATION)
        action.right_animation.set_animation_reference_point_path_data(acceleration, physics.GRAVITY)
        
        #if animation.name == "rasteira de costa":
        #    print(action.right_animation.lateral_velocities)
        #    print([frame.get_reference_position() for frame in action.right_animation.frames])
        
        action.left_animation = self.crte_player_animation(animation.flip())
        action.left_animation.set_animation_point_path_data(ACCELERATION)
        action.left_animation.set_animation_reference_point_path_data(acceleration, physics.GRAVITY)
    
    def crte_player_animation(self, animation):
        
        rtn_animation = copy.deepcopy(animation)
        rtn_animation.set_animation_height(
            self.player.get_animation_height(), 
            REFERENCE_HEIGHT
        )
        rtn_animation.set_frame_deltas()
        rtn_animation.set_animation_deltas()
        
        #if animation.name == "meia lua":
        #    print("original meia lua")
        #    
        #    for frame in animation.frames:
        #        print(frame.get_enclosing_rect().bottom)
        #    
        #    print("scaled meia lua")
        #    
        #    for frame in rtn_animation.frames:
        #        print(frame.get_enclosing_rect().bottom)
        
        return rtn_animation
