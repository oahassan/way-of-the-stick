import copy
import functools
from random import choice
import pygame
import inputtree
import player
import wotsuievents
import gamestate
import movesetdata
import actionwizard
from controlsdata import InputActionTypes, get_control_key, get_controls
import enumerations

class HumanPlayer(player.Player):
    def __init__(self, position):
        player.Player.__init__(self, position)
        self.input_action = None
        self.bound_keys = []
        self.command_tree = inputtree.InputTree()
        self.key_commands = {}
        self.key_bindings = {}
        self.negating_keys = {} #a dictionary for keys that can't be pressed simultaneously
        self.player_type = player.PlayerTypes.HUMAN
        self.controls = None
        self.attack_keys = []
        self.aerial_movement_keys = {}
        self.stun_movement_keys = {}
        self.handle_input_events = True
        self.increment_input_timer = False
        self.input_timer = 0
        self.input_timer_max = 100
    
    def handle_animation_end(self):
        if (self.get_player_state() == player.PlayerStates.ATTACKING or
        self.get_player_state() == player.PlayerStates.STUNNED):
            self.input_timer = 0
            self.increment_input_timer = False
        
        player.Player.handle_animation_end(self)
    
    def set_action(self):
        #Change state if key is released
        if (self.input_action != None and
            wotsuievents.key_released(self.input_action.key)):
                if self.input_action.key_release_action != None:
                    if self.get_player_state() != player.PlayerStates.TRANSITION:
                        self.transition(self.input_action.key_release_action)
                    elif self.action.next_action != self.input_action.key_release_action:
                        self.transition(self.input_action.key_release_action)
                    
                self.input_action = None
        
        commands = self.get_commands(wotsuievents.keys_pressed)
        self.handle_attack_input(commands)
    
        for key in wotsuievents.keys_pressed:
            if (self.input_action != None and
            self.input_action.key in self.negating_keys.keys() and
            key in self.negating_keys[self.input_action.key] and
            self.input_action.key in wotsuievents.keys_pressed):
                #This key can't be pressed at the same time as a currently pressed key
                continue
            
            if key in self.key_bindings.keys():
                if (self.is_aerial() and
                self.get_player_state() in [player.PlayerStates.JUMPING, player.PlayerStates.FLOATING]):
                    
                    if key == pygame.K_UP:
                        self.handle_key_input(key)
                        
                    elif key in self.aerial_movement_keys.keys():
                        self.handle_aerial_motion_input(key)
                
                elif self.action.action_state == player.PlayerStates.STUNNED:
                    if key in self.stun_movement_keys.keys():
                        self.handle_stun_motion_input(key)
                else:
                    self.handle_key_input(key)
    
    def get_commands(self, keys_pressed):
        """creates a list of commands that map to the current pressed keys"""
        commands = []
        
        for key in keys_pressed:
            if key in self.key_commands:
                command = self.key_commands[key]
                
                if (command == enumerations.InputActionTypes.MOVE_RIGHT or
                command == enumerations.InputActionTypes.MOVE_LEFT):
                    command = enumerations.InputActionTypes.FORWARD
                
                commands.append(command)
        
        return commands
    
    def handle_attack_input(self, key_commands):
        attack = self.command_tree.get_value(key_commands)
        
        if attack != None:
            self.resolve_input_action(attack)
    
    def handle_key_input(self,key):
        
        for input_action in self.key_bindings[key]:    
            if self.resolve_input_action(input_action):
                
                break
    
    def resolve_input_action(self, input_action):   
        if input_action.action.test_state_change(self):
            if self.get_player_state() == player.PlayerStates.TRANSITION:
                if (self.action.next_action != input_action.action and
                input_action.action.action_state == player.PlayerStates.ATTACKING):
                    #attacking is a special case so to make multiple key presses 
                    #easier
                    self.transition(input_action.action)
                    
                elif (self.action.next_action != input_action.action and
                self.action.next_action.test_change_to_action(input_action.action)):
                    self.transition(input_action.action)
                    
            elif input_action.action != self.action:
                
                self.transition(input_action.action)
            else:
                input_action.action.set_player_state(self)
            self.input_action = input_action
            
            return True
        
        else:
            return False
    
    def handle_aerial_motion_input(self,key):
        movement_type = self.key_commands[key]
        
        if movement_type == InputActionTypes.MOVE_LEFT:
            self.model.accelerate(self.get_aerial_acceleration(-1), 0)
            
        elif movement_type == InputActionTypes.MOVE_RIGHT:
            self.model.accelerate(self.get_aerial_acceleration(1), 0)
            
        elif movement_type == InputActionTypes.MOVE_DOWN:
            self.model.accelerate(0, player.Player.AERIAL_ACCELERATION)
    
    def handle_stun_motion_input(self,key):
        movement_type = self.key_commands[key]
        
        if movement_type == InputActionTypes.MOVE_LEFT:
            self.model.accelerate(-1*self.aerial_acceleration,0)
        elif movement_type == InputActionTypes.MOVE_RIGHT:
            self.model.accelerate(self.aerial_acceleration,0)
        elif movement_type == InputActionTypes.MOVE_UP:
            self.model.accelerate(0,-1*self.aerial_acceleration)
        elif movement_type == InputActionTypes.MOVE_DOWN:
            self.model.accelerate(0,5*self.aerial_acceleration)
    
    def load_moveset(self, moveset):
        self.moveset = moveset
        
        factory = player.ActionFactory()
        
        for action_type in InputActionTypes.AERIAL_MOVEMENTS:
            self.aerial_movement_keys[get_control_key(action_type)] = action_type
        
        for action_type in InputActionTypes.STUN_MOVEMENTS:
            self.stun_movement_keys[get_control_key(action_type)] = action_type
        
        for action_type in InputActionTypes.ATTACKS:
            self.attack_keys.append(get_control_key(action_type))
        
        for movement in player.PlayerStates.UNBOUND_MOVEMENTS:
            if movement == player.PlayerStates.STUNNED:
                self.actions[movement] = self.create_action(movement)
            elif movement == player.PlayerStates.TRANSITION:
                self.actions[movement] = player.Transition()
            else:
                movement_animation = moveset.movement_animations[movement]
                self.actions[movement] = self.create_action(
                    movement,
                    movement_animation
                )
        
        #Set move up actions
        jump_key = get_control_key(InputActionTypes.MOVE_UP)
        jump_action = self.create_action(
            player.PlayerStates.JUMPING,
            moveset.movement_animations[player.PlayerStates.JUMPING],
            None,
            jump_key
        )
        self.key_bindings[jump_key] = [jump_action]
        
        #Set move down actions
        crouch_key = get_control_key(InputActionTypes.MOVE_DOWN)
        crouch_action = self.create_action(
            player.PlayerStates.CROUCHING,
            moveset.movement_animations[player.PlayerStates.CROUCHING],
            None,
            crouch_key
        )
        self.key_bindings[crouch_key] = [crouch_action]
        
        #set jump and crouch buttons as negating keys
        self.add_negating_keys(jump_key, crouch_key)
        self.add_negating_keys(crouch_key, jump_key)
        
        #Set move right actions
        move_right_key = get_control_key(InputActionTypes.MOVE_RIGHT)
        walk_right_action = self.create_action(
            player.PlayerStates.WALKING,
            moveset.movement_animations[player.PlayerStates.WALKING],
            player.PlayerStates.FACING_RIGHT,
            move_right_key
        )
        run_right_action = self.create_action(
            player.PlayerStates.RUNNING,
            moveset.movement_animations[player.PlayerStates.RUNNING],
            player.PlayerStates.FACING_RIGHT,
            move_right_key
        )
        self.key_bindings[move_right_key] = [walk_right_action,run_right_action]
        
        #Set move left actions
        move_left_key = get_control_key(InputActionTypes.MOVE_LEFT)
        walk_left_action = self.create_action(
            player.PlayerStates.WALKING,
            moveset.movement_animations[player.PlayerStates.WALKING],
            player.PlayerStates.FACING_LEFT,
            move_left_key
        )
        run_left_action = self.create_action(
            player.PlayerStates.RUNNING,
            moveset.movement_animations[player.PlayerStates.RUNNING],
            player.PlayerStates.FACING_LEFT,
            move_left_key
        )
        self.key_bindings[move_left_key] = [walk_left_action,run_left_action]
        
        #set move left and move right buttons as negating keys
        self.add_negating_keys(move_right_key, move_left_key)
        self.add_negating_keys(move_left_key, move_right_key)
        
        #set key commands mapping keys to commands
        self.key_commands = dict([(value, key) for key, value in get_controls().iteritems()])
        
        #Set attack actions
        for attack_name in moveset.get_attacks():
            attack_type = moveset.get_attack_type(attack_name)
            
            attack_action = HumanAttack(attack_type)
            attack_action.set_acceleration(attack_type)
            
            factory._set_action_animations(
                attack_action,
                moveset.attack_animations[attack_name],
                attack_action.acceleration
            )
            
            attack_action.set_attack_data(self.model)
            attack_action.set_frame_sounds()
            
            input_action = player.InputAction(attack_action, None, None)
            
            self.command_tree.add_branches(
                moveset.attack_key_combinations[attack_name],
                input_action
            )
        
        self.actions[player.PlayerStates.STANDING].set_player_state(self)
    
    def add_negating_keys(self, key, negated_key):
        """adds a two keys to the list of keys that can't be pressed simultaneously"""
        
        if key in self.negating_keys.keys():
            self.negating_keys[key].append(negated_key)
        
        else:
            self.negating_keys[key] = [negated_key]
    
    def create_action(self, action_type, animation = None, direction = None, key = None):
        return_action = None
        factory = player.ActionFactory()
        
        if action_type == player.PlayerStates.STANDING:
            return_action = factory.create_stand(animation)
        elif action_type == player.PlayerStates.LANDING:
            return_action = factory.create_land(animation)
        elif action_type == player.PlayerStates.FLOATING:
            return_action = factory.create_float(animation)
        elif action_type == player.PlayerStates.STUNNED:
            return_action = factory.create_stun()
        elif action_type == player.PlayerStates.JUMPING:
            action = factory.create_jump(animation)
            return_action = player.InputAction(
                action,
                None,
                key
            )
        elif action_type == player.PlayerStates.CROUCHING:
            action = factory.create_crouch(animation)
            return_action = player.InputAction(
                action,
                self.actions[player.PlayerStates.STANDING],
                key
            )
        elif action_type == player.PlayerStates.WALKING:
            action = factory.create_walk(animation)
            action.direction = direction
            return_action = player.InputAction(
                action,
                self.actions[player.PlayerStates.STANDING],
                key
            )
        elif action_type == player.PlayerStates.RUNNING:
            action = factory.create_run(animation)
            action.direction = direction
            return_action = player.InputAction(
                action,
                self.actions[player.PlayerStates.STANDING],
                key
            )
        
        return return_action
    
    def handle_events(self):
        
        if self.handle_input_events:
            self.set_action()
        
        if self.increment_input_timer:
            self.input_timer += gamestate.time_passed
        
        player.Player.handle_events(self)

