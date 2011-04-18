import pygame
import gamestate
import mathfuncs
from wotsprot.rencode import serializable
from enumerations import PlayerPositions, PointNames, LineNames
from physics import Model, Orientations

PAN_RATE = 10
SCALE_RATE = .01

class ViewportCamera():
    def __init__(
        self,
        world_width,
        world_height,
        viewport_width,
        viewport_height
    ):
        self.world_height = world_height
        self.world_width = world_width
        self.viewport_height = viewport_height
        self.viewport_width = viewport_width
        self.viewport_position = (0,0)
        self.viewport_scale = 1
        self.zoom_count = 3
        self.zoom_threshold = 20
        self.pan_threshold = 10
    
    def update(self, constraining_rect):
        scale = self.get_viewport_scale(constraining_rect)
        
        if not self.can_zoom(constraining_rect):
            scale = self.viewport_scale
        
        pan_deltas = self.get_pan_deltas(
            scale,
            constraining_rect
        )
        
        self.viewport_scale = scale
        self.viewport_position = (
            self.viewport_position[0] + pan_deltas[0],
            self.viewport_position[1] + pan_deltas[1]
        )
    
    def can_zoom(self, constraining_rect):
        """Determine whether a zoom should be allowed.  This is in place to
        stabilize the camera.  Without it the screen shakes when because the
        width of the fighter sprites changes in their rest positions"""
        viewport_scale = self.viewport_scale
        scaled_viewport_width = self.viewport_width / viewport_scale
        scaled_viewport_height = self.viewport_height / viewport_scale
        
        scale_up_indicator = (
            constraining_rect.width > scaled_viewport_width or
            constraining_rect.height > scaled_viewport_height
        )
        
        scale_down_indicator = (
            (scaled_viewport_width - constraining_rect.width)*viewport_scale > 
            self.zoom_threshold and
            (scaled_viewport_height - constraining_rect.height)*viewport_scale > 
            self.zoom_threshold
        )
        
        return scale_up_indicator or scale_down_indicator
    
    def get_position_in_viewport(self, position):
        return (
            (position[0] - self.viewport_position[0]) * self.viewport_scale,
            (position[1] - self.viewport_position[1]) * self.viewport_scale
        )
    
    def get_viewport_scale(self, constraining_rect):
        """determine the scale of world objects on the viewport by forcing the
        viewport to include all rects in the constraining_rects.
        
        constraining_rect: a rect that contains everything in the world that 
        must appear in the viewport. The rect should be at world scale and 
        positioned in world coordinates.
        """
        scale = 1
        
        min_x_position = constraining_rect.left
        min_y_position = constraining_rect.top
        max_x_position = constraining_rect.right
        max_y_position = constraining_rect.bottom
        
        x_dist = max_x_position - min_x_position
        y_dist = max_y_position - min_y_position
        x_diff = x_dist - self.viewport_width
        y_diff = y_dist - self.viewport_height
        
        if x_diff > 0 and y_diff > 0:
            if x_diff > y_diff:
                scale = float(self.viewport_width) / x_dist
            else:
                scale = float(self.viewport_height) / y_dist
        elif x_diff > 0:
            scale = float(self.viewport_width) / x_dist
        elif y_diff > 0:
            scale = float(self.viewport_height) / y_dist
        else:
            pass #no scaling is required.
        
        if scale > self.viewport_scale:
            scale = min(scale, self.viewport_scale + SCALE_RATE)
        
        return scale
    
    def get_pan_deltas(
        self,
        scale,
        constraining_rect
    ):
        """determine the distance to move from the current viewport position"""
        min_x_position = constraining_rect.left
        min_y_position = constraining_rect.top
        max_x_position = constraining_rect.right
        max_y_position = constraining_rect.bottom
        
        target_position = self.get_target_position(scale, constraining_rect)
        x_position = target_position[0]
        y_position = target_position[1]
        
        x_pan_delta = 0
        y_pan_delta = 0
        
        if abs(self.viewport_position[0] - x_position)*scale > self.pan_threshold:
            if x_position > self.viewport_position[0]:
                x_pan_delta = max(
                    min(x_position - self.viewport_position[0], PAN_RATE),
                    max_x_position - (self.viewport_position[0] + (self.viewport_width / self.viewport_scale))
                )
            else:
                x_pan_delta = min(
                    max(x_position - self.viewport_position[0], -PAN_RATE),
                    min_x_position - self.viewport_position[0]
                )
        
        if abs(self.viewport_position[1] - y_position)*scale > self.pan_threshold:
            if y_position > self.viewport_position[1]:
                y_pan_delta = max(
                    min(y_position - self.viewport_position[1], PAN_RATE),
                    max_y_position - (self.viewport_position[1] + (self.viewport_height / self.viewport_scale))
                )
            else:
                y_pan_delta = min(
                    max(y_position - self.viewport_position[1], -PAN_RATE),
                    min_y_position - self.viewport_position[1]
                )
        
        return (x_pan_delta, y_pan_delta)
    
    def get_target_position(self, scale, constraining_rect):
        """determine the target position of the viewport in world coordinates
        
        scale: the scale of objects in the viewport where world scale is 1
        constraining_rects: the bounding rectangles that must be included in
        the viewport"""
        
        scaled_viewport_width = self.viewport_width / scale
        scaled_viewport_height = self.viewport_height / scale
        
        x_position = self.world_width - scaled_viewport_width
        y_position = self.world_height - scaled_viewport_height
        
        min_x_position = constraining_rect.left
        min_y_position = constraining_rect.top
        max_x_position = constraining_rect.right
        max_y_position = constraining_rect.bottom
        midpoint = mathfuncs.midpoint(
            (max_x_position, max_y_position),
            (min_x_position, min_y_position)
        )
        
        #a player is outside the range of the right edge of the world
        if min_x_position < self.world_width - scaled_viewport_width:
            
            #a player is outside the range of the left edge of the world 
            if max_x_position > scaled_viewport_width:
                x_position = midpoint[0] - (scaled_viewport_width / 2)
                
            else:
                x_position = 0
        
        #a player is outside of the range of the bottom edge of the world
        if min_y_position < self.world_height - scaled_viewport_height:
            
            #a player is outside the ranges of the top edge of the world
            if max_y_position > self.viewport_height:
                y_position = midpoint[1] - (scaled_viewport_height / 2)
            else:
                y_position = 0
        
        return (x_position, y_position)

