import os
import multiprocessing
import pygame

import wotsuievents
import gamestate
import player
import humanplayer
import aiplayer
import button
import stage
import stick
import mathfuncs
import math
import settingsdata
import versusrendering
from wotsfx import ClashEffect, HitEffect, TrailEffect
from versusmodeui import PlayerHealth, AttackList, PAUSE_MENU_WIDTH, PAUSE_MENU_HEIGHT
from simulation import MatchSimulation
from attackbuilderui import AttackLabel
from enumerations import PlayerPositions, MatchStates, PlayerTypes, ClashResults, \
PlayerStates, CommandCollections, InputActionTypes, PointNames, EffectTypes, EventTypes, \
EventStates
from versussound import AttackResultSoundMixer, PlayerSoundMixer
from controlsdata import get_controls
from playercontroller import InputCommandTypes
from particles import RunSmoke, JumpSmoke, FallSmoke
from physics import Orientations
import record

gamestate.stage = stage.load_default_stage()
step_number = 0
SIMULATION_FPS = 100

class EventRegistry():
    def __init__(self):
        self.events = {}
    
    def add_event_handler(self, event, func):
        if event in self.events:
            self.events[event].append(func)
        else:
            self.events[event] = [func]
    
    def remove_event_handler(self, event, func):
        if event in self.events:
            if func in self.events[event]:
                self.events[event].remove(func)
    
    def clear_events(self):
        self.events = {}
    
    def fire_event_handlers(self, event, args):
        if event in self.events:
            for func in self.events[event]:
                func(*args)

