import pygame
import gamestate
import wotsui
import wotsuievents

FONT_SIZES = [5, 7, 9, 12, 16, 21, 28, 37, 50, 67]

class Symbol:
    _DfltColor = (255, 255, 255)
    """an empty class for the symbol draw funciton of a tool"""
    def __init__(self):
        """creates a new symbol"""
        self.color = Symbol._DfltColor
        
    def draw(self, surface):
        """place holder for a draw function"""
        pass
    
    def draw_relative(self, surface):
        """place holder for a draw relative function"""
        pass

class Button(wotsui.SelectableObjectBase):
    """base class for editor tools"""
    
    _SlctdColor = (255,0,0)
    _InactiveColor = (255,255,255)
    _ButtonLineThickness = 2
    
    def __init__(self):
        """creates a new Tool
        
        pos: top left corner of the tools button."""
        wotsui.SelectableObjectBase.__init__(self)
        
        self.slctd_color = (255,0,0)
        self.inactive_color = (100,100,100)
        self.active_color = (255,255,255)
        self.symbol = Symbol()
        self.line_thickness = 1
        self.color = self.active_color
        self.selected = False
    
    def handle_events(self):
        pass
    
    def draw(self, surface):
        """draws a tool button on a surface
        
        assumes that the symbol has a draw method
        surface: the surface to draw the tool button on"""
        wotsui.UIObjectBase.draw(self, surface)
        
        rect = (self.position[0], \
                self.position[1], \
                self.width, \
                self.height)
                
        pygame.draw.rect(surface, \
                        self.color, \
                        rect, \
                        self.line_thickness)
        
        self.symbol.draw(self, surface)
    
    def draw_relative(self, surface, reference_position):
        """draws a tool button on a surface relative to the given position
        
        assumes that the symbol has a draw method
        surface: the surface to draw the tool button on
        reference_position: position to treat as origin"""
        wotsui.UIObjectBase.draw_relative(self, surface, reference_position)
        
        relative_position = self.get_relative_position(reference_position)
        
        rect = (relative_position[0], \
                relative_position[1], \
                self.width, \
                self.height)
                
        pygame.draw.rect(surface, \
                        self.color, \
                        rect, \
                        self.line_thickness)
        
        self.symbol.draw(self, surface)

class ExitButton(Button):
    _Width = 30
    _Height = 30
    _Position = (gamestate._WIDTH - _Width, 0)
    _SymbolLineThickness = 3
    
    def __init__(self):
        Button.__init__(self)
        self.width = ExitButton._Width
        self.height = ExitButton._Height
        self.position = ExitButton._Position
        self.line_thickness = ExitButton._SymbolLineThickness
        self.symbol.draw = ExitButton.draw_symbol
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        center = self.center()
        
        top_left = (center[0] - 6, center[1] - 6)
        top_right = (center[0] + 6, center[1] - 6)
        bottom_left = (center[0] - 6, center[1] + 6)
        bottom_right = (center[0] + 6, center[1] + 6)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom_right, \
                        top_left, \
                        ExitButton._SymbolLineThickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        bottom_left, \
                        top_right, \
                        ExitButton._SymbolLineThickness)

class TextButton(Button):
    TEXT_PADDING = 15
    
    def __init__(self, text, font_size = 32):
        Button.__init__(self)
        text_pos = (self.position[0] + TextButton.TEXT_PADDING, \
                    self.position[1] + TextButton.TEXT_PADDING)
        
        self.text = Label(text_pos, text, self.color, font_size)
        
        self.add_child(self.text)
        
        self.width = (2 * TextButton.TEXT_PADDING) + self.text.width
        self.height = (2 * TextButton.TEXT_PADDING) + self.text.height
        
        self.symbol.draw = TextButton.draw_symbol
    
    def inactivate(self):
        Button.inactivate(self)
        
        self.text.text_color = self.inactive_color
    
    def activate(self):
        Button.activate(self)
        
        self.text.text_color = self.active_color
    
    def draw_symbol(self, surface):
        pass

class Label(wotsui.UIObjectBase):
    def __init__(self, position, text, text_color, font_size=32):
        wotsui.UIObjectBase.__init__(self)
        self.position = position
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font('freesansbold.ttf', font_size)
        text_dimensions = self.font.size(self.text)
        self.width = text_dimensions[0]
        self.height = text_dimensions[1]
        self.fixed_dimensions = True
    
    def set_text(self, text):
        self.text = text
        text_dimensions = self.font.size(self.text)
        self.width = text_dimensions[0]
        self.height = text_dimensions[1]
    
    def draw(self, surface):
        """draw text of label on a surface"""
        if self.visible:
            wotsui.UIObjectBase.draw(self, surface)
            
            text_surface = self.font.render(self.text, True, self.text_color)
            
            surface.blit(text_surface, self.position)
    
    def draw_relative(self, surface, reference_position):
        """draw text of label on a surface relative positioned relative to a given 
        position"""
        if self.visible:
            wotsui.UIObjectBase.draw_relative(
                self,
                surface,
                reference_position
            )
            
            text_surface = self.font.render(self.text, True, self.text_color)
            
            surface.blit(text_surface, self.get_relative_position(reference_position))

class SelectableLabel(Label, wotsui.SelectableObjectBase):
    def __init__(self, position, text, font_size=32):
        wotsui.SelectableObjectBase.__init__(self)
        Label.__init__(self, position, text, self.active_color, font_size)
    
    def draw(self, surface):
        """draw text of label on a surface"""
        if self.visible:
            wotsui.UIObjectBase.draw(self, surface)
            
            text_surface = self.font.render(self.text, True, self.color)
            
            surface.blit(text_surface, self.position)
    
    def draw_relative(self, surface, reference_position):
        """draw text of label on a surface relative positioned relative to a given 
        position"""
        if self.visible:
            wotsui.UIObjectBase.draw_relative(
                self,
                surface,
                reference_position
            )
            
            text_surface = self.font.render(self.text, True, self.color)
            
            surface.blit(text_surface, self.get_relative_position(reference_position))

class DeleteButton(Button):
    
    def __init__(self):
        Button.__init__(self)
        self.line_thickness = 3
    
    def create(self, position, width, height):
        self.width = width
        self.height = height
        self.position = position
    
    def draw(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        center = self.center()
        
        top_left = self.position
        top_right = (top_left[0] + self.width, top_left[1])
        bottom_left = (top_left[0], top_left[1] + self.height)
        bottom_right = self.bottom_right()
        
        pygame.draw.line(surface, \
                        self.color, \
                        bottom_right, \
                        top_left, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.color, \
                        bottom_left, \
                        top_right, \
                        self.line_thickness)
