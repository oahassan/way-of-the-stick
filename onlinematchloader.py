import pygame
import gamestate
import button
import versusclient
import versusserver
import onlineversusmovesetselect
import player
import onlineversusmode

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
    
    setup_versusmode()

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
    
    if loading_match_label.text == LOADING_MATCH_TEXT + "....":
        loading_match_label.set_text(LOADING_MATCH_TEXT)
    
    if versusclient.listener.server_mode == versusserver.ServerModes.MATCH:
        unload()
        onlineversusmode.init()
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
    
    versusclient.listener.Pump()
    versusclient.get_network_messages()
    
    if gamestate.hosting:
        versusserver.server.Pump()

def setup_versusmode():
    if versusclient.local_player_is_in_match():
        setup_local_player()
        
    for player_position in versusclient.get_remote_player_positions():
        setup_remote_player(player_position)
    
    if (versusclient.local_player_is_in_match() and
    (versusclient.local_player_match_data_loaded() == False)):
        local_player_state_dictionary = \
            onlineversusmode.get_local_player_state_dictionary()
        
        local_player_position = versusclient.get_local_player_position()
        
        versusclient.listener.send_player_initial_state(
            local_player_state_dictionary, 
            local_player_position
        )

def setup_remote_player(player_position):
    """creates a remote player in the online versus mode module"""
    
    remote_player = onlineversusmode.RemotePlayer((0,0), player_position)
    
    set_player_initial_state(player_position, remote_player)
    
    onlineversusmode.set_player(player_position, remote_player)

def setup_local_player():
    """creates a local player in the online versus mode module"""
    
    local_player_position = versusclient.get_local_player_position()
    
    local_player_ui = \
        onlineversusmovesetselect.player_status_ui_dictionary[local_player_position]
    
    local_player_type = local_player_ui.get_player_type()
    
    local_player = None
    
    if local_player_type == player.PlayerTypes.HUMAN:
        local_player = onlineversusmode.LocalHumanPlayer((0,0), local_player_position)
        
    elif local_player_type == player.PlayerTypes.BOT:
        local_player = onlineversusmode.LocalBot((0,0), local_player_position)
    
    #Calling set initial state first makes it so that the player doesn't turn around in
    #the first frame if it's supposed to start facing left.
    set_player_initial_state(local_player_position, local_player)
    
    local_player.load_moveset(local_player_ui.get_player_moveset())
    
    onlineversusmode.set_player(local_player_position, local_player)

def set_player_initial_state(player_position, player):
    player.init_state()
    
    player.color = get_player_color(player_position)
    player.outline_color = player.color
    
    player.direction = get_player_model_direction(player_position)
    
    player.model.move_model(get_player_model_position(player_position))

def get_player_model_position(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return ((200, 367))
        
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return ((600, 367))

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
