import pygame
from wotsprot.udpclient import EndPoint

import wotsuievents
import movesetdata
import gamestate
from enumerations import PlayerPositions, SimulationDataKeys
from versusserver import DFLT_PORT, DataKeys, ServerModes

class ConnectionStatus:
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'

class ServerActions:
    JOIN_MATCH = "join_match"
    SPECTATE_MATCH = "spectate_match"
    PLAYER_READY = "player_ready"
    SET_GAME_MODE = "set_game_mode"
    END_MATCH = "end_match"
    ALL_MOVESETS_LOADED = "all_movesets_loaded"
    UPDATE_SIMULATION_STATE = "update_simulation_state"
    SEND_CHAT_MESSAGE = "send_chat_message"
    SET_MOVESET = "set_moveset"
    UPDATE_INPUT_STATE = "update_input_state"

class ClientConnectionListener(EndPoint):
    def __init__(self):
        EndPoint.__init__(self, local_address=("",0))
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.player_positions = {
            PlayerPositions.PLAYER1 : None, 
            PlayerPositions.PLAYER2 : None
        }
        self.player_positions_ready_dictionary = {
            PlayerPositions.PLAYER1 : False, 
            PlayerPositions.PLAYER2 : False
        }
        self.simulation_state = None
        self.player_input = {
            PlayerPositions.PLAYER1: None, 
            PlayerPositions.PLAYER2 : None
        }
        self.player_movesets = {
            PlayerPositions.PLAYER1 : None, 
            PlayerPositions.PLAYER2 : None
        }
        self.player_nicknames = {}
        self.spectators = []
        self.actions_received = []
        self.player_id = None
        self.server_mode = None
        self.new_simulation_state_indicator = False
        self.new_player_inputs_indicator = False
        self.new_player_input_inditicators = {
            PlayerPositions.PLAYER1 : False,
            PlayerPositions.PLAYER2 : False
        }
        self.callbacks = {}
    
    def register_callback(self, client_action, f):
        
        if client_action in self.callbacks:
            self.callbacks[client_action].append(f)
            
        else:
            self.callbacks[client_action] = [f]
    
    def clear_callbacks(self, client_action):
        
        del self.callbacks[client_action]
    
    def Close(self):
        EndPoint.Close(self)
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def pop_received_data(self):
        """returns the list of received actions and clears the list"""
        actions_received = self.actions_received
        self.actions_received = []
        
        return actions_received
    
    def send_chat_message(self, message):
        
        data = {
            DataKeys.ACTION : ServerActions.SEND_CHAT_MESSAGE,
            DataKeys.MESSAGE : message,
            DataKeys.NICKNAME : self.player_nicknames[self.player_id]
        }
        
        self.Send(data)
    
    def player_ready(self):
        data = {DataKeys.ACTION : ServerActions.PLAYER_READY}
        self.Send(data)
    
    def join_match(self):
        data = {DataKeys.ACTION : ServerActions.JOIN_MATCH}
        self.Send(data)
    
    def spectate_match(self):
        data = {DataKeys.ACTION : ServerActions.SPECTATE_MATCH}
        self.Send(data)
    
    def load_match_data(self):
        data = {
            DataKeys.ACTION : ServerActions.SET_GAME_MODE,
            DataKeys.SERVER_MODE : ServerModes.LOADING_MATCH_DATA
        }
        
        self.Send(data)
    
    def send_all_movesets_loaded(self):
        data = {DataKeys.ACTION : ServerActions.ALL_MOVESETS_LOADED}
        
        self.Send(data)
    
    def start_match(self):
        data = {
            DataKeys.ACTION : ServerActions.SET_GAME_MODE,
            DataKeys.SERVER_MODE : ServerModes.MATCH
        }
        
        self.Send(data)
    
    def end_match(self):
        data = {
            DataKeys.ACTION : ServerActions.END_MATCH
        }
        
        self.Send(data)
    
    def set_moveset(self, moveset):
        data = {
            DataKeys.ACTION : ServerActions.SET_MOVESET,
            DataKeys.MOVESET : moveset,
            DataKeys.PLAYER_POSITION : get_local_player_position()
        }
        
        self.Send(data)
    
    def send_input_to_host(self, data):
        data[DataKeys.ACTION] = ServerActions.UPDATE_INPUT_STATE
        
        self.Send(data)
    
    def get_moveset(self, player_position):
        return self.player_movesets[player_position]
    
    def del_player(self, player_to_delete_id):
        del self.player_nicknames[player_to_delete_id]
        
        if player_to_delete_id in self.spectators:
            self.spectators.remove(player_to_delete_id)
            print("spectator deleted")
        
        self.remove_player_from_match(player_to_delete_id)
    
    def remove_player_from_match(self, player_to_remove_id):
        for player_position, player_id in self.player_positions.iteritems():
            if player_to_remove_id == player_id:
                self.player_positions[player_position] = None
                self.player_positions_ready_dictionary[player_position] = False
                self.player_states[player_position] = None
                print("player deleted")
    
    def all_player_data_received(self):
        """If any player state is null this returns false."""
        return_indicator = True
        
        for player_state in self.player_states.values():
            if player_state == None:
                return_indicator = False
        
        return return_indicator
    
    def get_remote_input(self):
    
        self.new_player_inputs_indicator = False
        return self.player_inputs
    
    def get_server_simulation_state(self, data):
        
        self.new_player_states_indicator = False
        return self.simulation_state
    
    def update_simulation_state(self, simulation_state):
        
        if self.server_mode == ServerModes.MATCH:
            data = {
                DataKeys.ACTION : ServerActions.UPDATE_SIMULATION_STATE,
                DataKeys.SIMULATION_STATE : simulation_state
            }
            
            self.Send(data)
        
    def clear_player_states(self):
        for player_position in self.player_states.keys():
            self.player_states[player_position] = None
            self.player_movesets[player_position] = None
            self.player_input[player_position] = None
        
        self.new_player_inputs_indicator = False
        self.new_simulation_state_indicator = False
        self.simulation_state = None
    
    
    #Network methods
    
    def Network(self, data):
        if self.connection_status != ConnectionStatus.CONNECTED:
            self.connection_status = ConnectionStatus.CONNECTED
        
        self.actions_received.append(data)
        
        action = data[DataKeys.ACTION]
        if action in self.callbacks:
            for f in self.callbacks[action]:
                f(data)
        
        #print("local client")
        #print(data)
    
    def Network_player_joined_match(self, data):
        player_position = data[DataKeys.PLAYER_POSITION]
        id_of_player_at_position = data[DataKeys.PLAYER_ID]
        
        self.player_positions[player_position] = id_of_player_at_position
    
    def Network_player_joined(self, data):
        self.player_positions = data[DataKeys.PLAYER_POSITIONS]
    
    def Network_player_disconnected(self, data):
        deleted_player_id = data[DataKeys.PLAYER_ID]
        self.del_player(deleted_player_id)
    
    def Network_spectator_joined(self, data):
        spectator_name = data[DataKeys.NICKNAME]
        spectator_id = data[DataKeys.PLAYER_ID]
        
        self.spectators.append(spectator_id)
        self.player_nicknames[spectator_id] = spectator_name
        
        self.remove_player_from_match(spectator_id)
    
    def Network_get_player_id(self, data):
        self.player_id = data[DataKeys.PLAYER_ID]
    
    def Network_set_moveset(self, data):
        
        player_position = data[DataKeys.PLAYER_POSITION]
        self.player_movesets[player_position] = data[DataKeys.MOVESET]
    
    def Network_sync_to_server(self, data):
        """syncs client data on connected players with server"""
        
        #rencode sends lists accross as tuples so convert it back into a list
        self.spectators = [spectator_id for spectator_id in data[DataKeys.SPECTATORS]]
        
        self.player_positions = data[DataKeys.PLAYER_POSITIONS]
        self.player_nicknames = data[DataKeys.PLAYER_NICKNAMES]
        self.player_positions_ready_dictionary = data[DataKeys.PLAYER_POSITIONS_READY]
        self.player_movesets = data[DataKeys.PLAYER_MOVESETS]
        
        self.server_mode = data[DataKeys.SERVER_MODE]
    
    def Network_match_full(self, data):
        pass
    
    def Network_set_game_mode(self, data):
        self.server_mode = data[DataKeys.SERVER_MODE]
        print("client view of server")
        print(self.server_mode)
    
    def Network_end_match(self, data):
        self.server_mode = ServerModes.MOVESET_SELECT
        
        print("client view of server")
        print(self.server_mode)
    
    def Network_player_ready(self, data):
        player_position = data[DataKeys.PLAYER_POSITION]
        
        self.player_positions_ready_dictionary[player_position] = \
            data[DataKeys.PLAYER_READY_INDICATOR]
    
    def Network_receive_chat_message(self, data):
        pass
    
    # built in stuff

    def Network_socketConnect(self, data):
        self.connection_status = ConnectionStatus.CONNECTED
    
    def Network_connected(self, data):
        self.connection_status = ConnectionStatus.CONNECTED
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        self.Close()
        self.connection_status = ConnectionStatus.ERROR
    
    def Network_disconnected(self, data):
        print 'Server disconnected'
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.player_id = None
        self.server_mode = ServerModes.MOVESET_SELECT

