import pygame
import re

import wotsuievents
import wotsuicontainers
import gamestate
import menupage
import button
import onlineversusmovesetselectloader
import versusclient
import versusserver

VALID_IPV4_ADDRESS_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

connect_button = None
join_match_button = None
server_address_input = None

exit_button = None
exit_indicator = False

loaded = False

def load():
    global exit_button
    global exit_indicator
    global loaded
    global connect_button
    global server_address_input
    exit_button = button.ExitButton()
    exit_indicator = False
    loaded = True
    
    server_address_input = None
    connect_button = button.TextButton("Connect")
    connect_button.set_position((50,350))
    connect_button.inactivate()
    server_address_input = wotsuicontainers.TextEntryBox(
        "Enter Server Address:",
        position = (50, 200)
    )
    
def unload():
    global exit_button
    global exit_indicator
    global loaded
    global connect_button
    global server_address_input
    
    exit_button = None
    exit_indicator = False
    loaded = False
    connect_button = None
    server_address_input = None

def handle_events():
    global exit_button
    global exit_indicator
    global connect_button
    global loaded
    global server_address_input
    
    if not loaded:
        load()
    else:
        server_address_input.handle_events()
        exit_button.draw(gamestate.screen)
        connect_button.draw(gamestate.screen)
        server_address_input.draw(gamestate.screen)
        
        if (re.match(VALID_IPV4_ADDRESS_REGEX, server_address_input.get_input()) and
        connect_button.active == False):
            connect_button.activate()
        elif (not re.match(VALID_IPV4_ADDRESS_REGEX, server_address_input.get_input()) and
        connect_button.active):
            connect_button.inactivate()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if exit_button.contains(wotsuievents.mouse_pos):
                exit_indicator = True
                exit_button.color = button.Button._SlctdColor
                exit_button.symbol.color = button.Button._SlctdColor
            
            if connect_button.contains(wotsuievents.mouse_pos):
                connect_button.handle_selected()
            
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if exit_indicator == True:
                exit_indicator = False
                exit_button.color = button.Button._InactiveColor
                exit_button.symbol.color = button.Button._InactiveColor
                
                if exit_button.contains(wotsuievents.mouse_pos):
                    unload()
                    gamestate.mode = gamestate.Modes.ONLINEMENUPAGE
            
            if connect_button.contains(wotsuievents.mouse_pos) and connect_button.selected:
                connect_button.handle_selected()
                
                unload()
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER
                onlineversusmovesetselectloader.load(versusserver.get_lan_ip_address())
