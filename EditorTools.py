import pygame

from wotsuicontainers import TextBox
import button
import stick

class Symbol:
    _DfltColor = (255, 255, 255)
    """an empty class for the symbol draw funciton of a tool"""
    def __init__(self):
        """creates a new symbol"""
        self.color = Symbol._DfltColor
        
    def draw(self):
        """place holder for a draw function"""
        pass

class Tool(button.Button):
    """base class for editor tools"""
    
    _BUTTON_WIDTH = 51
    _BUTTON_HEIGHT = 45
    _SlctdColor = (255,0,0)
    _InactiveColor = (255,255,255)
    _ButtonLineThickness = 2
    
    def __init__(self, label_text = None):
        """creates a new Tool"""
        button.Button.__init__(self)
        
        #Variables for drawing the button for the point tool
        self.width = Tool._BUTTON_WIDTH
        self.height = Tool._BUTTON_HEIGHT
        self.button_height = Tool._BUTTON_HEIGHT
        self.button_width = Tool._BUTTON_WIDTH
        self.symbol = None
        self.line_thickness = Tool._ButtonLineThickness
        self.color = Tool._InactiveColor
        self.fixed_dimensions = True
        self.fixed_position = True
        
        #Variables for managing state while using a point tool
        self.frame = None
        self.point_clicked = False
        self.slctd_point = None
        self.animation = None
        self.label = None
        
        if label_text != None:
            self.label = \
                TextBox(
                    label_text,
                    Tool._BUTTON_WIDTH,
                    (self.position[0], self.position[1] + Tool._BUTTON_HEIGHT + Tool._ButtonLineThickness),
                    (255,255,255),
                    15
                )
            
            self.height += self.label.height
            self.width = max(self.width,self.label.width)
            self.add_child(self.label)
    
    def init_state(self, animation):
        """initalizes the state variables
        
        frame: current frame being edited"""
        self.animation = animation
        self.frame = animation.frames[animation.frame_index]
        self.color = Tool._SlctdColor
        self.symbol.color = Tool._SlctdColor
    
    def clear_state(self):
        """resets the state variables to default values"""
        for point in self.frame.points():
            point.color = stick.Point.inactiveColor
        
        self.animation = None
        self.frame = None
        self.point_clicked = False
        self.slctd_point = None
        self.color = Tool._InactiveColor
        self.symbol.color = Tool._InactiveColor
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        pass
    
    def draw(self, surface):
        """draws a tool button on a surface
        
        assumes that the symbol has a draw method
        surface: the surface to draw the tool button on"""
        
        rect = (self.position[0], \
                self.position[1], \
                self.button_width, \
                self.button_height)
                
        pygame.draw.rect(surface, \
                        self.color, \
                        rect, \
                        self.line_thickness)
        
        self.symbol.draw(self, surface)
        
        if self.label != None:
            self.label.draw(surface)
    
    def button_center(self):
        return (int(self.position[0] + (.5 * self.button_width)),
                int(self.position[1] + (.5 * self.button_height)))
    
    def button_bottom_right(self):
        return (self.position[0] + self.button_width,
                self.position[1] + self.button_height)
    
    def getPointsUnderMouse(self, mousePos):
        """gets a list of points the are under the mouse
        
        mousePos: the position of the mouse when the click event was
        recorded"""
        points = []
        
        for point in self.frame.points():
            if point.covers(mousePos):
                points.append(point)
        
        return points
