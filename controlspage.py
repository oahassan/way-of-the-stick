import pygame

import wotsui
import wotsuievents
import button
import gamestate

loaded = False
exit_button = None

def load():
    global loaded
    global exit_button
    
    exit_button = button.ExitButton()
    loaded = True

def unload():
    global loaded
    global exit_button
    
    exit_button = None
    loaded = False

def handle_events():
    global loaded
    global exit_buttonr
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
    
    if loaded:
        exit_button.draw(gamestate.screen)
