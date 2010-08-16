import pygame

import actionwizard
import gamestate
import animationexplorer
import button
import player

exit_button = button.ExitButton()
exit_indicator = False

save_attack_button = None
save_movement_button = None
labels = []
attack_type_buttons = []
movement_type_buttons = []
attack_navigator = None
movement_navigator = None
slctd_attack_animation = None
slctd_movement_animation = None
slctd_attack_type_button = None
slctd_movement_type_button = None
attack_type = None
movement_type = None
loaded = False

class MoveTypeButton(button.TextButton):
    def __init__(self, move_type, text, font_size=32):
        button.TextButton.__init__(self, text, font_size)
        self.move_type = move_type

class SaveButton(button.TextButton):
    SAVE_ATTACK = "SAVE_ATTACK"
    SAVE_MOVEMENT = "SAVE_MOVEMENT"
    
    def __init__(self, save_type):
        button.TextButton.__init__(self, 'Save')
        self.saved_label = None
        self.draw_saved_label = False
        self.save_type = save_type
    
    def draw(self, surface):
        button.TextButton.draw(self, surface)
        
        if self.draw_saved_label:
            self.saved_label.draw(surface)
    
    def handle_clicked(self, animation, move_type):
        if self.save_type == SaveButton.SAVE_ATTACK:
            if ((animation != None) and
                (move_type != None)):
                actionwizard.save_attack(move_type, \
                                         animation)
                self.draw_saved_label = True
        elif self.save_type == SaveButton.SAVE_MOVEMENT:
            if ((animation != None) and
                (move_type != None)):
                actionwizard.save_movement(move_type, \
                                           animation)
                if move_type in player.PlayerStates.UNBOUND_ACTIONS:
                    actionwizard.save_unbound_action(move_type, \
                                                     animation)
                self.draw_saved_label = True
    
    def handle_deselected(self):
        button.Button.handle_deselected(self)
        self.draw_saved_label = False

def load():
    global attack_type_buttons
    global movement_type_buttons
    global labels
    global save_attack_button
    global save_movement_button
    global attack_navigator
    global movement_navigator
    global exit_indicator
    global loaded
    
    select_attack_type_label = button.Label((10,10), "Select attack type:", (255,255,255))
    labels.append(select_attack_type_label)
    
    punch_attack_type_button = MoveTypeButton(player.AttackTypes.PUNCH, "Punch", 20)
    punch_attack_type_button.pos = (20, 40)
    attack_type_buttons.append(punch_attack_type_button)
    
    kick_attack_type_button = MoveTypeButton(player.AttackTypes.KICK, "Kick", 20)
    kick_attack_type_button.pos = (130, 40)
    attack_type_buttons.append(kick_attack_type_button)
    
    select_animation_label = button.Label((10,90), "Select animation:", (255,255,255))
    labels.append(select_animation_label)
    
    attack_navigator = animationexplorer.AnimationNavigator()
    attack_navigator.load_data((10,120), \
                                  100, \
                                  gamestate._WIDTH - 20, \
                                  animationexplorer.get_animations().values(), \
                                  gamestate.Modes.MOVEBUILDER)
    
    save_attack_button = SaveButton(SaveButton.SAVE_ATTACK)
    save_attack_button.pos = (10, 220)
    saved_attack_label_pos = (save_attack_button.pos[0], save_attack_button.pos[1] + save_attack_button.height)
    save_attack_button.saved_label = button.Label(saved_attack_label_pos, "Attack Saved!", (255,255,255))
    
    select_movement_type_label = button.Label((10,300), "Select movement type:", (255,255,255))
    labels.append(select_movement_type_label)
    
    walk_movement_type_button = MoveTypeButton(player.PlayerStates.WALKING, "Walk", 20)
    walk_movement_type_button.pos = (10, 330)
    movement_type_buttons.append(walk_movement_type_button)
    
    run_movement_type_button = MoveTypeButton(player.PlayerStates.RUNNING, "Run", 20)
    run_movement_type_button.pos = (110, 330)
    movement_type_buttons.append(run_movement_type_button)
    
    jump_movement_type_button = MoveTypeButton(player.PlayerStates.JUMPING, "Jump", 20)
    jump_movement_type_button.pos = (210, 330)
    movement_type_buttons.append(jump_movement_type_button)
    
    crouch_movement_type_button = MoveTypeButton(player.PlayerStates.CROUCHING, "Crouch", 20)
    crouch_movement_type_button.pos = (310, 330)
    movement_type_buttons.append(crouch_movement_type_button)
    
    rest_movement_type_button = MoveTypeButton(player.PlayerStates.STANDING, "Stand", 20)
    rest_movement_type_button.pos = (410, 330)
    movement_type_buttons.append(rest_movement_type_button)
    
    float_movement_type_button = MoveTypeButton(player.PlayerStates.FLOATING, "Float", 20)
    float_movement_type_button.pos = (510, 330)
    movement_type_buttons.append(float_movement_type_button)
    
    land_movement_type_button = MoveTypeButton(player.PlayerStates.LANDING, "Land", 20)
    land_movement_type_button.pos = (610, 330)
    movement_type_buttons.append(land_movement_type_button)
    
    stunned_movement_type_button = MoveTypeButton(player.PlayerStates.STUNNED, "Stunned", 20)
    stunned_movement_type_button.pos = (710, 330)
    movement_type_buttons.append(stunned_movement_type_button)
    
    select_animation_label = button.Label((10,380), "Select animation:", (255,255,255))
    labels.append(select_animation_label)
    
    movement_navigator = animationexplorer.AnimationNavigator()
    movement_navigator.load_data((10,410), \
                                  100, \
                                  gamestate._WIDTH - 20, \
                                  animationexplorer.get_animations().values(), \
                                  gamestate.Modes.MOVEBUILDER)
    
    save_movement_button = SaveButton(SaveButton.SAVE_MOVEMENT)
    save_movement_button.pos = (10, 510)
    saved_movement_label_pos = (save_movement_button.pos[0], save_movement_button.pos[1] + save_movement_button.height)
    save_movement_button.saved_label = button.Label(saved_movement_label_pos, "Movement Saved!", (255,255,255))

    
    exit_indicator = False
    gamestate.mode = gamestate.Modes.MOVEBUILDER
    
    loaded = True

