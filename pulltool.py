import sys
import copy

import pygame

import EditorTools
import stick
import button

class PullTool(EditorTools.Tool):
    _SYMBOL_RADIUS = 5
    
    def __init__(self):
        """creates a new point tool"""
        EditorTools.Tool.__init__(
            self,
            "pull",
            "Left click and drag to move a point.  Right click to anchor a point."
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.color = (255, 255, 255)
        self.symbol.draw = PullTool.draw_symbol
        self.anchor_points = None
        self.mouse_button_down = False
    
    def init_state(self, animation):
        """initalizes the state variables
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        
        self.anchor_points = []
        
        for line in self.frame.lines():
            line.set_length()
        
        for circle in self.frame.circles():
            circle.set_length()
    
    def clear_state(self):
        """clears the state of a point tool"""
        EditorTools.Tool.clear_state(self)
        self.anchor_points = None
    
    def draw_symbol(self, surface):
        """draws the symbol of the point tool inside its rectangle
        
        surface:  the surface to draw the symbol on"""
        pygame.draw.circle(surface, \
                           self.symbol.color, \
                           self.button_center(), \
                           PullTool._SYMBOL_RADIUS)
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        """Handles events while using the point tool
        
        surface: surface to draw on
        mousePos: position of mouse at time of events
        events: events to handle"""
        
        if (self.frame != self.animation.frames[self.animation.frame_index]):
            self.init_state(self.animation)
        
        for event in events:
            if event.type == pygame.QUIT: 
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handleMouseButtonDown(mousePos, mouseButtonsPressed)
                self.mouse_button_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.point_clicked = False
                self.mouse_button_down = False
                
                if self.slctd_point != None:
                    if self.slctd_point in self.anchor_points:
                        self.slctd_point.color = (0,0,255)
                    else:
                        self.slctd_point.color = stick.Point.inactiveColor
                    self.slctd_point = None
                
            elif event.type == pygame.MOUSEMOTION:
                if ((self.mouse_button_down == True) and
                    (self.slctd_point == None)):
                    reference_position = self.frame.get_reference_position()
                    new_position = (event.rel[0], event.rel[1])
                    self.frame.move(new_position)
        
        if self.point_clicked == True:
            lines = []
            lines.extend(self.frame.lines())
            lines.extend(self.frame.circles())
            point_to_lines = build_point_to_lines(lines)
            pull_point(self.slctd_point, \
                        mousePos, \
                        self.slctd_point, \
                        self.anchor_points, \
                        point_to_lines)
    
    def handleMouseButtonDown(self, mousePos, mouseButtonsPressed):
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
                self.point_clicked = True
        elif mouseButtonsPressed[2] == True:
            self.slctd_point = None
            
            if len(pointsUnderMouse) > 0:
                self.anchor_point(pointsUnderMouse)
            
            self.point_clicked = False
    
    def handlePointSlctd(self, pointsUnderMouse):
        """Changes the selected point and draws a new line between 
        them
        
        pointsUnderMouse: list of points that cover the position of
        the mouse when the click event was recorded"""
        previousslctd_point = self.slctd_point
        self.slctd_point = pointsUnderMouse[0]
        
        if previousslctd_point == None:
            self.slctd_point.color = stick.Point.slctdColor
        else:
            if self.slctd_point.id == previousslctd_point.id:
                self.slctd_point.color = stick.Point.slctdColor
            else:
                previousslctd_point.color = stick.Point.inactiveColor
                self.slctd_point.color = stick.Point.slctdColor
    
    def anchor_point(self, points_under_mouse):
        """adds the selected point as an anchor.  If it is already an anchor
        removes the selected point as an anchor.
        
        points_under_mouse: list of points that cover the position of the 
        mouse when the click event was recorded"""
        
        slctd_point = points_under_mouse[0]
        
        if slctd_point in self.anchor_points:
            self.anchor_points.remove(slctd_point)
            slctd_point.color = stick.Point.inactiveColor
        else:
            self.anchor_points.append(slctd_point)
            slctd_point.color = stick.Point.anchorColor


def pull_point(point, \
              new_pos, \
              start_point, \
              anchor_points, \
              point_to_lines, \
              pulled_lines = None, \
              pulled_anchors = None):
    """pulls all points connected to the selected point through lines
    
    point_to_lines: list of lines that have already been pulled"""
    
    if pulled_lines == None:
        pulled_lines = []
    
    if pulled_anchors == None:
        pulled_anchors = []
    
    pulled_points = []
    
    point.pos = (new_pos[0], new_pos[1])
    
    #anchors points pull first
    for line in point_to_lines[point.id]:
        if not (line in pulled_lines):
            for anchor_point in anchor_points:
                if anchor_point == line.other_end_point(point):
                    if ((point in anchor_points) and
                        (point == start_point)):
                        line.pull(anchor_point)
                        pulled_lines.append(line)
                    elif not (anchor_point in pulled_anchors):
                        pulled_anchors.append(anchor_point)
                        pulled_lines.append(line)
                        reverse_point_to_lines = build_point_to_lines(pulled_lines)
                        pull_point(anchor_point, \
                                    anchor_point.pos, \
                                    start_point, \
                                    anchor_points, \
                                    reverse_point_to_lines, \
                                    [], \
                                    pulled_anchors)
    
    for line in point_to_lines[point.id]:
        if not (line in pulled_lines):
            other_end_point = line.other_end_point(point)
            line.pull(point)
            pulled_points.append(other_end_point)
            pulled_lines.append(line)
    
    for pulled_point in pulled_points:
        pull_point(pulled_point, \
                    pulled_point.pos, \
                    start_point, \
                    anchor_points, \
                    point_to_lines, \
                    pulled_lines, \
                    pulled_anchors)

def build_point_to_lines(lines):
    """builds a dictionary that maps points to each line it belongs to
    
    lines: the lines to buld the dictionary from"""
    
    point_to_lines = {}
    
    for line in lines:
        for point in line.points:
            if point.id in point_to_lines.keys():
                point_to_lines[point.id].append(line)
            else:
                point_lines = [line]
                
                point_to_lines[point.id] = point_lines
    
    return point_to_lines

def remove_line_from_point_to_lines(line, point_to_lines):
    """removes a line from every point entry in a point_to_lines
    dictionary
    
    line: the line to remove
    point_to_lines: dictionary of point to lines"""
    
    for point in line.points:
        point_to_lines[point.id].remove(line)