class HumanAttack(player.Attack):

    def test_state_change(self, input_player):
        
        if input_player.get_player_state() == player.PlayerStates.STUNNED:
            return False
        elif (input_player.get_player_state() == player.PlayerStates.TRANSITION and
        input_player.action.next_action.action_state == player.PlayerStates.ATTACKING and
        input_player.input_timer < input_player.input_timer_max and
        input_player.action.next_action != self):
            #allow additional input in predetermined intervals to make using attacks 
            #with multiple button presses easier
            
            if input_player.action.last_action.action_state == player.PlayerStates.JUMPING:
                input_player.move_to_ground()
            elif input_player.action.next_action.elevation == player.Elevations.GROUNDED:
                input_player.move_to_ground()
            
            #Keep track of an attack getting overriden.  This happens with attacks 
            #that require multiple key presses.
            input_player.increment_input_timer = True
            return True
            
        elif (input_player.get_player_state() == player.PlayerStates.ATTACKING and
        input_player.input_timer < input_player.input_timer_max and
        input_player.action != self):
            #allow additional input in predetermined intervals to make using attacks 
            #with multiple button presses easier
            
            if input_player.action.elevation == player.Elevations.GROUNDED:
                input_player.move_to_ground()
            
            #Keep track of an attack getting overriden.  This happens with attacks 
            #that require multiple key presses.
            input_player.action.overriden = True
            input_player.increment_input_timer = True
            return True
            
        else:
            indicator = player.Action.test_state_change(self, input_player)
            
            if indicator:
                input_player.increment_input_timer = True
            
            return indicator

class ForwardMovement:
    """A wrapper class for walking and running to simplify input handling.  It
    keeps input handling from having to map to actions to one input command, while
    allowing the input for moving left and right to take on input command."""
    
    def __init__(self):
        self.player_state = PlayerStates.WALKING
        self.walk_action = None
        self.run_action = None
    
    def get_action(self):
        if self.player_state == player.PlayerStates.WALKING:
            return self.walk_action
        
        if self.player_state == player.PlayerStates.RUNNING:
            return self.run_action
    
    def test_state_change(self, player):
        if self.walk_action.test_state_change(player):
            self.player_state = PlayerStates.WALKING
            return True
        
        elif self.run_action.test_state_change(player):
            self.player_state = PlayerStates.RUNNING
            return True
        
        else:
            return False
    
    def set_player_state(self, player):
        if self.player_state == PlayerStates.WALKING:
            self.walk_action.set_player_state(player)
        
        elif self.player_state == PlayerStates.RUNNING:
            self.run_action.set_player_state(player)
