import pygame

import mathfuncs

class PointNames:
    HEAD_TOP = "headtop"
    TORSO_TOP = "torsotop"
    TORSO_BOTTOM = "torobottom"
    LEFT_ELBOW = "leftelbow"
    LEFT_HAND = "lefthand"
    RIGHT_ELBOW = "rightelbow"
    RIGHT_HAND = "righthand"
    LEFT_KNEE = "leftknee"
    LEFT_FOOT = "leftfoot"
    RIGHT_KNEE = "rightknee"
    RIGHT_FOOT = "rightfoot"
    POINT_NAMES = [HEAD_TOP,TORSO_TOP,TORSO_BOTTOM,LEFT_ELBOW, \
                   LEFT_HAND,RIGHT_ELBOW,RIGHT_HAND,LEFT_KNEE, \
                   LEFT_FOOT,RIGHT_KNEE,RIGHT_FOOT]

class LineNames:
    HEAD = "head"
    LEFT_UPPER_ARM = "leftupperarm"
    LEFT_FOREARM = "leftforearm"
    RIGHT_UPPER_ARM = "rightupperarm"
    RIGHT_FOREARM = "rightforearm"
    TORSO = "torso"
    LEFT_UPPER_LEG = "leftupperleg"
    LEFT_LOWER_LEG = "leftlowerleg"
    RIGHT_UPPER_LEG = "rightupperleg"
    RIGHT_LOWER_LEG = "rightlowerleg"

LINE_TO_POINTS = dict([(LineNames.HEAD, [PointNames.HEAD_TOP,PointNames.TORSO_TOP]),
                       (LineNames.LEFT_UPPER_ARM, [PointNames.TORSO_TOP,PointNames.LEFT_ELBOW]),
                       (LineNames.LEFT_FOREARM, [PointNames.LEFT_ELBOW,PointNames.LEFT_HAND]),
                       (LineNames.RIGHT_UPPER_ARM, [PointNames.TORSO_TOP,PointNames.RIGHT_ELBOW]),
                       (LineNames.RIGHT_FOREARM, [PointNames.RIGHT_ELBOW,PointNames.RIGHT_HAND]),
                       (LineNames.TORSO, [PointNames.TORSO_TOP,PointNames.TORSO_BOTTOM]),
                       (LineNames.LEFT_UPPER_LEG, [PointNames.TORSO_BOTTOM,PointNames.LEFT_KNEE]),
                       (LineNames.LEFT_LOWER_LEG, [PointNames.LEFT_KNEE,PointNames.LEFT_FOOT]),
                       (LineNames.RIGHT_UPPER_LEG, [PointNames.TORSO_BOTTOM,PointNames.RIGHT_KNEE]),
                       (LineNames.RIGHT_LOWER_LEG, [PointNames.RIGHT_KNEE,PointNames.RIGHT_FOOT])])

class Point:
    """A point of a stick figure
    
    gives the position of one end of a line on a stick figure.
    A point is drawn as a circle.  Points can be joined to create lines
    and joints"""
    
    slctdColor = (255,0,0)
    inactiveColor = (100,100,100)
    anchorColor = (0,0,255)
    radius = 5
    
    def __init__(self, pos):
        """Creates a new point
        
        pos: the position of the point"""
        self.pos = (float(pos[0]), float(pos[1]))
        self.color = Point.inactiveColor
        self.id = id(self)
        self.radius = Point.radius
        self.name = ''
    
    def get_top_left_and_bottom_right(self):
        return ((self.pos[0] - self.radius - 2, self.pos[1] - self.radius - 2), 
                (self.pos[0] + self.radius + 2, self.pos[1] + self.radius + 2))
    
    def get_enclosing_rect(self):
        return ((self.pos[0] - self.radius, self.pos[1] - self.radius), 
                (2*self.radius, 2*self.radius))
    
    def pixel_pos(self):
        """Determines the pixel coordinates of a point by rounding its x and y
        position to the nearest integer"""
        return(int(self.pos[0]), int(self.pos[1]))
    
    def draw(self, \
            surface, \
            color = None, \
            radius = -1, \
            pos_delta = None, \
            frame_image_reference_pos = None, \
            scale = 1):
        """Draws a point on a surface
        
        surface: the pygame surface to draw the point on"""
        if color == None:
            color = self.color
        
        if radius == -1:
            radius = self.radius
        
        position = self.pixel_pos()
        
        if frame_image_reference_pos != None:
            position = scale_image_point(self.pixel_pos(), \
                                        frame_image_reference_pos, \
                                        scale)
        
        if pos_delta != None:
            position = move_image_point(position, pos_delta)
        
        pygame.draw.circle(surface, \
                           color, \
                           position, \
                           int(radius))
    
    def covers(self, pos):
        """indicates if a point covers a coordinate
        
        pos: The coordinates to test"""
        containsIndicator = False
        if mathfuncs.distance(self.pos, pos) <= self.radius:
            containsIndicator = True
        
        return containsIndicator
        
