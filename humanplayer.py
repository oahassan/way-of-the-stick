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
from controlsdata import get_control_key, get_controls
from enumerations import PlayerStates, CommandDurations, InputActionTypes, CommandCollections
from playercontroller import Controller
from playerutils import ActionFactory, Transition, Action, Attack
from command import Command, CommandHandler

class HumanPlayer(player.Player):
    def __init__(self, position):
        player.Player.__init__(self, position)
        self.player_type = player.PlayerTypes.HUMAN
        self.controller = None
        self.handle_input_events = True
    
    def load_moveset(self, moveset):
        controller_factory = ControllerFactory()
        self.actions[PlayerStates.STUNNED] = controller_factory.create_action(
            PlayerStates.STUNNED
        )
        self.actions[PlayerStates.STANDING] = controller_factory.create_action(
            PlayerStates.STANDING,
            moveset.movement_animations[PlayerStates.STANDING]
        )
        self.actions[PlayerStates.FLOATING] = controller_factory.create_action(
            PlayerStates.FLOATING,
            moveset.movement_animations[PlayerStates.FLOATING]
        )
        self.actions[PlayerStates.LANDING] = controller_factory.create_action(
            PlayerStates.LANDING,
            moveset.movement_animations[PlayerStates.LANDING]
        )
        self.controller = controller_factory.create_controller_from_moveset(
            moveset,
            self
        )
        
        self.actions[PlayerStates.STANDING].set_player_state(self)
    
    #def handle_animation_end(self):
    #    """Determine the next action to use if an animation is copmlete."""
    #    
    #    action = self.get_current_action(wotsuievents.keys_pressed)
    #   
    #    if action == None:
    #        self.set_neutral_state()
    #   elif action.test_state_change(self):
    #        action.set_player_state(self)
    #    else:
    #        if (self.actions[PlayerStates.STANDING].test_state_change(self) or
    #       self.actions[PlayerStates.FLOATING].test_state_change(self)):
    #            self.set_neutral_state()
    
    def set_action(self):
        """Set the current action based on what keys are pressed."""
        
        action = self.get_current_action(wotsuievents.keys_pressed)
        
        if (action != None and
        action.test_state_change(self)):
            if type(Continue) == type(Action):
                action.set_player_state(self)
            else:
                self.transition(action)
    
    def get_current_action(self, keys_pressed):
        """Determine the current action state based on the keys pressed. If the
        keys pressed don't map to a valid action then None is returned."""
        
        if self.action.action_state == PlayerStates.STUNNED:
            action = self.controller.get_current_stun_movement()
        else:
            action = self.controller.get_current_attack()
        
        if action == None:
            if self.is_aerial():
                action = self.controller.get_current_aerial_action()
            
            else:
                action = self.controller.get_current_ground_movement()
        
        #if action == None:
        #    pass
        #elif action.action_state == PlayerStates.STANDING:
        #    pass
        #elif action.action_state == PlayerStates.ATTACKING:
        #    print action.action_state
        
        return action
    
    def handle_events(self):
        self.controller.update(wotsuievents.keys_pressed)
        
        if self.handle_input_events:
            self.set_action()
        
        player.Player.handle_events(self)

