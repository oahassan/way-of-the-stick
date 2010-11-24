import pygame

class Effect():
    def __init__(
        self,
        center,
        angle,
        max_width,
        max_height,
        inner_circle_ratio,
        fade_rate,
        time_multiplier):
        
        self.time_passed = 0
        self.center = center
        self.angle = angle
        self.max_width = max_width
        self.max_height = max_height
        self.inner_circle_ratio = inner_circle_ratio
        self.fade_rate = fade_rate
        self.time_multiplier = time_multiplier
    
    def draw_ellipse_effect(
        self,
        time_passed,
        surface):
        
        ratio = float(self.max_height) / float(self.max_width)
        
        #create effect dimensions by size
        self.time_passed += (self.time_multiplier * time_passed)
        
        big_height = min(ratio * self.time_passed, self.max_height)
        big_width = min(self.time_passed, self.max_width)
        
        small_height = (self.inner_circle_ratio * ratio) * self.time_passed
        small_width = self.inner_circle_ratio * self.time_passed
        
        if small_height > big_height + (ratio*2) and small_width > big_width + 2:
            self.time_passed = 0
        
        #create effect surface
        effect_surface = pygame.Surface((big_width, big_height)).convert()
        
        effect_position_big = (0,0)
        effect_position_small = (-2, (.5 * big_height) - (.5 * small_height))
        
        pygame.draw.ellipse(effect_surface, (255,255,255), (effect_position_big, (big_width, big_height)))
        pygame.draw.ellipse(effect_surface, (0,0,0), (effect_position_small, (small_width, small_height)))
        
        effect_surface.set_colorkey((0,0,0))
        effect_surface.set_alpha((255 * ((100 - (self.fade_rate * self.time_passed)) / 100)))
        
        effect_surface = pygame.transform.rotate(effect_surface, self.angle)
        effect_surface_rect = effect_surface.get_rect()
        
        final_position = (
            self.center[0] - (.5 * effect_surface_rect.width),
            self.center[1] - (.5 * effect_surface_rect.height)
        )
        
        surface.blit(effect_surface, final_position)
