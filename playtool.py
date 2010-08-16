import sys

import pygame

import animation
import EditorTools

class PlayTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2
    
    def __init__(self):
        """creates a new play tool"""
        EditorTools.Tool.__init__(self,'play')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = PlayTool.draw_symbol
        
    def draw_symbol(self, surface):
        """draws the symbol of the play tool
        
        surface: the surface to draw the play tool's symbol on"""
        point1 = (self.button_center()[0] - 6, self.button_center()[1] - 6)
        point2 = (self.button_center()[0] - 6, self.button_center()[1] + 6)
        point3 = (self.button_center()[0] + 6, self.button_center()[1])
        
        pygame.draw.polygon(surface, \
                            self.symbol.color, \
                            (point1, point2, point3), \
                            PlayTool._SYMBOL_LINE_THICKNESS)
    
    def clear_state(self):
        """clears the state of this tool"""
        self.animation.frame_index = len(self.animation.frames) - 1
        EditorTools.Tool.clear_state(self)
    
    def handle_events(self, \
                 surface, \
                 mousePos, \
                 mouseButtonsPressed, \
                 events):
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            self.animation.frame_index += 1
            
            if self.animation.frame_index >= len(self.animation.frames):
                self.animation.frame_index = 0