import sys
import os
import multiprocessing

# sys.stderr = open("logfile.txt","w")
# sys.stdout = open("logfile_out.txt","w")

import pygame

from pygame.locals import *

pygame.mixer.pre_init(frequency=44100, size=-16, channels=3, buffer=4096)
pygame.init()
pygame.font.init()

import wotsrendering
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
import onlineversusmovesetselectloader
import onlinemenupage
import onlinematchloader
import controlspage
import chat
import splash
import volume
import music
import versusclient
import versusserver
import stageselect
import credits
import serverselect

import gamestate
import serializability

if __name__ == "__main__":
    multiprocessing.freeze_support()
    gamestate.init_pygame_vars()
    screen = gamestate.screen
    pygame.display.set_caption("Way of the Stick")
    music.init()
    
    if len(sys.argv) >= 2 and sys.argv[1] == "dev":
        gamestate.devmode = True
    
    while 1:
        try:
            if gamestate.drawing_mode == gamestate.DrawingModes.UPDATE_ALL:
                screen.fill((0,0,0))
            
            gamestate.update_time()
            wotsuievents.get_events()
            
            events = wotsuievents.events
            event_types = wotsuievents.event_types
            mousePos = wotsuievents.mouse_pos
            mouseButtonsPressed = wotsuievents.mouse_buttons_pressed
            
            music.update()
            
            if pygame.QUIT in event_types:
                if (versusmode.local_state != None and
                versusmode.local_state.simulation_process != None):
                    
                    if versusmode.local_state.simulation_process.is_alive():
                        print("terminating!")
                        if versusmode.local_state.simulation_connection != None:
                            versusmode.local_state.simulation_connection.send('STOP')
                        else:
                            versusmode.local_state.simulation_process.terminate()
                        versusmode.local_state.simulation_process.join()
                
                sys.exit()
            elif pygame.K_ESCAPE in wotsuievents.keys_pressed:
                if (versusmode.local_state != None and
                versusmode.local_state.simulation_process != None):
                    
                    if versusmode.local_state.simulation_process.is_alive():
                        print("terminating!")
                        if versusmode.local_state.simulation_connection != None:
                            versusmode.local_state.simulation_connection.send('STOP')
                        else:
                            versusmode.local_state.simulation_process.terminate()
                        versusmode.local_state.simulation_process.join()
                
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
                if versusmode.initialized() == False:
                    versusmode.init()
                    
                versusmode.handle_events()
            elif gamestate.mode == gamestate.Modes.SETTINGSMODE:
                volume.handle_events()
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
            
            elif gamestate.mode == gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER:
                onlineversusmovesetselectloader.handle_events()
            
            elif gamestate.mode == gamestate.Modes.ONLINEMATCHLOADER:
                onlinematchloader.handle_events()
                chat.handle_events()
            
            elif gamestate.mode == gamestate.Modes.ONLINEMENUPAGE:
                onlinemenupage.handle_events()
            
            elif gamestate.mode == gamestate.Modes.SERVERSELECT:
                serverselect.handle_events()
                    
            elif gamestate.mode == gamestate.Modes.CONTROLSPAGE:
                controlspage.handle_events()
            
            elif gamestate.mode == gamestate.Modes.SPLASH:
                splash.handle_events()
            
            elif gamestate.mode == gamestate.Modes.STAGESELECT:
                stageselect.handle_events()
            
            elif gamestate.mode == gamestate.Modes.CREDITS:
                credits.handle_events()
            
            if gamestate.drawing_mode == gamestate.DrawingModes.UPDATE_ALL:
                pygame.display.flip()
            elif gamestate.drawing_mode == gamestate.DrawingModes.DIRTY_RECTS:
                wotsrendering.flush()
                gamestate.update_screen()
            
            if gamestate.hosting:
                versusserver.pump()
            
            gamestate.clock.tick(gamestate.frame_rate)
        
        except Exception as err:
            print("Unexpected error:", str(err))
            
            if (versusmode.local_state != None and
            versusmode.local_state.simulation_process != None):
                
                if versusmode.local_state.simulation_process.is_alive():
                    print("terminating!")
                    if versusmode.local_state.simulation_connection != None:
                        versusmode.local_state.simulation_connection.send('STOP')
                    else:
                        versusmode.local_state.simulation_process.terminate()
                    versusmode.local_state.simulation_process.join()
            
            elif (onlineversusmode.local_state != None and
            onlineversusmode.local_state.simulation_process != None):
                
                if onlineversusmode.local_state.simulation_process.is_alive():
                    print("terminating!")
                    onlineversusmode.local_state.simulation_process.terminate()
                    #onlineversusmode.local_state.simulation_process.join()
                    
            raise
