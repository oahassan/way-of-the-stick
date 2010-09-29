import re

import pygame
import eztext

import wotsuievents
import movesetdata
import gamestate
import onlineversusmode
import versusserver
import versusclient

import button
from onlineversusmovesetselectui import NetworkMessageNotification, LocalPlayerSetupContainer, RemotePlayerStateLabel
import movesetselectui
import wotsuicontainers

import player
import humanplayer
import aiplayer

VALID_IPV4_ADDRESS_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

loaded = False
exit_button = None
start_match_label = None
player_type_select = None
player_moveset_select = None
remote_player_state = None
ip_address_input = None
connect_button = None
connected = False
network_message_notifications = []
join_match_button = None
local_player_container_created = False
assigned_positions = None
spectate_button = None
local_player_position = None

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
    global connect_button
    global connected
    global player_status_ui_dictionary
    global join_match_button
    global assigned_positions
    global spectate_button
    
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
    join_match_button.inactivate()
    
    spectate_button = button.TextButton("Spectate")
    spectate_button.set_position((600, 50))
    spectate_button.inactivate()
    
    if gamestate.hosting:
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
    global connected
    global join_match_button
    global assigned_positions
    global spectate_button
    global local_player_position
    
    local_player_position = None
    exit_button = None
    loaded = False
    start_match_label = None
    ip_address_input = None
    network_message_label = None
    join_match_button = None
    assigned_positions = None
    spectate_button = None
    
    if connected:
        #clean up any remaining messages to the client
        versusclient.listener.Pump()
        versusclient.get_network_messages()
        
        versusclient.listener.close()
        print("listener closed")
    
    if gamestate.hosting:
        #clean up any remaining messages to the server
        versusserver.server.Pump()
        
        versusserver.server.close()
        versusserver.server = None
        print("server closed")
        
        gamestate.hosting = False
    
    connected = False

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
                versusclient.listener.load_match_data()
                start_match_label.handle_deselected()
        
        #TODO - inactivate join if selected and same for spectate
        elif join_match_button.selected:
            if join_match_button.contains(wotsuievents.mouse_pos):
                versusclient.listener.join_match()
                join_match_button.handle_deselected()
        
        elif spectate_button.selected:
            if spectate_button.contains(wotsuievents.mouse_pos):
                versusclient.listener.spectate_match()
                spectate_button.handle_deselected()
    
    if loaded:
        
        handle_local_player_ui_changes()
        handle_remote_player_ui_changes()
        reset_empty_position_uis()
        
        for player_position, player_status_ui in player_status_ui_dictionary.iteritems():
            if hasattr(player_status_ui, "set_player_ready"):
                if versusclient.listener.player_positions_ready_dictionary[player_position]:
                    player_status_ui.set_player_ready(True)
                    
                    if player_position in versusclient.get_remote_player_positions():
                        player_status_ui.set_player_state_label_text("Player Ready")
                else:
                    player_status_ui.set_player_ready(False)
                    
                    if player_position in versusclient.get_remote_player_positions():
                        player_status_ui.set_player_state_label_text("Preparing...")
        
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
        
        if gamestate.hosting == False:
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
            
            if (versusclient.client_was_connected() and
            versusclient.listener.connection_status == versusclient.ConnectionStatus.DISCONNECTED):
                gamestate.mode = gamestate.Modes.ONLINEMENUPAGE
                unload()
            
            if not versusclient.client_was_connected():
                ip_address_input.draw(gamestate.screen)
                connect_button.draw(gamestate.screen)
        
        if connected or gamestate.hosting:
            if not join_match_button.active:
                join_match_button.activate()
            
            if not spectate_button.active:
                spectate_button.activate()
            
            versusclient.listener.Pump()
            versusclient.get_network_messages()
            
            remove_expired_network_message_notifications()
            get_new_network_message_notifications()
            layout_network_message_notifications()
            
            time_passed = gamestate.clock.get_time()
            
            for notification in network_message_notifications:
                notification.draw(gamestate.screen)
                notification.update(time_passed)
            
            if (versusclient.listener.server_mode == 
            versusserver.ServerModes.LOADING_MATCH_DATA):
                setup_versusmode()
            
            if versusclient.listener.server_mode == versusserver.ServerModes.MATCH:
                onlineversusmode.init()
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
        
        if gamestate.hosting:
            versusserver.server.Pump()

