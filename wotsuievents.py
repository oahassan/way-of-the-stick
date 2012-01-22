import pygame

class KeyRepeat():
    HIGH = 'HIGH'
    NONE = 'NONE'

key_repeat = KeyRepeat.NONE
events = []
event_types = []
mouse_pos = (0,0)
mouse_delta = (0,0)
mouse_buttons_pressed = (0,0,0)
keys_pressed = []
keys_released = []

def key_released(key):
    global keys_released
    global keys_pressed
    
    released_indicator = False
    
    if ((key in keys_released) or
        ((key in keys_pressed) == False)):
        released_indicator = True
    
    return released_indicator

def mousebutton_pressed():
    return mouse_buttons_pressed[0] or mouse_buttons_pressed[1] or mouse_buttons_pressed[2]

def get_events():
    global events
    global event_types
    global mouse_pos
    global mouse_delta
    global mouse_buttons_pressed
    global keys_pressed
    global keys_released
    global key_repeat
    
    events = pygame.event.get()
    
    event_types = []
    
    if key_repeat == KeyRepeat.NONE:
        keys_pressed = []
        keys_released = []
    
    for event in events:
        event_types.append(event.type)
        
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            mouse_buttons_pressed = event.buttons
            mouse_delta = event.rel
        elif ((event.type == pygame.MOUSEBUTTONUP) or
              (event.type == pygame.MOUSEBUTTONDOWN)):
            mouse_pos = event.pos
            mouse_buttons_pressed = pygame.mouse.get_pressed()
            
        elif event.type == pygame.KEYDOWN:
            if event.key not in keys_pressed:
                keys_pressed.append(event.key)
            
            if event.key in keys_released:
                keys_released.remove(event.key)
        elif event.type == pygame.KEYUP:
            keys_released.append(event.key)
            
            if event.key in keys_pressed:
                keys_pressed.remove(event.key)
    
    if pygame.MOUSEMOTION not in events:
        mouse_delta = (0,0)
