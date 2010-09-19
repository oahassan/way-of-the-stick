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
