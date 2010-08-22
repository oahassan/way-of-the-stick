import math
import mathfuncs

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
