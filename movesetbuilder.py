import pygame

import wotsui
import wotsuievents
import button
import gamestate
import movesetdata
import movesetbuilderui
import attackbuilderui

exit_button = button.ExitButton()
loaded = False
moveset = None
movement_builder = None
attack_builder = None
moveset_name_entry_box = None

def load(edit_moveset):
    global loaded
    global moveset
    global movement_builder
    global moveset_name_entry_box
    global attack_builder
    
    loaded = True
    moveset = edit_moveset
    moveset_name_entry_box = movesetbuilderui.MovesetNameEntryBox()
    moveset_name_entry_box.set_moveset(moveset)
    movement_builder = movesetbuilderui.MovementBuilderContainer()
    movement_builder.set_moveset(moveset)
    movement_builder.expand()
    attack_builder = attackbuilderui.AttackBuilderContainer()
    attack_builder.set_moveset(moveset)
    attack_builder.collapse()

def unload():
    global loaded
    global moveset
    global movement_builder
    global moveset_name_entry_box
    global attack_builder
    
    moveset_name_entry_box = None
    moveset = None
    movement_builder = None
    attack_builder = None
    loaded = False

def handle_events():
    global exit_indicator
    global movement_builder
    global loaded
    global moveset_name_entry_box
    global attack_builder
    global moveset
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        if attack_builder.title.contains(wotsuievents.mouse_pos) and \
           attack_builder.expanded == False:
           movement_builder.save()
           movement_builder.collapse()
           attack_builder.expand()
        if movement_builder.title.contains(wotsuievents.mouse_pos) and \
           movement_builder.expanded == False:
           attack_builder.save()
           attack_builder.collapse()
           movement_builder.expand()
        
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                attack_builder.save()
                movement_builder.save()
                
                if moveset.name != '':
                    movesetdata.save_moveset(moveset)
                
                gamestate.mode = gamestate.Modes.MOVESETSELECT
                unload()
    
    if loaded:
        moveset_name_entry_box.handle_events()
        
        if movement_builder.expanded:
            movement_builder.handle_events()
        
        if attack_builder.expanded:
            attack_builder.handle_events()
        
        moveset_name_entry_box.draw(gamestate.screen)
        movement_builder.draw(gamestate.screen)
        attack_builder.draw(gamestate.screen)
        exit_button.draw(gamestate.screen)