class SurfaceRenderer():
    def __init__(
        self,
        viewport_camera
    ):
        self.viewport_camera = viewport_camera
    
    def draw_surface_to_screen(self, position, surface):
        
        surface_viewport_position = self.viewport_camera.get_position_in_viewport(position)
        
        scaled_surface = pygame.transform.scale(
            surface,
            (
                int(surface.get_width() * self.viewport_camera.viewport_scale),
                int(surface.get_height() * self.viewport_camera.viewport_scale)
            )
        )
        
        gamestate.screen.blit(scaled_surface, surface_viewport_position)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                surface_viewport_position,
                (scaled_surface.get_width(), scaled_surface.get_height())
            )
        )

class PlayerColors():
    def __init__(
        self,
        outline_color,
        health_color
    ):
        self.outline_color = outline_color
        self.health_color = health_color
    
    def _pack(self):
        return self.outline_color, self.health_color

class PlayerRendererState():
    def __init__(
        self,
        viewport_camera,
        player_positions
    ):
        self.viewport_camera = viewport_camera
        
        self.player_positions = player_positions
        self.player_model_dictionary = \
            build_player_model_dictionary(player_positions)
        self.player_health_percentage_dictionary = \
            build_player_health_percentage_dictionary(player_positions)
        self.player_outline_color_dictionary = dict(
            [(player_position, None) for player_position in player_positions]
        )
        self.player_health_color_dictionary = dict(
            [(player_position, None) for player_position in player_positions]
        )
    
    def update(self, player_rendering_info_dictionary, geometric_smoothing_weight):
        """updates the viewport camera and the rendering models
        
        player_rendering_info_dictionary: a data to render each player player position
        geometric_smoothing_weight: the weight to use in averaging the 
        rendering models and given player models to avoid jerky animation"""
        
        constraining_rects = [
            pygame.Rect(rendering_info.player_model.get_enclosing_rect())
            for rendering_info in player_rendering_info_dictionary.values()
        ]
        
        constraining_rect = constraining_rects[0].unionall(constraining_rects)
        
        self.viewport_camera.update(constraining_rect)
        
        for player_position, rendering_info in player_rendering_info_dictionary.iteritems():
            self.set_player_point_positions(
                player_position,
                rendering_info.player_model
            )
            
            self.player_outline_color_dictionary[player_position] = \
                rendering_info.player_outline_color
            self.player_health_color_dictionary[player_position] = \
                rendering_info.player_health_color
            self.player_health_percentage_dictionary[player_position] = \
                rendering_info.health_percentage
    
    def set_player_point_positions(
        self,
        player_position,
        player_model
    ):
        rendering_model = self.player_model_dictionary[player_position]
        
        rendering_model.set_absolute_point_positions(
            player_model.get_point_positions()
        )
        
        rendering_model.scale_in_place(self.viewport_camera.viewport_scale)
        
        position = rendering_model.get_reference_position()
        position = self.viewport_camera.get_position_in_viewport(position)
        
        rendering_model.move_model(position)

