import shelve
import copy
import math

import button

import pygame

import gamestate
import player
import animationexplorer
import animation
import stick

class ActionTyps():
    INPUT_ACTIONS = "inputactions"
    DEFAULT_ACTIONS = "preloaded actions"

_KEY_BINDING_DB_FILE_NM = "key_bindings_wots.dat"
key_bindings = {}

new_animation_button = NewAnimationButton((0,0))
_THUMBNAIL_PADDING = 25

slctd_animation = None
slctd_animation_thumbnail = None

exit_button = button.ExitButton()
exit_indicator = False

def init():
    global key_bindings
    key_bindings = shelve.open(_KEY_BINDING_DB_FILE_NM, "c")

def save_key_binding(key, action):
    global key_bindings
    
    key_bindings[key] = action

def delete_key_binding(key):
    """deletes an action from the action database"""
    global key_bindings
    
    del key_bindings[key]

def close():
    key_bindings.close()

class AttackButton(button.Button):
    SLCTD_COLOR = (255,0,0)
    INACTIVE_COLOR = (255,255,255)
    _Width = 50
    _Height = 50
    _SymbolLineThickness = 2
    
    def __init__(self, pos):
        button.Button.__init__(self)
        self.width = NewAnimationButton._Width
        self.height = NewAnimationButton._Height
        self.pos = pos
        self.line_thickness = NewAnimationButton._SymbolLineThickness
        self.symbol.draw = NewAnimationButton.draw_symbol
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        vert_top = (self.center()[0], self.center()[1] - 6)
        vert_bottom = (self.center()[0], self.center()[1] + 6)
        hor_left = (self.center()[0] - 6, self.center()[1])
        hor_right = (self.center()[0] + 6, self.center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        vert_top, \
                        vert_bottom, \
                        NewAnimationButton._SymbolLineThickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        hor_left, \
                        hor_right, \
                        NewAnimationButton._SymbolLineThickness)