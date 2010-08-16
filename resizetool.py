import sys

import pygame

import stick
import EditorTools
import pulltool
import mathfuncs

class ResizeTool(EditorTools.Tool):
    _SYMBOL_X_OFFSET = 10
    _SYMBOL_Y_OFFSET = 10
    _SYMBOL_ARROW_SMALL_OFFSET = 0
    _SYMBOL_ARROW_LARGE_OFFSET = 5
    
    _SYMBOL_LINE_THICKNESS = 3
    anchor_color = (0,0,255)
    
    def __init__(self):
        """creates a new resize tool"""
        EditorTools.Tool.__init__(self,'Resize')
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = ResizeTool.draw_symbol
        self.symbol.color = (255, 255, 255)
        self.line_thickness = ResizeTool._SYMBOL_LINE_THICKNESS
    
    def draw_symbol(self, surface):
        """draws a symbol onto a surface
        
        surface: the surface to draw the symbol on"""
        end_point1 = ((self.position[0] + ResizeTool._SYMBOL_X_OFFSET, \
                    self.position[1] + ResizeTool._SYMBOL_Y_OFFSET))
        arrow_point1_1 = ((end_point1[0] + \
                          ResizeTool._SYMBOL_ARROW_SMALL_OFFSET), \
                          (end_point1[1] + \
                          ResizeTool._SYMBOL_ARROW_LARGE_OFFSET))
        arrow_point1_2 = ((end_point1[0] + \
                          ResizeTool._SYMBOL_ARROW_LARGE_OFFSET), \
                          (end_point1[1] + \
                          ResizeTool._SYMBOL_ARROW_SMALL_OFFSET))
        end_point2 = ((self.button_bottom_right()[0] - ResizeTool._SYMBOL_X_OFFSET), \
                    (self.button_bottom_right()[1] - ResizeTool._SYMBOL_Y_OFFSET))
        arrow_point2_1 = ((end_point2[0] - \
                          ResizeTool._SYMBOL_ARROW_SMALL_OFFSET), \
                          (end_point2[1] - \
                          ResizeTool._SYMBOL_ARROW_LARGE_OFFSET))
        arrow_point2_2 = ((end_point2[0] - \
                         ResizeTool._SYMBOL_ARROW_LARGE_OFFSET), \
                          (end_point2[1] - \
                          ResizeTool._SYMBOL_ARROW_SMALL_OFFSET))
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point1, \
                        end_point2, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point1, \
                        arrow_point1_1, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point1, \
                        arrow_point1_2, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point2, \
                        arrow_point2_1, \
                        self.line_thickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        end_point2, \
                        arrow_point2_2, \
                        self.line_thickness)
    
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
            if self.slctd_point != None:
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
        
        if self.slctd_point.id in self.frame.point_to_lines.keys():
            for line in self.frame.point_to_lines[self.slctd_point.id]:
                if self.allow_line_resize(line, \
                                         self.slctd_point, \
                                         mouse_pos):
                    self.slctd_point.pos = mouse_pos
                    line.set_length()
        
        if self.slctd_point.id in self.frame.point_to_circles.keys():
            for line in self.frame.point_to_circles[self.slctd_point.id]:
                if self.allow_line_resize(line, \
                                         self.slctd_point, \
                                         mouse_pos):
                    self.slctd_point.pos = mouse_pos
                    line.set_length()
        
        if self.slctd_point.pos == mouse_pos:
            lines = []
            lines.extend(self.frame.lines())
            lines.extend(self.frame.circles())
            point_to_lines = pulltool.build_point_to_lines(lines)
            pulltool.pull_point(self.slctd_point, \
                                mouse_pos, \
                                self.slctd_point, \
                                [], \
                                point_to_lines)
    
    def allow_line_resize(self, line, end_point, new_pos):
        """checks if a line will exceed its max length if one of its
        endpoints moves to a new position
        
        line: the line to test
        end_point: the end point moving to a new position
        new_pos: the new position of the end_point"""
        
        indicator = True
        
        new_length = mathfuncs.distance(new_pos, \
                                        line.other_end_point(end_point).pos)
        
        if new_length >= line.max_length:
            indicator = False
        
        return indicator
    
    def handle_MOUSEBUTTONUP(self):
        """sets the start point and end point to none"""
        
        if self.slctd_point != None:
            self.slctd_point.color = stick.Point.inactiveColor
        
        self.slctd_point = None
    
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
                self.slctd_point = pointsUnderMouse[0]
                self.slctd_point.color = (stick.Point.slctdColor)