def unload():
    global labels
    global attack_type_buttons
    global movement_type_buttons
    global attack_navigator
    global movement_navigator
    global slctd_attack_animation
    global slctd_movement_animation
    global attack_type
    global movement_type
    global save_attack_button
    global save_movement_button
    global loaded
    global slctd_attack_type_button
    global slctd_movement_type_button
    
    labels = []
    attack_type_buttons = []
    movement_type_buttons = []
    attack_navigator = None
    movement_navigator = None
    slctd_attack_animation = None
    slctd_movement_animation = None
    attack_type = None
    movement_type = None
    save_attack_button = None
    save_movement_button = None
    slctd_attack_type_button = None
    slctd_movement_type_button = None
    
    loaded = False

def handle_events():
    global exit_indicator
    global slctd_attack_type_button
    global slctd_movement_type_button
    global slctd_attack_animation
    global slctd_movement_animation
    global attack_type
    global movement_type
    
    if loaded == False:
        load()
    
    attack_navigator.handle_events()
    slctd_attack_animation = attack_navigator.slctd_animation
    
    movement_navigator.handle_events()
    slctd_movement_animation = movement_navigator.slctd_animation
    
    if pygame.MOUSEBUTTONDOWN in gamestate.event_types:
        if exit_button.contains(gamestate.mouse_pos):
            exit_button.selected = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
        elif save_attack_button.contains(gamestate.mouse_pos):
            if ((slctd_attack_type_button != None) and
                (slctd_attack_animation != None)):
                attack_type = slctd_attack_type_button.move_type
                save_attack_button.handle_selected()
        elif save_movement_button.contains(gamestate.mouse_pos):
            if ((slctd_movement_type_button != None) and
                (slctd_movement_animation != None)):
                movement_type = slctd_movement_type_button.move_type
                save_movement_button.handle_selected()
        else:
            for attack_type_button in attack_type_buttons:
                if attack_type_button.contains(gamestate.mouse_pos):
                    if slctd_attack_type_button != None:
                        slctd_attack_type_button.handle_deselected()
                    
                    attack_type_button.handle_selected()
                    slctd_attack_type_button = attack_type_button
                    attack_type = attack_type_button.move_type
            
            for movement_type_button in movement_type_buttons:
                if movement_type_button.contains(gamestate.mouse_pos):
                    if slctd_movement_type_button != None:
                        slctd_movement_type_button.handle_deselected()
                    
                    movement_type_button.handle_selected()
                    slctd_movement_type_button = movement_type_button
                    movement_type = movement_type_button.move_type
    elif pygame.MOUSEBUTTONUP in gamestate.event_types:
        if exit_button.selected:
            exit_button.selected = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(gamestate.mouse_pos):
                exit_indicator = True
        
        if save_attack_button.selected:
            if save_attack_button.contains(gamestate.mouse_pos):
                save_attack_button.handle_clicked(slctd_attack_animation, attack_type)
            else: 
                save_attack_button.handle_deselected()
        
        if save_movement_button.selected:
            if save_movement_button.contains(gamestate.mouse_pos):
                save_movement_button.handle_clicked(slctd_movement_animation, movement_type)
            else: 
                save_movement_button.handle_deselected()

    if exit_indicator:
        exit_indicator = False
        gamestate.mode = gamestate.Modes.SETTINGSMODE
        unload()
    elif gamestate.mode != gamestate.Modes.MOVEBUILDER:
        unload()
    else:
        for label in labels:
            label.draw(gamestate.screen)
        
        for attack_type_button in attack_type_buttons:
            attack_type_button.draw(gamestate.screen)
        
        for movement_type_button in movement_type_buttons:
            movement_type_button.draw(gamestate.screen)
        
        save_attack_button.draw(gamestate.screen)
        save_movement_button.draw(gamestate.screen)
        
        attack_navigator.draw(gamestate.screen, gamestate.mouse_pos)
        movement_navigator.draw(gamestate.screen, gamestate.mouse_pos)
        
        exit_button.draw(gamestate.screen)