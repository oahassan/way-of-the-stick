import urllib
import socket

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

class PlayerPositions:
    NONE = "none"
    PLAYER1 = "player1"
    PLAYER2 = "player2"

class DataKeys:
    ACTION = "action"
    NICKNAME = "nickname"
    PLAYER_POSITIONS = "player_positions"
    PLAYER_POSITION = "player_position"
    PLAYER_ID = "player_id"

class ClientActions:
    SPECTATOR_JOINED = "spectator_joined"
    GET_PLAYER_ID = "get_player_id"
    GET_PLAYER_POSITION = "get_player_position"

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        
        self.nickname = self._server.generate_nickname()
        self.postion = PlayerPositions.NONE
    
    def Network(self, data):
        print("Server channel")
        print(data)
    
    def Network_join_match(self, data):
        player_position = self._server.add_player(self)
        
        data = \
            {
                DataKeys.ACTION : ClientActions.GET_PLAYER_POSITION,
                DataKeys.PLAYER_POSITION : player_position
            }
        
        self.Send(data)
    
    def Network_spectate_match(self, data):
        pass
    
    def Network_update_player_state(self, data):
        pass
    
    def Network_player_ready(self, data):
        pass
    
    def Close(self):
        print("deleting player: " + self.nickname)
        self._server.del_player(self)

class WotsServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, channelClass=None, localaddr=("127.0.0.1", 31425), listeners=5):
        Server.__init__(self, channelClass, localaddr, listeners)
        self.player_name_count = 0
        self.player_positions = \
            {
                PlayerPositions.PLAYER1 : None,
                PlayerPositions.PLAYER2 : None,
                PlayerPositions.NONE : []
            }
        self.players = []
        self.spectators = []
        
        print 'server started!'
    
    def Connected(self, channel, addr):
        print 'new connection:', channel
        
        self.assign_id(channel)
        self.add_spectator(channel)
    
    def close(self):
        """remove all players and close the sever's socket"""
        for spectator in self.spectators:
            spectator.close()
        
        for player in self.players:
            player.close()
        
        Server.close(self)
    
    def generate_nickname(self):
        """creates a player name and increments the number of the player name"""
        player_name = "stick" + str(self.player_name_count + 1)
        self.player_name_count += 1
        
        return player_name
    
    def assign_id(self, player):
        """sends a players server id to their client"""
        data = \
            {
                DataKeys.ACTION : ClientActions.GET_PLAYER_ID,
                DataKeys.PLAYER_ID : id(player)
            }
        
        player.Send(data)
    
    def add_spectator(self, player):
        """Add a spectator to the server"""
        print("spectator joined " + player.nickname)
        self.spectators.append(player)
        
        data = \
            {
                DataKeys.ACTION : ClientActions.SPECTATOR_JOINED,
                DataKeys.NICKNAME : player.nickname
            }
        
        self.send_to_all(data)
    
    def add_player(self, player):
        """Assign the player to a position and return its position.  If all positions are
        taken return the NONE position."""
        
        player1 = self.player_positions[PlayerPositions.PLAYER1]
        player2 = self.player_positions[PlayerPositions.PLAYER2]
        
        if player1 == None and not player == player2:
            self.player_positions[PlayerPositions.PLAYER1] = player
            self.players.append(player)
            
            return PlayerPositions.PLAYER1
            
        elif player2 == None and not player == player1:
            self.player_positions[PlayerPositions.PLAYER2] = player
            self.players.append(player)
            
            return PlayerPositions.PLAYER2
            
        elif not (player == player1 or player == player2):
            return PlayerPositions.NONE
        else:
            #do nothing because the player has already joined the match
            pass
    
    def del_player(self, player):
        """remove a player from the server"""
        if player == self.player_positions[PlayerPositions.PLAYER1]:
            self.player_positions[PlayerPositions.PLAYER1] = None
        elif player == self.player_positions[PlayerPositions.PLAYER2]:
            self.player_positions[PlayerPositions.PLAYER2] = None
        
        if player in self.players:
            self.players.remove(player)
        
        if player in self.spectators:
            self.spectators.remove(player)
    
    def send_to_all(self, data):
        """send data to all connected players"""
        [player.Send(data) for player in self.players]
        [spectator.Send(data) for spectator in self.spectators]

server = None

DFLT_PORT = 749387

listner = None

def get_public_ip_address():
    """this only works if you have an internet connection"""
    return \
        urllib.urlopen(
            'http://www.whatismyip.com/automation/n09230945.asp'
        ).read()

def get_lan_ip_address():
    """TODO - this only works if you have an internet connection so I need to find a
    better method"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    return s.getsockname()[0]

def start_public_server():
    global server
    
    server = WotsServer(localaddr=(get_public_ip_address(), int(DFLT_PORT)))

def start_lan_server():
    global server
    
    server = WotsServer(localaddr=(get_lan_ip_address(), int(DFLT_PORT)))

def server_ready():
    if server:
        return True
    else:
        return False
