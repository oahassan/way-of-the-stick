import pygame
import physics
import gamestate
import mathfuncs

class Stage():
    """A stage is the enviornment a match takes place in. the bkg_image
    is a pygame image object and the floor_height is the y pixel position
    of the floor of the map."""

    def __init__(self, bkg_image, floor_height):
        
        self.background_image = bkg_image
        self.ground = physics.Ground(position = (0, floor_height), \
                                    width = bkg_image.get_width())
        self.left_wall = physics.Wall(position = (0,0), \
                                     height = bkg_image.get_height(), \
                                     direction = physics.Wall.RIGHT_FACING)
        self.right_wall = physics.Wall(position = (bkg_image.get_width(), 0), \
                                       height = bkg_image.get_height(), \
                                       direction = physics.Wall.LEFT_FACING)
    
    def draw(self, surface):
        surface.blit(self.background_image, (0,0))

class ScrollableStage():
    """A collection a sprites used to draw the background of a match"""

    def __init__(self, floor_height, left_wall_position, right_wall_position):
        
        self.floor_height = floor_height
        self.left_screen_position = 0
        self.right_screen_position = gamestate._WIDTH
        
        self.left_wall = physics.Wall(
            position = (-600,0),
            height = 1600,
            direction = physics.Wall.RIGHT_FACING
        )
        self.right_wall = physics.Wall(
            position = (1200, 0),
            height = 1600,
            direction = physics.Wall.LEFT_FACING
        )
        self.ground = physics.Ground(
            position = (0, floor_height),
            width = gamestate._WIDTH)
        self.background_image = self.create_black_background()
        
        self.scroll_threshold = 50
    
    def create_background(self):
        background_surface = pygame.Surface((gamestate._WIDTH, gamestate._HEIGHT))
        background_surface.fill((255,255,255))
        
        for i in range(80, 100):
            pygame.draw.line(
                background_surface,
                (int(255 * i / 100), int(255 * i / 100), int(255 * i / 100)),
                (self.left_wall.position[0], self.floor_height + i - 80),
                (self.right_wall.position[0], self.floor_height + i - 80),
                3
            )
        
        return background_surface
    
    def create_black_background(self):
        background_surface = pygame.Surface((gamestate._WIDTH, gamestate._HEIGHT))
        background_surface.fill((0,0,0))
        
        for i in range(20):
            pygame.draw.line(
                background_surface,
                (int(100 * (20 - i)/20), int(100 * (20 - i)/20), int(100 * (20 - i)/20)),
                (self.left_wall.position[0], self.floor_height + i - 20),
                (self.right_wall.position[0], self.floor_height + i - 20),
                3
            )
        
        return background_surface
    
    def scroll_background(self, player_models):
        """Move the players and background so that it appears that the background is
        scrolling along with the player's movement"""
        
        #Get the minimum distance between any player and each wall
        min_and_max_positions = self.get_min_and_max_x_positions(player_models)
        
        furthest_left_position = min_and_max_positions[0][0]
        model_furthest_left = min_and_max_positions[0][1]
        
        furthest_right_position = min_and_max_positions[1][0]
        model_furthest_right = min_and_max_positions[1][1]
        
        left_threshold_position = self.left_screen_position + self.scroll_threshold
        right_threshold_position = self.right_screen_position - self.scroll_threshold
        
        if (furthest_left_position < left_threshold_position and
        furthest_right_position > right_threshold_position):
            
            #Make sure no players go off screen
            for model in player_models:
                model_rect = pygame.Rect(model.get_enclosing_rect())
                
                if model_rect.left < self.left_screen_position:
                    model.shift((self.left_screen_position - model_rect.left, 0))
                
                elif model_rect.right > self.right_screen_position:
                    model.shift((self.right_screen_position - model_rect.right, 0))
            
        elif furthest_left_position < left_threshold_position:
            if self.left_wall.position[0] == 0:
                #The player is on the edge of the stage so make sure they don't go off
                for model in player_models:
                    model_rect = pygame.Rect(model.get_enclosing_rect())
                    
                    if model_rect.left < self.left_wall.position[0]:
                        model.shift((self.left_wall.position[0] - model_rect.left, 0))
            elif mathfuncs.sign(model_furthest_left.velocity[0]) >= 0:
                #The player is not moving towards the edge so no shifting should happen
                pass
            else:
                x_displacement = left_threshold_position - furthest_left_position
                
                for model in player_models:
                    model.shift((x_displacement, 0))
                
                left_wall_displacement = min(
                    x_displacement,
                    self.left_screen_position - self.left_wall.position[0]
                )
                
                self.left_wall.shift((left_wall_displacement, 0))
                self.right_wall.shift((x_displacement, 0))
        
        elif furthest_right_position > right_threshold_position:
            if self.right_wall.position[0] == gamestate._WIDTH:
                #The player is on the edge of the stage so make sure they don't go off
                for model in player_models:
                    model_rect = pygame.Rect(model.get_enclosing_rect())
                    
                    if model_rect.right > self.right_wall.position[0]:
                        model.shift((self.right_wall_position[0] - model_rect.right, 0))
            elif mathfuncs.sign(model_furthest_right.velocity[0]) <= 0:
                #The player is not moving towards the edge so no shifting should happen
                pass
            else:
                x_displacement = right_threshold_position - furthest_right_position
                
                for model in player_models:
                    model.shift((x_displacement, 0))
                
                self.left_wall.shift((x_displacement, 0))
                
                right_wall_x_displacment = max(
                    x_displacement,
                    -(self.right_wall.position[0] - self.right_screen_position)
                )
                self.right_wall.shift((right_wall_x_displacment, 0))
    
    def get_min_and_max_x_positions(self, player_models):
        """finds the models with the minimum and maximum x positions and returns them
        in tuples containg the position and the model"""
        
        model_rect = pygame.Rect(player_models[0].get_enclosing_rect())
        
        min_and_max_positions = [
            (model_rect.left, player_models[0]),
            (model_rect.right, player_models[0])
        ]
        
        for model in player_models:
            model_rect = pygame.Rect(model.get_enclosing_rect())
            
            if model_rect.left < min_and_max_positions[0][0]:
                min_and_max_positions [0] = (model_rect.left, model)
            
            if model_rect.right > min_and_max_positions[1][0]:
                min_and_max_positions [1] = (model_rect.right, model)
        
        return min_and_max_positions 
    
    def draw(self, surface):
        pass
