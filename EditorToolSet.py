import sys

import pygame

import EditorTools
import PointTool
import LineTool
import circletool
import addframetool
import playtool
import framenavigator
import pathtool
import removeframetool
import resizetool

_HorizontalPadding = 5
_VerticalPadding = 5
_ContainerLineThickness = 2

#Variables for drawing toolset
pos = (10, 10)
tools = []
point_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                  pos[1] + ToolSet._VerticalPadding)
tools.append(PointTool.PointTool(point_tool_pos))
resize_tool_pos = (pos[0] + (3 * ToolSet._HorizontalPadding) + \
                  EditorTools.Tool._ButtonWidth, \
                  pos[1] + ToolSet._VerticalPadding)
tools.append(resizetool.ResizeTool(resize_tool_pos))
line_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                pos[1] + (3 * ToolSet._VerticalPadding) + \
                EditorTools.Tool._ButtonHeight)
tools.append(LineTool.LineTool(line_tool_pos))
circle_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                pos[1] + (5 * ToolSet._VerticalPadding) + \
                (2 * EditorTools.Tool._ButtonHeight))
tools.append(circletool.CircleTool(circle_tool_pos))
add_frame_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                     pos[1] + (7 * ToolSet._VerticalPadding) + \
                     (3 * EditorTools.Tool._ButtonHeight))
tools.append(addframetool.AddFrameTool(add_frame_tool_pos))
play_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                pos[1] + (9 * ToolSet._VerticalPadding) + \
                (4 * EditorTools.Tool._ButtonHeight))
tools.append(playtool.PlayTool(play_tool_pos))
prev_frame_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                      pos[1] + (11 * ToolSet._VerticalPadding) + \
                      (5 * EditorTools.Tool._ButtonHeight))
tools.append(framenavigator.PrevFrameTool(prev_frame_tool_pos))
next_frame_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                      pos[1] + (13 * ToolSet._VerticalPadding) + \
                      (6 * EditorTools.Tool._ButtonHeight))
tools.append(framenavigator.NextFrameTool(next_frame_tool_pos))
path_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                pos[1] + (15 * ToolSet._VerticalPadding) + \
                (7 * EditorTools.Tool._ButtonHeight))
tools.append(pathtool.PathTool(path_tool_pos))
remove_frame_tool_pos = (pos[0] + ToolSet._HorizontalPadding, \
                        pos[1] + (17 * ToolSet._VerticalPadding) + \
                        (8 * EditorTools.Tool._ButtonHeight))
tools.append(removeframetool.RemoveFrameTool(remove_frame_tool_pos))

#Variables for managing state
currentTool = None
frame = None
animation = None
slctdTool = None

def init(slctd_animation):
    animation = slctd_animation
    frame = slctd_animation.frames[0]
    animation.frame_index = 0
    currentTool = None
    

def draw(self, surface):
    """Draws a tool set onto a surface
    
    surface: the surface to draw the tool set on"""
    for tool in tools:
        tool.draw(surface)

def handle_events(self, \
                 surface, \
                 mousePos, \
                 mouseButtonsPressed, \
                 events):
    """handles events based on the selected tool
    
    surface: a surface to draw on
    mousePos: current position of the mouse
    mouseButtonsPressed: list of buttons pushed at last iteration of main
    loop
    events: list of events on queue"""
    
    if slctd_tool != None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN: 
                slctd_tool = get_slctd_tool(mousePos)
                slctd_tool.color = EditorTools.slctdColor
            elif event.type == pygame.MOUSEBUTTONUP:
                if slctd_tool != None:
                    if slctd_tool.contains(mousePos)
                        if currentTool != None:
                            currentTool.clear_state()
                        
                        currentTool = slctd_tool
                        currentTool.init_state(animation)
                    else:
                        slctd_tool.color = EditorTools.inactiveColor
                        slctd_tool = None
    
    if currentTool != None:
        currentTool.handle_events(surface, \
                                  mousePos, \
                                  mouseButtonsPressed, \
                                  events)
    
    draw(surface)
    
def get_slctd_tool(mousePos):
    """Returns the tool that was clicked.  If no tool was clicked
    None is returned.
    
    mousePos: position of mouse"""
    slctdTool = None
    
    for tool in tools:
        if tool.contains(mousePos):
            slctdTool = tool
            break
    
    return slctdTool
