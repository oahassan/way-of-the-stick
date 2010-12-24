import sys

# sys.stderr = open("logfile.txt","w")
sys.stdout = open("logfile_out.txt","w")

import pygame

from pygame.locals import *

pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=4096)
pygame.init()
pygame.font.init()

import wotsuievents
import animationexplorer
import actionwizard
import movebuilder
import frameeditor
import menupage
import versusmode
import keybinding
import movesetbuilder
import movesetselect
import versusmovesetselect
import onlineversusmode
import onlineversusmovesetselect
import onlinemenupage
import onlinematchloader
import controlspage
import chat
import splash

import gamestate

screen = gamestate.screen
pygame.display.set_caption("Way of the Stick")
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
    elif gamestate.mode == gamestate.Modes.FRAMEEDITOR:
        frameeditor.handle_events(screen, \
                                  mousePos, \
                                  mouseButtonsPressed, \
                                  events)
        
    elif gamestate.mode == gamestate.Modes.ANIMATIONEXPLORER:
        animationexplorer.handle_events(screen, \
                                        mousePos, \
                                        mouseButtonsPressed, \
                                        events)
    elif gamestate.mode == gamestate.Modes.MAINMENU:
        menupage.handle_events()
    elif gamestate.mode == gamestate.Modes.VERSUSMODE:
        if versusmode.initialized == False:
            versusmode.init()
            
        versusmode.handle_events()
    elif gamestate.mode == gamestate.Modes.SETTINGSMODE:
        actionwizard.handle_events()
    elif gamestate.mode == gamestate.Modes.MOVEBUILDER:
        movebuilder.handle_events()
    elif gamestate.mode == gamestate.Modes.MOVESETBUILDER:
        movesetbuilder.handle_events()
    elif gamestate.mode == gamestate.Modes.KEYBINDING:
        keybinding.handle_events()
    elif gamestate.mode == gamestate.Modes.MOVESETSELECT:
        movesetselect.handle_events()
    elif gamestate.mode == gamestate.Modes.VERSUSMOVESETSELECT:
        versusmovesetselect.handle_events()
    elif gamestate.mode == gamestate.Modes.ONLINEVERSUSMODE:
        onlineversusmode.handle_events()
        chat.handle_events()
        
    elif gamestate.mode == gamestate.Modes.ONLINEVERSUSMOVESETSELECT:
        onlineversusmovesetselect.handle_events()
        chat.handle_events()
        
    elif gamestate.mode == gamestate.Modes.ONLINEMENUPAGE:
        onlinemenupage.handle_events()
        
    elif gamestate.mode == gamestate.Modes.ONLINEMATCHLOADER:
        onlinematchloader.handle_events()
        chat.handle_events()
        
    elif gamestate.mode == gamestate.Modes.CONTROLSPAGE:
        controlspage.handle_events()
    
    elif gamestate.mode == gamestate.Modes.SPLASH:
        splash.handle_events()
        
    if gamestate.drawing_mode == gamestate.DrawingModes.UPDATE_ALL:
        pygame.display.flip()
    elif gamestate.drawing_mode == gamestate.DrawingModes.DIRTY_RECTS:
        gamestate.update_screen()
    
    gamestate.clock.tick(gamestate.frame_rate)
