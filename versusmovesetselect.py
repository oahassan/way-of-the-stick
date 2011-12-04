import pygame

import wotsuievents
import movesetdata
import gamestate
import versusmode

import button
import movesetselectui
import wotsuicontainers
from versusmovesetselectui import MovesetSelector, PlayerStatsWidget, DifficultyLabel, ColorWheel
from enumerations import PlayerPositions, PlayerTypes, PlayerStates, Difficulties

loaded = False
exit_button = None
start_match_label = None
player1_type_select = None
player1_difficulty_select = None
player1_moveset_select = None
player1_stats_widget = None
player1_color_select = None
player2_type_select = None
player2_difficulty_select = None
player2_moveset_select = None
player2_stats_widget = None
player2_color_select = None

def get_playable_movesets():
    movesets = movesetdata.get_movesets()
    playable_movesets = [moveset for moveset in movesets if moveset.is_complete()]
    
    return playable_movesets

def load():
    global loaded
    global exit_button
    global start_match_label
    global player1_type_select
    global player1_difficulty_select
    global player1_moveset_select
    global player1_stats_widget
    global player1_color_select
    global player2_type_select
    global player2_difficulty_select
    global player2_moveset_select
    global player2_stats_widget
    global player2_color_select
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((50, 550), "Start Match!")
    start_match_label.inactivate()
    
    if player1_moveset_select == None:
        playable_movesets = get_playable_movesets()
        
        player1_type_select = wotsuicontainers.ButtonContainer(
            (50,50),
            120,
            300,
            'Player 1',
            button.SelectableLabel,
            [[(0,0), 'Human',20], [(0,0), 'Bot',20]]
        )
        player1_type_select.buttons[0].handle_selected()
        player1_type_select.selected_button = player1_type_select.buttons[0]
        versusmode.local_state.player_type_dictionary[PlayerPositions.PLAYER2] = PlayerTypes.HUMAN
        
        player1_difficulty_select_position = (50, player1_type_select.height + 10)
        player1_difficulty_select = wotsuicontainers.ButtonContainer(
            player1_difficulty_select_position,
            100,
            350,
            'Select Difficulty',
            DifficultyLabel,
            [
                ['Easy', Difficulties.EASY], 
                ['Medium', Difficulties.MEDIUM],
                ['Hard', Difficulties.HARD],
                ['Challenge', Difficulties.CHALLENGE]
            ]
        )
        player1_difficulty_select.inactivate()
        
        player1_moveset_select_position = (
            50, 
            player1_difficulty_select.position[1] + player1_type_select.height
        )
        player1_moveset_select = MovesetSelector(
            player1_moveset_select_position,
            playable_movesets
        )
        player1_widget_position = (
            50, 
            player1_moveset_select.position[1] + player1_moveset_select.height + 10
        )
        player1_stats_widget = PlayerStatsWidget(player1_widget_position)
        
        player1_color_select_position = (
            player1_widget_position[0] + player1_stats_widget.width + 100,
            player1_widget_position[1] + 50
        )
        player1_color_select = ColorWheel(player1_color_select_position, 0)
        
        player2_type_select = wotsuicontainers.ButtonContainer(
            (450,50),
            120,
            300,
            'Player 2',
            button.SelectableLabel,
            [[(0,0), 'Human',20], [(0,0), 'Bot',20]]
        )
        player2_type_select.buttons[1].handle_selected()
        player2_type_select.selected_button = player2_type_select.buttons[1]
        versusmode.local_state.player_type_dictionary[PlayerPositions.PLAYER2] = PlayerTypes.BOT
        
        player2_difficulty_select_position = (450, player2_type_select.height + 10)
        player2_difficulty_select = wotsuicontainers.ButtonContainer(
            player2_difficulty_select_position,
            100,
            350,
            'Select Difficulty',
            DifficultyLabel,
            [
                ['Easy', Difficulties.EASY], 
                ['Medium', Difficulties.MEDIUM],
                ['Hard', Difficulties.HARD],
                ['Challenge', Difficulties.CHALLENGE]
            ]
        )
        player2_difficulty_select.activate()
        player2_difficulty_select.buttons[0].handle_selected()
        player2_difficulty_select.selected_button = player2_difficulty_select.buttons[0]
        
        player2_moveset_select_position = (
            450, 
            player2_difficulty_select.position[1] + player2_type_select.height
        )
        player2_moveset_select = MovesetSelector(
            player2_moveset_select_position,
            playable_movesets
        )
        player2_widget_position = (
            450, 
            player2_moveset_select.position[1] + player2_moveset_select.height + 10
        )
        player2_stats_widget = PlayerStatsWidget(player2_widget_position)
        
        player2_color_select_position = (
            player2_widget_position[0] + player2_stats_widget.width + 100,
            player2_widget_position[1] + 50
        )
        player2_color_select = ColorWheel(player2_color_select_position, 3)
    