class VersusModeState():
    def __init__(self):
        
        self.initialized = False
        self.player_positions = []
        self.player_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_key_handlers = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_event_handlers = {
            PlayerPositions.PLAYER1 : EventRegistry(),
            PlayerPositions.PLAYER2 : EventRegistry()
        }
        self.player_type_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_sound_mixer_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_health_bars = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.fight_label = None
        self.ready_label = None
        self.player1_wins_label = None
        self.player2_wins_label = None
        self.match_state = None
        self.match_time = None
        self.exit_button = button.ExitButton()
        self.exit_indicator = False
        self.exiting = False
        self.versus_mode_start_time = None
        self.fight_start_time = None
        self.fight_end_time = None
        self.fight_end_timer = None
        self.versus_mode_start_timer = None
        self.fight_start_timer = None
        self.fps_label = None
        self.command_label = None
        self.point_effects = {}
        self.trail_effects = {
            PlayerPositions.PLAYER1 : {},
            PlayerPositions.PLAYER2 : {}
        }
        self.particle_effects = {
            PlayerPositions.PLAYER1 : {},
            PlayerPositions.PLAYER2 : {}
        }
        self.camera = None
        self.player_renderer_state = None
        self.surface_renderer = None
        self.match_simulation = None
        self.simulation_process = None
        self.simulation_connection = None
        self.pause = False
        self.pause_held = False
        self.attack_lists = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.recording_indicator = False
        self.recording = None

        self.attack_result_sound_mixer = None
    
    def init(self, player_data):
        
        self.init_match_state_variables()
        self.init_player_data(player_data)
        self.init_sound_objects()
        self.init_rendering_objects()
        self.init_simulation_objects()
        self.set_GUI_module_variables()
        self.initialized = True
        self.exit_indicator = False
        self.exiting = False
        
        if self.simulation_process == None and self.exiting == False:
            self.start_match_simulation()
        
        self.init_screen()
    
    def init_recording(self, moveset1_name, moveset2_name):
        self.recording = record.Recording(
            self.match_simulation.timestep, 
            moveset1_name, 
            moveset2_name
        )
    
    def init_player_data(self, player_data):
        for player_datum in player_data:
            self.add_player(player_datum)
    
    def add_player(self, player_data):
        player = create_player(player_data)
        player_position = player_data.player_position
        self.player_positions.append(player_position)
        self.player_dictionary[player_position] = player
        self.player_key_handlers[player_position] = KeyToCommandTypeConverter(
            dict([(entry[1], entry[0]) 
            for entry in get_controls()[player_position].iteritems()])
        )
        self.player_event_handlers[player_position] = EventRegistry()
        self.player_type_dictionary[player_position] = player_data.player_type
        self.player_health_bars[player_position] = PlayerHealth(
            player_data.moveset.name, 
            player_position
        )
        self.attack_lists[player_position] = AttackList(
            player_data.moveset,
            (
                int((gamestate._WIDTH / 2) - PAUSE_MENU_WIDTH),
                int((gamestate._HEIGHT / 2) - (PAUSE_MENU_HEIGHT / 2))
            )
        )
    
    def init_screen(self):
        gamestate.screen.blit(gamestate.stage.background_image, (0,0))
        gamestate.new_dirty_rects.append(
            pygame.Rect((0,0), (gamestate._WIDTH, gamestate._HEIGHT))
        )
        gamestate.update_screen()

    def set_GUI_module_variables(self):
        wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
        gamestate.frame_rate = gamestate.VERSUSMODE_FRAMERATE
        gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS

    def exit(self):
        
        self.end_simulation()
        self.cleanup_rendering_objects()
        self.cleanup_match_state_variables()
        self.reset_GUI_variables()
        self.flush_recording()
        self.initialized = False
    
    def flush_recording(self):
        if self.recording_indicator:
            record.save(self.recording)
            self.recording = None
    
    def reset_GUI_variables(self):
        wotsuievents.key_repeat = wotsuievents.KeyRepeat.NONE
        gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
        gamestate.frame_rate = gamestate.NORMAL_FRAMERATE

    def handle_events(self):
        
        if gamestate.devmode:
            self.fps_label.set_text(str(gamestate.clock.get_fps()))
            self.fps_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.fps_label.position,
                    (self.fps_label.width, self.fps_label.height)
                )
            )
            
            self.command_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.command_label.position,
                    (self.command_label.width, self.command_label.height))
            )
        
        if self.exiting == False:
            
            simulation_messages = self.get_simulation_messages()
            self.handle_simulation_messages(simulation_messages)
            
            self.render_simulation()
            
            self.handle_pause_events()
            
            if not self.pause:
                self.clean_expired_effects()
                
                self.handle_match_state()
        
        if self.simulation_connection != None:
            self.update_simulation()
        
        self.handle_exit_events()
    
    def get_simulation_messages(self):
        simulation_messages = []
        
        while self.simulation_connection.poll():
            simulation_messages.append(self.simulation_connection.recv())
        
        return simulation_messages
    
    def handle_simulation_messages(self, simulation_messages):
        
        for message in simulation_messages:
            simulation_rendering_info = message
            
            if self.recording_indicator:
                self.recording.simulation_snapshots.append(simulation_rendering_info)
            
            if simulation_rendering_info.match_time > self.match_time:
                self.update_simulation_rendering(simulation_rendering_info)
    
    def handle_pause_events(self):
        if ((
        pygame.K_KP_ENTER in wotsuievents.keys_pressed or 
        pygame.K_RETURN in wotsuievents.keys_pressed) and
        not self.pause_held):
            self.pause_held = True
            self.simulation_connection.send('PAUSE')
            self.pause = not self.pause
        elif ((
        pygame.K_KP_ENTER in wotsuievents.keys_released or 
        pygame.K_RETURN in wotsuievents.keys_released) and 
        self.pause_held):
            self.pause_held = False
        
        if self.pause:
            for attack_list in self.attack_lists.values():
                attack_list.handle_events()
    
    def build_player_command_types(self):
        
        return {
            PlayerPositions.PLAYER1 : self.player_key_handlers[
                PlayerPositions.PLAYER1
            ].get_command_data(wotsuievents.keys_pressed),
            PlayerPositions.PLAYER2 : self.player_key_handlers[
                PlayerPositions.PLAYER2
            ].get_command_data(wotsuievents.keys_pressed)
        }
    
    def init_simulation_objects(self):
        
        self.simulation_connection, input_connection = multiprocessing.Pipe()
        
        self.match_simulation = MatchSimulation(
            input_connection,
            player_dictionary=self.player_dictionary,
            player_type_dictionary=self.player_type_dictionary
        )
    
    def init_match_state_variables(self):
        
        self.match_state = MatchStates.READY
        self.match_time = 0
        self.fight_end_timer = 0
        self.versus_mode_start_timer = 0
        self.fight_start_timer = 0
    
    def start_run_start_particle_effect(self, player_position, player_rendering_info):
        model = player_rendering_info.player_model
        orientation = model.orientation
        emit_position = (model.center()[0], model.bottom() + 10)
        
        if orientation == Orientations.FACING_RIGHT:
            self.particle_effects[player_position][EffectTypes.RIGHT_RUN_SMOKE].start(
                emit_position
            )
        else:
            self.particle_effects[player_position][EffectTypes.LEFT_RUN_SMOKE].start(
                emit_position
            )
    
    def start_jump_particle_effect(self, player_position, player_rendering_info):
        model = player_rendering_info.player_model
        
        
        if model.bottom() > gamestate.stage.floor_height - 50:
            emit_position = (model.center()[0], model.bottom() + 10)    
            self.particle_effects[player_position][EffectTypes.JUMP_SMOKE].start(
                emit_position
            )
    
    def start_fall_particle_effect(self, player_position, player_rendering_info):
        model = player_rendering_info.player_model
        emit_position = (model.center()[0], model.bottom() + 10)
        
        effect = self.particle_effects[player_position][EffectTypes.FALL_SMOKE]
        
        if not effect.active():
            effect.start(
                emit_position
            )
    
    def start_run_stop_particle_effect(self, player_position, player_rendering_info):
        model = player_rendering_info.player_model
        orientation = model.orientation
        
        if orientation == Orientations.FACING_RIGHT:
            emit_position = (model.position[0] + model.width, model.bottom() + 10)
            self.particle_effects[player_position][EffectTypes.LEFT_RUN_SMOKE].start(
                emit_position
            )
        else:
            emit_position = (model.position[0] - model.width, model.bottom() + 10)
            self.particle_effects[player_position][EffectTypes.RIGHT_RUN_SMOKE].start(
                emit_position
            )
    
    def end_trail_effects(self, player_position, player_rendering_info):
        self.trail_effects[player_position] = {}
    
    def init_rendering_objects(self):
        
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, PlayerStates.RUNNING),
            self.start_run_start_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.STOP, PlayerStates.RUNNING),
            self.start_run_stop_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, PlayerStates.JUMPING),
            self.start_jump_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, EventStates.STUN_GROUND),
            self.start_fall_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.STOP, PlayerStates.ATTACKING),
            self.end_trail_effects
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, PlayerStates.RUNNING),
            self.start_run_start_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.STOP, PlayerStates.RUNNING),
            self.start_run_stop_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, PlayerStates.JUMPING),
            self.start_jump_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, EventStates.STUN_GROUND),
            self.start_fall_particle_effect
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.STOP, PlayerStates.ATTACKING),
            self.end_trail_effects
        )
        
        self.particle_effects = {
            PlayerPositions.PLAYER1 : {
                EffectTypes.LEFT_RUN_SMOKE : RunSmoke(gamestate.stage.floor_height + 50, 1),
                EffectTypes.RIGHT_RUN_SMOKE : RunSmoke(gamestate.stage.floor_height + 50, -1),
                EffectTypes.JUMP_SMOKE : JumpSmoke(gamestate.stage.floor_height + 50),
                EffectTypes.FALL_SMOKE : FallSmoke(gamestate.stage.floor_height + 50)
            },
            PlayerPositions.PLAYER2 : {
                EffectTypes.LEFT_RUN_SMOKE : RunSmoke(gamestate.stage.floor_height + 50, 1),
                EffectTypes.RIGHT_RUN_SMOKE : RunSmoke(gamestate.stage.floor_height + 50, -1),
                EffectTypes.JUMP_SMOKE : JumpSmoke(gamestate.stage.floor_height + 50),
                EffectTypes.FALL_SMOKE : FallSmoke(gamestate.stage.floor_height + 50)
            }
        }
        
        self.point_effects = {}
        self.trail_effects = {
            PlayerPositions.PLAYER1 : {},
            PlayerPositions.PLAYER2 : {}
        }
        
        self.camera = versusrendering.ViewportCamera(
            gamestate.stage.width,
            gamestate.stage.height,
            gamestate._WIDTH,
            gamestate._HEIGHT
        )
        self.player_renderer_state = versusrendering.PlayerRendererState(
            self.camera,
            [PlayerPositions.PLAYER1, PlayerPositions.PLAYER2]
        )
        
        self.surface_renderer = versusrendering.SurfaceRenderer(self.camera)
        
        self.fps_label = button.Label(
            (5,5), 
            str(gamestate.clock.get_fps()),(0,0,255),
            10
        )
        self.command_label = AttackLabel("", [])
        self.command_label.key_combination_label.set_position((20,200))
        
        self.ready_label = button.Label((0,0),'READY...',(0,0,255),80)
        ready_label_position = (
            (gamestate._WIDTH / 2) - (self.ready_label.width / 2),
            (gamestate._HEIGHT / 2) - (self.ready_label.height / 2)
        )
        self.ready_label.set_position(ready_label_position)
        
        self.fight_label = button.Label((0,0),'FIGHT!',(0,0,255),80)
        fight_label_position = (
            (gamestate._WIDTH / 2) - (self.fight_label.width / 2),
            (gamestate._HEIGHT / 2) - (self.fight_label.height / 2)
        )
        self.fight_label.set_position(fight_label_position)
        
        self.player1_wins_label = button.Label((0,0),'PLAYER 1 WINS!',(0,0,255),80)
        player1_wins_label_position = (
            (gamestate._WIDTH / 2) - (self.player1_wins_label.width / 2), 
            (gamestate._HEIGHT / 2) - (self.player1_wins_label.height / 2)
        )
        self.player1_wins_label.set_position(player1_wins_label_position)
        
        self.player2_wins_label = button.Label((0,0),'PLAYER 2 WINS!',(0,0,255),80)
        player2_wins_label_position = (
            (gamestate._WIDTH / 2) - (self.player2_wins_label.width / 2),
            (gamestate._HEIGHT / 2) - (self.player2_wins_label.height / 2)
        )
        self.player2_wins_label.set_position(player2_wins_label_position)
    
    def init_sound_objects(self):
        self.attack_result_sound_mixer = AttackResultSoundMixer()
        
        self.player_sound_mixer_dictionary[PlayerPositions.PLAYER1] = PlayerSoundMixer(0)
        
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, EventStates.FOOT_SOUND),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER1].play_sound
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, EventStates.ATTACK_SOUND),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER1].play_sound
        )
        self.player_event_handlers[PlayerPositions.PLAYER1].add_event_handler(
            (EventTypes.START, PlayerStates.JUMPING),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER1].play_sound
        )
        
        self.player_sound_mixer_dictionary[PlayerPositions.PLAYER2] = PlayerSoundMixer(1)
        
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, EventStates.FOOT_SOUND),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER2].play_sound
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, EventStates.ATTACK_SOUND),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER2].play_sound
        )
        self.player_event_handlers[PlayerPositions.PLAYER2].add_event_handler(
            (EventTypes.START, PlayerStates.JUMPING),
            self.player_sound_mixer_dictionary[PlayerPositions.PLAYER2].play_sound
        )
    
    def cleanup_match_state_variables(self):
        
        self.match_state = None
        self.match_time = 0
        self.versus_mode_start_timer = None
        self.fight_start_timer = None
        self.fight_end_timer = None

    def cleanup_rendering_objects(self):
        
        self.point_effects = {}
        self.player_health_bars = {}
        self.trail_effects = None
        self.player_renderer_state = None
        self.surface_renderer = None
        self.fps_label = None
        self.command_label = None
        self.ready_label = None
        self.fight_label = None
        self.player1_wins_label = None
        self.player2_wins_label = None

    def end_simulation(self):
        
        self.simulation_connection.send('STOP')
        self.simulation_process.join()
        self.simulation_connection.close()
        self.simulation_connection = None
        gamestate.processes.remove(self.simulation_process)
        self.simulation_process = None
        self.match_simulation = None


    def handle_exit_events(self):
        
        self.exit_button.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                self.exit_button.position, 
                (self.exit_button.width, self.exit_button.height)
            )
        )
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if self.exit_button.contains(wotsuievents.mouse_pos):
                self.exit_indicator = True
                self.exit_button.color = button.Button._SlctdColor
                self.exit_button.symbol.color = button.Button._SlctdColor
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if self.exit_indicator == True:
                self.exit_indicator = False
                self.exit_button.color = button.Button._InactiveColor
                self.exit_button.symbol.color = button.Button._InactiveColor
                
                if self.exit_button.contains(wotsuievents.mouse_pos):
                    self.exiting = True
                    gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                    self.exit()

    def clean_expired_effects(self):
        
        dead_effects = []
        
        for point_id, effect in self.point_effects.iteritems():
            if effect.effect_over():
                dead_effects.append(point_id)
        
        for point_id in dead_effects:
            del self.point_effects[point_id]

    def render_simulation(self):
        
        for sprite in gamestate.stage.sprites:
            self.surface_renderer.draw_surface_to_screen(
                1,
                sprite.position, 
                sprite.image
            )
        
        versusrendering.draw_player_renderer_state(
            self.player_renderer_state, 
            gamestate.screen
        )
        
        for effect in self.point_effects.values():
            
            effect_position, effect_surface = effect.draw_effect()
            self.surface_renderer.draw_surface_to_screen(
                3,
                effect_position, 
                effect_surface
            )
        
        for player_trail_effects in self.trail_effects.values():
            for point_effects in player_trail_effects.values():
                for trail_effect in point_effects.values():
                    if trail_effect.is_renderable():
                        for polygon_positions in trail_effect.get_polygons():
                            self.surface_renderer.draw_polygon(
                                0,
                                polygon_positions,
                                (0,0,0),
                                8
                            )
                        
                        for polygon_positions in trail_effect.get_polygons():
                            self.surface_renderer.draw_polygon(
                                1,
                                polygon_positions,
                                (255,255,255),
                                5
                            )
                        
                        for polygon_positions in trail_effect.get_polygons():
                            self.surface_renderer.draw_polygon(
                                2,
                                polygon_positions,
                                trail_effect.color
                            )
        
        for player_particle_effects in self.particle_effects.values():
            for effect in player_particle_effects.values():
                if effect.active():
                    
                    surface, position = effect.draw()
                    self.surface_renderer.draw_surface_to_screen(
                        3,
                        position, 
                        surface
                    )
        
        for health_bar in self.player_health_bars.values():
            self.surface_renderer.draw_surface_to_absolute_position(
                1,
                health_bar.position, 
                health_bar.draw()
            )
        
        if self.camera.full_zoom_only and gamestate.devmode:
            for camera_rect in gamestate.stage.camera_rects:
                rect_surface = pygame.Surface((camera_rect.width, camera_rect.height))
                rect_surface.fill((0,0,0))
                rect_surface.set_colorkey((0,0,0))
                pygame.draw.rect(
                    rect_surface,
                    (0,255,0),
                    ((0,0), camera_rect.size),
                    10
                )
                self.surface_renderer.draw_surface_to_screen(
                    999,
                    camera_rect.topleft, 
                    rect_surface
                )
            
            rect_surface = pygame.Surface((
                self.camera.viewport_width / self.camera.viewport_scale, 
                self.camera.viewport_height / self.camera.viewport_scale
            ))
            rect_surface.fill((0,0,0))
            rect_surface.set_colorkey((0,0,0))
            pygame.draw.rect(
                rect_surface,
                (255,0,0),
                (
                    (0,0), 
                    (
                        self.camera.viewport_width / self.camera.viewport_scale, 
                        self.camera.viewport_height / self.camera.viewport_scale
                    )
                ),
                10
            )
            self.surface_renderer.draw_surface_to_screen(
                1000,
                self.camera.viewport_position, 
                rect_surface
            )
        
        if self.pause:
            for attack_list in self.attack_lists.values():
                attack_list.draw(gamestate.screen)

    def update_simulation(self):
        self.simulation_connection.send(
            (self.build_player_command_types(), gamestate.time_passed)
        )

    def update_simulation_rendering(self, simulation_rendering_info):
        
        self.command_label.set_key_combination(
            self.build_player_command_types()[PlayerPositions.PLAYER1].attack_command_types
        )
        self.set_outline_color(simulation_rendering_info)
        
        for effect in self.point_effects.values():
            if not self.pause:
                effect.update(gamestate.time_passed)
        
        if simulation_rendering_info.attack_result_rendering_info != None:
            self.create_collision_effects(
                simulation_rendering_info.attack_result_rendering_info
            )
            self.attack_result_sound_mixer.handle_hit_sounds(
                simulation_rendering_info.attack_result_rendering_info
            )
            
            if simulation_rendering_info.attack_result_rendering_info.attack_type in InputActionTypes.STRONG_ATTACKS:
                self.camera.start_shaking(
                    simulation_rendering_info.attack_result_rendering_info.attack_damage
                )
        
        if not self.pause:
            self.update_trail_effects(
                simulation_rendering_info.player_rendering_info_dictionary
            )
            self.update_particle_effects()
        
        for player_position, player_rendering_info in simulation_rendering_info.player_rendering_info_dictionary.iteritems():
            event_handler = self.player_event_handlers[player_position]
            
            for event in player_rendering_info.events:
                event_handler.fire_event_handlers(
                    event, 
                    (player_position, player_rendering_info)
                )
            
            health_bar = self.player_health_bars[player_position]
            health_bar.update(
                gamestate.time_passed,
                player_rendering_info.health_percentage
            )
        
        self.player_renderer_state.update(
            simulation_rendering_info.player_rendering_info_dictionary, 
            1
        )
        self.match_state = simulation_rendering_info.match_state
        self.match_time = simulation_rendering_info.match_time
    
    def update_particle_effects(self):
        for player_particle_effects in self.particle_effects.values():
            for effect in player_particle_effects.values():
                if effect.active():
                    effect.update(gamestate.time_passed)
    
    def update_trail_effects(self, player_rendering_info): 
        
        for player_position in self.trail_effects.keys():
            player_info = player_rendering_info[player_position]
            attack_type = player_info.attack_type
            player_trail_effects = self.trail_effects[player_position]
            
            if attack_type != None:
                
                player_model = player_info.player_model
                
                if player_info.animation_name in player_trail_effects:
                    #update pointeffects
                    for point_name, effect in player_trail_effects[player_info.animation_name].iteritems():
                        effect.update(player_model.points[point_name].pos)
                
                else:
                    #create point effects
                    point_effects = player_trail_effects[player_info.animation_name] = {}
                    
                    if attack_type in InputActionTypes.PUNCHES:
                        point_effects[PointNames.RIGHT_HAND] = TrailEffect(
                            player_model.points[PointNames.RIGHT_HAND].pos,
                            10,
                            50,
                            player_info.player_health_color
                        )
                        point_effects[PointNames.LEFT_HAND] = TrailEffect(
                            player_model.points[PointNames.LEFT_HAND].pos,
                            10,
                            50,
                            player_info.player_health_color
                        )
                    else:
                        point_effects[PointNames.RIGHT_FOOT] = TrailEffect(
                            player_model.points[PointNames.RIGHT_FOOT].pos,
                            10,
                            50,
                            player_info.player_health_color
                        )
                        point_effects[PointNames.LEFT_FOOT] = TrailEffect(
                            player_model.points[PointNames.LEFT_FOOT].pos,
                            10,
                            50,
                            player_info.player_health_color
                        )
            else:
                if len(player_trail_effects.keys()) > 0:
                    self.trail_effects[player_position] = {}
    
    def start_match_simulation(self):    
        
        self.match_simulation.step(
            self.build_player_command_types(), self.match_simulation.timestep
        )
        
        #initialize renderer state
        self.player_renderer_state.update(
            self.match_simulation.get_rendering_info(
            ).player_rendering_info_dictionary, 
            1
        )
        
        #start simulation process
        self.simulation_process = multiprocessing.Process(
            target=self.match_simulation.run,
            name="Way of the stick simulation"
        )
        gamestate.processes.append(self.simulation_process)
        self.simulation_process.start()
        
        #reset game clock
        gamestate.clock.tick(gamestate.frame_rate)
        gamestate.update_time()
        gamestate.clock.tick(gamestate.frame_rate)
        gamestate.update_time()

    def set_outline_color(self, simulation_rendering_info):
        player_rendering_info_dictionary = simulation_rendering_info.player_rendering_info_dictionary
        
        for player_position, rendering_info in player_rendering_info_dictionary.iteritems():
            
            if rendering_info.player_state == PlayerStates.STUNNED:
                if (simulation_rendering_info.match_time % 30) >= 15:
                    rendering_info.player_outline_color = (255, 255, 0)
                else:
                    rendering_info.player_outline_color = (255, 0, 0)
            else:
                pass #leave the outline color as it is

    def handle_match_state(self):
        
        if self.match_state == MatchStates.READY:
            self.ready_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.ready_label.position,
                    (self.ready_label.width, self.ready_label.height))
            )
            
        elif self.match_state == MatchStates.FIGHT and self.match_time < 4000:
            self.fight_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.fight_label.position,
                    (self.fight_label.width, self.fight_label.height))
            )
        
        elif self.match_state == MatchStates.PLAYER1_WINS:
            
            if self.fight_end_timer < 8000:
                self.fight_end_timer += gamestate.time_passed
                self.player1_wins_label.draw(gamestate.screen)
                
                gamestate.new_dirty_rects.append(
                    pygame.Rect(
                        self.player1_wins_label.position, 
                        (
                            self.player1_wins_label.width,
                            self.player1_wins_label.height
                        )
                    )
                )
                
            else:
                gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                self.exit()
        elif self.match_state == MatchStates.PLAYER2_WINS:
            
            if self.fight_end_timer < 8000:
                self.fight_end_timer += gamestate.time_passed
                self.player2_wins_label.draw(gamestate.screen)
                gamestate.new_dirty_rects.append(
                    pygame.Rect(
                        self.player2_wins_label.position,
                        (
                            self.player2_wins_label.width,
                            self.player2_wins_label.height
                        )
                    )
                )
            else:
                gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                self.exit()

    def create_collision_effects(self, attack_result_rendering_info):
        
        attack_knockback_vector = attack_result_rendering_info.knockback_vector
        
        damage = attack_result_rendering_info.attack_damage
        effect_height = max(50, damage)
        effect_width = max(50, .2 * damage)
        fade_rate = .2
        
        angle_in_degrees = 0
        
        if attack_knockback_vector[0] == 0:
            if mathfuncs.sign(attack_knockback_vector[1]) == 1:
                angle_in_degrees = 0
            else:
                angle_in_degrees = 180
                
        elif attack_knockback_vector[1] == 0:
            if mathfuncs.sign(attack_knockback_vector[0]) == 1:
                angle_in_degrees = 90
            else:
                angle_in_degrees = 270
            
        else:
            angle_in_degrees = math.degrees(
                math.asin(attack_knockback_vector[1] / math.hypot(
                        attack_knockback_vector[0], attack_knockback_vector[1]
                    )
                )
            )
        
        attack_point = attack_result_rendering_info.attack_point
        if not attack_point.id in self.point_effects:
            if attack_result_rendering_info.clash_indicator:
                self.point_effects[attack_point.id] = ClashEffect(
                    attack_result_rendering_info.clash_position,
                    angle_in_degrees,
                    effect_width,
                    effect_height,
                    .7,
                    fade_rate,
                    1
                )
            else:
                self.point_effects[attack_point.id] = HitEffect(
                    attack_result_rendering_info.attack_point.pos,
                    angle_in_degrees,
                    effect_width,
                    effect_height,
                    .7,
                    fade_rate,
                    .6
                )

