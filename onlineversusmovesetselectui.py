import pygame

import movesetdata
import gamestate

import wotsui
import wotsuicontainers
import button
import movesetselectui

class NetworkMessageNotification(button.Label):
    
    def __init__(self, text, timeout = 3000):
        button.Label.__init__(self, (0,0), text, (255,255,255), 20)
        self.timer = 0
        self.timeout = timeout
    
    def update(self, time_passed):
        self.timer += time_passed
    
    def expired(self):
        return self.timer > self.timeout

class RemotePlayerStateLabel(wotsui.UIObjectBase):
    
    def __init__(self, position, player_id, player_name):
        self.player_name_label = button.Label(position, player_name, (255,255,255), 23)
        self.add_child(self.player_name_label)
        
        player_state_label_position = (position[0], position[1] + 200)
        self.player_state_label = \
            button.Label(position, "Preparing...", (255,255,255), 23)
        self.add_child(self.player_state_label)
        
    def set_player_state_label_text(self, text):
        self.player_state_label.set_text(text)

class LocalPlayerSetupContainer(wotsui.UIObjectBase):
    
    def __init__(self, position, movesets):
        wotsui.UIObjectBase.__init__(self)
        
        player_type_select_position = position
        
        self.player_type_select = \
            wotsuicontainers.ButtonContainer(
                player_type_select_position,
                100,
                300,
                'Select Player Type',
                button.TextButton,
                [['Human',15], ['Bot',15]]
            )
        self.add_child(self.player_type_select)
        
        moveset_select_position = \
            (
                player_type_select_position[0],
                player_type_select_position[1] + self.player_type_select.height + 20
            )
        self.moveset_select = \
            movesetselectui.MovesetSelectContainer(
                moveset_select_position,
                200, \
                100, \
                'Select Your Moveset', \
                movesets
            )
        self.add_child(self.moveset_select)
    
    def handle_events(self):
    
        self.moveset_select.handle_events()
        self.player_type_select.handle_events()
    
    def player_ready(self):
        if ((self.moveset_select.selected_moveset != None) and
        (self.player_type_select.selected_button != None)):
            return True
        else:
            return False
