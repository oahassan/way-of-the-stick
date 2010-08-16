import pygame
import eztext

import button
import EditorTools
import animationexplorer
import actionwizard

class SaveTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2
    _TEXT_BOX_X_POS = 200
    _TEXT_BOX_Y_POS = 10
    
    def __init__(self):
        """creates a new add frame tool"""
        EditorTools.Tool.__init__(self,'save')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = SaveTool.draw_symbol
        self.symbol.line_thickness = SaveTool._SYMBOL_LINE_THICKNESS
        self.frame_count = 0
        self.save_button = SaveButton()
        self.text_input = eztext.Input(maxlength=100, \
                                      x=SaveTool._TEXT_BOX_X_POS, \
                                      y=SaveTool._TEXT_BOX_Y_POS, \
                                      prompt='Type animation name: ', \
                                      color=(255,255,255), \
                                      font=pygame.font.Font(None, 12))
        self.animation_saved = False
        self.draw_input = False
        self.animation_type = None
    
    def init_state(self, animation):
        """sets the state of a new add frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.frame_count = 0
        self.animation_saved = False
        self.draw_input = True
        
        if animation.name != "":
            self.text_input.value = animation.name
    
    def clear_state(self):
        self.animation_saved = False
        self.save_button.color = button.Button._InactiveColor
        self.draw_input = False
        EditorTools.Tool.clear_state(self)

    
    def draw(self, surface):
        EditorTools.Tool.draw(self, surface)
        
        if self.draw_input:
            self.save_button.draw(surface)
            self.text_input.draw(surface)
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        if self.animation_saved:
            pass
            # if self.frame_count == 5:
                # self.clear_state()
                # frameeditor.current_tool = None
            # else:
                # self.frame_count += 1
        else:
            event_types = []
            
            for event in events:
                event_types.append(event.type)
            
            self.text_input.update(events)
            
            if pygame.MOUSEBUTTONDOWN in event_types: 
                if self.save_button.contains(mousePos):
                    self.save_button.color = button.Button._SlctdColor
            elif pygame.MOUSEBUTTONUP in event_types:
                if self.save_button.contains(mousePos):
                    self.save()
                else:
                    self.save_button.color = button.Button._InactiveColor
        
        self.draw(surface)
    
    def save(self):
        if len(self.text_input.value) > 0:
            if ((self.animation.name == "") or
            (self.animation.name != self.text_input.value)):
                self.animation.name = self.text_input.value
            
            if self.animation_type == None:
                animationexplorer.save_animation(self.text_input.value, \
                                                self.animation)
            else:
                actionwizard.save_animation(self.animation_type, self.animation)
            
            self.animation_saved = True
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        bottom = (self.button_center()[0], self.button_center()[1] + 6)
        top_left = (self.button_center()[0] - 6, self.button_center()[1] - 6)
        top_right = (self.button_center()[0] + 6, self.button_center()[1] - 6)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom, \
                        top_left, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom, \
                        top_right, \
                        self.line_thickness)

class SaveButton(button.Button):
    _WIDTH = 30
    _HEIGHT = 30
    _POSITION = (400, 10)
    
    def __init__(self):
        button.Button.__init__(self)
        self.width = SaveButton._WIDTH
        self.height = SaveButton._HEIGHT
        self.position = SaveButton._POSITION
        self.line_thickness = SaveTool._SYMBOL_LINE_THICKNESS
        self.symbol.draw = SaveButton.draw_symbol
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        bottom = (self.center()[0], self.center()[1] + 6)
        top_left = (self.center()[0] - 6, self.center()[1] - 6)
        top_right = (self.center()[0] + 6, self.center()[1] - 6)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom, \
                        top_left, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom, \
                        top_right, \
                        self.line_thickness)