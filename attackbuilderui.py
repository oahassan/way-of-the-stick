import copy
import pygame
import eztext

import wotsui
import wotsuicontainers
import wotsuievents
import button
from inputtree import InputTree

import movesetdata
import actionwizard
import animationexplorer
import frameeditor
from movesetbuilderui import AnimationThumbnail, AnimationSelectContainer, MovesetBuilderLabel, BuilderContainer, MoveTypeButton, MovesetNameEntryBox
from enumerations import AttackTypes, InputActionTypes

import gamestate
import player

class AttackBuilderContainer(BuilderContainer):
    def __init__(self):
        BuilderContainer.__init__(self)
        self.position = (20, MovesetNameEntryBox._Y_POS + 60)
        title_position = (300, MovesetNameEntryBox._Y_POS + 60)
        self.title = MovesetBuilderLabel(title_position,"Create Attacks",(255,255,255),25)
        self.ValidationTree = InputTree()
        self.draw_tab = True
        
        attack_types = [(AttackTypes.KICK, "Kick"), (AttackTypes.PUNCH, "Punch")]
        self.animation_select_container = AttackSelectContainer(
            (20, self.position[1] + self.title.height + 15),
            "Select Attack Type",
            attack_types
        )
        self.key_select_container = KeySetContainer(
            (300, self.position[1] + self.title.height + 15),
            "Select Attack Commands"
        )
        self.key_select_container.inactivate()
        self.add_children([
            self.title,
            self.animation_select_container,
            self.key_select_container
        ])
        self.width = 750
    
    def set_moveset(self, moveset):
        self.animation_select_container.set_moveset(moveset)
    
    def save(self):
        self.animation_select_container.save_to_moveset()
    
    def sync_to_moveset(self):
        self.animation_select_container.sync_to_moveset()
    
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
        self.key_select_container.handle_events()
        
        animation = self.animation_select_container.selected_animation()
        
        if animation != None:
            label_combination = self.animation_select_container.get_key_combination(
                animation.name
            )
            
            if not self.key_select_container.active:
                self.key_select_container.activate()
                self.key_select_container.set_key_combination(
                    label_combination
                )
            
            if self.key_select_container.thumbnail == None:
                thumbnail = self.animation_select_container.get_thumbnail(
                    animation.name
                )
                
                self.key_select_container.set_thumbnail(thumbnail)
                
                self.key_select_container.set_key_combination(
                    self.animation_select_container.get_key_combination(
                        animation.name
                    )
                )
                
            elif self.key_select_container.thumbnail.animation.name != animation.name:
                thumbnail = self.animation_select_container.get_thumbnail(
                    animation.name
                )
                
                self.key_select_container.set_thumbnail(thumbnail)
                
                self.key_select_container.set_key_combination(
                    self.animation_select_container.get_key_combination(
                        animation.name
                    )
                )
            
            key_select_text = self.key_select_container.key_combination_label.text
            key_select_combination = self.key_select_container.key_combination
            label = self.animation_select_container.get_attack_label(animation.name)
            
            if (label != None and
            len(key_select_text) != len(label.key_combination_label.text)):
                if self.animation_select_container.is_valid_command(key_select_combination):
                    if len(key_select_combination) == 0:
                        self.animation_select_container.set_key_combination(
                            label.attack_name,
                            key_select_combination
                        )
                        
                    else:
                        if self.animation_select_container.command_in_use(key_select_combination):
                            self.key_select_container.command_in_use_label.show()
                        else:
                            if self.key_select_container.command_in_use_label.visible:
                                self.key_select_container.command_in_use_label.hide()
                            
                            self.animation_select_container.set_key_combination(
                                label.attack_name,
                                key_select_combination
                            )
            else:
                if len(key_select_combination) == 0:
                    if self.key_select_container.command_in_use_label.visible:
                        self.key_select_container.command_in_use_label.hide()
        
        else:
            if self.key_select_container.active:
                self.key_select_container.inactivate()
                self.key_select_container.set_key_combination([])
                
                if self.key_select_container.thumbnail != None:
                    self.key_select_container.remove_thumbnail()

class KeyButton(button.TextButton):
    
    def __init__(self, position, text, font_size, action_type):
        button.TextButton.__init__(self, text, font_size)
        self.action_type = action_type

