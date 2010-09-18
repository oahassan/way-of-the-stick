import pygame
import eztext

import wotsui
import wotsuievents
import button

SCROLL_LEFT = "SCROLL_LEFT"
SCROLL_RIGHT = "SCROLL_RIGHT"
SCROLL_UP = "SCROLL_UP"
SCROLL_DOWN = "SCROLL_DOWN"
SCROLL_BUTTON_HEIGHT = 15
SCROLL_BUTTON_WIDTH = 15

class ScrollableContainer(wotsui.UIObjectBase):
    def __init__(self):
        wotsui.UIObjectBase.__init__(self)
        
        self.viewable_area = None
        self.scrollable_area = None
        self.scrollbar_width = 0
        self.vertical_scroll_distance = 0
        self.vertical_scrollbar = None
        self.horizontal_scrollbar = None
    
    def set_viewable_area(self, position, height, width):
        viewable_area = wotsui.UIObjectBase()
        viewable_area.position = position
        viewable_area.height = height
        viewable_area.width = width
        viewable_area.surface = pygame.Surface((width, height))
        viewable_area.fixed_dimensions = True
        self.viewable_area = viewable_area
        self.add_child(viewable_area)
        
        scrollable_area = wotsui.UIObjectBase()
        scrollable_area.position = position
        self.scrollable_area = scrollable_area
    
    def show(self):
        self.visible = True
        
        self.scrollable_area.show()
        self.viewable_area.show()
        
        if self.is_vertically_scrollable():
            self.vertical_scrollbar.show()
        
        if self.is_horizontally_scrollable():
            self.horizontal_scrollbar.show()
        
        for child in self.children:
            if ((child != self.scrollable_area)
            and (child != self.viewable_area)
            and (child != self.vertical_scrollbar)
            and (child != self.horizontal_scrollbar)):
                child.show()
    
    def is_vertically_scrollable(self):
        return self.scrollable_area.height > self.viewable_area.height
    
    def is_horizontally_scrollable(self):
        return self.scrollable_area.width > self.viewable_area.width
    
    def init_vertical_scrollbar(self):
        if self.vertical_scrollbar != None:
            self.remove_child(self.vertical_scrollbar)
        
        vertical_scrollbar = VerticalScrollBar()
        scrollbar_position = (self.viewable_area.position[0] + self.viewable_area.width, \
                              self.viewable_area.position[1])
        scrollbar_track_height = self.viewable_area.height - (2 * SCROLL_BUTTON_HEIGHT)
        bar_height = 0
        
        self.scrollable_area.position = self.viewable_area.position
        
        if self.scrollable_area.height > 0:
           bar_height = (float(self.viewable_area.height) / self.scrollable_area.height) * scrollbar_track_height
        
        vertical_scrollbar.create_children()
        vertical_scrollbar.set_layout_data(scrollbar_position, \
                                            self.viewable_area.height, \
                                            bar_height)
        vertical_scrollbar.hide()
        self.vertical_scrollbar = vertical_scrollbar
        self.add_child(vertical_scrollbar)
    
    def get_scrollable_height(self):
        return self.scrollable_area.height - self.viewable_area.height
    
    def get_scrolled_height(self):
        return abs(self.viewable_area.position[1] - self.scrollable_area.position[1])
    
    def get_vertical_scroll_percent(self):
        scrollable_height = self.get_scrollable_height()
        scrolled_height = self.get_scrolled_height()
        
        percent = 0
        
        if scrollable_height > 0:
            percent = float(scrolled_height) / scrollable_height
        
        return percent
    
    def init_horizontal_scrollbar(self):
        if self.horizontal_scrollbar != None:
            self.remove_child(self.horizontal_scrollbar)
        
        horizontal_scrollbar = HorizontalScrollBar()
        scrollbar_position = (self.viewable_area.position[0], \
                              self.viewable_area.position[1] + self.viewable_area.height)
        scrollbar_track_width = self.viewable_area.width - (2 * SCROLL_BUTTON_WIDTH)
        bar_width = 0 
        
        self.scrollable_area.position = self.viewable_area.position
        
        if self.scrollable_area.width > 0:
            bar_width = (float(self.viewable_area.width) / self.scrollable_area.width) * scrollbar_track_width
        
        horizontal_scrollbar.create_children()
        horizontal_scrollbar.set_layout_data(scrollbar_position, \
                                             self.viewable_area.width, \
                                             bar_width)
        horizontal_scrollbar.hide()
        self.horizontal_scrollbar = horizontal_scrollbar
        self.add_child(horizontal_scrollbar)
    
    def get_scrollable_width(self):
        return self.scrollable_area.width - self.viewable_area.width
    
    def get_scrolled_width(self):
        return abs(self.viewable_area.position[0] - self.scrollable_area.position[0])
    
    def get_horizontal_scroll_percent(self):
        scrollable_width = self.get_scrollable_width()
        scrolled_width = self.get_scrolled_width()
        
        percent = 0
        
        if scrollable_width > 0:
            percent = float(scrolled_width) / scrollable_width
        
        return percent
    
    def handle_events(self):
        self.handle_vertical_scroll_events()
        self.handle_horizontal_scroll_events()
        
        # if self.viewable_area.contains(wotsuievents.mouse_pos):
            # self.scrollable_area.handle_events()
        
        for child in self.children:
            if child.visible:
                child.handle_events()
    
    def handle_vertical_scroll_events(self):
        vertical_scrollbar = self.vertical_scrollbar
        
        if (self.is_vertically_scrollable() and
            (not vertical_scrollbar.visible)):
            self.init_vertical_scrollbar()
            vertical_scrollbar = self.vertical_scrollbar
            vertical_scrollbar.show()
        
        if ((not self.is_vertically_scrollable()) and
            (vertical_scrollbar.visible)):
            print('hiding scrollbar')
            vertical_scrollbar.hide()
        
        if vertical_scrollbar.visible:
            vertical_scrollbar.handle_events()
            
            scroll_percent = self.get_vertical_scroll_percent()
            scrollbar_scroll_percent = vertical_scrollbar.get_scroll_percent()
            
            if scroll_percent != scrollbar_scroll_percent:
                new_scroll_height = self.get_scrollable_height() * scrollbar_scroll_percent
                scroll_distance = self.get_scrolled_height() - new_scroll_height
                self.scrollable_area.shift(0,scroll_distance)
    
    def handle_horizontal_scroll_events(self):
        horizontal_scrollbar = self.horizontal_scrollbar
        
        if (self.is_horizontally_scrollable() and
            (not horizontal_scrollbar.visible)):
            self.init_horizontal_scrollbar()
            horizontal_scrollbar = self.horizontal_scrollbar
            horizontal_scrollbar.show()
        
        if ((not self.is_horizontally_scrollable()) and
            (horizontal_scrollbar.visible)):
            horizontal_scrollbar.hide()
        
        if horizontal_scrollbar.visible:
            horizontal_scrollbar.handle_events()
            
            scroll_percent = self.get_horizontal_scroll_percent()
            scrollbar_scroll_percent = horizontal_scrollbar.get_scroll_percent()
            
            if scroll_percent != scrollbar_scroll_percent:
                new_scroll_width = self.get_scrollable_width() * scrollbar_scroll_percent
                scroll_distance = self.get_scrolled_width() - new_scroll_width
                self.scrollable_area.shift(scroll_distance,0)
    
    def add_child(self, child, scrollable_indicator=False):
        
        if scrollable_indicator:
            self.scrollable_area.add_child(child)
            
            self.set_dimensions()
            self.set_visible_dimensions()
        else:
            wotsui.UIObjectBase.add_child(self, child)
    
    def remove_child(self, child, scrollable_indicator=False):
        
        if scrollable_indicator:
            self.scrollable_area.remove_child(child)
            
            self.set_dimensions()
            self.set_visible_dimensions()
        else:
            wotsui.UIObjectBase.remove_child(self, child)
    
    def add_children(self, children, scrollable_indicator=False):
        
        if scrollable_indicator:
            self.scrollable_area.add_children(children)
            
            self.set_dimensions()
            self.set_visible_dimensions()
        else:
            wotsui.UIObjectBase.add_children(self, children)
    
    def remove_children(self, children, scrollable_indicator=False):
        if scrollable_indicator:
            self.scrollable_area.remove_children(children)
            
            self.set_dimensions()
            self.set_visible_dimensions()
        else:
            wotsui.UIObjectBase.remove_child(self, children)
    
    def draw(self, surface):
        viewable_area_surface = self.viewable_area.surface
        viewable_area_surface.fill((0,0,0))
        
        self.scrollable_area.draw_relative(viewable_area_surface, self.viewable_area.position)
        
        surface.blit(viewable_area_surface, self.viewable_area.position)
        
        for child in self.children:
            if ((child != self.scrollable_area) and
                (child != self.viewable_area)):
                child.draw(surface)
    
    def draw_relative(self, surface, reference_position):
        self.vertical_scrollbar.draw_relative(surface, reference_position)
        self.horizontal_scrollbar.draw_relative(surface, reference_position)
        
        viewable_area_surface = self.viewable_area.surface
        
        self.scrollable_area.draw_relative(viewable_area_surface, self.viewable_area.position)
        
        surface.blit(viewable_area_surface, self.viewable_area.get_relative_position(reference_position))

