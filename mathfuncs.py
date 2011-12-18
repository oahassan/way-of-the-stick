import math

def distance(pos1, pos2):
    """Finds the distance between to points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    
    return math.sqrt(math.fsum([(pos1[i] - pos2[i])**2 \
                    for i in range(len(pos1))]))
                    
def slope(pos1, pos2):
    """Finds the slope of the line between two-dimensional points"""
    if len(pos1) != len(pos2):
        raise Exception('position tuples have different lengths!')
    if ((len(pos1) != 2)
    or (len(pos2) != 2)):
        raise Exception('positions are not two dimensional!')
    xDelta = pos1[0] - pos2[0]
    yDelta = pos1[1] - pos2[1]
    
    return float(yDelta) / xDelta

def midpoint(pos1, pos2):
    """Finds the midpoint between two points"""
    x_pos = (pos1[0] + pos2[0]) / float(2)
    y_pos = (pos1[1] + pos2[1]) / float(2)
    
    return (x_pos, y_pos)

def sign(number):
    """returns the sign of a number"""
    return_sign = None
    
    if number == 0:
        return_sign = 0
    else:
        return_sign = int(number / abs(number))
    
    return return_sign

def test_overlap(self, rect1, rect2):
        """a fast test if two players could possibly be attacking each other"""
        
        overlap = True
        rect1_pos = (rect1.left, rect1.top)
        rect2_pos = (rect2.left, rect2.top)
        
        if ((rect1_pos[0] > (rect2_pos[0] + rect2.width)) or
            ((rect1_pos[0] + rect1.width) < rect2_pos[0]) or
            (rect1_pos[1] > (rect2_pos[1] + rect2.height)) or
            ((rect1_pos[1] + rect1.height) < rect2_pos[1])):
            overlap = False
        
        return overlap
