import urllib
import socket
import struct
import datetime

from functools import reduce
from wotsprot.udpserver import Server
from wotsprot.channel import Channel
from wotsprot import protocol
from enumerations import PlayerPositions, PlayerDataKeys, PlayerTypes, Difficulties, PlayerSelectActions, ServerDiscovery
import versusmode

class DataKeys:
    ACTION = "action"
    NICKNAME = "nickname"
    PLAYER_NICKNAMES = "player nicknames"
    PLAYER_POSITIONS = "player positions"
    SPECTATORS = "spectators"
    PLAYERS = "players"
    PLAYER_POSITION = "player position"
    PLAYER_ID = "player_id"
    PLAYER_POSITIONS_READY = "player positions ready"
    PLAYER_READY_INDICATOR = "player ready indicator"
    SERVER_MODE = "server mode"
    PLAYER_STATE = "player state"
    POINT_POSITIONS = "point positions"
    MESSAGE = "message"
    MOVESET_NAME = 14
    PLAYER_MOVESETS = "player movesets"
    SIMULATION_STATE = "simulation state"
    COLOR = 17
    DIFFICULTY = 18
    PLAYER_TYPE = 19
    SIZE = 20
    DUMMIES = 21
    

class ClientActions:
    SPECTATOR_JOINED = "spectator_joined"
    GET_PLAYER_ID = "get_player_id"
    GET_PLAYER_POSITION = "get_player_position"
    SYNC_TO_SERVER = "sync_to_server"
    PLAYER_DISCONNECTED = "player_disconnected"
    MATCH_FULL = "match_full"
    PLAYER_JOINED_MATCH = "player_joined_match"
    PLAYER_READY = "player_ready"
    SET_GAME_MODE = "set_game_mode"
    UPDATE_SIMULATION_STATE = "update_simulation_state"
    UPDATE_INPUT_STATE = "update_input_state"
    RECEIVE_CHAT_MESSAGE = "receive_chat_message"
    ADD_DUMMY = "add_dummy"
    ACK_SERVER = "acknowledge_server"

class ServerModes:
    MOVESET_SELECT = "moveset select"
    LOADING_MATCH_DATA = "loading match data"
    MATCH = "match"

class ChannelTypes:
    DUMMY = 0
    CLIENT = 1

