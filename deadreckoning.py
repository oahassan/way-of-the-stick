import mathfuncs

def build_dead_reckoning_accelerations(
    start_positions,
    end_positions,
    max_acceleration,
    initial_velocites = {}
    ):
    """returns the duration between the two sets of given poistions and the
    acceleration of each point.
    
    the start_positions and end_positions should be dictionaries containing the
    same keys"""
    
    duration = \
        get_duration(
            start_positions,
            end_positions,
            max_acceleration,
            initial_velocities
        )
    
    accelerations = \
        get_accelerations(
            start_positions,
            end_positions,
            duration,
            initial_velocities
        )
    
    return duration, accelerations

def get_duration(
        start_positions,
        end_positions,
        max_acceleration,
        initial_velocities
    ):
    """returns how much time in milliseconds it takes to move between the two 
    given sets of positions.  If there is no movement 10 ms is returned."""
    
    max_distance_key, max_distance = \
        get_max_distance(start_positions, end_positions)
    max_displacement = \
        get_displacement_components(
            start_positions[max_distance_key],
            end_positions[max_distance_key]
        )
    max_acceleration = \
        get_max_acceleration_components(
            max_displacement,
            max_distance,
            max_acceleration
        )
    initial_velocity = (0,0)
    
    if len(intitial_velocities.keys()) > 0:
        intial_velocity = initial_velocities[max_distance_key]
    
    if max_displacement[0] == 0 and max_displacement[1] == 0:
        return 10
    else:
        return get_constant_acceleration_duration(
            max_displacement,
            initial_velocity,
            max_acceleration
        )

def get_max_distance(start_positions, end_positions):
    """returns key moves the furthest and the distance it travels"""
    
    max_distance = 0
    max_distance_key = start_positions.keys()[0]
    
    for key, start_position in start_positions.iteritems():
        distance = mathfuncs.distance(start_position, end_positions[key])
        
        if distance > max_distance:
            max_distance = distance
            max_distance_key = key
    
    return max_distance_key, max_distance

def get_max_acceleration_components(displacement, distance, acceleration):
    """returns the x and y components of the acceleration of a point between two
    positions."""
    
    cos = displacement[0] / distance
    sin = displacement[1] / distance
    
    x_component = cos * acceleration
    y_component = sin * acceleration
    
    return x_component, y_component

def get_displacement_components(start_position, end_position):
    """returns the x and y displacement of a point between the given fame index and
    the next one."""
    
    x_displacement = end_position[0] - start_position[0]
    y_displacement = end_position[1] - start_position[1]
    
    return x_displacement, y_displacement

def get_constant_acceleration_duration(
        displacement, \
        initial_velocity, \
        acceleration
    ):
    """returns how long it will take to travel a distance in milliseconds given the
    initial velocity, the acceleration and the displacement.
    
    displacement: x and y displacement in a tuple (x,y)
    initial_velocity: x and y initial_velocity in a tuple (x,y)
    acceleration: x and y constant acceleration in a tuple (x,y)"""
    
    duration = 10
    
    if abs(displacement[0]) > abs(displacement[1]):
        if acceleration[0] != 0:
            x_velocity_final = \
                calculate_velocity_without_time(initial_velocity[0],acceleration[0],displacement[0])
            
            duration = float(x_velocity_final - initial_velocity[0]) / acceleration[0]
        else:
            if acceleration[1] != 0:
                y_velocity_final = calculate_velocity_without_time(initial_velocity[1],acceleration[1],displacement[1])
                
                duration = float(y_velocity_final - initial_velocity[1]) / acceleration[1]
    else:
        if acceleration[1] != 0:
            x_velocity_final = calculate_velocity_without_time(initial_velocity[1],acceleration[1],displacement[1])
            
            duration = float(x_velocity_final - initial_velocity[1]) / acceleration[1]
        else:
            if acceleration[0] != 0:
                y_velocity_final = calculate_velocity_without_time(initial_velocity[0],acceleration[0],displacement[0])
                
                duration = float(y_velocity_final - initial_velocity[0]) / acceleration[0]
    
    return duration

def calculate_velocity_without_time(initial_velocity, acceleration, displacement):
    final_velocity = math.sqrt((initial_velocity**2) + (2*acceleration*displacement))
    
    if displacement < 0:
        final_velocity = -1 * final_velocity
    
    return final_velocity

def get_accelerations(
        start_positions,
        end_positions,
        duration,
        initial_velocities
    ):
    """returns the accelerations for each key"""
    
    accelerations = {}
    initial_velocity = (0,0)
    
    for key, position in start_positions.iteritems():
        displacement = \
            get_displacement_components(position, end_positions[key])
        
        if len(initial_velocities.keys()) > 0:
            initial_velocity = intial_velocities[key]
        
        accelerations[key] = \
            calculate_acceleration_components(
                duration,
                displacement,
                initial_velocity
            )
    
    return accelerations

def calculate_acceleration_components(self, duration, displacement, initial_velocity):
    """calculates the x and y acceleration of a point given its displacement, initial
    velocity and the time between frames
    
    duration: the time between two frames
    displacement: the x and y displacement of a point between two frames
    initial_velocity: the x and y velocity of a point at the starting frame"""
    
    x_acceleration = float(2*(displacement[0] - (initial_velocity[0]*duration))) / (duration**2)
    y_acceleration = float(2*(displacement[1] - (initial_velocity[1]*duration))) / (duration**2)
    
    return (x_acceleration, y_acceleration)
