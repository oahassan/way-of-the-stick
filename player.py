import copy
import math
from random import choice

import pygame

import gamestate
import animation
import animationexplorer
import physics
import mathfuncs
import stick
import pulltool
from enumerations import InputActionTypes
import settingsdata
from playerutils import Transition
from playerconstants import *

class PlayerTypes:
    HUMAN = 'Human'
    BOT = 'Bot'
    REMOTE = 'Remote'

class AnimationModes():
    PHYSICS = "PHYSICS"
    KEYFRAME = "KEYFRAME"
    HYBRID = "HYBRID"

class PlayerStates():
    FACING_RIGHT = 'FACING_RIGHT'
    FACING_LEFT = 'FACING_LEFT'
    STANDING = 'STANDING'
    WALKING = 'WALKING'
    RUNNING = 'RUNNING'
    JUMPING = 'JUMPING'
    FLOATING = 'FLOATING'
    LANDING = 'LANDING'
    ATTACKING = 'ATTACKING'
    CROUCHING = 'CROUCHING'
    STUNNED = 'STUNNED'
    BLOCKING = 'BLOCKING'
    TRANSITION = 'TRANSITION'
    
    GROUND_STATES = [STANDING, CROUCHING, WALKING, RUNNING]
    
    MOVEMENTS = [STANDING,WALKING,RUNNING,JUMPING,FLOATING, \
                 LANDING,CROUCHING]
    
    UNBOUND_MOVEMENTS = [STANDING,FLOATING,LANDING,STUNNED, \
                        TRANSITION]
    
    PRESSED_KEY_STATE_TRANSITIONS = {
        STANDING : [WALKING,RUNNING,JUMPING,CROUCHING,ATTACKING],
        WALKING : [STANDING,JUMPING,CROUCHING,ATTACKING],
        RUNNING : [STANDING,JUMPING,CROUCHING,ATTACKING],
        CROUCHING : [STANDING,ATTACKING],
        JUMPING : [FLOATING,LANDING,ATTACKING],
        LANDING : [STANDING,CROUCHING,ATTACKING,JUMPING,WALKING,RUNNING],
        FLOATING : [LANDING,ATTACKING,FLOATING],
        ATTACKING : [STANDING, FLOATING],
        STUNNED : [],
        BLOCKING : [STANDING,CROUCHING],
        TRANSITION : [ATTACKING]
    }

