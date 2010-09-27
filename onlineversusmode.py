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
players = \
    {
        versusserver.PlayerPositions.PLAYER1 : None,
        versusserver.PlayerPositions.PLAYER2 : None
    }

class PlayerStateData:
    POINT_POSITIONS = "point positions"

class NetworkPlayer():
    
    def __init__(self, player_position):
        self.player_position = player_position
    
    def sync_to_server_data(self):
        """syncs a players state to that given from the server"""
        
        player_state_dictionary = versusclient.get_player_state(self.player_position)
        
        point_positions = player_state_dictionary[PlayerStateData.POINT_POSITIONS]
        self.model.set_absolution_point_positions(point_positions)

class RemotePlayer(player.Player, NetworkPlayer):
    
    def __init__(self, position, player_position):
        player.Player.__init__(self, position)
        NetworkPlayer.__init__(self, player_position)
    
    def handle_events(self):
        
        self.sync_to_server_data()
        player.draw_model(self)

class LocalPlayer(NetworkPlayer):
    
    def get_player_point_positions(self):
        
        return_dictionary = {}
        
        for point_name, point in self.model.points.iteritems():
            return_dictionary[point_name] = point.pos
        
        return return_dictionary

class LocalHumanPlayer(humanplayer.HumanPlayer, LocalPlayer):
    
    def __init__(self, position, player_position):
        humanplayer.HumanPlayer.__init__(self, position)
        LocalPlayer.__init__(self, player_position)

class LocalBot(aiplayer.Bot, LocalPlayer):
    
    def __init__(self, position, player_position):
        aiplayer.Bot.__init__(self, position)
        LocalPlayer.__init__(self, player_position)

gamestate.stage = stage.Stage(pygame.image.load('arenabkg.png'), 447)

initialized = False
human = None
bot = None
fight_label = None
ready_label = None
human_wins_label = None
bot_wins_label = None
fight_indicator = False
exit_button = button.ExitButton()
exit_indicator = False
versus_mode_start_time = None
fight_start_time = None
fight_end_time = None
fight_end_timer = None
versus_mode_start_timer = None
fight_start_timer = None
fps_label = None
player_type = None
bot_type = None

def init():
    global initialized
    global players
    global human
    global bot
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global fight_indicator
    global fight_end_timer
    global versus_mode_start_timer
    global fight_start_timer
    global fps_label
    global player_type
    global bot_type
    
    fps_label = button.Label((200,200), str(gamestate.clock.get_fps()),(255,255,255),50)
    fight_indicator = False
    fight_end_timer = 0
    versus_mode_start_timer = 0
    fight_start_timer = 0
    
    ready_label = button.Label((0,0),'READY...',(255,255,255),100)
    ready_label_position = ((gamestate._WIDTH / 2) - (ready_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (ready_label.height / 2))
    ready_label.set_position(ready_label_position)
    
    fight_label = button.Label((0,0),'FIGHT!',(255,255,255),100)
    fight_label_position = ((gamestate._WIDTH / 2) - (fight_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (fight_label.height / 2))
    fight_label.set_position(fight_label_position)
    
    human_wins_label = button.Label((0,0),'YOU WIN!',(255,255,255),100)
    human_wins_label_position = ((gamestate._WIDTH / 2) - (human_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (human_wins_label.height / 2))
    human_wins_label.set_position(human_wins_label_position)
    
    bot_wins_label = button.Label((0,0),'BOT WINS!',(255,255,255),100)
    bot_wins_label_position = ((gamestate._WIDTH / 2) - (bot_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (bot_wins_label.height / 2))
    bot_wins_label.set_position(bot_wins_label_position)
    
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
    initialized = True
    
    gamestate.frame_rate = 100
    gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS
    
    gamestate.stage.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect((0,0),(gamestate._WIDTH, gamestate._HEIGHT)))

def exit():
    global initialized
    global players
    global human
    global bot
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global fight_indicator
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    
    ready_label = None
    fight_label = None
    human_wins_label = None
    bot_wins_label = None
    fight_indicator = False
    versus_mode_start_timer = None
    fight_start_timer = None
    fight_end_timer = None
    human = None
    bot = None
    players = \
        {
            versusserver.PlayerPositions.PLAYER1 : None,
            versusserver.PlayerPositions.PLAYER2 : None
        }
    initialized = False
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.NONE
    gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
    gamestate.frame_rate = 20

def handle_events():
    global exit_button
    global exit_indicator
    global players
    
    for rect in gamestate.old_dirty_rects:
        rect_surface = pygame.Surface((rect.width,rect.height))
        rect_surface.blit(gamestate.stage.bkg_image,((-rect.left,-rect.top)))
        gamestate.screen.blit(rect_surface,rect.topleft)
    
    exit_button.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect(exit_button.position, (exit_button.width,exit_button.height)))
    
    for player_position, current_player in players.iteritems():
        if current_player.player_type == player.PlayerTypes.BOT:
            for other_player_position in get_other_player_positions(player_position):
                current_player.handle_events(players[other_player_position])
        
        else:
            current_player.handle_events()
    
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
                    exit()
                    gamestate.mode = gamestate.Modes.MAINMENU
    
    if versusclient.listener.server_mode == versusserver.ServerModes.MOVESET_SELECT:
        exit()
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
    
    if versusclient.listener.connection_status == versusclient.ConnectionStatus.DISCONNECTED:
        #TODO - goto mainmenu if hosting
        exit()
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
    
    versusclient.listener.Pump()
    versusclient.get_network_messages()
    
    if gamestate.hosting:
        versusserver.server.Pump()

def set_player(player_position, player):
    global players
    
    players[player_position] = player

def get_other_player_positions(player_position):
    global players
    
    return [position for position in players.keys if position != player_position]

def get_local_player_state_dictionary():
    local_player_position = versusclient.get_local_player_position()
    local_player = players[local_player_position]
    
    player_state_dictionary = \
        {PlayerStateData.POINT_POSITIONS : local_player.get_player_point_positions()}
    
    return player_state_dictionary
