import os
import shelve
import player
from wotsprot.rencode import dumps, loads, serializable
import string
import unicodedata
import stick
import animation

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#TODO - create new interface to data for just player created and unlocked movesets
_MOVESET_DB_FILE_NM = "moveset_wots.dat"
_EXPORTED_MOVESETS_DIR = os.path.join("sharing", "exported movesets")
_IMORTED_MOVESETS_DIR = os.path.join("sharing", "imported movesets")
_SHARED_MOVESETS_DIR = os.path.join("sharing", "shared movesets")
_MOVESET_SUFFIX = "-mov.mvs"

def export_moveset(moveset):
    global _MOVESET_SUFFIX
    global _EXPORTED_MOVESETS
    
    moveset_data = dumps(moveset)
    file_name =  removeDisallowedFilenameChars(moveset.name) + _MOVESET_SUFFIX
    
    with open(os.path.join(_EXPORTED_MOVESETS_DIR, file_name),'w') as f:
        f.write(moveset_data)

def removeDisallowedFilenameChars(filename):
    
    return ''.join(c for c in filename if c in validFilenameChars)

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
    def __init__(self, movement_animations=None, attack_animations=None, image=None, name=None):
        
        if movement_animations==None:
            movement_animations = {}
        self.movement_animations = movement_animations
        
        if attack_animations == None:
            attack_animations = {}
        self.attack_animations = attack_animations
        
        self.image = image
        
        if name == None:
            name = ''
        self.name = name
    
    def _pack(self):
        return (self.movement_animations, self.attack_animations, self.image, self.name)
    
    def has_movement_animation(self, movement_type):
        return_indicator = False
        
        if ((movement_type in self.movement_animations.keys()) and
            (self.movement_animations[movement_type] != None)):
            return_indicator = True
        
        return return_indicator
    
    def has_attack_animation(self, attack_type):
        return_indicator = False
        
        if ((attack_type in self.attack_animations.keys()) and
            (self.attack_animations[attack_type] != None)):
            return_indicator = True
        
        return return_indicator
    
    def save_movement_animation(self, player_state, animation):
        """saves movements animations"""
        self.movement_animations[player_state] = animation
    
    def save_attack_animation(self, attack_type, animation):
        """saves animation of an attack"""
        self.attack_animations[attack_type] = animation
    
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
        
        return action_found_indicator

serializable.register(stick.Point)
serializable.register(stick.Line)
serializable.register(stick.Circle)
serializable.register(animation.Animation)
serializable.register(animation.Frame)
serializable.register(Moveset)
