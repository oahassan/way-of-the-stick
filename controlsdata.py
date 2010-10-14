import shelve
import copy
import pygame

class InputActionTypes():
    MOVE_RIGHT = 'moveright'
    MOVE_LEFT = 'moveleft'
    MOVE_UP = 'moveup'
    MOVE_DOWN = 'movedown'
    BLOCK = 'block'
    WEAK_PUNCH = 'weakpunch'
    MEDIUM_PUNCH = 'mediumpunch'
    STRONG_PUNCH = 'strongpunch'
    WEAK_KICK = 'weakkick'
    MEDIUM_KICK = 'mediumkick'
    STRONG_KICK = 'strongkick'
    
    ATTACKS = [
        WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH,
        WEAK_KICK, MEDIUM_KICK, STRONG_KICK
    ]

CONTROlS_DB_FILE_NM = 'controls_wots.dat'

controls = None

def open_controls_shelf():
    controls = shelve.open(CONTROlS_DB_FILE_NM, "c")
    
    #default controls when opening for the first time
    if len(controls.keys()) == 0:
        controls[InputActionTypes.MOVE_RIGHT] = pygame.K_RIGHT
        controls[InputActionTypes.MOVE_LEFT] = pygame.K_LEFT
        controls[InputActionTypes.MOVE_UP] = pygame.K_UP
        controls[InputActionTypes.MOVE_DOWN] = pygame.K_DOWN
        controls[InputActionTypes.WEAK_PUNCH] = pygame.K_q
        controls[InputActionTypes.MEDIUM_PUNCH] = pygame.K_w
        controls[InputActionTypes.STRONG_PUNCH] = pygame.K_e
        controls[InputActionTypes.WEAK_KICK] = pygame.K_a
        controls[InputActionTypes.MEDIUM_KICK] = pygame.K_s
        controls[InputActionTypes.STRONG_KICK] = pygame.K_d
    
    return controls

def get_control_key(action_type):
    controls = open_controls_shelf()
    
    return_control = controls[action_type]
    
    controls.close()
    
    return return_control

def set_control_key(action_type, key):
    controls = open_controls_shelf()
    
    controls[action_type] = key
    
    controls.close()