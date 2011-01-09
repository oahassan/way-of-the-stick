import copy
import functools
import pygame

import wotsui
import wotsuicontainers
import wotsuievents
import button

import movesetdata
import player

class ImportAlertBox(wotsuicontainers.AlertBox):
    
    def __init__(self):
        wotsuicontainers.AlertBox.__init__(
            self,
            border_color = (255,255,255),
            border_padding = 10,
            border_thickness = 5,
            text = 'Importing Movesets...',
            width = 300,
            position = (0,0),
            text_color = (255,255,255),
            background_color = (0,0,0),
            font_size = 50
        )
        position = (
            400 - self.width,
            300 - self.height
        )
        self.set_position(position)

class MovesetActionLabel(button.Label, wotsui.SelectableObjectBase):
    def __init__(self, position, text):
        wotsui.SelectableObjectBase.__init__(self)
        button.Label.__init__(self, position, text, self.active_color, 25)
    
    def handle_selected(self):
        self.text_color = self.selected_color
        self.selected = True
    
    def handle_deselected(self):
        self.text_color = self.active_color
        self.selected = False
    
    def activate(self):
        self.text_color = self.active_color
        self.active = True
    
    def inactivate(self):
        self.text_color = self.inactive_color
        self.active = False
        self.selected = False

class MovesetSelectContainer(wotsuicontainers.ScrollableContainer):
    def __init__(self, position, moveset_container_height, moveset_container_width, title_text, movesets):
        wotsuicontainers.ScrollableContainer.__init__(self)
        
        self.selected_moveset = None
        self.position = position
        self.frame = None
        self.title = button.Label(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        viewable_area_position = (position[0], position[1] + self.height + 10)
        
        self.set_viewable_area(viewable_area_position, \
                               max(self.height, moveset_container_height - wotsuicontainers.SCROLL_BUTTON_HEIGHT), \
                               max(self.width, moveset_container_width - wotsuicontainers.SCROLL_BUTTON_WIDTH))
        
        self.thumbnails = []
        self.load_movesets(movesets)
        
        self.init_vertical_scrollbar()
        self.init_horizontal_scrollbar()
    
    def load_movesets(self, movesets):
        self.remove_children(self.thumbnails, True)
        self.thumbnails = []
        
        if len(movesets) > 0:
            moveset_thumbnails = []
            
            for moveset in movesets:
                moveset_thumbnails.append(MovesetThumbnail(moveset))
            
            self.thumbnails.extend(moveset_thumbnails)
            self.layout_thumbnails()
            self.add_children(moveset_thumbnails, True)
    
    def layout_thumbnails(self):
        viewable_area_position = self.viewable_area.position
        
        current_position = (viewable_area_position[0] + 10, \
                            viewable_area_position[1] + self.title.height + 10)
        thumbnails = self.thumbnails
        
        thumbnails[0].set_position(current_position)
        
        for i in range(1,len(thumbnails)):
            previous_thumbnail = thumbnails[i - 1]
            x_position = previous_thumbnail.position[0]
            y_position = previous_thumbnail.position[1]
            
            if self.width < 200:
                y_position += previous_thumbnail.height + 10
                x_position = viewable_area_position[0] + 10
            else:
                if i % int(self.width / 200) == 0:
                    y_position += previous_thumbnail.height + 10
                    x_position = viewable_area_position[0] + 10
                else:
                    x_position += 150
            
            current_position = (x_position, \
                                y_position)
            thumbnails[i].set_position(current_position)
    
    def handle_events(self):
        wotsuicontainers.ScrollableContainer.handle_events(self)
        
        if self.viewable_area.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                for thumbnail in self.thumbnails:
                    if thumbnail.contains(wotsuievents.mouse_pos):
                        if thumbnail.selected:
                            thumbnail.handle_deselected()
                            self.selected_moveset = None
                        else:
                            for other_thumbnail in self.thumbnails:
                                if other_thumbnail.selected:
                                    other_thumbnail.handle_deselected()
                            
                            thumbnail.handle_selected()
                            self.selected_moveset = thumbnail.moveset

class MovesetThumbnail(button.Button):
    _THUMBNAIL_HEIGHT = 80
    
    def __init__(self, moveset):
        button.Button.__init__(self)
        
        self.moveset = moveset
        self.thumbnail_animation = None
        self.frame = None
        self.position = (0,0)
        self.name_label = None
        self.height = 0
        self.width = 0
        self.fixed_dimensions = False
        self.name_label = None
        
        self.set_label(moveset.name)
        
        if moveset.has_movement_animation(player.PlayerStates.STANDING):
            self.set_animation(moveset.movement_animations[player.PlayerStates.STANDING])
    
    def handle_selected(self):
        button.Button.handle_selected(self)
        
        self.name_label.text_color = self.selected_color
    
    def handle_deselected(self):
        button.Button.handle_deselected(self)
        
        self.name_label.text_color = self.active_color
    
    def set_animation(self, animation):
        thumbnail_animation = copy.deepcopy(animation)
        thumbnail_animation.set_animation_height(MovesetThumbnail._THUMBNAIL_HEIGHT, 170)
        self.thumbnail_animation = thumbnail_animation
        self.frame = thumbnail_animation.get_widest_frame()
        self.width = max(self.width, thumbnail_animation.get_widest_frame().image_width())
    
    def set_label(self, text):
        text_pos = (self.position[0], \
                    self.position[1] + MovesetThumbnail._THUMBNAIL_HEIGHT + 5)
        name_label = button.Label(text_pos, text, self.color, 15)
        self.name_label = name_label
        self.add_child(name_label)
    
    def draw(self, surface):
        if self.thumbnail_animation != None:
            if self.contains(wotsuievents.mouse_pos):
                self.play_animation(self, surface, self.draw_current_frame)
            else:
                self.draw_current_frame(surface)
        else:
            wotsui.UIObjectBase.draw(self, surface)
    
    def draw_current_frame(self, surface):
        """draws the frame thumbnail"""
        
        frame_image_pos = self.frame.get_reference_position()
        temp_surface = pygame.Surface((self.frame.image_width(), \
                                       self.frame.image_height()))
        
        pos_delta = (0 - frame_image_pos[0], \
                     0 - frame_image_pos[1])
        
        self.frame.draw(temp_surface, \
                        self.color, \
                        1, \
                        pos_delta, \
                        point_radius = 1, \
                        line_thickness = 2)
        
        surface.blit(temp_surface, self.position)
        
        wotsui.UIObjectBase.draw(self, surface)
    
    def draw_relative(self, surface, position):
        if self.thumbnail_animation != None:
            if self.contains(wotsuievents.mouse_pos):
                partial_draw_relative = functools.partial(self.draw_current_frame_relative, \
                                                          reference_position=position)
                self.play_animation(surface, partial_draw_relative)
            else:
                self.draw_current_frame_relative(surface, position)
        else:
            wotsui.UIObjectBase.draw_relative(self, surface, position)
    
    def draw_current_frame_relative(self, surface, reference_position):
        
        frame_image_pos = self.frame.get_reference_position()
        temp_surface = pygame.Surface((self.frame.image_width(), \
                                       self.frame.image_height()))
        
        pos_delta = (0 - frame_image_pos[0], \
                     0 - frame_image_pos[1])
        
        self.frame.draw(temp_surface, \
                        self.color, \
                        1, \
                        pos_delta, \
                        point_radius = 1, \
                        line_thickness = 2)
        
        relative_position = self.get_relative_position(reference_position)
        
        surface.blit(temp_surface, relative_position)
        
        wotsui.UIObjectBase.draw_relative(self, surface, reference_position)
    
    def play_animation(self, surface, draw_func):
        """plays the animation"""
        frame_index = self.thumbnail_animation.frame_index
        
        self.frame = self.thumbnail_animation.frames[frame_index]
        draw_func(surface)
        
        if frame_index < len(self.thumbnail_animation.frames) - 1:
            self.thumbnail_animation.frame_index += 1
        else:
            self.thumbnail_animation.frame_index = 0