def unload():
    global loaded
    global exit_button
    global start_match_label
    
    exit_button = None
    loaded = False
    start_match_label = None

def clear_data():
    global player1_type_select
    global player1_difficulty_select
    global player1_moveset_select
    global player1_stats_widget
    global player1_color_select
    global player2_type_select
    global player2_difficulty_select
    global player2_moveset_select
    global player2_stats_widget
    global player2_color_select
    
    player1_type_select = None
    player1_difficulty_select = None
    player1_moveset_select = None
    player1_stats_widget = None
    player1_color_select = None
    player2_type_select = None
    player2_difficulty_select = None
    player2_moveset_select = None
    player2_stats_widget = None
    player2_color_select = None

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global player1_type_select
    global player1_difficulty_select
    global player1_moveset_select
    global player1_stats_widget
    global player1_color_select
    global player2_type_select
    global player2_difficulty_select
    global player2_moveset_select
    global player2_stats_widget
    global player2_color_select
    
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
                
                if button.text == "Bot":
                    player1_difficulty_select.activate()
                    
                    if player1_difficulty_select.selected_button != None:
                        player1_difficulty_select.selected_button.handle_selected()
                    else:
                        player1_difficulty_select.buttons[0].handle_selected()
                        player1_difficulty_select.selected_button = player1_difficulty_select.buttons[0]
                else:
                    player1_difficulty_select.inactivate()
                
                break
        
        if player1_difficulty_select.active:
            player1_difficulty_select.handle_events()
        
        for button in player2_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((player2_type_select.selected_button != None)
                and (player2_type_select.selected_button != button)):
                    player2_type_select.selected_button.handle_deselected()
                
                player2_type_select.selected_button = button
                
                if button.text == "Bot":
                    player2_difficulty_select.activate()
                    
                    if player2_difficulty_select.selected_button != None:
                        player2_difficulty_select.selected_button.handle_selected()
                    else:
                        player2_difficulty_select.buttons[0].handle_selected()
                        player2_difficulty_select.selected_button = player1_difficulty_select.buttons[0]
                else:
                    player2_difficulty_select.inactivate()
                
                break
        
        if player2_difficulty_select.active:
            player2_difficulty_select.handle_events()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
                clear_data()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                
                player_data = [
                    versusmode.PlayerData(
                        PlayerPositions.PLAYER1,
                        get_player_type(player1_type_select),
                        player1_moveset_select.selected_moveset,
                        player1_stats_widget.get_size(),
                        player1_color_select.selected_swatch.color,
                        get_player_difficulty(player1_difficulty_select)
                    ),
                    versusmode.PlayerData(
                        PlayerPositions.PLAYER2,
                        get_player_type(player2_type_select),
                        player2_moveset_select.selected_moveset,
                        player2_stats_widget.get_size(),
                        player2_color_select.selected_swatch.color,
                        get_player_difficulty(player2_difficulty_select)
                    )
                ]
                
                versusmode.init(player_data)
                
                #versusmode.local_state.init_recording(
                #    player1_moveset_select.selected_moveset.name,
                #    player2_moveset_select.selected_moveset.name
                #)
                
                unload()
                gamestate.mode = gamestate.Modes.VERSUSMODE
    if loaded:
        player1_moveset_select.handle_events()
        player2_moveset_select.handle_events()
        player1_stats_widget.handle_events()
        player2_stats_widget.handle_events()
        player1_color_select.handle_events()
        player2_color_select.handle_events()
        
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
        player1_difficulty_select.draw(gamestate.screen)
        player1_moveset_select.draw(gamestate.screen)
        player1_stats_widget.draw(gamestate.screen)
        player1_color_select.draw(gamestate.screen)
        player2_type_select.draw(gamestate.screen)
        player2_difficulty_select.draw(gamestate.screen)
        player2_moveset_select.draw(gamestate.screen)
        player2_stats_widget.draw(gamestate.screen)
        player2_color_select.draw(gamestate.screen)

def get_player_type(player_type_select):
    if player_type_select.selected_button != None:
        if player_type_select.selected_button.text == 'Human':
            return PlayerTypes.HUMAN
        elif player_type_select.selected_button.text == 'Bot':
            return PlayerTypes.BOT
    else:
        return 'Human'

def get_player_difficulty(player_difficulty_select):
    if player_difficulty_select.selected_button != None:
        return player_difficulty_select.selected_button.difficulty
    else:
        return None
