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
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((10, 500), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    
    player_type_select = \
        wotsuicontainers.ButtonContainer(
            (50,100),
            200,
            300,
            'Select Player Type',
            button.TextButton,
            [['Human',15], ['Bot',15]]
        )
    
    player_moveset_select = \
        movesetselectui.MovesetSelectContainer(
            (50, 220),
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

def unload():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global remote_player_state
    global ip_address_input
    global hosting_indicator
    
    exit_button = None
    loaded = False
    start_match_label = None
    player_type_select = None
    player_moveset_select = None
    remote_player_state = None
    ip_address_input = None
    
    if hosting_indicator:
        #clean up any remaining messages to the client
        versusclient.listener.Pump()
        versusclient.get_network_messages()
        
        versusclient.listener.close()
        versusclient.listener = None
        print("listener closed")
        
        #clean of any remaining messages to the server
        versusserver.server.Pump()
        
        versusserver.server.close()
        versusserver.server = None
        print("server closed")
    
    hosting_indicator = False

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global ip_address_input
    
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
                        versusmode.player_type = versusmode.PlayerTypes.BOTT
                
                unload()
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMODE
    if loaded:
        player_moveset_select.handle_events()
        ip_address_input.handle_events()
        
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
        ip_address_input.draw(gamestate.screen)
        
        
        if ((versusclient.get_connection_status() == 
        versusclient.ConnectionStatus.CONNECTED) or
        hosting_indicator):
            versusclient.listener.Pump()
            versusclient.get_network_messages()
        
        if hosting_indicator:
            versusserver.server.Pump()

def set_remote_player_state_position():
    global remote_player_state
    
    window_center = (gamestate._WIDTH / 2, gamestate._HEIGHT / 2)
    
    y_pos = window_center[1] - (remote_player_state.height / 2)
    
    window_x_75_percent = window_center[0] + ((gamestate._WIDTH - window_center[0]) / 2)
    
    x_pos = window_x_75_percent - (remote_player_state.width / 2)
    
    remote_player_state.set_position((x_pos, y_pos))