class KeyButtonContainer(wotsuicontainers.ButtonContainer):
    def __init__(
        self,
        position,
        height,
        width,
        title_text,
        button_class,
        button_args=None
    ):
        wotsuicontainers.ButtonContainer.__init__(
            self,
            position,
            height,
            width,
            title_text,
            button_class,
            button_args
        )
        self.remove_child(self.title)
        
    def layout_buttons(self):
        current_position = (self.position[0] + 10,
                            self.position[1] + 10)
        buttons = self.buttons
        
        buttons[0].set_position(current_position)
        
        for i in range(1,len(buttons)):
            previous_button = buttons[i - 1]
            current_position = (
                previous_button.position[0] + previous_button.width + 10,
                previous_button.position[1]
            )
            
            if (current_position[0] + buttons[i].width + 10 > self.position[0] + self.viewable_area.width):
                current_position = (
                    self.position[0] + 10,
                    current_position[1] + previous_button.height + 10
                )
            
            buttons[i].set_position(current_position)

class KeyReferenceContainer(wotsui.UIObjectBase):
    
    def __init__(self, position):
        wotsui.UIObjectBase.__init__(self)
        
        title = button.Label(position, "Command Key", (255,255,255), 20)
        self.add_child(title)
        
        label_list = []
        forward_label = button.Label((0,0), "FW - Move Forward", (255,255,255), 15)
        label_list.append(forward_label)
        up_label = button.Label((0,0), "UP - Move Up", (255,255,255), 15)
        label_list.append(up_label)
        down_label = button.Label((0,0), "DN - Move Down", (255,255,255), 15)
        label_list.append(down_label)
        wk_label = button.Label((0,0), "QK - Quick Kick", (255,255,255), 15)
        label_list.append(wk_label)
        mk_label = button.Label((0,0), "TK - Tricky Kick", (255,255,255), 15)
        label_list.append(mk_label)
        sk_label = button.Label((0,0), "SK - Strong Kick", (255,255,255), 15)
        label_list.append(sk_label)
        wp_label = button.Label((0,0), "QP - Quick Punch", (255,255,255), 15)
        label_list.append(wp_label)
        mp_label = button.Label((0,0), "TP - Tricky Punch", (255,255,255), 15)
        label_list.append(mp_label)
        sp_label = button.Label((0,0), "SP - Strong Punch", (255,255,255), 15)
        label_list.append(sp_label)
        ju_label = button.Label((0,0), "JU - Jump", (255,255,255), 15)
        label_list.append(ju_label)
        
        self.layout_labels(
            label_list,
            (position[0] + 10, position[1] + title.height + 10)
        )
        self.add_children(label_list)
    
    def layout_labels(self, labels, start_position):
        bottom_padding = 5
        
        current_position = (start_position[0], start_position[1])
        labels[0].set_position(start_position)
        
        for label_index in range(1, len(labels)):
            label = labels[label_index]
            current_position = (
                current_position[0],
                current_position[1] + label.height + bottom_padding
            )
            
            label.set_position(current_position)

