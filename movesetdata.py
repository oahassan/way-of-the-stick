import shelve
import player

_MOVESET_DB_FILE_NM = "moveset_wots.dat"

def get_movesets():
    movesets = shelve.open(_MOVESET_DB_FILE_NM, "c")
    
    return_movesets = []
    
    for moveset in movesets.values():
        return_movesets.append(moveset)
    
    movesets.close()
    
    return return_movesets

def get_moveset(moveset_name):
    movesets = shelve.open(_MOVESET_DB_FILE_NM, "c")
    return_moveset = None
    
    if moveset_name in movesets.keys():
        return_moveset = movesets[moveset_name]
    
    movesets.close()
    
    return return_moveset

def save_moveset(moveset):
    movesets = shelve.open(_MOVESET_DB_FILE_NM, "c")
    
    movesets[moveset.name] = moveset
    
    movesets.close()

def delete_moveset(moveset):
    movesets = shelve.open(_MOVESET_DB_FILE_NM, "c")
    
    del movesets[moveset.name]
    
    movesets.close()

class MovementTypes():
    MOVE_RIGHT = 'moveright'
    MOVE_LEFT = 'moveleft'
    MOVE_UP = 'moveup'
    MOVE_DOWN = 'movedown'
    
    MOVEMENT_TYPES = [MOVE_RIGHT, MOVE_LEFT, MOVE_UP, MOVE_DOWN]
    AERIAL_MOVEMENT_TYPES = [MOVE_RIGHT, MOVE_LEFT, MOVE_DOWN]

class Moveset():
    def __init__(self):
        self.movement_keys = {}
        self.movement_key_to_movement_type = {}
        self.movement_animations = {}
        self.attack_animations = {}
        self.attack_keys = {}
        self.attack_types = {}
        self.image = None
        self.name = ''
    
    def has_movement_animation(self, movement_type):
        return_indicator = False
        
        if ((movement_type in self.movement_animations.keys()) and
            (self.movement_animations[movement_type] != None)):
            return_indicator = True
        
        return return_indicator
    
    def has_movement_key(self, movement_type):
        return_indicator = False
        
        if ((movement_type in self.movement_keys.keys()) and
            (self.movement_keys[movement_type] != None)):
            return_indicator = True
        
        return return_indicator
    
    def has_attack_animation(self, animation_name):
        return_indicator = False
        
        if ((animation_name in self.attack_animations.keys()) and
            (self.attack_animations[animation_name] != None)):
            return_indicator = True
        
        return return_indicator
    
    def has_attack_key(self, attack_name):
        return_indicator = False
        
        if ((attack_name in self.attack_keys.keys()) and
            (self.attack_keys[attack_name] != None)):
            return_indicator = True
        
        return return_indicator
    
    def has_attack_type(self, attack_name):
        return_indicator = False
        
        if ((attack_name in self.attack_types.keys()) and
            (self.attack_types[attack_name] != None)):
            return_indicator = True
        
        return return_indicator
    
    def remove_attack(self, attack_name):
        if self.has_attack_animation(attack_name):
            del self.attack_animations[attack_name]
        
        if self.has_attack_key(attack_name):
            del self.attack_keys[attack_name]
        
        if self.has_attack_type(attack_name):
            del self.attack_types[attack_name]
    
    def save_movement_animation(self, player_state, animation):
        """saves movements animations"""
        self.movement_animations[player_state] = animation
    
    def save_movement_key(self, movement_type, key):
        """saves the key for a movement"""
        self.movement_keys[movement_type] = key
        
        if movement_type in self.movement_key_to_movement_type.values():
            for bound_key, bound_movement_type in self.movement_key_to_movement_type.iteritems():
                if bound_movement_type == movement_type:
                    del self.movement_key_to_movement_type[key]
                    break
        
        self.movement_key_to_movement_type[key] = movement_type
    
    def save_attack_animation(self, animation):
        """saves animation of an attack"""
        self.attack_animations[animation.name] = animation
    
    def save_attack_key(self, animation_name, key):
        """saves the key of an attack"""
        self.attack_keys[animation_name] = key
    
    def save_attack_type(self, animation_name, attack_type):
        """saves the type of an attack"""
        self.attack_types[animation_name] = attack_type
    
    def is_complete(self):
        """indicates if a moveset has all the data required for it to be used"""
        return self._has_movements()
        
    def _has_movements(self):
        """validates that all unbound actions have been assigned animations"""
        action_found_indicator = True
        
        for player_state in player.PlayerStates.MOVEMENTS:
            if player_state in self.movement_animations.keys():
                if self.movement_animations[player_state] == None:
                    action_found_indicator = False
                    break
            else:
                action_found_indicator = False
                break
        
        for movement_type in MovementTypes.MOVEMENT_TYPES:
            if movement_type in self.movement_keys.keys():
                if self.movement_keys[movement_type] == None:
                    action_found_indicator = False
                    break
            else:
                action_found_indicator = False
                break
        
        return action_found_indicator
    
    def attack_is_complete(self, attack_name):
        return (attack_name in self.attack_types.keys()) and (attack_name in self.attack_keys.keys())