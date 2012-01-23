import pygame

import wotsuievents
import button
import gamestate
import stage

start_position = (20,gamestate._HEIGHT)
label_groups = []
exit_button = button.ExitButton()

def get_group_height(label_group):
    return label_group[-1].bottom_right()[1] - label_group[0].position[1]

def get_stage_group_labels(next_position):
    stage_credits_data = stage.get_stage_credits()
    stage_group = []
    
    for credit_data in stage_credits_data:
        if "creator" in credit_data:
            stage_group.append(
                button.Label(
                    next_position,
                    credit_data["name"],
                    (255,255,255),
                    button.FONT_SIZES[5]
                )
            )
            
            next_position = (
                start_position[0] + 10, 
                next_position[1] + stage_group[-1].height + 5
            )
            
            stage_group.append(
                button.Label(
                    next_position,
                    "Creator: " + credit_data["creator"],
                    (255,255,255),
                    button.FONT_SIZES[4]
                )
            )
            
            next_position = (
                start_position[0] + 10, 
                next_position[1] + stage_group[-1].height + 5
            )
            
            if "art" in credit_data:
                stage_group.append(
                    button.Label(
                        next_position,
                        "Art: " + credit_data["art"],
                        (255,255,255),
                        button.FONT_SIZES[4]
                    )
                )
                
                next_position = (
                    start_position[0] + 10, 
                    next_position[1] + stage_group[-1].height + 5
                )
            
            if "music" in credit_data:
                stage_group.append(
                    button.Label(
                        next_position,
                        "Music: " + credit_data["music"],
                        (255,255,255),
                        button.FONT_SIZES[4]
                    )
                )
                
                next_position = (
                    start_position[0] + 10, 
                    next_position[1] + stage_group[-1].height + 5
                )
            
            next_position = (
                start_position[0], 
                stage_group[-1].position[1] + stage_group[-1].height + 10
            )
    
    return stage_group

created_group = []
created_group.append(
    button.Label(
        start_position,
        "Created By: Wale Hassan",
        (255,255,255),
        button.FONT_SIZES[6]
    )
)
label_groups.append(created_group)

next_position = (start_position[0], start_position[1] + get_group_height(created_group) + 20)

sound_effects_group = []
sound_effects_group.append(
    button.Label(
        next_position,
        "Sound Effects By: Wale Hassan",
        (255,255,255),
        button.FONT_SIZES[6]
    )
)
label_groups.append(sound_effects_group)

next_position = (start_position[0], next_position[1] + get_group_height(sound_effects_group) + 20)

music_group = []
music_group.append(
    button.Label(
        next_position,
        "Music",
        (255,255,255),
        button.FONT_SIZES[6]
    )
)

next_position = (start_position[0], next_position[1] + music_group[-1].height + 10)

music_group.append(
    button.Label(
        next_position,
        "'Mist of Battle' by Logical Defiance of www.newgrounds.com",
        (255,255,255),
        button.FONT_SIZES[5]
    )
)
label_groups.append(music_group)

next_position = (start_position[0], next_position[1] + music_group[-1].height + 20)

stages_group = []
stages_group.append(
    button.Label(
        next_position,
        "Stages",
        (255,255,255),
        button.FONT_SIZES[6]
    )
)
next_position = (start_position[0], next_position[1] + stages_group[-1].height + 10)

stages_group.extend(get_stage_group_labels(next_position))
label_groups.append(stages_group)

next_position = (start_position[0], stages_group[-1].bottom_right()[1] + 20)

libraries_group = []
libraries_group.append(
    button.Label(
        next_position,
        "Libraries",
        (255,255,255),
        button.FONT_SIZES[6]
    )
)
next_position = (start_position[0], next_position[1] + libraries_group[-1].height + 10)

libraries_group.append(
    button.Label(
        next_position,
        "Pygame",
        (255,255,255),
        button.FONT_SIZES[5]
    )
)
next_position = (start_position[0], next_position[1] + libraries_group[-1].height + 10)

libraries_group.append(
    button.Label(
        next_position,
        "PodSixNet by Chris McCormick",
        (255,255,255),
        button.FONT_SIZES[5]
    )
)
next_position = (start_position[0], next_position[1] + libraries_group[-1].height + 10)
label_groups.append(libraries_group)

def shift_labels():
    global label_groups
    y_shift = -1
    
    if label_groups[-1][-1].position[1] < 0:
        y_shift = gamestate._HEIGHT - label_groups[0][0].position[1]
    
    for group in label_groups:
        for label in group:
            label.shift(0, y_shift)

def handle_events():
    global label_groups
    global exit_button
    
    shift_labels()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
    
    for group in label_groups:
        for label in group:
            label.draw(gamestate.screen)
    
    exit_button.draw(gamestate.screen)
