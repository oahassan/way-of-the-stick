import pygame

import wotsuievents
import movesetdata
import gamestate
import versusserver
import versusclient
import onlinematchloader

import button
from onlineversusmovesetselectui import LocalPlayerSetupContainer, RemotePlayerStateLabel, ConnectingAlertBox
import movesetselectui
import wotsuicontainers

import player
import humanplayer
import aiplayer

from enumerations import PlayerSelectActions, PlayerDataKeys

loaded = False
exit_button = None
start_match_label = None
player_type_select = None
player_moveset_select = None
remote_player_state = None
join_match_button = None
local_player_container_created = False
assigned_positions = None
spectate_button = None
local_player_position = None

player_status_ui_dictionary = {
    versusserver.PlayerPositions.PLAYER1 : None,
    versusserver.PlayerPositions.PLAYER2 : None
}

def get_playable_movesets():
    movesets = movesetdata.get_movesets()
    playable_movesets = [moveset for moveset in movesets if moveset.is_complete()]
    
    return playable_movesets

def load():
    global loaded
    global exit_button
    global start_match_label
    global player_status_ui_dictionary
    global join_match_button
    global assigned_positions
    global spectate_button
    
    exit_button = button.ExitButton()
    loaded = True
    player_status_ui_dictionary = {
        versusserver.PlayerPositions.PLAYER1 : None,
        versusserver.PlayerPositions.PLAYER2 : None
    }
    start_match_label = movesetselectui.MovesetActionLabel((300, 550), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    assigned_positions = []
    
    init_player_status_ui_dictionary()
    
    join_match_button = button.TextButton("Join Match")
    join_match_button.set_position((360, 50))
    join_match_button.inactivate()
    
    spectate_button = button.TextButton("Spectate")
    spectate_button.set_position((600, 50))
    spectate_button.inactivate()
    
    register_network_callbacks()

def set_color(data):
    global player_status_ui_dictionary
    
    player_position = data[PlayerDataKeys.PLAYER_POSITION]
    player_ui = player_status_ui_dictionary[player_position]
    player_ui.player_color_select.set_color(data[PlayerDataKeys.COLOR])

def set_size(data):
    global player_status_ui_dictionary
    
    player_position = data[PlayerDataKeys.PLAYER_POSITION]
    player_ui = player_status_ui_dictionary[player_position]
    player_ui.player_stats_widget.set_size(data[PlayerDataKeys.SIZE])

def set_difficulty(data):
    global player_status_ui_dictionary
    
    player_position = data[PlayerDataKeys.PLAYER_POSITION]
    player_ui = player_status_ui_dictionary[player_position]
    player_ui.player_difficulty_select.set_selected_button(data[PlayerDataKeys.DIFFICULTY])

def set_player_type(data):
    global player_status_ui_dictionary
    
    player_position = data[PlayerDataKeys.PLAYER_POSITION]
    player_ui = player_status_ui_dictionary[player_position]
    player_ui.player_type_select.set_selected_button(data[PlayerDataKeys.PLAYER_TYPE])

def set_moveset(data):
    global player_status_ui_dictionary
    
    player_position = data[PlayerDataKeys.PLAYER_POSITION]
    player_ui = player_status_ui_dictionary[player_position]
    player_ui.moveset_select.set_moveset_by_name(data[PlayerDataKeys.MOVESET_NAME])

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
    versusclient.listener.unregister_callback(
        PlayerSelectActions.SET_COLOR,
        set_color
    )
    
    versusclient.listener.unregister_callback(
        PlayerSelectActions.SET_SIZE,
        set_size
    )
    
    versusclient.listener.unregister_callback(
        PlayerSelectActions.SET_DIFFICULTY,
        set_difficulty
    )
    
    versusclient.listener.unregister_callback(
        PlayerSelectActions.SET_PLAYER_TYPE,
        set_player_type
    )
    
    versusclient.listener.unregister_callback(
        PlayerSelectActions.SET_MOVESET,
        set_moveset
    )

def unload():
    global loaded
    global exit_button
    global start_match_label
    global ip_address_input
    global player_status_ui_dictionary
    global join_match_button
    global assigned_positions
    global spectate_button
    global local_player_position
    global local_player_container_created
    
    exit_button = None
    loaded = False
    start_match_label = None
    network_message_label = None
    join_match_button = None
    assigned_positions = None
    spectate_button = None
    player_status_ui_dictionary = None
    local_player_position = None
    local_player_container_created = False
    
    if versusclient.connected():
        unregister_network_callbacks()
        
        #clean up any remaining messages to the client
        versusclient.get_network_messages()
        versusclient.listener.Pump()
        
        versusclient.listener.close()
        versusclient.unload()
        print("listener closed")
    
    if gamestate.hosting:
        #clean up any remaining messages to the server
        versusserver.server.Pump()
        
        versusserver.server.close()
        versusserver.server = None
        print("server closed")
        
        gamestate.hosting = False

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global player_status_ui_dictionary
    global join_match_button
    global local_player_container_created
    global local_player_position
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        if start_match_label.active:
            if start_match_label.contains(wotsuievents.mouse_pos):
                start_match_label.handle_selected()
        
        if join_match_button.active:
            if join_match_button.contains(wotsuievents.mouse_pos):
                join_match_button.handle_selected()
        
        if spectate_button.active:
            if spectate_button.contains(wotsuievents.mouse_pos):
                spectate_button.handle_selected()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.ONLINEMENUPAGE
                unload()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                start_match_label.handle_deselected()
                versusclient.listener.load_match_data()
        
        #TODO - inactivate join if selected and same for spectate
        elif join_match_button.selected:
            if join_match_button.contains(wotsuievents.mouse_pos):
                versusclient.listener.join_match()
                join_match_button.handle_deselected()
                join_match_button.inactivate()
                
                spectate_button.activate()
        
        elif spectate_button.selected:
            if spectate_button.contains(wotsuievents.mouse_pos):
                versusclient.listener.spectate_match()
                spectate_button.handle_deselected()
                spectate_button.inactivate()
                join_match_button.activate()
    
    if loaded:
        
        if versusclient.dummies_only() and start_match_label.active == False:
            start_match_label.activate()
            
        
        if local_player_container_created:
            players_ready = True
            
            local_player_position = versusclient.get_local_player_position()
            
            if player_status_ui_dictionary[local_player_position].player_ready() and \
            not versusclient.listener.player_positions_ready_dictionary[local_player_position]:
                
                versusclient.listener.player_ready()
            
            for player_status_ui in player_status_ui_dictionary.values():
                if hasattr(player_status_ui, "player_ready"):
                    players_ready = (getattr(player_status_ui, "player_ready")() and players_ready)
                else:
                    players_ready = False
            
            if players_ready:
                if start_match_label.active == False:
                    start_match_label.activate()
            else:
                if start_match_label.active:
                    start_match_label.inactivate()
        
        for player_status_ui in player_status_ui_dictionary.values():
            player_status_ui.handle_events()
            player_status_ui.draw(gamestate.screen)
        
        join_match_button.draw(gamestate.screen)
        exit_button.draw(gamestate.screen)
        start_match_label.draw(gamestate.screen)
        spectate_button.draw(gamestate.screen)
        
        #Network Dependent Event Handling
        if (versusclient.listener.connection_status == 
        versusclient.ConnectionStatus.DISCONNECTED):
            
            unload()
            gamestate.mode = gamestate.Modes.ONLINEMENUPAGE
        
        if versusclient.connected() or gamestate.hosting:
            if not versusclient.local_player_is_in_match():
                if not join_match_button.active:
                    join_match_button.activate()
                
                if spectate_button.active:
                    spectate_button.inactivate()
                
            else:
                
                if not spectate_button.active:
                    spectate_button.activate()
                
                if join_match_button.active:
                    join_match_button.inactivate()
            
            update_player_data()
            
            if (versusclient.listener.server_mode == 
            versusserver.ServerModes.LOADING_MATCH_DATA) or \
            (versusclient.listener.server_mode == versusserver.ServerModes.MATCH):
                gamestate.mode = gamestate.Modes.ONLINEMATCHLOADER
            
            versusclient.get_network_messages()
            versusclient.listener.Pump() 
            
            if gamestate.hosting:
                versusserver.server.Pump()

def update_player_data():
    global player_status_ui_dictionary
    
    for player_position in player_status_ui_dictionary:
        if (player_position == versusclient.get_local_player_position() or
        (versusclient.is_dummy(player_position) and gamestate.hosting)):
            
            player_status_ui = player_status_ui_dictionary[player_position]
            
            if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
                if player_status_ui.moveset_select.contains(wotsuievents.mouse_pos):
                    versusclient.listener.set_moveset(player_status_ui.get_moveset().name, player_position)
                
                if player_status_ui.player_color_select.contains(wotsuievents.mouse_pos):
                    versusclient.listener.set_color(player_status_ui.get_color(), player_position)
                
                if player_status_ui.player_stats_widget.contains(wotsuievents.mouse_pos):
                    versusclient.listener.set_size(player_status_ui.get_size(), player_position)
                
                if player_status_ui.player_difficulty_select.contains(wotsuievents.mouse_pos):
                    versusclient.listener.set_difficulty(player_status_ui.get_difficulty(), player_position)
                
                if player_status_ui.player_type_select.contains(wotsuievents.mouse_pos):
                    versusclient.listener.set_player_type(player_status_ui.get_player_type(), player_position)
    
def get_local_player_setup_container_position(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return (50, 120)
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return (450, 120)

def init_player_status_ui_dictionary():
    """sets the player statuses for each position to waiting for player"""
    
    global player_status_ui_dictionary
    global local_player_container_created
    global assigned_positions
    
    local_player_container_created = False
    assigned_positions = []
    
    for player_position in versusclient.get_remote_player_positions():
        remote_player_id = versusclient.get_player_id_at_position(player_position)
        remote_player_nickname = versusclient.get_player_nickname(remote_player_id)
        
        new_ui_position = \
        get_local_player_setup_container_position(player_position)
    
        player_status_ui_dictionary[player_position] = \
            LocalPlayerSetupContainer(new_ui_position, get_playable_movesets())
        
        assigned_positions.append(player_position)
