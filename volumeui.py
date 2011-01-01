import sys
import pygame
import wotsuievents
import wotsui
from wotsuicontainers import HorizontalScrollBar, Bar, Track, ScrollButton, SCROLL_LEFT, SCROLL_RIGHT, SCROLL_BUTTON_HEIGHT, SCROLL_BUTTON_WIDTH
from button import Label

class Slider(HorizontalScrollBar):
    
    def __init__(self):
        HorizontalScrollBar.__init__(self)
    
    def create_children(self):
        self.scroll_left_button = VolumeButton(SCROLL_LEFT)
        self.scroll_right_button = VolumeButton(SCROLL_RIGHT)
        self.bar = Bar()
        self.track = VolumeTrack()
        
        self.add_children([self.scroll_left_button,
                           self.scroll_right_button,
                           self.track,
                           self.bar])
    
    def set_layout_data(self, position, width):
        wotsui.UIObjectBase.set_layout_data(self, position, SCROLL_BUTTON_HEIGHT, width)
        
        track_height = SCROLL_BUTTON_HEIGHT
        track_width = width - (2 * SCROLL_BUTTON_HEIGHT)
        track_position = (position[0] + SCROLL_BUTTON_WIDTH, position[1])
        self.track.set_layout_data(track_position, track_height, track_width)
        
        self.scroll_left_button.set_layout_data(position)
        
        scroll_right_button_position = (position[0] + width - SCROLL_BUTTON_WIDTH, \
                                        position[1])
        self.scroll_right_button.set_layout_data(scroll_right_button_position)
        
        bar_position = (position[0] + SCROLL_BUTTON_WIDTH, position[1] - int(SCROLL_BUTTON_HEIGHT / 2) - 5)
        self.bar.set_layout_data(bar_position, SliderBar.HEIGHT, SliderBar.WIDTH)

class VolumeTrack(Track):
    
    def draw(self, surface):
        tip_point = (self.position[0] + 7, \
                     self.center()[1])
        top_right = (self.top_right()[0] - 7, self.top_right()[1])
        bottom_right =  (self.bottom_right()[0] - 7, self.bottom_right()[1])
        
        pygame.draw.polygon(
            surface,
            self.color,
            [tip_point,
            top_right,
            bottom_right])
        
        pygame.draw.aalines(
            surface,
            self.color,
            True,
            [tip_point,
            top_right,
            bottom_right])
    
    def draw_relative(self, surface, position):
        tip_point = (self.get_relative_position(position)[0] + 7, \
                     self.center_relative(position)[1])
        top_right = (
            self.top_right_relative(position)[0] - 7,
            self.top_right_relative(position)[1]
        )
        bottom_right =  (
            self.bottom_right_relative(position)[0] - 7,
            self.bottom_right_relative(position)()[1]
        )
        
        pygame.draw.polygon(
            surface,
            self.color,
            [tip_point,
            top_right,
            bottom_right])
        
        pygame.draw.aalines(
            surface,
            self.color,
            True
            [tip_point,
            top_right,
            bottom_right])

class VolumeButton(ScrollButton):
    
    def __init__(self, direction):
        ScrollButton.__init__(self, direction)
        
        if self.direction == SCROLL_LEFT:
            self.image = Label(self.position, '-', self.color)
        else:
            self.image = Label(self.position, '+', self.color)
        
        self.add_child(self.image)
    
    def set_layout_data(self, position):
        ScrollButton.set_layout_data(self, position)
        self.layout_image()
    
    def layout_image(self):
        
        position_delta = (self.center()[0] - self.image.center()[0], self.center()[1] - self.image.center()[1])
        
        self.image.shift(position_delta[0], position_delta[1])
    
    def handle_selected(self):
        ScrollButton.handle_selected(self)
        self.image.text_color = self.color
    
    def handle_deselected(self):
        ScrollButton.handle_deselected(self)
        self.image.text_color = self.color
    
    def _draw_left_button(self, surface):
        self.image.draw(surface)
    
    def _draw_left_button_relative(self, surface, position):
        self.image.draw_relative(surface, position)
        
    def _draw_right_button(self, surface):
        self.image.draw(surface)
    
    def _draw_right_button_relative(self, surface, position):
        self.image.draw(surface, position)

class SliderBar(Bar):
    HEIGHT = 40
    WIDTH = 15
    
    def __init__(self):
        wotsui.SelectableObjectBase.__init__(self)

class VolumeControl(Slider):
    
    def __init__(self):
        Slider.__init__(self)
        self.percent_label = Label((0,0), '', (255, 255, 255), 30)
    
    def set_layout_data(self, position, slider_width):
        Slider.set_layout_data(self, position, slider_width)
        
        y_delta = self.center()[1] - self.percent_label.center()[1]
        x_delta = self.position[0] + self.width - self.percent_label.position[0]
        y_position = self.center()[1] - (.5 * self.percent_label.height)
        self.percent_label.shift(x_delta + 7, y_delta + 4)
    
    def handle_events(self):
        Slider.handle_events(self)
        
        self.percent_label.set_text(str(int(100 * self.get_scroll_percent())) + '%')
    
    def draw(self, surface):
        Slider.draw(self, surface)
        self.percent_label.draw(surface)
    
    def draw_relative(self, surface, position):
        Slider.draw_relative(self, surface, position)
        self.percent_label.draw_relative(surface, position)

if __name__ == '__main__':
    pygame.init()
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    slider = VolumeControl()
    slider.create_children()
    slider.set_layout_data((300, 100), 300)
    scroll_percent = Label((10,10),'',(0,0,255))
    slider.set_scroll_percent(.5)
    
    while True:
        wotsuievents.get_events()
    
        events = wotsuievents.events
        event_types = wotsuievents.event_types
        mousePos = wotsuievents.mouse_pos
        mouseButtonsPressed = wotsuievents.mouse_buttons_pressed
        
        if pygame.QUIT in event_types:
            sys.exit()
        
        slider.handle_events()
        scroll_percent.set_text(str(slider.get_scroll_percent()))
        
        screen.fill((0,0,0))
        slider.draw(screen)
        scroll_percent.draw(screen)
        
        pygame.display.update()
        
        clock.tick(20)
