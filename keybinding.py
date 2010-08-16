import pygame

import gamestate
import actionwizard
import player
import button
import animationexplorer

exit_button = button.ExitButton()
exit_indicator = False
loaded = False
binding_builder = None
binding_type_buttons = []
BINDING_TYPE_BUTTONS_POS = (10,10)
selected_binding_type_button = None

class BindTypes():
    MOVE_LEFT = "MOVE_LEFT"
    MOVE_RIGHT = "MOVE_RIGHT"
    JUMP = "JUMP"
    CROUCH = "CROUCH"
    ATTACK = "ATTACK"

class BindButton(button.TextButton):
    def __init__(self, action_types):
        button.TextButton.__init__(self, "Bind Key")
        self.action_types = action_types
        self.key = None
        self.animations = {}
        self.show_label = False
    
    def handle_clicked(self):
        if self.animations_set():
            for action_type in self.action_types:
                animation = self.animations[action_type]
                self.bind_action(action_type, animation)
            self.show_label = True
    
    def handle_deselected(self):
        button.Button.handle_deselected(self)
        self.show_label = False
    
    def animations_set(self):
        return_indicator = True
        
        for action_type in self.action_types:
            if ((action_type not in self.animations) or
                (self.animations[action_type] == None)):
                return_indicator = False
        
        return return_indicator
    
    def draw(self, surface):
        button.TextButton.draw(self, surface)
        
        if self.show_label:
            label_pos = (self.pos[0], \
                         self.pos[1] + self.height + button.TextButton.TEXT_PADDING)
            text_surface = self.font.render(pygame.key.name(self.key) + " Bound!", 1, self.color)
        
            surface.blit(text_surface, label_pos)

class BindDirectionalActionButton(BindButton):
    def __init__(self, action_types, direction):
        BindButton.__init__(self, action_types)
        self.direction = direction
    
    def bind_action(self, action_type, animation):
        actionwizard.save_binding(action_type, self.key, animation, self.direction)

class BindBiDirectionalActionButton(BindButton):
    def bind_action(self, action_type, animation):
        actionwizard.save_binding(action_type, self.key, animation)

class BindTypeButton(button.TextButton):
    def __init__(self, text, bind_type, action_types):
        button.TextButton.__init__(self, text, 20)
        self.bind_type = bind_type
        self.action_types = action_types

class BindingBuilder():
    def __init__(self):
        self.animation_navigators = {}
        self.animation_navigator_labels = {}
        self.key_selector = None
        self.bind_button = None
    
    def draw(self, surface):
        for navigator in self.animation_navigators.values():
            navigator.draw(surface, gamestate.mouse_pos)
        
        for label in self.animation_navigator_labels.values():
            label.draw(surface)
        
        self.key_selector.draw(surface)
        self.bind_button.draw(surface)
    
    def handle_events(self):
        for navigator in self.animation_navigators.values():
            navigator.handle_events()
        
        if pygame.MOUSEBUTTONDOWN in gamestate.event_types:
            if self.key_selector.contains(gamestate.mouse_pos):
                self.key_selector.handle_selected()
            elif self.key_selector.selected:
                self.key_selector.handle_deselected()
                
            if self.bind_button.contains(gamestate.mouse_pos):
                self.bind_button.handle_selected()
            elif self.key_selector.selected:
                self.bind_button.handle_deselected()
            
        elif pygame.MOUSEBUTTONUP in gamestate.event_types:
            if self.bind_button.contains(gamestate.mouse_pos):
                self.bind_button.handle_clicked()
        
        if ((self.key_selector.selected) and 
            (len(gamestate.keys_pressed) > 0)):
            self.key_selector.key = gamestate.keys_pressed[0]
            self.key_selector.handle_deselected()
        
        self.bind_button.key = self.key_selector.key
        
        for action_type, navigator in self.animation_navigators.iteritems():
            self.bind_button.animations[action_type] = navigator.slctd_animation
    
    def load(self, bind_type, action_types, pos):
        self.__init__()
        
        self.key_selector = KeySelector()
        self.key_selector.pos = pos
        
        action_navigator_pos = (pos[0], pos[1] + self.height() + 10)
        
        for action_type in action_types:
            self.add_action_navigator(action_type, action_navigator_pos)
            action_navigator_pos = (pos[0], pos[1] + self.height() + 10)
        
        bind_button_pos = (pos[0], pos[1] + self.height() + 10)
        
        if bind_type == BindTypes.MOVE_LEFT:
            self.bind_button = BindDirectionalActionButton(action_types, \
                                                           player.PlayerStates.FACING_LEFT)
        elif bind_type == BindTypes.MOVE_RIGHT:
            self.bind_button = BindDirectionalActionButton(action_types, \
                                                           player.PlayerStates.FACING_RIGHT)
        else:
            self.bind_button = BindBiDirectionalActionButton(action_types)
        
        self.bind_button.pos = bind_button_pos
        
    def height(self):
        return_height = 0
        
        if self.key_selector != None:
            return_height += self.key_selector.height
        
        for action_type, navigator in self.animation_navigators.iteritems():
            return_height += (10 + 
                              navigator.height + \
                              self.animation_navigator_labels[action_type].height)
        
        if self.bind_button != None:
            return_height += 10 + self.bind_button.height
        
        return return_height
    
    def get_label_text(self, action_type):
        label_text = ""
        
        if action_type == player.PlayerStates.WALKING:
            label_text = "Select Walk Animation:"
        elif action_type == player.PlayerStates.RUNNING:
            label_text = "Select Run Animation:"
        elif action_type == player.PlayerStates.JUMPING:
            label_text = "Select Jump Animation:"
        elif action_type == player.PlayerStates.CROUCHING:
            label_text = "Select Crouch Animation:"
        elif action_type == player.AttackTypes.PUNCH:
            label_text = "Select Punch Animation:"
        elif action_type == player.AttackTypes.KICK:
            label_text = "Select Kick Animation:"
        
        return label_text
    
    def add_action_navigator(self, action_type, label_pos):
        label = button.Label(label_pos, self.get_label_text(action_type), (255,255,255))
        self.animation_navigator_labels[action_type] = label
        
        animations = None
        
        if action_type in player.AttackTypes.ATTACK_TYPES:
            animations = actionwizard.get_attack_animations(action_type)
        else:
            animations = actionwizard.get_movement_animations(action_type)
        
        animation_navigator = animationexplorer.AnimationNavigator()
        animation_navigator.load_data((label_pos[0] + 10, label_pos[1] + 10 + label.height), \
                                      100, \
                                      gamestate._WIDTH - 20, \
                                      animations, \
                                      gamestate.Modes.KEYBINDING)
        
        self.animation_navigators[action_type] = animation_navigator

