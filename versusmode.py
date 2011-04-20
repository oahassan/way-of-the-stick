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

gamestate.stage = stage.ScrollableStage(1047, 0, gamestate._WIDTH)

initialized = False
player_dictionary = {
    PlayerPositions.PLAYER1 : None,
    PlayerPositions.PLAYER2 : None
}
player_type_dictionary = {
    PlayerPositions.PLAYER1 : None,
    PlayerPositions.PLAYER2 : None
}
fight_label = None
ready_label = None
player1_wins_label = None
player2_wins_label = None
match_state = None
match_time = None
exit_button = button.ExitButton()
exit_indicator = False
versus_mode_start_time = None
fight_start_time = None
fight_end_time = None
fight_end_timer = None
versus_mode_start_timer = None
fight_start_timer = None
fps_label = None
command_label = None
point_effects = {}
player_renderer_state = None
surface_renderer = None
match_simulation = None
simulation_process = None
simulation_connection = None

stun_channel = None
clash_sound = pygame.mixer.Sound("./sounds/clash-sound.ogg")
clash_sound.set_volume(settingsdata.get_sound_volume())

def init():
    global initialized
    global exit_indicator
    global player_dictionary
    global player_type_dictionary
    global ready_label
    global fight_label
    global player1_wins_label
    global player2_wins_label
    global match_state
    global match_time
    global fight_end_timer
    global versus_mode_start_timer
    global fight_start_timer
    global fps_label
    global point_effects
    global command_label
    global player_renderer_state
    global surface_renderer
    global match_simulation
    global simulation_connection
    
    point_effects = {}
    fps_label = button.Label((20,20), str(gamestate.clock.get_fps()),(0,0,255),30)
    #command_label = AttackLabel("", [])
    #command_label.key_combination_label.set_position((20,50))
    
    match_state = MatchStates.READY
    match_time = 0
    fight_end_timer = 0
    versus_mode_start_timer = 0
    fight_start_timer = 0
    
    ready_label = button.Label((0,0),'READY...',(0,0,255),80)
    ready_label_position = ((gamestate._WIDTH / 2) - (ready_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (ready_label.height / 2))
    ready_label.set_position(ready_label_position)
    
    fight_label = button.Label((0,0),'FIGHT!',(0,0,255),80)
    fight_label_position = ((gamestate._WIDTH / 2) - (fight_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (fight_label.height / 2))
    fight_label.set_position(fight_label_position)
    
    player1_wins_label = button.Label((0,0),'PLAYER 1 WINS!',(0,0,255),80)
    player1_wins_label_position = (
        (gamestate._WIDTH / 2) - (player1_wins_label.width / 2), 
        (gamestate._HEIGHT / 2) - (player1_wins_label.height / 2)
    )
    player1_wins_label.set_position(player1_wins_label_position)
    
    player2_wins_label = button.Label((0,0),'PLAYER 2 WINS!',(0,0,255),80)
    player2_wins_label_position = (
        (gamestate._WIDTH / 2) - (player2_wins_label.width / 2),
        (gamestate._HEIGHT / 2) - (player2_wins_label.height / 2)
    )
    player2_wins_label.set_position(player2_wins_label_position)
    
    for player_position in player_type_dictionary.keys():
        if player_type_dictionary[player_position] == PlayerTypes.BOT:
            player_dictionary[player_position] = aiplayer.Bot((0, 0))
        elif player_type_dictionary[player_position] == PlayerTypes.HUMAN:
            player_dictionary[player_position] = humanplayer.HumanPlayer((0, 0))
        else:
            raise Exception(
                "No player type set for player position: " + str(player_position)
            )
    
    simulation_connection, input_connection = multiprocessing.Pipe()
    
    match_simulation = MatchSimulation(
        input_connection,
        player_dictionary=player_dictionary,
        player_type_dictionary=player_type_dictionary
    )
    
    player1 = player_dictionary[PlayerPositions.PLAYER1]
    player1.init_state()
    player1.model.move_model((700, 967))
    
    player2 = player_dictionary[PlayerPositions.PLAYER2]
    player2.init_state()
    player2.model.move_model((1100, 967))
    player2.color = (100,100,100)
    player2.health_color = (200,200,200)
    
    camera = versusrendering.ViewportCamera(
        gamestate.stage.width,
        gamestate.stage.height,
        gamestate._WIDTH,
        gamestate._HEIGHT
    )
    player_renderer_state = versusrendering.PlayerRendererState(
        camera,
        player_dictionary.keys()
    )
    
    surface_renderer = versusrendering.SurfaceRenderer(camera)
    
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
    initialized = True
    exit_indicator = False
    
    gamestate.frame_rate = gamestate.VERSUSMODE_FRAMERATE
    gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS
    
    gamestate.stage = stage.ScrollableStage(1047, 0, gamestate._WIDTH)
    gamestate.screen.blit(gamestate.stage.background_image, (0,0))
    gamestate.new_dirty_rects.append(
        pygame.Rect((0,0), (gamestate._WIDTH, gamestate._HEIGHT))
    )

def exit():
    global initialized
    global ready_label
    global fight_label
    global player1_wins_label
    global player2_wins_label
    global match_state
    global match_time
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    global point_effects
    global command_label
    global player_renderer_state
    global match_simulation
    global simulation_connection
    global simulation_process
    
    simulation_connection.send('STOP')
    simulation_connection.close()
    simulation_process.terminate()
    simulation_process.join()
    simulation_connection = None
    gamestate.processes.remove(simulation_process)
    simulation_process = None
    match_simulation = None
    point_effects = {}
    player_renderer_state = None
    fps_label = None
    command_label = None
    ready_label = None
    fight_label = None
    player1_wins_label = None
    player2_wins_label = None
    match_state = None
    match_time = 0
    versus_mode_start_timer = None
    fight_start_timer = None
    fight_end_timer = None
    initialized = False
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.NONE
    gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
    gamestate.frame_rate = gamestate.NORMAL_FRAMERATE
    
def handle_events():
    global exit_button
    global exit_indicator
    global match_state
    global fps_label
    global comamnd_label
    global effects
    global player_renderer_state
    global surface_renderer
    global player_dictionary
    global match_simulation
    global simulation_process
    global simulation_connection
    global match_state
    global match_time
    
    if simulation_process == None and exit_indicator == False:
        #initialize renderer state
        player_renderer_state.update(
            match_simulation.get_rendering_info().player_rendering_info_dictionary, 
            1
        )
        
        #start simulation process
        simulation_process = multiprocessing.Process(
            target=match_simulation.run,
            name="Way of the stick simulation"
        )
        gamestate.processes.append(simulation_process)
        simulation_process.start()
        
        #reset game clock
        gamestate.time_passed = 10
    
    exit_button.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(
        pygame.Rect(exit_button.position, 
        (exit_button.width,exit_button.height))
    )
    
    fps_label.set_text(str(gamestate.clock.get_fps()))
    fps_label.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(
        pygame.Rect(fps_label.position,(fps_label.width,fps_label.height))
    )
    
    if exit_indicator == False:
        simulation_rendering_info = None
        
        while simulation_connection.poll():
            simulation_rendering_info = simulation_connection.recv()
        
        if simulation_rendering_info != None:
            set_outline_color(simulation_rendering_info)
            
            if simulation_rendering_info.attack_result_rendering_info != None:
                create_collision_effects(
                    simulation_rendering_info.attack_result_rendering_info
                )
            
            player_renderer_state.update(
                simulation_rendering_info.player_rendering_info_dictionary, 
                1
            )
            match_state = simulation_rendering_info.match_state
            match_time = simulation_rendering_info.match_time
        
        ground_surface = gamestate.stage.draw_ground()
        surface_renderer.draw_surface_to_screen(
            (0, gamestate.stage.floor_height - 20), 
            ground_surface
        )
        versusrendering.draw_player_renderer_state(
            player_renderer_state, 
            gamestate.screen
        )
        
        for effect in point_effects.values():
            effect.update(gamestate.time_passed)
            effect_position, effect_surface = effect.draw_ellipse_effect()
            surface_renderer.draw_surface_to_screen(
                effect_position, 
                effect_surface
            )
        
        dead_effects = []
        
        for point_id, effect in point_effects.iteritems():
            if effect.effect_over():
                dead_effects.append(point_id)
        
        for point_id in dead_effects:
            del point_effects[point_id]
        
        handle_match_state()
    
    if simulation_connection != None:
        simulation_connection.send(
            (build_player_keys_pressed(), gamestate.time_passed)
        )
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                exit()

def set_outline_color(simulation_rendering_info):
    player_rendering_info_dictionary = simulation_rendering_info.player_rendering_info_dictionary
    
    for player_position, rendering_info in player_rendering_info_dictionary.iteritems():
        
        if rendering_info.player_state == PlayerStates.STUNNED:
            if (simulation_rendering_info.match_time % 30) >= 15:
                rendering_info.player_outline_color = (255, 255, 0)
            else:
                rendering_info.player_outline_color = (255, 0, 0)
        else:
            pass #leave the outline color as it is

def handle_match_state():
    global match_state
    global match_time
    global ready_label
    global fight_label
    global player1_wins_label
    global player2_wins_label
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    
    if match_state == MatchStates.READY:
        ready_label.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(
            pygame.Rect(ready_label.position,(ready_label.width,ready_label.height))
        )
        
    elif match_state == MatchStates.FIGHT and match_time < 4000:
        fight_start_timer += gamestate.clock.get_time()
        match_state = MatchStates.FIGHT
        gamestate.new_dirty_rects.append(
            pygame.Rect(fight_label.position,(fight_label.width,fight_label.height))
        )
    
    elif match_state == MatchStates.PLAYER1_WINS:
        
        if fight_end_timer < 8000:
            fight_end_timer += gamestate.clock.get_time()
            player1_wins_label.draw(gamestate.screen)
            
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    player1_wins_label.position, 
                    (player1_wins_label.width, player1_wins_label.height)
                )
            )
            
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()
    elif match_state == MatchStates.PLAYER2_WINS:
        
        if fight_end_timer < 8000:
            fight_end_timer += gamestate.clock.get_time()
            player2_wins_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(player2_wins_label.position, \
                                             (player2_wins_label.width, \
                                              player2_wins_label.height)))
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()

def build_player_keys_pressed():
    return {
        PlayerPositions.PLAYER1 : wotsuievents.keys_pressed,
        PlayerPositions.PLAYER2 : wotsuievents.keys_pressed
    }

def create_collision_effects(attack_result_rendering_info):
    global point_effects
    
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
    if not attack_point.id in point_effects:
        point_effects[attack_point.id] = Effect(
            attack_result_rendering_info.attack_point.pos,
            angle_in_degrees,
            effect_width,
            effect_height,
            .7,
            fade_rate,
            .6
        )
