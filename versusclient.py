import urllib
import socket

import pygame
from PodSixNet.Connection import connection, ConnectionListener

import wotsuievents
import movesetdata
import gamestate
import versusmode

import button
import movesetselectui
import wotsuicontainers

class ConnectionStatus:
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'

DFLT_PORT = 749387

listner = None

def get_public_ip_addr():
    """this only works if you have an internet connection"""
    return \
        urllib.urlopen('http://www.whatismyip.com/automation/n09230945.asp').read()

def get_lan_ip_addr():
    """TODO - this only works if you have an internet connection so I need to find a
    better method"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    return s.getsockname()[0]

def connect_to_host(host_ip_address):
    """connects to a server using the default port specified in DFLT_PORT"""
    
    listner = ClientConnectionListner()
    listner.Connect((host_ip_address, DFLT_PORT))

def get_connection_status():
    """returns whether the game is connected to a server"""
    if listner:
        return listner.connection_status
    else:
        return ConnectionStatus.DISCONNECTED

class ClientConnectionListener(ConnectionListener):
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
    
    def Network(self, data):
        print(data)
    
    def Network_player_joined(self, data):
        print(data)
    
    def Network_spectator_joined(self, data):
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
        connection.Close()
        self.connection_status = ConnectionStatus.DISCONNECTED
