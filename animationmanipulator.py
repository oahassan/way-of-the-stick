def flip_animation(animation):
    #get x center of animation
    x_center = get_animation_x_center(animation)
    
    #subtract/add 2 * distance to center from each point
    for frame in animation.frames:
        for point in frame.point_dictionary.values():
            x_position = point.pos[0]
            
            if x_position > x_center:
                point.pos = (
                    x_center - (x_position - x_center),
                    point.pos[1]
                )
            else:
                point.pos = (
                    x_center + (x_center - x_position),
                    point.pos[1]
                )

def get_animation_x_center(animation):
    min_x = min([frame.reference_pos[0] for frame in animation.frames])
    max_x = 0
    
    for frame in animation.frames:
        frame_max_x = max([point.pos[0] for point in frame.point_dictionary.values()])
        
        if frame_max_x > max_x:
            max_x = frame_max_x
    
    return max_x - min_x / 2.0
