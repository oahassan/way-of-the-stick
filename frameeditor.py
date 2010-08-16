import pygame

import gamestate
import button
import EditorTools
import pulltool
import LineTool
import circletool
import addframetool
import playtool
import framenavigator
import pathtool
import removeframetool
import resizetool
import savetool
import animation
import stick


_HORIZONTAL_PADDING = 5
_VERTICAL_PADDING = 5
_ContainerLineThickness = 2
_TOOL_SET_POS = (0,0)

tools = []
exit_button = button.ExitButton()
animation = None
currentTool = None
slctd_tool = None
previous_tool = None
exit_state = gamestate.Modes.ANIMATIONEXPLORER
exit_ind = False
loaded = False

def load(animation_type, edit_animation, rtn_state):
    global animation
    global currentTool
    global slctd_tool
    global previous_tool
    global exit_ind
    global exit_state
    global tools
    global loaded
    
    animation = edit_animation
    animation.frame_index = 0
    currentTool = None
    slctd_tool = None
    previous_tool = None
    exit_ind = False
    exit_state = rtn_state
    
    tools = []
    tools.append(pulltool.PullTool())
    tools.append(resizetool.ResizeTool())
    # tools.append(LineTool.LineTool())
    # tools.append(circletool.CircleTool())
    tools.append(addframetool.AddFrameTool())
    tools.append(removeframetool.RemoveFrameTool())
    
    tools.append(framenavigator.MoveFrameLeftTool())
    tools.append(framenavigator.MoveFrameRightTool())
    tools.append(framenavigator.PrevFrameTool())
    tools.append(framenavigator.NextFrameTool())
    tools.append(pathtool.PathTool())
    tools.append(playtool.PlayTool())
    
    save_tool = savetool.SaveTool()
    save_tool.animation_type = animation_type
    tools.append(save_tool)
    
    layout_tools()
    loaded = True

def unload():
    global animation
    global currentTool
    global slctd_tool
    global previous_tool
    global exit_ind
    global exit_state
    global tools
    global loaded
    
    animation = None
    currentTool = None
    slctd_tool = None
    previous_tool = None
    exit_ind = False
    exit_state = None 
    tools = None
    loaded = False

def layout_tools():
    global tools
    
    current_position = (_TOOL_SET_POS[0] + _HORIZONTAL_PADDING, \
                        _TOOL_SET_POS[1] + _VERTICAL_PADDING)
    for tool_index in range(len(tools)):
        tool = tools[tool_index]
        tool.set_position((current_position[0],current_position[1]))
        
        x_position = current_position[0]
        y_position = current_position[1]
        
        if tool_index % 2 == 0:
            x_position = _TOOL_SET_POS[0] + (3 * _HORIZONTAL_PADDING) + tool.width
        else:
            y_position = current_position[1] + _VERTICAL_PADDING + tool.height
            x_position = _TOOL_SET_POS[0] + _HORIZONTAL_PADDING
        
        current_position = (x_position, y_position)

def draw(surface):
    """Draws a tool set onto a surface
    
    surface: the surface to draw the tool set on"""
    for tool in tools:
        tool.draw(surface)
    
    exit_button.draw(surface)

def handle_events(surface, mousePos, mouseButtonsPressed, events):
    """handles events based on the selected tool
    
    surface: a surface to draw on
    mousePos: current position of the mouse
    mouseButtonsPressed: list of buttons pushed at last iteration of main
    loop
    events: list of events on queue"""
    global slctd_tool
    global currentTool
    global exit_ind
    global loaded
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN: 
            slctd_tool = get_slctd_tool(mousePos)
            
            if slctd_tool != None:
                slctd_tool.color = EditorTools.Tool._SlctdColor
            elif exit_button.contains(mousePos):
                exit_button.color = button.Button._SlctdColor
                exit_ind = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if slctd_tool != None:
                if slctd_tool.contains(mousePos):
                    if currentTool != None:
                        currentTool.clear_state()
                    
                    currentTool = slctd_tool
                    currentTool.init_state(animation)
                else:
                    slctd_tool.color = EditorTools.Tool._InactiveColor
                
                slctd_tool = None
                
            elif exit_ind == True:
                gamestate.mode = exit_state
                exit_ind = False
                exit_button.color = button.Button._InactiveColor
                
                if currentTool != None:
                    currentTool.clear_state()
                    currentTool = None
                
                unload()
            else:
                exit_button.color = button.Button._InactiveColor
    
    if ((slctd_tool == None) and
        (currentTool != None) and
        (exit_ind == False)):
        currentTool.handle_events(surface, \
                                  mousePos, \
                                  mouseButtonsPressed, \
                                  events)
    
    if loaded:
        draw(surface)
        animation.draw_frame(surface)
        animation.draw_frames(surface, (20, 540))
    
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