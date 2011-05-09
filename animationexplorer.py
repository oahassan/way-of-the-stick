import shelve
import copy
import math

import pygame
import button
import gamestate
import animation
import stick

class NewAnimationButton(button.Button):
    SLCTD_COLOR = (255,0,0)
    INACTIVE_COLOR = (255,255,255)
    _Width = 50
    _Height = 50
    _SymbolLineThickness = 2
    
    def __init__(self, pos):
        button.Button.__init__(self)
        self.width = NewAnimationButton._Width
        self.height = NewAnimationButton._Height
        self.pos = pos
        self.line_thickness = NewAnimationButton._SymbolLineThickness
        self.symbol.draw = NewAnimationButton.draw_symbol
    
    def draw_symbol(self, surface):
        """draws symbol of the add frame tool
        
        surface: the top left corner of the button"""
        vert_top = (self.center()[0], self.center()[1] - 6)
        vert_bottom = (self.center()[0], self.center()[1] + 6)
        hor_left = (self.center()[0] - 6, self.center()[1])
        hor_right = (self.center()[0] + 6, self.center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        vert_top, \
                        vert_bottom, \
                        NewAnimationButton._SymbolLineThickness)
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        hor_left, \
                        hor_right, \
                        NewAnimationButton._SymbolLineThickness)

_ANIMATION_DB_FILE_NM = "animations_wots.dat"
animations = {}
animation_thumbnails = {}
new_animation_button = NewAnimationButton((0,0))
_THUMBNAIL_PADDING = 25

slctd_animation = None
slctd_animation_thumbnail = None

exit_button = button.ExitButton()
exit_indicator = False

def get_animations():
    return_animations = {}
    animations = shelve.open(_ANIMATION_DB_FILE_NM, "c")
    
    for key, value in animations.iteritems():
        return_animations[key] = value
    
    animations.close()
    
    return return_animations

def save_animation(name, animation):
    """Saves an animation to the animation database.  If an animation with 
    the given name already exists it is overwritten.
    
    name: the name of the animation to add
    animation: the animation object to add"""
    animations = shelve.open(_ANIMATION_DB_FILE_NM, "c")
    
    animations[name] = animation
    animations.close()

def delete_animation(name, animation):
    """deletes an animation from the animation database"""
    animations = shelve.open(_ANIMATION_DB_FILE_NM, "c")
    
    del animations[name]
    
    animations.close()

