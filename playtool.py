import sys

import pygame

from testplayer import TestPlayer
import animation
import EditorTools
import gamestate

class PlayTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2
    
    def __init__(self):
        """creates a new play tool"""
        EditorTools.Tool.__init__(self,'play')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = PlayTool.draw_symbol
        self.animation_type = None
        self.animation = None
        
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
    def init_state(self, animation):
        EditorTools.Tool.init_state(self, animation)
        self.test_player = TestPlayer()
        self.test_player.init_state()
        self.test_player.load_action(self.animation_type, self.animation)
        
        gamestate.frame_rate = 100
        gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS
        
        gamestate.screen.blit(gamestate.stage.background_image, (0,0))
        gamestate.new_dirty_rects.append(pygame.Rect((0,0),(gamestate._WIDTH, gamestate._HEIGHT)))
    
    def clear_state(self):
        """clears the state of this tool"""
        self.animation.frame_index = len(self.animation.frames) - 1
        EditorTools.Tool.clear_state(self)
    
        gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
        gamestate.frame_rate = 20
    
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
            for rect in gamestate.old_dirty_rects:
                rect_surface = pygame.Surface((rect.width,rect.height))
                rect_surface.blit(gamestate.stage.background_image,((-rect.left,-rect.top)))
                gamestate.screen.blit(rect_surface,rect.topleft)
            
            self.test_player.handle_events()
            #self.animation.frame_index += 1
            
            #if self.animation.frame_index >= len(self.animation.frames):
            #    self.animation.frame_index = 0
