import functools
import copy
import pygame
import eztext

import wotsui
import wotsuicontainers
import wotsuievents
import button

import movesetdata
import actionwizard
import animationexplorer
import frameeditor
from controlsdata import InputActionTypes

import gamestate
import player

class BuilderContainer(wotsui.UIObjectBase):
    def __init__(self):
        wotsui.UIObjectBase.__init__(self)
        self.moveset = None
        self.title = None
        self.expanded = False
        self.animation_select_container = None
        self.key_select_container = None
    
    def set_moveset(self, moveset):
        self.moveset = moveset
    
    def expand(self):
        for child in self.children:
            if child != self.title:
                child.show()
        
        self.expanded = True
    
    def collapse(self):
        for child in self.children:
            if child != self.title:
                child.hide()
        
        self.expanded = False
    
    def save(self):
        self.animation_select_container.save_selected_movement_animations()
    
    def handle_events(self):
        self.animation_select_container.handle_events()

class MovesetNameEntryBox(wotsuicontainers.TextEntryBox):
    _X_POS = 10
    _Y_POS = 10
    
    def __init__(self):
        wotsuicontainers.TextEntryBox.__init__(
            self,
            max_length = 100,
            position = (MovesetNameEntryBox._X_POS, MovesetNameEntryBox._Y_POS),
            prompt_text = 'Type moveset name: ',
            text_color = (255,255,255)
        )
        
        self.moveset = None
    
    def set_moveset(self, moveset):
        self.moveset = moveset
        self.text_entry_box.value = moveset.name
    
    def handle_events(self):
        wotsuicontainers.TextEntryBox.handle_events(self)
        
        if (self.selected and
        self.text_entry_box.value != self.moveset.name):
                self.moveset.name = self.text_entry_box.value

class MovementBuilderContainer(BuilderContainer):
    def __init__(self):
        BuilderContainer.__init__(self)
        self.position = (20, MovesetNameEntryBox._Y_POS + 60)
        self.title = MovesetBuilderLabel(self.position,"Create Movements",(255,255,255),25)
        self.draw_tab = False
        
        movement_select_title_text = "Select Movement Animations"
        animation_types = dict(zip(player.PlayerStates.MOVEMENTS, \
                                   player.PlayerStates.MOVEMENTS))
        self.animation_select_container = MovementAnimationSelectContainer((20,self.position[1] + self.title.height + 15), \
                                                                           movement_select_title_text, \
                                                                           animation_types)
        self.add_children([self.title, self.animation_select_container])
        
    def set_moveset(self, moveset):
        BuilderContainer.set_moveset(self, moveset)
        
        self.animation_select_container.set_moveset(moveset)
    
    def expand(self):
        BuilderContainer.expand(self)
        self.draw_tab = True
    
    def collapse(self):
        BuilderContainer.collapse(self)
        self.draw_tab = False
    
    def draw(self, surface):
        BuilderContainer.draw(self, surface)
        
        if self.draw_tab:
            title_top_left = self.title.position
            point1 = (title_top_left[0] - 10, title_top_left[1] - 10)
            title_top_right = self.title.top_right()
            point2 = (title_top_right[0] + 10, title_top_left[1] - 10)
            title_bottom_right = self.title.bottom_right()
            point3 = (title_bottom_right[0] + 10, title_bottom_right[1])
            point4 = (self.top_right()[0], title_bottom_right[1])
            
            pygame.draw.line(surface, (255,255,255), point1, point2)
            pygame.draw.line(surface, (255,255,255), point2, point3)
            pygame.draw.line(surface, (255,255,255), point3, point4)

