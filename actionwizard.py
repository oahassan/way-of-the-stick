import shelve
import copy
import math

import pygame
import eztext

import wotsuievents
import button
import menupage
import gamestate
import enumerations

class ActionDictionaries():
    INPUT_ACTIONS = "inputactions"
    UNBOUND_ACTIONS = "unboundactions"

class InputActionTypes():
    MOVE_RIGHT = 'moveright'
    MOVE_LEFT = 'moveleft'
    MOVE_UP = 'moveup'
    MOVE_DOWN = 'movedown'
    ATTACK = 'attack'
    BLOCK = 'block'
    WEAK_PUNCH = 'weakpunch'
    MEDIUM_PUNCH = 'mediumpunch'
    STRONG_PUNCH = 'strongpunch'
    WEAK_KICK = 'weakkick'
    MEDIUM_KICK = 'mediumkick'
    STRONG_KICK = 'strongkick'

MOVEMENT_DB_FILE_NM = "movements_wots.dat"
ATTACK_DB_FILE_NM = "attacks_wots.dat"
ACTION_DB_FILE_NM = "actions_wots.dat"

movements = None
actions = None
attacks = None

exit_button = button.ExitButton()
exit_indicator = False

menu_buttons = []

create_attack_button = menupage.MenuButton('Create Moves', gamestate.Modes.MOVEBUILDER)
menu_buttons.append(create_attack_button)

key_binding_button = menupage.MenuButton('Bind Keys', gamestate.Modes.KEYBINDING)
menu_buttons.append(key_binding_button)

menu = menupage.Menu()
menu.load(menu_buttons)

def open_actions_shelf():
    actions = shelve.open(ACTION_DB_FILE_NM, "c")
    
    if ActionDictionaries.INPUT_ACTIONS not in actions:
        actions[ActionDictionaries.INPUT_ACTIONS] = {}
    
    if ActionDictionaries.UNBOUND_ACTIONS not in actions:
        actions[ActionDictionaries.UNBOUND_ACTIONS] = {}
    
    return actions

def get_movement_animations(movement_type):
    return_movements = []
    
    movements = shelve.open(MOVEMENT_DB_FILE_NM, "c")
    
    if movement_type in movements:
        return_movements = movements[movement_type].values()
    
    movements.close()
    
    return return_movements

def get_attack_animations(attack_type):
    return_attacks = []
    
    attacks = shelve.open(ATTACK_DB_FILE_NM, "c")
    
    if attack_type in enumerations.InputActionTypes.KICKS:
        attack_type = enumerations.AttackTypes.KICK
    elif attack_type in enumerations.InputActionTypes.PUNCHES:
        attack_type = enumerations.AttackTypes.PUNCH
    elif attack_type == enumerations.AttackTypes.KICK:
        pass
    elif attack_type == enumerations.AttackTypes.PUNCH:
        pass
    else:
        raise Exception
    
    if attack_type in attacks:
        return_attacks = attacks[attack_type].values()
    
    attacks.close()
    
    return return_attacks

def get_input_actions():
    actions = open_actions_shelf()
    input_action_dictionary = actions[ActionDictionaries.INPUT_ACTIONS]
    
    actions.close()
    return input_action_dictionary

def get_unbound_actions():
    actions = open_actions_shelf()
    unbound_actions_dictionary = actions[ActionDictionaries.UNBOUND_ACTIONS]
    
    actions.close()
    return unbound_actions_dictionary

def save_binding(action_type, key, animation, direction = None):
    actions = open_actions_shelf()
    input_action_dictionary = actions[ActionDictionaries.INPUT_ACTIONS]
    
    if action_type not in input_action_dictionary:
        input_action_dictionary[action_type] = {}
    
    input_action_dictionary[action_type][key] = (direction, animation)
    
    actions[ActionDictionaries.INPUT_ACTIONS] = input_action_dictionary
    
    actions.close()

def save_unbound_action(action_type, animation):
    actions = open_actions_shelf()
    
    unbound_actions_dictionary = actions[ActionDictionaries.UNBOUND_ACTIONS]
    unbound_actions_dictionary[action_type] = animation
    
    actions[ActionDictionaries.UNBOUND_ACTIONS] = unbound_actions_dictionary
    
    actions.close()

