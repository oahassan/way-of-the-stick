import sys

import pygame

import stick
import EditorTools

class LineTool(EditorTools.Tool):
    _SYMBOL_X_OFFSET = 5
    _SYMBOL_Y_OFFSET = 5
    _SYMBOL_LINE_THICKNESS = 3
    ANCHOR_COLOR = (0,0,255)
    
    def __init__(self):
        """creates a new point tool"""
        EditorTools.Tool.__init__(self,'draw')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = LineTool.draw_symbol
        self.symbol.color = (255, 255, 255)
        self.start_point = None
        self.end_point = None
    
    def clear_state(self):
        """clears the state of the line tool and fixes the max_lengths of all
        the lines and circles of the current frame"""
        for line in self.frame.lines():
            line.set_max_length()
            line.set_length()
        
        for circle in self.frame.circles():
            circle.set_max_length()
            circle.set_length()
        
        EditorTools.Tool.clear_state(self)
    
    def draw_symbol(self, surface):
        """draws a symbol onto a surface
        
        surface: the surface to draw the symbol on"""
        end_point1 = ((self.position[0] + LineTool._SYMBOL_X_OFFSET, \
                    self.position[1] + LineTool._SYMBOL_Y_OFFSET))
        end_point2 = ((self.button_bottom_right()[0] - LineTool._SYMBOL_X_OFFSET), \
                    (self.button_bottom_right()[1] - LineTool._SYMBOL_Y_OFFSET))
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point1, \
                        end_point2, \
                        LineTool._SYMBOL_LINE_THICKNESS)
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        """Handles events while using the point tool
        
        surface: surface to draw on
        mousePos: position of mouse at time of events
        events: events to handle"""
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        elif pygame.MOUSEBUTTONDOWN in event_types:
            self.handle_MOUSEBUTTONDOWN(mousePos, mouseButtonsPressed)
        elif pygame.MOUSEBUTTONUP in event_types:
            self.handle_MOUSEBUTTONUP()
        else:
            if ((self.start_point != None) and
                (self.slctd_point != None)):
                pos_change = pygame.mouse.get_rel()
                prev_pos = [self.slctd_point.pos[i] + pos_change[i]
                            for i in range(len(pos_change))]
                
                if ((prev_pos[0] != self.slctd_point.pos[0])
                or (prev_pos[1] != self.slctd_point.pos[1])):
                    self.handle_drag(mousePos)
    
    def handle_drag(self, mouse_pos):
        """Creates a new line if there is no current end point.  Otherwise it
        resizes the current line.
        
        mouse_pos: the current position of the mouse"""
        
        if self.end_point == None:
            if self.start_point.covers(mouse_pos) == False:
                self.add_point_to_frame(mouse_pos)
                self.end_point = self.slctd_point
                self.add_line_to_frame(self.start_point, self.end_point)
                self.start_point.color = LineTool.ANCHOR_COLOR
        else:
            self.end_point.pos = mouse_pos
    
    def handle_MOUSEBUTTONUP(self):
        """sets the start point and end point to none"""
        
        if self.start_point != None:
            self.start_point.color = stick.Point.inactiveColor
            self.start_point = None
        
        if self.end_point != None:
            self.end_point.color = stick.Point.inactiveColor
            self.end_point = None
    
    def handle_MOUSEBUTTONDOWN(self, mousePos, mouseButtonsPressed):
        """Determines behavior based on button clicked
        
        mousePos: the position of the mouse when the click event was
        recorded
        mouseButtonsPressed: list of pressed buttons"""
        
        #Deselect current selection
        if self.slctd_point != None:
            self.slctd_point.color = stick.Point.inactiveColor
        
        #Determine if an existing point was selected
        pointsUnderMouse = self.getPointsUnderMouse(mousePos)
        
        if mouseButtonsPressed[0] == True:
            if len(pointsUnderMouse) > 0:
                self.handlePointSlctd(pointsUnderMouse)
            else:
                self.add_point_to_frame(mousePos)
                self.start_point = self.slctd_point
            
        elif mouseButtonsPressed[2] == True:
            self.slctd_point = None
            
            if len(pointsUnderMouse) > 0:
                self.frame.remove_point(pointsUnderMouse[0])
    
    def handlePointSlctd(self, pointsUnderMouse):
        """Changes the selected point and draws a new line between 
        them
        
        pointsUnderMouse: list of points that cover the position of
        the mouse when the click event was recorded"""
        previous_slctd_point = self.slctd_point
        self.slctd_point = pointsUnderMouse[0]
        self.start_point = self.slctd_point
        self.slctd_point.color = stick.Point.slctdColor
    
    def add_line_to_frame(self, end_point1, end_point2):
        """Creates a new line and adds it to the current frame
        
        point1: the first endpoint of the line
        point2: the second endpoint of the line"""
        newLine = stick.Line(end_point1, end_point2)
        self.frame.add_line(newLine)
    
    def add_point_to_frame(self, pointPos):
        """Creates a new point at the current mouse position and adds it
        to the current frame
        
        pointPos: the position to place the point at"""
        new_point = stick.Point(pointPos)
        new_point.color = stick.Point.slctdColor
        self.frame.add_point(new_point)
        self.slctd_point = new_point
