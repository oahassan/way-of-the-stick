"""
The motion module contains classes that move models in the physics simulation.
"""

import math
import mathfuncs
import stick
import pygame
from physics import Object

class AerialMotion():
    """A AerialMotion alters the motion of a model based on its current 
    velocity state. It is used to determine the acceleration of a model when
    it is in the air. At instantiation it takes in acceleration vector and a
    velocity vector that define the maximum acceleration and velocity 
    allowed.  The components of the velocity and acceleration vectors should
    have the same sign."""
    
    def __init__(self, acceleration_vector, velocity_vector):
        #set the maximum acceleration
        self.acceleration_vector = acceleration_vector
        
        #set the maximum velocity
        self.velocity_vector = velocity_vector
    
    def move_object(self, physics_object):
        """accelerate the object towards the maximum velocity vector"""
        
        if not isinstance(physics_object, Object):
            raise Exception("physics_object must be of type physics.Object.  Got: " + physics_object.__class__())
        
        x_object_velocity = physics_object.velocity[0]
        y_object_velocity = physics_object.velocity[1]
        
        x_acceleration = self.acceleration_vector[0]
        y_acceleration = self.acceleration_vector[1]
        
        if x_acceleration != 0:
            if mathfuncs.sign(x_object_velocity) == mathfuncs.sign(x_acceleration):
                x_acceleration_vector = min(
                    abs(self.velocity_vector[0] - x_object_velocity),
                    abs(x_acceleration * (x_object_velocity / self.velocity_vector[0]))
                ) * mathfuncs.sign(x_object_velocity)
            else:
                x_acceleration_vector = min(
                    abs(self.velocity_vector[0] - x_object_velocity),
                    abs(x_acceleration)
                ) * mathfuncs.sign(x_object_velocity)
        
        if y_acceleration != 0:
            if mathfuncs.sign(y_object_velocity) == mathfuncs.sign(y_acceleration):
                y_acceleration_vector = min(
                    abs(self.velocity_vector[1] - y_object_velocity),
                    abs(y_acceleration * (y_object_velocity / self.velocity_vector[1]))
                ) * mathfuncs.sign(y_object_velocity)
            else:
                y_acceleration_vector = min(
                    abs(self.velocity_vector[1] - y_object_velocity),
                    abs(y_acceleration)
                ) * mathfuncs.sign(y_object_velocity)
            
        physics_object.accelerate(x_acceleration, y_acceleration)
