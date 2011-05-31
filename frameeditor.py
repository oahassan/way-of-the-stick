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
import mathfuncs

LINE_COLORS = {
    stick.LineNames.HEAD : (0,0,0),
    stick.LineNames.LEFT_UPPER_ARM : (0,0,0),
    stick.LineNames.LEFT_FOREARM : (0,0,0),
    stick.LineNames.RIGHT_UPPER_ARM : (50,50,50),
    stick.LineNames.RIGHT_FOREARM : (50,50,50),
    stick.LineNames.TORSO : (0,0,0),
    stick.LineNames.LEFT_UPPER_LEG : (0,0,0),
    stick.LineNames.LEFT_LOWER_LEG : (0,0,0),
    stick.LineNames.RIGHT_UPPER_LEG : (50,50,50),
    stick.LineNames.RIGHT_LOWER_LEG : (50,50,50)
}

_HORIZONTAL_PADDING = 5
_VERTICAL_PADDING = 5
_ContainerLineThickness = 2
_TOOL_SET_POS = (0,0)


class FrameStats():
    def __init__(self):
        self.reference_position_label = button.Label((300, 10), "Reference Position: ", (255,255,255), 15)
        self.bottom_position_label = button.Label((300, 40), "Bottom Position: ", (255,255,255), 15)
        self.visible = True
    
    def update_frame_stats(self, frame):
        reference_position = frame.get_reference_position()
        self.reference_position_label.set_text("Reference Position: " + str(reference_position))
        self.bottom_position_label.set_text(
            "Bottom Position: " + str(reference_position[1] + frame.image_height())
        )
    
    def hide(self):
        self.visible = False
    
    def show(self):
        self.visible = True

tools = []
exit_button = button.ExitButton()
animation = None
currentTool = None
slctd_tool = None
previous_tool = None
play_tool = None
exit_state = gamestate.Modes.ANIMATIONEXPLORER
exit_ind = False
loaded = False
frame_stats = None

def load(animation_type, edit_animation, rtn_state):
    global animation
    global currentTool
    global slctd_tool
    global previous_tool
    global exit_ind
    global exit_state
    global tools
    global loaded
    global play_tool
    global frame_stats
    
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
    
    play_tool = playtool.PlayTool()
    play_tool.animation_type = animation_type
    tools.append(play_tool)
    
    save_tool = savetool.SaveTool()
    save_tool.animation_type = animation_type
    tools.append(save_tool)
    
    frame_stats = FrameStats()
    
    
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
    global play_tool
    global frame_stats
    
    play_tool = None
    animation = None
    currentTool = None
    slctd_tool = None
    previous_tool = None
    exit_ind = False
    exit_state = None 
    tools = None
    frame_stats = None
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
    
    if frame_stats.visible:
        frame_stats.reference_position_label.draw(surface)
        frame_stats.bottom_position_label.draw(surface)
    
    exit_button.draw(surface)

def draw_reference_frames(surface):
    global animation
    
    if animation.frame_index > 0:
        draw_frame(
            surface,
            animation.frames[animation.frame_index - 1],
            100
        )
    
    if animation.frame_index < len(animation.frames) - 1:
        draw_frame(
            surface,
            animation.frames[animation.frame_index + 1],
            100
        )
    
    draw_frame(surface, animation.frames[animation.frame_index])

def draw_frame(surface, frame, opacity=255):
    """draws all the points, lines and circles in a frame"""
    global LINE_COLORS
    
    frame_rect = frame.get_enclosing_rect(10, 16, 10)
    frame_surface = pygame.Surface((frame_rect.width, frame_rect.height))
    pos_delta = (-frame_rect.left, -frame_rect.top)
    
    for line in frame.lines():
        line.draw(frame_surface, (255,255,255), line_thickness = 20, pos_delta = pos_delta)
        
    for circle in frame.circles():
        outer_radius = (.5 * mathfuncs.distance(circle.endPoint1.pos, \
                                          circle.endPoint2.pos)) + 2
        circle.draw(frame_surface, (255,255,255), pos_delta = pos_delta, radius = outer_radius)
        
    for point in frame.points():
        point.draw(frame_surface, color=(255,255,255), radius=10, pos_delta = pos_delta)
    
    for line in frame.lines():
        line.draw(frame_surface, LINE_COLORS[line.name], line_thickness = 16, pos_delta = pos_delta)
    
    for circle in frame.circles():
        circle.draw(frame_surface, LINE_COLORS[circle.name], pos_delta = pos_delta)
    
    for point in frame.points():
        point.draw(frame_surface, radius=8, pos_delta = pos_delta)
    
    frame_surface.set_colorkey((0,0,0))
    frame_surface.set_alpha(opacity)
    
    surface.blit(frame_surface, (frame_rect.left, frame_rect.top))

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
    global animation
    
    mouseover_tool = get_mouseover_tool(mousePos)
    
    if mouseover_tool != None and mouseover_tool.has_help_text():
        mouseover_tool.help_text.draw(gamestate.screen)
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN: 
            slctd_tool = mouseover_tool
            
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
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            if frame_stats.visible:
                frame_stats.hide()
            else:
                frame_stats.show()
    
    if ((slctd_tool == None) and
        (currentTool != None) and
        (exit_ind == False)):
        currentTool.handle_events(surface, \
                                  mousePos, \
                                  mouseButtonsPressed, \
                                  events)
    
    if loaded:
        frame_stats.update_frame_stats(animation.frames[animation.frame_index])
        draw(surface)
        
        if currentTool != play_tool:
            #animation.draw_frame(surface)
            draw_reference_frames(surface)
            
            pygame.draw.line(
                surface,
                (200, 200, 200),
                (0, 500),
                (800, 500),
                1
            )
        
        animation.draw_frames(surface, (20, 540))
    
def get_mouseover_tool(mousePos):
    """Returns the tool that was clicked.  If no tool was clicked
    None is returned.
    
    mousePos: position of mouse"""
    slctdTool = None
    
    for tool in tools:
        if tool.contains(mousePos):
            slctdTool = tool
            break
    
    return slctdTool
