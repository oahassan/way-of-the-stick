import re

import pygame
import eztext

import wotsuievents
import movesetdata
import gamestate
import versusmode
import versusserver
import versusclient

import button
from onlineversusmovesetselectui import NetworkMessageNotification, LocalPlayerSetupContainer, RemotePlayerStateLabel
import movesetselectui
import wotsuicontainers

VALID_IPV4_ADDRESS_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

loaded = False
exit_button = None
start_match_label = None
player_type_select = None
player_moveset_select = None
remote_player_state = None
ip_address_input = None
connect_button = None
hosting_indicator = False
connected = False
network_message_notifications = []
join_match_button = None
local_player_container_created = False
assigned_position = None

player_status_ui_dictionary = \
    {
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
    global ip_address_input
    global hosting_indicator
    global connect_button
    global connected
    global player_status_ui_dictionary
    global join_match_button
    global assigned_positions
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((10, 520), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    assigned_positions = []
    
    player1_ui = button.Label((50,300), "Waiting for Player", (255,255,255),32)
    player2_ui = button.Label((0,0), "Waiting for Player", (255,255,255),32)
    
    player_status_ui_dictionary = \
    {
        versusserver.PlayerPositions.PLAYER1 : player1_ui,
        versusserver.PlayerPositions.PLAYER2 : player2_ui
    }
    
    set_player_state_position(player1_ui, versusserver.PlayerPositions.PLAYER1)
    set_player_state_position(player2_ui, versusserver.PlayerPositions.PLAYER2)
    
    ip_address_input = \
        wotsuicontainers.TextEntryBox(
            prompt_text = 'Enter ip address: ',
            position = (10,10),
            max_length = 15,
            text_color = (255, 255, 255)
        )
    
    join_match_button = button.TextButton("Join Match")
    join_match_button.set_position((360, 50))
    
    if hosting_indicator:
        versusserver.start_lan_server()
        versusclient.connect_to_host(versusserver.get_lan_ip_address())
        connected = True
    else:
        connect_button = button.TextButton("Connect to server")
        connect_button.set_position((10, 50))
        connect_button.inactivate()

def unload():
    global loaded
    global exit_button
    global start_match_label
    global ip_address_input
    global hosting_indicator
    global connected
    global join_match_button
    global assigned_positions
    
    exit_button = None
    loaded = False
    start_match_label = None
    ip_address_input = None
    network_message_label = None
    join_match_button = None
    assigned_positions = None
    
    if connected:
        #clean up any remaining messages to the client
        versusclient.listener.Pump()
        versusclient.get_network_messages()
        
        versusclient.listener.close()
        versusclient.listener = None
        print("listener closed")
    
    if hosting_indicator:
        #clean of any remaining messages to the server
        versusserver.server.Pump()
        
        versusserver.server.close()
        versusserver.server = None
        print("server closed")
    
    connected = False
    hosting_indicator = False

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global ip_address_input
    global connect_button
    global connected
    global network_message_notifications
    global player_status_ui_dictionary
    global join_match_button
    global local_player_container_created
    
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
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                pass
        
        elif join_match_button.selected:
            if join_match_button.contains(wotsuievents.mouse_pos):
                versusclient.listener.join_match()
                join_match_button.handle_deselected()
    
    if loaded:
        players_ready = True
        
        if not local_player_container_created:
            
            if versusclient.local_player_is_in_match():
                local_player_position = versusclient.get_local_player_position()
                
                new_ui_position = \
                    get_local_player_setup_container_position(local_player_position)
                
                player_status_ui_dictionary[local_player_position] = \
                    LocalPlayerSetupContainer(new_ui_position, get_playable_movesets())
                
                local_player_container_created = True
                assigned_positions.append(local_player_position)
            else:
                local_player_container_created = False
        
        for player_position in versusclient.get_remote_player_positions():
            if not player_position in assigned_positions:
                remote_player_id = versusclient.get_player_id_at_position(player_position)
                remote_player_nickname = versusclient.get_player_nickname(remote_player_id)
                
                new_ui_position = \
                    get_remote_player_state_label_position(player_position)
                
                player_status_ui_dictionary[player_position] = \
                    RemotePlayerStateLabel(
                        new_ui_position,
                        remote_player_id,
                        remote_player_nickname
                    )
                
                assigned_positions.append(player_position)
        
        for player_status_ui in player_status_ui_dictionary.values():
            player_status_ui.handle_events()
            player_status_ui.draw(gamestate.screen)
            
            if hasattr(player_status_ui, "player_ready"):
                player_ready = getattr(player_status_ui, "player_ready")() and player_ready
        
        if players_ready:
            if start_match_label.active == False:
                start_match_label.activate()
        else:
            if start_match_label.active:
                start_match_label.inactivate()
        
        join_match_button.draw(gamestate.screen)
        exit_button.draw(gamestate.screen)
        start_match_label.draw(gamestate.screen)
        
        if hosting_indicator == False:
            if ip_address_input.active:
                ip_address_input.handle_events()
            
            server_address = ip_address_input.text_entry_box.value.strip()
            
            if re.match(VALID_IPV4_ADDRESS_REGEX, server_address) and not connected:
                connect_button.activate()
            else:
                connect_button.inactivate()
            
            if connect_button.active and connect_button.contains(wotsuievents.mouse_pos):
                if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                    connect_button.handle_selected()
                    
                if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
                
                    if connect_button.selected:
                        ip_address_input.inactivate()
                    
                        versusclient.connect_to_host(server_address)
                        versusclient.get_network_messages()
                        versusclient.listener.Pump()
                        
                        connect_button.handle_deselected()
                        connect_button.inactivate()
                        
                        connected = True
                        
                    else:
                        connect_button.handle_deselected()
                
            ip_address_input.draw(gamestate.screen)
            connect_button.draw(gamestate.screen)
        
        if connected or hosting_indicator:
            versusclient.listener.Pump()
            versusclient.get_network_messages()
            
            remove_expired_network_message_notifications()
            get_new_network_message_notifications()
            layout_network_message_notifications()
            
            time_passed = gamestate.clock.get_time()
            
            for notification in network_message_notifications:
                notification.draw(gamestate.screen)
                notification.update(time_passed)
        
        if hosting_indicator:
            versusserver.server.Pump()

def get_new_network_message_notifications():
    received_actions = versusclient.listener.pop_received_actions()
    
    for action in received_actions:
        if (action[versusserver.DataKeys.ACTION] == 
        versusserver.ClientActions.SPECTATOR_JOINED):
            network_message_notifications.append(
                NetworkMessageNotification(
                    action[versusserver.DataKeys.NICKNAME] + " is now spectating."
                )
            )
        else:
            #TODO - Raise invalid value error here
            pass

def remove_expired_network_message_notifications():
    global network_message_notifications
    
    removable_messages = \
        [notification \
        for notification in network_message_notifications if notification.expired()]
    
    [network_message_notifications.remove(notification) \
    for notification in removable_messages]

def layout_network_message_notifications():
    global network_message_notifications
    
    network_message_count = len(network_message_notifications)
    
    row_count = min(5, network_message_count)
    
    first_row_position = (50, gamestate._HEIGHT - (row_count * 20))
    current_row_position = first_row_position
    
    for notification in network_message_notifications:
        notification.set_position(current_row_position)
        
        current_row_position = (50, current_row_position[1] + 20)
    
def get_local_player_setup_container_position(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return (50, 150)
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return (450, 150)

def get_remote_player_state_label_position(player_position):
    if player_position == versusserver.PlayerPositions.PLAYER1:
        return (50, 150)
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        return (450, 150)
 
def set_player_state_position(player_state_label, player_position):
    
    if player_position == versusserver.PlayerPositions.PLAYER1:
        window_right_center = (0, gamestate._HEIGHT / 2)
        
        y_pos = window_right_center[1] - (player_state_label.height / 2)
        
        window_x_25_percent = gamestate._WIDTH / 4
        x_pos = window_x_25_percent - (player_state_label.width / 2)
        
        player_state_label.set_position((x_pos, y_pos))
        
    elif player_position == versusserver.PlayerPositions.PLAYER2:
        window_center = (gamestate._WIDTH / 2, gamestate._HEIGHT / 2)
        
        y_pos = window_center[1] - (player_state_label.height / 2)
        
        window_x_75_percent = window_center[0] + ((gamestate._WIDTH - window_center[0]) / 2)
        x_pos = window_x_75_percent - (player_state_label.width / 2)
        
        player_state_label.set_position((x_pos, y_pos))