class Player():
    
    def __init__(self, position):
        self.player_type = None
        self.current_attack = None
        self.action = None
        self.color = (255,255,255)
        self.outline_color = self.color
        self.current_animation = None
        self.direction = PlayerStates.FACING_RIGHT
        self.stun_timeout = 500
        self.stun_timer = self.stun_timeout
        self.dash_timeout = 500
        self.dash_timer = self.dash_timeout
        self.high_jump_timeout = 300
        self.short_jump_timeout = 200
        self.jump_timer = self.high_jump_timeout
        self.model = physics.Model(position)
        self.walk_speed = .4
        self.run_speed = .75
        self.jump_speed = -.5
        self.high_jump_speed = -.75
        self.size = 5
        self.power = 5
        self.speed = 5
        self.weight = 5
        self.max_stun_velocity = 1
        self.tap_stun_acceleration = .05
        self.hold_stun_acceleration = .01
        self.aerial_acceleration = .01
        self.max_aerial_velocity = .1
        self.actions = {}
        self.knockback_vector = (0,0)
        self.interaction_vector = (0,0)
        self.interaction_point = None
        self.knockback_multiplier = 4
        self.health_max = 2000
        self.health_meter = self.health_max
        self.health_color = (0,0,100)
        self.moveset = None
        self.point_name_to_point_damage = {} #Point name to PointDamage object
        self.previous_point_positions = {}
        self.handle_input_events = True
    
    def set_player_stats(self, size):
        self.size = size
    
    def get_animation_height(self):
        return 50 + (10 * self.size)
    
    def init_state(self):
        self.model.load_points()
        self.model.load_lines()
        self.init_point_damage_dictionary()
    
    def handle_events(self, time_passed):
        
        self.model.time_passed = time_passed
        
        self.set_previous_point_positions()
        
        self.action.move_player(self)
        
        if self.action.action_state == PlayerStates.ATTACKING:
            self.update_point_damage()
        
        self.set_outline_color()
        
        if self.dash_timer < self.dash_timeout:
            self.dash_timer += time_passed
        
        if self.jump_timer < self.high_jump_timeout:
            self.jump_timer += time_passed
        
        if self.stun_timer < self.stun_timeout:
            self.stun_timer += time_passed
    
    def set_outline_color(self):
        if self.get_player_state() == PlayerStates.STUNNED:
            if (self.stun_timer % 30) >= 15:
                self.outline_color = (255, 255, 0)
            else:
                self.outline_color = (255, 0, 0)
        else:
            self.outline_color = self.color
    
    def move_to_ground(self):
        
        position = (
            self.model.position[0], 
            int(math.ceil(gamestate.stage.ground.position[1] - self.model.height))
        )
        self.model.move_model(position)
    
    def get_player_point_positions(self):
        """builds a dictionary of point name to point position for each point in the
        model"""
        
        return_dictionary = {}
        
        for point_name, point in self.model.points.iteritems():
            return_dictionary[point_name] = point.pos
        
        return return_dictionary
    
    def set_previous_point_positions(self):
        
        self.previous_point_positions = self.get_player_point_positions()
    
    def get_previous_point_position(self, point_name):
        """Get the previous position of the point from the previous points dictionary.
        If the dictionary doesn't exist yet return the current position of the point."""
        
        if point_name in self.previous_point_positions.keys():
            return self.previous_point_positions[point_name]
            
        else:
            return self.model.points[point_name].pos
    
    def get_point_position_change(self, point_name):
        """Get the change in position of a point between now and the previous 
        game loop"""
        
        current_position = self.model.points[point_name].pos
        previous_position = self.get_previous_point_position(point_name)
        
        return \
            current_position[0] - previous_position[0], \
            current_position[1] - previous_position[1]
    
    def set_action(self):
        pass
    
    def handle_animation_end(self):
        self.action.last_frame_index = 0
        
        if self.action.action_state == PlayerStates.JUMPING:
            self.transition(self.actions[PlayerStates.FLOATING])
        elif self.action.action_state == PlayerStates.LANDING:
            self.transition(self.get_neutral_state())
        elif self.action.action_state == PlayerStates.ATTACKING:
            self.current_attack = None
            self.transition(self.get_neutral_state())
        elif self.action.action_state == PlayerStates.TRANSITION:
            self.action.next_action.set_player_state(self)
        elif self.action.action_state == PlayerStates.STUNNED:
            self.transition(self.get_neutral_state())
        elif self.action.action_state == PlayerStates.STANDING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.FLOATING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.CROUCHING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.WALKING:
            self.action.set_player_state(self)
        elif self.action.action_state == PlayerStates.RUNNING:
            self.action.set_player_state(self)
    
    def transition(self, next_state):
        transition = Transition()
        transition.init_transition(self, next_state)
        transition.set_player_state(self)
    
    def set_neutral_state(self):
        self.get_neutral_state().set_player_state(self)
    
    def get_neutral_state(self):
        if self.get_player_state() == PlayerStates.LANDING:
            return self.actions[PlayerStates.STANDING]
        else:
            if self.is_aerial():
                return self.actions[PlayerStates.FLOATING]
            else:
                return self.actions[PlayerStates.STANDING]
    
    def set_velocity(self):
        velocity = self.model.velocity
        friction = self.model.friction
        
        if self.direction == PlayerStates.FACING_RIGHT:
            if self.action.action_state == PlayerStates.WALKING:
                self.model.velocity = (self.walk_speed + friction, velocity[1])
            elif self.action.action_state == PlayerStates.RUNNING:
                self.model.velocity = (self.run_speed + friction, velocity[1])
        elif self.direction == PlayerStates.FACING_LEFT:
            if self.action.action_state == PlayerStates.WALKING:
                self.model.velocity = (-(self.walk_speed + friction), velocity[1])
            elif self.action.action_state == PlayerStates.RUNNING:
                self.model.velocity = (-(self.run_speed + friction), velocity[1])
    
    def get_player_state(self):
        """returns the current state of the player"""
        return self.action.action_state
    
    def set_player_state(self, player_state):
        """sets the current state of the player"""
        
        if self.actions[player_state].test_state_change(self):
            self.actions[player_state].set_player_state(self)
    
    def get_attack_lines(self):
        return self.action.attack_lines
    
    def get_point(self, point_name):
        return self.model.points[point_name]
    
    def init_point_damage_dictionary(self):
        """initializes the point damage dictionary. NOTE: model must be intialized before
        calling."""
        for line_name in self.model.lines.keys():
            for point_name in stick.LINE_TO_POINTS[line_name]:
                if point_name not in self.point_name_to_point_damage.keys():
                    self.point_name_to_point_damage[point_name] = 0
    
    def update_point_damage(self):
        """updates the damage done by each attacking point"""
        
        current_point_positions_dictionary = self.get_player_point_positions()
        
        
        
        for point_name in self.point_name_to_point_damage.keys():
            
            current_relative_position = \
                self.get_point_relative_position(
                    point_name,
                    current_point_positions_dictionary
                )
            
            previous_relative_position = \
                self.get_point_relative_position(
                    point_name,
                    self.previous_point_positions
                )
            
            additional_damage = \
                min(
                    self.get_max_attack_damage(),
                    (mathfuncs.distance(
                        current_relative_position,
                        previous_relative_position
                    ) + self.get_extension_damage(
                        point_name,
                        current_point_positions_dictionary
                    )) * self.get_damage_growth_rate()
                )
            
            self.point_name_to_point_damage[point_name] += additional_damage
    
    def get_extension_damage(self, point_name, current_point_positions):
        if point_name == stick.PointNames.RIGHT_HAND:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.RIGHT_ELBOW,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_ELBOW:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_TOP,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_HAND:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.LEFT_ELBOW,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_ELBOW:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_TOP,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_FOOT:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.RIGHT_KNEE,
                current_point_positions
            )
        elif point_name == stick.PointNames.RIGHT_KNEE:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_BOTTOM,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_FOOT:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.LEFT_KNEE,
                current_point_positions
            )
        elif point_name == stick.PointNames.LEFT_KNEE:
            return self.get_line_length_change(
                point_name,
                stick.PointNames.TORSO_BOTTOM,
                current_point_positions
            )
        else:
            return 0
    
    def get_line_length_change(
        self,
        point1_name,
        point2_name,
        current_point_positions
    ):
        point1_prev_position = self.previous_point_positions[point1_name]
        point2_prev_position = self.previous_point_positions[point2_name]
        
        prev_line_length = mathfuncs.distance(
            point1_prev_position,
            point2_prev_position
        )
        
        point1_position = current_point_positions[point1_name]
        point2_position = current_point_positions[point2_name]
        
        current_line_length = mathfuncs.distance(
            point1_position,
            point2_position
        )
        
        return abs(current_line_length - prev_line_length)
    
    def get_point_relative_position(self, point_name, point_position_dictionary):
        """determines the relative position of point based on the positions in the 
        point_position_dictionary"""
        
        point_position = point_position_dictionary[point_name]
        left, top = point_position_dictionary[point_name]
        
        for position in point_position_dictionary.values():
            
            if position[0] < left:
                left = position[0]
                
            if position[1] < top:
                top = position[1]
        
        return point_position[0] - left, point_position[1] - top
    
    def reset_point_damage(self):
        """sets the point damage for each point at the start of an attack"""
        
        for point_name in self.point_name_to_point_damage.keys():
            
            self.point_name_to_point_damage[point_name] = 0
    
    def get_point_damage(self, point_name):
        """Returns the damage dealt when attacked from the given point"""
        return self.point_name_to_point_damage[point_name]
    
    def get_stun_timeout(self):
        """only call when attacking"""
        return 1 / self.get_attack_acceleration()
    
    def get_attack_type(self):
        return self.action.attack_type
    
    def get_max_attack_damage(self):
        if (self.get_attack_type() in 
        [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]):
            return WEAK_ATTACK_MAX_DAMAGE
            
        elif (self.get_attack_type() in 
        [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]):
            return MEDIUM_ATTACK_MAX_DAMAGE
            
        elif (self.get_attack_type() in 
        [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]):
            return STRONG_ATTACK_MAX_DAMAGE
    
    def get_damage_growth_rate(self):
        if (self.get_attack_type() in 
        [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]):
            return WEAK_DAMAGE_GROWTH_RATE
            
        elif (self.get_attack_type() in 
        [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]):
            return MEDIUM_DAMAGE_GROWTH_RATE
            
        elif (self.get_attack_type() in 
        [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]):
            return STRONG_DAMAGE_GROWTH_RATE
    
    def get_attack_acceleration(self):
        
        if (self.get_attack_type() in 
        [InputActionTypes.WEAK_PUNCH, InputActionTypes.WEAK_KICK]):
            return 2 * ACCELERATION
            
        elif (self.get_attack_type() in 
        [InputActionTypes.MEDIUM_PUNCH, InputActionTypes.MEDIUM_KICK]):
            return ACCELERATION
            
        elif (self.get_attack_type() in 
        [InputActionTypes.STRONG_PUNCH, InputActionTypes.STRONG_KICK]):
            return .5 * ACCELERATION
    
    def set_stun_timeout(self, timeout):
        self.stun_timeout = timeout
    
    def set_pull_point(self, point):
        self.pull_point = point
    
    def pull_point(self, deltas):
        pull_point_pos = self.interaction_point.pos
        new_pos = (pull_point_pos[0] + deltas[0],
                   pull_point_pos[1] + deltas[1])
        point_to_lines = self.model.build_point_to_lines(self.model.lines.values())
        
        self.model.pull_point(
            self.interaction_point,
            new_pos,
            self.interaction_point,
            [],
            point_to_lines
        )
        
        self.model.position = self.model.get_reference_position()
        self.model.set_dimensions()
    
    def set_health(self, health_value):
        
        self.health_meter = health_value
    
    def get_enclosing_rect(self):
        return pygame.Rect(*self.model.get_enclosing_rect())
    
    def attack_in_range(self, attack, enemy):
        bottom_right_top_left = self.model.get_top_left_and_bottom_right()
        bottom_right = bottom_right_top_left[1]
        top_left = bottom_right_top_left[0]
        
        attack_range_point = top_left
        
        if self.direction == PlayerStates.FACING_LEFT:
            attack_range_point = (bottom_right[0] - attack.range[0], \
                                  top_left[1])
        
        attack_rect = pygame.Rect(attack_range_point, (attack.range[0], attack.range[1]))
        enemy_rect = pygame.Rect(enemy.model.position, (enemy.model.width, enemy.model.height))
        
        in_range = attack_rect.colliderect(enemy_rect)
        
        return in_range
    
    def is_aerial(self):
        if self.action.action_state in PlayerStates.GROUND_STATES:
            return False
        elif self.action.action_state == PlayerStates.TRANSITION:
            if self.action.last_action.action_state in PlayerStates.GROUND_STATES:
                return False
            else:
                return int(self.model.position[1] + self.model.height) < gamestate.stage.ground.position[1]
        else:
            return int(self.model.position[1] + self.model.height) < gamestate.stage.ground.position[1]
    
    def apply_physics(self, duration, gravity = True):
        
        system = []
        
        self.set_velocity()
        self.model.resolve_self(duration, gravity)
        
        if self.is_aerial() == False:
            system.append(gamestate.stage.ground)
            
            if (((self.action.action_state == PlayerStates.FLOATING)
            or  (self.action.action_state == PlayerStates.JUMPING)) and
            (mathfuncs.sign(self.model.velocity[1]) > 0)):
                self.transition(self.actions[PlayerStates.LANDING])
        
        if self.model.orientation == physics.Orientations.FACING_RIGHT:
            if self.model.position[0] + self.model.width > gamestate.stage.right_wall.position[0]:
                system.append(gamestate.stage.right_wall)
        elif self.model.orientation == physics.Orientations.FACING_LEFT:
            if self.model.position[0] > gamestate.stage.right_wall.position[0]:
                system.append(gamestate.stage.right_wall)
        
        if self.model.orientation == physics.Orientations.FACING_RIGHT:
            if self.model.position[0] < gamestate.stage.left_wall.position[0]:
                system.append(gamestate.stage.left_wall)
        elif self.model.orientation == physics.Orientations.FACING_LEFT:
            if self.model.position[0] - self.model.width < gamestate.stage.left_wall.position[0]:
                system.append(gamestate.stage.left_wall)
        
        self.model.resolve_system(system, duration)

