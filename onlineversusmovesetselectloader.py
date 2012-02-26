import versusclient
import versusserver
import onlineversusmovesetselect
import onlinematchloader
import wotsuievents
import gamestate
import splash
import functools

from enumerations import PlayerPositions, PlayerDataKeys, PlayerSelectActions

class OnlineMovesetSelectLoader():
    def __init__(self):
        self.loaded_player_data = {
            PlayerPositions.PLAYER1 : {
                PlayerDataKeys.COLOR : False,
                PlayerDataKeys.SIZE : False,
                PlayerDataKeys.DIFFICULTY : False,
                PlayerDataKeys.PLAYER_TYPE : False,
                PlayerDataKeys.MOVESET_NAME : False
            },
            PlayerPositions.PLAYER2 : {
                PlayerDataKeys.COLOR : False,
                PlayerDataKeys.SIZE : False,
                PlayerDataKeys.DIFFICULTY : False,
                PlayerDataKeys.PLAYER_TYPE : False,
                PlayerDataKeys.MOVESET_NAME : False
            }
        }
        self.data_types = [
            PlayerDataKeys.COLOR, 
            PlayerDataKeys.SIZE, 
            PlayerDataKeys.DIFFICULTY, 
            PlayerDataKeys.PLAYER_TYPE, 
            PlayerDataKeys.MOVESET_NAME
        ]
        self.player_positions = [
            PlayerPositions.PLAYER1,
            PlayerPositions.PLAYER2
        ]
        self.timeout = 3000
        self.timer = 0
        self.retry_count = 0
        self.data_index = 0
        self.player_index = 0
    
    def update_data_requests(self):
        if self.all_data_loaded():
            return
        
        if self.player_data_loaded(self.player_positions[self.player_index]):
            self.player_index += 1
            self.data_index = 0
            self.timer = 0
            self.retry_count = 0
        
        player_position = self.player_positions[self.player_index]
        
        if self.loaded_player_data[player_position][self.data_types[self.data_index]]:
            self.data_index += 1
            self.retry_count = 0
            self.timer = 0
            
            if self.data_index < len(self.data_types):
                self.request_data(self.data_types[self.data_index], player_position)
            
        elif self.timer == 0:
            self.request_data(
                self.data_types[self.data_index], 
                self.player_positions[self.player_index]
            )
        elif self.timer >= self.timeout:
            self.request_data(
                self.data_types[self.data_index], 
                self.player_positions[self.player_index]
            )
            self.retry_count += 1
            self.timer = 0
        
        self.timer += gamestate.time_passed
    
    def request_data(self, data_type, player_position):
        if data_type == PlayerDataKeys.COLOR:
            versusclient.listener.get_color(player_position)
            
        elif data_type == PlayerDataKeys.SIZE:
            versusclient.listener.get_size(player_position)
            
        elif data_type == PlayerDataKeys.DIFFICULTY:
            versusclient.listener.get_difficulty(player_position)
        
        elif data_type == PlayerDataKeys.PLAYER_TYPE:
            versusclient.listener.get_player_type(player_position)
        
        elif data_type == PlayerDataKeys.MOVESET_NAME:
            versusclient.listener.get_moveset(player_position)
    
    def player_data_loaded(self, player_position):
        return reduce(
            lambda x,y: x and y, 
            self.loaded_player_data[player_position].values()
        )
    
    def all_data_loaded(self):
        return reduce(
            lambda x,y: x and y, 
            [reduce(lambda x,y: x and y, data.values()) 
            for data in self.loaded_player_data.values()]
        )
    
    def set_color(self, data):
        
        self.loaded_player_data[data[PlayerDataKeys.PLAYER_POSITION]][PlayerDataKeys.COLOR] = True

    def set_size(self, data):
        
        self.loaded_player_data[data[PlayerDataKeys.PLAYER_POSITION]][PlayerDataKeys.SIZE] = True

    def set_difficulty(self, data):
        
        self.loaded_player_data[data[PlayerDataKeys.PLAYER_POSITION]][PlayerDataKeys.DIFFICULTY] = True

    def set_player_type(self, data):
        
        self.loaded_player_data[data[PlayerDataKeys.PLAYER_POSITION]][PlayerDataKeys.PLAYER_TYPE] = True

    def set_moveset(self, data):
        
        self.loaded_player_data[data[PlayerDataKeys.PLAYER_POSITION]][PlayerDataKeys.MOVESET_NAME] = True

    def register_network_callbacks(self):
        versusclient.listener.register_callback(
            PlayerSelectActions.SET_COLOR,
            self.set_color
        )
        
        versusclient.listener.register_callback(
            PlayerSelectActions.SET_SIZE,
            self.set_size
        )
        
        versusclient.listener.register_callback(
            PlayerSelectActions.SET_DIFFICULTY,
            self.set_difficulty
        )
        
        versusclient.listener.register_callback(
            PlayerSelectActions.SET_PLAYER_TYPE,
            self.set_player_type
        )
        
        versusclient.listener.register_callback(
            PlayerSelectActions.SET_MOVESET,
            self.set_moveset
        )
    
    def unregister_network_callbacks(self):
        versusclient.listener.unregister_callback(
            PlayerSelectActions.SET_COLOR,
            self.set_color
        )
        
        versusclient.listener.unregister_callback(
            PlayerSelectActions.SET_SIZE,
            self.set_size
        )
        
        versusclient.listener.unregister_callback(
            PlayerSelectActions.SET_DIFFICULTY,
            self.set_difficulty
        )
        
        versusclient.listener.unregister_callback(
            PlayerSelectActions.SET_PLAYER_TYPE,
            self.set_player_type
        )
        
        versusclient.listener.unregister_callback(
            PlayerSelectActions.SET_MOVESET,
            self.set_moveset
        )

