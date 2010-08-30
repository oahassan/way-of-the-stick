import math
import mathfuncs
import stick

GRAVITY = .005
FRICTION = .003

class Object():
    def __init__(self, \
                position = (0,0), \
                height = 0, \
                width = 0, \
                gravity = GRAVITY, \
                friction = FRICTION, \
                velocity = (0,0)):
        self.gravity = gravity
        self.friction = friction
        self.position = position
        self.height = height
        self.width = width
        self.velocity = (0,0)
    
    def pixel_pos(self):
        return (int(self.position[0]), int(self.position[1]))
    
    def accelerate(self, x_accel = 0, y_accel = 0):
        """changes the velocity of an object by the given acceleration"""
        
        velocity = self.velocity
        velocity = (velocity[0] + x_accel, velocity[1] + y_accel)
        self.velocity = velocity
    
    def shift(self, deltas):
        self.position = (self.position[0] + delta[1], self.position[1] + deltas[1])
    
    def collide(self, object, duration):
        pass
    
    def resolve_self(self, duration):
        """Changes the position of an object based on its velocity"""
        
        x_velocity = self.velocity[0]
        y_velocity = self.velocity[1] 
        
        x_displacement = x_velocity*duration
        y_displacement = y_velocity*duration + (.5*self.gravity*(duration**2))
        
        self.shift((x_displacement,y_displacement))
        
        self.velocity = (x_velocity, y_velocity + self.gravity*duration)
    
    def resolve_system(self, system, duration):
        """Changes the position of an object based off of its interaction with
        other objects
        
        system: list of objects this object may collide with"""
        for object in system:
            object.collide(self, duration)

class Ground(Object):
    def __init__(self, \
                position = (0,0), \
                height = 0, \
                width = 0):
        Object.__init__(self, position, height, width)
    
    def collide(self, object, duration):
        """Accelerate an object that collides with the ground"""
        x_velocity = object.velocity[0]
        y_velocity = object.velocity[1]
        
        if x_velocity != 0:
            #apply friction to object
            friction_sign = -1 * mathfuncs.sign(x_velocity)
            x_velocity = x_velocity + (friction_sign*self.friction*duration)
            
            #stop if the x velocity changes sign as a result of friction
            if mathfuncs.sign(x_velocity) == friction_sign:
                x_velocity = 0
        
        if object.velocity[1] > 0:
            #apply an equal and opposite force to gravity
            y_velocity = 0
        
        object.velocity = (x_velocity,y_velocity)
        
        if object.position[1] + object.height > self.position[1]:
            object.shift((0, (self.position[1] - object.height) - object.position[1]))

class Wall(Object):
    LEFT_FACING = "left"
    RIGHT_FACING = "right"
    
    def __init__(self, \
                position = (0,0), \
                height = 0, \
                width = 0, \
                direction = LEFT_FACING):
        Object.__init__(self, position, height, width)
        self.direction = direction
    
    def collide(self, object, duration):
        """accelerates an object that collides with a wall"""
        x_velocity = object.velocity[0]
        y_velocity = object.velocity[1]
        
        if self.direction == Wall.LEFT_FACING:
            if x_velocity > 0:
                x_velocity = 0
                object.velocity = (x_velocity, y_velocity)
            
            object.shift((self.position[0] - object.width - 1 - object.position[0], 0))
        
        if self.direction == Wall.RIGHT_FACING:
            if object.velocity[0] < 0:
                x_velocity = 0
                object.velocity = (x_velocity, y_velocity)
            
            object.shift((self.position[0] + 1 - object.position[0], 0))