listener = None

def load():
    global listener
    
    listener = ClientConnectionListener()

def unload():
    global listener
    
    listener = None

def update_player_state(player_state_dictionary, player_position):
    listener.update_player_state(player_state_dictionary, player_position)

def get_player_state(player_position):
    return listener.simulation_state.player_states[player_position]

def local_player_match_data_loaded():
    player_position = get_local_player_position()
    
    if listener.simulation_state.player_states[player_position] == None:
        return False
    else:
        return True

def get_local_player_position():
    for player_position, player_id in listener.player_positions.iteritems():
        if player_id == listener.player_id:
            return player_position
    
    return PlayerPositions.NONE

def local_player_is_in_match(): 
    if listener == None:
        return False
    elif listener.player_id == None:
        return False
    else:
        if listener.player_id in listener.player_positions.values():
            return True
        else:
            return False

def get_remote_player_positions():
    remote_player_positions = []
    
    for position, player_id in listener.player_positions.iteritems():
        if not (player_id == None or player_id == listener.player_id):
            remote_player_positions.append(position)
    
    return remote_player_positions

def get_player_id_at_position(player_position):
    return listener.player_positions[player_position]

def get_player_nickname(player_id):
    return listener.player_nicknames[player_id]

def connected():
    if listener == None:
        return False
    elif listener.connection_status == ConnectionStatus.CONNECTED:
        return True
    else:
        return False

def send_chat_message(message):
    listener.send_chat_message(message)

def client_was_connected():
    return not listener.player_id == None

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
    global listener
    
    if listener == None:
        listener = ClientConnectionListener()
    
    listener.connection_status = ConnectionStatus.CONNECTING
    listener.Connect((host_ip_address, DFLT_PORT))

def get_network_messages():
    listener.Pump()

def clear_player_states():
    """sets all player states to None"""
    
    if listener != None:
        listener.clear_player_states()

def get_connection_status():
    """returns whether the game is connected to a server"""
    global listener
    
    if listener:
        return listener.connection_status
    else:
        return ConnectionStatus.DISCONNECTED
