import sys
from random import random, choice
import math
import pygame

from wotsfx import HitEffect, ClashEffect
from wotsuicontainers import TextBox
from chatui import MessageEntryBox
import wotsuievents
from button import Label
from mathfuncs import distance, sign

POINT_COUNT = 10
POINT_RADIUS = 2
PARTICLE_RADIUS = 20
COLOR_KEY = (3,233,1)

class ForceField():
    def __init__(
        self,
        reference_position,
        height,
        width,
    ):
        self.height = height
        self.width = width
        self.tile_height = 0
        self.tile_width = 0
        self.tiles = []
        self.gravity_tiles = []
        self.reference_position = reference_position
    
    def set_tiles(self, tile_height, tile_width):
        self.tiles = []
        
        self.tile_height = tile_height
        self.tile_width = tile_width
        
        col_count = self.width / tile_width
        row_count = self.height / tile_height
        
        for i in range(row_count):
            self.tiles.append([])
            
            for j in range(col_count):
                self.tiles[i].append(
                    ForceTile(
                        ((j + 1) * tile_width, (i + 1) * tile_height),
                        self.tile_width, 
                        self.tile_height
                    )
                )
        
    def get_tile(self, position):
        
        if self.contains(position):
            relative_position = self.get_relative_position(position)
            
            row_index = int(relative_position[1] / self.tile_height) - 1
            col_index = int(relative_position[0] / self.tile_width) - 1
        
            return self.tiles[row_index][col_index]
        
        else:
            return None
    
    def contains(self, position):
        if (position[0] < self.reference_position[0] or
        position[0] > self.reference_position[0] + self.width or
        position[1] < self.reference_position[1] or
        position[1] > self.reference_position[1] + self.height):
            return False
        else:
            return True
    
    def get_relative_position(self, absolute_position):
        return (
            absolute_position[0] - self.reference_position[0], 
            absolute_position[1] - self.reference_position[1]
        )
    
    def get_absolute_position(self, relative_position):
        return (
            self.reference_position[0] + relative_position[0], 
            self.reference_position[1] + relative_position[1]
        )
    
    def increase_gravity(self, position, acceleration):
        if self.contains(position):
            
            tile = self.get_tile(position)
            tile.gravity += acceleration
            
            if not (tile in self.gravity_tiles):
                self.gravity_tiles.append(tile)
            elif tile.gravity == 0:
                self.gravity_tiles.remove(tile)
            
            for row in self.tiles:
                for tile in row:
                    self.set_tile_acceleration(tile)
    
    def set_tile_acceleration(self, tile):
        x_acceleration = 0
        y_acceleration = 0
        
        for gravity_tile in self.gravity_tiles:
            length = distance(gravity_tile.position, tile.position)
            
            if length > 0:
                x_delta = tile.position[0] - gravity_tile.position[0]
                y_delta = tile.position[1] - gravity_tile.position[1]
                
                inverse_distance = -1/(length)
                x_acceleration += gravity_tile.gravity * x_delta/length * inverse_distance
                y_acceleration += gravity_tile.gravity * y_delta/length * inverse_distance
        
        tile.acceleration[0] = x_acceleration
        tile.acceleration[1] = y_acceleration
    
    def get_enclosing_rect(self):
        return (
            (self.reference_position[0] + 1,self.reference_position[1] + 1),
            (self.width, self.height)
        )
    
    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (255,0,0),
            self.get_enclosing_rect(),
            1
        )
        #for row in self.tiles:
        #    for tile in row:
        #        start_position = (
        #            self.reference_position[0] + tile.position[0],
        #            self.reference_position[1] + tile.position[1]
        #        )
        #        end_position = (
        #            start_position[0] + (100 * tile.acceleration[0]),
        #            start_position[1] + (100 * tile.acceleration[1])
        #        )
        #        
        #        pygame.draw.line(
        #            surface,
        #            (255,0,0),
        #            start_position,
        #            end_position,
        #            1
        #        )
                    

class ForceTile():
    def __init__(
        self,
        position,
        height,
        width
    ):
        self.position = position
        self.height = height
        self.width = width
        self.acceleration = [0,0]
        self.gravity = 0

