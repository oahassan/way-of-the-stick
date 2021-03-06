"""
Utility classes used by the player module.
"""

import animation
import physics
from enumerations import AttackTypes, Elevations

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
