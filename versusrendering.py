from random import choice
import pygame
import gamestate
import wotsrendering
import mathfuncs
from wotsprot.rencode import serializable
from enumerations import PlayerPositions, PointNames, LineNames
from physics import Model, Orientations

Y_PAN_RATE = 10
PAN_RATE = 10
SCALE_RATE = .01
SHAKE_MAX_DELTA = 20

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
        self.full_zoom_scale = 1
        self.zoom_count = 3
        self.zoom_threshold = 20
        self.pan_threshold = 10
        self.shake_delta_timer = 0
        self.shake_hold_duration = 100
        self.shake_delta = [0,0]
        self.shake_indicator = False
        self.shake_decay = .5
        self.full_zoom_only = False #True
    
    def start_shaking(self, shake_delta):
        self.shake_delta_timer = 0
        self.set_shake_delta(shake_delta)
        self.shake_indicator = True
    
    def set_shake_delta(self, shake_delta):
        delta = min(10, shake_delta)
        self.shake_delta[0] = choice((delta, -delta))
        self.shake_delta[1] = choice((delta, -delta))
    
    def shake(self):
        self.viewport_position = (
            self.viewport_position[0] + self.shake_delta[0],
            self.viewport_position[1] + self.shake_delta[1]
        )
        
        self.shake_delta_timer += gamestate.time_passed
        
        if self.shake_delta_timer > self.shake_hold_duration:
            self.shake_delta[0] = -float(self.shake_delta[0] * self.shake_decay)
            self.shake_delta[1] = -float(self.shake_delta[1] * self.shake_decay)
            self.shake_delta_timer = 0
        
        if self.shake_delta < 5:
            self.shake_indicator = False
    
    def update(self, constraining_rect):
        if self.shake_indicator:
            self.shake()
        
        target_rect = self.get_target_rect(constraining_rect)
        scale = self.calc_viewport_scale(constraining_rect, target_rect)
        
        #if not self.can_zoom(target_rect):
        #    scale = self.viewport_scale
        
        pan_deltas = self.get_pan_deltas(
            scale,
            constraining_rect,
            target_rect
        )
        
        self.viewport_scale = scale
        self.viewport_position = (
            self.viewport_position[0] + pan_deltas[0],
            self.viewport_position[1] + pan_deltas[1]
        )
    
    def get_target_rect(self, constraining_rect):
        
        containing_rects = [    
            camera_rect
            for camera_rect in gamestate.stage.camera_rects
            if camera_rect.contains(constraining_rect)
        ]
        
        def squared_distance(containing_rect):
            return mathfuncs.squared_distance(containing_rect.center, constraining_rect.center)
        
        if len(containing_rects) > 0:
            target_rect = min(containing_rects, key=squared_distance)
        else:
            target_rect = gamestate.stage.camera_rects[0]
        
        return target_rect
    
    def get_distance_in_viewport(self, distance):
        if self.full_zoom_only:
            return distance * self.viewport_width / float(self.world_width)
        else:
            return distance * self.viewport_scale
    
    def get_position_in_viewport(self, position):
        if self.full_zoom_only:
            return self.get_full_zoom_position(position)
        else:
            return self.get_viewport_zoom_position(position)
    
    def get_viewport_scale(self):
        if self.full_zoom_only:
            return self.viewport_width / float(self.world_width)
        else:
            return self.viewport_scale
    
    def get_viewport_zoom_position(self, position):
        return (
            (position[0] - self.viewport_position[0]) * self.viewport_scale,
            (position[1] - self.viewport_position[1]) * self.viewport_scale
        )
    
    def get_full_zoom_position(self, position):
        return (
            position[0] * self.viewport_width / float(self.world_width),
            position[1] * self.viewport_width / float(self.world_width)
        )
    
    def calc_viewport_scale(self, constraining_rect, target_rect):
        """determine the scale of world objects on the viewport by forcing the
        viewport to include all rects in the constraining_rects.
        
        constraining_rect: a rect that contains everything in the world that 
        must appear in the viewport. The rect should be at world scale and 
        positioned in world coordinates.
        """
        scale = self.viewport_scale
        target_scale = 1
        constraining_scale = 1
        
        min_x_position = target_rect.left
        min_y_position = target_rect.top
        max_x_position = target_rect.right
        max_y_position = target_rect.bottom
        
        x_dist = max_x_position - min_x_position
        y_dist = max_y_position - min_y_position
        x_diff = max_x_position - min_x_position#x_dist - self.viewport_width
        y_diff = max_y_position - min_y_position#y_dist - self.viewport_height
        
        if x_diff > 0 and y_diff > 0:
            if x_diff > y_diff:
                target_scale = float(self.viewport_width) / target_rect.width
                constraining_scale = float(self.viewport_width) / constraining_rect.width
            else:
                target_scale = float(self.viewport_height) / target_rect.height
                constraining_scale = float(self.viewport_height) / constraining_rect.height
        elif x_diff > 0:
            target_scale = float(self.viewport_width) / target_rect.width
            constraining_scale = float(self.viewport_width) / constraining_rect.width
        elif y_diff > 0:
            target_scale = float(self.viewport_height) / target_rect.height
            constraining_scale = float(self.viewport_height) / constraining_rect.height
        else:
            pass #no scaling is required.
        
        if target_scale > self.viewport_scale:
            scale = min(target_scale, self.viewport_scale + SCALE_RATE)
            
        elif target_scale < self.viewport_scale:
            scale = max(target_scale, self.viewport_scale - SCALE_RATE)
        
        if constraining_scale < scale:
            scale = constraining_scale
        
        return scale
    
    def get_pan_deltas(
        self,
        scale,
        constraining_rect,
        target_rect
    ):
        """determine the distance to move from the current viewport position"""
        min_x_position = constraining_rect.left
        min_y_position = constraining_rect.top
        max_x_position = constraining_rect.right
        max_y_position = constraining_rect.bottom
        
        target_position = target_rect.topleft #self.get_target_position(scale, target_rect)
        x_position = target_position[0]
        y_position = target_position[1]
        
        x_pan_delta = 0
        y_pan_delta = 0
        
        if abs(self.viewport_position[0] - x_position) > self.pan_threshold:
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
        
        if abs(self.viewport_position[1] - y_position) > self.pan_threshold:
            if y_position > self.viewport_position[1]:
                y_pan_delta = max(
                    min(y_position - self.viewport_position[1], Y_PAN_RATE),
                    max_y_position - (self.viewport_position[1] + (self.viewport_height / self.viewport_scale))
                )
            else:
                y_pan_delta = min(
                    max(y_position - self.viewport_position[1], -Y_PAN_RATE),
                    min_y_position - self.viewport_position[1]
                )
        
        #Force smooth panning when scaling
        x_diff = x_position - self.viewport_position[0]
        y_diff = y_position - self.viewport_position[1]
        
        if y_diff > 0:
            ratio = x_diff / float(y_diff)
            
            if ratio > 0:
                if x_pan_delta <> 0:
                    y_pan_delta = x_pan_delta / float(ratio)
                elif y_pan_delta <> 0:
                    x_pan_delta = y_pan_delta * float(ratio)
        
        #Force world to stay in view
        new_viewport_right = self.viewport_position[0] + (self.viewport_width / scale) + x_pan_delta
        new_viewport_left = self.viewport_position[0] + x_pan_delta
        
        #if new_viewport_left < gamestate.stage.constraining_rect.left:
        #    x_pan_delta = min(gamestate.stage.constraining_rect.left - self.viewport_position[0], 0)
        if new_viewport_right > gamestate.stage.constraining_rect.right:
            x_pan_delta = gamestate.stage.constraining_rect.right - new_viewport_right
            #NOTE sometimes the corrected pan delata is 10 pixesl bigger the constraining right
        
        new_viewport_bottom = self.viewport_position[1] + (self.viewport_height / scale) + y_pan_delta
        new_viewport_top = self.viewport_position[1] + y_pan_delta
        
        #if new_viewport_top < gamestate.stage.constraining_rect.top:
        #    y_pan_delta = max(gamestate.stage.constraining_rect.top - self.viewport_position[1], 0)
        if new_viewport_bottom > gamestate.stage.constraining_rect.bottom:
            y_pan_delta = gamestate.stage.constraining_rect.bottom - new_viewport_bottom
        
        #Force players to be in view
        new_viewport_right = self.viewport_position[0] + (self.viewport_width / scale) + x_pan_delta
        new_viewport_left = self.viewport_position[0] + x_pan_delta
        
        #if new_viewport_left < gamestate.stage.constraining_rect.left:
        #    x_pan_delta = min(gamestate.stage.constraining_rect.left - self.viewport_position[0], 0)
        if new_viewport_right < constraining_rect.right:
            x_pan_delta = constraining_rect.right - new_viewport_right        
        
        new_viewport_bottom = self.viewport_position[1] + (self.viewport_height / scale) + y_pan_delta
        new_viewport_top = self.viewport_position[1] + y_pan_delta
        
        #if new_viewport_top < gamestate.stage.constraining_rect.top:
        #    y_pan_delta = max(gamestate.stage.constraining_rect.top - self.viewport_position[1], 0)
        if new_viewport_bottom < constraining_rect.bottom:
            #print("Correcting!")
            #print("viewport bottom: " + str(new_viewport_bottom))
            #print("player bottom: " + str(constraining_rect.bottom))
            y_pan_delta = constraining_rect.bottom - new_viewport_bottom
            #print(y_pan_delta)
        
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
    
    def draw_polygon(self, layer, points, color, line_width=0):
        
        polygon_points = [
            self.viewport_camera.get_position_in_viewport(point)
            for point in points
        ]
        
        if len(points) == 3:
            gamestate.new_dirty_rects.append(self.get_enclosing_rect(polygon_points, line_width))
            wotsrendering.queue_polygon(layer, gamestate.screen, color, polygon_points, line_width)
        else:
            gamestate.new_dirty_rects.append(self.get_enclosing_rect(polygon_points[0:3], line_width))
            wotsrendering.queue_polygon(layer, gamestate.screen, color, polygon_points[0:3], line_width)
            
            gamestate.new_dirty_rects.append(self.get_enclosing_rect(polygon_points[-3:], line_width))
            wotsrendering.queue_polygon(layer, gamestate.screen, color, polygon_points[-3:], line_width)
        
    def get_enclosing_rect(self, points, line_width):
        min_position = map(min, zip(*points))
        max_position = map(max, zip(*points))
        
        min_position[0] -= line_width
        min_position[1] -= line_width
        max_position[0] += line_width
        max_position[1] += line_width
        
        width = max_position[0] - min_position[0]
        height = max_position[1] - min_position[1]
        
        return pygame.Rect(min_position, (width, height))
    
    def draw_surface_to_screen(self, layer, position, surface):
        
        surface_viewport_position = self.viewport_camera.get_position_in_viewport(
            position
        )
        
        scaled_surface = pygame.transform.scale(
            surface,
            (
                int(surface.get_width() * self.viewport_camera.get_viewport_scale()),
                int(surface.get_height() * self.viewport_camera.get_viewport_scale())
            )
        )
        
        wotsrendering.queue_surface(layer, gamestate.screen, scaled_surface, surface_viewport_position)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                surface_viewport_position,
                (scaled_surface.get_width(), scaled_surface.get_height())
            )
        )
    
    def draw_surface_to_absolute_position(self, layer, position, surface):
        wotsrendering.queue_surface(layer, gamestate.screen, surface, position)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                position,
                (surface.get_width(), surface.get_height())
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
        
        position = rendering_model.position
        position = self.viewport_camera.get_position_in_viewport(position)
        
        rendering_model.scale_in_place(self.viewport_camera.get_viewport_scale())
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
        
        if gamestate.stage.draw_reflections:
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
    
    #enclosing_rects = []
    
    #if gamestate.devmode:
    #    pygame.draw.rect(gamestate.screen, (100,100,100),enclosing_rect,1)
    
    for name, point in model.points.iteritems():
        if name != PointNames.HEAD_TOP:
            #enclosing_rects.append(draw_outline_point(point, (0,0,0), surface))
            draw_outline_point(point, (0,0,0), surface)
    
    for name, line in model.lines.iteritems():
        if name == LineNames.HEAD:
            #enclosing_rects.append(draw_outline_circle(line, (0,0,0), surface))
            draw_outline_circle(line, (0,0,0), surface)
        else:
            #if player.action.action_state == PlayerStates.FLOATING:
            #    outline_color = (255,0,0)
            #elif player.action.action_state == PlayerStates.TRANSITION:
            #    outline_color = (0,255,0)
                
            #enclosing_rects.append(draw_outline_line(line, (0,0,0), surface))
            draw_outline_line(line, (0,0,0), surface)
    
    #gamestate.new_dirty_rects.append(enclosing_rects[0].unionall(enclosing_rects))
    
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
                health_color,
                surface
            )

