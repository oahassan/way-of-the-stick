import pygame

import movesetdata
import gamestate

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

class LocalPlayerSetupContainer(wotsui.UIObjectBase):
    
    def __init__(self, position, movesets):
        
        player_type_select_position = position
        
        self.player_type_select = \
            wotsuicontainers.ButtonContainer(
                player_type_select_position,
                200,
                300,
                'Select Player Type',
                button.TextButton,
                [['Human',15], ['Bot',15]]
            )
        
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
    
    def handle_events():
    
        player_moveset_select.handle_events()
        bot_moveset_select.handle_events()
    
    def player_ready():
        if ((player_moveset_select.selected_moveset != None) and
            (bot_moveset_select.selected_moveset != None)):
            return True
        else:
            return False
