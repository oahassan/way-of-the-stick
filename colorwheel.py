#how to draw polygons
#pygame.draw.polygon(Surface, color, pointlist, width=0)

#Try drawing bezier curve with polygon as points
#then fill for thickness

from wotsfx import HitEffect, ClashEffect
import sys
import math
import pygame
import wotsui
from wotsuicontainers import TextBox
from chatui import MessageEntryBox
import wotsuievents
from button import Label
from mathfuncs import distance, sign

pygame.init()
pygame.font.init()

text_box = TextBox('text', 700, (50,50))

message_entry = MessageEntryBox((10,400), 400)

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

BLUE = (0,0,255)
GREEN = (0,255,0)
YELLOW = (255,255,0)
ORANGE = (255,127,0)
RED = (255,0,0)
PURPLE = (128,0,128)

COLORS = [ORANGE, RED, PURPLE, BLUE, GREEN, YELLOW]

angle_increment = 2.0 * math.pi / len(COLORS)
radius = 40
side_length = 20

CENTER = (400, 300)

class ColorWheel(wotsui.UIObjectBase):
    def __init__(self, center, radius, swatch_radius, selected_index):
        wotsui.UIObjectBase.__init__(self)
        
        self.swatch_center = center
        self.color_swatches = []
        self.swatch_radius = swatch_radius
        self.selected_swatch = None
        
        for i in range(len(COLORS)):
            angle = angle_increment * i
            swatch_center = (
                int(center[0] + (math.cos(angle) * radius)),  
                int(center[1] + (math.sin(angle) * radius))
            )
            self.color_swatches.append(
                ColorSwatchCircle(COLORS[i], swatch_center, swatch_radius)
            )
        
        self.color_swatches.append(
            ColorSwatchRect(
                (255, 255, 255),
                (0, 0, 0),
                (
                    int(center[0] - radius - swatch_radius), 
                    int(center[1] + radius + swatch_radius)
                ),
                int(radius + swatch_radius), 
                int(.333 * (radius + swatch_radius))
            )
        )
        
        self.color_swatches.append(
            ColorSwatchRect(
                (0, 0, 0),
                (255, 255, 255),
                (
                    center[0], 
                    int(center[1] + radius + swatch_radius)
                ),
                int(radius + swatch_radius), 
                int(.333 * (radius + swatch_radius))
            )
        )
        
        self.add_children(self.color_swatches)
        self.evaluate_position()
        self.set_dimensions()
        
        self.color_swatches[selected_index].handle_selected()
        self.selected_swatch = self.color_swatches[selected_index]
    
    def draw(self, surface):
        for swatch in self.color_swatches:
            swatch.draw(surface)
        
        pygame.draw.circle(
            screen, 
            self.selected_swatch.color, 
            self.swatch_center, 
            self.swatch_radius
        )
    
    def handle_events(self):
        if wotsuievents.mousebutton_pressed():
            for swatch in self.color_swatches:
                if swatch.contains(wotsuievents.mouse_pos):
                    self.selected_swatch.handle_deselected()
                    swatch.handle_selected()
                    self.selected_swatch = swatch

class ColorSwatchCircle(wotsui.SelectableObjectBase):
    def __init__(self, color, center, radius):
        wotsui.SelectableObjectBase.__init__(self)
        self.color = color
        self.active_color = color
        self.selected_color = color
        self.center = center
        self.position = (center[0] - radius, center[1] - radius)
        self.height = radius
        self.width = radius
        self.radius = radius
    
    def contains(self, position):
        if distance(position, self.center) <= self.radius:
            return True
        else:
            return False
    
    def draw(self, surface):
        pygame.draw.circle(
            screen, 
            self.color, 
            self.center, 
            self.radius
        )
        
        if self.selected:
            pygame.draw.circle(
                screen, 
                (255,255,255), 
                self.center, 
                self.radius,
                3
            )
            
            pygame.draw.circle(
                screen, 
                (0,0,0), 
                self.center, 
                self.radius,
                1
            )

class ColorSwatchRect(wotsui.SelectableObjectBase):
    def __init__(self, color, border_outer_line_color, position, width, height):
        wotsui.SelectableObjectBase.__init__(self)
        self.color = color
        self.active_color = color
        self.selected_color = color
        self.border_outer_line_color = border_outer_line_color
        self.position = position
        self.height = height
        self.width = width
    
    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.color,
            (self.position, (self.width, self.height))
        )
        
        if self.selected:
            pygame.draw.rect(
                surface,
                self.border_outer_line_color,
                (self.position, (self.width, self.height)),
                4
            )
            
            pygame.draw.rect(
                surface,
                self.color,
                (self.position, (self.width, self.height)),
                2
            )
        
        else:
            pygame.draw.rect(
                surface,
                self.border_outer_line_color,
                (self.position, (self.width, self.height)),
                1
            )

wheel = ColorWheel(CENTER, radius, side_length, 0)

start = (300,200)
end = (600, 400)
thickness = 30

if __name__ == '__main__':


    while 1:
        screen.fill((0,0,0))
        wotsuievents.get_events()
        
        #angle_label.set_text(str(input_angle))
        #angle_label.draw(screen)
        
        if pygame.QUIT in wotsuievents.event_types:
            sys.exit()
        
        wheel.handle_events()
        wheel.draw(screen)
        
        pygame.display.flip()
        
        clock.tick(20)