class Line:
    """A line between to points"""
    
    slctdColor = (255,0,0)
    inactiveColor = (255,255,255)
    
    def __init__(self, point1, point2):
        """creates a new line
        
        point1: an endpoint for the line
        point2: an endpoint for the line"""
        self.endPoint1 = point1
        self.endPoint2 = point2
        self.points = [self.endPoint1, self.endPoint2]
        self.end_points = [self.endPoint1, self.endPoint2]
        self.thickness = 3
        Line.set_length(self)
        Line.set_max_length(self)
        self.id = id(self)
        self.color = Line.inactiveColor
    
    def draw(self, \
            surface, \
            color = None, \
            line_thickness = -1, \
            pos_delta = None, \
            frame_image_reference_pos = None, \
            scale = 1):
        """draws a line on a surface
        
        surface: the pygame surface to draw the line on"""
        if color == None:
            color = self.color
        
        if line_thickness == -1:
            line_thickness = self.thickness
        
        point1 = self.endPoint1.pos
        point2 = self.endPoint2.pos
        
        if frame_image_reference_pos != None:
            point1 = scale_image_point(self.endPoint1.pos, frame_image_reference_pos, scale)
            point2 = scale_image_point(self.endPoint2.pos, frame_image_reference_pos, scale)
        
        if pos_delta != None:
            point1 = move_image_point(point1, pos_delta)
            point2 = move_image_point(point2, pos_delta)
        
        pygame.draw.line(surface, \
                        color, \
                        point1, \
                        point2, \
                        line_thickness)
    
    def other_end_point(self, point):
        """returns the opposite end point if the given point is an end point.
        Otherwise it returns Nonde
        
        point: an end point of the line"""
        other_end_point = None
        
        if self.is_end_point(point.id):
            for end_point in self.end_points:
                if end_point != point:
                    other_end_point = end_point
                    break
                
        return other_end_point
    
    def other_named_end_point(self, point):
        """returns the opposite end point if the given point is an end point.
        Otherwise it returns None
        
        point: an end point of the line"""
        other_end_point = None
        
        if self.is_named_end_point(point.name):
            for end_point in self.end_points:
                if end_point != point:
                    other_end_point = end_point
                    break
                
        return other_end_point
    
    def is_end_point(self, pointId):
        """indicates if a point is an endpoint of a line
        
        pointId: id of point to match against endpoint ids"""
        isEndPointIndicator = False
        
        if ((self.endPoint1.id == pointId) \
        or (self.endPoint2.id == pointId)):
            isEndPointIndicator = True
            
        return isEndPointIndicator
    
    def is_named_end_point(self, point_name):
        """indicates if a point is an endpoint of a line
        
        point_name: name of point to match against endpoint names"""
        isEndPointIndicator = False
        
        if ((self.endPoint1.name == point_name) \
        or (self.endPoint2.name == point_name)):
            isEndPointIndicator = True
            
        return isEndPointIndicator
    
    def set_length(self):
        """sets the length of a line to the distance between its two
        endpoints"""
        self.length = mathfuncs.distance(self.endPoint1.pos, \
                                        self.endPoint2.pos)
    
    def set_max_length(self):
        """sets the maximum length of a line to the distance between its two
        endpoints"""
        self.max_length = mathfuncs.distance(self.endPoint1.pos, \
                                            self.endPoint2.pos)
    
    def pull(self, slctd_point):
        """Changes the position of one endpoint based off the new position of
        the selected endpoint so that the line has a new slope and the
        original length.
        
        slctd_point:  the point that has been moved"""
        pulled_point = self.endPoint1
        
        if slctd_point.id == pulled_point.id:
            pulled_point = self.endPoint2
        
        new_length = mathfuncs.distance(slctd_point.pos, pulled_point.pos)
        
        x_delta = slctd_point.pos[0] - pulled_point.pos[0]
        y_delta = slctd_point.pos[1] - pulled_point.pos[1]
        
        pulled_point.pos = (pulled_point.pos[0] \
                            + x_delta - \
                            ((x_delta / new_length) * self.length), \
                            pulled_point.pos[1] + \
                            y_delta - \
                            ((y_delta / new_length) * self.length))
    
    def get_top_left_and_bottom_right(self):
        end_point_1_corners = self.endPoint1.get_top_left_and_bottom_right()
        end_point_2_corners = self.endPoint2.get_top_left_and_bottom_right()
        
        #NOTE assumes that width of lines is not greater than radius of points
        top_left_x = min(end_point_1_corners[0][0],end_point_2_corners[0][0])
        top_left_y = min(end_point_1_corners[0][1],end_point_2_corners[0][1])
        bottom_right_x = max(end_point_1_corners[1][0],end_point_2_corners[1][0])
        bottom_right_y = max(end_point_1_corners[1][1],end_point_2_corners[1][1])
        
        return ((top_left_x, top_left_y), 
                (bottom_right_x, bottom_right_y))
    
    def get_reference_position(self):
        radius = (.5 * mathfuncs.distance(self.endPoint1.pos, \
                                          self.endPoint2.pos))
        pos = mathfuncs.midpoint(self.endPoint1.pos, self.endPoint2.pos)
        
        return (pos[0] - radius, pos[1] - radius)