def draw_player_renderer_state(player_renderer_state, surface):
    
    for player_position in player_renderer_state.player_positions:
        draw_player(
            player_renderer_state.player_model_dictionary[player_position],
            player_renderer_state.player_health_percentage_dictionary[player_position],
            player_renderer_state.player_outline_color_dictionary[player_position],
            player_renderer_state.player_health_color_dictionary[player_position],
            surface
        )
        draw_reflection(
            player_renderer_state.player_model_dictionary[player_position],
            player_renderer_state.player_health_percentage_dictionary[player_position],
            player_renderer_state.player_outline_color_dictionary[player_position],
            player_renderer_state.player_health_color_dictionary[player_position],
            player_renderer_state.viewport_camera,
            surface
        )

def draw_player(
    model, 
    health_percentage, 
    outline_color,
    health_color,
    surface
):
    """draws the model to the screen"""
    
    enclosing_rect = pygame.Rect(*model.get_enclosing_rect())  
    
    gamestate.new_dirty_rects.append(enclosing_rect)
    
    #pygame.draw.rect(gamestate.screen, (100,100,100),enclosing_rect,1)
    
    for name, point in model.points.iteritems():
        if name != PointNames.HEAD_TOP:
            draw_outline_point(point, (0,0,0), surface)
    
    for name, line in model.lines.iteritems():
        if name == LineNames.HEAD:
            draw_outline_circle(line, (0,0,0), surface)
        else:
            #if player.action.action_state == PlayerStates.FLOATING:
            #    outline_color = (255,0,0)
            #elif player.action.action_state == PlayerStates.TRANSITION:
            #    outline_color = (0,255,0)
                
            draw_outline_line(line, (0,0,0), surface)
    
    for name, point in model.points.iteritems():
        if name != PointNames.HEAD_TOP:
            draw_outer_point(point, outline_color, surface)
    
    for name, line in model.lines.iteritems():
        if name == LineNames.HEAD:
            draw_outer_circle(line, outline_color, surface)
        else:
            draw_outer_line(line, outline_color, surface)
    
    for name, point in model.points.iteritems():
        if name != PointNames.HEAD_TOP:
            draw_inner_point(
                point,
                health_color,
                surface
            )
    
    for name, line in model.lines.iteritems():
        if name == LineNames.HEAD:
            draw_inner_circle(line, health_color, surface)
        else:
            draw_health_line(
                line,
                health_percentage,
                health_color,
                surface
            )

