"""
The player controller module translates game events into player actions.
"""

from wotsprot.rencode import serializable
from enumerations import InputActionTypes, CommandCollections

class InputCommandTypes():
    def __init__(
        self,
        attack_command_types,
        ground_movement_command_type,
        aerial_movement_command_types,
        aerial_action_command_types,
        stun_movement_command_types
    ):
        self.attack_command_types = attack_command_types
        self.ground_movement_command_type = ground_movement_command_type
        self.aerial_movement_command_types = aerial_movement_command_types
        self.aerial_action_command_types = aerial_action_command_types
        self.stun_movement_command_types = stun_movement_command_types
    
    def __eq__(self, x):
        if x == None:
            return False
        
        if type(self) != type(x):
            return False
        
        return (
            self.attack_command_types == x.attack_command_types
            and self.ground_movement_command_type == x.ground_movement_command_type
            and self.aerial_movement_command_types == x.aerial_movement_command_types
            and self.aerial_action_command_types == x.aerial_action_command_types
            and self.stun_movement_command_types == x.stun_movement_command_types
        )
    
    def __ne__(self, x):
        if x == None:
            return True
        
        if type(self) != type(x):
            return True
        
        return (
            self.attack_command_types != x.attack_command_types
            or self.ground_movement_command_type != x.ground_movement_command_type
            or self.aerial_movement_command_types != x.aerial_movement_command_types
            or self.aerial_action_command_types != x.aerial_action_command_types
            or self.stun_movement_command_types != x.stun_movement_command_types
        )
    
    def __str__(self):
        return("""
attack:             {0}
ground movement:    {1}
aerial movement:    {2}
aerial action:      {3}
stun movement:      {4}
""".format(
                self.attack_command_types, self.ground_movement_command_type, 
                self.aerial_movement_command_types, self.aerial_action_command_types,
                self.stun_movement_command_types
            )
        )
    
    def __repr__(self):
        return self.__str__()
    
    def _pack(self):
        return (self.attack_command_types, self.ground_movement_command_type, 
        self.aerial_movement_command_types, self.aerial_action_command_types,
        self.stun_movement_command_types)

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
        
        #last set of command types passed to update function
        self.last_input_command_types = None
    
    def update(self, input_command_types):
        """Updates each of the command handlers with given keys pressed."""
        
        self._update_aerial_movement(input_command_types.aerial_movement_command_types)
        self._update_aerial_action(input_command_types.aerial_action_command_types)
        self._update_ground_movement(input_command_types.ground_movement_command_type)
        self._update_stun_movement(input_command_types.stun_movement_command_types)
        self._update_attack(input_command_types.attack_command_types)
        
        self.last_input_command_types = input_command_types
    
    def get_last_input_command_types(self):
        return self.last_input_command_types
    
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
    
    def _update_aerial_movement(self, command_types):
        """Returns PhysicsModifiers for each command type in
        command_types.  If none of the keys_pressed are in the 
        aerial_movement_command_handler then None is returned."""
        
        command_state = self._create_aerial_movement_command_states(
            command_types
        )
        
        self.aerial_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_aerial_movement_command_states(self, command_types):
        """Creates a CommandState object from a list of command types given."""
        
        command_states = self.aerial_movement_command_handler.get_command_state()
        
        for command_type in command_types:
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _update_stun_movement(self, command_types):
        """Returns PhysicsModifiers for each command type the list 
        command_types.  If none of the keys_pressed are in the 
        stun_movement_command_handler then None is returned."""
        
        command_state = self._create_stun_movement_command_states(
            command_types
        )
        
        self.stun_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_stun_movement_command_states(self, command_types):
        """Creates a CommandState object from a list of keys_pressed for the
        stun command handler."""
        
        command_states = self.stun_movement_command_handler.get_command_state()
        
        for command_type in command_types:
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _update_ground_movement(self, command_type):
        """Returns an Action for the given command type."""
        
        command_state = self._create_ground_movement_command_states(
            command_type
        )
        
        self.ground_movement_command_handler.update_current_commands(
            command_state
        )
    
    def _create_ground_movement_command_states(self, command_type):
        """Creates a CommandState object from a list of command_types for the
        ground movement command handler."""
        
        command_states = self.ground_movement_command_handler.get_command_state()
        
        command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _update_aerial_action(self, command_types):
        """Returns an Action for the command type with the highest precdence in
        the list command_types.  If none of the keys pressed are in the 
        aerial_action_command_handler then None is returned."""
        
        command_state = self._create_aerial_action_command_states(
            command_types
        )
        
        self.aerial_action_command_handler.update_current_commands(
            command_state
        )
    
    def _create_aerial_action_command_states(self, command_types):
        """Creates a CommandState object from a list of command_types for the
        aerial action command handler."""
        
        command_states = self.aerial_action_command_handler.get_command_state()
        
        for command_type in command_types:
            command_states.set_command_state(command_type, True)
        
        return command_states
    
    def _update_attack(self, command_types):
        """Returns an attack Action that matches the command types in 
        command_types."""
        
        command_state = self._create_attack_command_states(
            command_types
        )
        
        self.attack_command_handler.update_current_commands(
            command_state
        )
    
    def _create_attack_command_states(self, command_types):
        """Creates a CommandState object from a list command_types for the
        attack command handler."""
        
        command_states = self.attack_command_handler.get_command_state()
        
        for command_type in command_types:
            command_states.set_command_state(command_type, True)
        
        return command_states

serializable.register(InputCommandTypes)
