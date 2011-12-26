import pygame

class DrawTypes:
    LINE = 0
    CIRCLE = 1
    RECT = 2
    ELLIPSE = 3
    POLYGON = 4
    SURFACE = 5

draw_queue = {}

def flush():
    keys = sorted(draw_queue.keys())
    
    for key in keys:
        for queued_draw_args in draw_queue[key]:
            draw(*queued_draw_args)
        
        draw_queue[key] = []

def draw(draw_type, args):
    if draw_type == DrawTypes.LINE:
        pygame.draw.line(*args)
    elif draw_type == DrawTypes.CIRCLE:
        pygame.draw.circle(*args)
    elif draw_type == DrawTypes.POLYGON:
        pygame.draw.polygon(*args)
    elif draw_type == DrawTypes.SURFACE:
        args[0].blit(args[1], args[2])

def add_draw_to_queue(layer, args):
    global draw_queue
    
    if layer in draw_queue:
        draw_queue[layer].append(args)
    else:
        draw_queue[layer] = [args]

def queue_line(layer, surface, color, point1, point2, thickness=0):
    
    add_draw_to_queue(
        layer,
        (
            DrawTypes.LINE, 
            (surface, 
            color, 
            point1, 
            point2, 
            thickness)
        )
    )

def queue_circle(layer, surface, color, point, radius, thickness=0):
    
    add_draw_to_queue(
        layer,
        (
            DrawTypes.CIRCLE, 
            (surface,
            color,
            point,
            int(radius))
        )
    )

def queue_polygon(layer, surface, color, points, thickness=0):
    add_draw_to_queue(
        layer,
        (
            DrawTypes.POLYGON, 
            (surface,
            color,
            points,
            thickness)
        )
    )

def queue_surface(layer, surface, source, position):
    add_draw_to_queue(
        layer,
        (
            DrawTypes.SURFACE,
            (surface, source, position)
        )
    )
            
