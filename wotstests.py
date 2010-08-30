from nose.tools import *
import unittest
import copy
import math

import stick
import animation
import mathfuncs

class AnimationTests(unittest.TestCase):
    TEST_POINT_NAME = "testpoint"
    ACCELERATION = 1
    GRAVITY = 1
    
    def init_function_parms(self):
        x_initial_velocity = 0
        x_tuple = self.create_kinematics_tuple(x_initial_velocity,0,'x')
        
        y_initial_velocity = 0
        y_tuple = self.create_kinematics_tuple(y_initial_velocity,0,'y')
        
        self.add_frame_kinematics_data(x_tuple, y_tuple)
        
        x_initial_velocity = self.final_velocities[0][0]
        x_tuple = self.create_kinematics_tuple(x_initial_velocity,1,'x')
        
        y_initial_velocity = self.final_velocities[0][1]
        y_tuple = self.create_kinematics_tuple(y_initial_velocity,1,'y')
        
        self.add_frame_kinematics_data(x_tuple, y_tuple)
        
        x_initial_velocity = 0
        x_tuple = self.create_kinematics_tuple(x_initial_velocity,2,'x')
        
        y_initial_velocity = 0
        y_tuple = self.create_kinematics_tuple(y_initial_velocity,2,'y')
        
        self.add_frame_kinematics_data(x_tuple, y_tuple)
        
        x_initial_velocity = 0
        x_tuple = self.create_kinematics_tuple(x_initial_velocity,3,'x')
        
        y_initial_velocity = 0
        y_tuple = self.create_kinematics_tuple(y_initial_velocity,3,'y')
        
        self.add_frame_kinematics_data(x_tuple, y_tuple)
    
    def create_kinematics_tuple(self, initial_velocity, frame_index, axis):
        kinematics_tuple = None
        start_point = self.animation.frames[frame_index].points()[0]
        end_point = self.animation.frames[frame_index + 1].points()[0]
        
        if axis == 'x':
            displacement = end_point.pos[0] - start_point.pos[0]
            acceleration = self.cos(start_point.pos, end_point.pos)*AnimationTests.ACCELERATION
            final_velocity = self.calculate_velocity_without_time(initial_velocity,acceleration,displacement)
            kinematics_tuple = (displacement,initial_velocity,final_velocity,acceleration)
        elif axis == 'y':
            displacement = end_point.pos[1] - start_point.pos[1]
            acceleration = self.sin(start_point.pos, end_point.pos)*AnimationTests.ACCELERATION
            final_velocity = self.calculate_velocity_without_time(initial_velocity,acceleration,displacement)
            kinematics_tuple = (displacement,initial_velocity,final_velocity,acceleration)
        
        return kinematics_tuple
    
    def add_frame_kinematics_data(self, x_kinematics_tuple, y_kinematics_tuple):
        duration = 10
        
        if x_kinematics_tuple[0] != 0:
            duration = float(x_kinematics_tuple[2] - x_kinematics_tuple[1]) / x_kinematics_tuple[3]
        elif y_kinematics_tuple[0] != 0:
            duration = float(y_kinematics_tuple[2] - y_kinematics_tuple[1]) / y_kinematics_tuple[3]
        
        #recalculate the final velocity given the rounding of time
        x_acceleration = self.calculate_acceleration(duration, x_kinematics_tuple[0], x_kinematics_tuple[1])
        x_final_velocity = self.calculate_velocity_with_time(duration, x_kinematics_tuple[1], x_acceleration)
        
        y_acceleration = self.calculate_acceleration(duration, y_kinematics_tuple[0], y_kinematics_tuple[1])
        y_final_velocity = self.calculate_velocity_with_time(duration, y_kinematics_tuple[1], y_acceleration)
        
        x_kinematics_tuple = (x_kinematics_tuple[0], x_kinematics_tuple[1], x_final_velocity, x_acceleration)
        y_kinematics_tuple = (y_kinematics_tuple[0], y_kinematics_tuple[1], y_final_velocity, y_acceleration)
        
        self.displacements.append((x_kinematics_tuple[0], y_kinematics_tuple[0]))
        self.initial_velocities.append((x_kinematics_tuple[1], y_kinematics_tuple[1]))
        self.final_velocities.append((x_kinematics_tuple[2], y_kinematics_tuple[2]))
        self.accelerations.append((x_kinematics_tuple[3], y_kinematics_tuple[3]))
        self.frame_times.append(duration)
        
        if len(self.frame_start_times) == 0:
            self.frame_start_times.append(0)
        else:
            self.frame_start_times.append(self.frame_end_times[len(self.frame_end_times) - 1])
        
        self.frame_end_times.append(self.frame_start_times[len(self.frame_start_times) - 1] + duration)
    
    def sin(self, start_position, end_position):
        distance = mathfuncs.distance(start_position, end_position)
        y_delta = end_position[1] - start_position[1]
        
        sin = 0
        
        if distance > 0:
            sin = float(y_delta) / distance
        
        return sin
    
    def cos(self, start_position, end_position):
        distance = mathfuncs.distance(start_position, end_position)
        x_delta = end_position[0] - start_position[0]
        
        cos = 0
        
        if distance > 0:
            cos = float(x_delta) / distance
        
        return cos
    
    def calculate_displacement(self, duration, initial_velocity, acceleration):
        return (initial_velocity*duration) + (.5*acceleration*(duration**2))
    
    def calculate_velocity_without_time(self, initial_velocity, acceleration, displacement):
        final_velocity = math.sqrt((initial_velocity**2) + (2*acceleration*displacement))
        
        if displacement < 0:
            final_velocity = -1 * final_velocity
        
        return final_velocity
    
    def calculate_velocity_with_time(self, duration, initial_velocity, acceleration):
        return initial_velocity + (acceleration*duration)
    
    def calculate_acceleration(self, duration, displacement, initial_velocity):
        return float(2*(displacement - (initial_velocity*duration)))/(duration**2)
    