class Track(wotsui.UIObjectBase):
    def __init__(self):
        wotsui.UIObjectBase.__init__(self)
        self.color = (100,100,100)
        self.fixed_dimensions = True
    
    def draw(self, surface):
        draw_rect = pygame.Rect(self.position, (self.width, self.height))
        
        pygame.draw.rect(surface, self.color, draw_rect)
    
    def draw_relative(self, surface, position):
        draw_rect = pygame.Rect(self.get_relative_position(), (self.width, self.height))
        
        pygame.draw.rect(surface, self.color, draw_rect)

class Bar(wotsui.SelectableObjectBase):
    def __init__(self):
        wotsui.SelectableObjectBase.__init__(self)
        self.color = (255,255,255)
        self.fixed_dimensions = True
    
    def draw(self, surface):
        draw_rect = pygame.Rect(self.position, (self.width, self.height))
        
        pygame.draw.rect(surface, self.color, draw_rect)
        
    def draw_relative(self, surface, position):
        draw_rect = pygame.Rect(self.get_relative_position(), (self.width, self.height))
        
        pygame.draw.rect(surface, self.color, draw_rect)

class ScrollButton(button.Button):
    def __init__(self, direction):
        button.Button.__init__(self)
        self.direction = direction
        self.fixed_dimensions = True
    
    def set_layout_data(self, position):
        wotsui.UIObjectBase.set_layout_data(self, position, SCROLL_BUTTON_HEIGHT, SCROLL_BUTTON_WIDTH)
    
    def draw(self, surface):
        if self.direction == SCROLL_LEFT:
            self._draw_left_button(surface)
        elif self.direction == SCROLL_RIGHT:
            self._draw_right_button(surface)
        elif self.direction == SCROLL_UP:
            self._draw_up_button(surface)
        elif self.direction == SCROLL_DOWN:
            self._draw_down_button(surface)
    
    def _draw_left_button(self, surface):
        tip_point = (self.position[0], self.center()[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, self.top_right(), self.bottom_right()])
    
    def _draw_right_button(self, surface):
        tip_point = (self.position[0] + self.width, self.center()[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, self.position, self.bottom_left()])
    
    def _draw_up_button(self, surface):
        tip_point = (self.center()[0], self.position[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, self.bottom_right(), self.bottom_left()])
    
    def _draw_down_button(self, surface):
        tip_point = (self.center()[0], self.position[1] + self.height)
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, self.position, self.top_right()])
    
    def draw_relative(self, surface, position):
        if self.direction == SCROLL_LEFT:
            self._draw_left_button_relative(surface, position)
        elif self.direction == SCROLL_RIGHT:
            self._draw_right_button_relative(surface, position)
        elif self.direction == SCROLL_UP:
            self._draw_up_button_relative(surface, position)
        elif self.direction == SCROLL_DOWN:
            self._draw_down_button_relative(surface, position)
    
    def _draw_left_button_relative(self, surface, position):
        tip_point = (self.get_relative_position(position)[0], \
                     self.center_relative(position)[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, \
                             self.top_right_relative(position), \
                             self.bottom_right_relative(position)])
    
    def _draw_right_button_relative(self, surface, position):
        tip_point = (self.get_relative_position(position)[0] + self.width, \
                     self.center_relative(position)[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, \
                             self.get_relative_position(position), \
                             self.bottom_left_relative(position)])
    
    def _draw_up_button_relative(self, surface, position):
        tip_point = (self.center_relative(position)[0], \
                     self.get_relative_position(position)[1])
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, \
                             self.bottom_right_relative(position), \
                             self.bottom_left_relative(position)])
    
    def _draw_down_button_relative(self, surface, position):
        tip_point = (self.center_relative(position)[0], \
                     self.get_relative_position(position)[1] + self.height)
        
        pygame.draw.polygon(surface, \
                            self.color, \
                            [tip_point, \
                             self.get_relative_position(position), \
                             self.top_right_relative(position)])

