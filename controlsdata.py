import shelve
import copy
from actionwizard import InputActionTypes
import pygame

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
        controls[InputActionTypes.WEAK_PUNCH] = pygmae.K_q
        controls[InputActionTypes.MEDIUM_PUNCH] = pygmae.K_w
        controls[InputActionTypes.STRONG_PUNCH] = pygmae.K_e
        controls[InputActionTypes.WEAK_KICK] = pygmae.K_a
        controls[InputActionTypes.MEDIUM_KICK] = pygmae.K_s
        controls[InputActionTypes.STRONG_KICK] = pygmae.K_d
    
    return controls

def get_controls():
    controls = open_controls_shelf()
    
    return_controls = controls.copy()
    
    controls.close()
    
    return return_controls
