import pygame

import wotsuievents
import movesetdata
import gamestate
import versusmode

import button
import movesetselectui
import wotsuicontainers
from enumerations import PlayerPositions

loaded = False
exit_button = None
start_match_label = None
player1_type_select = None
player1_moveset_select = None
player2_type_select = None
player2_moveset_select = None

def get_playable_movesets():
    movesets = movesetdata.get_movesets()
    playable_movesets = [moveset for moveset in movesets if moveset.is_complete()]
    
    return playable_movesets

def load():
    global loaded
    global exit_button
    global start_match_label
    global player1_type_select
    global player1_moveset_select
    global player2_type_select
    global player2_moveset_select
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((10, 500), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    player1_type_select = wotsuicontainers.ButtonContainer(
        (50,50),
        100,
        300,
        'Select Player Type',
        button.TextButton,
        [['Human',15], ['Bot',15]]
    )
    
    player1_moveset_select_position = (50, 50 + player1_type_select.height + 30)
    player1_moveset_select = movesetselectui.MovesetSelectContainer(
        player1_moveset_select_position,
        300,
        100,
        'Select Your Moveset',
        playable_movesets
    )
    player2_type_select = wotsuicontainers.ButtonContainer(
        (400,50),
        100,
        300,
        'Select Enemy Type',
        button.TextButton,
        [['Human',15], ['Bot',15]]
    )
    player2_moveset_select_position = (400, 50 + player2_type_select.height + 30)
    player2_moveset_select = movesetselectui.MovesetSelectContainer(
        player2_moveset_select_position,
        300, \
        100, \
        'Select Enemy Moveset', \
        playable_movesets
    )
    
def unload():
    global loaded
    global exit_button
    global start_match_label
    global player1_type_select
    global player1_moveset_select
    global player2_type_select
    global player2_moveset_select
    
    exit_button = None
    loaded = False
    start_match_label = None
    player1_type_select = None
    player1_moveset_select = None
    player2_type_select = None
    player2_moveset_select = None

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global player1_type_select
    global player1_moveset_select
    global player2_type_select
    global player2_moveset_select
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        if start_match_label.active:
            if start_match_label.contains(wotsuievents.mouse_pos):
                start_match_label.handle_selected()
        
        for button in player1_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((player1_type_select.selected_button != None)
                and (player1_type_select.selected_button != button)):
                    player1_type_select.selected_button.handle_deselected()
                
                player1_type_select.selected_button = button
                break
        
        for button in player2_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((player2_type_select.selected_button != None)
                and (player2_type_select.selected_button != button)):
                    player2_type_select.selected_button.handle_deselected()
                
                player2_type_select.selected_button = button
                break
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                if player1_type_select.selected_button != None:
                    if player1_type_select.selected_button.text.text == 'Human':
                        versusmode.player_type_dictionary[PlayerPositions.PLAYER1] = versusmode.PlayerTypes.HUMAN
                    elif player1_type_select.selected_button.text.text == 'Bot':
                        versusmode.player_type_dictionary[PlayerPositions.PLAYER1] = versusmode.PlayerTypes.BOT
                
                if player2_type_select.selected_button != None:
                    if player2_type_select.selected_button.text.text == 'Human':
                        versusmode.player_type_dictionary[PlayerPositions.PLAYER2] = versusmode.PlayerTypes.HUMAN
                    elif player2_type_select.selected_button.text.text == 'Bot':
                        versusmode.player_type_dictionary[PlayerPositions.PLAYER2] = versusmode.PlayerTypes.BOT
                
                versusmode.init()
                versusmode.player_dictionary[PlayerPositions.PLAYER1].load_moveset(
                    player1_moveset_select.selected_moveset
                )
                versusmode.player_dictionary[PlayerPositions.PLAYER2].load_moveset(
                    player2_moveset_select.selected_moveset
                )
                unload()
                gamestate.mode = gamestate.Modes.VERSUSMODE
    if loaded:
        player1_moveset_select.handle_events()
        player2_moveset_select.handle_events()
        
        if ((player1_moveset_select.selected_moveset != None) and
            (player1_type_select.selected_button != None) and
            (player2_moveset_select.selected_moveset != None) and
            (player2_type_select.selected_button != None)):
            if start_match_label.active == False:
                start_match_label.activate()
        else:
            if start_match_label.active:
                start_match_label.inactivate()
        
        exit_button.draw(gamestate.screen)
        start_match_label.draw(gamestate.screen)
        player1_type_select.draw(gamestate.screen)
        player1_moveset_select.draw(gamestate.screen)
        player2_type_select.draw(gamestate.screen)
        player2_moveset_select.draw(gamestate.screen)