class VerticalScrollBar(wotsui.UIObjectBase):
    def __init__(self):
        wotsui.UIObjectBase.__init__(self)
        self.scroll_up_button = None
        self.scroll_down_button = None
        self.bar = None
        self.track = None
        self.scroll_increment = 1
    
    def create_children(self):
        self.scroll_up_button = ScrollButton(SCROLL_UP)
        self.scroll_down_button = ScrollButton(SCROLL_DOWN)
        self.bar = Bar()
        self.track = Track()
        
        self.add_children([self.scroll_up_button, \
                           self.scroll_down_button, \
                           self.track, \
                           self.bar])
    
    def set_layout_data(self, position, height, bar_height):
        wotsui.UIObjectBase.set_layout_data(self, position, height, SCROLL_BUTTON_WIDTH)
        
        track_width = SCROLL_BUTTON_WIDTH
        track_height = height - (2 * SCROLL_BUTTON_HEIGHT)
        track_position = (position[0], position[1] + SCROLL_BUTTON_HEIGHT)
        self.track.set_layout_data(track_position, track_height, track_width)
        
        self.scroll_up_button.set_layout_data(position)
        
        scroll_down_button_position = (position[0], \
                                       position[1] + height - SCROLL_BUTTON_HEIGHT)
        self.scroll_down_button.set_layout_data(scroll_down_button_position)
        
        bar_position = (position[0] + 1, position[1] + SCROLL_BUTTON_HEIGHT)
        self.bar.set_layout_data(bar_position, \
                                 bar_height, \
                                 SCROLL_BUTTON_WIDTH - 2)
    
    def scrollable_height(self):
        return self.track.height - self.bar.height
    
    def scrolled_distance(self):
        return self.bar.position[1] - self.track.position[1]
    
    def get_scroll_percent(self):
        return float(self.scrolled_distance()) / self.scrollable_height()
    
    def scroll(self, distance):
        
        bar_position = self.bar.position
        self.bar.position = (bar_position[0], bar_position[1] + distance)
        
        scroll_percent = self.get_scroll_percent()
        
        if scroll_percent > 1:
            self.bar.position = (bar_position[0], self.track.position[1] + self.scrollable_height())
        elif scroll_percent < 0:
            self.bar.position = (bar_position[0], self.track.position[1])
    
    def handle_events(self):
        scroll_down_button = self.scroll_down_button
        scroll_up_button = self.scroll_up_button
        bar = self.bar
        
        if scroll_down_button.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not scroll_down_button.selected:
                    scroll_down_button.handle_selected()
                
                self.scroll(self.scroll_increment)
        
        if scroll_up_button.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not scroll_up_button.selected:
                    scroll_up_button.handle_selected()
                
                self.scroll(-1 * self.scroll_increment)
        
        if bar.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not bar.selected:
                    bar.handle_selected()
                
                self.scroll(wotsuievents.mouse_delta[1])
        
        if pygame.MOUSEMOTION in wotsuievents.event_types:
            if bar.selected:
                self.scroll(wotsuievents.mouse_delta[1])
        
        if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if bar.selected:
                bar.handle_deselected()
            if scroll_up_button.selected:
                scroll_up_button.handle_deselected()
            if scroll_down_button.selected:
                scroll_down_button.handle_deselected()