def draw_health_line(line, health_color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    wotsrendering.queue_line(
        2,
        surface,
        health_color,
        point1,
        point2,
        int(10)
    )

def draw_outline_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    wotsrendering.queue_line(
        1,
        surface,
        color,
        point1,
        point2,
        int(18)
    )
    
    top_left = map(min, zip(point1, point2))
    bottom_right = map(max, zip(point1, point2))
    
    return pygame.Rect(top_left, (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))

def draw_outer_line(line, color, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    wotsrendering.queue_line(
        1,
        surface,
        color,
        point1,
        point2,
        int(14)
    )

def draw_outline_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    wotsrendering.queue_circle(
        1,
        surface,
        color,
        (int(pos[0]), int(pos[1])),
        int(radius) + 2
    )
    
    return pygame.Rect(
        (pos[0] - radius - 2, pos[1] - radius - 2), 
        (2 * (radius + 2), 2 * (radius + 2))
    )

def draw_outer_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    wotsrendering.queue_circle(
        1,
        surface,
        color,
        (int(pos[0]), int(pos[1])),
        int(radius)
    )

def draw_inner_circle(circle, color, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                      circle.endPoint2.pos))
    pos = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    if radius <= 2:
        radius = 3
    
    wotsrendering.queue_circle(
        2,
        surface,
        color,
        (int(pos[0]), int(pos[1])),
        int(radius - 2)
    )


def draw_outline_point(point, color, surface):
    position = point.pixel_pos()
    
    wotsrendering.queue_circle(
        1,
        surface,
        color,
        position,
        int(9)
    )
    
    return pygame.Rect(
        (position[0] - 9, position[1] - 9), 
        (18, 18)
    )

def draw_outer_point(point, color, surface):
    position = point.pixel_pos()
    
    wotsrendering.queue_circle(
        1,
        surface,
        color,
        position,
        int(7)
    )

def draw_inner_point(point, color, surface):
    """Draws a point on a surface
    
    surface: the pygame surface to draw the point on"""
    
    position = point.pixel_pos()
    
    wotsrendering.queue_circle(
        2,
        surface,
        color,
        position,
        int(5)
    )

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
    
    def reflection_transform(surface, reflection_surface, player_rect, camera):
        #flip and scale the surface and decrease its opacity to make the reflection
        reflection_surface = pygame.transform.flip(reflection_surface, False, True)
        reflection_surface = pygame.transform.scale(
            reflection_surface,
            (
                max(int(
                    player_rect.width * 
                    player_rect.bottom / 
                    (gamestate.stage.floor_height - camera.viewport_position[1]) /
                    camera.get_viewport_scale()
                ), 10),
                max(int(
                    (.75 * player_rect.height) *
                    player_rect.bottom /
                    (gamestate.stage.floor_height - camera.viewport_position[1]) /
                    camera.get_viewport_scale()
                ), 10)
            )
        ).convert()
        reflection_surface.set_alpha(150)
        
        reflection_position = (
            player_rect.left,
            ((gamestate.stage.floor_height- 3) - camera.viewport_position[1]) * camera.get_viewport_scale()
        )
        wotsrendering.queue_surface(
            3, 
            surface, 
            reflection_surface, 
            reflection_position
        )
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                reflection_position,
                (reflection_surface.get_width(), reflection_surface.get_height())
            )
        )
    wotsrendering.queue_rendering_function(
        3, 
        reflection_transform, 
        (surface, reflection_surface, player_rect, camera)
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
