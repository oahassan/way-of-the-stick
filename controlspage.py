import pygame

import wotsuievents
import gamestate
import controlsdata
from button import Label, ExitButton
from movesetbuilderui import BindButton
from wotsuicontainers import ButtonContainer

loaded = False
exit_button = None
set_movement_keys_label = None
set_attack_keys_label = None
movement_buttons = None
attack_buttons = None
active_button = None
press_key_label = None
bind_buttons = None

def load():
    global loaded
    global exit_button
    global set_movement_keys_label
    global set_attack_keys_label
    global movement_buttons
    global attack_buttons
    global active_button
    global press_key_label
    global bind_buttons
    
    exit_button = ExitButton()
    loaded = True
    press_key_label = \
        Label(
            (60, 15),
            "Select an action, then press a key to bind the action to that key",
            (255, 0, 0),
            22
        )
    set_movement_keys_label = Label((20, 60), "Set Movement Keys", (255, 255, 255))
    set_attack_keys_label = Label((20, 280), "Set Attack Keys", (255, 255, 255))
    
    movement_buttons = []
    
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MOVE_LEFT, "Move Left"),
        movement_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MOVE_UP, "Move Up"),
        movement_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MOVE_RIGHT, "Move Right"),
        movement_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MOVE_DOWN, "Move Down"),
        movement_buttons
    )
    
    layout_buttons( 
        (40, set_movement_keys_label.height + set_movement_keys_label.position[1] + 15),
        movement_buttons
    )
    
    attack_buttons = []
    
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.WEAK_PUNCH, "Weak Punch"),
        attack_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.WEAK_KICK, "Weak Kick"),
        attack_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MEDIUM_PUNCH, "Medium Punch"),
        attack_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.MEDIUM_KICK, "Medium Kick"),
        attack_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.STRONG_PUNCH, "Strong Punch"),
        attack_buttons
    )
    add_bind_button_to_button_list(
        BindButton(controlsdata.InputActionTypes.STRONG_KICK, "Strong Kick"),
        attack_buttons
    )
    
    layout_buttons( 
        (40, set_attack_keys_label.height + set_attack_keys_label.position[1] + 15),
        attack_buttons
    )
    
    bind_buttons = []
    bind_buttons.extend(movement_buttons)
    bind_buttons.extend(attack_buttons)
    
    active_button = None

def unload():
    global loaded
    global exit_button
    global set_movement_keys_label
    global set_attack_keys_label
    global movement_buttons
    global attack_buttons
    global active_button
    global press_key_label
    global bind_buttons
    
    exit_button = None
    loaded = False
    set_movement_keys_label = None
    set_attack_keys_label = None
    movement_buttons = None
    attack_buttons = None
    active_button = None
    press_key_label = None
    bind_buttons = None

def handle_events():
    global loaded
    global exit_button
    global set_movement_keys_label
    global set_attack_keys_label
    global movement_buttons
    global attack_buttons
    global active_button
    global press_key_label
    global bind_buttons
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        for bind_button in bind_buttons:
            if bind_button.contains(wotsuievents.mouse_pos):
                
                if active_button != None:
                    active_button.handle_deselected()
                
                bind_button.handle_selected()
                active_button = bind_button
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
    if (pygame.KEYDOWN in wotsuievents.event_types and
    active_button != None):
        active_button.set_key(wotsuievents.keys_pressed[0])
        controlsdata.set_control_key(
            active_button.move_type,
            wotsuievents.keys_pressed[0]
        )
        
        active_button.handle_deselected()
        active_button = None
    
    if loaded:
        exit_button.draw(gamestate.screen)
        set_movement_keys_label.draw(gamestate.screen)
        set_attack_keys_label.draw(gamestate.screen)
        press_key_label.draw(gamestate.screen)
        
        for attack_button in attack_buttons:
            attack_button.draw(gamestate.screen)
        
        for movement_button in movement_buttons:
            movement_button.draw(gamestate.screen)

def add_bind_button_to_button_list(bind_button, button_list,):
    
    bind_button.set_key(controlsdata.get_control_key(bind_button.move_type))
    button_list.append(bind_button)

def layout_buttons(start_position, buttons):
    
    button_position = start_position
    
    for button_index in range(len(buttons)):
        
        buttons[button_index].set_position(button_position)
        
        next_x_position = button_position[0]
        next_y_position = button_position[1]
        
        if ((button_index + 1) % 2) == 1:
            next_x_position = start_position[0] + 400
        
        else:
            next_x_position = start_position[0]
            next_y_position += buttons[button_index].height + 10
        
        button_position = (next_x_position, next_y_position)
