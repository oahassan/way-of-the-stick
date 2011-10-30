import multiprocessing
import pygame
from wotsfx import ClashEffect, HitEffect
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
from versusmodeui import PlayerHealth, AttackList, PAUSE_MENU_WIDTH, PAUSE_MENU_HEIGHT
from simulation import MatchSimulation
from attackbuilderui import AttackLabel
from enumerations import PlayerPositions, MatchStates, PlayerTypes, ClashResults, \
PlayerStates, CommandCollections, InputActionTypes
from versussound import AttackResultSoundMixer, PlayerSoundMixer
from controlsdata import get_controls
from playercontroller import InputCommandTypes

gamestate.stage = stage.ScrollableStage(1047, 0, gamestate._WIDTH)
step_number = 0

class VersusModeState():
    def __init__(self):
        
        self.initialized = False
        self.player_dictionary = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }
        self.player_key_handlers = {
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
        self.pause = False
        self.pause_held = False
        self.attack_lists = {
            PlayerPositions.PLAYER1 : None,
            PlayerPositions.PLAYER2 : None
        }

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
        gamestate.update_screen()

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
        
        if gamestate.devmode:
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
                
                if simulation_rendering_info.match_time > self.match_time:
                    self.update_simulation_rendering(simulation_rendering_info)
            
            self.render_simulation()
            
            self.handle_pause_events()
            
            if not self.pause:
                self.clean_expired_effects()
                
                self.handle_match_state()
        
        if self.simulation_connection != None:
            self.update_simulation()
        
        self.handle_exit_events()
    
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
    
    def init_player_health_bars(self):
        self.player_health_bars[PlayerPositions.PLAYER1] = PlayerHealth(
            self.player_dictionary[PlayerPositions.PLAYER1].moveset.name, 
            PlayerPositions.PLAYER1
        )
        self.player_health_bars[PlayerPositions.PLAYER2] = PlayerHealth(
            self.player_dictionary[PlayerPositions.PLAYER2].moveset.name,
            PlayerPositions.PLAYER2
        )
    
    def init_attack_lists(self):
        self.attack_lists[PlayerPositions.PLAYER1] = AttackList(
            self.player_dictionary[PlayerPositions.PLAYER1].moveset,
            (
                int((gamestate._WIDTH / 2) - PAUSE_MENU_WIDTH),
                int((gamestate._HEIGHT / 2) - (PAUSE_MENU_HEIGHT / 2))
            )
        )
        self.attack_lists[PlayerPositions.PLAYER2] = AttackList(
            self.player_dictionary[PlayerPositions.PLAYER2].moveset,
            (
                int((gamestate._WIDTH / 2)),
                int((gamestate._HEIGHT / 2) - (PAUSE_MENU_HEIGHT / 2))
            )
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
            
            
            self.player_key_handlers[player_position] = KeyToCommandTypeConverter(
                dict([(entry[1], entry[0]) for entry in get_controls().iteritems()])
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
        self.player_health_bars = {}
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
            if not self.pause:
                effect.update(gamestate.time_passed)
            
            effect_position, effect_surface = effect.draw_effect()
            self.surface_renderer.draw_surface_to_screen(
                effect_position, 
                effect_surface
            )
        
        for health_bar in self.player_health_bars.values():
            self.surface_renderer.draw_surface_to_absolute_position(
                health_bar.position, 
                health_bar.draw()
            )
        
        if self.pause:
            for attack_list in self.attack_lists.values():
                attack_list.draw(gamestate.screen)

    def update_simulation(self):
        self.simulation_connection.send(
            (self.build_player_command_types(), gamestate.time_passed)
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
        
        for player_position, player_rendering_info in simulation_rendering_info.player_rendering_info_dictionary.iteritems():
            health_bar = self.player_health_bars[player_position]
            health_bar.update(
                gamestate.time_passed,
                player_rendering_info.health_percentage
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

def init():
    local_state.init()

def handle_events():
    local_state.handle_events()

def initialized():
    return local_state.initialized

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
