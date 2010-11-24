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
    
    def update(
        self,
        time_passed
    ):
        ratio = float(self.max_height) / float(self.max_width)
        
        self.time_passed += (self.time_multiplier * time_passed)
        
        self.height = min(ratio * self.time_passed, self.max_height)
        self.width = min(self.time_passed, self.max_width)
        self.position = (
            self.center[0] - (.5 * self.width),
            self.center[1] - (.5 * self.height)
        )
    
    def get_enclosing_rect():
        return (self.position, (self.width, self.height))
    
    def effect_over(self):
        ratio = float(self.max_height) / float(self.max_width)
        
        small_height = (self.inner_circle_ratio * ratio) * self.time_passed
        small_width = self.inner_circle_ratio * self.time_passed
        
        return (small_height > self.height + (ratio*2)) and (small_width > self.width + 2)
    
    def draw_ellipse_effect(
        self,
        surface
    ):
        
        ratio = float(self.max_height) / float(self.max_width)
        
        #create effect dimensions by size
        small_height = (self.inner_circle_ratio * ratio) * self.time_passed
        small_width = self.inner_circle_ratio * self.time_passed
        
        if self.effect_over():
            self.time_passed = 0
        
        #create effect surface
        effect_surface = pygame.Surface((self.width, self.height)).convert()
        
        effect_position_big = (0,0)
        effect_position_small = (-2, (.5 * self.height) - (.5 * small_height))
        
        pygame.draw.ellipse(effect_surface, (255,255,255), (effect_position_big, (self.width, self.height)))
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