class LanDiscoveryBroadcast(socket.socket):

    def __init__(self, address, name):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set Time-to-live (optional)
        ttl_bin = struct.pack('@i', 1)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
        self.last_update_timestamp = datetime.datetime.now()
        self.address = address
        self.name = name
    
    def Send(self):
        payload = protocol.write_broadcast_header(0) + protocol.encode(
            {
                DataKeys.ACTION : ClientActions.ACK_SERVER,
                ServerDiscovery.ADDRESS : self.address,
                ServerDiscovery.NAME : self.name
            }
        )
        
        self.sendto(payload, (protocol.SERVER_DISCOVERY_GROUP, protocol.SERVER_DISCOVERY_PORT))
        self.last_update_timestamp = datetime.datetime.now()

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        
        self.channel_type = ChannelTypes.CLIENT
        self.nickname = self._server.generate_nickname()
        self.postion = PlayerPositions.NONE
        self.player_id = id(self)
        self.size = None
        self.moveset = None
        self.player_type = None
        self.difficulty = None
        self.color = None
    
    def Network(self, data):
        #print("Server channel")
        #print(data)
        pass
    
    def Network_send_chat_message(self, data):
        
        data[DataKeys.ACTION] = ClientActions.RECEIVE_CHAT_MESSAGE
        self._server.send_to_all(data)
    
    def Network_join_match(self, data):
        player_position = self._server.add_player(self)
        
        if player_position == PlayerPositions.NONE:
            data = {
                DataKeys.ACTION : ClientActions.MATCH_FULL,
                DataKeys.PLAYER_POSITION : player_position,
                DataKeys.PLAYER_ID : self.player_id
            }
            
            self.Send(data)
        else:
            data = {
                DataKeys.ACTION : ClientActions.PLAYER_JOINED_MATCH,
                DataKeys.PLAYER_POSITION : player_position,
                DataKeys.PLAYER_ID : self.player_id,
                DataKeys.NICKNAME : self.nickname
            }
            
            self._server.send_to_all(data)
    
    def Network_spectate_match(self, data):
        self._server.add_spectator(self)
    
    def Network_send_initial_player_state(self, data):
        """send data about the starting state of player to all clients"""
        
        send_data = {DataKeys.ACTION : ClientActions.RECEIVE_PLAYER_INITIAL_STATE}
        
        for key, value in data.iteritems():
            if key != DataKeys.ACTION:
                send_data[key] = value
        
        self._server.send_to_all(send_data)
    
    def Network_all_movesets_loaded(self, data):
        """indicate on server that all remote player states have been received"""
        
        player_position = self._server.get_player_position(self)
        
        if player_position != None:
            self._server.set_all_movesets_loaded_indicator(player_position, True)
        
        #TODO - add timeout not necessarily here
        if self._server.all_movesets_loaded():
            
            self._server.mode = ServerModes.MATCH
            
            data = {
                DataKeys.ACTION : ClientActions.SET_GAME_MODE,
                DataKeys.SERVER_MODE : ServerModes.MATCH
            }
            
            self._server.send_to_all(data)
    
    def Network_start_match(self, data):
        self._server.mode = ServerModes.MATCH
        
        self._server.send_to_all(data)
        
    def Network_end_match(self, data):
        self._server.mode = ServerModes.MOVESET_SELECT
        
        for player_position in self._server.player_positions.keys():
            self._server.set_all_movesets_loaded_indicator(player_position, False)
        
        self._server.send_to_all(data)
    
    def Network_update_simulation_state(self, data):
        self._server.send_to_all(data)
    
    def Network_player_ready(self, data):
        
        player_position = self._server.get_player_position(self)
        self._server.set_player_position_ready(player_position, True)
        
        data = {
            DataKeys.ACTION : ClientActions.PLAYER_READY,
            DataKeys.PLAYER_POSITION : player_position,
            DataKeys.PLAYER_ID : self.player_id,
            DataKeys.PLAYER_READY_INDICATOR : True
        }
        
        self._server.send_to_all(data)
    
    def Network_set_moveset(self, data):
        self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].moveset = data[PlayerDataKeys.MOVESET_NAME]
        
        self._server.send_to_all(data)
    
    def Network_get_moveset(self, data):
        data[DataKeys.ACTION] = PlayerSelectActions.SET_MOVESET
        data[PlayerDataKeys.MOVESET_NAME] = self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].moveset
        
        self.Send(data)
    
    def Network_set_color(self, data):
        self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].color = data[PlayerDataKeys.COLOR]
        
        self._server.send_to_all(data)
    
    def Network_get_color(self, data):
        data[DataKeys.ACTION] = PlayerSelectActions.SET_COLOR
        data[PlayerDataKeys.COLOR] = self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].color
        
        self.Send(data)
    
    def Network_set_difficulty(self, data):
        self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].difficulty = data[PlayerDataKeys.DIFFICULTY]
        
        self._server.send_to_all(data)
    
    def Network_get_difficulty(self, data):
        data[DataKeys.ACTION] = PlayerSelectActions.SET_DIFFICULTY
        data[PlayerDataKeys.DIFFICULTY] = self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].difficulty
        
        self.Send(data)
    
    def Network_set_player_type(self, data):
        self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].player_type = data[PlayerDataKeys.PLAYER_TYPE]
        
        self._server.send_to_all(data)
    
    def Network_get_player_type(self, data):
        data[DataKeys.ACTION] = PlayerSelectActions.SET_PLAYER_TYPE
        data[PlayerDataKeys.PLAYER_TYPE] = self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].player_type
        
        self.Send(data)
    
    def Network_set_size(self, data):
        self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].size = data[PlayerDataKeys.SIZE]
        
        self._server.send_to_all(data)
    
    def Network_get_size(self, data):
        data[DataKeys.ACTION] = PlayerSelectActions.SET_SIZE
        data[PlayerDataKeys.SIZE] = self._server.player_data[
            data[PlayerDataKeys.PLAYER_POSITION]
        ].size
        
        self.Send(data)
    
    def Network_update_input_state(self, data):
        self._server.send_to_all(data)
    
    def Network_set_game_mode(self, data):
        if self._server.client_is_player(self) or self._server.dummies_only():
            server_mode = data[DataKeys.SERVER_MODE]
            
            self._server.mode = server_mode
            
            self._server.send_to_all(data)
    
    def Close(self):
        print("deleting player: " + self.nickname)
        self._server.del_player(self)

class DummyChannel():
    def __init__(self, player_data, server):
        self._server = server
        self.channel_type = ChannelTypes.DUMMY
        self.nickname = self._server.generate_nickname()
        self.position = player_data.player_position
        self.player_id = id(self)
        self.size = player_data.size
        self.moveset = player_data.moveset
        self.player_type = player_data.player_type
        self.difficulty = player_data.difficulty
        self.color = player_data.color

class WotsServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.player_name_count = 0
        self.player_positions_ready = {
            PlayerPositions.PLAYER1 : False,
            PlayerPositions.PLAYER2 : False
        }
        self.player_movesets = {
            PlayerPositions.PLAYER1 : "one attack", 
            PlayerPositions.PLAYER2 : "one attack"
        }
        self.player_data = {
            PlayerPositions.PLAYER1 : versusmode.PlayerData(
                PlayerPositions.PLAYER1,
                PlayerTypes.BOT,
                "one attack",
                5,
                (255,0,0),
                Difficulties.CHALLENGE
            ), 
            PlayerPositions.PLAYER2 : versusmode.PlayerData(
                PlayerPositions.PLAYER2,
                PlayerTypes.BOT,
                "one attack",
                5,
                (0,0,255),
                Difficulties.CHALLENGE
            )
        }
        self.dummies = {
            PlayerPositions.PLAYER1 : DummyChannel(self.player_data[PlayerPositions.PLAYER1], self), 
            PlayerPositions.PLAYER2 : DummyChannel(self.player_data[PlayerPositions.PLAYER2], self)
        }
        self.player_positions = {
            PlayerPositions.PLAYER1 : self.dummies[PlayerPositions.PLAYER1], 
            PlayerPositions.PLAYER2 : self.dummies[PlayerPositions.PLAYER2]
        }
        
        #indicates that point position data has been received by players in the match
        #this ensures that models are ready to be drawn at each client.
        self.all_movesets_loaded_indicators = {
            PlayerPositions.PLAYER1 : False, 
            PlayerPositions.PLAYER2 : False
        }
        
        self.players = []
        self.spectators = []
        self.mode = ServerModes.MOVESET_SELECT
        
        print 'server started!'
    
    def Connected(self, channel, addr):
        print 'new connection:', channel
        
        self.assign_id(channel)
        self.add_spectator(channel)
        self.sync_client_to_server(channel)
    
    def dummies_only(self):
        return_indicator = True
        
        for dummy in self.dummies.values():
            return_indicator = return_indicator and dummy in self.player_positions.values()
        
        return return_indicator
    
    def close(self):
        """remove all players and close the sever's socket"""
        for spectator in self.spectators:
            spectator.close()
        
        for player in self.players:
            player.close()
        
        Server.close(self)
    
    def set_all_movesets_loaded_indicator(self, player_position, indicator):
        self.all_movesets_loaded_indicators[player_position] = indicator
    
    def all_movesets_loaded(self):
        
        return reduce(
            lambda x, y : x and y,
            [
                all_movesets_loaded_indicator 
                for all_movesets_loaded_indicator 
                in self.all_movesets_loaded_indicators.values()
            ]
        )
    
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
        
        data = {
            DataKeys.ACTION : ClientActions.SYNC_TO_SERVER,
            DataKeys.SPECTATORS : spectators,
            DataKeys.PLAYER_POSITIONS : player_positions,
            DataKeys.PLAYER_NICKNAMES : player_nicknames,
            DataKeys.PLAYER_POSITIONS_READY : self.player_positions_ready,
            DataKeys.PLAYER_MOVESETS : self.player_movesets,
            DataKeys.SERVER_MODE : self.mode,
            DataKeys.DUMMIES : { 
                PlayerPositions.PLAYER1 : self.dummies[PlayerPositions.PLAYER1].player_id,
                PlayerPositions.PLAYER2 : self.dummies[PlayerPositions.PLAYER2].player_id
            }
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
        
        data = {
            DataKeys.ACTION : ClientActions.SPECTATOR_JOINED,
            DataKeys.NICKNAME : spectator.nickname,
            DataKeys.PLAYER_ID : spectator.player_id
        }
        
        self.send_to_all(data)
    
    def add_dummy(self, player_position):
        self.player_positions[player_position] = self.dummies[player_position]
        
        data = {
            DataKeys.ACTION : ClientActions.ADD_DUMMY,
            DataKeys.PLAYER_POSITION : player_position,
            DataKeys.PLAYER_ID : self.dummies[player_position].id
        }
        
        self.send_to_all(data)
    
    def add_player(self, player):
        """Assign the player to a position and return its position.  If all positions are
        taken return the NONE position."""
        
        player1 = self.player_positions[PlayerPositions.PLAYER1]
        player2 = self.player_positions[PlayerPositions.PLAYER2]
        
        if player1.channel_type == ChannelTypes.DUMMY and not player == player2:
            self.player_positions[PlayerPositions.PLAYER1] = player
            self.players.append(player)
            self.spectators.remove(player)
            
            return PlayerPositions.PLAYER1
            
        elif player2.channel_type == ChannelTypes.DUMMY and not player == player1:
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
            self.player_positions_ready[PlayerPositions.PLAYER1] = False
            self.all_movesets_loaded_indicators[PlayerPositions.PLAYER1] = False
            self.add_dummy(PlayerPositions.PLAYER1)
        elif player == self.player_positions[PlayerPositions.PLAYER2]:
            self.player_positions[PlayerPositions.PLAYER2] = None
            self.player_positions_ready[PlayerPositions.PLAYER2] = False
            self.all_movesets_loaded_indicators[PlayerPositions.PLAYER2] = False
            self.add_dummy(PlayerPositions.PLAYER2)
        
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
broadcast = None

DFLT_PORT = 45000

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
    
    server = WotsServer(address=(get_public_ip_address(), int(DFLT_PORT)))

def start_lan_server():
    global server
    global broadcast
    
    address = get_lan_ip_address()
    server = WotsServer(address=(address, int(DFLT_PORT)))
    broadcast = LanDiscoveryBroadcast(address, "LAN Server")

def pump():
    if server != None:
        server.Pump()
    
    if broadcast != None:
        if (datetime.datetime.now() - broadcast.last_update_timestamp) > protocol.BROADCAST_INTERVAL:
            broadcast.Send()

def server_ready():
    if server:
        return True
    else:
        return False
