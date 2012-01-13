import pygame
import wotsui
import button
from enumerations import PlayerPositions
from wotsuicontainers import ButtonContainer, ScrollableContainer
from attackbuilderui import AttackLabel
import gamestate

#Health Bar Constants
LABEL_COLOR = (255,255,255)
LABEL_FONT_SIZE = 20
PLAYER_HEALTH_Y_PADDING_PX = 30
PLAYER_HEALTH_X_PADDING_PX = 30
HEALTH_BAR_Y_PADDING_PX = 20
PLAYER_HEALTH_PX_WIDTH = 300
PLAYER_HEALTH_PX_HEIGHT = 15
HEALTH_BAR_BORDER_WIDTH_PX = 5
HEALTH_BAR_BORDER_COLOR = (100,100,100)
HEALTH_BAR_BKG_COLOR = (0,0,0)
HEALTH_BAR_FG_COLOR = (0,255,0)
DAMAGE_COLOR = (255,0,0)
DAMAGE_TIMEOUT = 300
DAMAGE_TRANSITION_RATE_PERCENT_PER_MS = .0005

#Pause menu constants
PAUSE_MENU_HEIGHT = 400
PAUSE_MENU_WIDTH = 300

class AttackList(ButtonContainer):
    def __init__(self, moveset, position):
        ButtonContainer.__init__(
            self,
            position,
            PAUSE_MENU_HEIGHT,
            PAUSE_MENU_WIDTH,
            moveset.name + " Move List",
            AttackLabel,
            self.get_button_args(moveset)
        )
        self.init_button_text()
        self.set_dimensions()
        self.layout_buttons()
        self.reset_scroll()
    
    def layout_buttons(self):
        current_position = (
            self.scrollable_area.position[0] + 10,
            self.scrollable_area.position[1] + self.title.height
        )
        attack_labels = self.buttons
        
        attack_labels[0].set_position(current_position)
        
        for i in range(1,len(attack_labels)):
            previous_label = attack_labels[i - 1]
            current_position = (
                previous_label.position[0], 
                previous_label.position[1] + previous_label.height + 3
            )
            attack_labels[i].set_position(current_position)
    
    def draw(self, surface):
        #return_surface = pygame.Surface((PAUSE_MENU_HEIGHT, PAUSE_MENU_WIDTH))
        rect = pygame.Rect(
            self.position,
            (self.width, self.height)
        )
        gamestate.new_dirty_rects.append(rect)
        
        pygame.draw.rect(
            surface, 
            (50,50,50), 
            rect,
            1
        )
        
        ButtonContainer.draw(self, surface)
        
        pygame.draw.rect(
            surface, 
            (255,255,255), 
            rect,
            1
        )
    
    def get_button_args(self, moveset):
        button_args = []
        
        for attack_name, attack_commands in moveset.attack_key_combinations.iteritems():
            button_args.append([attack_name, attack_commands])
        
        return button_args
    
    def init_button_text(self):
        for button in self.buttons:
            button.set_key_combination(button.key_combination)
        
    def handle_events(self):
        ScrollableContainer.handle_events(self)

