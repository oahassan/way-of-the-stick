import sys
import pygame
import gamestate
import wotsuievents
import wotsui
import settingsdata
from volumeui import VolumeControl
from button import Label, ExitButton
import music

sound_label = None
sound_control = None
music_label = None
music_control = None

exit_button = None
exit_indicator = False
loaded = False

def load():
    global exit_button
    global exit_indicator
    global loaded
    global sound_label
    global sound_control
    global music_label
    global music_control
    
    exit_button = ExitButton()
    exit_indicator = False
    loaded = True
    
    #Create control labels and controls
    sound_label_position = (20,20)
    sound_label = Label(
        sound_label_position,
        'Effects Volume',
        (255,255,255),
        40
    )
    sound_control = VolumeControl()
    sound_control_position = (
        sound_label_position[0],
        sound_label_position[1] + sound_label.height + 20
    )
    sound_control.create_children()
    sound_control.set_layout_data(sound_control_position, 300)
    sound_control.set_scroll_percent(settingsdata.get_sound_volume())
    
    music_label_position = sound_control_position = (
        sound_control.position[0],
        sound_control.position[1] + sound_control.height + 40
    )
    music_label = Label(
        music_label_position, 
        'Music Volume',
        (255,255,255),
        40
    )
    music_control = VolumeControl()
    music_control.create_children()
    music_control_position = (
        music_label_position[0],
        music_label_position[1] + music_label.height + 20
    )
    music_control.set_layout_data(music_control_position, 300)
    music_control.set_scroll_percent(settingsdata.get_music_volume())

def unload():
    global exit_button
    global exit_indicator
    global loaded
    global sound_label
    global sound_control
    global music_label
    global music_control
    
    settingsdata.save_sound_volume(sound_control.get_scroll_percent())
    settingsdata.save_music_volume(music_control.get_scroll_percent())
    
    exit_button = None
    exit_indicator = False
    loaded = False
    sound_label = None
    sound_control = None
    music_label = None
    music_control = None

def handle_events():
    global exit_button
    global exit_indicator
    global sound_label
    global sound_control
    global music_label
    global music_control
    
    if not loaded:
        load()
    
    sound_control.handle_events()
    music_control.handle_events()
    music.set_volume(music_control.get_scroll_percent())
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.handle_selected()
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                unload()
                gamestate.mode = gamestate.Modes.MAINMENU
        
        if gamestate.mode == gamestate.Modes.ONLINEVERSUSMOVESETSELECT:
            if host_match_button.contains(wotsuievents.mouse_pos):
                gamestate.hosting = True
            elif join_match_button.contains(wotsuievents.mouse_pos):
                versusclient.load()
    
    if loaded:
        exit_button.draw(gamestate.screen)
        sound_label.draw(gamestate.screen)
        sound_control.draw(gamestate.screen)
        music_label.draw(gamestate.screen)
        music_control.draw(gamestate.screen)
