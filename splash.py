import math
import pygame
import physics
import button
import player
import gamestate
import wotsuievents
import stick
import mathfuncs
import stage
import wotsrendering
import versusrendering

model_points = {
    "leftknee":(327.0, 397.0),
    "torobottom":(359.20003832670159, 389.772695653222),
    "lefthand":(379.00012005298674, 365.00000242725667),
    "headtop":(360.00389424414533, 294.77839592055835),
    "rightfoot":(347.82556957482643, 401.05051726341674),
    "rightknee":(393.09972251248587, 400.54944264080564),
    "rightelbow":(380.08871934933899, 364.00045161073228),
    "leftfoot":(376.90830898159703, 399.67594742052978),
    "torsotop":(359.38893487538741, 329.77299300317634),
    "leftelbow":(339.00829306884123, 364.19143921379521),
    "righthand":(343.00000000003388, 364.99999999999909)
}

def create_model():
    global model_points
    model = physics.Model((0,0))
    model.init_stick_data()
    
    for point_name, position in model_points.iteritems():
        model.points[point_name].pos = position
    model.scale(3)
    #import pdb;pdb.set_trace()
    model_rect = pygame.Rect(*model.get_enclosing_rect())
    model_position = (300, 160)
    model.move_model(model_position)
    
    return model

model = create_model()
stick_surface_position_delta = -.3
stick_surface_path_count = 0
stick_surface_current_delta = 0
camera = versusrendering.ViewportCamera(800,600,800,600)

title_label = button.Label((50,50), "Way of the Stick", (255,255,255), 82)#, "NinjaLine.ttf")
credits_label = button.Label((20, 550), "Powered by Pygame.", (255,255,255), 32)
loading_label = button.Label((185, 50), "Loading...", (255,255,255), 82)#, "NinjaLine.ttf")

def draw_bkg_and_stick():
    ground_surface = stage.draw_ground(800, 200)
    gamestate.screen.fill((0,0,0), ((0,450),(800,250)))
    gamestate.screen.fill((0,0,0), ((0,0),(800,450)))
    gamestate.screen.blit(ground_surface, (0, 450))
    versusrendering.draw_reflection(
        model,
        (255,255,255),
        (0,0,0),
        30,
        camera,
        gamestate.screen,
        500
    )
    versusrendering.draw_player(
        model, 
        (255,255,255),
        (0,0,0),
        30,
        gamestate.screen,
        1)
    
    wotsrendering.flush()

def draw_title_splash():
    
    draw_bkg_and_stick()
    
    title_label.draw(gamestate.screen)
    credits_label.draw(gamestate.screen)

def draw_loading_splash():
    draw_bkg_and_stick()
    
    loading_label.draw(gamestate.screen)
    
    pygame.display.flip()

def handle_events():
    global model
    global stick_surface_position_delta
    global stick_surface_path_count
    global stick_surface_current_delta
    global title_label
    global credits_label
    
    draw_title_splash()
    stick_surface_path_count = (stick_surface_path_count + 1) % 360
    
    if (pygame.KEYDOWN in wotsuievents.event_types or
    pygame.MOUSEBUTTONDOWN in wotsuievents.event_types):
        gamestate.mode = gamestate.Modes.MAINMENU