local_state = VersusModeState()

def init(player_data):
    local_state.init(player_data)

def handle_events():
    local_state.handle_events()

def initialized():
    return local_state.initialized

class PlayerData():
    def __init__(
        self,
        player_position,
        player_type,
        moveset,
        size,
        color,
        difficulty = None
    ):
        self.player_position = player_position
        self.player_type = player_type
        self.moveset = moveset
        self.size = size
        self.color = color
        self.difficulty = difficulty

def create_player(player_data):   
    player = None
    
    #Create Player
    if player_data.player_type == PlayerTypes.BOT:
        player = aiplayer.Bot(
            (0, 0),
            player_data.player_position
        )
    elif player_data.player_type == PlayerTypes.HUMAN:
        player = humanplayer.HumanPlayer(
            (0, 0),
            player_data.player_position
        )
    else:
        raise Exception(
            "No player type set for player position: " + str(player_data.player_position)
        )
    
    player.init_state()
    
    if player_data.player_type == PlayerTypes.BOT:
        player.set_difficulty(player_data.difficulty)
    
    player.set_player_stats(player_data.size)
    player.load_moveset(player_data.moveset)
    player.model.velocity = (0,0)
    player.health_color = player_data.color
    
    if player_data.player_position == PlayerPositions.PLAYER1:
        player.direction = PlayerStates.FACING_RIGHT
        player.model.move_model(gamestate.stage.player_positions[0])
    else:
        player.direction = PlayerStates.FACING_LEFT
        player.model.move_model(gamestate.stage.player_positions[1])
    
    player.action = None
    player.actions[PlayerStates.STANDING].set_player_state(player)
    
    return player