class ControllerFactory():
    
    def __init__(self):
        self.action_factory = ActionFactory()
    
    def create_controller_from_moveset(self, moveset, input_player):
        """Creates a controller object from a moveset"""
        
        #Create the command handlers for the controller
        aerial_movement_command_types = [command_type for command_type in CommandCollections.AERIAL_MOVEMENTS]
        aerial_movement_command_handler = CommandHandler(
            aerial_movement_command_types
        )
        
        aerial_action_command_types = [command_type for command_type in CommandCollections.AERIAL_ACTIONS]
        aerial_action_command_handler = CommandHandler(
            aerial_action_command_types
        )
        
        stun_movement_command_handler = CommandHandler(
            [command_type for command_type in CommandCollections.STUN_MOVEMENTS]
        )
        
        ground_movement_command_types = [command_type for command_type in CommandCollections.GROUND_MOVEMENTS]
        ground_movement_command_handler = CommandHandler(
            ground_movement_command_types
        )
        
        attack_command_handler = CommandHandler(
            [command_type for command_type in CommandCollections.ATTACK_ACTIONS]
        )
        
        #create the key to command mappings for the controller
        movement_key_to_command_type = dict(
            [(get_control_key(action_type), action_type) for action_type in InputActionTypes.MOVEMENTS]
        )
        
        attack_key_to_command_type = dict(
            [(get_control_key(action_type), action_type) for action_type in CommandCollections.ATTACK_ACTIONS if action_type != InputActionTypes.FORWARD]
        )
        
        #Set aerial no movement actions
        float_action = self.create_action(
            PlayerStates.FLOATING,
            moveset.movement_animations[PlayerStates.FLOATING]
        )
        tap_no_movement = Command(
            InputActionTypes.NO_MOVEMENT,
            CommandDurations.TAP
        )
        aerial_movement_command_handler.add_command([tap_no_movement], float_action)
        
        hold_no_movement = Command(
            InputActionTypes.NO_MOVEMENT,
            CommandDurations.HOLD
        )
        aerial_movement_command_handler.add_command([hold_no_movement], float_action)
        
        #Set ground no movement actions
        stand_action = self.create_action(
            PlayerStates.STANDING,
            moveset.movement_animations[PlayerStates.STANDING]
        )
        tap_no_movement = Command(
            InputActionTypes.NO_MOVEMENT,
            CommandDurations.TAP
        )
        ground_movement_command_handler.add_command([tap_no_movement], stand_action)
        
        hold_no_movement = Command(
            InputActionTypes.NO_MOVEMENT,
           CommandDurations.HOLD
        )
        ground_movement_command_handler.add_command([hold_no_movement], stand_action)
        
        #Set jump actions
        jump_action = self.create_action(
            player.PlayerStates.JUMPING,
            moveset.movement_animations[player.PlayerStates.JUMPING],
            None
        )
        tap_jump_command = Command(
            InputActionTypes.JUMP, 
            CommandDurations.TAP
        )
        hold_jump_command = Command(
            InputActionTypes.JUMP, 
            CommandDurations.HOLD
        )
        
        ground_movement_command_handler.add_command(
            [tap_jump_command],
            jump_action
        )
        aerial_action_command_handler.add_command(
            [tap_jump_command],
            jump_action
        )
        aerial_action_command_handler.add_command(
            [hold_jump_command],
            jump_action
        )
        
        #Set move down actions
        crouch_action = self.create_action(
            player.PlayerStates.CROUCHING,
            moveset.movement_animations[player.PlayerStates.CROUCHING],
            None
        )
        tap_down_command = Command(
            InputActionTypes.MOVE_DOWN, 
            CommandDurations.TAP
        )
        hold_down_command = Command(
            InputActionTypes.MOVE_DOWN,
            CommandDurations.HOLD
        )
        
        ground_movement_command_handler.add_command(
            [tap_down_command],
            crouch_action
        )
        ground_movement_command_handler.add_command(
            [hold_down_command],
            crouch_action
        )
        
        #Set move right actions
        tap_right_command = Command(
            InputActionTypes.MOVE_RIGHT,
            CommandDurations.TAP
        )
        hold_right_command = Command(
            InputActionTypes.MOVE_RIGHT,
            CommandDurations.HOLD
        )
        
        walk_right_action = self.create_action(
            player.PlayerStates.WALKING,
            moveset.movement_animations[PlayerStates.WALKING],
            player.PlayerStates.FACING_RIGHT
        )
        run_right_action = self.create_action(
            player.PlayerStates.RUNNING,
            moveset.movement_animations[PlayerStates.RUNNING],
            PlayerStates.FACING_RIGHT
        )
        
        ground_movement_command_handler.add_command(
            [tap_right_command, tap_right_command],
            run_right_action
        )
        ground_movement_command_handler.add_command(
            [tap_right_command],
            walk_right_action
        )
        ground_movement_command_handler.add_command(
            [hold_right_command],
            Continue()
        )
        
        #Set move left actions
        tap_left_command = Command(
            InputActionTypes.MOVE_LEFT,
            CommandDurations.TAP
        )
        hold_left_command = Command(
            InputActionTypes.MOVE_LEFT,
            CommandDurations.HOLD
        )
        
        walk_left_action = self.create_action(
            player.PlayerStates.WALKING,
            moveset.movement_animations[PlayerStates.WALKING],
            PlayerStates.FACING_LEFT
        )
        run_left_action = self.create_action(
            player.PlayerStates.RUNNING,
            moveset.movement_animations[PlayerStates.RUNNING],
            PlayerStates.FACING_LEFT
        )
        
        ground_movement_command_handler.add_command(
            [tap_left_command, tap_left_command],
            run_left_action
        )
        ground_movement_command_handler.add_command(
            [tap_left_command],
            walk_left_action
        )
        ground_movement_command_handler.add_command(
            [hold_left_command],
            Continue()
        )
        
        #Set attack actions
        for attack_name in moveset.get_attacks():
            attack_type = moveset.get_attack_type(attack_name)
            
            attack_action = Attack(attack_type)
            attack_action.set_acceleration(attack_type)
            
            self.action_factory._set_action_animations(
                attack_action,
                moveset.attack_animations[attack_name],
                attack_action.acceleration
            )
            
            attack_action.set_attack_data(input_player.model)
            attack_action.set_frame_sounds()
            
            commands = []
            
            for command_type in moveset.attack_key_combinations[attack_name]:
                commands.append(Command(command_type, CommandDurations.TAP))
            
            attack_command_handler.add_command(
                commands,
                attack_action
            )
        
        return Controller(
            movement_key_to_command_type, 
            attack_key_to_command_type,
            aerial_movement_command_handler,
            aerial_action_command_handler,
            stun_movement_command_handler,
            ground_movement_command_handler,
            attack_command_handler
        )
    
    def create_action(self, action_type, animation = None, direction = None, key = None):
        return_action = None
        
        if action_type == player.PlayerStates.STANDING:
            return_action = self.action_factory.create_stand(animation)
            
        elif action_type == player.PlayerStates.LANDING:
            return_action = self.action_factory.create_land(animation)
            
        elif action_type == player.PlayerStates.FLOATING:
            return_action = self.action_factory.create_float(animation)
            
        elif action_type == player.PlayerStates.STUNNED:
            return_action = self.action_factory.create_stun()
            
        elif action_type == player.PlayerStates.JUMPING:
            return_action = self.action_factory.create_jump(animation)
            
        elif action_type == player.PlayerStates.CROUCHING:
            return_action = self.action_factory.create_crouch(animation)
            
        elif action_type == player.PlayerStates.WALKING:
            return_action = self.action_factory.create_walk(animation)
            return_action.direction = direction
            
        elif action_type == player.PlayerStates.RUNNING:
            return_action = self.action_factory.create_run(animation)
            return_action.direction = direction
        
        return return_action

def Continue():
    def test_state_change(self, player):
        if player.model.animation_run_time >= player.action.animation.animation_length:
            return True
    
    def test_change_to_action(self, action):
        return True
    
    def set_player_state(self, player, direction):
        player.action.set_player_state(player, direction)
