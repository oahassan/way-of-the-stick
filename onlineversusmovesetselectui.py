import pygame

import movesetdata
import gamestate

import wotsui
import wotsuievents
import wotsuicontainers
import button
import movesetselectui
import versusmovesetselectui

import player
from enumerations import *

class ConnectingAlertBox(wotsuicontainers.AlertBox):
    
    def __init__(self):
        wotsuicontainers.AlertBox.__init__(
            self,
            border_color = (255,255,255),
            border_padding = 10,
            border_thickness = 5,
            text = 'Connecting to server...',
            width = 300,
            position = (0,0),
            text_color = (0,0,0),
            background_color = (255,255,255),
            font_size = 50
        )
        position = (
            400 - int(.5 * self.width),
            300 - int(self.height)
        )
        self.set_position(position)

class PlayerStatusUiBase():
    
    def __init__(self):
        self.ready_indicator = False
    
    def set_player_ready(self, ready_indicator):
        self.ready_indicator = ready_indicator
    
    def player_ready(self):
        return self.ready_indicator

class RemotePlayerStateLabel(wotsui.UIObjectBase, PlayerStatusUiBase):
    
    def __init__(self, position, player_id, player_name):
        wotsui.UIObjectBase.__init__(self)
        PlayerStatusUiBase.__init__(self)
        
        self.player_name_label = button.Label(position, player_name, (255,255,255), 25)
        self.add_child(self.player_name_label)
        
        player_state_label_position = (position[0], position[1] + 200)
        self.player_state_label = \
            button.Label(player_state_label_position, "Preparing...", (255,255,255), 25)
        self.add_child(self.player_state_label)
    
    def set_player_state_label_text(self, text):
        self.player_state_label.set_text(text)

class LocalPlayerSetupContainer(wotsui.UIObjectBase, PlayerStatusUiBase):
    
    def __init__(self, position, movesets):
        wotsui.UIObjectBase.__init__(self)
        PlayerStatusUiBase.__init__(self)
        
        player_type_select_position = position
        
        self.player_type_select = \
            wotsuicontainers.ButtonContainer(
                player_type_select_position,
                100,
                300,
                'Select Player Type',
                button.SelectableLabel,
                [[(0,0),player.PlayerTypes.BOT,15]] #[[player.PlayerTypes.HUMAN,15], [player.PlayerTypes.BOT,15]]
            )
        self.player_type_select.buttons[0].handle_selected()
        self.player_type_select.selected_button = self.player_type_select.buttons[0]
        self.add_child(self.player_type_select)
        
        player_difficulty_select_position = (
            player_type_select_position[0], 
            player_type_select_position[1] + self.player_type_select.height - 20
        )
        self.player_difficulty_select = wotsuicontainers.ButtonContainer(
            player_difficulty_select_position,
            100,
            350,
            'Select Difficulty',
            versusmovesetselectui.DifficultyLabel,
            [
                ['Easy', Difficulties.EASY], 
                ['Medium', Difficulties.MEDIUM],
                ['Hard', Difficulties.HARD],
                ['Challenge', Difficulties.CHALLENGE]
            ]
        )
        #self.player_difficulty_select.inactivate()
        self.add_child(self.player_difficulty_select)
        
        moveset_select_position = (
            player_difficulty_select_position[0],
            player_difficulty_select_position[1] + self.player_difficulty_select.height #+ 20
        )
        self.moveset_select = versusmovesetselectui.MovesetSelector(
            moveset_select_position,
            movesets
        )
        self.add_child(self.moveset_select)
        
        player_widget_position = (
            moveset_select_position[0], 
            self.moveset_select.position[1] + self.moveset_select.height + 10
        )
        self.player_stats_widget = versusmovesetselectui.PlayerStatsWidget(player_widget_position)
        self.add_child(self.player_stats_widget)
        
        player_color_select_position = (
            player_widget_position[0] + self.player_stats_widget.width + 100,
            player_widget_position[1] + 50
        )
        self.player_color_select = versusmovesetselectui.ColorWheel(player_color_select_position, 0)
        self.add_child(self.player_color_select)
    
    def handle_events(self):
    
        self.moveset_select.handle_events()
        self.player_type_select.handle_events()
        self.player_difficulty_select.handle_events()
        self.player_color_select.handle_events()
        self.player_stats_widget.handle_events()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            for button in self.player_type_select.buttons:
                if button.contains(wotsuievents.mouse_pos):
                    button.handle_selected()
                    
                    if ((self.player_type_select.selected_button != None)
                    and (self.player_type_select.selected_button != button)):
                        self.player_type_select.selected_button.handle_deselected()
                    
                    self.player_type_select.selected_button = button
                    break
    
    def get_player_type(self):
        if self.player_type_select.selected_button != None:
            if self.player_type_select.selected_button.text == 'Human':
                return PlayerTypes.HUMAN
            elif self.player_type_select.selected_button.text == 'Bot':
                return PlayerTypes.BOT
        else:
            return PlayerTypes.BOT
    
    def get_moveset(self):
        if self.moveset_select.selected_moveset != None:
            return self.moveset_select.selected_moveset
        else:
            return None
    
    def get_color(self):
        return self.player_color_select.selected_swatch.color
    
    def get_size(self):
        return self.player_stats_widget.get_size()
    
    def get_difficulty(self):
        if self.player_difficulty_select.selected_button != None:
            return self.player_difficulty_select.selected_button.difficulty
        else:
            return None
    
    def player_ready(self):
        if ((self.moveset_select.selected_moveset != None) and
        (self.player_type_select.selected_button != None)):
            self.ready_indicator = True
            return True
        else:
            self.ready_indicator = False
            return False
