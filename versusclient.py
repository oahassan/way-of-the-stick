import pygame
from PodSixNet.Connection import connection, ConnectionListener

import wotsuievents
import movesetdata
import gamestate
import versusmode
from versusserver import DFLT_PORT

import button
import movesetselectui
import wotsuicontainers

class ConnectionStatus:
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'

listener = None

class ClientConnectionListener(ConnectionListener):
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def close(self):
        connection.Close()
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    #Network methods
    
    def Network(self, data):
        print("local client")
        print(data)
    
    def Network_player_joined(self, data):
        print("local client")
        print(data)
    
    def Network_spectator_joined(self, data):
        print("local client")
        print(data)
    
    def Network_update_player_state(self, data):
        pass
    
    # built in stuff

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

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
    global listener
    
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
