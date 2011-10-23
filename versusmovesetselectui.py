import pygame

import movesetdata
import gamestate

import button
import wotsuievents
from wotsui import UIObjectBase
from wotsuicontainers import Slider, ScrollButton, SCROLL_LEFT, SCROLL_RIGHT
from movesetselectui import MovesetLoader, MovesetThumbnail

class DifficultyLabel(button.SelectableLabel):  
    def __init__(self, text, difficulty):
        button.SelectableLabel.__init__(self, (0,0), text, 20)
        self.difficulty = difficulty

class MovesetSelector(UIObjectBase, MovesetLoader):
    WIDTH = 300
    HEIGHT = 120
    
    def __init__(self, position, movesets):
        
        self.set_layout_data(position, MovesetSelector.HEIGHT, MovesetSelector.WIDTH)
        self.selected_thumbnail_index = 0
        self.fixed_dimensions = True
        
        MovesetLoader.__init__(self, movesets)
        self.selected_moveset = self.thumbnails[self.selected_thumbnail_index].moveset
        self.left_scroll_button = ScrollButton(SCROLL_LEFT)
        self.right_scroll_button = ScrollButton(SCROLL_RIGHT)
        self.set_scroll_button_layout_data()
        self.scroll_increment = 10
    
    def load_movesets(self, movesets):
        self.thumbnails = []
        
        if len(movesets) > 0:
            moveset_thumbnails = []
            
            for moveset in movesets:
                moveset_thumbnails.append(MovesetThumbnail(moveset))
            
            self.thumbnails.extend(moveset_thumbnails)
            self.layout_thumbnails()
    
    def set_scroll_button_layout_data(self):
        self.left_scroll_button.set_layout_data((0,0))
        left_button_position = (
            self.position[0],
            self.center()[1] - (self.left_scroll_button.height / 2)
        )
        self.left_scroll_button.set_layout_data(left_button_position)
        
        self.right_scroll_button.set_layout_data((0,0))
        right_button_position = (
            self.position[0] + self.width - self.right_scroll_button.width,
            self.center()[1] - (self.right_scroll_button.height / 2)
        )
        self.right_scroll_button.set_layout_data(right_button_position)
    
    def draw(self, surface):
        
        container_surface = pygame.Surface((self.width, self.height))
        
        for thumbnail in self.thumbnails:
            thumbnail.draw_relative(container_surface, self.position)
        
        self.draw_scroll_button(self.left_scroll_button, container_surface)
        self.draw_scroll_button(self.right_scroll_button, container_surface)
        
        surface.blit(container_surface, self.position)
    
    def draw_scroll_button(self, scroll_button, container_surface):
        scroll_button_surface = pygame.Surface((scroll_button.width, self.height))
        scroll_button_surface_position = (
            scroll_button.position[0],
            self.position[1]
        )
        scroll_button.draw_relative(
            scroll_button_surface,
            scroll_button_surface_position
        )
        relative_position = scroll_button.get_relative_position(self.position)
        
        container_surface.blit(
            scroll_button_surface,
            (relative_position[0], 0)
        )
    
    def get_selected_thumbnail_position(self):
        selected_thumbnail = self.thumbnails[self.selected_thumbnail_index]
        
        return (
            self.center()[0] - (selected_thumbnail.width / 2), 
            self.position[1]
        )
    
    def layout_thumbnails(self):
        thumbnails = self.thumbnails
        selected_thumbnail = thumbnails[self.selected_thumbnail_index]
        
        selected_thumbnail_position = self.get_selected_thumbnail_position()

        selected_thumbnail.set_position(selected_thumbnail_position)
        
        previous_position = selected_thumbnail_position
        for i in range(self.selected_thumbnail_index - 1, -1, -1):
            current_thumbnail = thumbnails[i]
            x_position = previous_position[0] - current_thumbnail.width - 10
            y_position = previous
            current_thumbnail.set_position((x_position, y_position))
            
            previous_position = (x_position, y_position)
        
        previous_thumbnail = selected_thumbnail
        for i in range(self.selected_thumbnail_index + 1, len(thumbnails)):
            current_thumbnail = thumbnails[i]
            x_position = previous_thumbnail.position[0] + previous_thumbnail.width + 10
            y_position = previous_thumbnail.position[1]
            current_thumbnail.set_position((x_position, y_position))
            
            previous_thumbnail = current_thumbnail
        
        [thumbnail.inactivate() 
        for thumbnail in thumbnails 
        if thumbnail != selected_thumbnail]
    
    def handle_events(self):
        self.thumbnails[self.selected_thumbnail_index].handle_events()
        
        if self.is_selected_thumbnail_in_place() == False:
            self.shift_thumbnails()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if (self.left_scroll_button.contains(wotsuievents.mouse_pos) and
            self.left_scroll_button.selected == False):
                self.left_scroll_button.handle_selected()
                
                if self.selected_thumbnail_index > 0:
                    self.select_next_moveset(self.selected_thumbnail_index - 1)
            elif (self.right_scroll_button.contains(wotsuievents.mouse_pos) and
            self.right_scroll_button.selected == False):
                self.right_scroll_button.handle_selected()
                
                if self.selected_thumbnail_index < len(self.thumbnails) - 1:
                    self.select_next_moveset(self.selected_thumbnail_index + 1)
        
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if self.left_scroll_button.selected:
                self.left_scroll_button.handle_deselected()
            
            if self.right_scroll_button.selected:
                self.right_scroll_button.handle_deselected()
    
    def is_selected_thumbnail_in_place(self):
        target_x_position = self.get_selected_thumbnail_position()[0]
        index = self.selected_thumbnail_index
        
        return target_x_position == self.thumbnails[index].position[0]
    
    def get_thumbnail_x_displacement(self):
        target_x_position = self.get_selected_thumbnail_position()[0]
        index = self.selected_thumbnail_index
        selected_thumbnail_x_position = self.thumbnails[index].position[0]
        
        distance = target_x_position - selected_thumbnail_x_position
        
        if distance > 0:
            return min(self.scroll_increment, distance)
        else:
            return max(-self.scroll_increment, distance)
    
    def shift_thumbnails(self):
        x_displacement = self.get_thumbnail_x_displacement()
        
        [thumbnail.shift(x_displacement, 0) for thumbnail in self.thumbnails]
    
    def select_next_moveset(self, next_moveset_index):
        self.thumbnails[self.selected_thumbnail_index].inactivate()
        self.thumbnails[next_moveset_index].activate()
        self.selected_moveset = self.thumbnails[next_moveset_index].moveset
        self.selected_thumbnail_index = next_moveset_index