def draw_health_line(line, health_percentage, health_color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    health_point1 = point1
    x_delta = health_percentage * (point2[0] - health_point1[0])
    y_delta = health_percentage * (point2[1] - health_point1[1])
    health_point2 = (int(point1[0] + x_delta), int(point1[1] + y_delta))
    
    pygame.draw.line(
        surface,
        health_color,
        health_point1,
        health_point2,
        int(10)
    )

def draw_outline_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    pygame.draw.line(surface, \
                    color, \
                    point1, \
                    point2, \
                    int(18))

def draw_outer_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    pygame.draw.line(surface, \
                    color, \
                    point1, \
                    point2, \
                    int(14))

def draw_outline_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius) + 2)

def draw_outer_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius))

def draw_inner_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    if radius <= 2:
        radius = 3
    
    pygame.draw.circle(surface, \
                      color, \
                      (int(pos[0]), int(pos[1])), \
                      int(radius - 2))


def draw_outline_point(point, color, surface):
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(9))

def draw_outer_point(point, color, surface):
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(7))

def draw_inner_point(point, color, surface):
    """Draws a point on a surface
    
    surface: the pygame surface to draw the point on"""
    
    position = point.pixel_pos()
    
    pygame.draw.circle(surface, \
                       color, \
                       position, \
                       int(5))

def draw_reflection(
    model,
    health_percentage,
    outline_color,
    health_color,
    camera,
    surface
):
    """draws the reflection of the player on the given surface"""

    player_rect = pygame.Rect(*model.get_enclosing_rect())
    previous_position = (model.position[0], model.position[1])
    
    if model.orientation == Orientations.FACING_RIGHT:
        model.move_model((8,8))
    else:
        model.move_model((player_rect.width - 8, 8))
    
    #create a surface to perform the reflection on that tightly surounds the player
    reflection_surface = pygame.Surface((player_rect.width, player_rect.height))
    reflection_surface.fill((1,234,25))
    reflection_surface.set_colorkey((1,234,25))
    draw_player(
        model,
        health_percentage,
        outline_color,
        health_color,
        reflection_surface
    )
    
    #flip and scale the surface and decrease its opacity to make the reflection
    reflection_surface = pygame.transform.flip(reflection_surface, False, True)
    reflection_surface = pygame.transform.scale(
        reflection_surface,
        (
            max(int(
                player_rect.width * 
                player_rect.bottom / 
                (gamestate.stage.floor_height - camera.viewport_position[1]) /
                camera.viewport_scale
            ), 10),
            max(int(
                (.75 * player_rect.height) *
                player_rect.bottom /
                (gamestate.stage.floor_height - camera.viewport_position[1]) /
                camera.viewport_scale
            ), 10)
        )
    ).convert()
    reflection_surface.set_alpha(150)
    
    reflection_position = (
        player_rect.left,
        ((gamestate.stage.floor_height- 3) - camera.viewport_position[1]) * camera.viewport_scale
    )
    surface.blit(reflection_surface, reflection_position)
    
    gamestate.new_dirty_rects.append(
        pygame.Rect(
            reflection_position,
            (reflection_surface.get_width(), reflection_surface.get_height())
        )
    )
    
    model.move_model(previous_position)

def build_player_model_dictionary(player_positions):
    player_model_dictionary = {}
    
    for player_position in player_positions:
        player_model = Model((0,0))
        player_model.init_stick_data()
        
        player_model_dictionary[player_position] = player_model
    
    return player_model_dictionary

def build_player_health_percentage_dictionary(player_positions):
    player_health_percentage_dictionary = {}
    
    for player_position in player_positions:
        player_health_percentage_dictionary[player_position] = 1
    
    return player_health_percentage_dictionary

serializable.register(PlayerColors)