class Model(Object):
    """A representation of the stick figure used to keep tack of its position"""
    def __init__(self, position):
        Object.__init__(self, position)
        self.points = {}
        self.lines = {}
        self.animation_run_time = 0
        self.time_passed = 0
    
    def load_points(self):
        """sets the position of each point in a stick to that from a passed in dictionary
        of named point positions"""
        
        for point_name in stick.PointNames.POINT_NAMES:
            self.points[point_name] = stick.Point((0,0))
            self.points[point_name].name = point_name
            self.points[point_name].radius = 3
    
    def load_lines(self):
        """creates the lines of the body of the model"""
        self.lines[stick.LineNames.HEAD] = stick.Circle(self.points[stick.PointNames.HEAD_TOP],
                                                        self.points[stick.PointNames.TORSO_TOP])
        self.lines[stick.LineNames.TORSO] = stick.Line(self.points[stick.PointNames.TORSO_TOP],
                                                       self.points[stick.PointNames.TORSO_BOTTOM])
        self.lines[stick.LineNames.LEFT_UPPER_ARM] = stick.Line(self.points[stick.PointNames.TORSO_TOP],
                                                                self.points[stick.PointNames.LEFT_ELBOW])
        self.lines[stick.LineNames.LEFT_FOREARM] = stick.Line(self.points[stick.PointNames.LEFT_ELBOW],
                                                              self.points[stick.PointNames.LEFT_HAND])
        self.lines[stick.LineNames.RIGHT_UPPER_ARM] = stick.Line(self.points[stick.PointNames.TORSO_TOP],
                                                                 self.points[stick.PointNames.RIGHT_ELBOW])
        self.lines[stick.LineNames.RIGHT_FOREARM] = stick.Line(self.points[stick.PointNames.RIGHT_ELBOW],
                                                               self.points[stick.PointNames.RIGHT_HAND])
        self.lines[stick.LineNames.LEFT_UPPER_LEG] = stick.Line(self.points[stick.PointNames.TORSO_BOTTOM],
                                                                self.points[stick.PointNames.LEFT_KNEE])
        self.lines[stick.LineNames.LEFT_LOWER_LEG] = stick.Line(self.points[stick.PointNames.LEFT_KNEE],
                                                                self.points[stick.PointNames.LEFT_FOOT])
        self.lines[stick.LineNames.RIGHT_UPPER_LEG] = stick.Line(self.points[stick.PointNames.TORSO_BOTTOM],
                                                                self.points[stick.PointNames.RIGHT_KNEE])
        self.lines[stick.LineNames.RIGHT_LOWER_LEG] = stick.Line(self.points[stick.PointNames.RIGHT_KNEE],
                                                                 self.points[stick.PointNames.RIGHT_FOOT])
        
        for line in self.lines.values():
            line.thickness = 7
    
    def get_reference_position(self):
        """Calculates the position of the top left corner of a rectangle
        enclosing the points of the model"""
        min_x_pos = 99999999
        min_y_pos = 99999999
        
        for line in self.lines.values():
            reference_position = line.get_reference_position()
            
            if reference_position[0] < min_x_pos:
                min_x_pos = reference_position[0]
            
            if reference_position[1] < min_y_pos:
                min_y_pos = reference_position[1]
        
        for point in self.points.values():
            reference_position = point.pos
            
            if reference_position[0] < min_x_pos:
                min_x_pos = reference_position[0]
            
            if reference_position[1] < min_y_pos:
                min_y_pos = reference_position[1]
        
        return min_x_pos, min_y_pos
    
    def get_enclosing_rect(self):
        """returns a tuple for the enclosing rect as a pygame rect"""
        top_left_x = None
        top_left_y = None
        bottom_right_x = None
        bottom_right_y = None
        
        for line in self.lines.values():
            top_left, bottom_right = line.get_top_left_and_bottom_right()
            
            if top_left_x == None:
                top_left_x = top_left[0]
                top_left_y = top_left[1]
                bottom_right_x = bottom_right[0]
                bottom_right_y = bottom_right[1]
            else:
                top_left_x = min(top_left_x,top_left[0])
                top_left_y = min(top_left_y,top_left[1])                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                bottom_right_x = max(bottom_right_x,bottom_right[0])
                bottom_right_y = max(bottom_right_y,bottom_right[1])
        width = bottom_right_x - top_left_x
        height = bottom_right_y - top_left_y
        
        return ((top_left_x, top_left_y), \
                (width, height))
    
    
    def get_top_left_and_bottom_right(self):
        """Finds the top left and bottom right containers of a rectangle containg the
        points and lines of the frame"""
        top_left_x = None
        top_left_y = None
        bottom_right_x = None
        bottom_right_y = None
        
        for line in self.lines.values():
            top_left, bottom_right = line.get_top_left_and_bottom_right()
            
            if top_left_x == None:
                top_left_x = top_left[0]
                top_left_y = top_left[1]
                bottom_right_x = bottom_right[0]
                bottom_right_y = bottom_right[1]
            else:
                top_left_x = min(top_left_x,top_left[0])
                top_left_y = min(top_left_y,top_left[1])                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                bottom_right_x = max(bottom_right_x,bottom_right[0])
                bottom_right_y = max(bottom_right_y,bottom_right[1])
        
        return ((top_left_x, top_left_y), \
                (bottom_right_x, bottom_right_y))
    
    def set_dimensions(self):
        """sets the height and width of the model"""
        position = self.get_reference_position()
        bottom_right_x, bottom_right_y = position
        
        for point in self.points.values():
            if point.pos[0] > bottom_right_x:
                bottom_right_x = point.pos[0]
            
            if point.pos[1] > bottom_right_y:
                bottom_right_y = point.pos[1]
        
        self.height = bottom_right_y - position[1]
        self.width = bottom_right_x - position[0]
    
    def set_frame_point_pos(self, deltas):
        """Sets the position of each point with respect to the reference point"""
        current_position = (self.position[0],self.position[1])
        
        for point_name, pos_delta in deltas.iteritems():
            self.points[point_name].pos = (self.position[0] + pos_delta[0], \
                                           self.position[1] + pos_delta[1])
        
        self.move_model(current_position)
    
    def set_point_position(self, deltas):
        """Incerements the position of each point by point specific deltas"""
        
        for point_name, pos_delta in deltas.iteritems():
            point_position = self.points[point_name].pos
            self.points[point_name].pos = (point_position[0] + deltas[point_name][0], \
                                           point_position[1] + deltas[point_name][1])
        
        self.position = self.get_reference_position()
        self.set_dimensions()
    
    def set_point_position_in_place(self, deltas):
        """Incerements the position of each point by point specific deltas without 
        changing the reference point"""
        
        current_position = (self.position[0],self.position[1])
        
        for point_name, pos_delta in deltas.iteritems():
            point_position = self.points[point_name].pos
            self.points[point_name].pos = (point_position[0] + deltas[point_name][0], \
                                           point_position[1] + deltas[point_name][1])
        
        self.move_model(current_position)
    
    def move_model(self, new_position):
        """moves model to the new reference position"""
        position = self.get_reference_position()
        pos_delta = (new_position[0] - position[0], \
                     new_position[1] - position[1])
        
        for point in self.points.values():
            current_position = (point.pos[0], point.pos[1])
            point.pos = (current_position[0] + pos_delta[0], \
                         current_position[1] + pos_delta[1])
        
        self.position = self.get_reference_position()
        self.set_dimensions()
    
    def shift(self, deltas):
        position = self.position
        self.position = (position[0] + deltas[0], \
                         position[1] + deltas[1])
        
        for point in self.points.values():
            current_pos = point.pos
            point.pos = (current_pos[0] + deltas[0], \
                         current_pos[1] + deltas[1])
        
        self.set_dimensions()
    
    def pull_point(self, 
                  point,
                  new_pos,
                  start_point,
                  anchor_points,
                  point_to_lines,
                  pulled_lines = None,
                  pulled_anchors = None):
        """pulls all points connected to the selected point through lines
        
        point_to_lines: list of lines that have already been pulled"""
        
        if pulled_lines == None:
            pulled_lines = []
        
        if pulled_anchors == None:
            pulled_anchors = []
        
        pulled_points = []
        
        point.pos = new_pos
        
        #anchors points pull first
        for line in point_to_lines[point.name]:
            if not (line in pulled_lines):
                for anchor_point in anchor_points:
                    if anchor_point == line.other_named_end_point(point):
                        if ((point in anchor_points) and
                            (point == start_point)):
                            line.pull(anchor_point)
                            pulled_lines.append(line)
                        elif not (anchor_point in pulled_anchors):
                            pulled_anchors.append(anchor_point)
                            pulled_lines.append(line)
                            reverse_point_to_lines = build_point_to_lines(pulled_lines)
                            self.pull_point(anchor_point,
                                           anchor_point.pos,
                                           start_point,
                                           anchor_points,
                                           reverse_point_to_lines,
                                           [],
                                           pulled_anchors)
        
        for line in point_to_lines[point.name]:
            if not (line in pulled_lines):
                other_end_point = line.other_named_end_point(point)
                line.pull(point)
                pulled_points.append(other_end_point)
                pulled_lines.append(line)
        
        for pulled_point in pulled_points:
            self.pull_point(pulled_point,
                           pulled_point.pos,
                           start_point,
                           anchor_points,
                           point_to_lines,
                           pulled_lines,
                           pulled_anchors)

    def build_point_to_lines(self, lines):
        """builds a dictionary that maps points to each line it belongs to
        
        lines: the lines to buld the dictionary from"""
        
        point_to_lines = {}
        
        for line in lines:
            for point in line.points:
                if point.name in point_to_lines.keys():
                    point_to_lines[point.name].append(line)
                else:
                    point_lines = []
                    point_lines.append(line)
                    point_to_lines[point.name] = point_lines
        
        return point_to_lines

