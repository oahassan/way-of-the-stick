import os
import shutil
import shelve
import enumerations
from wotsprot.rencode import dumps, loads, serializable
import string
import unicodedata
import stick
import animation
import actionwizard

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#TODO - create new interface to data for just player created and unlocked movesets
_MOVESET_DB_FILE_NM = "moveset_wots.dat"
_EXPORTED_MOVESETS_DIR = os.path.join("sharing", "exported movesets")
_IMPORTED_MOVESETS_DIR = os.path.join("sharing", "imported movesets")
_SHARED_MOVESETS_DIR = os.path.join("sharing", "shared movesets")
_MOVESET_SUFFIX = "-mov.mvs"

def import_movesets():
    
    for mvs in os.listdir(_SHARED_MOVESETS_DIR):
        
        if mvs.endswith(_MOVESET_SUFFIX):
            moveset = None
            shared_path = os.path.join(_SHARED_MOVESETS_DIR, mvs)
            
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
            shutil.move(shared_path, os.path.join(_IMPORTED_MOVESETS_DIR, mvs))

def save_imported_animations(moveset):
    for animation_type, animation in moveset.movement_animations.iteritems():
        save_animation_without_overwrite(animation_type, animation)
    
    for animation_type, animation in moveset.attack_animations.iteritems():
        if animation_type in []:
            save_animation_without_overwrite(animation_type, animation)
        elif animation_type in []:
            save_animation_without_overwrite(animation_type, animation)
        else:
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
