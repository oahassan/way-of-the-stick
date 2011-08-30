"""
The player controller module translates game events into player actions.
"""

from enumerations import InputActionTypes, CommandCollections

class Controller():
    
    def __init__(
        self,
        movement_key_to_command_type, 
        attack_key_to_command_type,
        aerial_movement_command_handler,
        aerial_action_command_handler,
        stun_movement_command_handler,
        ground_movement_command_handler,
        attack_command_handler
    ):
        #mappings of keys to command types defined in 
        #enumerations.InputActionTypes
        self.movement_key_to_command_type = movement_key_to_command_type
        self.attack_key_to_command_type = attack_key_to_command_type
        
        #command handler that has PhysicsModifiers for aerial movement as 
        #values
        self.aerial_movement_command_handler = aerial_movement_command_handler
        
        #command handler that has aerial Actions as values
        self.aerial_action_command_handler = aerial_action_command_handler
        
        #command handler that has PhysicsModifiers for stun movement as values
        self.stun_movement_command_handler = stun_movement_command_handler
        
        #command handler that has ground movement Actions as values
        self.ground_movement_command_handler = ground_movement_command_handler
        
        #command handler that has attack Actions as values
        self.attack_command_handler = attack_command_handler
    
    def update(self, keys_pressed):
        """Updates each of the command handlers with given keys pressed."""
        
        self._update_aerial_movement(keys_pressed)
        self._update_aerial_action(keys_pressed)
        self._update_ground_movement(keys_pressed)
        self._update_stun_movement(keys_pressed)
        self._update_attack(keys_pressed)
    
    def get_current_aerial_action(self):
        return_aerial_action = self.aerial_action_command_handler.get_current_command_sequence_value()
        
        if return_aerial_action == None:
            command_state = self.aerial_action_command_handler.get_command_state()
            
            for command in self.aerial_action_command_handler.current_commands:
                if command.command_type not in InputActionTypes.MOVEMENTS or command.command_type == InputActionTypes.JUMP:
                    command_state.set_command_state(command.command_type, True)
            
            self.aerial_action_command_handler.replace_current_commands(
                command_state
            )
            
            return_aerial_action = self.aerial_action_command_handler.get_current_command_sequence_value()
        
        return return_aerial_action
    
    def get_current_aerial_movements(self):
        """Return the values that corresponds to each current aerial movement
        command."""
        
        current_aerial_movements = []
        
        for command in self.aerial_movement_command_handler.current_commands:
            if command.command_type in CommandCollections.AERIAL_MOVEMENTS:
                current_aerial_movements.append(
                    self.aerial_movement_command_handler.get_command_sequence_value(
                        [command]
                    )
                )
        
        return current_aerial_movements
    
    def get_current_stun_movements(self):
        """Return the values that corresponds to each current stun movement
        command."""
        
        current_stun_movements = []
        
        for command in self.stun_movement_command_handler.current_commands:
            if command.command_type in CommandCollections.STUN_MOVEMENTS:
                current_stun_movements.append(
                    self.stun_movement_command_handler.get_command_sequence_value(
                        [command]
                    )
                )
        
        return current_stun_movements
    
    def get_current_ground_movement(self):
        return self.ground_movement_command_handler.get_current_command_sequence_value()
    
    def get_current_attack(self):
        return_attack = self.attack_command_handler.get_current_command_sequence_value()
        
        if return_attack == None:
            command_state = self.attack_command_handler.get_command_state()
            
            for command in self.attack_command_handler.current_commands:
                if command.command_type not in InputActionTypes.MOVEMENTS:
                    command_state.set_command_state(command.command_type, True)
            
            self.attack_command_handler.replace_current_commands(
                command_state
            )
            
            return_attack = self.attack_command_handler.get_current_command_sequence_value()
        
        return return_attack
    
    def _update_aerial_movement(self, keys_pressed):
        """Returns PhysicsModifiers for each movement key the list 
        keys_pressed.  If none of the keys_pressed are in the 
        aerial_movement_command_handler then None is returned."""
        
        command_state = self._create_aerial_movement_command_states(
            keys_pressed
        )
        
        self.aerial_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_aerial_movement_command_states(self, keys_pressed):
        """Creates a CommandState object from a list of keys_pressed for the
        aerial command handler."""
        
        command_states = self.aerial_movement_command_handler.get_command_state()
        
        for command_type in self._get_aerial_command_types(keys_pressed):
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _get_aerial_command_types(self, keys_pressed):
        """Returns the valid key combinations for aerial movement keys.
        MOVE_LEFT, MOVE_RIGHT, and MOVE_DOWN are the only valid commands for 
        aerial commands.  If none of the keys in keys_pressed are bound to any 
        of those command_types NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.movement_key_to_command_type:
            
                key_command_type = self.movement_key_to_command_type[key]
                if key_command_type in CommandCollections.AERIAL_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #it is not a valid aerial movement so add nothing for this 
                #key
                pass
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def _update_stun_movement(self, keys_pressed):
        """Returns PhysicsModifiers for each movement key the list 
        keys_pressed.  If none of the keys_pressed are in the 
        stun_movement_command_handler then None is returned."""
        
        command_state = self._create_stun_movement_command_states(
            keys_pressed
        )
        
        self.stun_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_stun_movement_command_states(self, keys_pressed):
        """Creates a CommandState object from a list of keys_pressed for the
        stun command handler."""
        
        command_states = self.stun_movement_command_handler.get_command_state()
        
        for command_type in self._get_stun_command_types(keys_pressed):
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _get_stun_command_types(self, keys_pressed):
        """Returns the valid key combinations for stun movement keys.
        MOVE_LEFT, MOVE_RIGHT, MOVE_DOWN, and MOVE_UP are the only valid 
        commands for stun commands."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.movement_key_to_command_type:
            
                key_command_type = self.movement_key_to_command_type[key]
                if key_command_type in CommandCollections.STUN_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #it is not a valid aerial movement so add nothing for this 
                #key
                pass
        
        return return_command_types
    
    def _update_ground_movement(self, keys_pressed):
        """Returns an Action for the movement key with the highest precdence in
        the list keys_pressed.  If none of the keys pressed are in the 
        ground_movement_command_handler then None is returned."""
        
        command_state = self._create_ground_movement_command_states(
            keys_pressed
        )
        
        self.ground_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_ground_movement_command_states(self, keys_pressed):
        """Creates a CommandState object from a list of keys_pressed for the
        ground movement command handler."""
        
        command_states = self.ground_movement_command_handler.get_command_state()
        
        command_type = self._get_ground_command_type(keys_pressed)
        command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _get_ground_command_type(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_type = InputActionTypes.NO_MOVEMENT
        
        for key in keys_pressed:
            if key in self.movement_key_to_command_type:
            
                key_command_type = self.movement_key_to_command_type[key]
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
                #it is not a valid ground movement so add nothing for this 
                #key
                pass
        
        return return_command_type
    
    def _update_aerial_action(self, keys_pressed):
        """Returns an Action for the movement key with the highest precdence in
        the list keys_pressed.  If none of the keys pressed are in the 
        aerial_action_command_handler then None is returned."""
        
        command_state = self._create_aerial_action_command_states(
            keys_pressed
        )
        
        self.aerial_action_command_handler.update_current_commands(
            command_state
        )
    
    def _create_aerial_action_command_states(self, keys_pressed):
        """Creates a CommandState object from a list of keys_pressed for the
        aerial action command handler."""
        
        command_states = self.aerial_action_command_handler.get_command_state()
        
        command_types = self._get_aerial_action_command_types(keys_pressed)
        
        for command_type in command_types:
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _get_aerial_action_command_types(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            key_command_type = None
            
            if key in self.movement_key_to_command_type:
                key_command_type = self.movement_key_to_command_type[key]
            elif key in self.attack_key_to_command_type:            
                key_command_type = self.attack_key_to_command_type[key]
            
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
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def _update_attack(self, keys_pressed):
        """Returns an attack Action that matches the list of keys in 
        keys_pressed.  If the attack_command_handler does not have a matching
        attack then None is returned."""
        
        command_state = self._create_attack_command_states(
            keys_pressed
        )
        
        self.attack_command_handler.update_current_commands(
            command_state
        )
    
    def _create_attack_command_states(self, keys_pressed):
        """Creates a CommandState object from a list of keys_pressed for the
        attack command handler."""
        
        command_states = self.attack_command_handler.get_command_state()
        
        for command_type in self._get_attack_command_types(keys_pressed):
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _get_attack_command_types(self, keys_pressed):
        """Returns the valid key combinations for attack keys. All movement
        commands and attack commands valid, however MOVE_RIGHT and MOVE_LEFT 
        are changed into MOVE_FORWARD commands. Also NO_MOVMENT is NOT an 
        active command if no movement keys are pressed."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.attack_key_to_command_type:
            
                command_type = self.attack_key_to_command_type[key]
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
                #it is not a valid aerial movement so add nothing for this 
                #key
                pass
        
        return return_command_types
    