class AttackBuilderContainer(BuilderContainer):
    def __init__(self):
        BuilderContainer.__init__(self)
        self.position = (20, MovesetNameEntryBox._Y_POS + 60)
        title_position = (400, MovesetNameEntryBox._Y_POS + 60)
        self.title = MovesetBuilderLabel(title_position,"Create Attacks",(255,255,255),25)
        self.draw_tab = False
        
        movement_select_title_text = "Select Attack Animations"
        animation_types = \
            {
                InputActionTypes.WEAK_PUNCH : 'Weak Punch',
                InputActionTypes.MEDIUM_PUNCH : 'Medium Punch',
                InputActionTypes.STRONG_PUNCH : 'Strong Punch',
                InputActionTypes.WEAK_KICK : 'Weak Kick',
                InputActionTypes.MEDIUM_KICK : 'Medium Kick',
                InputActionTypes.STRONG_KICK : 'Strong Kick'
            }
        self.animation_select_container = AttackAnimationSelectContainer((20,self.position[1] + self.title.height + 15), \
                                                                          movement_select_title_text, \
                                                                          animation_types)
        self.add_children([self.title, self.animation_select_container])
    
    def save(self):
        self.animation_select_container.save_selected_attack_animations()
    
    def set_moveset(self, moveset):
        BuilderContainer.set_moveset(self, moveset)
        
        self.animation_select_container.set_moveset(moveset)
    
    def expand(self):
        BuilderContainer.expand(self)
        self.draw_tab = True
    
    def collapse(self):
        BuilderContainer.collapse(self)
        self.draw_tab = False
    
    def draw(self, surface):
        BuilderContainer.draw(self, surface)
        
        if self.draw_tab:
            point1 = (self.position[0], self.title.bottom_left()[1])
            title_bottom_left = self.title.bottom_left()
            point2 = (title_bottom_left[0] - 10, title_bottom_left[1])
            title_top_left = self.title.position
            point3 = (title_top_left[0] - 10, title_top_left[1] - 10)
            title_top_right = self.title.top_right()
            point4 = (title_top_right[0] + 10, title_top_left[1] - 10)
            title_bottom_right = self.title.bottom_right()
            point5 = (title_bottom_right[0] + 10, title_bottom_right[1])
            point6 = (self.top_right()[0], title_bottom_right[1])
            
            pygame.draw.line(surface, (255,255,255), point1, point2)
            pygame.draw.line(surface, (255,255,255), point2, point3)
            pygame.draw.line(surface, (255,255,255), point3, point4)
            pygame.draw.line(surface, (255,255,255), point4, point5)
            pygame.draw.line(surface, (255,255,255), point5, point6)
    
    def handle_events(self):
        self.animation_select_container.handle_events()