class HorizontalScrollBar(wotsui.UIObjectBase):
    def __init__(self):
        wotsui.UIObjectBase.__init__(self)
        self.scroll_left_button = None
        self.scroll_right_button = None
        self.bar = None
        self.track = None
        self.scroll_increment = 1
    
    def create_children(self):
        self.scroll_left_button = ScrollButton(SCROLL_LEFT)
        self.scroll_right_button = ScrollButton(SCROLL_RIGHT)
        self.bar = Bar()
        self.track = Track()
        
        self.add_children([self.scroll_left_button, \
                           self.scroll_right_button, \
                           self.track, \
                           self.bar])
    
    def set_layout_data(self, position, width, bar_width):
        wotsui.UIObjectBase.set_layout_data(self, position, SCROLL_BUTTON_HEIGHT, width)
        
        track_height = SCROLL_BUTTON_HEIGHT
        track_width = width - (2 * SCROLL_BUTTON_HEIGHT)
        track_position = (position[0] + SCROLL_BUTTON_WIDTH, position[1])
        self.track.set_layout_data(track_position, track_height, track_width)
        
        self.scroll_left_button.set_layout_data(position)
        
        scroll_right_button_position = (position[0] + width - SCROLL_BUTTON_WIDTH, \
                                        position[1])
        self.scroll_right_button.set_layout_data(scroll_right_button_position)
        
        bar_position = (position[0] + SCROLL_BUTTON_WIDTH, position[1])
        self.bar.set_layout_data(bar_position, SCROLL_BUTTON_HEIGHT, bar_width)
    
    def scrollable_width(self):
        return self.track.width - self.bar.width
    
    def scrolled_distance(self):
        return self.bar.position[0] - self.track.position[0]
    
    def get_scroll_percent(self):
        return float(self.scrolled_distance()) / self.scrollable_width()
    
    def scroll(self, distance):
        
        bar_position = self.bar.position
        self.bar.position = (bar_position[0] + distance, bar_position[1])
        
        scroll_percent = self.get_scroll_percent()
        
        if scroll_percent > 1:
            self.bar.position = (self.track.position[0] + self.scrollable_width(), bar_position[1])
        elif scroll_percent < 0:
            self.bar.position = (self.track.position[0], bar_position[1])
    
    def handle_events(self):
        scroll_left_button = self.scroll_left_button
        scroll_right_button = self.scroll_right_button
        bar = self.bar
        
        if scroll_right_button.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not scroll_right_button.selected:
                    scroll_right_button.handle_selected()
                # print("scroll right")
                # print(self.scrolled_distance())
                self.scroll(self.scroll_increment)
        
        if scroll_left_button.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not scroll_left_button.selected:
                    scroll_left_button.handle_selected()
                # print("scroll left")
                # print(self.scrolled_distance())
                self.scroll(-1 * self.scroll_increment)
        
        if bar.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if not bar.selected:
                    bar.handle_selected()
                
                self.scroll(wotsuievents.mouse_delta[0])
        
        if pygame.MOUSEMOTION in wotsuievents.event_types:
            if bar.selected:
                self.scroll(wotsuievents.mouse_delta[0])
        
        if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if bar.selected:
                bar.handle_deselected()
            if scroll_right_button.selected:
                scroll_right_button.handle_deselected()
            if scroll_left_button.selected:
                scroll_left_button.handle_deselected()

