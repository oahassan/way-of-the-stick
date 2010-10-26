import pygame
import wotsuievents
import gamestate
from chatui import MessageEntryBox

entry_box = None
loaded_indicator = False

def load():
    global entry_box
    global loaded_indicator
    
    loaded_indicator = True
    entry_box = MessageEntryBox((50,0), 700, 20)
    entry_box.hide()

def unload():
    global entry_box
    global loaded_indicator
    
    loaded_indicator = False
    entry_box = None

def handle_events():
    global loaded_indicator
    global entry_box
    
    if not loaded_indicator:
        load()
    
    if entry_box.visible:
        if pygame.K_ESCAPE in wotsuievents.keys_pressed:
            close_entry_box()
        
        elif pygame.K_RETURN in wotsuievents.keys_pressed:
            close_entry_box()
        
        else:
            entry_box.handle_events()    
            entry_box.draw(gamestate.screen)
        
    else:
        if pygame.K_t in wotsuievents.keys_pressed:
            entry_box.show()

def close_entry_box():
    entry_box.clear_text()
    entry_box.hide()
