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

class NetworkMessageNotification(button.Label):
    
    def __init__(self, text, timeout = 3000):
        button.Label.__init__(self, (0,0), text, (255,255,255), 20)
        self.timer = 0
        self.timeout = timeout
    
    def update(self, time_passed):
        self.timer += time_passed
    
    def expired(self):
        return self.timer > self.timeout

def get_playable_movesets():
    movesets = movesetdata.get_movesets()
    playable_movesets = [moveset for moveset in movesets if moveset.is_complete()]
    
    return playable_movesets

def load():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global remote_player_state
    global ip_address_input
    global hosting_indicator
    global connect_button
    global connected
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((10, 520), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    
    player_type_select = \
        wotsuicontainers.ButtonContainer(
            (50,140),
            200,
            300,
            'Select Player Type',
            button.TextButton,
            [['Human',15], ['Bot',15]]
        )
    
    player_moveset_select = \
        movesetselectui.MovesetSelectContainer(
            (50, 240),
            200,
            100,
            'Select Your Moveset',
            playable_movesets
        )
    
    remote_player_state = \
        button.Label((0,0), "Waiting for Player", (255,255,255),32)
    
    ip_address_input = \
        wotsuicontainers.TextEntryBox(
            prompt_text = 'Enter ip address: ',
            position = (10,10),
            max_length = 15,
            text_color = (255, 255, 255)
        )
    
    set_remote_player_state_position()
    
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
    global player_type_select
    global player_moveset_select
    global remote_player_state
    global ip_address_input
    global hosting_indicator
    global connected
    
    exit_button = None
    loaded = False
    start_match_label = None
    player_type_select = None
    player_moveset_select = None
    remote_player_state = None
    ip_address_input = None
    network_message_label = None
    
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
    global player_type_select
    global player_moveset_select
    global ip_address_input
    global connect_button
    global connected
    global network_message_notifications
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        if start_match_label.active:
            if start_match_label.contains(wotsuievents.mouse_pos):
                start_match_label.handle_selected()
        
        for button in player_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((player_type_select.selected_button != None)
                and (player_type_select.selected_button != button)):
                    player_type_select.selected_button.handle_deselected()
                
                player_type_select.selected_button = button
                break
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                if player_type_select.selected_button != None:
                    if player_type_select.selected_button.text.text == 'Human':
                        versusmode.player_type = versusmode.PlayerTypes.HUMAN
                    elif player_type_select.selected_button.text.text == 'Bot':
                        versusmode.player_type = versusmode.PlayerTypes.BOT
                
                unload()
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
    if loaded:
        player_moveset_select.handle_events()
        
        if player_moveset_select.selected_moveset != None:
            if start_match_label.active == False:
                start_match_label.activate()
        else:
            if start_match_label.active:
                start_match_label.inactivate()
        
        exit_button.draw(gamestate.screen)
        start_match_label.draw(gamestate.screen)
        player_type_select.draw(gamestate.screen)
        player_moveset_select.draw(gamestate.screen)
        remote_player_state.draw(gamestate.screen)
        
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
    

def set_remote_player_state_position():
    global remote_player_state
    
    window_center = (gamestate._WIDTH / 2, gamestate._HEIGHT / 2)
    
    y_pos = window_center[1] - (remote_player_state.height / 2)
    
    window_x_75_percent = window_center[0] + ((gamestate._WIDTH - window_center[0]) / 2)
    
    x_pos = window_x_75_percent - (remote_player_state.width / 2)
    
    remote_player_state.set_position((x_pos, y_pos))
