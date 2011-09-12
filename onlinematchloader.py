import pygame
import gamestate
import button
import versusclient
import versusserver
import onlineversusmovesetselect
import player
import onlineversusmode
import movesetdata
from functools import reduce
from enumerations import PlayerTypes, PlayerStates

LOADING_MATCH_TEXT = "Loading Match"

loading_match_label = None
loaded_indicator = False
load_match_progress_timer = 0

def load():
    global loading_match_label
    global load_match_progress_timer
    
    loading_match_label = button.Label((0, 0), LOADING_MATCH_TEXT, (255,255,255),40)
    loading_match_label.set_position(get_layout_label_pos())
    
    load_match_progress_timer = 0
    
    if versusclient.local_player_is_in_match():
        setup_local_player()

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
    
    handle_moveset_changes()
    
    if versusclient.listener.server_mode == versusserver.ServerModes.MATCH:
        
        unload()
        onlineversusmode.init()
        onlineversusmode.local_state.init_player_sounds()
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
    
    versusclient.get_network_messages()
    versusclient.listener.Pump()
    
    if gamestate.hosting:
        versusserver.server.Pump()

def handle_moveset_changes():
    for player_position, moveset_name in versusclient.listener.player_movesets.iteritems():
        if moveset_name != None and onlineversusmode.local_state.player_dictionary[player_position] == None:
            setup_remote_player(player_position, moveset_name)
            
            if versusclient.local_player_is_in_match() and all_movesets_loaded():
                versusclient.listener.send_all_movesets_loaded()

def all_movesets_loaded():
    return reduce(
        lambda x, y : x and y,
        [
            loaded_player != None
            for loaded_player
            in onlineversusmode.local_state.player_dictionary.values()
        ]
    )

def setup_remote_player(player_position, moveset_name):
    """creates a remote player in the online versus mode module"""
    
    remote_player = onlineversusmode.NetworkPlayer((0,0), player_position)
    remote_player.load_moveset(movesetdata.get_moveset(moveset_name))
    set_player_initial_state(player_position, remote_player)
    
    onlineversusmode.set_player(player_position, remote_player)

def setup_local_player():
    """creates a local player in the online versus mode module"""
    
    local_player_position = versusclient.get_local_player_position()
    
    local_player_ui = \
        onlineversusmovesetselect.player_status_ui_dictionary[local_player_position]
    
    local_player_type = local_player_ui.get_player_type()
    
    for player_position in onlineversusmode.local_state.player_type_dictionary.keys():
        onlineversusmode.local_state.player_type_dictionary[player_position] = PlayerTypes.HUMAN
    
    local_player = onlineversusmode.NetworkPlayer((0,0), local_player_position)
    
    moveset = local_player_ui.get_player_moveset()
    local_player.load_moveset(moveset)
    
    #Calling set initial state first makes it so that the player doesn't turn around in
    #the first frame if it's supposed to start facing left.
    set_player_initial_state(local_player_position, local_player)
    
    onlineversusmode.set_player(local_player_position, local_player)
    versusclient.listener.set_moveset(moveset.name)

def set_player_initial_state(player_position, player):
    player.init_state()
    player.actions[PlayerStates.STANDING].set_player_state(player)
    player.color = get_player_color(player_position)
    player.outline_color = player.color
    
    player.direction = get_player_model_direction(player_position)
    
    player.model.move_model(get_player_model_position(player_position))

def get_player_model_position(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return ((400, 967))
        
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return ((1200, 967))

def get_player_model_direction(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return player.PlayerStates.FACING_RIGHT
        
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return player.PlayerStates.FACING_LEFT

def get_player_color(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return (255,0,0)
        
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return (0,255,0)

def get_layout_label_pos():
    """returns a position that centers the loading match label in the middle of the
    screen"""
    global loading_match_label
    
    x_pos = (gamestate._WIDTH / 2) - (loading_match_label.width / 2)
    y_pos = (gamestate._HEIGHT / 2) - (loading_match_label.height / 2)
    
    return (x_pos, y_pos)
