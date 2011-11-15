import shelve
import copy
import pygame
from enumerations import InputActionTypes, PlayerPositions

CONTROlS_DB_FILE_NM = 'controls_wots.dat'

controls = None

def open_controls_shelf():
    controls = shelve.open(CONTROlS_DB_FILE_NM, "c")
    
    #default controls when opening for the first time
    if len(controls.keys()) == 0:
        player_1_controls = {}
        player_1_controls[InputActionTypes.MOVE_RIGHT] = pygame.K_d
        player_1_controls[InputActionTypes.MOVE_LEFT] = pygame.K_a
        player_1_controls[InputActionTypes.MOVE_UP] = pygame.K_w
        player_1_controls[InputActionTypes.MOVE_DOWN] = pygame.K_s
        player_1_controls[InputActionTypes.WEAK_PUNCH] = pygame.K_u
        player_1_controls[InputActionTypes.MEDIUM_PUNCH] = pygame.K_i
        player_1_controls[InputActionTypes.STRONG_PUNCH] = pygame.K_o
        player_1_controls[InputActionTypes.WEAK_KICK] = pygame.K_j
        player_1_controls[InputActionTypes.MEDIUM_KICK] = pygame.K_k
        player_1_controls[InputActionTypes.STRONG_KICK] = pygame.K_l
        player_1_controls[InputActionTypes.JUMP] = pygame.K_SPACE
        
        controls[PlayerPositions.PLAYER1] = player_1_controls
        
        player_2_controls = {}
        player_2_controls[InputActionTypes.MOVE_RIGHT] = pygame.K_KP3
        player_2_controls[InputActionTypes.MOVE_LEFT] = pygame.K_KP1
        player_2_controls[InputActionTypes.MOVE_UP] = pygame.K_KP5
        player_2_controls[InputActionTypes.MOVE_DOWN] = pygame.K_KP2
        player_2_controls[InputActionTypes.WEAK_PUNCH] = pygame.K_INSERT
        player_2_controls[InputActionTypes.MEDIUM_PUNCH] = pygame.K_HOME
        player_2_controls[InputActionTypes.STRONG_PUNCH] = pygame.K_PAGEUP
        player_2_controls[InputActionTypes.WEAK_KICK] = pygame.K_DELETE
        player_2_controls[InputActionTypes.MEDIUM_KICK] = pygame.K_END
        player_2_controls[InputActionTypes.STRONG_KICK] = pygame.K_PAGEDOWN
        player_2_controls[InputActionTypes.JUMP] = pygame.K_KP0
        
        controls[PlayerPositions.PLAYER2] = player_2_controls
    
    return controls

def get_controls():
    controls = open_controls_shelf()
    
    return_controls = dict([(key, value) for key, value in controls.iteritems()])
    
    controls.close()
    
    return return_controls

def get_control_key(player_position, action_type):
    controls = open_controls_shelf()
    
    return_control = controls[player_position][action_type]
    
    controls.close()
    
    return return_control

def set_control_key(player_position, action_type, key):
    controls = open_controls_shelf()
    player_controls = controls[player_position]
    player_controls[action_type] = key
    controls[player_position] = player_controls
    
    controls.close()
