import pygame

import actionwizard
import gamestate
import animationexplorer
import button
import player

exit_button = button.ExitButton()
exit_indicator = False

class AttackTypeButton(button.TextButton):
    def __init__(self, attack_type, text, font_size=32):
        button.TextButton.__init__(self, text, font_size)
        self.attack_type = attack_type
    
    def handle_selected(self):
        global attack_type
        global slctd_attack_type_button
        button.Button.handle_selected(self)
        
        slctd_attack_type_button = self
        attack_type = self.attack_type

class SaveButton(button.TextButton):
    def __init__(self):
        button.TextButton.__init__(self, 'Save')
        self.saved_label = None
        self.draw_saved_label = False
    
    def draw(self, surface):
        button.TextButton.draw(self, surface)
        
        if self.draw_saved_label:
            self.saved_label.draw(surface)
    
    def handle_clicked(self):
        action_wizard.save_attack(attack_type, \
                                  slctd_attack_animation.name, \
                                  slctd_attack_animation)
        self.draw_saved_label = True
    
    def handle_deselected(self):
        button.Button.handle_deselected(self)
        self.draw_saved_label = False

#Visual elements
class attackbuilder():
    save_button = None
    labels = []
    attack_type_buttons = []
    animation_navigator = None
    slctd_attack_animation = None
    slctd_attack_type_button = None
    attack_type = None
    loaded = False

    def load():
        global attack_type_buttons
        global labels
        global save_button
        global animation_navigator
        global exit_indicator
        global loaded
        
        select_attack_type_label = button.Label((10,20), "Select attack type:", (255,255,255))
        labels.append(select_attack_type_label)
        
        punch_attack_type_button = AttackTypeButton(player.AttackTypes.PUNCH, "Punch", 20)
        punch_attack_type_button.pos = (20, 50)
        attack_type_buttons.append(punch_attack_type_button)
        
        kick_attack_type_button = AttackTypeButton(player.AttackTypes.KICK, "Kick", 20)
        kick_attack_type_button.pos = (130, 50)
        attack_type_buttons.append(kick_attack_type_button)
        
        select_animation_label = button.Label((10,100), "Select animation:", (255,255,255))
        labels.append(select_animation_label)
        
        animation_navigator = animationexplorer.AnimationNavigator()
        animation_navigator.load_data((10,130), \
                                      100, \
                                      gamestate._WIDTH - 20, \
                                      animationexplorer.animations.values(), \
                                      gamestate.Modes.ATTACKBUILDER)
        
        save_button = SaveButton()
        save_button.pos = (10, 250)
        saved_button_label_pos = (save_button.pos[0], save_button.pos[1] + save_button.height)
        save_button.saved_label = button.Label(saved_button_label_pos, 'Attack Saved!', (255,255,255))
        
        exit_indicator = False
        gamestate.mode = gamestate.Modes.ATTACKBUILDER
        
        loaded = True

    def unload():
        global labels
        global attack_type_buttons
        global animation_navigator
        global slctd_attack_animation
        global attack_type
        global save_button
        global loaded
        
        labels = []
        attack_type_buttons = []
        animation_navigator = None
        slctd_attack_animation = None
        attack_type = None
        save_button = None
        
        loaded = False

    def handle_events():
        global exit_indicator
        
        if loaded == False:
            load()
        
        if animation_navigator.contains(gamestate.mouse_pos):
            animation_navigator.handle_events()
            slctd_attack_animation = animation_navigator.slctd_animation
        else:
            if pygame.MOUSEBUTTONDOWN in gamestate.event_types:
                if exit_button.contains(gamestate.mouse_pos):
                    exit_button.selected = True
                    exit_button.color = button.Button._SlctdColor
                    exit_button.symbol.color = button.Button._SlctdColor
                elif save_button.contains(gamestate.mouse_pos):
                    save_button.handle_selected()
                else:
                    for attack_type_button in attack_type_buttons:
                        if attack_type_button.contains(gamestate.mouse_pos):
                            attack_type_button.handle_selected()
                        elif slctd_attack_type_button != attack_type_button:
                            attack_type_button.handle_deselected()
                    
            elif pygame.MOUSEBUTTONUP in gamestate.event_types:
                if exit_button.selected:
                    exit_button.selected = False
                    exit_button.color = button.Button._InactiveColor
                    exit_button.symbol.color = button.Button._InactiveColor
                    
                    if exit_button.contains(gamestate.mouse_pos):
                        exit_indicator = True
                
                if save_button.selected:
                    if save_button.contains(gamestate.mouse_pos):
                        save_button.handle_clicked()
                    else: 
                        save_button.handle_deselected()
        
        if exit_indicator:
            exit_indicator = False
            gamestate.mode = gamestate.Modes.SETTINGSMODE
            unload()
        else:
            for label in labels:
                label.draw(gamestate.screen)
            
            for attack_type_button in attack_type_buttons:
                attack_type_button.draw(gamestate.screen)
            
            save_button.draw(gamestate.screen)
            
            animation_navigator.draw(gamestate.screen, gamestate.mouse_pos)
            exit_button.draw(gamestate.screen)