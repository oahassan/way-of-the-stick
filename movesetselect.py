import pygame

import wotsui
import wotsuievents
import button
import gamestate
import movesetdata
import movesetbuilder
import movesetselectui

loaded = False
exit_button = None
create_new_moveset_label = None
edit_moveset_label = None
delete_moveset_label = None
moveset_select_container = None

def load():
    global loaded
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    global exit_button
    
    exit_button = button.ExitButton()
    create_new_moveset_label = button.TextButton('Create New Moveset', 25)
    create_new_moveset_label.set_position((10,10))
    
    moveset_select_container_position = (10, 20 + create_new_moveset_label.height)
    moveset_select_container = movesetselectui.MovesetSelectContainer(moveset_select_container_position, \
                                                                      400, \
                                                                      700, \
                                                                      'Select A Moveset', \
                                                                      movesetdata.get_movesets())
    
    edit_moveset_label_position = (10, create_new_moveset_label.height + 20 + moveset_select_container.height + 10)
    edit_moveset_label = button.TextButton('Edit Moveset', 25)
    edit_moveset_label.inactivate()
    edit_moveset_label.set_position(edit_moveset_label_position)
    
    delete_moveset_label_position = (10 + edit_moveset_label.width + 20, edit_moveset_label_position[1])
    delete_moveset_label = button.TextButton('Delete Moveset',25)
    delete_moveset_label.inactivate()
    delete_moveset_label.set_position(delete_moveset_label_position)
    
    loaded = True

def unload():
    global loaded
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    global exit_button
    
    exit_button = None
    create_new_moveset_label = None
    edit_moveset_label = None
    delete_moveset_label = None
    moveset_select_container = None
    
    loaded = False

def handle_events():
    global loaded
    global exit_button
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        if create_new_moveset_label.contains(wotsuievents.mouse_pos):
            create_new_moveset_label.handle_selected()
        
        if edit_moveset_label.contains(wotsuievents.mouse_pos) and edit_moveset_label.active:
            edit_moveset_label.handle_selected()
        
        if delete_moveset_label.contains(wotsuievents.mouse_pos) and delete_moveset_label.active:
            delete_moveset_label.handle_selected()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
        elif create_new_moveset_label.selected:
            create_new_moveset_label.handle_deselected()
            
            if create_new_moveset_label.contains(wotsuievents.mouse_pos):
                movesetbuilder.load(movesetdata.Moveset())
                gamestate.mode = gamestate.Modes.MOVESETBUILDER
                unload()
        
        elif edit_moveset_label.selected:
            edit_moveset_label.handle_deselected()
            
            if edit_moveset_label.contains(wotsuievents.mouse_pos):
                movesetbuilder.load(moveset_select_container.selected_moveset)
                gamestate.mode = gamestate.Modes.MOVESETBUILDER
                unload()
        
        elif delete_moveset_label.selected:
            delete_moveset_label.handle_deselected()
            
            if delete_moveset_label.contains(wotsuievents.mouse_pos):
                movesetdata.delete_moveset(moveset_select_container.selected_moveset)
                moveset_select_container.selected_moveset = None
                moveset_select_container.load_movesets(movesetdata.get_movesets())
    
    if loaded:
        moveset_select_container.handle_events()
        
        exit_button.draw(gamestate.screen)
        edit_moveset_label.draw(gamestate.screen)
        create_new_moveset_label.draw(gamestate.screen)
        delete_moveset_label.draw(gamestate.screen)
        moveset_select_container.draw(gamestate.screen)
        
        if moveset_select_container.selected_moveset != None:
            if not edit_moveset_label.active:
                edit_moveset_label.activate()
            if not delete_moveset_label.active:
                delete_moveset_label.activate()
        else:
            if edit_moveset_label.active:
                edit_moveset_label.inactivate()
            if delete_moveset_label.active:
                delete_moveset_label.inactivate()