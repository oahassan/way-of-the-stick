import sys

import pygame
import animation
import EditorTools
import wotsui
import wotsuievents
import gamestate

REFERENCE_FRAME_PADDING = 15
FRAME_IMAGE_PADDING = 10

class ReferenceFrame(wotsui.SelectableObjectBase):
    
    def __init__(self, position, frame):
        wotsui.SelectableObjectBase.__init__(self)
        self.position = position
        self.selected_color = (0,0,255)
        self.active_color = (100, 100, 100)
        self.activate()
        self.position_delta = (
            frame.get_reference_position()[0] - position[0],
            frame.get_reference_position()[1] - position[1]
        )
        self.frame = frame
        self.height = animation.Animation._ThumbnailHeight
        self.contains_mouse = False
        
        if frame.image_height() < animation.Animation._ThumbnailHeight:
            self.scale = 1
        else:
            self.scale = animation.Animation._ThumbnailHeight / float(frame.image_height())
        
        self.width = self.scale * float(frame.image_width())
    
    def set_dimensions(self):
        self.height = animation.Animation._ThumbnailHeight
        self.width = self.scale * self.frame.image_width()
    
    def set_position(self, position):
        self.position = position
    
    def draw(self, surface):
        frame_position = self.frame.get_reference_position()
        
        self.position_delta = (
            self.position[0] - frame_position[0],
            self.position[1] - frame_position[1]
        )
        
        self.frame.draw(
                surface,
                self.color,
                self.scale,
                self.position_delta,
                animation.Animation._ThumbnailPointRadius,
                animation.Animation._ThumbnailLineThickness
            )
        
        if self.contains_mouse:
            border_top_left = (
                self.position[0] - FRAME_IMAGE_PADDING,
                self.position[1] - FRAME_IMAGE_PADDING
            )
            border_height = self.height + (2 * FRAME_IMAGE_PADDING)
            border_width = self.width + (2 * FRAME_IMAGE_PADDING)
            
            pygame.draw.rect(
                surface,
                (255,255,255),
                (border_top_left, (border_width, border_height)),
                3
            )
    
    def handle_events(self):
        self.set_dimensions()
        
        if self.contains(wotsuievents.mouse_pos):
            self.contains_mouse = True
        else:
            self.contains_mouse = False  

class FrameNavigator():
    def __init__(self, input_animation):
        self.animation = input_animation
        self.reference_frames = []
        self.create_reference_frames()
        self.reference_frame_index = 0
        self.active_reference_frame = self.reference_frames[0]
        self.active_reference_frame.handle_selected()
        self.layout_reference_frames(
            (REFERENCE_FRAME_PADDING, 
            gamestate._HEIGHT - (animation.Animation._ThumbnailHeight + REFERENCE_FRAME_PADDING)),
            0
        )
    
    def create_reference_frames(self):
        for frame in self.animation.frames:
            self.reference_frames.append(ReferenceFrame((0,0), frame))
    
    def update_reference_frames(self):
        #remove or add any deleted or added frames
        if len(self.animation.frames) != len(self.reference_frames):
            index = 0
            
            while self.animation.frames[index] == self.reference_frames[index].frame:
                index += 1
        
            start_position = self.reference_frames[index].position
            
            if len(self.animation.frames) < len(self.reference_frames):
                del self.reference_frames[index]
            else:
                self.reference_frames.insert(
                    index, 
                    ReferenceFrame((0,0),self.animation.frames[index])
                )
            
            self.layout_reference_frames(start_position, index)
    
    def update_active_reference_frame(self, frame_index):
        self.reference_frame_index = frame_index
        self.active_reference_frame.handle_deselected()
        self.active_reference_frame = self.reference_frames[frame_index]
        self.active_reference_frame.handle_selected()
    
    def update_reference_frame_positions(self):
        #re-position frames to keep active frames on the screen
        if self.active_reference_frame.position[0] < REFERENCE_FRAME_PADDING:
            self.shift_reference_frames(
                REFERENCE_FRAME_PADDING - self.active_reference_frame.position[0]
            )
        elif (self.active_reference_frame.position[0] + self.active_reference_frame.width 
        > gamestate._WIDTH + REFERENCE_FRAME_PADDING):
                self.shift_reference_frames(
                gamestate._WIDTH - REFERENCE_FRAME_PADDING - 
                self.active_reference_frame.position[0] - self.active_reference_frame.width
            )
    
    def shift_reference_frames(self, x_delta):
        for reference_frame in self.reference_frames:
            new_position = (reference_frame.position[0] + x_delta, reference_frame.position[1])
            reference_frame.set_position(new_position)
    
    def layout_reference_frames(self, start_position, start_index):
        current_position = (start_position[0], start_position[1])
        
        for i in range(start_index, len(self.reference_frames)):
            reference_frame = self.reference_frames[i]
            
            reference_frame.set_position(current_position)
            
            current_position = (
                current_position[0] + reference_frame.width + REFERENCE_FRAME_PADDING,
                current_position[1]
            )
    
    def draw(self, surface):
        
        for reference_frame in self.reference_frames:
            if (reference_frame.position[0] > 0
            and reference_frame.position[0] < gamestate._WIDTH):
                reference_frame.draw(surface)
    
    def handle_events(self):
        
        if self.reference_frame_index != self.animation.frame_index:
            self.update_active_reference_frame(self.animation.frame_index)
        
        self.update_reference_frames()
        self.update_reference_frame_positions()
        
        for i in range(len(self.reference_frames)):
            reference_frame = self.reference_frames[i]
            reference_frame.handle_events()
            
            if (wotsuievents.mousebutton_pressed()
            and reference_frame.contains_mouse):
                reference_frame.handle_selected()
            
            if (not wotsuievents.mousebutton_pressed() 
            and reference_frame.selected):
                if (reference_frame.contains_mouse
                and reference_frame != self.active_reference_frame):
                    self.active_reference_frame.handle_deselected()
                    self.active_reference_frame = reference_frame
                    self.reference_frame_index = i
                    self.animation.frame_index = i
                elif reference_frame != self.active_reference_frame:
                    reference_frame.handle_deselected()
        

class MoveFrameLeftTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new move frame left tool"""
        EditorTools.Tool.__init__(
            self,
            'move frame',
            'Move the current frame before the previous frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = MoveFrameLeftTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new previous frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.move_frame_left()
        self.frame_count = 0
    
    def move_frame_left(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index > 0:
            frames = self.animation.frames
            frame_index = self.animation.frame_index
            self.animation.frames = frames[:frame_index - 1] + [frames[frame_index]] + [frames[frame_index - 1]] + frames[frame_index + 1:]
            self.animation.frame_index -= 1
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor
    
    def draw_symbol(self, surface):
        """draws the symbol for the previous frame tool"""
        point1 = (self.button_center()[0] - 5, self.button_center()[1])
        point2 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        point3 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point4 = (self.button_center()[0] + 10, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point2, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point3, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point4, \
                        MoveFrameLeftTool._SYMBOL_LINE_THICKNESS)

class MoveFrameRightTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new move frame right tool"""
        EditorTools.Tool.__init__(
            self,
            'move frame',
            'Move the current frame after the next frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = MoveFrameRightTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new next frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.move_frame_right()
        self.frame_count = 0
    
    def move_frame_right(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index < len(self.animation.frames) - 1:
            frames = self.animation.frames
            frame_index = self.animation.frame_index
            self.animation.frames = frames[:frame_index] + [frames[frame_index + 1]] + [frames[frame_index]] + frames[frame_index + 2:]
            self.animation.frame_index += 1
    
    def draw_symbol(self, surface):
        """draws the symbol for the next frame tool"""
        point1 = (self.button_center()[0] + 5, self.button_center()[1])
        point2 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        point3 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point4 = (self.button_center()[0] - 10, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point2, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point3, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point1, \
                        point4, \
                        MoveFrameRightTool._SYMBOL_LINE_THICKNESS)
                        
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor

class PrevFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new previous frame tool"""
        EditorTools.Tool.__init__(
            self,
            'prev. frame',
            'Edit the previous frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = PrevFrameTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new previous frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.go_to_prev_frame()
        self.frame_count = 0
    
    def go_to_prev_frame(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index > 0:
            self.animation.frame_index -= 1
    
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor
    
    def draw_symbol(self, surface):
        """draws the symbol for the previous frame tool"""
        point1 = (self.button_center()[0] - 5, self.button_center()[1])
        point2 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        point3 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point4 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point5 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        
        pygame.draw.polygon(surface, \
                            self.symbol.color, \
                            (point1, point2, point3), \
                            PrevFrameTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point4, \
                        point5, \
                        PrevFrameTool._SYMBOL_LINE_THICKNESS)
        
class NextFrameTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 3
    
    def __init__(self):
        """Creates a new next frame tool"""
        EditorTools.Tool.__init__(
            self,
            'next frame',
            'Edit the next frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = NextFrameTool.draw_symbol
    
    def init_state(self, animation):
        """sets the state of a new next frame tool
        
        animation: the current animation being edited"""
        EditorTools.Tool.init_state(self, animation)
        self.go_to_next_frame()
        self.frame_count = 0
    
    def go_to_next_frame(self):
        """decrements the frame index of the animation"""
        
        if self.animation.frame_index < len(self.animation.frames) - 1:
            self.animation.frame_index += 1
    
    def draw_symbol(self, surface):
        """draws the symbol for the next frame tool"""
        point1 = (self.button_center()[0] + 5, self.button_center()[1])
        point2 = (self.button_center()[0] - 5, self.button_center()[1] - 3)
        point3 = (self.button_center()[0] - 5, self.button_center()[1] + 3)
        point4 = (self.button_center()[0] + 5, self.button_center()[1] - 3)
        point5 = (self.button_center()[0] + 5, self.button_center()[1] + 3)
        
        pygame.draw.polygon(surface, \
                            self.symbol.color, \
                            (point1, point2, point3), \
                            NextFrameTool._SYMBOL_LINE_THICKNESS)
        pygame.draw.line(surface, \
                        self.symbol.color, \
                        point4, \
                        point5, \
                        NextFrameTool._SYMBOL_LINE_THICKNESS)
                        
    def handle_events(self, \
                     surface, \
                     mousePos, \
                     mouseButtonsPressed, \
                     events):
        event_types = []
        
        for event in events:
            event_types.append(event.type)
        
        if pygame.QUIT in event_types:
            sys.exit()
        else:
            self.frame_count += 1
            
            if self.frame_count >= 5:
                self.color = EditorTools.Tool._InactiveColor
                self.symbol.color = EditorTools.Tool._InactiveColor