class Particle():
    def __init__(self):
        self.position = [0.0,0.0]
        self.velocity = [0.0,0.0]
        self.duration = 0
        self.total_duration = 0
        self.color = (255,255,255)
        self.points = []
    
    def init(self, duration, position, velocity, color):
        self.time_passed = 0
        self.duration = duration
        self.total_duration = duration
        self.position[0] = position[0]
        self.position[1] = position[1]
        self.velocity[0] = velocity[0] + .05
        self.velocity[1] = velocity[1]
        self.color = color
        self.set_points()
    
    def set_points(self):
        self.points = []
        
        for i in range(POINT_COUNT):
            angle = -random() * math.pi
            x_position = int(PARTICLE_RADIUS * random() * math.cos(angle)) + PARTICLE_RADIUS + POINT_RADIUS
            y_position = int(PARTICLE_RADIUS * random() * math.sin(angle)) + PARTICLE_RADIUS + POINT_RADIUS
            self.points.append((x_position, y_position))
    
    def reset(self, duration, position):
        self.duration = duration
        self.position[0] = position[0]
        self.position[1] = position[1]
    
    def accelerate(self, acceleration):
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]
    
    def update(self, time_passed):
        self.position[0] += self.velocity[0] * time_passed
        self.position[1] += self.velocity[1] * time_passed
        
        self.duration -= time_passed
    
    def draw_relative(self, surface, reference_position):
        if self.position[1] < 300:
            surface_position = (
                self.position[0] - reference_position[0],
                self.position[1] - reference_position[1]
            )
            
            render_surface = pygame.Surface((60, 60)).convert()
            render_surface.set_colorkey((2,232,3))
            render_surface.fill((2,232,3))
            
            alpha = int(255 * float(self.duration) / self.total_duration)
            render_surface.set_alpha(alpha)
            
            for point in self.points:
                
                pygame.draw.circle(
                    render_surface,
                    self.color,
                    (int(point[0]), 
                    int(point[1])),
                    4
                )
            
            surface.blit(
                render_surface,
                (int(surface_position[0]), int(surface_position[1]))
            )
    
    def draw(self, surface):
        #for point in self.points:
        #surface.set_at(
        #    (int(self.position[0]), 
        #    int(self.position[1])), 
        #    self.color
        #)
        render_surface = pygame.Surface((40, 40)).convert()
        render_surface.set_colorkey((2,232,3))
        alpha = int(255 * float(self.duration) / self.total_duration)
        
        render_surface.set_alpha(alpha)
        
        for point in self.points:
            if self.position[1] < 300:
                render_surface.fill((2,232,3))
                
                pygame.draw.circle(
                    render_surface,
                    self.color,
                    (int(point[0]), 
                    int(point[1])),
                    1
                )
                
                surface.blit(
                    render_surface,
                    (int(self.position[0] + point[0]),
                    int(self.position[1] + point[1]))
                )
    
    def get_enclosing_rect(self):
        min_position = map(min, zip(*self.points))
        max_position = map(max, zip(*self.points))
        height = 2 * (PARTICLE_RADIUS + POINT_RADIUS)
        width = 2 * (PARTICLE_RADIUS + POINT_RADIUS)
        
        position = (
            self.position[0] - (PARTICLE_RADIUS + POINT_RADIUS), 
            self.position[1] - (PARTICLE_RADIUS + POINT_RADIUS)
        )
        
        return (position, (height, width))

