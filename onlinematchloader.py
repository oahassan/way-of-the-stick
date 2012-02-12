import pygame
import gamestate
import button
import versusclient
import versusserver
import player
import onlineversusmode
import movesetdata
from versusmode import PlayerData
from functools import reduce
from enumerations import PlayerTypes, PlayerStates, PlayerPositions, PlayerDataKeys, PlayerSelectActions

LOADING_MATCH_TEXT = "Loading Match"

loading_match_label = None
loaded_indicator = False
load_match_progress_timer = 0
player_data = {
    PlayerPositions.PLAYER1 : PlayerData(
        PlayerPositions.PLAYER1,
        None,
        None,
        None,
        None,
        None
    ), PlayerPositions.PLAYER2 : PlayerData(
        PlayerPositions.PLAYER2,
        None,
        None,
        None,
        None,
        None
    )}

def set_color(data):
    global player_data
    
    player_data[data[PlayerDataKeys.PLAYER_POSITION]].color = data[PlayerDataKeys.COLOR]

def set_size(data):
    global player_data
    
    player_data[data[PlayerDataKeys.PLAYER_POSITION]].size = data[PlayerDataKeys.SIZE]

def set_difficulty(data):
    global player_data
    
    player_data[data[PlayerDataKeys.PLAYER_POSITION]].difficulty = data[PlayerDataKeys.DIFFICULTY]

def set_player_type(data):
    global player_data
    
    if gamestate.hosting:
        player_data[data[PlayerDataKeys.PLAYER_POSITION]].player_type = data[PlayerDataKeys.PLAYER_TYPE]
    else:
        player_data[data[PlayerDataKeys.PLAYER_POSITION]].player_type = PlayerTypes.REMOTE

def set_moveset(data):
    global player_data
    
    if (player_data[data[PlayerDataKeys.PLAYER_POSITION]].moveset == None
    or player_data[data[PlayerDataKeys.PLAYER_POSITION]].moveset.name != data[PlayerDataKeys.MOVESET_NAME]):
        player_data[data[PlayerDataKeys.PLAYER_POSITION]].moveset = movesetdata.get_moveset(
            data[PlayerDataKeys.MOVESET_NAME]
        )

def register_network_callbacks():
    versusclient.listener.register_callback(
        PlayerSelectActions.SET_COLOR,
        set_color
    )
    
    versusclient.listener.register_callback(
        PlayerSelectActions.SET_SIZE,
        set_size
    )
    
    versusclient.listener.register_callback(
        PlayerSelectActions.SET_DIFFICULTY,
        set_difficulty
    )
    
    versusclient.listener.register_callback(
        PlayerSelectActions.SET_PLAYER_TYPE,
        set_player_type
    )
    
    versusclient.listener.register_callback(
        PlayerSelectActions.SET_MOVESET,
        set_moveset
    )

def unregister_network_callbacks():
    versusclient.listener.clear_callback(PlayerSelectActions.SET_COLOR)
    versusclient.listener.clear_callback(PlayerSelectActions.SET_SIZE)
    versusclient.listener.clear_callback(PlayerSelectActions.SET_DIFFICULTY)
    versusclient.listener.clear_callback(PlayerSelectActions.SET_PLAYER_TYPE)
    versusclient.listener.clear_callback(PlayerSelectActions.SET_MOVESET)

def load():
    global loading_match_label
    global load_match_progress_timer
    global player_data
    
    loading_match_label = button.Label((0, 0), LOADING_MATCH_TEXT, (255,255,255),40)
    loading_match_label.set_position(get_layout_label_pos())
    
    load_match_progress_timer = 0
    
    if versusclient.local_player_is_in_match():
        onlineversusmode.init(player_data.values())
        
        versusclient.listener.send_all_movesets_loaded()

def unload():
    global loading_match_label
    global loaded_indicator
    
    loaded_indicator = False
    loading_match_label = None

def handle_events():
    global loaded_indicator
    global load_match_progress_timer
    
    if loaded_indicator == False:
        load()
        loaded_indicator = True
    
    loading_match_label.draw(gamestate.screen)
    
    load_match_progress_timer += gamestate.clock.get_time()
    
    if load_match_progress_timer > 3000:
        loading_match_label.set_text(loading_match_label.text + ".")
        load_match_progress_timer = 0
    
    if loading_match_label.text == LOADING_MATCH_TEXT + "....":
        loading_match_label.set_text(LOADING_MATCH_TEXT)
    
    if versusclient.listener.server_mode == versusserver.ServerModes.MATCH:
        
        unload()
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
    
    versusclient.get_network_messages()
    versusclient.listener.Pump()
    
    if gamestate.hosting:
        versusserver.server.Pump()

def get_layout_label_pos():
    """returns a position that centers the loading match label in the middle of the
    screen"""
    global loading_match_label
    
    x_pos = (gamestate._WIDTH / 2) - (loading_match_label.width / 2)
    y_pos = (gamestate._HEIGHT / 2) - (loading_match_label.height / 2)
    
    return (x_pos, y_pos)
