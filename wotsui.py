class UIObjectBase():
    def __init__(self):
        self.position = (0,0)
        self.visible_position = (0,0)
        self.height = 0
        self.visible_height = 0
        self.width = 0
        self.visible_width = 0
        self.visible = True
        self.children = []
        self.surface = None
        self.fixed_position = False
        self.fixed_dimensions = False
    
    def set_layout_data(self, position, height, width):
        self.position = position
        self.height = height
        self.width = width
    
    def set_dimensions(self):
        """sets the height and width of a UIObjectBase based on its contents"""
        if not self.fixed_dimensions:
            if len(self.children) > 0:
                self.width = max([(child.position[0] + child.width) for child in self.children]) - \
                                     self.position[0]
                
                self.height = max([(child.position[1] + child.height) for child in self.children]) - \
                                      self.position[1]
            else:
                self.width = 0
                self.height = 0
    
    def set_visible_dimensions(self):
        """sets the height and width of a UIObjectBase based on its visible contents"""
        if not self.fixed_dimensions:
            if len(self.children) > 0:
                self.visible_width = max([(child.position[0] + child.width) for child in self.children if child.visible]) - \
                                     self.position[0]
                
                self.visible_height = max([(child.position[1] + child.height) for child in self.children if child.visible]) - \
                                      self.position[1]
            else:
                self.visible_width = 0
                self.visible_height = 0
    
    def evaluate_position(self):
        """finds the top left position of a UIObjectBase based on its contents"""
        if not self.fixed_position:
            self.position = (min([child.position[0] for child in self.children]), \
                             min([child.position[1] for child in self.children]))
    
    def set_visible_position(self):
        """finds the top left position of a UIObjectBase based on its visible contents"""
        if not self.fixed_position:
            self.visible_position = \
                (min([child.position[0] for child in self.children if child.visible]), \
                 min([child.position[1] for child in self.children if child.visible]))
    
    def get_relative_position(self, position):
        return (self.position[0] - position[0], self.position[1] - position[1])
    
    def set_position(self, new_position):
        x_shift = new_position[0] - self.position[0]
        y_shift = new_position[1] - self.position[1]
        
        self.shift(x_shift, y_shift)
    
    def draw(self, surface):
        
        for child in self.children:
            if child.visible:
                child.draw(surface)
    
    def draw_relative(self, surface, position):
        for child in self.children:
            if child.visible:
                child.draw_relative(surface, position)
    
    def hide(self):
        self.visible = False
        
        for child in self.children:
            child.hide()
    
    def show(self):
        self.visible = True
        
        for child in self.children:
            child.show()
    
    def shift(self, x_shift, y_shift):
        """moves a UIObjectBase and its children by the given distances
        
        x_shift: distance in pixels to move laterally
        y_shift: distance in pixels to move vertically"""
        self.position = (self.position[0] + x_shift, self.position[1] + y_shift)
        
        for child in self.children:
            child.shift(x_shift, y_shift)
    
    def center(self):
        return (self.position[0] + (self.width / 2), \
                self.position[1] + (self.height / 2))
    
    def center_relative(self, position):
        return (self.get_relative_position(position)[0] + (self.width / 2), \
                self.get_relative_position(position)[1] + (self.height / 2))
    
    def bottom_right(self):
        return (self.position[0] + self.width, self.position[1] + self.height)
    
    def bottom_right_relative(self, position):
        return (self.get_relative_position(position)[0] + self.width, \
                self.get_relative_position(position)[1] + self.height)
    
    def bottom_left(self):
        return (self.position[0], self.position[1] + self.height)
    
    def bottom_left_relative(self, position):
        return (self.get_relative_position(position)[0], \
                self.get_relative_position(position)[1] + self.height)
    
    def top_right(self):
        return (self.position[0] + self.width, self.position[1])
    
    def top_right_relative(self, position):
        return (self.get_relative_position(position)[0] + self.width, \
                self.get_relative_position(position)[1])
    
    def contains(self, position):
        """Indicates if a position lies within the area of a tool's
        button
        
        position:  position to test"""
        covers_position_indicator = False
        
        if ((self.position[0] <= position[0]) \
        and (self.position[1] <= position[1]) \
        and (self.bottom_right()[0] >= position[0]) \
        and (self.bottom_right()[1] >= position[1])):
            covers_position_indicator = True
        
        return covers_position_indicator
    
    def add_child(self, child):
        self.children.append(child)
        self.set_dimensions()
        self.set_visible_dimensions()
    
    def remove_child(self, child):
        self.children.remove(child)
        self.set_dimensions()
        self.set_visible_dimensions()
    
    def add_children(self, children):
        self.children.extend(children)
        self.set_dimensions()
        self.set_visible_dimensions()
    
    def remove_children(self, children):
        for child in children:
            self.children.remove(child)
        
        self.set_dimensions()
        self.set_visible_dimensions()
    
    def handle_events(self):
        pass

class SelectableObjectBase(UIObjectBase):
    def __init__(self):
        UIObjectBase.__init__(self)
        self.selected = False
        self.active = True
        self.color = (255,255,255)
        self.selected_color = (255,0,0)
        self.active_color = (255,255,255)
        self.inactive_color = (100,100,100)
    
    def activate(self):
        self.color = self.active_color
        self.active = True
    
    def inactivate(self):
        self.color = self.inactive_color
        self.active = False
        self.selected = False
    
    def handle_selected(self):
        self.color = self.selected_color
        self.selected = True
    
    def handle_deselected(self):
        self.color = self.active_color
        self.selected = False
