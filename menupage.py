import pygame

import button
import gamestate
import wotsuievents

class MenuButton(button.TextButton):
    def __init__(self, text, gamestate_mode, font_size=32):
        button.TextButton.__init__(self, text, font_size)
        self.gamestate_mode = gamestate_mode
    
    def handle_select(self):
        """changes state of button when it is clicked"""
        self.color = button.Button._SlctdColor
        self.symbol.color = button.Button._SlctdColor
        self.selected = True
    
    def handle_deselect(self, change_state):
        """changes state of button when it is clicked"""
        self.color = button.Button._InactiveColor
        self.symbol.color = button.Button._InactiveColor
        self.selected = False
        
        if change_state:
            if ((pygame.MOUSEBUTTONUP in wotsuievents.event_types) and 
                (self.contains(wotsuievents.mouse_pos))):
                gamestate.mode = self.gamestate_mode
            elif pygame.K_RETURN in wotsuievents.keys_released:
                gamestate.mode = self.gamestate_mode

def draw(surface):
    """draws the menu on to the given surface"""
    
    for menu_button in main_menu_buttons:
        menu_button.draw(surface)

def get_selected_button():
    global main_menu_buttons
    
    slctd_button = None
    for button in main_menu_buttons:
        if button.selected:
            slctd_button = button
    
    return slctd_button

def get_mouse_over_button():
    global main_menu_buttons
    
    rtn_button = None
    for button in main_menu_buttons:
        if button.contains(wotsuievents.mouse_pos):
            rtn_button = button
    
    return rtn_button
    
def get_menu_height():
    rtn_height = 0
    
    for button in main_menu_buttons:
        rtn_height += button.height
        rtn_height += MENU_BUTTON_PADDING
    
    return rtn_height

def get_menu_width():
    menu_width = 0
    
    for button in main_menu_buttons:
        menu_width = max(menu_width, button.width)
    
    return menu_width
    
def get_menu_pos():
    """returns a position that centers the menu in the middle of the 
    screen"""
    menu_height = get_menu_height()
    menu_width = get_menu_width()
    
    x_pos = (gamestate._WIDTH / 2) - (menu_width / 2)
    y_pos = (gamestate._HEIGHT / 2) - (menu_height / 2)
    
    return (x_pos, y_pos)

def get_menu_button_x_pos(menu_button):
    """returns a position that centers the button in the middle of the 
    screen"""
    return (gamestate._WIDTH / 2) - (menu_button.width / 2)

MENU_BUTTON_PADDING = 20

main_menu_buttons = []
menu_button_index = 0
menu_pos = None

def load():
    versus_mode_button = MenuButton('Versus Mode', \
                                    gamestate.Modes.VERSUSMOVESETSELECT)
    move_set_builder_button = MenuButton('Move Set Builder', \
                                         gamestate.Modes.MOVESETSELECT)
    
    main_menu_buttons.append(versus_mode_button)
    main_menu_buttons.append(move_set_builder_button)
    
    menu_button_index = 0
    menu_pos = get_menu_pos()
    menu_button_y_pos = menu_pos[1]
    
    for menu_button in main_menu_buttons:
        menu_button.set_position((get_menu_button_x_pos(menu_button), menu_button_y_pos))
        
        menu_button_y_pos += menu_button.height + MENU_BUTTON_PADDING

def unload():
    global menu_button_index
    global main_menu_buttons
    
    main_menu_buttons = []
    menu_button_index = 0

