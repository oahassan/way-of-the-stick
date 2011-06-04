import multiprocessing
import pygame
from wotsfx import Effect
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
from simulation import MatchSimulation
from attackbuilderui import AttackLabel
from enumerations import PlayerPositions, MatchStates, PlayerTypes, ClashResults, \
PlayerStates
from versussound import AttackResultSoundMixer, PlayerSoundMixer

gamestate.stage = stage.ScrollableStage(1047, 0, gamestate._WIDTH)
step_number = 0

class VersusModeState():
    def __init__(self):
        
        self.initialized = False
        self.player_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_type_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_sound_mixer_dictionary = {
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
        self.versus_mode_start_time = None
        self.fight_start_time = None
        self.fight_end_time = None
        self.fight_end_timer = None
        self.versus_mode_start_timer = None
        self.fight_start_timer = None
        self.fps_label = None
        self.command_label = None
        self.point_effects = {}
        self.player_renderer_state = None
        self.surface_renderer = None
        self.match_simulation = None
        self.simulation_process = None
        self.simulation_connection = None

        self.attack_result_sound_mixer = AttackResultSoundMixer()
    
    def init(self):
        
        self.init_match_state_variables()
        self.init_rendering_objects()
        self.init_player_data()
        self.init_simulation_objects()
        self.set_GUI_module_variables()
        self.init_stage()
        self.init_screen()
        
        self.initialized = True
        self.exit_indicator = False

    def init_screen(self):
        gamestate.screen.blit(gamestate.stage.background_image, (0,0))
        gamestate.new_dirty_rects.append(
            pygame.Rect((0,0), (gamestate._WIDTH, gamestate._HEIGHT))
        )

    def init_stage(self):
        gamestate.stage = stage.ScrollableStage(1047, 0, gamestate._WIDTH)

    def set_GUI_module_variables(self):
        wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
        gamestate.frame_rate = gamestate.VERSUSMODE_FRAMERATE
        gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS

    def exit(self):
        
        self.end_simulation()
        self.cleanup_rendering_objects()
        self.cleanup_match_state_variables()
        self.reset_GUI_variables()
        self.initialized = False

    def reset_GUI_variables(self):
        wotsuievents.key_repeat = wotsuievents.KeyRepeat.NONE
        gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
        gamestate.frame_rate = gamestate.NORMAL_FRAMERATE

    def handle_events(self):
        
        if self.simulation_process == None and self.exit_indicator == False:
            self.start_match_simulation()
        
        self.fps_label.set_text(str(gamestate.clock.get_fps()))
        self.fps_label.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                self.fps_label.position,
                (self.fps_label.width, self.fps_label.height))
        )
        
        if self.exit_indicator == False:
            simulation_rendering_info = None
            
            while self.simulation_connection.poll():
                simulation_rendering_info = self.simulation_connection.recv()
                
                self.update_simulation_rendering(simulation_rendering_info)
            
            self.render_simulation()
            
            self.clean_expired_effects()
            
            self.handle_match_state()
        
        if self.simulation_connection != None:
            self.update_simulation()
        
        self.handle_exit_events()

    def build_player_keys_pressed(self):
        return {
            PlayerPositions.PLAYER1 : wotsuievents.keys_pressed,
            PlayerPositions.PLAYER2 : wotsuievents.keys_pressed
        }
    
    def init_simulation_objects(self):
        
        self.simulation_connection, input_connection = multiprocessing.Pipe()
        
        self.match_simulation = MatchSimulation(
            input_connection,
            player_dictionary=self.player_dictionary,
            player_type_dictionary=self.player_type_dictionary
        )

    def init_player_data(self):
        
        for player_position in self.player_type_dictionary.keys():
            if self.player_type_dictionary[player_position] == PlayerTypes.BOT:
                self.player_dictionary[player_position] = aiplayer.Bot((0, 0))
            elif self.player_type_dictionary[player_position] == PlayerTypes.HUMAN:
                self.player_dictionary[player_position] = humanplayer.HumanPlayer(
                    (0, 0)
                )
            else:
                raise Exception(
                    "No player type set for player position: " + str(player_position)
                )
        
        player1 = self.player_dictionary[PlayerPositions.PLAYER1]
        player1.direction = PlayerStates.FACING_RIGHT
        player1.init_state()
        player1.model.move_model((400, 967))
        
        player2 = self.player_dictionary[PlayerPositions.PLAYER2]
        player2.direction = PlayerStates.FACING_LEFT
        player2.init_state()
        player2.model.move_model((1200, 967))
        player2.color = (100,100,100)
        player2.health_color = (200,200,200)
    
    def init_player_sounds(self):
        player1 = self.player_dictionary[PlayerPositions.PLAYER1]
        self.player_sound_mixer_dictionary[PlayerPositions.PLAYER1] = PlayerSoundMixer(player1)
        
        player2 = self.player_dictionary[PlayerPositions.PLAYER2]
        self.player_sound_mixer_dictionary[PlayerPositions.PLAYER2] = PlayerSoundMixer(player2)
    
    def init_match_state_variables(self):
        
        self.match_state = MatchStates.READY
        self.match_time = 0
        self.fight_end_timer = 0
        self.versus_mode_start_timer = 0
        self.fight_start_timer = 0

    def init_rendering_objects(self):
        
        self.point_effects = {}
        
        camera = versusrendering.ViewportCamera(
            gamestate.stage.width,
            gamestate.stage.height,
            gamestate._WIDTH,
            gamestate._HEIGHT
        )
        self.player_renderer_state = versusrendering.PlayerRendererState(
            camera,
            [PlayerPositions.PLAYER1, PlayerPositions.PLAYER2]
        )
        
        self.surface_renderer = versusrendering.SurfaceRenderer(camera)
        
        self.fps_label = button.Label(
            (20,20), 
            str(gamestate.clock.get_fps()),(0,0,255),
            30
        )
        #command_label = AttackLabel("", [])
        #command_label.key_combination_label.set_position((20,50))
        
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
    
    def cleanup_match_state_variables(self):
        
        self.match_state = None
        self.match_time = 0
        self.versus_mode_start_timer = None
        self.fight_start_timer = None
        self.fight_end_timer = None

    def cleanup_rendering_objects(self):
        
        self.point_effects = {}
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
        self.simulation_connection.close()
        self.simulation_process.terminate()
        self.simulation_process.join()
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
        
        ground_surface = gamestate.stage.draw_ground()
        self.surface_renderer.draw_surface_to_screen(
            (0, gamestate.stage.floor_height - 20), 
            ground_surface
        )
        versusrendering.draw_player_renderer_state(
            self.player_renderer_state, 
            gamestate.screen
        )
        
        for effect in self.point_effects.values():
            effect.update(gamestate.time_passed)
            effect_position, effect_surface = effect.draw_ellipse_effect()
            self.surface_renderer.draw_surface_to_screen(
                effect_position, 
                effect_surface
        )

    def update_simulation(self):
        self.simulation_connection.send(
            (self.build_player_keys_pressed(), gamestate.time_passed)
        )

    def update_simulation_rendering(self, simulation_rendering_info):
        
        self.set_outline_color(simulation_rendering_info)
        
        if simulation_rendering_info.attack_result_rendering_info != None:
            self.create_collision_effects(
                simulation_rendering_info.attack_result_rendering_info
            )
            self.attack_result_sound_mixer.handle_hit_sounds(
                simulation_rendering_info.attack_result_rendering_info
            )
        
        self.player_renderer_state.update(
            simulation_rendering_info.player_rendering_info_dictionary, 
            1
        )
        self.play_player_sounds(simulation_rendering_info, PlayerPositions.PLAYER1)
        self.play_player_sounds(simulation_rendering_info, PlayerPositions.PLAYER2)
        self.match_state = simulation_rendering_info.match_state
        self.match_time = simulation_rendering_info.match_time
    
    def play_player_sounds(self, simulation_rendering_info, player_position):
        player_rendering_info = simulation_rendering_info.player_rendering_info_dictionary[player_position]
        
        self.player_sound_mixer_dictionary[player_position].play_sound(
            player_rendering_info.player_state,
            player_rendering_info.animation_name,
            player_rendering_info.frame_index
        )
    
    def start_match_simulation(self):    
        
        self.match_simulation.step(
            self.build_player_keys_pressed(), self.match_simulation.timestep
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
            self.fight_start_timer += gamestate.time_passed
            self.match_state = MatchStates.FIGHT
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
            self.point_effects[attack_point.id] = Effect(
                attack_result_rendering_info.attack_point.pos,
                angle_in_degrees,
                effect_width,
                effect_height,
                .7,
                fade_rate,
                .6
            )

local_state = VersusModeState()

def init():
    local_state.init()

def handle_events():
    local_state.handle_events()

def initialized():
    return local_state.initialized