class KeySelector(button.TextButton):
    def __init__(self):
        button.TextButton.__init__(self, "Select Key")
        self.key = None
    
    def draw(self, surface):
        button.TextButton.draw(self, surface)
        
        if self.key != None:
            key_name_pos = (self.pos[0] + self.width + button.TextButton.TEXT_PADDING, \
                            self.pos[1] + button.TextButton.TEXT_PADDING)
            text_surface = self.font.render(pygame.key.name(self.key), 1, self.color)
        
            surface.blit(text_surface, key_name_pos)
        
def load():
    global binding_type_buttons
    global loaded
    
    binding_type_buttons.append(BindTypeButton("Move Left", \
                                               BindTypes.MOVE_LEFT, \
                                               [player.PlayerStates.WALKING, \
                                                player.PlayerStates.RUNNING]))
    binding_type_buttons.append(BindTypeButton("Move Right", \
                                               BindTypes.MOVE_RIGHT, \
                                               [player.PlayerStates.WALKING, \
                                                player.PlayerStates.RUNNING]))
    binding_type_buttons.append(BindTypeButton("Jump", \
                                               BindTypes.JUMP, \
                                               [player.PlayerStates.JUMPING]))
    binding_type_buttons.append(BindTypeButton("Crouch", \
                                               BindTypes.CROUCH, \
                                               [player.PlayerStates.CROUCHING]))
    binding_type_buttons.append(BindTypeButton("Punch", \
                                               BindTypes.ATTACK, \
                                               [player.AttackTypes.PUNCH]))
    binding_type_buttons.append(BindTypeButton("Kick", \
                                               BindTypes.ATTACK, \
                                               [player.AttackTypes.KICK]))
    
    layout_binding_type_buttons(binding_type_buttons)
    
    loaded = True

def layout_binding_type_buttons(binding_type_buttons):
    
    button_pos = (BINDING_TYPE_BUTTONS_POS[0], BINDING_TYPE_BUTTONS_POS[1])
    
    for binding_type_button in binding_type_buttons:
        binding_type_button.pos = button_pos
        button_pos = (button_pos[0] + binding_type_button.width + 10, button_pos[1])

def unload():
    global binding_builder
    global binding_type_buttons
    global loaded
    
    binding_builder = None
    
    binding_type_buttons = []
    
    loaded = False

def handle_events():
    global exit_indicator
    global binding_type_buttons
    global binding_builder
    global loaded
    global selected_binding_type_button
    
    if loaded == False:
        load()
    
    if binding_builder != None:
        binding_builder.handle_events()
    
    if pygame.MOUSEBUTTONDOWN in gamestate.event_types:
        if exit_button.contains(gamestate.mouse_pos):
            exit_button.selected = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
        
        for binding_type_button in binding_type_buttons:
            if binding_type_button.contains(gamestate.mouse_pos):   
                binding_type_button.handle_selected()
                
                if binding_builder == None:
                    binding_builder = BindingBuilder()
                
                if selected_binding_type_button != None:
                    selected_binding_type_button.handle_deselected()
                
                selected_binding_type_button = binding_type_button
                
                binding_builder.load(binding_type_button.bind_type, \
                                     binding_type_button.action_types, \
                                     (10, 70))
                
    elif pygame.MOUSEBUTTONUP in gamestate.event_types:
        if exit_button.selected:
            exit_button.selected = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(gamestate.mouse_pos):
                exit_indicator = True

    if exit_indicator:
        exit_indicator = False
        gamestate.mode = gamestate.Modes.SETTINGSMODE
        unload()
    else:
        exit_button.draw(gamestate.screen)
        
        if binding_builder != None:
            binding_builder.draw(gamestate.screen)
        
        for binding_type_button in binding_type_buttons:
            binding_type_button.draw(gamestate.screen)