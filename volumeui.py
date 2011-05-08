import sys
import pygame
import wotsuievents
import wotsui
from wotsuicontainers import Slider
from button import Label

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
