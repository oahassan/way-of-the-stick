import pygame
from PodSixNet.Connection import connection, ConnectionListener

import wotsuievents
import movesetdata
import gamestate
import versusmode
from versusserver import DFLT_PORT, PlayerPositions, DataKeys, ServerModes

import button
import movesetselectui
import wotsuicontainers

class ConnectionStatus:
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'

class ServerActions:
    JOIN_MATCH = "join_match"
    SPECTATE_MATCH = "spectate_match"
    PLAYER_READY = "player_ready"
    SET_GAME_MODE = "set_game_mode"
    END_MATCH = "end_match"
    INITIAL_PLAYER_STATES_RECEIVED = "initial_player_states_received"
    SEND_INITIAL_PLAYER_STATE = "send_initial_player_state"
    UPDATE_PLAYER_STATE = "update_player_state"

class ClientConnectionListener(ConnectionListener):
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.player_positions = \
            {PlayerPositions.PLAYER1 : None, PlayerPositions.PLAYER2 : None}
        self.player_positions_ready_dictionary = \
            {PlayerPositions.PLAYER1 : False, PlayerPositions.PLAYER2 : False}
        self.player_states = \
            {PlayerPositions.PLAYER1 : None, PlayerPositions.PLAYER2 : None}
        self.player_nicknames = {}
        self.spectators = []
        self.actions_received = []
        self.player_id = None
        self.server_mode = None
    
    def close(self):
        connection.Close()
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def pop_received_data(self):
        """returns the list of received actions and clears the list"""
        actions_received = self.actions_received
        self.actions_received = []
        
        return actions_received
    
    def player_ready(self):
        data = {DataKeys.ACTION : ServerActions.PLAYER_READY}
        connection.Send(data)
    
    def join_match(self):
        data = {DataKeys.ACTION : ServerActions.JOIN_MATCH}
        connection.Send(data)
    
    def spectate_match(self):
        data = {DataKeys.ACTION : ServerActions.SPECTATE_MATCH}
        connection.Send(data)
    
    def load_match_data(self):
        data = {
            DataKeys.ACTION : ServerActions.SET_GAME_MODE,
            DataKeys.SERVER_MODE : ServerModes.LOADING_MATCH_DATA
        }
        
        connection.Send(data)
    
    def start_match(self):
        data = {
            DataKeys.ACTION : ServerActions.SET_GAME_MODE,
            DataKeys.SERVER_MODE : ServerModes.MATCH
        }
        
        connection.Send(data)
    
    def end_match(self):
        data = {
            DataKeys.ACTION : ServerActions.END_MATCH
        }
        
        connection.Send(data)
    
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
                print("player deleted")
    
    def all_player_states_received(self):
        """If any player state is null this returns false."""
        return_indicator = True
        
        for player_state in self.player_states.values():
            if player_state == None:
                return_indicator = False
        
        return return_indicator
    
    def send_player_initial_state(self, player_state_dictionary, player_position):
        """notify the server of a local players initial state"""
        
        data = \
            {
                DataKeys.ACTION : ServerActions.SEND_INITIAL_PLAYER_STATE,
                DataKeys.PLAYER_STATE : player_state_dictionary,
                DataKeys.PLAYER_POSITION : get_local_player_position()
            }
        
        connection.Send(data)
    
    def update_player_state(self, player_state_dictionary, player_position):
        
        if self.server_mode == ServerModes.MATCH:
            data = \
                {
                    DataKeys.ACTION : ServerActions.UPDATE_PLAYER_STATE,
                    DataKeys.PLAYER_STATE : player_state_dictionary,
                    DataKeys.PLAYER_POSITION : get_local_player_position()
                }
            
            connection.Send(data)
        
    def clear_player_states(self):
        for player_position in self.player_states.keys():
            self.player_states[player_position] = None
    
    #Network methods
    
    def Network(self, data):
        self.actions_received.append(data)
        
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
    
    def Network_sync_to_server(self, data):
        """syncs client data on connected players with server"""
        
        #rencode sends lists accross as tuples so convert it back into a list
        self.spectators = [spectator_id for spectator_id in data[DataKeys.SPECTATORS]]
        
        self.player_positions = data[DataKeys.PLAYER_POSITIONS]
        self.player_nicknames = data[DataKeys.PLAYER_NICKNAMES]
        self.player_positions_ready_dictionary = data[DataKeys.PLAYER_POSITIONS_READY]
        
        self.server_mode = data[DataKeys.SERVER_MODE]
    
    def Network_receive_player_initial_state(self, data):
        """receive the inital state of a remote player.  If all states have been received
        notify the server."""
        player_position = data[DataKeys.PLAYER_POSITION]
        
        self.player_states[player_position] = data[DataKeys.PLAYER_STATE]
        
        if self.all_player_states_received():
            #notify server that all player states have been received
            data = {DataKeys.ACTION : ServerActions.INITIAL_PLAYER_STATES_RECEIVED}
            
            connection.Send(data)
    
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
        
    
    def Network_update_player_state(self, data):
    
        if self.server_mode == ServerModes.MATCH:
            player_position = data[DataKeys.PLAYER_POSITION]
            
            self.player_states[player_position] = data[DataKeys.PLAYER_STATE]
    
    # built in stuff

    def Network_socketConnect(self, data):
        self.connection_status = ConnectionStatus.CONNECTED
    
    def Network_connected(self, data):
        self.connection_status = ConnectionStatus.CONNECTED
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        connection.Close()
        self.connection_status = ConnectionStatus.ERROR
    
    def Network_disconnected(self, data):
        print 'Server disconnected'
        #connection.Close()
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
    return listener.player_states[player_position]

def local_player_match_data_loaded():
    player_position = get_local_player_position()
    
    if listener.player_states[player_position] == None:
        return False
    else:
        return True

def get_local_player_position():
    for player_position, player_id in listener.player_positions.iteritems():
        if player_id == listener.player_id:
            return player_position

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

def client_was_connected():
    return not listener.player_id == None

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
    global listener
    
    if listener == None:
        listener = ClientConnectionListener()
    
    listener.Connect((host_ip_address, DFLT_PORT))

def get_network_messages():
    connection.Pump()

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