def save_animation(animation_type, animation):
    if animation_type in enumerations.PlayerStates.MOVEMENTS:
        save_movement(animation_type, animation)
        
    elif ((animation_type in enumerations.AttackTypes.ATTACK_TYPES) or
    (animation_type in enumerations.InputActionTypes.ATTACKS)):
        save_attack(animation_type, animation)

def save_attack(attack_type, animation):
    attacks = shelve.open(ATTACK_DB_FILE_NM, "c")
    attack_type_dictionary = {}
    
    if attack_type in enumerations.InputActionTypes.KICKS:
        attack_type = enumerations.AttackTypes.KICK
    elif attack_type in enumerations.InputActionTypes.PUNCHES:
        attack_type = enumerations.AttackTypes.PUNCH
    else:
        raise Exception
    
    if attack_type in attacks:
        attack_type_dictionary = attacks[attack_type]
    
    attack_type_dictionary[animation.name] = animation
    
    attacks[attack_type] = attack_type_dictionary
    
    attacks.close()

def save_movement(movement_type, animation):
    movements = shelve.open(MOVEMENT_DB_FILE_NM, "c")
    movement_type_dictionary = {}
    
    if movement_type in movements:
        movement_type_dictionary = movements[movement_type]
    
    movement_type_dictionary[animation.name] = animation
    movements[movement_type] = movement_type_dictionary
    
    movements.close()

def get_animation(animation_type, name):
    if animation_type in enumerations.PlayerStates.MOVEMENTS:
        return get_movement(animation_type, name)
        
    elif ((animation_type in enumerations.AttackTypes.ATTACK_TYPES) or
    (animation_type in enumerations.InputActionTypes.ATTACKS)):
        return get_attack(animation_type, name)
    
    else:
        raise Exception("Tried to retrieve invalid animation type: " + animation_type)

def get_attack(attack_type, name):
    attacks = shelve.open(ATTACK_DB_FILE_NM, "c")
    
    if attack_type in enumerations.InputActionTypes.KICKS:
        attack_type = enumerations.AttackTypes.KICK
    elif attack_type in enumerations.InputActionTypes.PUNCHES:
        attack_type = enumerations.AttackTypes.PUNCH
    else:
        raise Exception
    
    attack_type_dictionary = attacks[attack_type]
    
    return_animation = None
    
    if name in attack_type_dictionary:
        return_animation = attack_type_dictionary[name]
    
    attacks.close()
    
    return return_animation

def get_movement(movement_type, name):
    movements = shelve.open(MOVEMENT_DB_FILE_NM, "c")
    movement_type_dictionary = movements[movement_type]
    
    return_animation = None
    
    if name in movement_type_dictionary:
        return_animation = movement_type_dictionary[name]
    
    movements.close()
    
    return return_animation

def delete_animation(animation_type, animation):
    if animation_type in enumerations.PlayerStates.MOVEMENTS:
        delete_movement(animation_type, animation)
    elif (animation_type in enumerations.AttackTypes.ATTACK_TYPES or
    animation_type in enumerations.InputActionTypes.ATTACKS):
        delete_attack(animation_type, animation)

def delete_attack(attack_type, animation):
    attacks = shelve.open(ATTACK_DB_FILE_NM, "c")
    attack_type_dictionary = {}
    
    if attack_type in enumerations.InputActionTypes.KICKS:
        attack_type = enumerations.AttackTypes.KICK
    elif attack_type in enumerations.InputActionTypes.PUNCHES:
        attack_type = enumerations.AttackTypes.PUNCH
    else:
        raise Exception
    
    if attack_type in attacks:
        attack_type_dictionary = attacks[attack_type]
    
    if animation.name in attack_type_dictionary.keys():
        del attack_type_dictionary[animation.name]
    
    attacks[attack_type] = attack_type_dictionary
    
    attacks.close()

def delete_movement(movement_type, animation):
    movements = shelve.open(MOVEMENT_DB_FILE_NM, "c")
    movement_type_dictionary = {}
    
    if movement_type in movements:
        movement_type_dictionary = movements[movement_type]
    
    if animation.name in movement_type_dictionary.keys():
        del movement_type_dictionary[animation.name]
    
    movements[movement_type] = movement_type_dictionary
    
    movements.close()

def handle_events():
    global exit_indicator
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
    
    menu.handle_events()
    menu.draw(gamestate.screen)
    exit_button.draw(gamestate.screen)
