import EditorTools
import copy
import pygame

class AddFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2

    def __init__(self):
        """creates a new add frame tool"""
        EditorTools.Tool.__init__(self,'add frame')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = AddFrameTool.draw_symbol
        self.frame_count = 0
    
    def init_state(self, animation):
        """sets the state of a new add frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.add_frame(animation.frames[animation.frame_index])
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
    
    def add_frame(self, frame):
        """adds a new frame to the animation
        
        frame: the frame to add to the animation"""
        self.animation.add_frame(copy.deepcopy(frame))
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        vert_top = (self.button_center()[0] - 6, self.button_center()[1])
        vert_bottom = (self.button_center()[0] + 6, self.button_center()[1])
        hor_left = (self.button_center()[0], self.button_center()[1] - 6)
        hor_right = (self.button_center()[0], self.button_center()[1] + 6)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        vert_top, \
                        vert_bottom, \
                        AddFrameTool._SYMBOL_LINE_THICKNESS)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        hor_left, \
                        hor_right, \
                        AddFrameTool._SYMBOL_LINE_THICKNESS)