class ParticleSystem():
    def __init__(self, particle_count, particle_class, drag_coefficient):
        
        self.emit_position = [0,0]
        self.emit_rate = 0
        self.particle_duration = 0
        self.particle_max_velocity = 0
        self.particle_angle_range = [0, 2 * math.pi]
        self.particle_color = (255,255,255)
        
        self.duration = 0
        self.drag_coefficient = drag_coefficient
        self.force_fields = []
        
        self.particles = [particle_class() for i in range(particle_count)]
        self.live_particles = []
        self.dead_particles = []
        self.dead_particles.extend(self.particles)
    
    def init(
        self, 
        emit_position,
        emit_rate,
        max_velocity, 
        angle_range,
        duration,
        color
    ):
        self.emit_position[0] = emit_position[0]
        self.emit_position[1] = emit_position[1]
        self.emit_rate = emit_rate
        self.particle_duration = duration
        self.particle_max_velocity = max_velocity
        self.particle_angle_range[0] = angle_range[0]
        self.particle_angle_range[1] = angle_range[1]
        self.particle_color = color
        self.duration = duration
        self.cycle = False
    
    def active(self):
        return self.duration > 0
    
    def add_force_field(self, force_field):
        self.force_fields.append(force_field)
    
    def get_particle_init_velocity(self):
        velocity = self.particle_max_velocity * random()
        angle_delta = random() * (self.particle_angle_range[1] - self.particle_angle_range[0])
        angle = self.particle_angle_range[0] + angle_delta
        
        return (
            math.cos(angle) * velocity,
            math.sin(angle) * velocity
        )
    
    def apply_force_fields(self, particle):
        for field in self.force_fields:
            tile = field.get_tile(particle.position)
            
            if tile != None:
                particle.accelerate(tile.acceleration)
    
    def update(self, time_passed, step_size):
        
        while time_passed > 0:
            time_passed = time_passed - step_size
            
            for particle in self.live_particles:
                self.apply_force_fields(particle)
                particle.accelerate(
                    (-1 * self.drag_coefficient * particle.velocity[0],
                    -1 * self.drag_coefficient * particle.velocity[1])
                )
                particle.update(step_size)
            
            if self.emit_rate > 0:
                new_particle_count = min(len(self.dead_particles), self.emit_rate)
                
                if new_particle_count > 0:
                    live_particles = [
                        particle
                        for particle in self.dead_particles[:new_particle_count]
                    ]
                    for particle in live_particles:
                        
                        particle.init(
                            self.particle_duration, 
                            self.emit_position, 
                            self.get_particle_init_velocity(), 
                            self.particle_color)
                        
                        self.dead_particles.remove(particle)
                        self.live_particles.append(particle)            
            
            dead_particles = [
                particle 
                for particle in self.live_particles 
                if particle.duration <= 0
            ]
            
            for particle in dead_particles:
                self.live_particles.remove(particle)
                
                if self.cycle:
                    self.dead_particles.append(particle)
    
    def draw(self, surface):
        
        rect = self.get_enclosing_rects()
        particle_surface = pygame.Surface(rect[1])
        
        for particle in self.live_particles:
            particle.draw_relative(particle_surface, rect[0])
        
        scaled_width = int(.5 * rect[1][0])
        scaled_height = int(.5 * rect[1][1])
        
        scaled_surface = pygame.transform.scale(
            particle_surface, 
            (scaled_width, scaled_height)
        )
        scaled_position = (rect[0][0], rect[0][1] + scaled_height)
        surface.blit(scaled_surface, scaled_position)
    
    def get_enclosing_rects(self):
        #return [particle.get_enclosing_rect() for particle in self.live_particles]
        
        rects = [particle.get_enclosing_rect() for particle in self.live_particles]
        if len(rects) > 0:
            min_position = map(min, zip(*[rect[0] for rect in rects]))
            max_position = map(max, zip(*[
                (rect[0][0] + rect[1][0], rect[0][1] + rect[1][1]) 
                for rect in rects
            ]))
            height = max_position[1] - min_position[1]
            width = max_position[0] - min_position[0]
            
            return (
                (int(min_position[0]), int(min_position[1])), 
                (int(width), int(height))
            )
        else:
            return ((0,0), (0, 0))