def handle_events():
    """handles selection and navigation on the MAINMENU"""
    global menu_button_index
    global main_menu_buttons
    
    if len(main_menu_buttons) == 0:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        selected_button = get_mouse_over_button()
        
        if selected_button != None:
            selected_button.handle_select()
        
    elif ((pygame.MOUSEBUTTONUP in wotsuievents.event_types) or
        (pygame.K_RETURN in wotsuievents.keys_released)):
        selected_button = get_selected_button()
        
        if selected_button != None:
            selected_button.handle_deselect(True)
            unload()
            
    elif pygame.K_UP in wotsuievents.keys_pressed:
        main_menu_buttons[menu_button_index].handle_deselect(False)
        
        if menu_button_index == 0:
            menu_button_index = len(main_menu_buttons) - 1
        else:
            menu_button_index -= 1
        
        main_menu_buttons[menu_button_index].handle_select()
    
    elif pygame.K_DOWN in wotsuievents.keys_pressed:
        main_menu_buttons[menu_button_index].handle_deselect(False)
        
        if menu_button_index == len(main_menu_buttons) - 1:
            menu_button_index = 0
        else:
            menu_button_index += 1
        
        main_menu_buttons[menu_button_index].handle_select()
    
    draw(gamestate.screen)

class Menu():
    MENU_BUTTON_PADDING = 20
    
    def __init__(self):
        self.buttons = []
        self.menu_button_index = 0
        self.menu_pos = None
        self.selected_button = None
    
    def load(self, buttons):
        self.buttons = buttons
        self.menu_pos = self.get_menu_pos()
        menu_button_y_pos = self.menu_pos[1]
        
        for menu_button in self.buttons:
            menu_button.set_position((self.get_menu_button_x_pos(menu_button), menu_button_y_pos))
            
            menu_button_y_pos += menu_button.height + Menu.MENU_BUTTON_PADDING
    
    def draw(self, surface):
        """draws the menu on to the given surface"""
        
        for menu_button in self.buttons:
            menu_button.draw(surface)

    def get_selected_button(self):
        slctd_button = None
        for menu_button in self.buttons:
            if menu_button.selected:
                slctd_button = menu_button
        
        return slctd_button

    def get_mouse_over_button(self):
        
        rtn_button = None
        for menu_button in self.buttons:
            if menu_button.contains(wotsuievents.mouse_pos):
                rtn_button = menu_button
        
        return rtn_button
        
    def get_menu_height(self):
        rtn_height = 0
        
        for menu_button in self.buttons:
            rtn_height += menu_button.height
            rtn_height += Menu.MENU_BUTTON_PADDING
        
        return rtn_height

    def get_menu_width(self):
        menu_width = 0
        
        for menu_button in self.buttons:
            menu_width = max(menu_width, menu_button.width)
        
        return menu_width
        
    def get_menu_pos(self):
        """returns a position that centers the menu in the middle of the 
        screen"""
        menu_height = self.get_menu_height()
        menu_width = self.get_menu_width()
        
        x_pos = (gamestate._WIDTH / 2) - (menu_width / 2)
        y_pos = (gamestate._HEIGHT / 2) - (menu_height / 2)
        
        return (x_pos, y_pos)

    def get_menu_button_x_pos(self, menu_button):
        """returns a position that centers the button in the middle of the 
        screen"""
        return (gamestate._WIDTH / 2) - (menu_button.width / 2)

    def handle_events(self):
        """handles selection and navigation on the MAINMENU"""
        menu_button_index = self.menu_button_index
        menu_buttons = self.buttons
        menu_button_index = self.menu_button_index
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            self.selected_button = self.get_mouse_over_button()
            
            if self.selected_button != None:
                self.selected_button.handle_select()
            
        elif ((pygame.MOUSEBUTTONUP in wotsuievents.event_types) or
            (pygame.K_RETURN in wotsuievents.keys_released)):
            self.selected_button = self.get_selected_button()
            
            if self.selected_button != None:
                self.selected_button.handle_deselect(True)
                
        elif pygame.K_UP in wotsuievents.keys_pressed:
            menu_buttons[menu_button_index].handle_deselect(False)
            
            if menu_button_index == 0:
                self.menu_button_index = len(menu_buttons) - 1
            else:
                self.menu_button_index -= 1
            
            menu_buttons[menu_button_index].handle_select()
        
        elif pygame.K_DOWN in wotsuievents.keys_pressed:
            menu_buttons[menu_button_index].handle_deselect(False)
            
            if menu_button_index == len(menu_buttons) - 1:
                self.menu_button_index = 0
            else:
                self.menu_button_index += 1
            
            menu_buttons[menu_button_index].handle_select()