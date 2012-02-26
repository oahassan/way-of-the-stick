import pygame
import mathfuncs

class TrailEffect():
    def __init__(
        self,
        start_position,
        max_width,
        max_length,
        color
    ):
        self.positions = [start_position]
        self.widths = []
        self.length = 0
        self.max_length = max_length
        self.max_width = float(max_width)
        self.color = color
    
    def update(self, position):
        self.length += mathfuncs.distance(self.positions[-1], position)
        self.positions.append(position)
        
        if self.length > self.max_length:
            self.length -= mathfuncs.distance(self.positions[0], self.positions[1])
            self.positions = self.positions[1:]
        elif self.length > 0:
            self.widths = [1]
            width_delta = float(self.max_width / len(self.positions))
            
            for i in range(len(self.positions)):
                self.widths.append(min(self.max_width, self.widths[i] * 1.5))
    
    def is_renderable(self):
        return self.length > 0
    
    def get_polygons(self):
        polygon_positions = [[self.positions[0]]]
        polygon_positions[0].extend(self.get_line_positions(1))
        
        if len(self.positions) > 2:
            for i in range(2,len(self.positions)):
                new_positions = polygon_positions[i - 2][-2:]
                new_positions.extend(self.get_line_positions(i))
                
                polygon_positions.append(new_positions)
        
        return polygon_positions
    
    def get_line_positions(self, end_position_index):
        start_position = self.positions[end_position_index - 1]
        end_position = self.positions[end_position_index]
        
        l1 = mathfuncs.distance(end_position, start_position)
        
        if l1 > 0:
            #YAY FOR SIMILAR TRIANGLES!
            x1 = end_position[0] - start_position[0]
            y1 = end_position[1] - start_position[1]
            l2 = self.widths[end_position_index] / 2.0
            
            position1 = (
                end_position[0] + (y1 / l1 * l2),
                end_position[1] - (x1 / l1 * l2)
            )
            position2 = (
                end_position[0] - (y1 / l1 * l2),
                end_position[1] + (x1 / l1 * l2)
            )
            
            return (position1, position2)
        else:
            return (end_position, end_position)

class Effect():
    def __init__(
        self,
        center,
        angle,
        max_width,
        max_height,
        inner_circle_ratio,
        fade_rate,
        time_multiplier
    ):
        
        self.time_passed = 0
        self.height = 0
        self.width = 0
        self.position = center
        self.center = center
        self.angle = angle
        self.max_width = max_width
        self.max_height = max_height
        self.inner_circle_ratio = inner_circle_ratio
        self.fade_rate = fade_rate
        self.time_multiplier = time_multiplier
    
    def get_enclosing_rect(self):
        return (self.position, (self.width, self.height))

class HitEffect(Effect):
    def update(
        self,
        time_passed
    ):
        ratio = float(self.max_height) / float(self.max_width)
        
        self.time_passed += (self.time_multiplier * time_passed)
        
        big_height = min(ratio * self.time_passed, self.max_height)
        big_width = min(self.time_passed, self.max_width)
        
        effect_surface = pygame.Surface((big_width, big_height)).convert()
        effect_surface = pygame.transform.rotate(effect_surface, self.angle)
        effect_surface_rect = effect_surface.get_rect()
        
        self.height = effect_surface_rect.height
        self.width = effect_surface_rect.width
        self.position = (
            self.center[0] - (.5 * self.width),
            self.center[1] - (.5 * self.height)
        )
    
    def draw_effect(self):
        
        ratio = float(self.max_height) / float(self.max_width)
        
        #create effect dimensions by size
        big_height = min(ratio * self.time_passed, self.max_height)
        big_width = min(self.time_passed, self.max_width)
        small_height = (self.inner_circle_ratio * ratio) * self.time_passed
        small_width = self.inner_circle_ratio * self.time_passed
        
        #create effect surface
        effect_surface = pygame.Surface((big_width, big_height)).convert()
        effect_surface.fill((1,232,5))
        
        effect_position_big = (0,0)
        effect_position_small = (-2, (.5 * big_height) - (.5 * small_height))
        
        pygame.draw.ellipse(effect_surface, (255,255,255), (effect_position_big, (big_width, big_height)))
        pygame.draw.ellipse(effect_surface, (1,232,5), (effect_position_small, (small_width, small_height)))
        
        effect_surface.set_colorkey((1,232,5))
        effect_surface.set_alpha((255 * ((100 - (self.fade_rate * self.time_passed)) / 100)))
        
        effect_surface = pygame.transform.rotate(effect_surface, self.angle)
        effect_surface_rect = effect_surface.get_rect()
        
        final_position = (
            self.center[0] - (.5 * effect_surface_rect.width),
            self.center[1] - (.5 * effect_surface_rect.height)
        )
        
        return (final_position, effect_surface)
    
    def effect_over(self):
        ratio = float(self.max_height) / float(self.max_width)
        
        small_height = (self.inner_circle_ratio * ratio) * self.time_passed
        small_width = self.inner_circle_ratio * self.time_passed
        
        return (small_height > self.height + (ratio*2)) and (small_width > self.width + 2)

class ClashEffect(Effect):
    def update(
        self,
        time_passed
    ):
        
        self.time_passed += (self.time_multiplier * time_passed)
        
        big_height = min(self.time_passed, self.max_height)
        big_width = min(self.time_passed, self.max_width)
        
        effect_surface = pygame.Surface((big_width, big_height)).convert()
        effect_surface = pygame.transform.rotate(effect_surface, self.angle)
        effect_surface_rect = effect_surface.get_rect()
        
        self.height = effect_surface_rect.height
        self.width = effect_surface_rect.width
        self.position = (
            self.center[0] - (.5 * self.width),
            self.center[1] - (.5 * self.height)
        )
    
    def draw_effect(self):
        
        #create effect dimensions by size
        big_height = min(self.time_passed, self.max_height)
        big_width = min(self.time_passed, self.max_width)
        
        #create effect surface
        effect_surface = pygame.Surface((big_width, big_height)).convert()
        effect_surface.fill((1,232,5))
        
        effect_position_big = (int(.5 * big_width), int(.5 * big_height))
        
        color_weights = [255]
        
        for i in range(1, int(.5 * big_width) - int(big_width * .01)):
            color_weights.append(int(.9 * color_weights[i - 1]))
        color_weights = color_weights[::-1]
        
        for i in range(int(.5 * big_width),int(big_width * .01), -2):
            weight_index = i - int(big_width * .01)
            color = (color_weights[-weight_index], color_weights[-weight_index], color_weights[-weight_index])
            pygame.draw.circle(effect_surface, color, effect_position_big, i)
        
        effect_surface.set_colorkey((1,232,5))
        effect_surface.set_alpha((255 * ((100 - (self.fade_rate * self.time_passed)) / 100)))
        effect_surface_rect = effect_surface.get_rect()
        
        final_position = (
            self.center[0] - (.5 * effect_surface_rect.width),
            self.center[1] - (.5 * effect_surface_rect.height)
        )
        
        return (final_position, effect_surface)
    
    def effect_over(self):
        return self.time_passed > 70
