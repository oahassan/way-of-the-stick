import sys

import pygame

import stick
import LineTool

class CircleTool(LineTool.LineTool):
    
    _SYMBOL_RADIUS = 10
    
    def __init__(self):
        """creates a new point tool"""
        LineTool.LineTool.__init__(self)
        self.symbol.draw = CircleTool.draw_symbol
        
    def draw_symbol(self, surface):
        """draws the symbol of the point tool inside its rectangle
        
        surface:  the surface to draw the symbol on"""
        pygame.draw.circle(surface, \
                           self.symbol.color, \
                           self.button_center(), \
                           CircleTool._SYMBOL_RADIUS, \
                           LineTool.LineTool._SYMBOL_LINE_THICKNESS)
                           
    def handle_drag(self, mouse_pos):
        """Creates a new line if there is no current end point.  Otherwise it
        resizes the current line.
        
        mouse_pos: the current position of the mouse"""
        
        if self.end_point == None:
            if self.start_point.covers(mouse_pos) == False:
                self.add_point_to_frame(mouse_pos)
                self.end_point = self.slctd_point
                self.add_circle_to_frame(self.start_point, self.end_point)
                self.start_point.color = LineTool.LineTool.anchor_color
        else:
            self.end_point.pos = mouse_pos
    
    def add_circle_to_frame(self, end_point1, end_point2):
        """Creates a new line and adds it to the current frame
        
        point1: the first endpoint of the line
        point2: the second endpoint of the line"""
        new_circle = stick.Circle(end_point1, end_point2)
        self.frame.add_circle(new_circle)