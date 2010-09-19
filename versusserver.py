import urllib
import socket

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        
        self.nickname = self._server.generate_nickname()
    
    def Network():
        print(data)
    
    def Network_join_match(data):
        pass
    
    def Network_spectate_match(data):
        pass
    
    def Network_update_player_state(data):
        pass
    
    def Network_player_ready(data):
        pass

class WotsServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, channelClass=None, localaddr=("127.0.0.1", 31425), listeners=5):
        Server.__init__(self, channelClass, localaddr, listeners)
        self.player_name_count = 0
        self.players = []
        self.spectators = []
        
        print 'server started!'
    
    def Connected(self, channel, addr):
        print 'new connection:', channel
        self.spectators.append(channel)
    
    def generate_nickname(self):
        """creates a player name and increments the number of the player name"""
        player_name = "player" + str(self.player_name_count + 1)
        self.player_name_count += 1
        
        return player_name

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