def draw_model(player, surface):
    """draws the model to the screen"""
    
    enclosing_rect = pygame.Rect(*player.model.get_enclosing_rect())  
    
    gamestate.new_dirty_rects.append(enclosing_rect)
    
    #pygame.draw.rect(gamestate.screen, (100,100,100),enclosing_rect,1)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_outline_point(point, (0,0,0), surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_outline_circle(line, (0,0,0), surface)
        else:
            outline_color = (0,0,0)
            #if player.action.action_state == PlayerStates.FLOATING:
            #    outline_color = (255,0,0)
            #elif player.action.action_state == PlayerStates.TRANSITION:
            #    outline_color = (0,255,0)
                
            draw_outline_line(line, outline_color, surface)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_outer_point(point, player.outline_color, surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_outer_circle(line, player.outline_color, surface)
        else:
            draw_outer_line(line, player.outline_color, surface)
    
    for name, point in player.model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_inner_point(point, player.health_color, surface)
    
    for name, line in player.model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_inner_circle(line, player.health_color, surface)
        else:
            draw_health_line(line, player, surface)

def draw_health_line(line, player, surface):
    point1 = line.endPoint1.pixel_pos()
    point2 = line.endPoint2.pixel_pos()
    
    health_point1 = point1
    health_level = float(player.health_meter) / player.health_max
    x_delta = health_level * (point2[0] - health_point1[0])
    y_delta = health_level * (point2[1] - health_point1[1])
    health_point2 = (point1[0] + x_delta, point1[1] + y_delta)
    
    pygame.draw.line(surface, \
                    player.health_color, \
                    health_point1, \
                    health_point2, \
                    int(10))

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

def draw_reflection(player, surface):
    """draws the reflection of the player on the given surface"""

    player_rect = pygame.Rect(*player.model.get_enclosing_rect())
    previous_position = (player.model.position[0], player.model.position[1])
    
    if player.model.orientation == physics.Orientations.FACING_RIGHT:
        player.model.move_model((8,8))
    else:
        player.model.move_model((player_rect.width - 8, 8))
    
    #create a surface to perform the reflection on that tightly surounds the player
    reflection_surface = pygame.Surface((player_rect.width, player_rect.height))
    reflection_surface.fill((1,234,25))
    reflection_surface.set_colorkey((1,234,25))
    draw_model(player, reflection_surface)
    
    #flip and scale the surface and decrease its opacity to make the reflection
    reflection_surface = pygame.transform.flip(reflection_surface, False, True)
    reflection_surface = pygame.transform.scale(
        reflection_surface,
        (
            max(int(player_rect.width * player_rect.bottom / gamestate.stage.floor_height), 10),
            max(int(
                (.75 * player_rect.height) *
                player_rect.bottom /
                gamestate.stage.floor_height
            ), 10)
        )
    ).convert()
    reflection_surface.set_alpha(150)
    
    reflection_position = (player_rect.left, gamestate.stage.floor_height - 3)
    surface.blit(reflection_surface, reflection_position)
    
    gamestate.new_dirty_rects.append(
        pygame.Rect(
            reflection_position,
            (reflection_surface.get_width(), reflection_surface.get_height())
        )
    )
    
    player.model.move_model(previous_position)
