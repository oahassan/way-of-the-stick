import pygame

import wotsuievents
import movesetdata
import gamestate
import versusmode
import splash
import button
import movesetselectui
import wotsuicontainers
import stageselect
from versusmovesetselectui import MovesetSelector, PlayerStatsWidget, DifficultyLabel, ColorWheel
from enumerations import PlayerPositions, PlayerTypes, PlayerStates, Difficulties

class VersusMovesetSelectUiObjects():
    def __init__(self):        
        
        self.start_match_label = None
        self.player1_type_select = None
        self.player1_difficulty_select = None
        self.player1_moveset_select = None
        self.player1_stats_widget = None
        self.player1_color_select = None
        self.player2_type_select = None
        self.player2_difficulty_select = None
        self.player2_moveset_select = None
        self.player2_stats_widget = None
        self.player2_color_select = None
        self.exit_button = None
        
        self.init_UI_objects()
        
    def init_UI_objects(self):
        self.exit_button = button.ExitButton()        
        
        self.start_match_label = movesetselectui.MovesetActionLabel((50, 550), "Select Stage!")
        self.start_match_label.inactivate()
        
        playable_movesets = movesetdata.get_playable_movesets()
        
        self.player1_type_select = wotsuicontainers.ButtonContainer(
            (50,50),
            120,
            300,
            'Player 1',
            button.SelectableLabel,
            [[(0,0), 'Human',20], [(0,0), 'Bot',20]]
        )
        self.player1_type_select.buttons[0].handle_selected()
        self.player1_type_select.selected_button = self.player1_type_select.buttons[0]
        #versusmode.local_state.player_type_dictionary[PlayerPositions.PLAYER2] = PlayerTypes.HUMAN
        
        player1_difficulty_select_position = (50, self.player1_type_select.height + 10)
        self.player1_difficulty_select = wotsuicontainers.ButtonContainer(
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
        self.player1_difficulty_select.inactivate()
        
        player1_moveset_select_position = (
            50, 
            self.player1_difficulty_select.position[1] + self.player1_type_select.height
        )
        self.player1_moveset_select = MovesetSelector(
            player1_moveset_select_position,
            playable_movesets
        )
        player1_widget_position = (
            50, 
            self.player1_moveset_select.position[1] + self.player1_moveset_select.height + 10
        )
        self.player1_stats_widget = PlayerStatsWidget(player1_widget_position)
        
        player1_color_select_position = (
            player1_widget_position[0] + self.player1_stats_widget.width + 100,
            player1_widget_position[1] + 50
        )
        self.player1_color_select = ColorWheel(player1_color_select_position, 0)
        
        self.player2_type_select = wotsuicontainers.ButtonContainer(
            (450,50),
            120,
            300,
            'Player 2',
            button.SelectableLabel,
            [[(0,0), 'Human',20], [(0,0), 'Bot',20]]
        )
        self.player2_type_select.buttons[1].handle_selected()
        self.player2_type_select.selected_button = self.player2_type_select.buttons[1]
        #versusmode.local_state.player_type_dictionary[PlayerPositions.PLAYER2] = PlayerTypes.BOT
        
        player2_difficulty_select_position = (450, self.player2_type_select.height + 10)
        self.player2_difficulty_select = wotsuicontainers.ButtonContainer(
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
        self.player2_difficulty_select.activate()
        self.player2_difficulty_select.buttons[0].handle_selected()
        self.player2_difficulty_select.selected_button = self.player2_difficulty_select.buttons[0]
        
        player2_moveset_select_position = (
            450, 
            self.player2_difficulty_select.position[1] + self.player2_type_select.height
        )
        self.player2_moveset_select = MovesetSelector(
            player2_moveset_select_position,
            playable_movesets
        )
        player2_widget_position = (
            450, 
            self.player2_moveset_select.position[1] + self.player2_moveset_select.height + 10
        )
        self.player2_stats_widget = PlayerStatsWidget(player2_widget_position)
        
        player2_color_select_position = (
            player2_widget_position[0] + self.player2_stats_widget.width + 100,
            player2_widget_position[1] + 50
        )
        self.player2_color_select = ColorWheel(player2_color_select_position, 3)
    
    def get_player_type(self, player_type_select):
        if player_type_select.selected_button != None:
            if player_type_select.selected_button.text == 'Human':
                return PlayerTypes.HUMAN
            elif player_type_select.selected_button.text == 'Bot':
                return PlayerTypes.BOT
        else:
            return 'Human'

    def get_player_difficulty(self, player_difficulty_select):
        if player_difficulty_select.selected_button != None:
            return player_difficulty_select.selected_button.difficulty
        else:
            return None
        
class VersusMovesetSelectState():
    def __init__(self):
        self.UI_objects = VersusMovesetSelectUiObjects()
        self.loaded = True
    
    def create_player_data(self):
        
        return [
            versusmode.PlayerData(
                PlayerPositions.PLAYER1,
                self.UI_objects.get_player_type(self.UI_objects.player1_type_select),
                self.UI_objects.player1_moveset_select.selected_moveset,
                self.UI_objects.player1_stats_widget.get_size(),
                self.UI_objects.player1_color_select.selected_swatch.color,
                self.UI_objects.get_player_difficulty(self.UI_objects.player1_difficulty_select)
            ),
            versusmode.PlayerData(
                PlayerPositions.PLAYER2,
                self.UI_objects.get_player_type(self.UI_objects.player2_type_select),
                self.UI_objects.player2_moveset_select.selected_moveset,
                self.UI_objects.player2_stats_widget.get_size(),
                self.UI_objects.player2_color_select.selected_swatch.color,
                self.UI_objects.get_player_difficulty(self.UI_objects.player2_difficulty_select)
            )
        ]
    
    def handle_events(self):
        if self.loaded == False:
            self.load()
        
        exit_button = self.UI_objects.exit_button
        start_match_label = self.UI_objects.start_match_label
        player1_type_select = self.UI_objects.player1_type_select 
        player1_difficulty_select = self.UI_objects.player1_difficulty_select
        player1_moveset_select = self.UI_objects.player1_moveset_select
        player1_stats_widget = self.UI_objects.player1_stats_widget
        player1_color_select = self.UI_objects.player1_color_select
        player2_type_select = self.UI_objects.player2_type_select
        player2_difficulty_select = self.UI_objects.player2_difficulty_select
        player2_moveset_select = self.UI_objects.player2_moveset_select
        player2_stats_widget = self.UI_objects.player2_stats_widget
        player2_color_select = self.UI_objects.player2_color_select
        get_player_type = self.UI_objects.get_player_type
        get_player_difficulty = self.UI_objects.get_player_difficulty
        
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
                    self.exit()
            
            elif start_match_label.selected:
                if start_match_label.contains(wotsuievents.mouse_pos):
                    self.start_match()
            
        if self.loaded:
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
        
    def load(self):
        if self.UI_objects == None:
            self.UI_objects = VersusMovesetSelectUiObjects()

        self.loaded = True
        self.UI_objects.start_match_label.handle_deselected()
    
    def exit(self):
        gamestate.mode = gamestate.Modes.MAINMENU
        self.UI_objects = None
        self.exit_button = None
        self.loaded = False
    
    def start_match(self):
        splash.draw_loading_splash()
        gamestate.mode = gamestate.Modes.STAGESELECT
        stageselect.load(self.create_player_data())
        self.loaded = False

versusmode_state = VersusMovesetSelectState()

def handle_events():
    global versusmode_state
    
    versusmode_state.handle_events()