class RunSmoke(ParticleSystem):
    def __init__(self, floor_height, direction):
        ParticleSystem.__init__(self, 20, Particle, .04)
        
        self.floor_height = floor_height
        
        self.particle_buffer = pygame.Surface(
            (2 * (PARTICLE_RADIUS + POINT_RADIUS), 2 * (PARTICLE_RADIUS + POINT_RADIUS))
        ).convert()
        self.particle_buffer.set_colorkey(COLOR_KEY)
        
        self.direction = direction
        field = None
        
        if direction < 0:
            field = ForceField(
                [self.emit_position[0] + 100, self.emit_position[1] - 100],
                75,
                100
            )
        else:
            field = ForceField(
                [self.emit_position[0] - 500 + 10, self.emit_position[1] - 100],
                75,
                100
            )
        field.set_tiles(1,1)
        self.field = field
        self.add_force_field(field)
        
        for row in self.field.tiles:
            for tile in row:
                tile.acceleration[0] = direction * .015
                tile.acceleration[1] = random() / 80
    
    def start(self, emit_position):
        self.emit_position[0] = emit_position[0]
        self.emit_position[1] = emit_position[1]
        
        if self.direction > 0:
            self.field.reference_position[0] = self.emit_position[0] - 50
            self.field.reference_position[1] = self.emit_position[1] - self.field.height + 10
        else:
            self.field.reference_position[0] = self.emit_position[0] - self.field.width + 50
            self.field.reference_position[1] = self.emit_position[1] - self.field.height + 10
        
        angle_range = None
        
        if self.direction > 0:
            angle_range = [-math.pi/3, -math.pi]
        else:
            angle_range = [0, -2*math.pi/3]
        
        self.init(
            emit_position, 
            10,
            .3,
            angle_range, 
            1000,
            (255, 255, 255)
        )
        self.duration = 1000
        
        self.live_particles = []
        self.dead_particles = []
        self.dead_particles.extend(self.particles)
        
        for particle in self.particles:
                        
            particle.init(
                self.particle_duration, 
                self.emit_position, 
                self.get_particle_init_velocity(), 
                self.particle_color)
    
    def update(self, time_passed):
        if self.duration > 0:
            self.duration -= time_passed
            
            ParticleSystem.update(self, time_passed, 10)
            for particle in self.particles:
                if particle.position[1] > self.floor_height:
                    particle.position[1] = self.floor_height + 1
    
    def draw2(self, surface):
        temp_surface, position = self.draw()
        surface.blit(temp_surface, position)
    
    def draw(self):
        rect = self.get_enclosing_rects()
        system_surface = pygame.Surface(rect[1])
        system_surface.set_colorkey((0,0,0))
        system_surface.fill((0,0,0))
        
        particle_surface = self.particle_buffer
        
        for particle in self.live_particles:
            
            alpha = min(100, int(255 * float(particle.duration) / particle.total_duration))
            particle_surface.fill(COLOR_KEY)
            particle_surface.set_alpha(alpha)
            
            surface_position = (
                int(particle.position[0] - rect[0][0] - PARTICLE_RADIUS - POINT_RADIUS),
                int(particle.position[1] - rect[0][1] - PARTICLE_RADIUS - POINT_RADIUS)
            )
            
            for point in particle.points:
                if particle.position[1] + point[1] < self.floor_height:
                    pygame.draw.circle(
                        particle_surface,
                        particle.color,
                        (int(point[0]), 
                        int(point[1])),
                        POINT_RADIUS
                    )
            
            #surface.blit(
            #    particle_surface,
            #    surface_position
            #)
            
            system_surface.blit(
                particle_surface,
                surface_position
            )
        
        #scaled_width = int(.5 * rect[1][0])
        #scaled_height = int(.5 * rect[1][1])
        
        #scaled_surface = pygame.transform.scale(
        #    system_surface, 
        #    (scaled_width, scaled_height)
        #)
        #scaled_position = (rect[0][0], rect[0][1] + scaled_height)
        return system_surface, rect[0]
        

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN, 32)
    clock = pygame.time.Clock()

    system = ParticleSystem(100, Particle, .04)
    field = ForceField((350,200), 100, 150)
    field.set_tiles(1,1)
    system.init(
        (400,300),
        300,
        0.4, 
        [-math.pi/3, -math.pi], 
        1000,
        (255, 255, 255)
    )
    system.add_force_field(field)

    mouse_position_label = Label((0,0),"", (255,255,255), 20)
    tile_position_label = Label((0,20),"", (255,255,255), 20)
    acceleration_label = Label((0,40),"",(255,255,255), 20)
    gravity_label = Label((0,60),"",(255,255,255), 20)
    frame_rate_label = Label((0,80),"",(255,255,255), 20)

    run_smoke = RunSmoke(500, 1)
    run_smoke2 = RunSmoke(500, -1)
    run_smoke3 = RunSmoke(500, 1)
    run_smoke4 = RunSmoke(500, -1)

    new_rects = []
    dirty_rects = []

    start_runsmoke = False

    while 1:
        screen.fill((0,0,0))
        wotsuievents.get_events()
        
        #angle_label.set_text(str(input_angle))
        #angle_label.draw(screen)
        
        if pygame.QUIT in wotsuievents.event_types:
            sys.exit()
        elif len(wotsuievents.keys_pressed) > 0:
            sys.exit()
        
        if wotsuievents.mouse_buttons_pressed[0] == 1:
            start_runsmoke = True
        elif wotsuievents.mouse_buttons_pressed[0] == 0:
            if start_runsmoke:
                run_smoke.start(wotsuievents.mouse_pos)
                run_smoke2.start([wotsuievents.mouse_pos[0] - 50, wotsuievents.mouse_pos[1]])
                run_smoke3.start([wotsuievents.mouse_pos[0], wotsuievents.mouse_pos[1] - 100])
                run_smoke4.start([wotsuievents.mouse_pos[0] - 50, wotsuievents.mouse_pos[1] - 100])
                start_runsmoke = False
        elif wotsuievents.mouse_buttons_pressed[2] == 1:
            field.increase_gravity(wotsuievents.mouse_pos, -.01)
        elif pygame.K_UP in wotsuievents.keys_pressed:
            system.particle_angle_range[1] -= .1 * math.pi
        elif pygame.K_DOWN in wotsuievents.keys_pressed:
            system.particle_angle_range[1] += .1 * math.pi
        elif pygame.K_SPACE in wotsuievents.keys_pressed:
            field.gravity_tiles = []
            for row in field.tiles:
                for tile in row:
                    tile.acceleration[0] = 0
                    tile.acceleration[1] = 0
                    tile.gravity = 0
                    
        elif pygame.K_e in wotsuievents.keys_pressed:
            field.gravity_tiles = []
            for row in field.tiles:
                for tile in row:
                    tile.acceleration[0] = .015
                    tile.acceleration[1] = random() / 80
                    tile.gravity = 0
        
        frame_rate_label.set_text("frame rate: " + str(clock.get_fps()))
        new_rects.append((frame_rate_label.position, (frame_rate_label.width, frame_rate_label.height)))
        
        if field.contains(wotsuievents.mouse_pos):
            mouse_position_label.set_text("mouse position: " + str(wotsuievents.mouse_pos))
            tile = field.get_tile(wotsuievents.mouse_pos)
            tile_position_label.set_text("tile position: " + str(field.get_absolute_position(tile.position)))
            acceleration_label.set_text("tile acceleration: " + str(tile.acceleration))
            gravity_label.set_text("tile gravity: " + str(tile.gravity))
        else:
            mouse_position_label.set_text("mouse position: " + str(wotsuievents.mouse_pos))
            tile = field.get_tile(wotsuievents.mouse_pos)
            tile_position_label.set_text("tile position:")
            acceleration_label.set_text("tile acceleration:")
            gravity_label.set_text("tile gravity:")
        
        time_passed = min(100, clock.get_time())
        #system.update(time_passed, 10)
        #field.draw(screen)
        #system.draw(screen)
        #new_rects.append(system.get_enclosing_rects())
        
        if run_smoke.active:
            run_smoke.update(time_passed)
            run_smoke.draw2(screen)
            #run_smoke.force_fields[0].draw(screen)
            #new_rects.append(run_smoke.field.get_enclosing_rect())
            new_rects.append(run_smoke.get_enclosing_rects())
        
        if run_smoke2.active:
            run_smoke2.update(time_passed)
            run_smoke2.draw2(screen)
            #run_smoke.force_fields[0].draw(screen)
            #new_rects.append(run_smoke.field.get_enclosing_rect())
            new_rects.append(run_smoke2.get_enclosing_rects())
        
        if run_smoke3.active:
            run_smoke3.update(time_passed)
            run_smoke3.draw2(screen)
            #run_smoke.force_fields[0].draw(screen)
            #new_rects.append(run_smoke.field.get_enclosing_rect())
            new_rects.append(run_smoke3.get_enclosing_rects())
        
        if run_smoke4.active:
            run_smoke4.update(time_passed)
            run_smoke4.draw2(screen)
            #run_smoke.force_fields[0].draw(screen)
            #new_rects.append(run_smoke.field.get_enclosing_rect())
            new_rects.append(run_smoke4.get_enclosing_rects())
        
        #mouse_position_label.draw(screen)
        #tile_position_label.draw(screen)
        #acceleration_label.draw(screen)
        #gravity_label.draw(screen)
        frame_rate_label.draw(screen)
        
        
        pygame.display.update(dirty_rects)
        pygame.display.update(new_rects)
        
        dirty_rects = new_rects
        new_rects = []
        
        for old_rect in dirty_rects:
            screen.fill((0,0,0), old_rect)
        
        clock.tick(100)
