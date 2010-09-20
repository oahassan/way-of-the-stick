import pygame
from PodSixNet.Connection import connection, ConnectionListener

import wotsuievents
import movesetdata
import gamestate
import versusmode
from versusserver import DFLT_PORT, PlayerPositions, DataKeys

import button
import movesetselectui
import wotsuicontainers

class ConnectionStatus:
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'

class ServerActions:
    JOIN_MATCH = "join_match"

class ClientConnectionListener(ConnectionListener):
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.player_positions = {PlayerPositions.PLAYER1:None, PlayerPositions.PLAYER2:None}
        self.player_nicknames = {}
        self.spectators = []
        self.actions_received = []
        self.player_id = None
    
    def close(self):
        connection.Close()
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def pop_received_actions(self):
        """returns the list of received actions and clears the list"""
        actions_received = self.actions_received
        self.actions_received = []
        
        return actions_received
    
    def join_match(self):
        data = {DataKeys.ACTION : ServerActions.JOIN_MATCH}
        connection.Send(data)
    
    #Network methods
    
    def Network(self, data):
        self.actions_received.append(data)
        
        print("local client")
        print(data)
    
    def Network_get_player_position(self, data):
        player_position = data[DataKeys.PLAYER_POSITION]
        id_of_player_at_position = data[DataKeys.PLAYER_ID]
        
        self.player_positions[player_position] = id_of_player_at_position
    
    def Network_player_joined(self, data):
        self.player_positions = data[DataKeys.PLAYER_POSITIONS]
    
    def Network_spectator_joined(self, data):
        spectator_name = data[DataKeys.NICKNAME]
        spectator_id = data[DataKeys.PLAYER_ID]
        
        self.spectators.append(spectator_id)
        self.player_nicknames[spectator_id] = spectator_name 
    
    def Network_get_player_id(self, data):
        self.player_id = data[DataKeys.PLAYER_ID]
    
    def Network_update_player_state(self, data):
        pass
    
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

listener = ClientConnectionListener()

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

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
    global listener
    
    if listener == None:
        listener = ClientConnectionListener()
    
    listener.Connect((host_ip_address, DFLT_PORT))

def get_network_messages():
    connection.Pump()

def get_connection_status():
    """returns whether the game is connected to a server"""
    global listener
    
    if listener:
        return listener.connection_status
    else:
        return ConnectionStatus.DISCONNECTED