class PlayerSettingControl(Slider):
    BAR_HEIGHT = 20
    
    def __init__(self, position, slider_width, title_text):
        Slider.__init__(self)
        self.title_label = button.Label(position, title_text, (255, 255, 255), 20)
        self.value_label = button.Label((0,0), '5', (255, 255, 255), 20)
        self.create_children()
        self.set_layout_data(
            position, 
            slider_width, 
            PlayerSettingControl.BAR_HEIGHT
        )
        
        self.set_scroll_percent(.5)
        
        self.add_child(self.title_label)
        self.add_child(self.value_label)
        
    def get_value(self):
        return int(10 * self.get_scroll_percent())
    
    def set_layout_data(self, position, slider_width, bar_height):
        slider_position = (
            self.title_label.position[0],
            self.title_label.position[1] + self.title_label.height + 5
        )
        Slider.set_layout_data(self, slider_position, slider_width, bar_height)
        
        y_delta = self.center()[1] - self.value_label.center()[1]
        x_delta = self.position[0] + self.width - self.value_label.position[0]
        y_position = self.center()[1] - (.5 * self.value_label.height)
        self.value_label.shift(x_delta + 7, y_delta + 4)
        
        self.set_dimensions()
    
    def handle_events(self):
        Slider.handle_events(self)
        
        self.value_label.set_text(str(int(10 * self.get_scroll_percent())))
    
    def draw(self, surface):
        Slider.draw(self, surface)
        self.value_label.draw(surface)
    
    def draw_relative(self, surface, position):
        Slider.draw_relative(self, surface, position)
        self.title_label.draw_relative(surface, position)
        self.value_label.draw_relative(surface, position)

class PlayerStatsWidget(UIObjectBase):
    def __init__(self, position):
        UIObjectBase.__init__(self)
        
        self.size_control = PlayerSettingControl(position, 200, "Size")
        self.add_child(self.size_control)
        
        power_control_position = (
            position[0],
            self.size_control.position[1] + self.size_control.height + 10
        )
        self.power_control = PlayerSettingControl(power_control_position, 200, "Power")
        self.add_child(self.power_control)
        
        speed_control_position = (
            position[0],
            self.power_control.position[1] + self.power_control.height + 10
        )
        self.speed_control = PlayerSettingControl(speed_control_position, 200, "Speed")
        self.add_child(self.speed_control)
        
        weight_control_position = (
            position[0],
            self.speed_control.position[1] + self.speed_control.height + 10
        )
        self.weight_control = PlayerSettingControl(
            weight_control_position, 
            200, 
            "Weight"
        )
        #self.add_child(self.weight_control)
    
    def get_size(self): 
        return self.size_control.get_value()
    
    def handle_events(self):
        size_control_percent = self.size_control.get_scroll_percent()
        self.size_control.handle_events()
        
        if size_control_percent != self.size_control.get_scroll_percent():
            new_size_control_percent = self.size_control.get_scroll_percent()
            
            if new_size_control_percent == 0:
                self.power_control.set_scroll_percent(0)
                self.speed_control.set_scroll_percent(1)
            else:
                self.power_control.set_scroll_percent(new_size_control_percent)
                self.speed_control.set_scroll_percent(1 - new_size_control_percent)
        
        power_control_percent = self.power_control.get_scroll_percent()
        self.power_control.handle_events()
        
        if power_control_percent != self.power_control.get_scroll_percent():
            new_power_control_percent = self.power_control.get_scroll_percent()
            
            if new_power_control_percent == 0:
                self.size_control.set_scroll_percent(0)
                self.speed_control.set_scroll_percent(1)
            else:
                self.size_control.set_scroll_percent(new_power_control_percent)
                self.speed_control.set_scroll_percent(1 - new_power_control_percent)
        
        speed_control_percent = self.speed_control.get_scroll_percent()
        self.speed_control.handle_events()
        
        if speed_control_percent != self.speed_control.get_scroll_percent():
            new_speed_control_percent = self.speed_control.get_scroll_percent()
            
            if new_speed_control_percent == 0:
                self.power_control.set_scroll_percent(1)
                self.size_control.set_scroll_percent(1)
            else:
                self.power_control.set_scroll_percent(1 - new_speed_control_percent)
                self.size_control.set_scroll_percent(1 - new_speed_control_percent)
        
        #self.weight_control.handle_events()
