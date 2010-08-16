import math

def distance(pos1, pos2):
    """finds the distance between to points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    
    return math.sqrt(math.fsum([(pos1[i] - pos2[i])**2 \
                    for i in range(len(pos1))]))
                    
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