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
from controlsdata import get_controls
from enumerations import PlayerStates, CommandDurations, InputActionTypes, CommandCollections
from playercontroller import Controller, InputCommandTypes
from playerutils import ActionFactory, Transition, Action, Attack, JumpAttack, Continue


class HumanPlayer(player.Player):
    def __init__(self, position):
        player.Player.__init__(self, position)
        self.player_type = player.PlayerTypes.HUMAN
        self.key_to_command_type_converter = KeyToCommandTypeConverter(
            dict([(entry[1], entry[0]) for entry in get_controls().iteritems()])
        )
    
    def load_moveset(self, moveset):
        player.Player.load_moveset(self, moveset)
        
        self.actions[PlayerStates.STANDING].set_player_state(self)
    
    def get_attack_actions(self):
        return [
            attack_action
            for attack_action in self.actions.values()
            if attack_action.action_state == PlayerStates.ATTACKING
        ]
    
    def get_foot_actions(self):
        return [self.walk_right_action, self.run_right_action]
    
    def handle_events(self, keys_pressed, time_passed):
        
        if self.handle_input_events:
            input_command_types = self.key_to_command_type_converter.get_command_data(
                keys_pressed
            )
            self.controller.update(input_command_types)
        
        self.set_action()
        self.set_motion()
        
        player.Player.handle_events(self, time_passed)

class KeyToCommandTypeConverter():
    def __init__(self, key_to_command_type):
        self.key_to_command_type = key_to_command_type
    
    def get_command_data(self, keys_pressed):
        return InputCommandTypes(
           self.get_attack_command_types(keys_pressed),
           self.get_ground_movement_command_type(keys_pressed),
           self.get_aerial_movement_command_types(keys_pressed),
           self.get_aerial_action_command_types(keys_pressed),
           self.get_stun_movement_command_types(keys_pressed)
       )
    
    def get_attack_command_types(self, keys_pressed):
        """Returns the valid key combinations for attack keys. All movement
        commands and attack commands valid, however MOVE_RIGHT and MOVE_LEFT 
        are changed into MOVE_FORWARD commands. Also NO_MOVMENT is NOT an 
        active command if no movement keys are pressed."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                command_type = self.key_to_command_type[key]
                if (command_type in CommandCollections.ATTACK_ACTIONS):
                    
                    if (command_type == InputActionTypes.MOVE_RIGHT or
                    command_type == InputActionTypes.MOVE_LEFT):
                        return_command_types.append(InputActionTypes.FORWARD)
                        
                    else:
                        return_command_types.append(command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        return return_command_types
    
    def get_ground_movement_command_type(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_type = InputActionTypes.NO_MOVEMENT
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.GROUND_MOVEMENTS:
                    
                    if key_command_type == InputActionTypes.MOVE_DOWN:
                        return_command_type = key_command_type
                    
                    elif (key_command_type == InputActionTypes.JUMP and
                    return_command_type != InputActionTypes.MOVE_DOWN):
                        return_command_type = key_command_type
                    
                    elif key_command_type == InputActionTypes.MOVE_LEFT:
                        if (return_command_type != InputActionTypes.MOVE_DOWN and
                        return_command_type != InputActionTypes.MOVE_UP and 
                        return_command_type != InputActionTypes.MOVE_RIGHT):
                            return_command_type = key_command_type
                        
                        elif return_command_type == InputActionTypes.MOVE_RIGHT:
                            return_command_type = InputActionTypes.NO_MOVEMENT
                    
                    elif key_command_type == InputActionTypes.MOVE_RIGHT:
                        if (return_command_type != InputActionTypes.MOVE_DOWN and
                        return_command_type != InputActionTypes.MOVE_UP and 
                        return_command_type != InputActionTypes.MOVE_LEFT):
                            return_command_type = key_command_type
                        
                        elif return_command_type == InputActionTypes.MOVE_LEFT:
                            return_command_type = InputActionTypes.NO_MOVEMENT
                    
                else:
                    #it is not a valid ground movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key so pass
                pass
        
        return return_command_type
    
    def get_aerial_movement_command_types(self, keys_pressed):
        """Returns the valid key combinations for aerial movement keys.
        MOVE_LEFT, MOVE_RIGHT, and MOVE_DOWN are the only valid commands for 
        aerial commands.  If none of the keys in keys_pressed are bound to any 
        of those command_types NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.AERIAL_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def get_aerial_action_command_types(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
                key_command_type = self.key_to_command_type[key]
                
                if key_command_type in CommandCollections.AERIAL_ACTIONS:
                    
                    if key_command_type == InputActionTypes.NO_MOVEMENT:
                        #the key command is no movment
                        pass
                    elif (key_command_type == InputActionTypes.MOVE_RIGHT or
                    key_command_type == InputActionTypes.MOVE_LEFT):
                        return_command_types.append(InputActionTypes.FORWARD)
                    else:
                        return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial action so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def get_stun_movement_command_types(self, keys_pressed):
        """Returns the valid key combinations for stun movement keys.
        MOVE_LEFT, MOVE_RIGHT, MOVE_DOWN, and MOVE_UP are the only valid 
        commands for stun commands."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.STUN_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        return return_command_types
