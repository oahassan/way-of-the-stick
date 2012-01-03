from threading import Thread
import pygame

import wotsui
import wotsuievents
import button
import gamestate
import movesetdata
import movesetbuilder
import movesetselectui
import splash

loaded = False
exit_button = None
create_new_moveset_label = None
edit_moveset_label = None
delete_moveset_label = None
moveset_select_container = None
export_moveset_label = None
import_movesets_label = None
import_movesets_thread = None
import_alert_box = None

def load():
    global loaded
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    global exit_button
    global export_moveset_label
    global import_movesets_label
    global import_alert_box
    
    import_alert_box = movesetselectui.ImportAlertBox()
    
    exit_button = button.ExitButton()
    create_new_moveset_label = button.TextButton('Create New Moveset', 25)
    create_new_moveset_label.set_position((10,10))
    
    import_movesets_label_position = (10 + create_new_moveset_label.width + 20, create_new_moveset_label.position[1])
    import_movesets_label = button.TextButton('Import Movesets', 25)
    import_movesets_label.set_position(import_movesets_label_position)
    
    moveset_select_container_position = (10, 20 + create_new_moveset_label.height)
    moveset_select_container = movesetselectui.MovesetSelectContainer(
        moveset_select_container_position,
        400,
        700,
        'Select A Moveset',
        movesetdata.get_movesets())
    
    edit_moveset_label_position = (10, create_new_moveset_label.height + 20 + moveset_select_container.height + 10)
    edit_moveset_label = button.TextButton('Edit Moveset', 25)
    edit_moveset_label.inactivate()
    edit_moveset_label.set_position(edit_moveset_label_position)
    
    delete_moveset_label_position = (10 + edit_moveset_label.width + 20, edit_moveset_label_position[1])
    delete_moveset_label = button.TextButton('Delete Moveset',25)
    delete_moveset_label.inactivate()
    delete_moveset_label.set_position(delete_moveset_label_position)
    
    export_moveset_label_position = (20 + edit_moveset_label.width + delete_moveset_label.width + 20, delete_moveset_label_position[1])
    export_moveset_label = button.TextButton('Export Moveset',25)
    export_moveset_label.inactivate()
    export_moveset_label.set_position(export_moveset_label_position)
    
    loaded = True

def unload():
    global loaded
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    global exit_button
    global export_moveset_label
    global import_movesets_label
    
    exit_button = None
    create_new_moveset_label = None
    edit_moveset_label = None
    delete_moveset_label = None
    moveset_select_container = None
    export_moveset_label = None
    import_movesets_label = None
    
    loaded = False

def handle_events():
    global loaded
    global exit_button
    global create_new_moveset_label
    global edit_moveset_label
    global delete_moveset_label
    global moveset_select_container
    global export_moveset_label
    global import_movesets_label
    global import_movesets_thread
    global import_alert_box
    
    if loaded == False:
        load()
    
    if import_movesets_thread == None:
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if exit_button.contains(wotsuievents.mouse_pos):
                exit_button.handle_selected()
            
            if create_new_moveset_label.contains(wotsuievents.mouse_pos):
                create_new_moveset_label.handle_selected()
            
            if import_movesets_label.contains(wotsuievents.mouse_pos):
                import_movesets_label.handle_selected()
            
            if (edit_moveset_label.contains(wotsuievents.mouse_pos) and
            edit_moveset_label.active):
                edit_moveset_label.handle_selected()
            
            if (delete_moveset_label.contains(wotsuievents.mouse_pos) and
            delete_moveset_label.active):
                delete_moveset_label.handle_selected()
            
            if (export_moveset_label.contains(wotsuievents.mouse_pos) and
            export_moveset_label.active):
                export_moveset_label.handle_selected()
        if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if exit_button.selected:
                exit_button.handle_deselected()
                
                if exit_button.contains(wotsuievents.mouse_pos):
                    gamestate.mode = gamestate.Modes.MAINMENU
                    unload()
            
            elif create_new_moveset_label.selected:
                create_new_moveset_label.handle_deselected()
                
                if create_new_moveset_label.contains(wotsuievents.mouse_pos):
                    splash.draw_loading_splash()
                    movesetbuilder.load(movesetdata.Moveset())
                    gamestate.mode = gamestate.Modes.MOVESETBUILDER
                    unload()
            
            elif import_movesets_label.selected:
                import_movesets_label.handle_deselected()
                
                if import_movesets_label.contains(wotsuievents.mouse_pos):
                    import_movesets_thread = Thread(
                        target=movesetdata.import_movesets
                    )
                    import_movesets_thread.start()
            
            elif edit_moveset_label.selected:
                edit_moveset_label.handle_deselected()
                
                if edit_moveset_label.contains(wotsuievents.mouse_pos):
                    splash.draw_loading_splash()
                    movesetbuilder.load(
                        moveset_select_container.selected_moveset
                    )
                    gamestate.mode = gamestate.Modes.MOVESETBUILDER
                    unload()
            
            elif delete_moveset_label.selected:
                delete_moveset_label.handle_deselected()
                
                if delete_moveset_label.contains(wotsuievents.mouse_pos):
                    movesetdata.delete_moveset(
                        moveset_select_container.selected_moveset
                    )
                    moveset_select_container.selected_moveset = None
                    moveset_select_container.load_movesets(
                        movesetdata.get_movesets()
                    )
            elif export_moveset_label.selected:
                export_moveset_label.handle_deselected()
                
                if export_moveset_label.contains(wotsuievents.mouse_pos):
                    movesetdata.export_moveset(
                        moveset_select_container.selected_moveset
                    )
    
    if loaded:
        exit_button.draw(gamestate.screen)
        edit_moveset_label.draw(gamestate.screen)
        create_new_moveset_label.draw(gamestate.screen)
        delete_moveset_label.draw(gamestate.screen)
        export_moveset_label.draw(gamestate.screen)
        import_movesets_label.draw(gamestate.screen)
        moveset_select_container.draw(gamestate.screen)
        
        if import_movesets_thread == None:
            moveset_select_container.handle_events()
            
        elif import_movesets_thread.is_alive() == True:
            import_alert_box.draw(gamestate.screen)
            
        elif import_movesets_thread.is_alive() == False:
            moveset_select_container.selected_moveset = None
            moveset_select_container.load_movesets(
                movesetdata.get_movesets()
            )
            import_movesets_thread = None
        
        if moveset_select_container.selected_moveset != None:
            if not edit_moveset_label.active:
                edit_moveset_label.activate()
            if not delete_moveset_label.active:
                delete_moveset_label.activate()
            if not export_moveset_label.active:
                export_moveset_label.activate()
        else:
            if edit_moveset_label.active:
                edit_moveset_label.inactivate()
            if delete_moveset_label.active:
                delete_moveset_label.inactivate()
            if export_moveset_label.active:
                export_moveset_label.inactivate()
