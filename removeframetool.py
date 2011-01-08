import EditorTools

import pygame

class RemoveFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2

    def __init__(self):
        """creates a new remove frame tool"""
        EditorTools.Tool.__init__(
            self,
            'delete frame',
            'Delete the current frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = RemoveFrameTool.draw_symbol
        self.frame_count = 0
    
    def init_state(self, animation):
        """sets the state of a new remove frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.remove_frame(animation.frames[animation.frame_index])
        self.frame_count = 0
    
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
    
    def remove_frame(self, frame):
        """removes the current frame to the animation and sets a clone of it 
        as the new current frame
        
        frame: the frame to remove to the animation"""
        self.animation.remove_frame(frame)
    
    def draw_symbol(self, surface):
        """draws symbol of the remove frame tool
        
        surface: the top left corner of the button"""
        hor_left = (self.button_center()[0] - 6, self.button_center()[1])
        hor_right = (self.button_center()[0] + 6, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        hor_left, \
                        hor_right, \
                        RemoveFrameTool._SYMBOL_LINE_THICKNESS)