class Circle(Line):
    """A circle with a radius that is one half the distance between two given
    points.  The two points lie opposite each other on the circle"""
    
    def __init__(self, point1, point2):
        """creates a new circle
        
        point1: a point that lies on the circle
        point2: a point that lies on the circle opposite of point1"""
        Line.__init__(self, point1, point2)
        self.diameter = 0
    
    def get_top_left_and_bottom_right(self):
        position = mathfuncs.midpoint(self.endPoint1.pos, self.endPoint2.pos)
        position = (int(position[0]), int(position[1]))
        radius = int(self.diameter / 2)
        point_radius = max(self.endPoint1.radius, self.endPoint2.radius)
        
        point1_top_left, point1_bottom_right = self.endPoint1.get_top_left_and_bottom_right()
        point2_top_left, point1_bottom_right = self.endPoint2.get_top_left_and_bottom_right()
        
        return (position[0] - radius - self.thickness - point_radius, position[1] - radius - self.thickness - point_radius), \
                (position[0] + radius + self.thickness + point_radius, position[1] + radius + self.thickness + point_radius)
    
    def center(self):
        return mathfuncs.midpoint(self.endPoint1.pos, self.endPoint2.pos)
    
    def set_diameter(self):
        """Sets the diameter of a circle to the distance between its two
        endpoints"""
        self.set_length()
    
    def draw(self, \
            surface, \
            color = None, \
            line_thickness = -1, \
            pos_delta = None, \
            frame_image_reference_pos = None, \
            scale = 1):
        """draws a circle on a surface
        
        surface: the pygame surface to draw the circle on"""
        if color == None:
            color = self.color
        
        radius = (.5 * mathfuncs.distance(self.endPoint1.pos, \
                                         self.endPoint2.pos))
        pos = mathfuncs.midpoint(self.endPoint1.pos, self.endPoint2.pos)
        
        if frame_image_reference_pos != None:
            pos = scale_image_point(pos, frame_image_reference_pos, scale)
            radius = radius * scale
        
        if pos_delta != None:
            pos = move_image_point(pos, pos_delta)
        
        if line_thickness == -1:
            line_thickness = self.thickness
        
        if radius < line_thickness:
            line_thickness = radius
        
        pygame.draw.circle(surface, \
                          color, \
                          (int(pos[0]), int(pos[1])), \
                          int(radius), \
                          int(line_thickness))

def coalesce_top_right_and_bottom_left(*args):
    """Finds the top left and bottom right of a list of top left and bottom right pairs"""
    
    if len(args) == 0:
        raise Exception
    
    top_left_x = args[0][0][0]
    top_left_y = args[0][0][1]
    bottom_right_x = args[0][1][0]
    bottom_right_y = args[0][1][1]
    
    for top_left_bottom_right in args:
        top_left, bottom_right = top_left_bottom_right
        
        top_left_x = min(top_left_x, top_left[0])
        top_left_y = min(top_left_y, top_left[1])
        bottom_right_x = max(bottom_right_x, bottom_right[0])
        bottom_right_y = max(bottom_right_y, bottom_right[1])
    
    return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)

def move_image_point(point_pos, pos_delta):
    """draws the frame image with the top left corner of the image at the
    given position
    
    point_pos: the current position of the point
    pos_delta: the change in position of the point"""
    
    new_x = point_pos[0] + pos_delta[0]
    new_y = point_pos[1] + pos_delta[1]
    
    return (int(new_x), int(new_y))

def scale_image_point(point_pos, frame_image_reference_pos, scale):
    """scales the position of the point relative to the top left coner of
    the window.
    
    point_pos: the current position of the point
    scale: floating number to multiply the distance to the top left corner
    of the window"""
    
    x_delta = point_pos[0] - frame_image_reference_pos[0]
    y_delta = point_pos[1] - frame_image_reference_pos[1]
    
    new_x = frame_image_reference_pos[0] + (scale * x_delta)
    new_y = frame_image_reference_pos[1] + (scale * y_delta)
    
    return (int(new_x), int(new_y))
