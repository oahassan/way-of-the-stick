import pygame

import wotsui
import wotsuicontainers
import wotsuievents
import button

class RowEntry(wotsui.UIObjectBase):
    def __init__(self, ip_address):
        wotsui.UIObjectBase.__init__(self)
        
        self.ip_address = button.SelectableLabel((0,0), str(ip_address), 32)
        self.add_child(self.ip_address)
        self.width = 450
    
    def handle_selected(self):
        for child in self.children:
            child.handle_selected()
    
    def handle_deselected(self):
        for child in self.children:
            child.handle_deselected()
    
    def activate(self):
        for child in self.children:
            child.activate()
            
    def inactivate(self):
        for child in self.children:
            child.inactivate()
    
    def get_address(self):
        return self.ip_address.text

class ServerTable(wotsuicontainers.ScrollableContainer):
    
    def __init__(self, position):
        wotsuicontainers.ScrollableContainer.__init__(self)
        
        self.allow_multiple_select = False
        
        self.selected_row = None
        
        self.set_layout_data(
            position,
            300,
            500
        )
        self.set_viewable_area(
            position,
            300 - wotsuicontainers.SCROLL_BUTTON_HEIGHT,
            500 - wotsuicontainers.SCROLL_BUTTON_WIDTH
        )
    
    def add_server_address(self, ip_address):
        server_row = RowEntry(ip_address)
        server_row.set_position(self.get_address_position())
        
        self.add_child(server_row, True)
        
        #self.reset_scroll()
    
    def get_address_position(self):
        x_position = self.position[0]
        y_position = self.scrollable_area.position[1] + self.scrollable_area.height
        
        return [x_position, y_position]
            
    def handle_events(self):
        wotsuicontainers.ScrollableContainer.handle_events(self)
        
        for address_row in self.scrollable_area.children:
            if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
                if address_row.contains(wotsuievents.mouse_pos):
                    address_row.handle_selected()
                    
                    if self.selected_row != None:
                        self.selected_row.handle_deselected()
                    
                    self.selected_row = address_row
    
    def draw(self, surface):
        wotsuicontainers.ScrollableContainer.draw(self, surface)
        
        pygame.draw.line(
            surface,
            (255,255,255),
            self.viewable_area.position,
            self.viewable_area.top_right()
        )
