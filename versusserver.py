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
    PLAYER_NICKNAMES = "player_nicknames"
    PLAYER_POSITIONS = "player_positions"
    SPECTATORS = "spectators"
    PLAYERS = "players"
    PLAYER_POSITION = "player_position"
    PLAYER_ID = "player_id"
    PLAYER_POSITIONS_READY = "player_positions_ready"
    SERVER_MODE = "server_mode"

class ClientActions:
    SPECTATOR_JOINED = "spectator_joined"
    GET_PLAYER_ID = "get_player_id"
    GET_PLAYER_POSITION = "get_player_position"
    SYNC_TO_SERVER = "sync_to_server"
    PLAYER_DISCONNECTED = "player_disconnected"
    MATCH_FULL = "match_full"
    PLAYER_JOINED_MATCH = "player_joined_match"
    PLAYER_READY = "player_ready"

class ServerModes:
    MOVESETSELECT = "movesetselect"
    MATCH = "match"

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        
        self.nickname = self._server.generate_nickname()
        self.postion = PlayerPositions.NONE
        self.player_id = id(self)
    
    def Network(self, data):
        print("Server channel")
        print(data)
    
    def Network_join_match(self, data):
        player_position = self._server.add_player(self)
        
        if player_position == PlayerPositions.NONE:
            data = \
                {
                    DataKeys.ACTION : ClientActions.MATCH_FULL,
                    DataKeys.PLAYER_POSITION : player_position,
                    DataKeys.PLAYER_ID : self.player_id
                }
            
            self.Send(data)
        else:
            data = \
                {
                    DataKeys.ACTION : ClientActions.PLAYER_JOINED_MATCH,
                    DataKeys.PLAYER_POSITION : player_position,
                    DataKeys.PLAYER_ID : self.player_id,
                    DataKeys.NICKNAME : self.nickname
                }
            
            self._server.send_to_all(data)
    
    def Network_spectate_match(self, data):
        self._server.add_spectator(self)
    
    def Network_update_player_state(self, data):
        pass
    
    def Network_player_ready(self, data):
        
        player_position = self._server.get_player_position(self)
        self._server.set_player_position_ready(player_position, True)
        
        data = \
                {
                    DataKeys.ACTION : ClientActions.PLAYER_READY,
                    DataKeys.PLAYER_POSITION : player_position,
                    DataKeys.PLAYER_ID : self.player_id
                }
        
        self._server.send_to_all(data)
    
    def Network_set_game_mode(self, data):
        if self._server.client_is_player(self):
            server_mode = data[DataKeys.SERVER_MODE]
            
            self._server.mode = server_mode
            
            self._server.send_to_all(data)
    
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
                PlayerPositions.PLAYER2 : None
            }
        self.player_positions_ready = \
            {
                PlayerPositions.PLAYER1 : False,
                PlayerPositions.PLAYER2 : False
            }
        self.players = []
        self.spectators = []
        self.mode = ServerModes.MOVESETSELECT
        
        print 'server started!'
    
    def Connected(self, channel, addr):
        print 'new connection:', channel
        
        self.assign_id(channel)
        self.add_spectator(channel)
        self.sync_client_to_server(channel)
    
    def close(self):
        """remove all players and close the sever's socket"""
        for spectator in self.spectators:
            spectator.close()
        
        for player in self.players:
            player.close()
        
        Server.close(self)
    
    def sync_client_to_server(self, client):
        """send the client the current state of the server"""
        spectators = [spectator.player_id for spectator in self.spectators]
        
        player_positions = {}
        
        for position, player in self.player_positions.iteritems():
            if player == None:
                player_positions[position] = None
            else:
                player_positions[position] = player.player_id
        
        player_nicknames = {}
        
        for player in self.players:
            player_nicknames[player.player_id] = player.nickname
        
        for spectator in self.spectators:
            player_nicknames[spectator.player_id] = spectator.nickname
        
        data = \
            {
                DataKeys.ACTION : ClientActions.SYNC_TO_SERVER,
                DataKeys.SPECTATORS : spectators,
                DataKeys.PLAYER_POSITIONS : player_positions,
                DataKeys.PLAYER_NICKNAMES : player_nicknames,
                DataKeys.PLAYER_POSITIONS_READY : self.player_positions_ready,
                DataKeys.SERVER_MODE : self.mode
            }
        
        client.Send(data)
    
    def generate_nickname(self):
        """creates a player name and increments the number of the player name"""
        player_name = "stick" + str(self.player_name_count + 1)
        self.player_name_count += 1
        
        return player_name
    
    def get_player_position(self, player_to_find):
        """return the position of the player to find.  If the player to find has no
        position none is returned"""
        for player_position, player in self.player_positions.iteritems():
            if player == player_to_find:
                return player_position
    
    def set_player_position_ready(self, player_position, ready_indicator):
        self.player_positions_ready[player_position] = ready_indicator
    
    def assign_id(self, player):
        """sends a players server id to their client"""
        data = \
            {
                DataKeys.ACTION : ClientActions.GET_PLAYER_ID,
                DataKeys.PLAYER_ID : player.player_id
            }
        
        player.Send(data)
    
    def add_spectator(self, spectator):
        """Add a spectator to the server"""
        print("spectator joined " + spectator.nickname)
        self.spectators.append(spectator)
        
        for player_position, player in self.player_positions.iteritems():
            if player == spectator:
                self.player_positions[player_position] = None
                self.players.remove(spectator)
                
                break
        
        data = \
            {
                DataKeys.ACTION : ClientActions.SPECTATOR_JOINED,
                DataKeys.NICKNAME : spectator.nickname,
                DataKeys.PLAYER_ID : spectator.player_id
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
            self.spectators.remove(player)
            
            return PlayerPositions.PLAYER1
            
        elif player2 == None and not player == player1:
            self.player_positions[PlayerPositions.PLAYER2] = player
            self.players.append(player)
            self.spectators.remove(player)
            
            return PlayerPositions.PLAYER2
            
        elif player == player1:
            return PlayerPositions.PLAYER1
            
        elif player == player2:
            return PlayerPositions.PLAYER2
            
        else:
            return PlayerPositions.NONE
    
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
        
        data = \
            {
                DataKeys.ACTION : ClientActions.PLAYER_DISCONNECTED,
                DataKeys.PLAYER_ID : player.player_id,
                DataKeys.NICKNAME : player.nickname
            }
        
        self.send_to_all(data)
    
    def send_to_all(self, data):
        """send data to all connected players"""
        [player.Send(data) for player in self.players]
        [spectator.Send(data) for spectator in self.spectators]
    
    def client_is_player(self, client):
        return client in self.players

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
