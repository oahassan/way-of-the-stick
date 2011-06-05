"""
The command module is used for determining what the resulting action is from a
sequence of player inputs. It consists of the classes:
    
    CommandHandler
    Command
    CommandState

The CommandHandler allows you to store a value for a given sequence of
commands in a command tree. The value can be whatever you want (e.g. an object, 
string, etc.).  Each command in the sequence must be a Command instance.
Command is a data class that contains a user defined type and a duration defined
in enumerations.CommandDurations.

Currently, when adding a command sequence every permutation of the command 
sequence is added to the command tree. So, when you want to retrieve a value 
the sequence can be in any order. It also means that sequences that have the 
same commands, but different orders are equivalent.

    example:
    
        [TAP_RIGHT, TAP_MEDIUM_KICK] == \
            [TAP_MEDIUM_KICK, TAP_RIGHT]

The CommandHandler also keeps a history of commands in a list of CommandState
objects.  A CommandState object stores which of the command types a
CommandHandler accepts are currently active. 

Note: you should use the get_empty_command_state method of a CommandHandler to
create CommandStates to make sure your CommandState object matches your 
CommandHandlers valid command types.

A CommandHandler uses the 
history of CommandStates to determine what Commands are currently active. 
Calling its Update method with a CommandState object containing the current 
active command types will change the current tree commands. Calling 
get_current_action will return the value for the current combination of 
tree commands.


TODO
    1. allow ordered sequences in command trees
"""

import inputtree
from wotsprot.rencode import serializable
from enumerations import InputActionTypes, CommandDurations
from collections import deque

class Command:
    """This class stores data about the type and duration of a command"""
    def __init__(self, command_type, duration):
        self.command_type = command_type
        self.duration = duration
    
    def _pack(self):
        return (command_type, duration)
    
    def __str__(self):
        return ("Command Type: {0}, Duration: {1}".format(
            self.command_type.__str__(),
            self.duration.__str__()
        ))
    
    def __repr__(self):
        return ("Command Type: {0}, Duration: {1}".format(
            self.command_type.__str__(),
            self.duration.__str__()
        ))
    
    def __hash__(self):
        return (self.command_type + self.duration).__hash__()
    
    def __eq__(self, other):
        if not isinstance(other, Command):
            raise Exception("Cannot compare type Command and type " + other.__class__())
        
        if (other.command_type == self.command_type and
        other.duration == self.duration):
            return True
        else:
            return False
    
    def __ne__(self, other):
        if not isinstance(other, Command):
            raise Exception("Cannot compare type Command and type " + other.__class__())
        
        return (other.command_type != self.command_type or
            other.duration != self.duration)

class CommandState:
    """This class is a dictionary containing which commands are
    active in a given game step."""
    
    def __init__(self, command_types):
        
        self._command_states = dict(
            [(command, False) for command in command_types]
        )
    
    def __eq__(self, other):
        return self._command_states == other._command_states
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        
        return self._command_states.__str__()
    
    def __repr__(self):
    
        return self._command_states.__str__()
    
    def set_command_state(self, command, active_indicator):
        """Sets the state of the given command to the given indicator value.
        The command must be in the command state dictionary.  The active
        indicator should have a value of true or false."""
        
        if command in self._command_states:
            if active_indicator == True or active_indicator == False:
            
                self._command_states[command] = active_indicator
            else:
                raise Exception(
                    "active indicator must be True or False.  Got " + 
                    str(active_indicator)
                )
        else:
            raise Exception(
                "Command not found in self.command_states: " + str(command)
            )
    
    def get_command_state(self, command):
        """returns the true if the command is active.  Otherwise it returns
        false. An exception is raised if the command is not in command statuses
        dictionary."""
        
        if command in self._command_states:
            return self._command_states[command]
        else:
            raise Exception(
                "Command not found in self.command_states: " + str(command)
            )

