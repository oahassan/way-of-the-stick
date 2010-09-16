import pygame
from PodSixNet.Connection import connection, ConnectionListener

import wotsuievents
import movesetdata
import gamestate
import versusmode

import button
import movesetselectui
import wotsuicontainers

def connect_to_host(host, port):
    connection.Connect((host, port))

class ClientConnectionListener(ConnectionListener):
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
		print "You are now connected to the server"
	
	def Network_error(self, data):
		print 'error:', data['error'][1]
		connection.Close()
	
	def Network_disconnected(self, data):
		print 'Server disconnected'
		connection.Close()
