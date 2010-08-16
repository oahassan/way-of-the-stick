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
    global animation_thumbnails
    
    animations = shelve.open(_ANIMATION_DB_FILE_NM, "c")
    
    if name in animation_thumbnails.keys():
        animation_thumbnails[name].animation = animation
    
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
    WOTS_animation.point_names[stick.PointNames.HEAD_TOP] = head_top_point.id
    
    torso_top_point = stick.Point(torso_top_pos)
    WOTS_animation.point_names[stick.PointNames.TORSO_TOP] = torso_top_point.id
    
    head = stick.Circle(head_top_point, torso_top_point)
    
    torso_bottom_point = stick.Point(torso_bottom_pos)
    WOTS_animation.point_names[stick.PointNames.TORSO_BOTTOM] = torso_bottom_point.id
    
    torso = stick.Line(torso_top_point, torso_bottom_point)
    
    left_elbow_point = stick.Point(left_elbow_pos)
    WOTS_animation.point_names[stick.PointNames.LEFT_ELBOW] = left_elbow_point.id
    
    left_upper_arm = stick.Line(torso_top_point, left_elbow_point)
    
    left_hand_point = stick.Point(left_hand_pos)
    WOTS_animation.point_names[stick.PointNames.LEFT_HAND] = left_hand_point.id
    
    left_lower_arm = stick.Line(left_elbow_point, left_hand_point)
    
    right_elbow_point = stick.Point(right_elbow_pos)
    WOTS_animation.point_names[stick.PointNames.RIGHT_ELBOW] = right_elbow_point.id
    
    right_upper_arm = stick.Line(torso_top_point, right_elbow_point)
    
    right_hand_point = stick.Point(right_hand_pos)
    WOTS_animation.point_names[stick.PointNames.RIGHT_HAND] = right_hand_point.id
    
    right_lower_arm = stick.Line(right_elbow_point, right_hand_point)
    
    left_knee_point = stick.Point(left_knee_pos)
    WOTS_animation.point_names[stick.PointNames.LEFT_KNEE] = left_knee_point.id
    
    left_upper_leg = stick.Line(torso_bottom_point, left_knee_point)
    
    left_foot_point = stick.Point(left_foot_pos)
    WOTS_animation.point_names[stick.PointNames.LEFT_FOOT] = left_foot_point.id
    
    left_lower_leg = stick.Line(left_knee_point, left_foot_point)
    
    right_knee_point = stick.Point(right_knee_pos)
    WOTS_animation.point_names[stick.PointNames.RIGHT_KNEE] = right_knee_point.id
    
    right_upper_leg = stick.Line(torso_bottom_point, right_knee_point)
    
    right_foot_point = stick.Point(right_foot_pos)
    WOTS_animation.point_names[stick.PointNames.RIGHT_FOOT] = right_foot_point.id
    
    right_lower_leg = stick.Line(right_knee_point, right_foot_point)
    
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
    
    return WOTS_animation

