import sys
import copy

import pygame

import animation
import EditorTools

class PathTool(EditorTools.Tool):
    _SYMBOL_LINE_THICKNESS = 2
    
    def __init__(self):
        """creates a new path tool"""
        EditorTools.Tool.__init__(
            self,
            'fill',
            'Add filler frames between the current frame and the next frame.'
        )
        self.symbol = EditorTools.Symbol()
        self.symbol.draw = PathTool.draw_symbol
        
    def draw_symbol(self, surface):
        """draws the symbol of the path tool
        
        surface: the surface to draw the path tool's symbol on"""
        point1 = (self.button_center()[0] - 6, self.button_center()[1] - 6)
        point2 = (self.button_center()[0] - 6, self.button_center()[1] + 6)
        point3 = (self.button_center()[0] + 6, self.button_center()[1])
        point4 = (self.button_center()[0] - 12, self.button_center()[1])
        point5 = (self.button_center()[0] + 12, self.button_center()[1])
        
        pygame.draw.line(surface, \
                        self.color, \
                        point1, \
                        point3, \
                        PathTool._SYMBOL_LINE_THICKNESS)
        
        pygame.draw.line(surface, \
                        self.color, \
                        point2, \
                        point3, \
                        PathTool._SYMBOL_LINE_THICKNESS)
        
        pygame.draw.line(surface, \
                        self.color, \
                        point4, \
                        point5, \
                        PathTool._SYMBOL_LINE_THICKNESS)
    
    def init_state(self, animation):
        """initializes the state of this tool
        
        animation: the current animation"""
        EditorTools.Tool.init_state(self, animation)
        
        if len(animation.frames) > 1:
            self.insert_frames(5)
    
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
            self.color = EditorTools.Tool._InactiveColor
            self.symbol.color = EditorTools.Tool._InactiveColor
    
    def insert_frames(self, frame_count):
        """inserts linking frames between the current frame and the next
        frame
        
        frame_count: the number of frames to insert"""
        point_positions = self.get_point_positions(frame_count)
        start_frame_index = self.animation.frame_index
        
        if start_frame_index == len(self.animation.frames) - 1:
            for i in range(frame_count):
                prev_frame_index = start_frame_index + i
                
                new_frame = copy.deepcopy(self.animation.frames[prev_frame_index])
                
                for point in new_frame.points():
                    point.pos = point_positions[point.id][i]

                self.animation.frames.append(new_frame)
        else:
            end_frame = self.animation.frames[start_frame_index + 1]
            
            for i in range(frame_count):
                prev_frame_index = start_frame_index + i
                end_frame_index = self.animation.frames.index(end_frame)
                
                new_frame = copy.deepcopy(self.animation.frames[prev_frame_index])
                
                for point in new_frame.points():
                    point.pos = point_positions[point.id][i]
                
                self.animation.frames.insert(end_frame_index, new_frame)
        
    def get_point_positions(self, frame_count):
        """gets the positions of each point in each intermediary frame.
        
        frame_count: the number of frames to insert"""
        point_positions = {}
        frames = self.animation.frames
        frame_index = self.animation.frame_index
        
        start_frame = frames[frame_index]
        end_frame = None
        
        if self.animation.frame_index < len(self.animation.frames) - 1:
            end_frame = self.animation.frames[frame_index + 1]
        else:
            end_frame = self.animation.frames[0]
        
        for point in start_frame.points():
            point_positions[point.id] = []
            
            start_pos = point.pos
            end_pos = end_frame.point_dictionary[point.id].pos
            
            x_delta = end_pos[0] - start_pos[0]
            y_delta = end_pos[1] - start_pos[1]
            
            x_increment = x_delta / (frame_count + 1)
            y_increment = y_delta / (frame_count + 1)
            
            new_pos = (start_pos[0] + x_increment, \
                      start_pos[1] + y_increment)
            
            for i in range(frame_count):
                point_positions[point.id].append(new_pos)
                
                new_pos = (new_pos[0] + x_increment, \
                          new_pos[1] + y_increment)
        
        return point_positions
