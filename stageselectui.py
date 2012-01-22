import pygame

import wotsuievents
import wotsuicontainers
import gamestate
import button
from wotsui import SelectableObjectBase, UIObjectBase

class StartMatchLabel():
    
    def __init__(self):
        self.text = button.Label((0,0), "Press Enter to Start Match", (255,255,255), 40)
        self.width = gamestate._WIDTH
        self.height = self.text.height + 40
        self.surface = pygame.Surface((self.width, self.height))
        self.position = (0, (gamestate._HEIGHT / 2) - (self.height / 2))
        self.text.set_position(
            ((gamestate._WIDTH / 2) - (self.text.width / 2),
            (gamestate._HEIGHT / 2) - (self.text.height / 2))
        )
        self.alpha = 0
    
    def draw(self, surface):
        
        self.text.draw_relative(self.surface, self.position)
        pygame.draw.line(self.surface, (255,255,255), (0,5), (self.width, 5), 10)
        pygame.draw.line(self.surface, (255,255,255), (0, self.height - 5), (self.width, self.height - 5), 10)
        
        if self.alpha < 255:
            self.alpha += min(12, 255 - self.alpha)
        
        self.surface.set_alpha(self.alpha)
        
        surface.blit(self.surface, self.position)
    
    def hide(self):
        self.alpha = 0

class StageThumbnail(SelectableObjectBase):
    def __init__(self, stage):
        SelectableObjectBase.__init__(self)
        self.stage = stage
        self.image_height = 133
        self.image_width = 200
        self.outline_width = 4
        self.label_padding = 5
        self.label = button.Label(
            (self.position[0],
            self.position[1] + self.image_height + self.outline_width + self.label_padding),
            self.stage.name, 
            (255,255,255), 
            14
        )
        self.height = self.image_height + self.outline_width + self.label_padding + self.label.height
        self.width = self.image_width + self.outline_width
        self.scale = self.get_scale()
        self.image = pygame.transform.scale(
            self.stage.background_image,
            (int(self.scale * stage.width),
            int(self.scale * stage.height))
        )
        self.fixed_dimensions = True
        
        self.add_child(self.label)
    
    #def set_position(self, position):
    #    SelectableObjectBase.set_position(self, position)
    #    self.label.set_position(
    #        (self.position[0], 
    #        self.position[1] + self.image_height + self.outline_width + self.label_padding)
    #    )
    
    #def shift(self, x_delta, y_delta):
    #    SelectableObjectBase.shift(self, x_delta, y_delta)
    #    self.label.shift(x_delta, y_delta)
    
    def get_scale(self):
        stage = self.stage
        if stage.height > stage.width:
            return self.image_width / float(stage.width)
        else:
            return self.image_height / float(stage.height)
    
    def get_image(self):
        return 
    
    def draw(self):
        half_outline_width = self.outline_width / 2
        
        temp_surface = pygame.Surface(
            (self.width, self.height)
        )
        rect = temp_surface.blit(
            self.image, 
            (half_outline_width, half_outline_width)
        )
        self.label.draw_relative(temp_surface, self.position)

        pygame.draw.circle(
            temp_surface,
            self.color,
            rect.topleft,
            half_outline_width
        )
        pygame.draw.circle(
            temp_surface,
            self.color,
            rect.topright,
            half_outline_width
        )
        pygame.draw.circle(
            temp_surface,
            self.color,
            rect.bottomleft,
            half_outline_width
        )
        pygame.draw.circle(
            temp_surface,
            self.color,
            rect.bottomright,
            half_outline_width
        )
        
        pygame.draw.rect(
            temp_surface,
            self.color,
            ((half_outline_width, half_outline_width),
            (self.image.get_width(), self.image.get_height())),
            self.outline_width
        )
        
        return (self.position, temp_surface)

class StageSelector(UIObjectBase):
    def __init__(self, stages, position):
        UIObjectBase.__init__(self)
        self.set_position(position)
        self.height = 500
        self.width = 210
        self.stages = stages
        self.thumbnails = [StageThumbnail(stage) for stage in stages]
        self.thumbnail_padding = 20
        self.surface = pygame.Surface((self.width, self.height))
        self.selected_thumbnail = None
        self.selected_thumbnail_target_position = [
            self.position[0],
            self.position[1] + (.5 * self.height) - (.5 * self.thumbnails[0].height)
        ]
        self.layout_thumbnails()
    
    def layout_thumbnails(self):
        next_position = [self.position[0], self.position[1]]
        self.thumbnails[0].set_position(next_position)
        
        for i in xrange(1,len(self.thumbnails)):
            next_position = [
                next_position[0], 
                next_position[1] + self.thumbnails[i-1].height + self.thumbnail_padding
            ]
            self.thumbnails[i].set_position(next_position)
    
    def draw(self, surface):
        self.surface.fill((0,0,0))
        container_surface = self.surface
        
        for thumbnail in self.thumbnails:
            thumbnail_position, thumbnail_surface = thumbnail.draw()
            #print(self.get_relative_position(thumbnail_position))
            container_surface.blit(
                thumbnail_surface, 
                thumbnail.get_relative_position(self.position)
            )
        
        #self.draw_scroll_button(self.left_scroll_button, container_surface)
        #self.draw_scroll_button(self.right_scroll_button, container_surface)
        
        surface.blit(container_surface, self.position)
    
    def shift_thumbnails(self):
        direction = 1
        
        if self.selected_thumbnail_target_position[1] < self.selected_thumbnail.position[1]:
            direction = -1
        
        shift_distance = min(
            abs(self.selected_thumbnail_target_position[1] - self.selected_thumbnail.position[1]),
            10
        )
        
        for thumbnail in self.thumbnails:
            thumbnail.shift(0, shift_distance * direction)
    
    def selected_thumbnail_is_not_in_place(self):
        return (self.selected_thumbnail != None and 
        self.selected_thumbnail.position[1] != self.selected_thumbnail_target_position[1])
    
    def handle_events(self):
        if self.contains(wotsuievents.mouse_pos):
            if wotsuievents.mousebutton_pressed():
                for thumbnail in self.thumbnails:
                    if thumbnail.contains(wotsuievents.mouse_pos):
                        if self.selected_thumbnail != None:
                            self.selected_thumbnail.handle_deselected()
                        
                        thumbnail.handle_selected()
                        self.selected_thumbnail = thumbnail
        
        if self.selected_thumbnail_is_not_in_place():
            self.shift_thumbnails()
