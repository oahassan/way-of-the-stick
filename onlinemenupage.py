import pygame

import wotsuievents
import gamestate
import menupage
import button

host_match_button = None
join_match_button = None

exit_button = None
exit_indicator = False
loaded = False

def load():
    global exit_button
    global exit_indicator
    global loaded
    
    exit_button = button.ExitButton()
    exit_indicator = False
    loaded = True
    
def unload():
    global exit_button
    global exit_indicator
    global loaded
    
    exit_button = None
    exit_indicator = False
    loaded = False

def handle_events():
    global exit_button
    global exit_indicator
    
    if not loaded:
        load()
    
    exit_button.draw(gamestate.screen)
    
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
