import math

def distance(pos1, pos2):
    """finds the distance between two points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    
    return math.sqrt(math.fsum([(pos1[i] - pos2[i])**2 \
                    for i in range(len(pos1))]))

def fast_distance(pos1, pos2):
    """find a close approximation to the distance between two points
    
    this only works for two dimensional points"""
    
    distances = [abs(pos1[i] - pos2[i]) for i in range(len(pos1))]
    
    return ((1007 * max(distances)) + (441 * min(distances))) / 1024

def distance_squared(pos1, pos2):
    """find the sqyare of the distance between to points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    
    return math.fsum([(pos1[i] - pos2[i])**2 for i in range(len(pos1))])

def slope(pos1, pos2):
    """finds the slope of the line between two-dimensional points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    if ((len(pos1) != 2)
    or (len(pos2) != 2)):
        raise Exception('positions are not two dimensional!')
    xDelta = pos1[0] - pos2[0]
    yDelta = pos1[1] - pos2[1]
    
    return yDelta / xDelta

def midpoint(pos1, pos2):
    """Finds the midpoint between two points"""
    x_pos = (pos1[0] + pos2[0]) / 2
    y_pos = (pos1[1] + pos2[1]) / 2
    
    return (x_pos, y_pos)

def sign(number):
    """returns the sign of a number"""
    return_sign = None
    
    if number == 0:
        return_sign = 0
    else:
        return_sign = int(number / abs(number))
    
    return return_sign