class PointPathTests(AnimationTests):
    def setUp(self):
        self.animation = animation.Animation()
        
        self.first_frame_point = stick.Point((0,0))
        self.second_frame_point = copy.deepcopy(self.first_frame_point)
        self.second_frame_point.pos = (10,10)
        self.third_frame_point = copy.deepcopy(self.first_frame_point)
        self.third_frame_point.pos = (20,20)
        self.fourth_frame_point = copy.deepcopy(self.first_frame_point)
        self.fourth_frame_point.pos = (10,10)
        self.fifth_frame_point = copy.deepcopy(self.first_frame_point)
        self.fifth_frame_point.pos = (10,10)
        
        self.animation.frames[0].add_point(self.first_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[1].add_point(self.second_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[2].add_point(self.third_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[3].add_point(self.fourth_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[4].add_point(self.fifth_frame_point)
        
        self.displacements = []
        self.initial_velocities = []
        self.final_velocities = []
        self.accelerations = []
        self.frame_times = []
        self.frame_start_times = []
        self.frame_end_times = []
        
        self.init_function_parms()
        
        self.animation.point_names[AnimationTests.TEST_POINT_NAME] = self.first_frame_point.id
        self.animation.set_animation_point_path_data(AnimationTests.ACCELERATION)
       
    def test_hold_position(self):
        start_time = 14
        end_time = 20
        
        displacement = self.animation.build_point_time_delta_dictionary(start_time, end_time)[AnimationTests.TEST_POINT_NAME]
        
        self.assertEqual(0,displacement[0])
        self.assertEqual(0,displacement[1])
    
    def test_reverse_position(self):
        start_time = 3
        end_time = 10
        
        initial_acceleration = self.accelerations[0]
        x_first_frame_displacement = self.calculate_displacement(start_time,0,initial_acceleration[0])
        y_first_frame_displacement = self.calculate_displacement(start_time,0,initial_acceleration[1])
        
        third_frame_acceleration = self.accelerations[2]
        first_frame_displacement = self.displacements[0]
        second_frame_displacement = self.displacements[1]
        
        x_third_frame_initial_velocity = self.initial_velocities[2][0]
        y_third_frame_initial_velocity = self.initial_velocities[2][1]
        
        third_frame_duration = end_time - self.frame_start_times[2]
        
        x_displacement = (second_frame_displacement[0] + first_frame_displacement[0] - x_first_frame_displacement) + \
                         (x_third_frame_initial_velocity*third_frame_duration) + (.5*third_frame_acceleration[0]*(third_frame_duration**2))
        y_displacement = (second_frame_displacement[1] + first_frame_displacement[1] - y_first_frame_displacement) + \
                         (y_third_frame_initial_velocity*third_frame_duration) + (.5*third_frame_acceleration[1]*(third_frame_duration**2))
        
        displacement = self.animation.build_point_time_delta_dictionary(start_time, end_time)[AnimationTests.TEST_POINT_NAME]
        
        self.assertEqual(x_displacement, displacement[0])
        self.assertEqual(y_displacement, displacement[1])
    
    def test_get_velocity_components(self):
        velocity = self.animation.get_velocity_components(2,self.first_frame_point.id)
        trueVelocity = self.initial_velocities[2]
        
        self.assertEqual(velocity[0], trueVelocity[0])
        self.assertEqual(velocity[1], trueVelocity[1])
    
    def test_calculate_position_by_time(self):
        start_time = 0
        end_time = 2
        # import pdb; pdb.set_trace()
        
        initial_velocity = self.initial_velocities[0]
        initial_acceleration = self.accelerations[0]
        x_initial_velocity = initial_velocity[0]
        y_initial_velocity = initial_velocity[1]
        x_initial_acceleration = initial_acceleration[0]
        y_initial_acceleration = initial_acceleration[1]
        
        duration = end_time - start_time
        x_displacement = (x_initial_velocity * duration) + (.5*x_initial_acceleration*(duration**2))
        y_displacement = (y_initial_velocity * duration) + (.5*y_initial_acceleration*(duration**2))
        
        displacement = self.animation.build_point_time_delta_dictionary(start_time, end_time)[AnimationTests.TEST_POINT_NAME]
        
        self.assertEqual(x_displacement, displacement[0])
        self.assertEqual(y_displacement, displacement[1])
    
    def test_start_to_mid_frame_position(self):
        start_time = 0
        end_time = 6
        
        x_initial_velocity = self.initial_velocities[1][0]
        y_initial_velocity = self.initial_velocities[1][1]
        acceleration = self.accelerations[1]
        duration = end_time - self.frame_end_times[0]
        
        x_displacement = self.displacements[0][0] + (x_initial_velocity*duration) + (.5*acceleration[0]*(duration**2))
        y_displacement = self.displacements[0][1] + (y_initial_velocity*duration) + (.5*acceleration[1]*(duration**2))
        
        displacement = self.animation.build_point_time_delta_dictionary(start_time, end_time)[AnimationTests.TEST_POINT_NAME]
        
        self.assertEqual(x_displacement, displacement[0])
        self.assertEqual(y_displacement, displacement[1])
    
    def test_mid_frame_to_mid_frame_position(self):
        start_time = 3
        end_time = 6
        
        initial_acceleration = self.accelerations[0]
        x_first_frame_displacement = self.calculate_displacement(start_time,0,initial_acceleration[0])
        y_first_frame_displacement = self.calculate_displacement(start_time,0,initial_acceleration[1])
        
        second_frame_acceleration = self.accelerations[1]
        first_frame_displacement = self.displacements[0]
        
        x_second_frame_initial_velocity = self.initial_velocities[1][0]
        y_second_frame_initial_velocity = self.initial_velocities[1][1]
        
        second_frame_duration = end_time - self.frame_start_times[1]
        
        x_displacement = (first_frame_displacement[0] - x_first_frame_displacement) + \
                         (x_second_frame_initial_velocity*second_frame_duration) + (.5*second_frame_acceleration[0]*(second_frame_duration**2))
        y_displacement = (first_frame_displacement[1] - y_first_frame_displacement) + \
                         (y_second_frame_initial_velocity*second_frame_duration) + (.5*second_frame_acceleration[1]*(second_frame_duration**2))
        
        displacement = self.animation.build_point_time_delta_dictionary(start_time, end_time)[AnimationTests.TEST_POINT_NAME]
        
        self.assertEqual(x_displacement, displacement[0])
        self.assertEqual(y_displacement, displacement[1])
    
    def test_get_constant_acceleration_frame_to_frame_duration_with_x(self):
        
        initial_velocity = self.initial_velocities[2]
        acceleration = self.accelerations[2]
        displacement = self.displacements[2]
        
        x_final_velocity = self.final_velocities[2][0]
        duration = float(x_final_velocity - initial_velocity[0]) / acceleration[0]
        
        animation_duration = self.animation.get_constant_acceleration_frame_to_frame_duration(0,0,displacement,initial_velocity,acceleration)
        
        self.assertEqual(duration, animation_duration)
    
    def test_get_constant_acceleration_frame_to_frame_duration_with_y(self):
        
        initial_velocity = (0,0)
        acceleration = (0,1)
        displacement = (0,10)
        
        y_final_velocity = math.sqrt((initial_velocity[1]**2) + 2*acceleration[1]*displacement[1])
        duration = float(y_final_velocity - initial_velocity[1]) / acceleration[1]
        
        animation_duration = self.animation.get_constant_acceleration_frame_to_frame_duration(0,0,displacement,initial_velocity,acceleration)
        
        self.assertEqual(duration, animation_duration)
       
class AnimationPhysicsTests(AnimationTests):
    def setUp(self):
        self.animation = animation.Animation()
        
        self.first_frame_point = stick.Point((20,20))
        self.second_frame_point = copy.deepcopy(self.first_frame_point)
        self.second_frame_point.pos = (10,10)
        self.third_frame_point = copy.deepcopy(self.first_frame_point)
        self.third_frame_point.pos = (20,20)
        self.fourth_frame_point = copy.deepcopy(self.first_frame_point)
        self.fourth_frame_point.pos = (0,0)
        self.fifth_frame_point = copy.deepcopy(self.first_frame_point)
        self.fifth_frame_point.pos = (10,10)
        
        self.animation.frames[0].add_point(self.first_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[1].add_point(self.second_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[2].add_point(self.third_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[3].add_point(self.fourth_frame_point)
        self.animation.frames.append(animation.Frame())
        self.animation.frames[4].add_point(self.fifth_frame_point)
        
        self.displacements = []
        self.initial_velocities = []
        self.final_velocities = []
        self.accelerations = []
        self.frame_times = []
        self.frame_start_times = []
        self.frame_end_times = []
        
        self.init_function_parms()
        
        self.animation.point_names[AnimationTests.TEST_POINT_NAME] = self.first_frame_point.id
        self.animation.set_animation_reference_point_path_data(AnimationTests.ACCELERATION,
                                                               AnimationTests.GRAVITY)
    
    def test_get_jump_height(self):
        jump_height_1 = self.animation.get_jump_height(0,2)
        jump_height_2 = self.animation.get_jump_height(2,4)
        
        self.assertEqual(-10, jump_height_1)
        self.assertEqual(-20, jump_height_2)
    
    def test_get_jump_velocity(self):
        self.assertEqual(0, self.animation.get_initial_jump_velocity(1))
        #import pdb;pdb.set_trace()
        y_velocity_1 = -math.sqrt(abs(2*AnimationTests.GRAVITY*10))
        self.assertEqual(y_velocity_1, self.animation.get_initial_jump_velocity(0))
    
if __name__ == '__main__':
    unittest.main()