class CommandHandler:
    """This class keeps a history of pressed commands and can tell you what the
    currently active commands are"""
    
    def __init__(self, command_types):
        #a list of valid command types
        self.command_types = command_types
        
        #a dictionary mapping command types to tap commands
        self.tap_commands = self._create_command_dictionary(
            CommandDurations.TAP,
            command_types
        )
        
        #a dictionary mapping command types to hold commands
        self.hold_commands = self._create_command_dictionary(
            CommandDurations.HOLD, 
            command_types
        )
        
        #history of previously active commands
        self.command_buffer = deque()
        
        #max length command states kept in the history
        self.command_buffer_max_length = 30
        
        #the maximum number of history entries between the same command
        #to register a double click
        self.repeat_command_count_threshold = 8
        
        #the minimum number of history entries of a consecutive command to
        #register a HOLD command
        self.hold_count_threshold = 5
        
        #the currently active commands
        self.current_commands = []
        
        #the types of the currently active commands
        self.current_command_types = []
        
        #the count of the number of calls to Update.  It serves as a measure of
        #time for commands.
        self.command_sequence = 0
        
        #A dictionary of command trees
        self.command_tree = inputtree.InputTree()
    
    def _create_command_dictionary(self, command_duration, command_types):
        """builds a dictionary mapping the command types to Commands with the 
        given duration"""
        
        return dict([(command_type, Command(command_type, command_duration)) for command_type in command_types])
    
    def add_command(self, command_sequence, value):
        """add a sequence of commands and the resulting action to the correct
        command tree"""
        
        self._validate_command_sequence(command_sequence)
        self.command_tree.add_branches(command_sequence, value)
    
    def get_command_sequence_value(self, command_sequence):
        """Retrieve the value matching the given command sequence if it exists
        in the command tree."""
        
        self._validate_command_sequence(command_sequence)
        
        return_value = self.command_tree.get_value(command_sequence)
            
        if return_value == None:
            return_value = self.command_tree.get_value(command_sequence[-1:])
        
        return return_value
    
    def get_current_command_sequence_value(self):
        """returns the value for the current command sequence in the inputtree.
        If the command sequence doesn't exist None is returned."""
        
        return self.get_command_sequence_value(self.current_commands)
    
    def get_command_state(self):
        """returns a command state object with command types matching this 
        CommandHandler.  State is intialized to false for each command type"""
        return CommandState(self.command_types)
    
    def update_current_commands(self, command_states):
        """takes in the current raw commands and updates the current command 
        list and command durations"""
        
        if not isinstance(command_states, CommandState):
            raise Exception("command_state must be a CommandState object.")
        
        self._update_current_command_types(command_states)
        self._update_current_commands(command_states)
        
        if len(self.command_buffer) > self.command_buffer_max_length:
            self.command_buffer.popleft()
        self.command_buffer.append(self.current_commands)
        
        self.command_sequence += 1
    
    def _update_current_command_types(self, command_states):
        """Sets the current command type list to only contain active command
        types in the given CommandState"""
        
        current_command_types = []
        
        for command_type in self.command_types:
            if command_states.get_command_state(command_type):
                current_command_types.append(command_type)
        
        self.current_command_types = current_command_types
    
    def _update_current_commands(self, command_states):
        """Sets the next current command list based on the the command history 
        and the list of current commands"""
        
        current_commands = self._get_input_commands(command_states)
        current_commands.extend(self._get_repeated_commands(current_commands))
        
        self.current_commands = current_commands
    
    def _get_input_commands(self, command_states):
        """get a list of active commands in the given CommandState"""
        
        commands = []
        
        for command_type in self.command_types:
            if command_states.get_command_state(command_type):
                duration = self._get_command_duration(command_type)
                
                if duration == CommandDurations.TAP:
                    
                    commands.append(self.tap_commands[command_type])
                
                elif duration == CommandDurations.HOLD:
                    
                    commands.append(self.hold_commands[command_type])
                    
                else:
                    raise Exception(
                        "Invalid Command Duration: " + str(duration)
                    )
        
        return commands
    
    def _get_repeated_commands(self, current_commands):
        """Get a list of commands that have been repeated within the repeat
        threshold of this CommandHandler."""
        
        commands = []
        
        #determine the number of past command_sequences to look through
        previous_command_buffer_length = min(
            len(self.command_buffer), self.repeat_command_count_threshold
        )
        
        if previous_command_buffer_length > 0:
            previous_command_buffers = [self.command_buffer[i] for i in range(-previous_command_buffer_length, 0)]
            
            #order buffers from newest to oldest
            reverse_buffers = list(previous_command_buffers)
            reverse_buffers.reverse()
            
            for command in current_commands:
                command_absent = False
                command_repeated = False
                
                for index in range(len(reverse_buffers)):
                    
                    if not command_absent:
                        #search from a command without the current command
                        if not command in reverse_buffers[index]:
                            command_absent = True
                            
                    else:
                        if not command_repeated:
                            #if a command list without the current command is found
                            #search previous command lists for the command
                            if command in reverse_buffers[index]:
                                command_repeated = True
                                break
                
                if command_repeated:
                    commands.append(command)
        
        return commands
    
    def _get_command_duration(self, command_type):
        """Returns how many consecutive command_states the given command type
        is active in since the most recent command_state."""
        
        hold_count = 0
        
        reverse_buffer = list(self.command_buffer)
        reverse_buffer.reverse()
        
        for index in range(len(reverse_buffer)):
            tap_command = self.tap_commands[command_type]
            hold_command = self.hold_commands[command_type]
            
            if (tap_command in reverse_buffer[index] or
            hold_command in reverse_buffer[index]):
                hold_count += 1
            else:
                break
        
        if hold_count > self.hold_count_threshold:
            return CommandDurations.HOLD
        else:
            return CommandDurations.TAP
    
    def _validate_command_sequence(self, command_sequence):
        """check that a command sequence only contains valid commands"""
        
        for command in command_sequence:
            if not isinstance(command, Command):
                raise Exception(
                    "command_sequence contains an invalid command type: " + 
                    str(command.__class__())
                )
            
            if not command.command_type in self.command_types:
                raise Exception("""
                Invalid command type in command_sequence.
                Valid values are {0}.
                Got {1}""".format(self.command_types, command.command_type)
            )

serializable.register(Command)

