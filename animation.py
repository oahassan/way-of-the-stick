import copy

import pygame

import stick
import mathfuncs
import math

class Frame:
    """contains the data in an animation frame"""
    
    def __init__(self):
        """creates a new frame"""
        self.point_dictionary = {}
        self.line_dictionary = {}
        self.circle_dictionary = {}
        self.point_to_lines = {}
        self.point_to_circles = {}
        self.reference_pos = None
    
    def clear(self):
        """removes all points, lines, and circles from a frame"""
        self.point_dictionary = {}
        self.line_dictionary = {}
        self.circle_dictionary = {}
        self.point_to_lines = {}
        self.point_to_circles = {}
        self.reference_pos = None
    
    def points(self):
        """Returns all the points in the point dictionary"""
        return self.point_dictionary.values()
    
    def lines(self):
        """Returns all the lines in the point dictionary"""
        return self.line_dictionary.values()
    
    def circles(self):
        """Returns all the circles in the point dictionary"""
        return self.circle_dictionary.values()
    
    def draw(self, \
            surface, \
            color = None, \
            scale = 1, \
            pos_delta = None, \
            point_radius = -1, \
            line_thickness = -1):
        """draws all the points, lines and circles in a frame"""
        
        current_image_pos = None
        
        if scale != 1:
            current_image_pos = self.get_reference_position()
        
        for line in self.lines():
            line.draw(surface, \
                     color, \
                     line_thickness, \
                     pos_delta, \
                     current_image_pos, \
                     scale)
            
        for circle in self.circles():
            circle.draw(surface, \
                        color, \
                        line_thickness, \
                        pos_delta, \
                        current_image_pos, \
                        scale)
            
        for point in self.points():
            point.draw(surface, \
                      color, \
                      point_radius, \
                      pos_delta, \
                      current_image_pos, \
                      scale)
    
    def add_point(self, point):
        """Adds a new point to a frame
        
        point: the point to add"""
        self.point_dictionary[point.id] = point
    
    def add_line(self, line):
        """Adds a new line to a frame
        
        line: the line to add"""
        self.line_dictionary[line.id] = line
        
        if (line.endPoint1.id in self.point_dictionary.keys()) == False:
            self.add_point(line.endPoint1)
        
        self.add_point_to_lines_entry(line.endPoint1, line)
        
        if (line.endPoint2.id in self.point_dictionary.keys()) == False:
            self.add_point(line.endPoint2)
        
        self.add_point_to_lines_entry(line.endPoint2, line)
    
    def add_point_to_lines_entry(self, point, line):
        if point.id in self.point_to_lines.keys():
            if not (line in self.point_to_lines[point.id]):
                self.point_to_lines[point.id].append(line)
        else:
            self.point_to_lines[point.id] = []
            self.point_to_lines[point.id].append(line)
    
    def add_circle(self, circle):
        """Adds a new circle to a frame
        
        circle: the circle to add"""
        self.circle_dictionary[circle.id] = circle
        
        if (circle.endPoint1.id in self.point_dictionary.keys()) == False:
            self.add_point(circle.endPoint1)
        
        self.add_point_to_circles_entry(circle.endPoint1, circle)
        
        if (circle.endPoint2.id in self.point_dictionary.keys()) == False:
            self.add_point(circle.endPoint2)
        
        self.add_point_to_circles_entry(circle.endPoint2, circle)
    
    def add_point_to_circles_entry(self, point, circle):
        if point.id in self.point_to_circles.keys():
            if not (circle in self.point_to_circles[point.id]):
                self.point_to_circles[point.id].append(circle)
        else:
            self.point_to_circles[point.id] = []
            self.point_to_circles[point.id].append(circle)
    
    def remove_point(self, point):
        del self.point_dictionary[point.id]
        
        self.remove_lines(point)
        
        self.remove_circles(point)
    
    def remove_lines(self, point):
        if point.id in self.point_to_lines.keys():
            for line in self.point_to_lines[point.id]:
                del self.line_dictionary[line.id]
                
                if line.endPoint1.id == point.id:
                    self.point_to_lines[line.endPoint2.id].remove(line)
                else:
                    self.point_to_lines[line.endPoint1.id].remove(line)
                
            del self.point_to_lines[point.id]

    def remove_circles(self, point):
        if point.id in self.point_to_circles.keys():
            for circle in self.point_to_circles[point.id]:
                del self.circle_dictionary[circle.id]
                
                if circle.endPoint1.id == point.id:
                    self.point_to_circles[circle.endPoint2.id].remove(circle)
                else:
                    self.point_to_circles[circle.endPoint1.id].remove(circle)
                
            del self.point_to_circles[point.id]
    
    def move(self, pos_delta):
        """draws the frame image with the top left corner of the image at the
        given position
        
        pos_delta: the change in position of the point"""
        
        for point in self.points():
            position = point.pos
            new_x = position[0] + pos_delta[0]
            new_y = position[1] + pos_delta[1]
            point.pos = (new_x, new_y)
    
    def scale(self, scale):
        """scales the lines in a frame by the given ratio
        
        scale: floating number to multiply the size of the frame by"""
        reference_position = self.get_reference_position()
        pos_delta_dictionary = self.build_pos_delta_dictionary(reference_position)
        
        for point in self.points():
            new_x = reference_position[0] + \
                    (scale * pos_delta_dictionary[point.id][0])
            new_y = reference_position[1] + \
                    (scale * pos_delta_dictionary[point.id][1])
            point.pos = (new_x, new_y)
        
    def get_reference_position(self):
        """Calculates the position of the top left corner of a rectangle
        enclosing the image in a frame"""
        min_x_pos = 99999999
        min_y_pos = 99999999
        
        for line in self.lines():
            reference_position = line.get_reference_position()
            
            if reference_position[0] < min_x_pos:
                min_x_pos = reference_position[0]
            
            if reference_position[1] < min_y_pos:
                min_y_pos = reference_position[1]
        
        for circle in self.circles():
            reference_position = circle.get_reference_position()
            
            if reference_position[0] < min_x_pos:
                min_x_pos = reference_position[0]
            
            if reference_position[1] < min_y_pos:
                min_y_pos = reference_position[1]
        
        return (min_x_pos, min_y_pos)
    
    def build_pos_delta_dictionary(self, reference_position):
        """builds a dictionary of the x and y displacement of each point to 
        the reference position
        
        reference_position: the position to build a refrence to"""
        
        distance_to_reference_position = {}
        
        for point in self.points():
            x_delta = point.pos[0] - reference_position[0]
            y_delta = point.pos[1] - reference_position[1]
            
            distance_to_reference_position[point.id] = (x_delta, y_delta)
        
        return distance_to_reference_position
    
    def get_top_left_and_bottom_right(self):
        """Finds the top left and bottom right containers of a rectangle containg the
        points and lines of the frame"""
        top_left_x = None
        top_left_y = None
        bottom_right_x = None
        bottom_right_y = None
        
        for line in self.lines():
            top_left_and_bottom_right = line.get_top_left_and_bottom_right()
            
            if top_left_x == None:
                top_left_x = top_left_and_bottom_right[0][0]
                top_left_y = top_left_and_bottom_right[0][1]
                bottom_right_x = top_left_and_bottom_right[1][0]
                bottom_right_y = top_left_and_bottom_right[1][1]
            else:
                top_left_x = min(top_left_x,top_left_and_bottom_right[0][0])
                top_left_y = min(top_left_y,top_left_and_bottom_right[0][1])
                bottom_right_x = max(bottom_right_x,top_left_and_bottom_right[1][0])
                bottom_right_y = max(bottom_right_y,top_left_and_bottom_right[1][1])
        
        for circle in self.circles():
            top_left_and_bottom_right = circle.get_top_left_and_bottom_right()
            
            top_left_x = min(top_left_x,top_left_and_bottom_right[0][0])
            top_left_y = min(top_left_y,top_left_and_bottom_right[0][1])
            bottom_right_x = max(bottom_right_x,top_left_and_bottom_right[1][0])
            bottom_right_y = max(bottom_right_y,top_left_and_bottom_right[1][1])
        
        return ((top_left_x, top_left_y), \
                (bottom_right_x, bottom_right_y))
    
    def image_height(self):
        """calculates the height of the image in a frame"""
        top_left_and_bottom_right = self.get_top_left_and_bottom_right()
        
        return top_left_and_bottom_right[1][1] - top_left_and_bottom_right[0][1]
        
    def image_width(self):
        """calculates the width of the image in a frame"""
        top_left_and_bottom_right = self.get_top_left_and_bottom_right()
        
        return top_left_and_bottom_right[1][0] - top_left_and_bottom_right[0][0]
    
    def flip(self):
        """flips a frame over its x_axis"""
        
        max_x_pos = 0
        min_x_pos = 99999999
        
        for point in self.points():
            if point.pos[0] > max_x_pos:
                max_x_pos = point.pos[0]
            
            if point.pos[0] < min_x_pos:
                min_x_pos = point.pos[0]
        
        mid_x_pos = min_x_pos + ((max_x_pos - min_x_pos) / 2)
        
        for point in self.points():
            delta = point.pos[0] - mid_x_pos
            point.pos = (mid_x_pos - delta, point.pos[1])
    
