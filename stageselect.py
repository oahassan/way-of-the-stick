import os
from glob import glob

import pygame

import wotsuievents
import stage
import button
import gamestate
import versusmode
import splash
import versusmovesetselect
from stageselectui import StageSelector, StartMatchLabel, SelectStageBackground

loaded = False
exit_button = None
UI_objects = None

class StageSelectUI():
    def __init__(self, stages):
        self.background = None
        self.stage_selector = StageSelector(stages, (250, 50))
        self.title_label = button.Label((10,15), "Select Stage", (255,255,255))
        self.start_match_label = StartMatchLabel()
        self.start_match_label_draw_timer = 0
        self.start_match_label_draw_timeout = 2000
    
    def stage_selected(self):
        return self.stage_selector.selected_thumbnail != None

def load():
    global loaded
    global exit_button
    global UI_objects
    
    exit_button = button.ExitButton()
    loaded = True
    
    if UI_objects == None:
        UI_objects = StageSelectUI(get_stage_data())
    
    UI_objects.background = SelectStageBackground(versusmovesetselect.create_player_data())
    
def unload():
    global loaded
    global exit_button
    
    exit_button = None
    loaded = False

def clear_data():
    global UI_objects
    
    UI_objects = None

def get_stage_data():
    stage_list = []
    
    for file_path in glob(os.path.join(".", stage.STAGE_DIR_NM, "*.stg")):
        if os.path.isfile(file_path):
            
            try:
                loaded_stage = stage.load_from_JSON(file_path)
                stage_list.append(loaded_stage)
            except:
                print("unable to load stage: " + file_path)
    
    if len(stage_list) == 0:
        stage_list.append(stage.load_default_stage())
    
    return stage_list

def handle_events():
    global UI_objects
    global loaded
    global exit_button
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                unload()
                clear_data()
    
    if loaded:
        gamestate.screen.blit(UI_objects.background.surface, (0,0))
        exit_button.draw(gamestate.screen)
        UI_objects.stage_selector.draw(gamestate.screen)
        UI_objects.title_label.draw(gamestate.screen)
        UI_objects.stage_selector.handle_events()
        
        if UI_objects.stage_selected():
            if UI_objects.start_match_label_draw_timer >= UI_objects.start_match_label_draw_timeout:
                UI_objects.start_match_label.draw(gamestate.screen)
            else:
                UI_objects.start_match_label_draw_timer += gamestate.time_passed
            
            if ((UI_objects.stage_selector.contains(wotsuievents.mouse_pos) and
            pygame.MOUSEMOTION in wotsuievents.event_types) or 
            pygame.K_UP in wotsuievents.keys_pressed or
            pygame.K_DOWN in wotsuievents.keys_pressed):
               UI_objects.start_match_label_draw_timer = 0
               UI_objects.start_match_label.hide() 
            
            if (pygame.K_KP_ENTER in wotsuievents.keys_pressed or 
            pygame.K_RETURN in wotsuievents.keys_pressed):
                gamestate.screen.fill((0,0,0))
                splash.draw_loading_splash()
                
                gamestate.stage = UI_objects.stage_selector.selected_thumbnail.stage
                player_data = versusmovesetselect.create_player_data()
                
                versusmode.init(player_data)
                
                #versusmode.local_state.init_recording(
                #    player1_moveset_select.selected_moveset.name,
                #    player2_moveset_select.selected_moveset.name
                #)
                
                unload()
                gamestate.mode = gamestate.Modes.VERSUSMODE
        else:
            UI_objects.start_match_label_draw_timer = 0            
            UI_objects.start_match_label.hide()