class KeySetContainer(BuilderContainer):
    def __init__(self, position, title_text):
        BuilderContainer.__init__(self)
        
        self.active = True
        self.position = position
        self.title = MovesetBuilderLabel(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        key_container_position = (position[0], position[1] + self.title.height + 10)
        button_args = [
            ((0,0), "FW", 18, InputActionTypes.FORWARD),
            ((0,0), "UP", 18, InputActionTypes.MOVE_UP),
            ((0,0), "DN", 18, InputActionTypes.MOVE_DOWN),
            ((0,0), "QK", 18, InputActionTypes.WEAK_KICK),
            ((0,0), "TK", 18, InputActionTypes.MEDIUM_KICK),
            ((0,0), "SK", 18, InputActionTypes.STRONG_KICK),
            ((0,0), "QP", 18, InputActionTypes.WEAK_PUNCH),
            ((0,0), "TP", 18, InputActionTypes.MEDIUM_PUNCH),
            ((0,0), "SP", 18, InputActionTypes.STRONG_PUNCH),
            ((0,0), "JU", 18, InputActionTypes.JUMP)
        ]
        self.key_buttons = KeyButtonContainer(
            key_container_position,
            270,
            250,
            "",
            KeyButton,
            button_args
        )
        self.add_child(self.key_buttons)
        
        command_key_position = (
            position[0] + self.key_buttons.width,
            key_container_position[1] + 10
        )
        self.command_key = KeyReferenceContainer(command_key_position)
        self.add_child(self.command_key)
        
        command_in_use_position = (position[0], position[1] + self.height - 10)
        self.command_in_use_label = button.Label(
            command_in_use_position,
            "this command is already in use",
            (255,0,0),
            15
        )
        self.command_in_use_label.hide()
        self.add_child(self.command_in_use_label)
        
        self.key_combination = []
        key_combination_position = (
            position[0],
            position[1] + self.height
        )
        self.key_combination_label = button.Label(
            key_combination_position,
            "--",
            (255,255,255),
            22
        )
        self.add_child(self.key_combination_label)
        
        clear_button_position = (position[0], position[1] + self.height + 10)
        self.clear_button = button.TextButton(
            "Clear",
            15
        )
        self.clear_button.set_position(clear_button_position)
        self.add_child(self.clear_button)
        
        self.thumbnail = None
        self.thumbnail_position = (
            self.position[0] + 50,
            self.position[1] + self.height + 30
        )
    
    def inactivate(self):
        self.active = False
        
        for button in self.key_buttons.buttons:
            button.inactivate()
    
    def activate(self):
        self.active = True
        
        for button in self.key_buttons.buttons:
            button.activate()
    
    def handle_events(self):
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            for button in self.key_buttons.buttons:
                if button.active and button.contains(wotsuievents.mouse_pos):
                    button.handle_selected()
                    
                    if self.key_buttons.selected_button != None:
                        self.key_buttons.selected_button.handle_deselected()
                    
                    self.key_buttons.selected_button = button
                    break
            
            if self.clear_button.contains(wotsuievents.mouse_pos):
                self.clear_button.handle_selected()
            
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if (self.key_buttons.selected_button != None and
            self.key_buttons.selected_button.contains(wotsuievents.mouse_pos)):
                button = self.key_buttons.selected_button
                
                if not button.action_type in self.key_combination:
                    self.key_combination.append(button.action_type)
                    self.set_key_combination_text()
                
                button.handle_deselected()
                self.key_buttons.selected_button = None
            
            if (self.clear_button.selected and
            self.clear_button.contains(wotsuievents.mouse_pos)):
                self.set_key_combination([])
                self.clear_button.handle_deselected()
    
    def set_thumbnail(self, thumbnail):
        
        if self.thumbnail != None:
            self.remove_child(
                self.thumbnail
            )
        
        self.thumbnail = thumbnail
        
        if thumbnail != None:
            self.add_child(thumbnail)
            thumbnail.set_position(self.thumbnail_position)
    
    def remove_thumbnail(self):
        self.remove_child(
            self.thumbnail
        )
        self.thumbnail = None
    
    def set_key_combination(self, key_combination):
        if key_combination == None:
            self.key_combination = []
        else:
            self.key_combination = copy.deepcopy(key_combination)
        self.set_key_combination_text()
    
    def set_key_combination_text(self):
        text = ""
        
        for action_type in self.key_combination:
            if text == "":
                text = self.get_key_text(action_type)
            else:
                text += " + " + self.get_key_text(action_type)
        
        self.key_combination_label.set_text(text)
    
    def get_key_text(self, action_type):
        if action_type == InputActionTypes.FORWARD:
            return "FW"
            
        elif action_type == InputActionTypes.MOVE_UP:
            return "UP"
        
        elif action_type == InputActionTypes.MOVE_DOWN:
            return "DN"
        
        elif action_type == InputActionTypes.WEAK_KICK:
            return "QK"
        
        elif action_type == InputActionTypes.MEDIUM_KICK:
            return "TK"
        
        elif action_type == InputActionTypes.STRONG_KICK:
            return "SK"
        
        elif action_type == InputActionTypes.WEAK_PUNCH:
            return "QP"
        
        elif action_type == InputActionTypes.MEDIUM_PUNCH:
            return "TP"
        
        elif action_type == InputActionTypes.STRONG_PUNCH:
            return "SP"
        
        elif action_type == InputActionTypes.JUMP:
            return "JU"

class AttackSelectContainer(AnimationSelectContainer):
    def __init__(self, position, title_text, animation_types):
        BuilderContainer.__init__(self)
        
        self.moveset = None
        self.position = position
        self.title = MovesetBuilderLabel(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        button_list = []
        
        for type_tuple in animation_types:
            button_list.append(MoveTypeButton(type_tuple[0], type_tuple[1], 20))
        
        self.buttons = button_list
        self.layout_buttons()
        self.add_children(button_list)
        
        self.buttons[0].handle_selected()
        
        navigator_position = (position[0] + 15, position[1] + self.height + 15)
        animation_navigator = AttackNavigator(navigator_position, 221, 250)
        animation_navigator.load_data(navigator_position, self.buttons[0].move_type)
        self.animation_navigator = animation_navigator
        
        self.add_child(animation_navigator)
        
        self.validation_tree = InputTree()
    
    def init_validation_tree(self):
        for attack_name, key_combination in self.moveset.attack_key_combinations.iteritems():
            self.validation_tree.add_branches(key_combination, attack_name)
    
    def selected_animation(self):
        
        return self.animation_navigator.selected_animation
    
    def get_thumbnail(self, animation_name):
        
        if animation_name in self.animation_navigator.animation_thumbnails:
            return self.animation_navigator.animation_thumbnails[animation_name]
    
    def get_attack_label(self, animation_name):
        
        if animation_name in self.animation_navigator.attack_label_dictionary:
            return self.animation_navigator.attack_label_dictionary[animation_name]
    
    def get_key_combination(self, animation_name):
        
        if animation_name in self.animation_navigator.attack_label_dictionary:
            return self.animation_navigator.attack_label_dictionary[animation_name].key_combination
    
    def set_key_combination(self, animation_name, key_combination):
        
        label = self.get_attack_label(animation_name)
        self.validation_tree.delete_value(label.key_combination)
        
        label.set_key_combination(key_combination)
        
        self.validation_tree.add_branches(key_combination, animation_name)
    
    def is_valid_command(self, key_combination):
        """check if the given key combination is allowed.  An empty key combination is
        allowed to remove an attack from a moveset.  Any other key combination must 
        contain an attack key"""
        
        if len(key_combination) == 0:
            return True
        
        for action_type in InputActionTypes.ATTACKS:
            if action_type in key_combination:
                return True
        
        return False
    
    def command_in_use(self, key_combination):
        """Check if a key combination is in use by another attack"""
        if self.validation_tree.get_value(key_combination) != None:
            return True
        else:
            return False
    
    def set_moveset(self, moveset):
        self.moveset = moveset
        self.sync_to_moveset()
        self.init_validation_tree()
    
    def sync_to_moveset(self):
        for label in self.animation_navigator.attack_labels:
            if label.attack_name in self.moveset.attack_key_combinations:
                label.set_key_combination(
                    self.moveset.attack_key_combinations[label.attack_name]
                )
    
    def save_to_moveset(self):
        for label in self.animation_navigator.attack_labels:
            if len(label.key_combination) > 0:
                self.moveset.save_attack_animation(
                    self.animation_navigator.get_animation(label.attack_name)
                )
                self.moveset.save_attack_key_combination(
                    label.attack_name,
                    label.key_combination
                )
                self.moveset.save_attack_type(
                    label.attack_name,
                    self.animation_navigator.animation_type
                )
            elif label.attack_name in self.moveset.attack_key_combinations:
                self.moveset.delete_attack(label.attack_name)
    
    def handle_events(self):
        reload_indicator = self.animation_navigator.reload_indicator
        
        self.animation_navigator.handle_events()
        
        if reload_indicator:
            self.sync_to_moveset()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            for button in self.buttons:
                if button.contains(wotsuievents.mouse_pos):
                    for other_button in self.buttons:
                        if other_button.selected and other_button != button:
                            other_button.handle_deselected()
                    
                    button.handle_selected()
                    self.save_to_moveset()
                    self.animation_navigator.animation_type = button.move_type
                    self.animation_navigator.load_animation_data()
                    self.animation_navigator.selected_animation = None
                    self.sync_to_moveset()

class AttackLabel(wotsui.SelectableObjectBase):
    def __init__(self, attack_name, key_combination):
        wotsui.SelectableObjectBase.__init__(self)
        
        self.attack_name = attack_name
        self.attack_name_label = button.Label((0,0), attack_name, (255,255,255), 17)
        self.key_combination = key_combination
        key_combination_position = (
            self.attack_name_label.position[0] + 20,
            self.attack_name_label.position[1] + self.attack_name_label.height + 5
        )
        self.key_combination_label = button.Label(
            key_combination_position,
            "--",
            (255,255,255),
            14
        )
        self.add_child(self.attack_name_label)
        self.add_child(self.key_combination_label)
    
    def handle_selected(self):
        wotsui.SelectableObjectBase.handle_selected(self)
        self.attack_name_label.text_color = (255,0,0)
    
    def handle_deselected(self):
        wotsui.SelectableObjectBase.handle_deselected(self)
        self.attack_name_label.text_color = (255,255,255)
    
    def draw_right(self):
        side_length = self.key_combination_label.height
        return_surface = pygame.Surface((side_length, side_length))
        
        point1 = (0, int(.5 * side_length))
        point2 = (side_length, int(.5 * side_length))
        point3 = (int(.6 * side_length, 0))
        point4 = (int(.6 * side_length, side_length))
        
        pygame.line.draw(return_surface, (255,255,255), point1, point2, 5)
        pygame.line.draw(return_surface, (255,255,255), point2, point3, 5)
        pygame.line.draw(return_surface, (255,255,255), point2, point4, 5)
    
    def draw_left(self):
        side_length = self.key_combination_label.height
        return_surface = pygame.Surface((side_length, side_length))
        
        point1 = (0, int(.5 * side_length))
        point2 = (side_length, int(.5 * side_length))
        point3 = (int(.4 * side_length, 0))
        point4 = (int(.4 * side_length, side_length))
        
        pygame.line.draw(return_surface, (255,255,255), point1, point2, 5)
        pygame.line.draw(return_surface, (255,255,255), point1, point3, 5)
        pygame.line.draw(return_surface, (255,255,255), point1, point4, 5)
    
    def draw_up(self):
        side_length = self.key_combination_label.height
        return_surface = pygame.Surface((side_length, side_length))
        
        point1 = (int(.5 * side_length), 0)
        point2 = (int(.5 * side_length), side_length)
        point3 = (0, int(.4 * side_length))
        point4 = (side_length, int(.4 * side_length))
        
        pygame.line.draw(return_surface, (255,255,255), point1, point2, 5)
        pygame.line.draw(return_surface, (255,255,255), point1, point3, 5)
        pygame.line.draw(return_surface, (255,255,255), point1, point4, 5)
    
    def draw_down(self):
        side_length = self.key_combination_label.height
        return_surface = pygame.Surface((side_length, side_length))
        
        point1 = (int(.5 * side_length), 0)
        point2 = (int(.5 * side_length), side_length)
        point3 = (0, int(.6 * side_length))
        point4 = (side_length, int(.6 * side_length))
        
        pygame.line.draw(return_surface, (255,255,255), point1, point2, 5)
        pygame.line.draw(return_surface, (255,255,255), point2, point3, 5)
        pygame.line.draw(return_surface, (255,255,255), point2, point4, 5)
    
    def set_key_combination(self, key_combination):
        self.key_combination = copy.deepcopy(key_combination)
        self.key_combination_label.set_text(" + ".join(
            [self.get_key_text(action_type) for action_type in key_combination]
        ))
        self.set_dimensions()
    
    def get_key_text(self, action_type):
        if action_type == InputActionTypes.FORWARD:
            return "FW"
            
        elif action_type == InputActionTypes.MOVE_UP:
            return "UP"
        
        elif action_type == InputActionTypes.MOVE_DOWN:
            return "DN"
        
        elif action_type == InputActionTypes.WEAK_KICK:
            return "QK"
        
        elif action_type == InputActionTypes.MEDIUM_KICK:
            return "TK"
        
        elif action_type == InputActionTypes.STRONG_KICK:
            return "SK"
        
        elif action_type == InputActionTypes.WEAK_PUNCH:
            return "QP"
        
        elif action_type == InputActionTypes.MEDIUM_PUNCH:
            return "TP"
        
        elif action_type == InputActionTypes.STRONG_PUNCH:
            return "SP"
        
        elif action_type == InputActionTypes.JUMP:
            return "JU"

class AttackNavigator(wotsuicontainers.ScrollableContainer):

    def __init__(self, position, width, height):
        wotsuicontainers.ScrollableContainer.__init__(self)
        
        self.reload_indicator = False
        self.set_layout_data(position, height, width)
        self.set_viewable_area(
            position,
            height - wotsuicontainers.SCROLL_BUTTON_HEIGHT,
            width - wotsuicontainers.SCROLL_BUTTON_WIDTH
        )
        
        self.attack_labels = []
        self.attack_label_dictionary = {}
        self.animation_thumbnails = {}
        self.animation_type = None
        self.selected_animation = None
        self.new_animation_button = button.TextButton("Create New Animation", 15)
        self.add_child(self.new_animation_button)
        
        self.edit_animation_button = button.TextButton("Edit Animation", 15)
        self.add_child(self.edit_animation_button)
        self.edit_animation_help_text = button.Label(
            (0,0),
            "Select an animation to edit",
            (255,255,255),
            14
        )
        self.add_child(self.edit_animation_help_text)
        self.edit_animation_help_text.hide()
        
        self.delete_animation_button = button.TextButton(
            "Delete Animation",
            15
        )
        self.add_child(self.delete_animation_button)
        self.delete_animation_help_text = button.Label(
            (0,0),
            "Select an animation to delete",
            (255,255,255),
            14
        )
        self.delete_animation_help_text.hide()
        self.add_child(self.delete_animation_help_text)
        
        self.gamestate_mode = gamestate.Modes.MOVESETBUILDER
        self.allow_multiple_select = False
    
    def load_data(self, position, animation_type):
        self.animation_type = animation_type
        self.set_layout_data(position, self.height, self.width)
        self.set_viewable_area(
            position,
            self.height - wotsuicontainers.SCROLL_BUTTON_HEIGHT,
            self.width - wotsuicontainers.SCROLL_BUTTON_WIDTH
        )
        
        new_animation_button_position = (
            position[0],
            position[1] + self.height + 5
        )
        self.new_animation_button.set_position(new_animation_button_position)
        
        edit_animation_button_position = (
            new_animation_button_position[0], 
            new_animation_button_position[1]  + self.new_animation_button.height + 5
        )
        self.edit_animation_button.set_position(edit_animation_button_position)
        edit_animation_help_text_position = (
            edit_animation_button_position[0] + self.edit_animation_button.width + 10,
            edit_animation_button_position[1]
        )
        self.edit_animation_help_text.set_position(
            edit_animation_help_text_position
        )
        
        delete_animation_button_position = (
            edit_animation_button_position[0],
            edit_animation_button_position[1] + self.edit_animation_button.height + 5
        )
        self.delete_animation_button.set_position(delete_animation_button_position)
        delete_animation_help_text_position = (
            delete_animation_button_position[0] + self.delete_animation_button.width + 10,
            delete_animation_button_position[1]
        )
        self.delete_animation_help_text.set_position(
            delete_animation_help_text_position
        )
        
        self.load_animation_data()
    
    def load_animation_data(self):
        if len(self.attack_labels) > 0:
            self.clear_data()
        
        for animation in self.get_animations():
            animation_thumbnail = AnimationThumbnail((0,0), animation)
            self.animation_thumbnails[animation.name] = animation_thumbnail
            attack_label = AttackLabel(animation.name, [])
            self.attack_labels.append(attack_label)
            self.attack_label_dictionary[animation.name] = attack_label
        
        if len(self.animation_thumbnails) > 0:
            self.layout_attack_labels()
            self.add_children(self.attack_labels, True)
        
        self.reset_scroll()
    
    def clear_data(self):
        self.remove_children(self.attack_labels, True)
        self.animation_thumbnails = {}
        self.attack_labels = []
        self.attack_label_dictionary = {}
    
    def get_animations(self):
        
        animations = actionwizard.get_attack_animations(self.animation_type)
        
        return sorted(animations, key=lambda animation: animation.name)
    
    def layout_attack_labels(self):
        current_position = (
            self.scrollable_area.position[0],
            self.scrollable_area.position[1]
        )
        attack_labels = self.attack_labels
        
        attack_labels[0].set_position(current_position)
        
        for i in range(1,len(attack_labels)):
            previous_label = attack_labels[i - 1]
            current_position = (
                previous_label.position[0], 
                previous_label.position[1] + previous_label.height + 3
            )
            attack_labels[i].set_position(current_position)
    
    def draw_relative(self, surface, position):
        wotsuicontainers.ScrollableContainer.draw_relative(self, surface, position)
        self.new_animation_button.draw_relative(surface, position)
        self.edit_animation_button.draw_relative(surface, position)
        self.delete_animation_button.draw_relative(surface, position)
    
    def get_animation(self, animation_name):
        return self.animation_thumbnails[animation_name].animation
    
    def get_thumbnail(self, animation_name):
        return self.animation_thumbnails[animation_name]
    
    def handle_events(self):
        wotsuicontainers.ScrollableContainer.handle_events(self)
        
        if self.reload_indicator:
            self.load_animation_data()
            self.reload_indicator = False
        
        if self.viewable_area.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if self.edit_animation_button.selected:
                    pass
                elif self.delete_animation_button.selected:
                    pass
                else:
                    for label in self.attack_labels:
                        if label.contains(wotsuievents.mouse_pos):
                            if self.allow_multiple_select:
                                if label.selected:
                                    label.handle_deselected()
                                    
                                    if self.selected_animation == self.get_animation(label.animation_name):
                                        self.selected_animation = None
                                else:
                                    label.handle_selected()
                            else:
                                for other_label in self.attack_labels:
                                    if other_label.selected:
                                        other_label.handle_deselected()
                                
                                label.handle_selected()
            elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
                for label in self.attack_labels:
                    if label.contains(wotsuievents.mouse_pos):
                        self.selected_animation = self.get_animation(
                            label.attack_name
                        )
                        
                        if self.edit_animation_button.selected:
                            self.edit_animation_button.handle_deselected()
                            frameeditor.load(
                                self.animation_type,
                                copy.deepcopy(self.get_animation(label.attack_name)),
                                self.gamestate_mode
                            )
                            gamestate.mode = gamestate.Modes.FRAMEEDITOR
                            self.edit_animation_help_text.hide()
                            self.reload_indicator = True
                            
                        elif self.delete_animation_button.selected:
                            actionwizard.delete_animation(
                                self.animation_type,
                                self.get_animation(label.attack_name)
                            )
                            self.selected_animation = None
                            self.load_animation_data()
                            self.delete_animation_button.handle_deselected()
                            self.delete_animation_help_text.hide()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if self.new_animation_button.contains(wotsuievents.mouse_pos):
                self.new_animation_button.handle_selected()
                self.selected_animation = animationexplorer.create_WOTS_animation()
                
                if self.edit_animation_button.selected:
                    self.edit_animation_button.handle_deselected()
            
            if self.edit_animation_button.contains(wotsuievents.mouse_pos):
                if self.edit_animation_button.selected:
                    self.edit_animation_button.handle_deselected()
                    self.edit_animation_help_text.hide()
                    
                else:
                    self.edit_animation_button.handle_selected()
                    self.edit_animation_help_text.show()
            
            if self.delete_animation_button.contains(wotsuievents.mouse_pos):
                if self.delete_animation_button.selected:
                    self.delete_animation_button.handle_deselected()
                    self.delete_animation_help_text.hide()
                    
                else:
                    self.delete_animation_button.handle_selected()
                    self.delete_animation_help_text.show()
                    
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            
            if (self.new_animation_button.selected and
            self.new_animation_button.contains(wotsuievents.mouse_pos)):
                if self.selected_animation != None:
                    new_animation = copy.deepcopy(self.selected_animation)
                    new_animation.name = ''
                    
                    frameeditor.load(
                        self.animation_type,
                        new_animation,
                        self.gamestate_mode
                    )
                    gamestate.mode = gamestate.Modes.FRAMEEDITOR
                    self.reload_indicator = True
                
                self.new_animation_button.handle_deselected()

if __name__ == "__main__":
    import sys

    # sys.stderr = open("logfile.txt","w")
    # sys.stdout = open("logfile_out.txt","w")

    import pygame

    from pygame.locals import *

    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=4096)
    pygame.init()
    pygame.font.init()

    import gamestate
    gamestate.init_pygame_vars()
    
    screen = gamestate.screen
    pygame.display.set_caption("Way of the Stick")
    attack_builder_container = AttackBuilderContainer()
    attack_builder_container.set_moveset(movesetdata.Moveset())
    
    while 1:
        if gamestate.drawing_mode == gamestate.DrawingModes.UPDATE_ALL:
            screen.fill((0,0,0))
        
        gamestate.time_passed = gamestate.clock.get_time()
        wotsuievents.get_events()
        
        events = wotsuievents.events
        event_types = wotsuievents.event_types
        mousePos = wotsuievents.mouse_pos
        mouseButtonsPressed = wotsuievents.mouse_buttons_pressed
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            attack_builder_container.handle_events()
            attack_builder_container.draw(gamestate.screen)
            
        if gamestate.drawing_mode == gamestate.DrawingModes.UPDATE_ALL:
            pygame.display.flip()
        elif gamestate.drawing_mode == gamestate.DrawingModes.DIRTY_RECTS:
            gamestate.update_screen()
        
        gamestate.clock.tick(gamestate.frame_rate)