class ModelCollision():
    HITBOX_SIDE_LENGTH = 7
    
    def __init__(self, player1, player2):
        player_to_hitbox = dict([(player1, []), (player2, [])])
        hitbox_to_player = {}
        hitbox_to_line = {}
        
        self.add_player_hitboxes_to_dictionaries(player1)
        self.add_player_hitboxes_to_dictionaries(player2)
    
    def add_player_hitboxes_to_dictionaries(self, player):
        """populates the hitbox dictinoaries of a playerplayercollision.  This does NOT
        included the colliding rects."""
        for name, line in player.model.lines.iteritems():
            if name == stick.LineNames.HEAD:
                hitbox = get_circle_hitbox(line)
                
                self.hitbox_to_player[hitbox] = player
                self.hitbox_to_line[hitbox] = name
                self.player_to_hitbox[player].append[hitbox]
            else:
                hitboxes = get_line_hitboxes(line)
                
                for hitbox in hitboxes:
                    self.hitbox_to_player[hitbox] = player
                    self.hitbox_to_line[hitbox] = name
                    self.player_to_hitbox[player].append[hitbox]
    
    def get_circle_hitbox(circle):
        """returns the smallest rect that encloses the circle"""
        circle.set_length()
        radius = int(circle.length / 2)
        hitbox = pygame.Rect((circle.center()[0] - radius,
                              circle.center()[1] - radius),
                             (circle.length, circle.length))
        
        return hitbox

    def get_line_hitboxes(line):
        """returns a list of rects that lie on the given line."""
        line_rects = []
        
        line.set_length()
        box_count = line.length / (HITBOX_SIDE_LENGTH/2)
        
        if box_count > 0:
            for pos in get_hitbox_positions(box_count, line):
                line_rects.append(pygame.Rect(pos, (HITBOX_SIDE_LENGTH,HITBOX_SIDE_LENGTH)))
        else:
            line_rects.append(pygame.Rect(line.endPoint1.pos, (HITBOX_SIDE_LENGTH,HITBOX_SIDE_LENGTH)))
        
        return line_rects

    def get_hitbox_positions(box_count, line):
            """gets top left of each hitbox on a line.
            
            box_count: the number of hit boxes"""
            hitbox_positions = []
            
            start_pos = line.endPoint1.pixel_pos()
            end_pos = line.endPoint2.pixel_pos()
            
            x_delta = end_pos[0] - start_pos[0]
            y_delta = end_pos[1] - start_pos[1]
            
            length = line.length
            length_to_hit_box_center = 0
            increment = line.length / box_count
            
            hitbox_positions.append((int(end_pos[0] - (HITBOX_SIDE_LENGTH / 2)), 
                                     int(end_pos[1] - (HITBOX_SIDE_LENGTH / 2))))
            
            length_to_hit_box_center += increment
            x_pos = (start_pos[0] + 
                     x_delta - 
                     ((x_delta / length) * length_to_hit_box_center))
            y_pos = (start_pos[1] + 
                     y_delta - 
                     ((y_delta / length) * length_to_hit_box_center))
            box_center = (x_pos, y_pos)
            
            for i in range(int(box_count)):
                hitbox_positions.append((int(box_center[0] - (HITBOX_SIDE_LENGTH / 2)), 
                                         int(box_center[1] - (HITBOX_SIDE_LENGTH / 2))))
                
                length_to_hit_box_center += increment
                x_pos = (start_pos[0] + 
                         x_delta - 
                         ((x_delta / length) * length_to_hit_box_center))
                y_pos = (start_pos[1] + 
                         y_delta - 
                         ((y_delta / length) * length_to_hit_box_center))
                box_center = (x_pos, y_pos)
            
            hitbox_positions.append((int(start_pos[0] - (HITBOX_SIDE_LENGTH / 2)), 
                                     int(start_pos[1] - (HITBOX_SIDE_LENGTH / 2))))
            
            return hitbox_positions
