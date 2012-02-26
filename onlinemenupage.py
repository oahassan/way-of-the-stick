import pygame

import wotsuievents
import gamestate
import menupage
import button
import onlineversusmovesetselectloader
import versusclient
import versusserver

host_match_button = None
join_match_button = None
menu = None

exit_button = None
exit_indicator = False
loaded = False

def load():
    global exit_button
    global exit_indicator
    global loaded
    global menu
    global host_match_button
    global join_match_button
    
    exit_button = button.ExitButton()
    exit_indicator = False
    loaded = True
    
    #Create menu buttons
    host_match_button = \
        menupage.MenuButton(
            "Host Match", 
            gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER
        )
    
    join_match_button = \
        menupage.MenuButton(
            "Join Match",
            gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER
        )
    
    #create module menu object
    menu = menupage.Menu()
    
    menu.load([host_match_button, join_match_button])
    
def unload():
    global exit_button
    global exit_indicator
    global loaded
    global menu
    global host_match_button
    global join_match_button
    
    exit_button = None
    exit_indicator = False
    loaded = False
    host_match_button = None
    join_match_button = None
    menu = None

def handle_events():
    global exit_button
    global exit_indicator
    global menu
    global host_match_button
    global loaded
    
    if not loaded:
        load()
    
    menu.handle_events()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(wotsuievents.mouse_pos):
                unload()
                gamestate.mode = gamestate.Modes.MAINMENU
        
    if gamestate.mode == gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER:
        if host_match_button.contains(wotsuievents.mouse_pos):
            gamestate.hosting = True
            onlineversusmovesetselectloader.load(versusserver.get_lan_ip_address())
        elif join_match_button.contains(wotsuievents.mouse_pos):
            onlineversusmovesetselectloader.load(versusserver.get_lan_ip_address())
    elif loaded:
        exit_button.draw(gamestate.screen)
        menu.draw(gamestate.screen)
