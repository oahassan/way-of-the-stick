import os
import shutil
import shelve
from glob import glob
import enumerations
from wotsprot.rencode import dumps, loads, serializable
import string
import unicodedata
import stick
import animation
import actionwizard

_HOME_DIR = ''

if 'HOME' in os.environ:
    _HOME_DIR = os.environ["HOME"]
elif 'USERPROFILE' in os.environ:
    _HOME_DIR = os.environ["USERPROFILE"]

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#TODO - create new interface to data for just player created and unlocked movesets
_MOVESET_DB_FILE_NM = "moveset_wots.dat"
_SHARING_DIR = os.path.join(_HOME_DIR, "wots_sharing")
_EXPORTED_MOVESETS_DIR = os.path.join(_SHARING_DIR, "exported")
_IMPORTED_MOVESETS_DIR = os.path.join(_SHARING_DIR, "imported")
_SHARED_MOVESETS_DIR = os.path.join(_SHARING_DIR, "new")
_MOVESET_SUFFIX = "-mov.mvs"
_SHARED_MOVESETS_GLOB_PATH = os.path.join(_SHARED_MOVESETS_DIR, "*" + _MOVESET_SUFFIX)

if not os.path.exists(_SHARING_DIR):
    os.mkdir(_SHARING_DIR)
    os.mkdir(_EXPORTED_MOVESETS_DIR)
    os.mkdir(_IMPORTED_MOVESETS_DIR)
    os.mkdir(_SHARED_MOVESETS_DIR)

def import_movesets():
    
    for shared_path in glob(_SHARED_MOVESETS_GLOB_PATH):
        
        if os.path.isfile(shared_path):
            moveset = None
            
            with open(shared_path, 'rb') as mvs_file:
                moveset = loads(mvs_file.read())
            
            save_imported_animations(moveset)
            
            #save the moveset if a moveset with its name doesn't already exist.  If it does exist find a name that has yet to be saved by appending '(#)' where # is a number.
            existing_moveset = get_moveset(moveset.name)
            
            if existing_moveset == None:
                save_moveset(moveset)
            
            else:
                name_counter = 1
                name = moveset.name
                
                while existing_moveset != None:
                    name_counter += 1
                    moveset.name = name + "(" + str(name_counter) + ")"
                    
                    existing_moveset = get_moveset(moveset.name)
                
                save_moveset(moveset)
            
            #move the imported moveset to the imported folder to show that it has been completed
            shutil.move(
                shared_path,
                os.path.join(
                    _IMPORTED_MOVESETS_DIR,
                    os.path.split(shared_path)[1]
                )
            )

def save_imported_animations(moveset):
    for animation_type, animation in moveset.movement_animations.iteritems():
        save_animation_without_overwrite(animation_type, animation)
    
    for animation_name, animation in moveset.attack_animations.iteritems():
        animation_type = moveset.attack_types[animation_name]
        
        save_animation_without_overwrite(animation_type, animation)

def save_animation_without_overwrite(animation_type, animation):
    #save the moveset if a moveset with its name doesn't already exist.  If it does exist find a name that has yet to be saved by appending '(#)' where # is a number.
    existing_animation = actionwizard.get_animation(animation_type, animation.name)
    
    if existing_animation == None:
        actionwizard.save_animation(animation_type, animation)
    
    else:
        name_counter = 1
        name = animation.name
        
        while existing_animation != None:
            name_counter += 1
            animation.name = name + "(" + str(name_counter) + ")"
            
            existing_animation = actionwizard.get_animation(animation_type, animation.name)
        
        actionwizard.save_animation(animation_type, animation)

def export_moveset(moveset):
    global _MOVESET_SUFFIX
    global _EXPORTED_MOVESETS
    
    moveset_data = dumps(moveset)
    file_name =  removeDisallowedFilenameChars(moveset.name) + _MOVESET_SUFFIX
    
    with open(os.path.join(_EXPORTED_MOVESETS_DIR, file_name),'wb') as f:
        f.write(moveset_data)

def removeDisallowedFilenameChars(filename):
    
    return ''.join(c for c in filename if c in validFilenameChars)