def setup_versusmode():
    if versusclient.local_player_is_in_match():
        setup_local_player()
        
    for player_position in versusclient.get_remote_player_positions():
        setup_remote_player(player_position)
    
    if (versusclient.local_player_is_in_match() and
    (versusclient.local_player_match_data_loaded() == False)):
        
        local_player_state_dictionary = onlineversusmode.get_local_player_state_dictionary()
        
        local_player_position = versusclient.get_local_player_position()
        versusclient.listener.send_player_initial_state(
            local_player_state_dictionary, 
            local_player_position
        )

def setup_remote_player(player_position):
    remote_player = onlineversusmode.RemotePlayer((0,0), player_position)
    
    set_player_initial_state(player_position, remote_player)
    
    onlineversusmode.set_player(player_position, remote_player)

def setup_local_player():
    """creates a local player in the versus mode module"""
    global player_status_ui_dictionary
    
    local_player_position = versusclient.get_local_player_position()
    
    local_player_ui = player_status_ui_dictionary[local_player_position]
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
    
    player.direction = get_player_model_direction(player_position)
    
    player.model.move_model(get_player_model_position(local_player_position))

def get_new_network_message_notifications():
    received_data = versusclient.listener.pop_received_data()
    
    for data in received_data:
        if (data[versusserver.DataKeys.ACTION] == 
        versusserver.ClientActions.SPECTATOR_JOINED):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[versusserver.DataKeys.NICKNAME] + " is now spectating."
                )
            )
        
        elif (data[versusserver.DataKeys.ACTION] ==
        versusserver.ClientActions.PLAYER_DISCONNECTED):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[versusserver.DataKeys.NICKNAME] + " has left the game."
                )
            )
        
        elif (data[versusserver.DataKeys.ACTION] ==
        versusserver.ClientActions.PLAYER_JOINED_MATCH):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[versusserver.DataKeys.NICKNAME] + " has joined the game."
                )
            )
        
        elif (data[versusserver.DataKeys.ACTION] ==
        versusserver.ClientActions.MATCH_FULL):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    "The match is full."
                )
            )
        
        elif (data[versusserver.DataKeys.ACTION] ==
        versusserver.ClientActions.PLAYER_DISCONNECTED):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[versusserver.DataKeys.NICKNAME] + " has left the game."
                )
            )
        
        else:
            #TODO - Raise invalid value error here
            pass

def handle_local_player_ui_changes():
    """change ui if local or remote player states change"""
    global player_status_ui_dictionary
    global local_player_container_created
    global local_player_position
    global assigned_positions
    
    if local_player_container_created:
        if not versusclient.local_player_is_in_match():
            new_ui = button.Label((0,0), "Waiting for Player", (255,255,255),32)
            set_player_state_position(new_ui, local_player_position)
            
            player_status_ui_dictionary[local_player_position] = new_ui
            
            assigned_positions.remove(local_player_position)
            local_player_position = None
            local_player_container_created = False
        
    else:
        
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

def handle_remote_player_ui_changes():
    global player_status_ui_dictionary
    global assigned_positions
    
    for player_position in versusclient.get_remote_player_positions():
        if player_position in assigned_positions:
            pass
        else:
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

def reset_empty_position_uis():
    global player_status_ui_dictionary
    global assigned_positions
    
    for player_position in assigned_positions:
        player_id = versusclient.listener.player_positions[player_position]
        
        if player_id == None:
            
            assigned_positions.remove(player_position)
            
            new_ui = button.Label((0,0), "Waiting for Player", (255,255,255),32)
            set_player_state_position(new_ui, player_position)
            
            player_status_ui_dictionary[player_position] = new_ui

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