class ButtonContainer(ScrollableContainer):
    def __init__(self, position, height, width, title_text, button_class, button_args=None):
        ScrollableContainer.__init__(self)
        
        self.title = button.Label(position, title_text, (255,255,255), 22)
        self.add_child(self.title)
        
        self.set_layout_data(position, \
                             height, \
                             width)
        self.set_viewable_area(position, \
                               height - SCROLL_BUTTON_HEIGHT, \
                               width - SCROLL_BUTTON_WIDTH)
        
        button_list = []
        
        for button_arg in button_args:
            button_list.append(button_class(*button_arg))
        
        self.buttons = button_list
        self.layout_buttons()
        self.add_children(button_list, True)
        
        self.selected_button = None
    
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
    
    def has_button(self, button_name):
        has_button_indicator = False
        
        for button in self.buttons:
            if button.text == button_name:
                has_button_indicator = True
                break
        
        return has_button_indicator
    
    def add_button(self, button_name):
        button = button.TextButton(button_name, 20)
        
        self.buttons.append(button)
        self.add_child(button, True)
        self.layout_buttons()
    
    def remove_button(self, button_name):
        for button in self.buttons:
            if button.text == button_name:
                self.buttons.remove(button)
                self.remove_child(button, True)
                
                if len(self.buttons) > 0:
                    self.layout_buttons()
                break

class TextEntryBox(wotsui.SelectableObjectBase):
    
    def __init__(
        self,
        prompt_text = '',
        max_length = 100,
        position = (0, 0),
        text_color =(255, 255, 255)
    ):
        wotsui.SelectableObjectBase.__init__(self)
        self.moveset = None
        
        self.text_entry_box = \
            eztext.Input(
                maxlength = max_length,
                x = position[0],
                y = position[1],
                prompt = prompt_text,
                color = text_color,
                font = pygame.font.Font('freesansbold.ttf', 30)
            )
        
        self.set_layout_data(
            position,
            self.text_entry_box.height, \
            self.text_entry_box.width
        )
    
    def set_position(self, position):
        """moves the top left of the text entry box to the given position"""
        wotsui.SelectableObjectBase.set_position(self, position)
        self.text_entry_box.set_position(position)
    
    def draw(self, surface):
        self.text_entry_box.draw(surface)
    
    def _update(self):
        """sends events to the eztext entry box to update its text and resizes
        the text entry box accordingly"""
        self.text_entry_box.update(wotsuievents.events)
        
        self.set_layout_data(
            self.position,
            self.text_entry_box.height, \
            self.text_entry_box.width
        )
    
    def handle_events(self):
        """handle events that affect the text entry box"""
        if self.contains(wotsuievents.mouse_pos):
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if self.selected:
                    self.handle_deselected()
                    
                else:
                    self.handle_selected()
                
                self.text_entry_box.color = self.color
        
        if self.selected:
            self._update()