def create_WOTS_animation():
    head_top_pos = (gamestate._WIDTH / 2, gamestate._HEIGHT / 3)
    torso_top_pos = (head_top_pos[0], head_top_pos[1] + 35)
    torso_bottom_pos = (torso_top_pos[0], torso_top_pos[1] + 60)
    left_elbow_pos = (torso_top_pos[0] - 20, torso_top_pos[1] + (20 * math.sqrt(3)))
    left_hand_pos = (left_elbow_pos[0], left_elbow_pos[1] + 40)
    right_elbow_pos = (torso_top_pos[0] + 20, torso_top_pos[1] + (20 * math.sqrt(3)))
    right_hand_pos = (right_elbow_pos[0], right_elbow_pos[1] + 40)
    left_knee_pos = (torso_bottom_pos[0] - 25, torso_bottom_pos[1] + (25 * math.sqrt(3)))
    left_foot_pos = (left_knee_pos[0], left_knee_pos[1] + 50)
    right_knee_pos = (torso_bottom_pos[0] + 25, torso_bottom_pos[1] + (25 * math.sqrt(3)))
    right_foot_pos = (right_knee_pos[0], right_knee_pos[1] + 50)
    
    WOTS_animation = animation.Animation()
    frame = WOTS_animation.frames[0]
    
    head_top_point = stick.Point(head_top_pos)
    head_top_point.name = stick.PointNames.HEAD_TOP
    WOTS_animation.point_names[stick.PointNames.HEAD_TOP] = head_top_point.id
    
    torso_top_point = stick.Point(torso_top_pos)
    torso_top_point.name = stick.PointNames.TORSO_TOP
    WOTS_animation.point_names[stick.PointNames.TORSO_TOP] = torso_top_point.id
    
    head = stick.Circle(head_top_point, torso_top_point)
    head.name = stick.LineNames.HEAD
    
    torso_bottom_point = stick.Point(torso_bottom_pos)
    torso_bottom_point.name = stick.PointNames.TORSO_BOTTOM
    WOTS_animation.point_names[stick.PointNames.TORSO_BOTTOM] = torso_bottom_point.id
    
    torso = stick.Line(torso_top_point, torso_bottom_point)
    torso.name = stick.LineNames.TORSO
    
    left_elbow_point = stick.Point(left_elbow_pos)
    left_elbow_point.name = stick.PointNames.LEFT_ELBOW
    WOTS_animation.point_names[stick.PointNames.LEFT_ELBOW] = left_elbow_point.id
    
    left_upper_arm = stick.Line(torso_top_point, left_elbow_point)
    left_upper_arm.name = stick.LineNames.LEFT_UPPER_ARM
    
    left_hand_point = stick.Point(left_hand_pos)
    left_hand_point.name = stick.PointNames.LEFT_HAND
    WOTS_animation.point_names[stick.PointNames.LEFT_HAND] = left_hand_point.id
    
    left_lower_arm = stick.Line(left_elbow_point, left_hand_point)
    left_lower_arm.name = stick.LineNames.LEFT_FOREARM
    
    right_elbow_point = stick.Point(right_elbow_pos)
    right_elbow_point.name = stick.PointNames.RIGHT_ELBOW
    WOTS_animation.point_names[stick.PointNames.RIGHT_ELBOW] = right_elbow_point.id
    
    right_upper_arm = stick.Line(torso_top_point, right_elbow_point)
    right_upper_arm.name = stick.LineNames.RIGHT_UPPER_ARM
    
    right_hand_point = stick.Point(right_hand_pos)
    right_hand_point.name = stick.PointNames.RIGHT_HAND
    WOTS_animation.point_names[stick.PointNames.RIGHT_HAND] = right_hand_point.id
    
    right_lower_arm = stick.Line(right_elbow_point, right_hand_point)
    right_lower_arm.name = stick.LineNames.RIGHT_FOREARM
    
    left_knee_point = stick.Point(left_knee_pos)
    left_knee_point.name = stick.PointNames.LEFT_KNEE
    WOTS_animation.point_names[stick.PointNames.LEFT_KNEE] = left_knee_point.id
    
    left_upper_leg = stick.Line(torso_bottom_point, left_knee_point)
    left_upper_leg.name = stick.LineNames.LEFT_UPPER_LEG
    
    left_foot_point = stick.Point(left_foot_pos)
    left_foot_point.name = stick.PointNames.LEFT_FOOT
    WOTS_animation.point_names[stick.PointNames.LEFT_FOOT] = left_foot_point.id
    
    left_lower_leg = stick.Line(left_knee_point, left_foot_point)
    left_lower_leg.name = stick.LineNames.LEFT_LOWER_LEG
    
    right_knee_point = stick.Point(right_knee_pos)
    right_knee_point.name = stick.PointNames.RIGHT_KNEE
    WOTS_animation.point_names[stick.PointNames.RIGHT_KNEE] = right_knee_point.id
    
    right_upper_leg = stick.Line(torso_bottom_point, right_knee_point)
    right_upper_leg.name = stick.LineNames.RIGHT_UPPER_LEG
    
    right_foot_point = stick.Point(right_foot_pos)
    right_foot_point.name = stick.PointNames.RIGHT_FOOT
    WOTS_animation.point_names[stick.PointNames.RIGHT_FOOT] = right_foot_point.id
    
    right_lower_leg = stick.Line(right_knee_point, right_foot_point)
    right_lower_leg.name = stick.LineNames.RIGHT_LOWER_LEG
    
    frame.add_circle(head)
    frame.add_line(torso)
    frame.add_line(left_upper_arm)
    frame.add_line(left_lower_arm)
    frame.add_line(right_upper_arm)
    frame.add_line(right_lower_arm)
    frame.add_line(left_upper_leg)
    frame.add_line(left_lower_leg)
    frame.add_line(right_upper_leg)
    frame.add_line(right_lower_leg)
    
    #set_point_radii(WOTS_animation)
    #set_line_thicknesses(WOTS_animation)
    
    return WOTS_animation

def set_point_radii(animation):
    for frame in animation.frames:
        for point in frame.point_dictionary.values():
            point.radius = 8

def set_line_thicknesses(animation):
    
    for circle in frame.circles():
        circle.thickness = 16
    
    for line in frame.lines():
        line.thickness = 16

def add_names_to_points_and_lines(animation):
    for frame in animation.frames:
        add_point_names_to_frame(animation.point_names, frame)
        add_line_names_to_frame(animation.point_names, frame)

def add_line_names_to_frame(name_to_points, frame):
    
    for circle in frame.circles():
        circle.name = stick.LineNames.HEAD
    
    for line in frame.lines():
        if (line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_TOP]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_BOTTOM]]):
            line.name = stick.LineNames.TORSO
            
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_TOP]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_ELBOW]]):
            line.name = stick.LineNames.RIGHT_UPPER_ARM
            
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_ELBOW]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_HAND]]):
            line.name = stick.LineNames.RIGHT_FOREARM
        
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_BOTTOM]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_KNEE]]):
            line.name = stick.LineNames.RIGHT_UPPER_LEG
            
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_KNEE]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.RIGHT_FOOT]]):
            line.name = stick.LineNames.RIGHT_LOWER_LEG
        
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_TOP]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_ELBOW]]):
            line.name = stick.LineNames.LEFT_UPPER_ARM
            
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_ELBOW]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_HAND]]):
            line.name = stick.LineNames.LEFT_FOREARM
        
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.TORSO_BOTTOM]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_KNEE]]):
            line.name = stick.LineNames.LEFT_UPPER_LEG
            
        elif (line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_KNEE]] and
        line in frame.point_to_lines[name_to_points[stick.PointNames.LEFT_FOOT]]):
            line.name = stick.LineNames.LEFT_LOWER_LEG

def add_point_names_to_frame(point_names_to_ids, frame):
    """fills in the name for each point in a frame"""
    for name, point_id in point_names_to_ids.iteritems():
        frame.point_dictionary[point_id].name = name
