import math
import pygame
import physics
import button
import player
import gamestate
import wotsuievents
import stick
import mathfuncs

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

def draw_model(model, surface, color = (0,0,0)):
    for name, point in model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_outline_point(point, surface)
    
    for name, line in model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_outline_circle(line, surface)
        else:
            draw_outline_line(line, surface)
    
    for name, point in model.points.iteritems():
        if name != stick.PointNames.HEAD_TOP:
            draw_inner_point(point, surface, color)
    
    for name, line in model.lines.iteritems():
        if name == stick.LineNames.HEAD:
            draw_inner_circle(line, surface, color)
        else:
            draw_inner_line(line, surface, color)

def draw_outline_line(line, surface):
    pygame.draw.line(surface, (255,255,255), line.endPoint1.pixel_pos(), line.endPoint2.pixel_pos(), 40)
    
def draw_inner_line(line, surface, color):
    pygame.draw.line(surface, color, line.endPoint1.pixel_pos(), line.endPoint2.pixel_pos(), 30)

def draw_outline_circle(circle, surface):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, circle.endPoint2.pos))
    position = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, (255, 255, 255), (int(position[0]), int(position[1])), int(radius))

def draw_inner_circle(circle, surface, color):
    radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, circle.endPoint2.pos))
    position = mathfuncs.midpoint(circle.endPoint1.pos, circle.endPoint2.pos)
    
    pygame.draw.circle(surface, color, (int(position[0]), int(position[1])), int(radius) - 5)

def draw_outline_point(point, surface):
    pygame.draw.circle(surface, (255,255,255), point.pixel_pos(), 20)

def draw_inner_point(point, surface, color):
    pygame.draw.circle(surface, color, point.pixel_pos(), 15)

model = create_model()
stick_surface_position_delta = -.3
stick_surface_path_count = 0
stick_surface_current_delta = 0

title_label = button.Label((50,50), "Way of the Stick", (255,255,255), 66, "NinjaLine.ttf")
credits_label = button.Label((20, 550), "Powered by Pygame.", (255,255,255), 32)
loading_label = button.Label((185, 50), "Loading...", (255,255,255), 66, "NinjaLine.ttf")

def draw_title_splash():
    title_label.draw(gamestate.screen)
    credits_label.draw(gamestate.screen)
    draw_model(model, gamestate.screen)

def draw_loading_splash():
    loading_label.draw(gamestate.screen)
    draw_model(model, gamestate.screen)
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
