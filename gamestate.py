import pygame

_WIDTH = 800
_HEIGHT = 600

class Modes():
    FRAMEEDITOR = 'FRAMEEDITOR'
    ANIMATIONEXPLORER = 'ANIMATIONEXPLORER'
    MAINMENU = 'MAINMENU'
    VERSUSMODE = 'VERSUSMODE'
    SETTINGSMODE = 'SETTINGSMODE'
    MOVEBUILDER = 'MOVEBUILDER'
    MOVESETBUILDER = 'MOVESETBUILDER'
    KEYBINDING = 'KEYBINDING'
    MOVESETSELECT = 'MOVESETSELECT'
    VERSUSMOVESETSELECT = 'VERSUSMOVESETSELECT'
    ONLINEVERSUSMODE = 'ONLINEVERSUSMODE'
    ONLINEVERSUSMOVESETSELECT = 'ONLINEVERSUSMOVESETSELECT'
    ONLINEMENUPAGE = 'ONLINEMENUPAGE'
    ONLINEMATCHLOADER = 'ONLINEMATCHLOADER'
    CONTROLSPAGE = 'CONTROLSPAGE'

class DrawingModes():
    DIRTY_RECTS = 'DIRTY_RECTS'
    UPDATE_ALL = 'UPDATE_ALL'

stage = None

frame_rate = 20

drawing_mode = DrawingModes.UPDATE_ALL
mode = Modes.MAINMENU
animation = None

screen = pygame.display.set_mode((_WIDTH, _HEIGHT))
clock = pygame.time.Clock()

old_dirty_rects = []
new_dirty_rects = []

hosting = False

def clear_old_dirty_rects():
    global old_dirty_rects
    
    old_dirty_rects = []

def clear_new_dirty_rects():
    global new_dirty_rects
    
    new_dirty_rects = []

def update_screen():
    global old_dirty_rects
    global new_dirty_rects
    
    pygame.display.update(old_dirty_rects)
    pygame.display.update(new_dirty_rects)
    old_dirty_rects = new_dirty_rects
    new_dirty_rects = []

def collapse_new_dirty_rects():
    global old_dirty_rects
    global new_dirty_rects
    
    collapsed_rects = []
    rect_to_overlapping_rects = {}
    rect_to_rect_groups = {}
    combined_indices = []
    
    for index in range(len(new_dirty_rects)):
        current_rect = new_dirty_rects[index]
        
        if index in rect_to_rect_groups.keys():
            pass
        else:
            other_rects = [other_rect for other_rect in new_dirty_rects if other_rect != current_rect]
            
            overlapping_rects = [other_rects[rect_index] for rect_index in current_rect.collidelistall(other_rects)]
            current_rect_added_indicator = False
            
            for rect in overlapping_rects:
                rect_index = new_dirty_rects.index(rect)
                
                if rect_index in rect_to_rect_groups.keys():
                    #add current rect to existing group
                    collapsed_rect_index = rect_to_rect_groups[rect_index]
                    collapsed_rects[collapsed_rect_index].union_ip(current_rect)
                    collapsed_rects[collapsed_rect_index].unionall_ip(overlapping_rects)
                    
                    #add any other overlapping rects to the existing group
                    for overlapping_rect in overlapping_rects:
                        overlapping_rect_index = new_dirty_rects.index(overlapping_rect)
                        rect_to_rect_groups[overlapping_rect_index] = collapsed_rect_index
                    
                    current_rect_added_indicator = True
                    break
            
            if current_rect_added_indicator == False:
                collapsed_rect = current_rect.unionall(overlapping_rects)
                
                collapsed_rects.append(collapsed_rect)
                rect_to_rect_groups[index] = len(collapsed_rects) - 1
                
                for rect in other_rects:
                    rect_index = new_dirty_rects.index(rect)
                    rect_to_rect_groups[rect_index] = len(collapsed_rects) - 1
    
    new_dirty_rects = collapsed_rects
