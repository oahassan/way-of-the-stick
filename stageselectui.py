import copy

import pygame

import splash
import wotsuievents
import wotsuicontainers
import gamestate
import button
import physics
from wotsui import SelectableObjectBase, UIObjectBase
from enumerations import PlayerPositions, PlayerStates

class SelectStageBackground():
    def __init__(self, player_data):
        self.surface = pygame.Surface((gamestate._WIDTH, gamestate._HEIGHT))
        self.create_background(player_data)
    
    def create_background(self, player_data):
        player1_model = physics.Model((0,0))
        player2_model = physics.Model((0,0))
        
        self.set_point_positions(player_data, PlayerPositions.PLAYER1, player1_model)
        self.set_point_positions(player_data, PlayerPositions.PLAYER2, player2_model)
        
        splash.draw_model(player1_model, self.surface, player_data[0].color)
        splash.draw_model(player2_model, self.surface, player_data[1].color)
        
        self.surface.set_alpha(100)
    
    def set_point_positions(self, player_data, player_position, player_model):
        data_index = 0
        
        if player_position == PlayerPositions.PLAYER2:
            data_index = 1
            player_model.direction = physics.Orientations.FACING_LEFT
        
        data = player_data[data_index]
        animation = data.moveset.movement_animations[PlayerStates.STANDING]
        frame = copy.deepcopy(animation.get_widest_frame())
        
        frame.scale(3)
        
        if player_position == PlayerPositions.PLAYER2:
            frame.flip()
        
        point_id_position_dictionary = frame.build_pos_delta_dictionary(frame.get_reference_position())
        point_name_position_dictionary = dict([
            (name, point_id_position_dictionary[id]) 
            for name, id in animation.point_names.iteritems()
        ])
        
        player_model.set_absolute_point_positions(point_name_position_dictionary)
        
        if player_position == PlayerPositions.PLAYER1:
            x_position = 200 - player_model.width
            player_model.move_model(
                (x_position, 
                (gamestate._HEIGHT / 2) - (player_model.height / 2))
            )
        else:
            x_position = gamestate._WIDTH - 200
            player_model.move_model(
                (x_position, 
                (gamestate._HEIGHT / 2) - (player_model.height / 2))
            )

class StartMatchLabel():
    
    def __init__(self):
        self.text = button.Label(
            (0,0), 
            "Press Enter to Start Match", 
            (255,255,255), 
            button.FONT_SIZES[8])
        self.width = gamestate._WIDTH
        self.height = self.text.height + 40
        self.surface = pygame.Surface((self.width, self.height))
        self.position = (0, (gamestate._HEIGHT / 2) - (self.height / 2))
        self.text.set_position(
            ((gamestate._WIDTH / 2) - (self.text.width / 2),
            (gamestate._HEIGHT / 2) - (self.text.height / 2))
        )
        self.alpha = 5
    
    def draw(self, surface):
        self.surface.fill((0,0,0))
        
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
        self.image_height = 225
        self.image_width = 300
        self.outline_width = 4
        self.label_padding = 5
        self.label = button.Label(
            (self.position[0],
            self.position[1] + self.image_height + self.outline_width + self.label_padding),
            self.stage.name, 
            (255,255,255), 
            button.FONT_SIZES[6]
        )
        self.height = self.image_height + self.outline_width + self.label_padding + self.label.height
        self.width = self.image_width + self.outline_width
        self.scale = self.get_scale()
        self.image = pygame.transform.scale(
            self.stage.background_image,
            (min(int(self.scale * stage.width), self.image_width),
            min(int(self.scale * stage.height), self.image_height))
        )
        self.fixed_dimensions = True
        
        self.add_child(self.label)
    
    def get_scale(self):
        stage = self.stage
        if stage.height < stage.width:
            return self.image_width / float(stage.width)
        else:
            return self.image_height / float(stage.height)
    
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
        self.width = 310
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
        self.fade_top = None
        self.fade_bottom = None
        self.create_fades()
    
    def layout_thumbnails(self):
        next_position = [self.position[0], self.position[1]]
        self.thumbnails[0].set_position(next_position)
        
        for i in xrange(1,len(self.thumbnails)):
            next_position = [
                next_position[0], 
                next_position[1] + self.thumbnails[i-1].height + self.thumbnail_padding
            ]
            self.thumbnails[i].set_position(next_position)
    
    def create_fades(self):
        self.fade_top = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        height = self.fade_top.get_height()
        height_interval = 5
        alpha_count = 20
        alpha = 50
        alpha_interval = (255 - 50) / alpha_count
        
        for i in xrange(1,31):
            pygame.draw.rect(
                self.fade_top,
                (0,0,0,alpha),
                ((0,0), (self.fade_top.get_width(), height))
            )
            
            if i % 6 == 0:
                height_interval -= 1
            
            alpha = min(255, alpha + alpha_interval)
            height -= height_interval
        self.fade_bottom = pygame.transform.rotate(self.fade_top, 180)
    
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
        
        container_surface.blit(self.fade_top, (0,0))
        container_surface.blit(
            self.fade_bottom, 
            (0, self.height - self.fade_bottom.get_height())
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
        
        if pygame.K_UP in wotsuievents.keys_pressed:
            if self.selected_thumbnail != None:
                new_selected_index = self.thumbnails.index(self.selected_thumbnail) - 1
                if new_selected_index == -1:
                    new_selected_index = len(self.thumbnails) - 1
                
                self.selected_thumbnail.handle_deselected()
                self.thumbnails[new_selected_index].handle_selected()
                self.selected_thumbnail = self.thumbnails[new_selected_index]
            else:
                new_selected_index = 0
                self.thumbnails[new_selected_index].handle_selected()
                self.selected_thumbnail = self.thumbnails[new_selected_index]
        
        if pygame.K_DOWN in wotsuievents.keys_pressed:
            if self.selected_thumbnail != None:
                new_selected_index = self.thumbnails.index(self.selected_thumbnail) + 1
                if new_selected_index == len(self.thumbnails):
                    new_selected_index = 0
                
                self.selected_thumbnail.handle_deselected()
                self.thumbnails[new_selected_index].handle_selected()
                self.selected_thumbnail = self.thumbnails[new_selected_index]
            else:
                new_selected_index = 0
                self.thumbnails[new_selected_index].handle_selected()
                self.selected_thumbnail = self.thumbnails[new_selected_index]
        
        if self.selected_thumbnail_is_not_in_place():
            self.shift_thumbnails()