class AnimationSelectContainer(BuilderContainer):
    def __init__(self, position, title_text, animation_types):
        BuilderContainer.__init__(self)
        
        self.position = position
        self.title = MovesetBuilderLabel(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        button_list = []
        
        for type, type_text in animation_types.iteritems():
            button_list.append(MoveTypeButton(type, type_text, 13))
        
        self.buttons = button_list
        self.layout_buttons()
        self.add_children(button_list)
        
        self.buttons[0].handle_selected()
        
        animation_navigator = AnimationNavigator()
        navigator_position = (position[0], position[1] + self.height + 15)
        animation_navigator.load_data(navigator_position, self.buttons[0].move_type)
        self.animation_navigator = animation_navigator
        
        self.add_child(animation_navigator)
    
    def set_moveset(self, moveset):
        self.moveset = moveset
        self.sync_to_moveset()
    
    def sync_to_moveset(self):
        pass
    
    def layout_buttons(self):
        title = self.title
        current_position = (title.position[0] + 10, \
                            title.position[1] + title.height + 10)
        buttons = self.buttons
        
        buttons[0].set_position(current_position)
        
        for i in range(1,len(buttons)):
            previous_button = buttons[i - 1]
            current_position = (previous_button.position[0] + previous_button.width + 10, \
                                previous_button.position[1])
            buttons[i].set_position(current_position)

class AttackAnimationSelectContainer(AnimationSelectContainer):
    def handle_events(self):
        self.animation_navigator.handle_events()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            for button in self.buttons:
                if button.contains(wotsuievents.mouse_pos):
                    for other_button in self.buttons:
                        if other_button.selected and other_button != button:
                            self.save_selected_attack_animations()
                            other_button.handle_deselected()
                    
                    button.handle_selected()
                    self.animation_navigator.animation_type = button.move_type
                    self.animation_navigator.load_animation_thumbnails()
                    
                    self.sync_to_moveset()
    
    def sync_to_moveset(self):
        for button in self.buttons:
            if button.selected:
                if self.moveset.has_attack_animation(button.move_type):
                    for thumbnail in self.animation_navigator.animation_thumbnails:
                        if thumbnail.animation.name == self.moveset.attack_animations[button.move_type].name:
                            thumbnail.handle_selected()
                            self.animation_navigator.selected_animation = thumbnail.animation
    
    def save_selected_attack_animations(self):
        selected_animation = self.animation_navigator.selected_animation
        
        if selected_animation != None:
            self.moveset.save_attack_animation(
                self.animation_navigator.animation_type,
                selected_animation
            )

class MovementAnimationSelectContainer(AnimationSelectContainer):
    def handle_events(self):
        self.animation_navigator.handle_events()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            for button in self.buttons:
                if button.contains(wotsuievents.mouse_pos):
                    for other_button in self.buttons:
                        if other_button.selected and other_button != button:
                            self.save_selected_movement_animations()
                            other_button.handle_deselected()
                    
                    button.handle_selected()
                    self.animation_navigator.animation_type = button.move_type
                    self.animation_navigator.load_animation_thumbnails()
                    
                    self.sync_to_moveset()
    
    def sync_to_moveset(self):
        for button in self.buttons:
            if button.selected:
                if self.moveset.has_movement_animation(button.move_type):
                    for thumbnail in self.animation_navigator.animation_thumbnails:
                        if thumbnail.animation.name == self.moveset.movement_animations[button.move_type].name:
                            thumbnail.handle_selected()
                            self.animation_navigator.selected_animation = thumbnail.animation
    
    def save_selected_movement_animations(self):
        selected_animation = self.animation_navigator.selected_animation
        
        if selected_animation != None:
            self.moveset.save_movement_animation(self.animation_navigator.animation_type, selected_animation)

class MoveTypeButton(button.TextButton):
    def __init__(self, move_type, text, font_size=32):
        button.TextButton.__init__(self, text, font_size)
        self.move_type = move_type
        self.fixed_dimensions = True

class MovesetBuilderLabel(button.Label):    
    def on_mouseover(self):
        self.text_color = (0,0,255)
    
    def on_mouseoff(self):
        self.text_color = (255,255,255)

class AnimationThumbnail(button.Button):
    _THUMBNAIL_HEIGHT = 80
    
    def __init__(self, position, animation):
        button.Button.__init__(self)
        
        self.animation = animation
        
        thumbnail_animation = copy.deepcopy(animation)
        thumbnail_animation.set_animation_height(AnimationThumbnail._THUMBNAIL_HEIGHT, 170)
        self.thumbnail_animation = thumbnail_animation
        
        self.frame = self.thumbnail_animation.get_middle_frame()
        
        text_pos = (position[0], \
                    position[1] + AnimationThumbnail._THUMBNAIL_HEIGHT + 5)
        name_label = button.Label(text_pos, animation.name, self.color, 15)
        self.name_label = name_label
        self.add_child(name_label)
        self.height = AnimationThumbnail._THUMBNAIL_HEIGHT + 5 + name_label.height
        self.width = max(thumbnail_animation.get_widest_frame().image_width(), self.name_label.width)
        self.position = position
        
        self.fixed_dimensions = True
    
    def draw(self, surface):
        if self.contains(wotsuievents.mouse_pos):
            self.play_animation(self, surface, self.draw_current_frame)
        else:
            self.draw_current_frame(surface)
    
    def draw_current_frame(self, surface):
        """draws the frame thumbnail"""
        
        frame_image_pos = self.frame.get_reference_position()
        temp_surface = pygame.Surface((self.frame.image_width(), \
                                       self.frame.image_height()))
        
        pos_delta = (0 - frame_image_pos[0], \
                     0 - frame_image_pos[1])
        
        self.frame.draw(temp_surface, \
                        self.color, \
                        1, \
                        pos_delta, \
                        point_radius = 1, \
                        line_thickness = 2)
        
        surface.blit(temp_surface, self.position)
        
        wotsui.UIObjectBase.draw(self, surface)
    
    def draw_relative(self, surface, position):
        if self.contains(wotsuievents.mouse_pos):
            partial_draw_relative = functools.partial(self.draw_current_frame_relative, \
                                                      reference_position=position)
            self.play_animation(surface, partial_draw_relative)
        else:
            self.draw_current_frame_relative(surface, position)
    
    def draw_current_frame_relative(self, surface, reference_position):
        
        frame_image_pos = self.frame.get_reference_position()
        temp_surface = pygame.Surface((self.frame.image_width(), \
                                       self.frame.image_height()))
        
        pos_delta = (0 - frame_image_pos[0], \
                     0 - frame_image_pos[1])
        
        self.frame.draw(temp_surface, \
                        self.color, \
                        1, \
                        pos_delta, \
                        point_radius = 1, \
                        line_thickness = 2)
        
        relative_position = self.get_relative_position(reference_position)
        
        surface.blit(temp_surface, relative_position)
        
        wotsui.UIObjectBase.draw_relative(self, surface, reference_position)
    
    def play_animation(self, surface, draw_func):
        """plays the animation"""
        frame_index = self.thumbnail_animation.frame_index
        
        self.frame = self.thumbnail_animation.frames[frame_index]
        draw_func(surface)
        
        if frame_index < len(self.thumbnail_animation.frames) - 1:
            self.thumbnail_animation.frame_index += 1
        else:
            self.thumbnail_animation.frame_index = 0

class AnimationNavigator(wotsuicontainers.ScrollableContainer):
    HEIGHT = 120
    WIDTH = 700
    
    def __init__(self):
        wotsuicontainers.ScrollableContainer.__init__(self)
        
        self.animation_thumbnails = []
        self.animation_type = None
        self.selected_animation = None
        self.new_animation_button = button.TextButton("Create New Animation", 15)
        self.add_child(self.new_animation_button)
        
        self.edit_animation_button = button.TextButton("Edit Animation", 15)
        self.add_child(self.edit_animation_button)
        
        self.delete_animation_button = button.TextButton("Delete Animation", 15)
        self.add_child(self.delete_animation_button)
        
        self.gamestate_mode = gamestate.Modes.MOVESETBUILDER
        self.allow_multiple_select = False
    
    def load_data(self, position, animation_type):
        self.animation_type = animation_type
        self.set_layout_data(position, \
                             AnimationNavigator.HEIGHT, \
                             AnimationNavigator.WIDTH)
        self.set_viewable_area(position, \
                               AnimationNavigator.HEIGHT - wotsuicontainers.SCROLL_BUTTON_HEIGHT, \
                               AnimationNavigator.WIDTH - wotsuicontainers.SCROLL_BUTTON_WIDTH)
        
        new_animation_button_position = (position[0] + 10, \
                                         position[1] + AnimationNavigator.HEIGHT + 5)
        self.new_animation_button.set_position(new_animation_button_position)
        
        edit_animation_button_position = (new_animation_button_position[0] + self.new_animation_button.width + 20, \
                                          new_animation_button_position[1])
        self.edit_animation_button.set_position(edit_animation_button_position)
        
        delete_animation_button_position = (edit_animation_button_position[0] + self.edit_animation_button.width + 20, \
                                            edit_animation_button_position[1])
        self.delete_animation_button.set_position(delete_animation_button_position)
        
        self.load_animation_thumbnails()
    
    def load_animation_thumbnails(self):
        if len(self.animation_thumbnails) > 0:
            self.clear_animation_thumbnails()
        
        for animation in self.get_animations():
            animation_thumbnail = AnimationThumbnail((0,0), animation)
            self.animation_thumbnails.append(animation_thumbnail)
        
        if len(self.animation_thumbnails) > 0:
            self.layout_thumbnails()
            self.add_children(self.animation_thumbnails, True)
        
        self.init_vertical_scrollbar()
        self.init_horizontal_scrollbar()
    
    def clear_animation_thumbnails(self):
        self.remove_children(self.animation_thumbnails, True)
        self.animation_thumbnails = []
    
    def get_animations(self):
        animations = None
        
        if self.animation_type in player.PlayerStates.MOVEMENTS:
            animations = actionwizard.get_movement_animations(self.animation_type)
        elif self.animation_type in InputActionTypes.ATTACKS:
        
            action_type = player.AttackTypes.PUNCH
            
            if self.animation_type in [InputActionTypes.WEAK_KICK, InputActionTypes.MEDIUM_KICK, InputActionTypes.STRONG_KICK]:
                action_type = player.AttackTypes.KICK
            
            animations = actionwizard.get_attack_animations(action_type)
        
        return animations
    
    def layout_thumbnails(self):
        current_position = (self.position[0] + 10, \
                            self.position[1])
        thumbnails = self.animation_thumbnails
        
        thumbnails[0].set_position(current_position)
        
        for i in range(1,len(thumbnails)):
            previous_thumbnail = thumbnails[i - 1]
            current_position = (previous_thumbnail.position[0] + previous_thumbnail.width + 10, \
                                previous_thumbnail.position[1])
            thumbnails[i].set_position(current_position)
    
    def draw_relative(self, surface, position):
        wotsuicontainers.ScrollableContainer.draw_relative(self, surface, position)
        self.new_animation_button.draw_relative(surface, position)
        self.edit_animation_button.draw_relative(surface, position)
        self.delete_animation_button.draw_relative(surface, position)
    
    def handle_events(self):
        wotsuicontainers.ScrollableContainer.handle_events(self)
        
        if self.viewable_area.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if self.edit_animation_button.selected:
                    pass
                elif self.delete_animation_button.selected:
                    pass
                else:
                    for thumbnail in self.animation_thumbnails:
                        if thumbnail.contains(wotsuievents.mouse_pos):
                            if self.allow_multiple_select:
                                if thumbnail.selected:
                                    thumbnail.handle_deselected()
                                    
                                    if self.selected_animation == thumbnail.animation:
                                        self.selected_animation = None
                                else:
                                    thumbnail.handle_selected()
                            else:
                                for other_thumbnail in self.animation_thumbnails:
                                    if other_thumbnail.selected:
                                        other_thumbnail.handle_deselected()
                                
                                thumbnail.handle_selected()
            elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
                for thumbnail in self.animation_thumbnails:
                    if thumbnail.contains(wotsuievents.mouse_pos):
                        if self.edit_animation_button.selected:
                            self.edit_animation_button.handle_deselected()
                            frameeditor.load(self.animation_type, copy.deepcopy(thumbnail.animation), self.gamestate_mode)
                            gamestate.mode = gamestate.Modes.FRAMEEDITOR
                        elif self.delete_animation_button.selected:
                            actionwizard.delete_animation(self.animation_type, thumbnail.animation)
                            self.load_animation_thumbnails()
                        else:
                            self.selected_animation = thumbnail.animation
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if self.new_animation_button.contains(wotsuievents.mouse_pos):
                self.new_animation_button.handle_selected()
                self.selected_animation = animationexplorer.create_WOTS_animation()
                
                if self.edit_animation_button.selected:
                    self.edit_animation_button.handle_deselected()
            
            if self.edit_animation_button.contains(wotsuievents.mouse_pos):
                if self.edit_animation_button.selected:
                    self.edit_animation_button.handle_deselected()
                else:
                    self.edit_animation_button.handle_selected()
            
            if self.delete_animation_button.contains(wotsuievents.mouse_pos):
                if self.delete_animation_button.selected:
                    self.delete_animation_button.handle_deselected()
                else:
                    self.delete_animation_button.handle_selected()
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if ((self.selected_animation != None) and
                (self.new_animation_button.contains(wotsuievents.mouse_pos))):
                new_animation = copy.deepcopy(self.selected_animation)
                new_animation.name = ''
                
                frameeditor.load(self.animation_type, new_animation, self.gamestate_mode)
                gamestate.mode = gamestate.Modes.FRAMEEDITOR
            
            if self.new_animation_button.selected:
                self.new_animation_button.handle_deselected()

class KeyBindingContainer(wotsuicontainers.ScrollableContainer):
    _HEIGHT = 170
    _WIDTH = 700
    
    def __init__(self, position, title_text, move_types):
        wotsuicontainers.ScrollableContainer.__init__(self)
        self.moveset = None
        self.position = position
        
        self.title = MovesetBuilderLabel(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        viewable_area_position = (position[0], position[1] + self.height + 10)
        self.set_viewable_area(viewable_area_position, \
                               KeyBindingContainer._HEIGHT - wotsuicontainers.SCROLL_BUTTON_HEIGHT, \
                               KeyBindingContainer._WIDTH - wotsuicontainers.SCROLL_BUTTON_WIDTH)
        self.buttons = []
        
        if len(move_types.keys()) > 0:
            button_list = []
            
            for type, type_text in move_types.iteritems():
                button_list.append(BindButton(type, type_text, 20))
            
            self.buttons.extend(button_list)
            self.layout_buttons()
            self.add_children(button_list, True)
        
        self.init_vertical_scrollbar()
        self.init_horizontal_scrollbar()
    
    def set_moveset(self, moveset):
        self.moveset = moveset
        self.sync_to_moveset()
    
    def sync_to_moveset(self):
        pass
    
    def layout_buttons(self):
        viewable_area_position = self.viewable_area.position
        
        current_position = (viewable_area_position[0] + 10, \
                            viewable_area_position[1])
        buttons = self.buttons
        
        buttons[0].set_position(current_position)
        
        for i in range(1,len(buttons)):
            previous_button = buttons[i - 1]
            x_position = previous_button.position[0]
            y_position = previous_button.position[1]
            
            if self.width < 200:
                y_position += previous_button.height + 10
                x_position = viewable_area_position[0] + 10
            else:
                if i % int(self.width / 200) == 0:
                    y_position += previous_button.height + 10
                    x_position = viewable_area_position[0] + 10
                else:
                    x_position += 200
            
            current_position = (x_position, \
                                y_position)
            buttons[i].set_position(current_position)
    
    def handle_events(self):
        wotsuicontainers.ScrollableContainer.handle_events(self)
        
        if self.viewable_area.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                for button in self.buttons:
                    if button.contains(wotsuievents.mouse_pos):
                        if button.selected:
                            button.handle_deselected()
                        else:
                            button.handle_selected()
                    else:
                        if button.selected:
                            button.handle_deselected()
            elif pygame.KEYDOWN in wotsuievents.event_types:
                for button in self.buttons:
                    if button.selected:
                        button.key = wotsuievents.keys_pressed[0]
                        button.handle_deselected()

class MovementKeyBindingContainer(KeyBindingContainer):
    def save(self):
        for button in self.buttons:
            if button.key != None:
                self.moveset.save_movement_key(button.move_type, button.key)
    
    def sync_to_moveset(self):
        for move_type, key in self.moveset.movement_keys.iteritems():
            for button in self.buttons:
                if button.move_type == move_type:
                    button.key = key
                    break

class AttackKeyBindingContainer(KeyBindingContainer):
    def sync_to_moveset(self):
        for attack_name, key in self.moveset.attack_keys.iteritems():
            if not self.has_button(attack_name):
                self.add_button(attack_name)
            
            for button in self.buttons:
                if button.move_type == attack_name:
                    button.key = key
    
    def has_button(self, attack_name):
        has_button_indicator = False
        
        for button in self.buttons:
            if button.move_type == attack_name:
                has_button_indicator = True
                break
        
        return has_button_indicator
    
    def add_button(self, attack_name):
        button = BindButton(attack_name, attack_name, 20)
        
        self.buttons.append(button)
        self.add_child(button, True)
        self.layout_buttons()
    
    def remove_button(self, attack_name):
        for button in self.buttons:
            if button.move_type == attack_name:
                self.buttons.remove(button)
                self.remove_child(button, True)
                
                if len(self.buttons) > 0:
                    self.layout_buttons()
                break
    
    def save(self):
        for button in self.buttons:
            if button.key != None:
                self.moveset.save_attack_key(button.move_type, button.key)

class BindButton(button.TextButton):
    def __init__(self, move_type, action_text, font_size=32):
        button.TextButton.__init__(self, action_text, font_size)
        self.move_type = move_type
        self.key = None
    
    def set_key(self, key):
        self.key = key
    
    def draw(self, surface):
        button.TextButton.draw(self, surface)
        
        if self.key != None:
            key_position = (self.position[0] + self.width + button.TextButton.TEXT_PADDING, \
                            self.position[1] + self.height - self.text.font.size(pygame.key.name(self.key))[1])
            text_surface = self.text.font.render(pygame.key.name(self.key), 1, self.color)
        
            surface.blit(text_surface, key_position)
    
    def draw_relative(self, surface, reference_position):
        button.TextButton.draw_relative(self, surface, reference_position)
        
        relative_position = self.get_relative_position(reference_position)
        
        if self.key != None:
            key_position = (relative_position[0] + self.width + button.TextButton.TEXT_PADDING, \
                            relative_position[1] + self.height - self.text.font.size(pygame.key.name(self.key))[1])
            text_surface = self.text.font.render(pygame.key.name(self.key), 1, self.color)
        
            surface.blit(text_surface, key_position)
