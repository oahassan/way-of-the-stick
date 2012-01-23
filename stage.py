import os
from glob import glob
import json

import pygame
import physics
import music
import gamestate
import mathfuncs

STAGE_DIR_NM = "stages"

class BkgSprite():
    
    def __init__(
        self,
        position,
        width,
        height,
        image,
        layer
    ):
        self.position = position
        self.width = width
        self.height = height
        self.image = image
        self.surface = pygame.Surface((width, height))
        self.layer = layer

def get_stage_credits():
    credits_list = []
    
    for file_path in glob(os.path.join(".", STAGE_DIR_NM, "*.stg")):
        if os.path.isfile(file_path):
            
            try:
                stage_data = None
                
                with open(file_path,'r') as stage_file:
                    stage_data = json.load(stage_file)
                
                if "credits" in stage_data:
                    stage_data["credits"]["name"] = stage_data["stage-name"]
                    credits_list.append(stage_data["credits"])
            except Exception as ex:
                print("unable to load stage credits: " + file_path)
                print(ex)
    
    return credits_list

def load_from_JSON(path):    
    stage_data = None
    
    with open(path,'r') as stage_file:
        stage_data = json.load(stage_file)
    
    draw_reflections = False
    
    if "reflections" in stage_data:
        draw_reflections = stage_data["reflections"]
    
    if "shadows" in stage_data:
        draw_shadows = stage_data["shadows"]
    
    camera_rects = [get_default_camera_rect(stage_data["world-width"], stage_data["world-height"])]
    
    for rect_data in stage_data["camera-rects"]:
        camera_rects.append(pygame.Rect(*rect_data))
    
    constraining_rect = camera_rects[0].unionall(camera_rects)
    
    music_path = ""
    if ("music" not in stage_data or 
    not os.path.isfile(os.path.join(".", "stages", stage_data["music"]))):
        music_path = music.versusmovesetselect_music_path
    else:
        music_path = os.path.join(".", "stages", stage_data["music"])
    
    stage = ScrollableStage(
        stage_data["world-width"],
        stage_data["world-height"],
        stage_data["floor-height"], 
        pygame.image.load(
            os.path.join(".", "stages", stage_data["bkg-image"])
        ),
        draw_reflections,
        draw_shadows,
        camera_rects,
        constraining_rect,
        stage_data["player-positions"],
        stage_data["stage-name"],
        music_path
    )
    
    for sprite_data in stage_data["sprites"]:
        stage.sprites.append(
            BkgSprite(
                sprite_data["position"],
                sprite_data["width"],
                sprite_data["height"],
                create_sprite_image(sprite_data),
                sprite_data["layer"]
            )
        )
    
    return stage

def get_default_camera_rect(world_width, world_height):
    
    rect_width, rect_height = (world_width, world_height)
    
    aspect_ratio = gamestate._WIDTH / float(gamestate._HEIGHT)
    
    if world_width > world_height:
        rect_height = int(world_width / aspect_ratio)
    
    if world_width < world_height:
        rect_width = int(world_height * aspect_ratio)
    
    return pygame.Rect((0,0), (rect_width, rect_height))

def create_sprite_image(sprite_data):
    image_width = sprite_data["width"]
    image_height = sprite_data["height"]
    image = pygame.Surface((image_width, image_height))
    
    sprite_image = pygame.image.load(
        os.path.join(".", "stages", sprite_data["image"])
    )
    
    sprite_image_width = sprite_image.get_width()
    sprite_image_height = sprite_image.get_height()
    
    repeat_x = False
    
    if "image-x-repeat" in sprite_data:
        repeat_x = sprite_data["image-x-repeat"]
    
    x_offset = 0
    
    if "image-x-offset" in sprite_data:
        x_offset = sprite_data["image-x-offset"]
    
    repeat_y = False
    
    if "image-y-repeat" in sprite_data:
        repeat_y = sprite_data["image-y-repeat"]
    
    y_offset = 0
    
    if "image-y-offset" in sprite_data:
        y_offset = sprite_data["image-y-offset"]
    
    next_x_position = 0
    next_y_position = 0
    
    for j in xrange(max(int(image_height / (sprite_image_height + y_offset)), 1)):
        for i in xrange(max(int(image_width / (sprite_image_width + x_offset)) + 1, 1)):
            image.blit(sprite_image, (next_x_position, next_y_position))
            
            if repeat_x:
                next_x_position += sprite_image_width + x_offset
        
        if repeat_y:
            next_y_position += sprite_image_height + y_offset
    
    return image

def load_default_stage():
    stage = ScrollableStage(
        1800,
        1200,
        1147, 
        create_background(),
        True,
        False,
        [get_default_camera_rect(1800, 1200)],
        get_default_camera_rect(1800, 1200),
        [[550, 1067], [1250, 1067]],
        "Void",
        music.versusmode_music_path
    )
    
    stage.sprites.append(
        BkgSprite(
            (-50, 1127),
            1900,
            20,
            draw_ground(1900),
            -1
        )
    )
    
    return stage

def load_play_tool_stage():
    stage = ScrollableStage(
        1800,
        800,
        500, 
        create_background(),
        True,
        False,
        [get_default_camera_rect(1800, 1200)],
        get_default_camera_rect(1800, 1200),
        [[550, 1067], [1250, 1067]],
        "Play Tool"
    )
    
    stage.sprites.append(
        BkgSprite(
            (-50, 1127),
            1900,
            20,
            draw_ground(1900),
            -1
        )
    )
    
    return stage

def create_background():
    background_surface = pygame.Surface((gamestate._WIDTH, gamestate._HEIGHT))
    background_surface.fill((0,0,0))
    
    return background_surface

def draw_ground(width):
    ground_surface = pygame.Surface((width, 20))
    
    for i in range(20):
        pygame.draw.line(
            ground_surface,
            (int(100 * (20 - i)/20), int(100 * (20 - i)/20), int(100 * (20 - i)/20)),
            (0, i),
            (width, i),
            3,
        )
    
    return ground_surface

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
    """A stage is the enviornment a match takes place in. the bkg_image
    is a pygame image object and the floor_height is the y pixel position
    of the floor of the map."""

    def __init__(
        self, 
        world_width,
        world_height,
        floor_height,
        bkg_image,
        draw_reflections,
        draw_shadows,
        camera_rects,
        constraining_rect,
        player_positions,
        name,
        music
    ):
        self.name = name
        self.floor_height = floor_height
        self.left_screen_position = 0
        self.right_screen_position = gamestate._WIDTH
        self.width = world_width
        self.height = world_height
        self.constraining_rect = constraining_rect
        
        self.left_wall = physics.Wall(
            position = (0,0),
            height = world_height,
            direction = physics.Wall.RIGHT_FACING
        )
        self.right_wall = physics.Wall(
            position = (world_width, 0),
            height = world_height,
            direction = physics.Wall.LEFT_FACING
        )
        self.ground = physics.Ground(
            position = (0, floor_height),
            width = world_width)
        self.background_image = bkg_image
        self.sprites = []
        self.scroll_threshold = 0
        self.draw_reflections = draw_reflections
        self.draw_shadows = draw_shadows
        self.camera_rects = camera_rects
        self.player_positions = player_positions
        self.music = music
    
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
            #elif mathfuncs.sign(model_furthest_left.velocity[0]) >= 0:
                #The player is not moving towards the edge so no shifting should happen
            #    pass
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
                        model.shift((self.right_wall.position[0] - model_rect.right, 0))
            #elif mathfuncs.sign(model_furthest_right.velocity[0]) <= 0:
                #The player is not moving towards the edge so no shifting should happen
            #    pass
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