class AnimationNavigator():
    BUTTON_PADDING = 10
    
    def __init__(self):
        self.animation_thumbnails = []
        self.visible_thumbnails = []
        self.slctd_scroll_button = None
        self.scroll_left_button = None
        self.scroll_right_button = None
        self.slctd_animation = None
        self.edit_animation = None
        self.slctd_animation_thumbnail = None
        self.new_animation_button = None
        self.scroll_buttons = []
        self.height = 0
        self.width = 0
        self.pos = None
        self.thumbnail_index = 0
        self.gamestate_mode = None
    
    def top_left(self):
        return self.pos
    
    def top_right(self):
        return (pos[0] + self.width, self.pos[1])
    
    def bottom_left(self):
        return (self.pos[0], self.pos[1] + self.height())
    
    def bottom_right(self):
        return (self.pos[0] + self.width, self.pos[1] + self.height)
    
    def contains(self, pos):
        """Indicates if a position lies within the area of a tool's
        button
        
        pos:  position to test"""
        coversPositionIndicator = False
        
        if ((self.top_left()[0] <= pos[0]) \
        and (self.top_left()[1] <= pos[1]) \
        and (self.bottom_right()[0] >= pos[0]) \
        and (self.bottom_right()[1] >= pos[1])):
            coversPositionIndicator = True
        
        return coversPositionIndicator
    
    def load_data(self, pos, height, width, animations, gamestate_mode):
        self.pos = pos
        self.height = height
        self.width = width
        self.gamestate_mode = gamestate_mode
        
        self.scroll_left_button = AnimationNavigator.LeftScrollButton(pos, self)
        self.scroll_buttons.append(self.scroll_left_button)
        
        scroll_right_pos = (pos[0] + width - 40, pos[1])
        self.scroll_right_button = AnimationNavigator.RightScrollButton(scroll_right_pos, self)
        self.scroll_buttons.append(self.scroll_right_button)
        
        new_animation_button_position = (pos[0] + width - 40 - \
                                         AnimationNavigator.BUTTON_PADDING - \
                                         NewAnimationButton._Width, pos[1])
        self.new_animation_button = NewAnimationButton(new_animation_button_position)
        
        for animation in animations:
            self.animation_thumbnails.append(AnimationThumbnail((0,0), animation))
        
        self.set_visible_thumbnails()
    
    def handle_events(self):
        
        if pygame.MOUSEBUTTONDOWN in gamestate.event_types:
            if self.new_animation_button.contains(gamestate.mouse_pos):
                self.slctd_animation = create_WOTS_animation()
                self.new_animation_button.color = button.Button._SlctdColor
            else:
                for thumbnail in self.visible_thumbnails:
                    if thumbnail.contains(gamestate.mouse_pos):
                        if self.slctd_animation == None:
                            thumbnail.color = AnimationThumbnail._INACTIVE_COLOR
                            self.slctd_animation_thumbnail = thumbnail
                            thumbnail.color = AnimationThumbnail._SLCTD_COLOR
                            self.slctd_animation = thumbnail.animation
                        else:
                            if thumbnail == self.slctd_animation_thumbnail:
                                self.edit_animation = self.slctd_animation
                            else:
                                if self.slctd_animation_thumbnail != None:
                                    self.slctd_animation_thumbnail.color = AnimationThumbnail._INACTIVE_COLOR
                                self.slctd_animation_thumbnail = thumbnail
                                thumbnail.color = AnimationThumbnail._SLCTD_COLOR
                                self.slctd_animation = thumbnail.animation
                                self.edit_animation = None
                
                for scroll_button in self.scroll_buttons:
                    if scroll_button.contains(gamestate.mouse_pos):
                        self.slctd_scroll_button = scroll_button
                        scroll_button.handle_selected()
        elif pygame.MOUSEBUTTONUP in gamestate.event_types:
            if ((self.slctd_animation != None) and
                (self.new_animation_button.contains(gamestate.mouse_pos))):
                frameeditor.init(self.slctd_animation, self.gamestate_mode)
                gamestate.mode = gamestate.Modes.FRAMEEDITOR
            
            if ((self.edit_animation != None) and
                (self.slctd_animation_thumbnail.contains(gamestate.mouse_pos))):
                frameeditor.init(copy.deepcopy(self.edit_animation), self.gamestate_mode)
                gamestate.mode = gamestate.Modes.FRAMEEDITOR
            
            if self.slctd_scroll_button != None:
                if self.slctd_scroll_button.contains(gamestate.mouse_pos):
                    self.slctd_scroll_button.scroll()
                
                self.slctd_scroll_button.handle_deselected()
            
            self.new_animation_button.color = button.Button._InactiveColor
    
    def draw(self, surface, mouse_pos):
        for scroll_button in self.scroll_buttons:
            scroll_button.draw(scroll_button, surface)
        
        self.draw_animation_thumbnails(surface, gamestate.mouse_pos)
        self.new_animation_button.draw(surface)
    
    def draw_animation_thumbnails(self, surface, mouse_pos):
        """draws the thumbnails of the animations in the database"""
        for thumbnail in self.visible_thumbnails:
            if thumbnail.contains(mouse_pos):
                thumbnail.play_animation(surface)
            else:
                thumbnail.frame = thumbnail.thumbnail_animation.get_middle_frame()
                thumbnail.draw(surface)
    
    def set_visible_thumbnails(self):
        self.visible_thumbnails = []
        
        start_pos = (self.pos[0] + self.scroll_left_button.width + AnimationNavigator.BUTTON_PADDING, \
                     self.pos[1])
        usable_width = (self.width - (2 * self.scroll_left_button.width) - \
                       (3 * AnimationNavigator.BUTTON_PADDING) - self.new_animation_button.width)
        
        thumbnail_index = self.thumbnail_index
        next_pos = start_pos
        
        while usable_width > 0:
            if thumbnail_index == len(self.animation_thumbnails):
                break
            elif usable_width < self.animation_thumbnails[thumbnail_index].width() + AnimationNavigator.BUTTON_PADDING:
                break
            else:
                thumbnail = self.animation_thumbnails[thumbnail_index]
                self.visible_thumbnails.append(thumbnail)
                thumbnail.pos = next_pos
                next_pos = (next_pos[0] + thumbnail.width() + AnimationNavigator.BUTTON_PADDING, \
                            next_pos[1])
                usable_width -= thumbnail.width() + AnimationNavigator.BUTTON_PADDING
                thumbnail_index += 1
    
    class RightScrollButton(button.Button):
        def __init__(self, pos, animation_navigator):
            button.Button.__init__(self)
            self.pos = pos
            self.width = 40
            self.height = animation_navigator.height
            self.draw = AnimationNavigator.RightScrollButton.draw_symbol
            self.animation_navigator = animation_navigator
        
        def draw_symbol(self, surface):
            point1 = (self.pos[0] + 40, self.pos[1] + 40)
            point2 = (self.pos[0], self.pos[1] + 20)
            point3 = (self.pos[0], self.pos[1] + 60)
            
            pygame.draw.polygon(surface, self.color, [point1,point2,point3])
        
        def scroll(self):
            thumbnail_index = self.animation_navigator.thumbnail_index
            thumbnails = self.animation_navigator.animation_thumbnails
            
            if thumbnail_index < len(thumbnails) - 1:
                needed_width = thumbnails[thumbnail_index + 1].width()
                
                while needed_width > 0:
                    needed_width -= thumbnails[thumbnail_index].width() + AnimationNavigator.BUTTON_PADDING
                    thumbnail_index += 1
                
                self.animation_navigator.thumbnail_index = thumbnail_index
                self.animation_navigator.set_visible_thumbnails()
    
    class LeftScrollButton(button.Button):
        def __init__(self, pos, animation_navigator):
            button.Button.__init__(self)
            self.pos = pos
            self.width = 40
            self.height = animation_navigator.height
            self.draw = AnimationNavigator.LeftScrollButton.draw_symbol
            self.animation_navigator = animation_navigator
        
        def draw_symbol(self, surface):
            point1 = (self.pos[0], self.pos[1] + 40)
            point2 = (self.pos[0] + 40, self.pos[1] + 20)
            point3 = (self.pos[0] + 40, self.pos[1] + 60)
            
            pygame.draw.polygon(surface, self.color, [point1,point2,point3])
        
        def scroll(self):
            animation_navigator = self.animation_navigator
            
            if animation_navigator.thumbnail_index > 0:
                animation_navigator.thumbnail_index -= 1
                self.animation_navigator.set_visible_thumbnails()