def get_movesets():
    movesets = shelve.open(_MOVESET_DB_FILE_NM, "c")
    
    return_movesets = []
    
    for moveset in movesets.values():
        return_movesets.append(moveset)
    
    movesets.close()
    
    return sorted(return_movesets, key=lambda moveset: moveset.name)

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
    def __init__(self, attack_types=None, attack_key_combinations=None, movement_animations=None, attack_animations=None, image=None, name=None):
        
        if movement_animations==None:
            movement_animations = {}
        self.movement_animations = movement_animations
        
        if attack_animations == None:
            attack_animations = {}
        self.attack_animations = attack_animations
        
        if attack_key_combinations==None:
            attack_key_combinations = {}
        self.attack_key_combinations = attack_key_combinations
        
        if attack_types == None:
            attack_types = {}
        self.attack_types = attack_types
        
        self.image = image
        
        if name == None:
            name = ''
        self.name = name
    
    def _pack(self):
        return (
            self.attack_types,
            self.attack_key_combinations,
            self.movement_animations,
            self.attack_animations,
            self.image,
            self.name
        )
    
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
    
    def get_attacks(self):
        """returns a list of all attacks with complete attack data"""
        return_attacks = []
        
        for attack_name in self.attack_key_combinations.keys():
            if (attack_name in self.attack_types and
            attack_name in self.attack_animations):
                return_attacks.append(attack_name)
        
        return return_attacks
    
    def get_attack_type(self, attack_name):
        
        attack_type = self.attack_types[attack_name]
        
        if attack_type == enumerations.AttackTypes.PUNCH:
            key_combination = self.attack_key_combinations[attack_name]
            
            if (enumerations.InputActionTypes.STRONG_PUNCH in key_combination or
            enumerations.InputActionTypes.STRONG_KICK in key_combination):
                return enumerations.InputActionTypes.STRONG_PUNCH
            
            elif (enumerations.InputActionTypes.MEDIUM_PUNCH in key_combination or
            enumerations.InputActionTypes.MEDIUM_KICK in key_combination):
                return enumerations.InputActionTypes.MEDIUM_PUNCH
            
            elif (enumerations.InputActionTypes.WEAK_PUNCH in key_combination or
            enumerations.InputActionTypes.WEAK_KICK in key_combination):
                return enumerations.InputActionTypes.WEAK_PUNCH
        
        elif attack_type == enumerations.AttackTypes.KICK:
            key_combination = self.attack_key_combinations[attack_name]
            
            if (enumerations.InputActionTypes.STRONG_PUNCH in key_combination or
            enumerations.InputActionTypes.STRONG_KICK in key_combination):
                return enumerations.InputActionTypes.STRONG_KICK
            
            elif (enumerations.InputActionTypes.MEDIUM_PUNCH in key_combination or
            enumerations.InputActionTypes.MEDIUM_KICK in key_combination):
                return enumerations.InputActionTypes.MEDIUM_KICK
            
            elif (enumerations.InputActionTypes.WEAK_PUNCH in key_combination or
            enumerations.InputActionTypes.WEAK_KICK in key_combination):
                return enumerations.InputActionTypes.WEAK_KICK
        else:
            raise Exception("attack type is not valid: " + attack_name)
    
    def delete_attack(self, attack_name):
        """deletes all attack data for the given attack from a moveset"""
        if attack_name in self.attack_animations:
            del self.attack_animations[attack_name]
        
        if attack_name in self.attack_key_combinations:
            del self.attack_key_combinations[attack_name]
        
        if attack_name in self.attack_types:
            del self.attack_types[attack_name]
    
    def save_movement_animation(self, player_state, animation):
        """saves movements animations"""
        self.movement_animations[player_state] = animation
    
    def save_attack_animation(self, animation):
        """saves animation of an attack"""
        self.attack_animations[animation.name] = animation
    
    def save_attack_key_combination(self, attack_name, key_combination):
        """saves a key combination for an attack"""
        self.attack_key_combinations[attack_name] = key_combination
    
    def save_attack_type(self, attack_name, attack_type):
        """saves the attack type of an attack"""
        self.attack_types[attack_name] = attack_type
    
    def is_complete(self):
        """indicates if a moveset has all the data required for it to be used"""
        return self._has_movements()
        
    def _has_movements(self):
        """validates that all unbound actions have been assigned animations"""
        action_found_indicator = True
        
        for player_state in enumerations.PlayerStates.MOVEMENTS:
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