class KeyToCommandTypeConverter():
    def __init__(self, key_to_command_type):
        self.key_to_command_type = key_to_command_type
    
    def get_command_data(self, keys_pressed):
            
        return InputCommandTypes(
           self.get_attack_command_types(keys_pressed),
           self.get_ground_movement_command_type(keys_pressed),
           self.get_aerial_movement_command_types(keys_pressed),
           self.get_aerial_action_command_types(keys_pressed),
           self.get_stun_movement_command_types(keys_pressed)
       )
    
    def get_attack_command_types(self, keys_pressed):
        """Returns the valid key combinations for attack keys. All movement
        commands and attack commands valid, however MOVE_RIGHT and MOVE_LEFT 
        are changed into MOVE_FORWARD commands. Also NO_MOVMENT is NOT an 
        active command if no movement keys are pressed."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                command_type = self.key_to_command_type[key]
                if (command_type in CommandCollections.ATTACK_ACTIONS):
                    
                    if (command_type == InputActionTypes.MOVE_RIGHT or
                    command_type == InputActionTypes.MOVE_LEFT):
                        return_command_types.append(InputActionTypes.FORWARD)
                        
                    else:
                        return_command_types.append(command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        return return_command_types
    
    def get_ground_movement_command_type(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_type = InputActionTypes.NO_MOVEMENT
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.GROUND_MOVEMENTS:
                    
                    if key_command_type == InputActionTypes.MOVE_DOWN:
                        return_command_type = key_command_type
                    
                    elif (key_command_type == InputActionTypes.JUMP and
                    return_command_type != InputActionTypes.MOVE_DOWN):
                        return_command_type = key_command_type
                    
                    elif key_command_type == InputActionTypes.MOVE_LEFT:
                        if (return_command_type != InputActionTypes.MOVE_DOWN and
                        return_command_type != InputActionTypes.MOVE_UP and 
                        return_command_type != InputActionTypes.MOVE_RIGHT):
                            return_command_type = key_command_type
                        
                        elif return_command_type == InputActionTypes.MOVE_RIGHT:
                            return_command_type = InputActionTypes.NO_MOVEMENT
                    
                    elif key_command_type == InputActionTypes.MOVE_RIGHT:
                        if (return_command_type != InputActionTypes.MOVE_DOWN and
                        return_command_type != InputActionTypes.MOVE_UP and 
                        return_command_type != InputActionTypes.MOVE_LEFT):
                            return_command_type = key_command_type
                        
                        elif return_command_type == InputActionTypes.MOVE_LEFT:
                            return_command_type = InputActionTypes.NO_MOVEMENT
                    
                else:
                    #it is not a valid ground movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key so pass
                pass
        
        return return_command_type
    
    def get_aerial_movement_command_types(self, keys_pressed):
        """Returns the valid key combinations for aerial movement keys.
        MOVE_LEFT, MOVE_RIGHT, and MOVE_DOWN are the only valid commands for 
        aerial commands.  If none of the keys in keys_pressed are bound to any 
        of those command_types NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.AERIAL_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def get_aerial_action_command_types(self, keys_pressed):
        """Returns the command with highest precedence out of the pressed keys. 
        Only one movement command is allowed at a time for ground movements. If
        none of the keys in keys_pressed are bound to a ground movement command
        type then NO_MOVMENT is the active command type."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
                key_command_type = self.key_to_command_type[key]
                
                if key_command_type in CommandCollections.AERIAL_ACTIONS:
                    
                    if key_command_type == InputActionTypes.NO_MOVEMENT:
                        #the key command is no movment
                        pass
                    elif (key_command_type == InputActionTypes.MOVE_RIGHT or
                    key_command_type == InputActionTypes.MOVE_LEFT):
                        return_command_types.append(InputActionTypes.FORWARD)
                    else:
                        return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial action so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        if len(return_command_types) == 0:
            return_command_types.append(InputActionTypes.NO_MOVEMENT)
        
        return return_command_types
    
    def get_stun_movement_command_types(self, keys_pressed):
        """Returns the valid key combinations for stun movement keys.
        MOVE_LEFT, MOVE_RIGHT, MOVE_DOWN, and MOVE_UP are the only valid 
        commands for stun commands."""
        
        return_command_types = []
        
        for key in keys_pressed:
            if key in self.key_to_command_type:
            
                key_command_type = self.key_to_command_type[key]
                if key_command_type in CommandCollections.STUN_MOVEMENTS:
                    
                    return_command_types.append(key_command_type)
                    
                else:
                    #it is not a valid aerial movement so add nothing for this 
                    #key
                    pass
            else:
                #not a mapped key, so pass
                pass
        
        return return_command_types