class PlayerHealth(wotsui.UIObjectBase):
    def __init__(self, label_text, player_position):
        wotsui.UIObjectBase.__init__(self)
        self.changed = True
        self.label = button.Label(
            (0,0), 
            label_text, 
            LABEL_COLOR, 
            LABEL_FONT_SIZE
        )
        self.label.set_position(self.get_label_position(player_position))
        self.add_child(self.label)
        self.health_bar = HealthBar(
            self.get_bar_position(player_position)
        )
        self.add_child(self.health_bar)
        self.evaluate_position()
        self.set_dimensions()
    
    def get_health_percent(self):
        return self.health_bar.health_percent
    
    def get_label_position(self, player_position):
        if player_position == PlayerPositions.PLAYER1:
            return (PLAYER_HEALTH_X_PADDING_PX, PLAYER_HEALTH_Y_PADDING_PX)
        else:
            return (
                gamestate._WIDTH - PLAYER_HEALTH_X_PADDING_PX - self.label.width, 
                PLAYER_HEALTH_Y_PADDING_PX
            )
    
    def get_bar_position(self, player_position):
        if player_position == PlayerPositions.PLAYER1:
            return (
                PLAYER_HEALTH_X_PADDING_PX, 
                self.label.position[1] + self.label.height + HEALTH_BAR_Y_PADDING_PX
            )
        else:
            return (
                gamestate._WIDTH - PLAYER_HEALTH_X_PADDING_PX - PLAYER_HEALTH_PX_WIDTH, 
                self.label.position[1] + self.label.height + HEALTH_BAR_Y_PADDING_PX
            )
    
    def draw(self):
        return_surface = pygame.Surface(
            (self.width, self.height)
        ).convert()
        return_surface.set_colorkey((111,111,111))
        return_surface.fill((111,111,111))
        
        self.label.draw_relative(return_surface, self.position)
        
        return_surface.blit(
            self.health_bar.draw(),
            (0,PLAYER_HEALTH_Y_PADDING_PX)
        )
        
        return return_surface
    
    def update(self, time_passed, player_health_percent):
        damage_percent = self.health_bar.health_percent - player_health_percent
        if damage_percent > 0:
            self.health_bar.add_damage(damage_percent)
            self.changed = True
        
        if self.health_bar.damage_delta == 0:
            self.changed = False
        
        self.health_bar.update(time_passed)

class HealthBar(wotsui.UIObjectBase):
    def __init__(self, position):
        wotsui.UIObjectBase.__init__(self)
        
        self.player_position = position
        self.set_layout_data(
            position, 
            PLAYER_HEALTH_PX_HEIGHT, 
            PLAYER_HEALTH_PX_WIDTH
        )
        self.health_percent = float(1)
        self.damage_delta = float(0)
        self.damage_delta_timer = DAMAGE_TIMEOUT
    
    def add_damage(self, damage_percent):
        self.damage_delta += damage_percent
        self.health_percent -= damage_percent
        self.damage_delta_timer = 0
    
    def update(self, time_passed):
        if self.damage_delta_timer <= DAMAGE_TIMEOUT:
            self.damage_delta_timer += time_passed
        elif self.damage_delta > 0:
            self.damage_delta -= DAMAGE_TRANSITION_RATE_PERCENT_PER_MS * time_passed
    
    def get_damage_position(self):
        if PlayerPositions.PLAYER1 == self.player_position:
            return (0,0)
        else:
            return (self.width - int(float(self.width) * (self.health_percent + self.damage_delta)), 0)
    
    def get_health_position(self):
        if PlayerPositions.PLAYER1 == self.player_position:
            return (0,0)
        else:
            return (self.width - int(float(self.width) * self.health_percent), 0)
    
    def draw(self):
        return_surface = pygame.Surface(
            (self.width, self.height)
        ).convert()
        return_surface.fill(HEALTH_BAR_BKG_COLOR)
        
        damage_position = self.get_damage_position()
        
        damage_rect = (
            damage_position[0],
            damage_position[1],
            int(float(self.width) * (self.health_percent + self.damage_delta)),
            self.height
        )
        return_surface.fill(
            DAMAGE_COLOR,
            damage_rect
        )
        
        health_position = self.get_health_position()
        health_rect = (
            health_position[0],
            health_position[1],
            int(float(self.width) * self.health_percent),
            self.height
        )       
        return_surface.fill(
            HEALTH_BAR_FG_COLOR,
            health_rect
        )
        
        border_rect = (
            0,
            0,
            self.width,
            self.height
        )
        pygame.draw.rect(
            return_surface,
            HEALTH_BAR_BORDER_COLOR,
            border_rect,
            HEALTH_BAR_BORDER_WIDTH_PX
        )
        return return_surface
