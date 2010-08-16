import pygame
import physics

class Stage():
    def __init__(self, bkg_image, floor_height):
        """A stage is the enviornment a match takes place in. the bkg_image
        is a pygame image object and the floor_height is the y pixel position
        of the floor of the map."""
        
        self.bkg_image = bkg_image
        self.ground = physics.Ground(position = (0, floor_height), \
                                    width = bkg_image.get_width())
        self.left_wall = physics.Wall(position = (0,0), \
                                     height = bkg_image.get_height(), \
                                     direction = physics.Wall.RIGHT_FACING)
        self.right_wall = physics.Wall(position = (bkg_image.get_width(), 0), \
                                       height = bkg_image.get_height(), \
                                       direction = physics.Wall.LEFT_FACING)
    
    def draw(self, surface):
        surface.blit(self.bkg_image, (0,0))