class Animation:
    """contains the data for a stick animation"""
    _ThumbnailHeight = 50
    _ThumbnailPadding = 30
    _ThumbnailLineThickness = 1
    _ThumbnailPointRadius = 2
    _ThumbnailColor = (255,255,255)
    _ActiveThumbnailColor = (0,0,255)
    _PrevFrameColor = (50,50,50)
    
    def __init__(self):
        """creates a new animation"""
        self.frames = []
        self.frames.append(Frame())
        self.frame_index = 0
        self.name = ""
        self.point_names = {}
        self.frame_deltas = []
        self.animation_deltas = []
        self.frame_times = []
        self.frame_start_times = []
        self.frame_reference_point_initial_velocities = []
        self.frame_point_initial_velocities = []
        self.frame_point_final_velocities = []
        self.frame_point_accelerations = []
        self.animation_length = 0
    
    def draw_frame(self, surface):
        """draws the current frame and sets the next frame
        
        surface: the surface to draw the frame onto."""
        frame_index = self.frame_index
        
        if frame_index > 0:
            self.frames[frame_index - 1].draw(surface, \
                                             Animation._PrevFrameColor)
        
        self.frames[self.frame_index].draw(surface)
    
    def add_frame(self, frame):
        """adds the current frame to the animation and increments the frame
        index
        
        frame: the frame to add to the animation"""
        
        if self.frame_index == len(self.frames) - 1:
            self.frames.append(frame)
        else:
            self.frames.insert(self.frame_index + 1, frame)
        
        self.frame_index += 1
    
    def remove_frame(self, frame):
        """adds the current frame to the animation and increments the frame
        index
        
        frame: the frame to add to the animation"""
        if len(self.frames) > 1:
            self.frames.remove(frame)
        
        if self.frame_index == len(self.frames):
            self.frame_index -= 1
        
    def draw_frames(self, surface, pos):
        """draws the frames of an animation in sequence
        
        surface: the surface to draw the frames on
        pos: the top left corner to draw the first frame"""
        
        frame_pos = pos
        start_index = max(0, self.frame_index - 2)
        end_index = min(len(self.frames), self.frame_index + 3)
        
        for i in range(start_index, end_index):
            frame = self.frames[i]
            
            color = Animation._ThumbnailColor
            
            if i == self.frame_index:
                color = Animation._ActiveThumbnailColor
            
            image_height = frame.image_height()
            
            scale = 0
            
            if image_height < Animation._ThumbnailHeight:
                scale = 1
            else:
                scale = Animation._ThumbnailHeight / image_height
            
            reference_pos = frame.get_reference_position()
            
            pos_delta = (frame_pos[0] - reference_pos[0], \
                        frame_pos[1] - reference_pos[1])
            
            if scale > 0:
                frame.draw(surface, \
                          color, \
                          scale, \
                          pos_delta, \
                          Animation._ThumbnailPointRadius, \
                          Animation._ThumbnailLineThickness)
            
            next_x_pos = frame_pos[0] + \
                         (scale * frame.image_width()) + \
                         Animation._ThumbnailPadding
            
            frame_pos = (next_x_pos, frame_pos[1])
    
    def get_widest_frame(self):
        widest_frame = self.frames[0]
        
        for frame in self.frames:
            if frame.image_width() > widest_frame.image_width():
                widest_frame = frame
        
        return widest_frame
        
    def get_tallest_frame(self):
        tallest_frame = self.frames[0]
        
        for frame in self.frames:
            if frame.image_height() > tallest_frame.image_height():
                tallest_frame = frame
                
        return tallest_frame
    
    def get_middle_frame(self):
        """returns a frame from the middle of the animation"""
        middle_frame_index = (len(self.frames) / 2)
        
        return self.frames[middle_frame_index]
    
    def flip(self):
        """returns a new animation flipped over the y_axis"""
        for frame in self.frames:
            frame.reference_pos = frame.get_reference_position()
        
        rtn_animation = copy.deepcopy(self)
        frame_deltas = rtn_animation.bld_animation_delta_dctnry()
        reference_pos = self.frames[0].get_reference_position()
        
        for i in range(len(rtn_animation.frames)):
            new_frame = rtn_animation.frames[i]
            point_deltas = frame_deltas[i]
            
            for point in new_frame.points():
                point.pos = (reference_pos[0] - point_deltas[point.id][0], \
                            reference_pos[1] + point_deltas[point.id][1])
        
        return rtn_animation
        
    def bld_animation_delta_dctnry(self):
        """returns a dictionary of the change in position of each point
        between each frame"""
        
        frame_deltas = {}
        reference_pos = self.frames[0].get_reference_position()
        
        for i in range(len(self.frames)):
            frame = self.frames[i]
            start_to_frame_deltas = frame.build_pos_delta_dictionary(reference_pos)
            
            frame_deltas[i] = start_to_frame_deltas
        
        return frame_deltas
    
    def bld_frame_to_frame_deltas(self):
        """returns a dictionary of the change in position of each point
        between each frame"""
        
        frame_deltas = {}
        reference_pos = self.frames[0].get_reference_position()
        
        for i in range(len(self.frames)):
            frame = self.frames[i]
            prev_frame = frame
            
            if i != 0:
                prev_frame = self.frames[i - 1]
            
            frame_to_frame_deltas = self.bld_frame_to_frame_deltas_dctnry(frame, prev_frame)
            
            frame_deltas[i] = frame_to_frame_deltas
        
        return frame_deltas
    
    def bld_frame_to_frame_deltas_dctnry(self, frame, prev_frame):
        frame_deltas = {}
        
        for point_id, point in frame.point_dictionary.iteritems():
            prev_frame_position = prev_frame.point_dictionary[point_id].pos
            delta = (point.pos[0] - prev_frame_position[0], \
                     point.pos[1] - prev_frame_position[1])
            
            frame_deltas[point_id] = delta
        
        return frame_deltas
    
    def set_animation_height(self, height, reference_height):
        """scales each frame to the given height"""
        
        relative_heights = {}
        
        for i in range(len(self.frames)):
            frame = self.frames[i]
            
            relative_heights[i] = frame.image_height() / reference_height
        
        for i in range(len(self.frames)):
            frame = self.frames[i]
            scale = 1
            relative_height = height * relative_heights[i]
            
            if frame.image_height() > relative_height:
                scale = relative_height / frame.image_height()
                frame.scale(scale)
    
    def set_frame_positions(self, reference_pos):
        """sets the position of each frame with respect to the reference
        position"""
        first_frame = self.frames[0]
        first_frame_pos = first_frame.get_reference_position()
        frame_delta = (reference_pos[0] - first_frame_pos[0], \
                       reference_pos[1] - first_frame_pos[1])
        
        for frame in self.frames:
            frame.move(frame_delta)
    
    def set_frame_deltas(self):
        """populates the dictionary of distances between a frames reference position and
        the position of each point keyed by the point names"""
        for frame in self.frames:
            frame_deltas = {}
            reference_pos = frame.get_reference_position()
            id_delta_dctnry = frame.build_pos_delta_dictionary(reference_pos)
            
            for name, id in self.point_names.iteritems():
                frame_deltas[name] = id_delta_dctnry[id]
            
            self.frame_deltas.append(frame_deltas)
    
    def set_animation_deltas(self):
        """populates the dictionary of distances between the position of the points in
        each frame and the reference position of the first frame"""
        id_delta_dictionaires = self.bld_frame_to_frame_deltas()
        
        for frame_index, dictionary in id_delta_dictionaires.iteritems():
            frame_deltas = {}
            
            for name, id in self.point_names.iteritems():
                frame_deltas[name] = dictionary[id]
            
            self.animation_deltas.append(frame_deltas)
    
    def get_point_id_by_name(self, point_id):
        """returns the name of a point with the given id"""
        
        return_name = None
        
        for name, named_point_id in self.point_names.iteritems():
            if point_id == named_point_id:
                return_name = name
                break
        
        return return_name
    
    def get_frame_index_at_time(self, duration):
        rtn_index = 0
        
        for frame_index in range(len(self.frames)):
            if self.frame_start_times[frame_index] > duration:
                break
            else:
                rtn_index = frame_index
        
        return rtn_index
    
    #Get point position change given time
    def build_point_time_delta_dictionary(self, start_time, end_time):
        point_deltas = {}
        
        # if end_time >= self.frame_start_times[len(self.frames) - 1]:
            # import pdb; pdb.set_trace()
        
        for point_name, point_id in self.point_names.iteritems():
            point_deltas[point_name] = self.get_point_deltas(point_id, \
                                                             start_time, \
                                                             end_time)
        
        return point_deltas
    
    def get_point_deltas(self, point_id, start_time, end_time):
        """returns the displacement of a point given the start time of the movement and
        the end time of the movement.  Time resets to 0 at start of animation and 
        increments in milliseconds.
        
        point_id: id of the point to return deltas for"""
        start_frame_index = self.get_frame_index_at_time(start_time)
        end_frame_index = self.get_frame_index_at_time(end_time)
        
        x_displacement = 0
        y_displacement = 0
        
        for frame_index in range(start_frame_index, end_frame_index + 1):
            displacement_start_time = self.frame_start_times[frame_index]
            displacement_end_time = displacement_start_time + self.frame_times[frame_index]
            
            if frame_index == start_frame_index:
                displacement_start_time = start_time
                start_time_difference = start_time - self.frame_start_times[frame_index]
                displacement_end_time = displacement_start_time + self.frame_times[frame_index] - start_time_difference
            
            if frame_index == end_frame_index:
                displacement_end_time = end_time
            
            displacement = self.calculate_point_displacement(frame_index, \
                                                             point_id, \
                                                             displacement_start_time, \
                                                             displacement_end_time)
            x_displacement += displacement[0]
            y_displacement += displacement[1]
        
        return (x_displacement,y_displacement)
    
    def calculate_point_displacement(self, frame_index, point_id, start_time, end_time):
        """Determines the displacement of a point between two frames given the start time
        of the movement and the end time of the movement.  The two times should fall
        within the start of the frame with the given frame index and the next.
        
        frame_index: the index of the starting fame
        point_id: the point that's moving
        start_time: the start time of the displacement
        end_time: the end time of the displacement"""
        
        frame_start_time = self.frame_start_times[frame_index]
        used_frame_time = start_time - frame_start_time
        
        
        
        acceleration = self.frame_point_accelerations[frame_index][point_id]
        frame_initial_velocity = self.frame_point_initial_velocities[frame_index][point_id]
        
        # if self.point_names[stick.PointNames.RIGHT_FOOT] == point_id:
            # print([acceleration,frame_initial_velocity])
        
        strat_time_velocity = (self.calculate_velocity(acceleration[0], \
                                                       frame_initial_velocity[0], \
                                                       used_frame_time), \
                               self.calculate_velocity(acceleration[1], \
                                                       frame_initial_velocity[1], \
                                                       used_frame_time))
        
        duration = end_time - start_time
        
        x_displacement = self.calculate_displacement(acceleration[0], \
                                                     strat_time_velocity[0], \
                                                     duration)
        y_displacement = self.calculate_displacement(acceleration[1], \
                                                     strat_time_velocity[1], \
                                                     duration)
        
        return (x_displacement, y_displacement)
    
    def calculate_velocity(self, acceleration, initial_velocity, duration):
        """calculates the final velocity of an object given it's acceleration, initial
        velocity and the duration in milliseconds.
        
        acceleration: the constant acceleration of the object in pixels per millisecond squared
        initial_velocity: the constant velocity of the object in pixels per millisecond
        duration: the time in which the velocity is changing"""
        
        return acceleration*duration + initial_velocity
    
    def calculate_displacement(self, acceleration, initial_velocity, duration):
        """calculates displacement given acceleration, initial velocity and duration the
        duration of the displacement in milliseconds.
        
        acceleration: the constant acceleration of the displaced object
        initial_velocity: the initial velocity of the displaced object
        duration: the time over which the object is displaced"""
        
        return (.5*acceleration*(duration**2)) + initial_velocity*duration
    
    #Create Reference Point Travel Data
    def set_animation_reference_point_path_data(self, acceleration, gravity):
        """populates tables that determine the reference position of the animation at a
        given point in time.  These tables contain the x and y velocity of the reference 
        point at the start of each frame.  The x velocity is calculated by dividing the
        x displacement by the frame time calculated by set_animation_point_path_data.
        The y velocity is calculated by inferring when the figure is jumping and how
        long that jump takes given gravity.
        
        acceleration: maximum acceleration allowed in pixels per millisecond
        gravity: constant acceleration of gravity"""
        pass
        #Get y velocities
        #Get x velocities
    
    def get_frame_reference_point_x_velocities(self, acceleration, frame_index):
        """Gets the x velocity of the reference point at the start of each frame.  The x
        velocity is calculated by dividing the x displacement by the frame time 
        calculated by set_animation_point_path_data.
        
        acceleration: maximum acceleration allowed in pixels per millisecond
        frame_index: the index of the current frame"""
        #For each frame
        #Calculate x displacement between the two frames
        #Calculate the final velocity and save it as the initial velocity of the next frame
    
    def get_reference_point_y_velocities(self, gravity):
        """Gets y velocity of the reference point at the start of each frame.  The y 
        velocity is calculated by inferring when the figure is jumping and how long that
        jump takes given gravity.
        
        gravity: constant acceleration of gravity"""
        pass
        #Get jump intervals
        #Get jump interval initial velocities
        #save jump interval initial velocities
    
    def get_jump_frame_intervals(self, gravity):
        """returns a list of tuples for the starting and ending frames of jumps in an
        animation.
        
        gravity: constant acceleration of gravity in pixels per millisecond"""
        pass
        #Every jump start is paired with a jump end
        #if figure is grounded in the current frame and airborne in the next frame then 
        #   the current frame is the start of a jump
        #if figure is grounded in the current frame and was airborne in the previous frame
        #   set the current frame as end of a jump
        #if the current frame is the last frame and the figure is airborne then the current
        #   frame is the end of the jump
    
    def figure_is_airborne(self, frame_index):
        """returns whether the figure is grounded in the given frame index.  The first
        frame is used as a reference for where the ground is."""
        pass
        #if this frame's bottom is above the first frame's bottom the figure is airborne.
    
    def get_jump_interval_velocity(self, gravity, start_frame_index, end_frame_index):
        """returns the duration in milliseconds of each jump interval
        
        gravity: constant acceleration of gravity in pixels per millisecond"""
        pass
        #Find how high the figure jumps
        #calculate the initial velocity given the displacement, a final velocity of 0 and
        #an acceleration of the given gravity.
    
    def get_jump_height(self, start_frame_index, end_frame_index):
        """returns the height of the jump between two frame indices"""
        pass
        #subtract the height frames y position from the starting frame's y position
    
    #Create Point Travel Data
    def set_animation_point_path_data(self, acceleration):
        """populates tables that determine the position of each point at a given point of 
        time.
        
        acceleration: maximum acceleration allowed in pixels per millisecond"""
        
        self.init_frame_point_path_dictionaries()
        
        for frame_index in range(len(self.frames) - 1):
            self.set_frame_point_path_data(frame_index,acceleration)
            self.animation_length += self.frame_times[frame_index]
        
        self.add_final_frame_path_data()
    
    def add_final_frame_path_data(self):
        point_velocities = {}
        point_accelerations = {}
        
        self.frame_times.append(10)
        self.animation_length += 10
        
        frame_index = len(self.frames) - 1
        for point in self.frames[frame_index].points():
            point_velocities[point.id] = (0,0)
            point_accelerations[point.id] = (0,0)
        
        self.frame_point_initial_velocities.append(point_velocities)
        self.frame_point_accelerations.append(point_accelerations)
    
    def init_frame_point_path_dictionaries(self):
        self.frame_times = []
        self.frame_start_times = [0,]
        self.frame_point_initial_velocities = []
        self.frame_point_final_velocities = []
        self.frame_point_accelerations = []
        self.animation_length = 0
        
        point_velocities_dictionary = {}
        
        for point in self.frames[0].points():
            point_velocities_dictionary[point.id] = (0,0)
        
        self.frame_point_initial_velocities.append(point_velocities_dictionary)
    
    def set_frame_point_path_data(self, frame_index, acceleration):
        """builds a dictionary of path functions that give the position of each point at
        a given time  between the given frame index and the next.
        
        frame_index: the index of starting frame
        acceleration: maximum acceleration allowed in pixels per millisecond"""
        
        max_delta_point_id = self.get_max_delta_point_id(frame_index)
        acceleration = self.get_acceleration_components(frame_index, max_delta_point_id,acceleration)
        initial_velocity = self.get_velocity_components(frame_index, max_delta_point_id)
        displacement = self.get_point_displacement(frame_index, max_delta_point_id)
        
        #update initial velocity for displacements of 0
        if displacement[0] == 0:
            x_initial_velocity = 0
        else:
            x_initial_velocity = initial_velocity[0]
        
        if displacement[1] == 0:
            y_initial_velocity = 0
        else:
            y_initial_velocity = initial_velocity[1]
        
        initial_velocity = (x_initial_velocity, y_initial_velocity)
        
        duration = self.get_constant_acceleration_frame_to_frame_duration(frame_index, \
                                                                          max_delta_point_id, \
                                                                          displacement, \
                                                                          initial_velocity, \
                                                                          acceleration)
        
        if duration <= 0:
            duration = self.get_constant_velocity_frame_to_frame_duration(displacement, \
                                                                          initial_velocity)
            self.update_frame_point_path_data(duration, frame_index)
        else:
            self.update_frame_point_path_data(duration, frame_index)
    
    def update_frame_point_path_data(self, duration, frame_index):
        self.frame_times.append(duration)
        
        previous_frame_start_time = self.frame_start_times[frame_index]
        self.frame_start_times.append(previous_frame_start_time + duration)
        
        point_initial_velocity_dictionary = {}
        point_final_velocity_dictionary = {}
        point_acceleration_dictionary = {}
        
        for point in self.frames[frame_index].points():
            displacement = self.get_point_displacement(frame_index, point.id)
            initial_velocity = self.get_velocity_components(frame_index, point.id)
            
            #update initial velocity for displacements of 0
            if displacement[0] == 0:
                x_initial_velocity = 0
            else:
                x_initial_velocity = initial_velocity[0]
            
            if displacement[1] == 0:
                y_initial_velocity = 0
            else:
                y_initial_velocity = initial_velocity[1]
            
            initial_velocity = (x_initial_velocity, y_initial_velocity)
            self.frame_point_initial_velocities[frame_index][point.id] = initial_velocity
            
            #get acceleration components and velocity components
            acceleration = self.calculate_acceleration_components(duration, \
                                                                  displacement, \
                                                                  initial_velocity)
            point_acceleration_dictionary[point.id] = acceleration
            
            final_velocity = self.calculate_final_velocity_components(duration, \
                                                                      initial_velocity, \
                                                                      acceleration)
            point_initial_velocity_dictionary[point.id] = final_velocity
            point_final_velocity_dictionary[point.id] = final_velocity
        
        self.frame_point_initial_velocities.append(point_initial_velocity_dictionary)
        self.frame_point_final_velocities.append(point_final_velocity_dictionary)
        self.frame_point_accelerations.append(point_acceleration_dictionary)
    
    def calculate_acceleration_components(self, duration, displacement, initial_velocity):
        """calculates the x and y acceleration of a point given its displacement, initial
        velocity and the time between frames
        
        duration: the time between two frames
        displacement: the x and y displacement of a point between two frames
        initial_velocity: the x and y velocity of a point at the starting frame"""
        
        x_acceleration = float(2*(displacement[0] - (initial_velocity[0]*duration))) / (duration**2)
        y_acceleration = float(2*(displacement[1] - (initial_velocity[1]*duration))) / (duration**2)
        
        return (x_acceleration, y_acceleration)
    
    def calculate_final_velocity_components(self, duration, initial_velocity, acceleration):
        """calculates the final velocity components of a point given its initial velocity,
        it's acceleration and the time between to frames
        
        duration: time between two frames in milliseconds
        displacement: displacement of the point
        initial_velocity: the x and y components of a point at the start of a frame in
                          pixels per millisecond
        acceleration: the x and y components of the acceleration of a point within a frame
                      in pixels per millisecond squared"""
        
        x_velocity = initial_velocity[0] + (acceleration[0]*duration)
        y_velocity = initial_velocity[1] + (acceleration[1]*duration)
        
        return (x_velocity, y_velocity)
    
    def get_acceleration_components(self, frame_index, point_id, acceleration):
        """returns the x and y components of the acceleration of a point between two
        frames.
        
        frame_index: the starting frame index
        point_id: the id of the point
        acceleration: the resulting acceleration"""
        
        x_component = self.get_point_cos(frame_index, point_id) * acceleration
        y_component = self.get_point_sin(frame_index, point_id) * acceleration
        
        return (x_component, y_component)
    
    def get_point_sin(self, frame_index, point_id):
        """returns the sin of the angle between the two positions of a point in the
        given frame index and the next.
        
        frame_index: the starting frame index
        point_id: the id of the point"""
        
        frame_point_position = self.frames[frame_index].point_dictionary[point_id].pos
        next_frame_point_position = self.frames[frame_index + 1].point_dictionary[point_id].pos
        
        distance = mathfuncs.distance(frame_point_position, next_frame_point_position)
        y_delta = next_frame_point_position[1] - frame_point_position[1]
        
        sin = 0
        
        if distance > 0:
            sin = float(y_delta) / distance
        
        return sin
    
    def get_point_cos(self, frame_index, point_id):
        """returns the cos of the angle between the two positions of a point in the
        given frame index and the next.
        
        frame_index: the starting frame index
        point_id: the id of the point"""
        
        frame_point_position = self.frames[frame_index].point_dictionary[point_id].pos
        next_frame_point_position = self.frames[frame_index + 1].point_dictionary[point_id].pos
        
        distance = mathfuncs.distance(frame_point_position, next_frame_point_position)
        x_delta = next_frame_point_position[0] - frame_point_position[0]
        
        cos = 0
        
        if distance > 0:
            cos = float(x_delta) / distance
        
        return cos
    
    def get_point_displacement(self, frame_index, point_id):
        """returns the x and y displacement of a point between the given fame index and
        the next one.
        
        frame_index: the starting frame_index
        point_id: the id of the point"""
        
        frame_point_position = self.frames[frame_index].point_dictionary[point_id].pos
        next_frame_point_position = self.frames[frame_index + 1].point_dictionary[point_id].pos
        
        return (next_frame_point_position[0] - frame_point_position[0], \
                next_frame_point_position[1] - frame_point_position[1])
    
    def get_velocity_components(self, frame_index, point_id):
        """returns the x and y velocity components of a point between two frames.
        
        frame_index: the index of the starting frame
        point_id: the id of the point"""
        
        displacement = self.get_point_displacement(frame_index, point_id)
        
        velocity = self.frame_point_initial_velocities[frame_index][point_id]
        x_velocity = velocity[0]
        y_velocity = velocity[1]
        
        if ((mathfuncs.sign(displacement[0]) != mathfuncs.sign(velocity[0])) or
            (displacement[0] == 0)):
            x_velocity = 0
        
        if ((mathfuncs.sign(displacement[1]) != mathfuncs.sign(velocity[1])) or
            (displacement[1] == 0)):
            y_velocity = 0
        
        velocity = (x_velocity, y_velocity)
        
        return velocity
    
    def get_max_delta_point_id(self, frame_index):
        """returns the id of the point that travels the greatest distance between the
        given frame_index and the next.
        
        frame_index: the index of the starting frame"""
        
        frame_points = self.frames[frame_index].point_dictionary
        next_frame_points = self.frames[frame_index + 1].point_dictionary
        
        max_delta_point_id = frame_points.keys()[0]
        max_distance = mathfuncs.distance(frame_points[max_delta_point_id].pos, \
                                          next_frame_points[max_delta_point_id].pos)
        
        for point in frame_points.values():
            distance = mathfuncs.distance(point.pos, next_frame_points[point.id].pos)
            
            if distance > max_distance:
                max_delta_point_id = point.id
                max_distance = distance
        
        return max_delta_point_id
    
    def get_constant_acceleration_frame_to_frame_duration(self, \
                                                          frame_index, \
                                                          point_id, \
                                                          displacement, \
                                                          initial_velocity, \
                                                          acceleration):
        """returns how long it will take to travel a distance in milliseconds given the
        initial velocity, the acceleration and the displacement.
        
        frame_index: the index of the starting frame
        point_id: the point used to calculate the frame duration
        distance: x and y displacement in a tuple (x,y)
        initial_velocity: x and y initial_velocity in a tuple (x,y)
        acceleration: x and y constant acceleration in a tuple (x,y)"""
        
        duration = -1
        
        if acceleration[0] != 0:
            x_velocity_final = self.calculate_velocity_without_time(initial_velocity[0],acceleration[0],displacement[0])
            
            duration = float(x_velocity_final - initial_velocity[0]) / acceleration[0]
        else:
            if acceleration[1] != 0:
                y_velocity_final = self.calculate_velocity_without_time(initial_velocity[1],acceleration[1],displacement[1])
                
                duration = float(y_velocity_final - initial_velocity[1]) / acceleration[1]
        
        # x_velocity_final = min(32,math.sqrt(initial_velocity[0]**2 + ((2 * acceleration[0])*(displacement[0]))))
        
        # if displacement[0] < 0:
            # x_velocity_final = max(-32,x_velocity_final)
        
        # x_acceleration = ((x_velocity_final**2) - (initial_velocity[0]**2))/(2 * displacement[0])
        
        # if x_acceleration > 0:
            # duration = (float(x_velocity_final - initial_velocity[0]) / x_acceleration)
        # else:
            # y_velocity_final = min(32,math.sqrt(initial_velocity[1]**2 + ((2 * acceleration[1])*(displacement[1]))))
            
            # if displacement[1] < 0:
                # y_velocity_final = min(-32,y_velocity_final)
            
            # y_acceleration = ((y_velocity_final**2) - (initial_velocity[1]**2))/(2 * displacement[1])
            
            # if y_acceleration > 0:
                # duration = (float(y_velocity_final - initial_velocity[1]) / y_acceleration)
        
        # x_velocity_final = min(32,math.sqrt(initial_velocity[0]**2 + ((2 * acceleration[0])*(displacement[0]))))
        
        # if x_velocity_final == initial_velocity[0]:
            # y_velocity_final = min(32,math.sqrt(initial_velocity[1]**2 + ((2 * acceleration[1])*(displacement[1]))))
            
            # if y_velocity_final == initial_velocity[1]:
                # pass
            # else:
                # y_acceleration = ((y_velocity_final**2) - (initial_velocity[1]**2))/(2 * displacement[1])
                
                # duration = (float(y_velocity_final - initial_velocity[1]) / y_acceleration)
        # else:
            #apply y max velocity constraint to acceleration
            # x_acceleration = ((x_velocity_final**2) - (initial_velocity[0]**2))/(2 * displacement[0])
            # y_constrained_acceleration = (x_acceleration / self.get_point_cos(frame_index, point_id)) * self.get_point_sin(frame_index, point_id)
            
            # y_constrained_velocity_final = min(32,math.sqrt(initial_velocity[1]**2 + ((2 * y_constrained_acceleration)*(displacement[1]))))
            
            # if y_constrained_velocity_final == 0:
                # duration = (float(x_velocity_final - initial_velocity[0]) / x_acceleration)
            # else:
                # y_double_constrained_acceleration = ((y_constrained_velocity_final**2) - (initial_velocity[1]**2))/(2 * displacement[1])
                
                # x_double_constrained_acceleration = \
                    # (y_double_constrained_acceleration / self.get_point_sin(frame_index, point_id)) * self.get_point_cos(frame_index, point_id)
                
                # print(initial_velocity[0])
                # print(x_double_constrained_acceleration)
                # print(displacement[0])
                
                # x_constrained_velocity_final = math.sqrt(initial_velocity[0]**2 + ((2 * x_double_constrained_acceleration)*(displacement[0])))
                
                # duration = (float(x_constrained_velocity_final - initial_velocity[0]) / x_double_constrained_acceleration)
        
        return duration
    
    def calculate_velocity_without_time(self, initial_velocity, acceleration, displacement):
        final_velocity = math.sqrt((initial_velocity**2) + (2*acceleration*displacement))
        
        if displacement < 0:
            final_velocity = -1 * final_velocity
        
        return final_velocity
    
    def get_constant_velocity_frame_to_frame_duration(self, displacement, initial_velocity):
        """returns how long it will take to travel a distance in milliseconds given the
        initial velocity and the displacement.
        
        displacement: x and y displacement in a tuple (x,y)
        initial_velocity: x and y initial_velocity in a tuple (x,y)"""
        
        duration = 10
        
        if ((initial_velocity[0] == 0) or (displacement[0] == 0)):
            if ((initial_velocity[1] == 0) or (displacement[1] == 0)):
                pass
            else:
                duration = int(float(displacement[1]) / initial_velocity[1])
        else:
            duration = int(float(displacement[0]) / initial_velocity[0])
        
        return duration
