import pygame

import wotsuievents
import movesetdata
import gamestate
import versusmode

import button
import movesetselectui
import wotsuicontainers

loaded = False
exit_button = None
start_match_label = None
player_type_select = None
player_moveset_select = None
bot_type_select = None
bot_moveset_select = None

def get_playable_movesets():
    movesets = movesetdata.get_movesets()
    playable_movesets = [moveset for moveset in movesets if moveset.is_complete()]
    
    return playable_movesets

def load():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global bot_type_select
    global bot_moveset_select
    
    exit_button = button.ExitButton()
    loaded = True
    start_match_label = movesetselectui.MovesetActionLabel((10, 500), "Start Match!")
    start_match_label.inactivate()
    playable_movesets = get_playable_movesets()
    player_type_select = wotsuicontainers.ButtonContainer((50,50),
                                                          200,
                                                          300,
                                                          'Select Player Type',
                                                          button.TextButton,
                                                          [['Human',15], ['Bot',15]])
    player_moveset_select = movesetselectui.MovesetSelectContainer((50, 270), \
                                                                   200, \
                                                                   100, \
                                                                   'Select Your Moveset', \
                                                                   playable_movesets)
    bot_type_select = wotsuicontainers.ButtonContainer((400,50),
                                                       200,
                                                       300,
                                                       'Select Enemy Type',
                                                       button.TextButton,
                                                       [['Human',15], ['Bot',15]])
    bot_moveset_select = movesetselectui.MovesetSelectContainer((400, 270),
                                                                200, \
                                                                100, \
                                                                'Select Enemy Moveset', \
                                                                playable_movesets)
    
def unload():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global bot_type_select
    global bot_moveset_select
    
    exit_button = None
    loaded = False
    start_match_label = None
    player_type_select = None
    player_moveset_select = None
    bot_type_select = None
    bot_moveset_select = None

def handle_events():
    global loaded
    global exit_button
    global start_match_label
    global player_type_select
    global player_moveset_select
    global bot_type_select
    global bot_moveset_select
    
    if loaded == False:
        load()
    
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_button.handle_selected()
        
        if start_match_label.active:
            if start_match_label.contains(wotsuievents.mouse_pos):
                start_match_label.handle_selected()
        
        for button in player_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((player_type_select.selected_button != None)
                and (player_type_select.selected_button != button)):
                    player_type_select.selected_button.handle_deselected()
                
                player_type_select.selected_button = button
                break
        
        for button in bot_type_select.buttons:
            if button.contains(wotsuievents.mouse_pos):
                button.handle_selected()
                
                if ((bot_type_select.selected_button != None)
                and (bot_type_select.selected_button != button)):
                    bot_type_select.selected_button.handle_deselected()
                
                bot_type_select.selected_button = button
                break
        
    if pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_button.selected:
            exit_button.handle_deselected()
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.MAINMENU
                unload()
        
        elif start_match_label.selected:
            if start_match_label.contains(wotsuievents.mouse_pos):
                if player_type_select.selected_button != None:
                    if player_type_select.selected_button.text.text == 'Human':
                        versusmode.player_type = versusmode.PlayerTypes.HUMAN
                    elif player_type_select.selected_button.text.text == 'Bot':
                        versusmode.player_type = versusmode.PlayerTypes.BOT
                
                if bot_type_select.selected_button != None:
                    if bot_type_select.selected_button.text.text == 'Human':
                        versusmode.bot_type = versusmode.PlayerTypes.HUMAN
                    elif bot_type_select.selected_button.text.text == 'Bot':
                        versusmode.bot_type = versusmode.PlayerTypes.BOT
                
                versusmode.init()
                versusmode.human.load_moveset(player_moveset_select.selected_moveset)
                versusmode.bot.load_moveset(bot_moveset_select.selected_moveset)
                unload()
                gamestate.mode = gamestate.Modes.VERSUSMODE
    if loaded:
        player_moveset_select.handle_events()
        bot_moveset_select.handle_events()
        
        if ((player_moveset_select.selected_moveset != None) and
            (bot_moveset_select.selected_moveset != None)):
            if start_match_label.active == False:
                start_match_label.activate()
        else:
            if start_match_label.active:
                start_match_label.inactivate()
        
        exit_button.draw(gamestate.screen)
        start_match_label.draw(gamestate.screen)
        player_type_select.draw(gamestate.screen)
        player_moveset_select.draw(gamestate.screen)
        bot_type_select.draw(gamestate.screen)
        bot_moveset_select.draw(gamestate.screen)
