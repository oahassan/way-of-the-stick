import pygame

import versusclient
import versusserver
import wotsuievents
import gamestate
import player
import humanplayer
import aiplayer
import button
import stage
import stick
import mathfuncs

exit_button = button.ExitButton()
exit_indicator = False

def handle_events():
    global exit_button
    global exit_indicator
    
    exit_button.draw(gamestate.screen)
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(wotsuievents.mouse_pos):
                if versusclient.local_player_is_in_match():
                    versusclient.listener.end_match()
                else:
                    versusclient.listener.close()
                    gamestate.mode = gamestate.Modes.MAINMENU
    
    if versusclient.listener.server_mode == versusserver.ServerModes.MOVESET_SELECT:
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
    
    versusclient.listener.Pump()
    versusclient.get_network_messages()
    
    if gamestate.hosting:
        versusserver.server.Pump()