if __name__ == '__main__':
    import unittest
    
    class CommandTest(unittest.TestCase):
        
        def setUp(self):
            self.command1 = Command('1', CommandDurations.TAP)
            self.command1_2 = Command('1', CommandDurations.TAP)
            self.command2 = Command('2', CommandDurations.TAP)
            self.command_state = CommandState(['1', '2'])
            self.command_state_2 = CommandState(['1', '2'])
            self.command_state2 = CommandState(['2', '3'])
            self.command_types = ['1', '2']
            self.handler = handler = CommandHandler(self.command_types)
            self.command_sequence = [
                self.command1,
                self.command2
            ]
        
        def tearDown(self):
            del self.command1
            del self.command1_2
            del self.command2
            del self.command_state
            del self.command_state_2
            del self.command_state2
            del self.command_types
            del self.handler
            del self.command_sequence
        
        def test_command_equivalence(self):
        
            print("test command equivalence")
            self.assertEqual(self.command1, self.command1_2)
        
        def test_command_inequivalence(self):
            print("test command not equal")
            
            self.assertNotEqual(self.command1, self.command2)
        
        def test_command_hash(self):
            print("test command hash")
            
            self.assertEqual(
                (self.command_types[0] + CommandDurations.TAP).__hash__(),
                self.command1.__hash__()
            )
        
        def test_command_state_equal(self):
            print("test command state equivalence")
            self.assertEqual(self.command_state, self.command_state_2)
        
        def test_command_state_not_equal(self):
            print("test command state not equal")
            self.assertNotEqual(self.command_state, self.command_state2)
        
        def test_set_and_get_command_state(self):
            print("test setting and getting the state of command from a CommandState")
            self.command_state.set_command_state('1', True)
            self.assertEqual(self.command_state.get_command_state('1'), True)
        
        def test_create_command_handler(self):
            print("test a creating a command handler")
            
            self.assertEqual(self.handler.command_types, self.command_types)
            self.assertEqual(
                self.handler.tap_commands,
                dict(zip(self.command_types, [self.command1, self.command2]))
            )
            self.assertEqual(
                self.handler.hold_commands,
                dict(zip(
                    self.command_types,
                    [Command(command_type, CommandDurations.HOLD) for command_type in self.command_types]
                ))
            )
        
        def test_adding_command_to_handler(self):
            print("test adding a command to a command handler")
            self.handler.add_command([self.command1, self.command2], 'blah')
            self.assertEqual(
                self.handler.command_tree.__str__(),
                """
key: Command Type: 1, Duration: tap value: None
    key: Command Type: 2, Duration: tap value: blah
key: Command Type: 2, Duration: tap value: None
    key: Command Type: 1, Duration: tap value: blah"""
                )
        
        def test_get_command_state_from_handler(self):
            print("test command state from handler")
            self.assertEqual(
                self.command_state,
                self.handler.get_command_state()
            )    
        
        def test_add_command(self):
            print("test adding command to handler")
            self.handler.add_command(self.command_sequence, "BooYah!")
            self.assertEqual(
                self.handler.command_tree.get_value(
                    self.command_sequence
                ),
                "BooYah!"
            )
        
        def test_update_handler_current_commands(self):
            print("testing updating current commands")
            command_states = self.handler.get_command_state()
            command_states.set_command_state(self.command_types[0], True)
            self.handler.update_current_commands(command_states)
            
            self.assertEqual(
                self.handler.current_command_types,
                [self.command_types[0]]
            )
            self.assertEqual(
                self.handler.current_commands,
                [self.command1]
            )
        
        def test_double_tap(self):
            print("test double tap command")
            command_states = self.handler.get_command_state()
            command_states.set_command_state(self.command_types[0], True)
            self.handler.update_current_commands(command_states)
            
            next_states = self.handler.get_command_state()
            self.handler.update_current_commands(next_states)
            
            last_states = self.handler.get_command_state()
            last_states.set_command_state(self.command_types[0], True)
            self.handler.update_current_commands(last_states)
            
            self.assertEqual(
                self.handler.current_command_types,
                [self.command_types[0]]
            )
            self.assertEqual(
                self.handler.current_commands,
                [self.command1, self.command1]
            )
        
        def test_get_current_command_value(self):
            print(
                "test get current command value where commands map to a value"
            )
            self.handler.add_command(self.command_sequence, "BooYah!")
            command_states = self.handler.get_command_state()
            command_states.set_command_state(self.command_types[0], True)
            command_states.set_command_state(self.command_types[1], True)
            self.handler.update_current_commands(command_states)
            
            self.assertEqual(
                self.handler.get_current_command_sequence_value(),
                "BooYah!"
            )
            
        def test_get_current_command_value_with_no_matching_value(self):
            print(
                "test get current command value when the current commands" + 
                "don't match an added command"
            )
            print(
                "test get current command value where commands map to a value"
            )
            self.handler.add_command(self.command_sequence, "BooYah!")
            command_states = self.handler.get_command_state()
            command_states.set_command_state(self.command_types[0], True)
            self.handler.update_current_commands(command_states)
            
            self.assertEqual(
                self.handler.get_current_command_sequence_value(),
                None
            )
            
    unittest.main()