loaded = False
moveset_select_loader = OnlineMovesetSelectLoader()

def load(): 
    global moveset_select_loader
    global loaded
    
    splash.draw_loading_splash()
    
    moveset_select_loader.loaded_player_data = {
        PlayerPositions.PLAYER1 : {
            PlayerDataKeys.COLOR : False,
            PlayerDataKeys.SIZE : False,
            PlayerDataKeys.DIFFICULTY : False,
            PlayerDataKeys.PLAYER_TYPE : False,
            PlayerDataKeys.MOVESET_NAME : False
        },
        PlayerPositions.PLAYER2 : {
            PlayerDataKeys.COLOR : False,
            PlayerDataKeys.SIZE : False,
            PlayerDataKeys.DIFFICULTY : False,
            PlayerDataKeys.PLAYER_TYPE : False,
            PlayerDataKeys.MOVESET_NAME : False
        }
    }
    
    #TODO - Make this passed in
    server_address = versusserver.get_lan_ip_address()
    
    if gamestate.hosting:
        versusserver.start_lan_server()
        server_address = versusserver.get_lan_ip_address()
    
    versusclient.connect_to_host(server_address)
    
    loaded = True

def unload():
    global moveset_select_loader
    global loaded
    
    moveset_select_loader.unregister_network_callbacks()
    moveset_select_loader = None
    
    gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
    loaded = False

def handle_events():
    global loaded
    global moveset_select_loader
    
    if loaded == False:
        load()
    
    versusclient.get_network_messages()
    versusclient.listener.Pump()
    
    if gamestate.hosting:
        versusserver.server.Pump()
    
    if versusclient.connected():
        if onlineversusmovesetselect.loaded == False:
            onlineversusmovesetselect.load()
            onlinematchloader.register_network_callbacks()
            moveset_select_loader.register_network_callbacks()
        
        if moveset_select_loader.all_data_loaded():
            unload()
        else:
            moveset_select_loader.update_data_requests()
