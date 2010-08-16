import sys

import pygame
import animation
import EditorTools

class MoveFrameLeftTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new move frame left tool"""
        EditorTools.Tool.__init__(self,'move frame')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = MoveFrameLeftTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new previous frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.move_frame_left()
        self.frame_count = 0
    
    def move_frame_left(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index > 0:
            frames = self.animation.frames
            frame_index = self.animation.frame_index
            self.animation.frames = frames[:frame_index - 1] + [frames[frame_index]] + [frames[frame_index - 1]] + frames[frame_index + 1:]
            self.animation.frame_index -= 1
    
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
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor
    
    def draw_symbol(self, surface):
        """draws the symbol for the previous frame tool"""
        point1 = (self.button_center()[0] - 5, self.button_center()[1])
        point2 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        point3 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point4 = (self.button_center()[0] + 10, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point2, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point3, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point4, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)

class MoveFrameRightTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new move frame right tool"""
        EditorTools.Tool.__init__(self,'move frame')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = MoveFrameRightTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new next frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.move_frame_right()
        self.frame_count = 0
    
    def move_frame_right(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index < len(self.animation.frames) - 1:
            frames = self.animation.frames
            frame_index = self.animation.frame_index
            self.animation.frames = frames[:frame_index] + [frames[frame_index + 1]] + [frames[frame_index]] + frames[frame_index + 2:]
            self.animation.frame_index += 1
    
    def draw_symbol(self, surface):
        """draws the symbol for the next frame tool"""
        point1 = (self.button_center()[0] + 5, self.button_center()[1])
        point2 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        point3 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point4 = (self.button_center()[0] - 10, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point2, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point3, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point4, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
                        
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
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor

class PrevFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new previous frame tool"""
        EditorTools.Tool.__init__(self,'previous frame')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = PrevFrameTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new previous frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.go_to_prev_frame()
        self.frame_count = 0
    
    def go_to_prev_frame(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index > 0:
            self.animation.frame_index -= 1
    
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
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor
    
    def draw_symbol(self, surface):
        """draws the symbol for the previous frame tool"""
        point1 = (self.button_center()[0] - 5, self.button_center()[1])
        point2 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        point3 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point4 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point5 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        
        pygame.draw.polygon(surface, \
                            self.symbol.color, \
                            (point1, point2, point3), \
                            PrevFrameTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point4, \
                        point5, \
                        PrevFrameTool._SYMBOL_LINE_THICKNESS)
        
class NextFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new next frame tool"""
        EditorTools.Tool.__init__(self,'next frame')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = NextFrameTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new next frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.go_to_next_frame()
        self.frame_count = 0
    
    def go_to_next_frame(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index < len(self.animation.frames) - 1:
            self.animation.frame_index += 1
    
    def draw_symbol(self, surface):
        """draws the symbol for the next frame tool"""
        point1 = (self.button_center()[0] + 5, self.button_center()[1])
        point2 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        point3 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point4 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point5 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        
        pygame.draw.polygon(surface, \
                            self.symbol.color, \
                            (point1, point2, point3), \
                            NextFrameTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point4, \
                        point5, \
                        NextFrameTool._SYMBOL_LINE_THICKNESS)
                        
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
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor