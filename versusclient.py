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

class ClientConnectionListener(ConnectionListener):
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.player_positions = {PlayerPositions.PLAYER1:None, PlayerPositions.PLAYER2:None}
        self.spectators = []
        self.actions_received = []
    
    def close(self):
        connection.Close()
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def pop_received_actions(self):
        """returns the list of received actions and clears the list"""
        actions_received = self.actions_received
        self.actions_received = []
        
        return actions_received
    
    #Network methods
    
    def Network(self, data):
        self.actions_received.append(data)
        
        print("local client")
        print(data)
    
    def Network_player_joined(self, data):
        self.player_positions = data[DataKeys.PLAYER_POSITIONS]
        
        print("local client")
        print(data)
    
    def Network_spectator_joined(self, data):
        spectator_name = data[DataKeys.NICKNAME]
        self.spectators.append(spectator_name)
    
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

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
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
