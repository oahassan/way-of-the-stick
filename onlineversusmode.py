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
import versusmode
from controlsdata import InputActionTypes

exit_button = button.ExitButton()
exit_indicator = False
players = \
    {
        versusserver.PlayerPositions.PLAYER1 : None,
        versusserver.PlayerPositions.PLAYER2 : None
    }

class PlayerStateData:
    POINT_POSITIONS = "point positions"
    POINT_DAMAGES = "point damages"
    PLAYER_STATE = "player state"
    HEALTH = "health"
    ATTACK_SEQUENCE = "attack sequence"
    ATTACK_LINE_NAMES = "attack line names"
    ATTACK_TYPE = "attack type"
    STUN_TIMER = "stun timer"
    PLAY_SOUND = "play sound"

class NetworkPlayer():
    
    def __init__(self, player_position):
        self.player_position = player_position
        self.attack_sequence = 0
    
    def sync_to_server_data(self):
        """syncs a players state to that given from the server"""
        
        player_state_dictionary = versusclient.get_player_state(self.player_position)
        
        for data_key, data_value in player_state_dictionary.iteritems():
            if data_key == PlayerStateData.POINT_POSITIONS:
                point_positions = player_state_dictionary[PlayerStateData.POINT_POSITIONS]
                self.model.set_absolute_point_positions(point_positions)
            
            elif data_key == PlayerStateData.POINT_DAMAGES:
                #set point damage
                point_damage_dictionary = player_state_dictionary[PlayerStateData.POINT_DAMAGES]
                
                self.update_point_damage(point_damage_dictionary)
            
            elif data_key == PlayerStateData.PLAYER_STATE:
                #set player state
                self.set_player_state(player_state_dictionary)
                
            elif data_key == PlayerStateData.HEALTH:
                #set player health
                health_value = player_state_dictionary[PlayerStateData.HEALTH]
                
                self.set_health(health_value)

class RemotePlayer(player.Player, NetworkPlayer):
    
    def __init__(self, position, player_position):
        player.Player.__init__(self, position)
        NetworkPlayer.__init__(self, player_position)
        
        self.player_state = player.PlayerStates.STANDING
        self.attack_line_names = []
        self.attack_type = None
    
    def sync_to_server_data(self):
        """syncs a players state to that given from the server"""
        
        player_state_dictionary = versusclient.get_player_state(self.player_position)
        
        for data_key, data_value in player_state_dictionary.iteritems():
            if data_key == PlayerStateData.POINT_POSITIONS:
                point_positions = player_state_dictionary[PlayerStateData.POINT_POSITIONS]
                self.model.set_absolute_point_positions(point_positions)
            
            elif data_key == PlayerStateData.POINT_DAMAGES:
                #set point damage
                point_damage_dictionary = player_state_dictionary[PlayerStateData.POINT_DAMAGES]
                
                self.update_point_damage(point_damage_dictionary)
            
            elif data_key == PlayerStateData.PLAYER_STATE:
                #set player state
                self.sync_player_state_to_server(player_state_dictionary)
                
            elif data_key == PlayerStateData.HEALTH:
                #set player health
                health_value = player_state_dictionary[PlayerStateData.HEALTH]
                
                self.set_health(health_value)
            
            elif data_key == PlayerStateData.ATTACK_LINE_NAMES:
                
                attack_line_names = player_state_dictionary[PlayerStateData.ATTACK_LINE_NAMES]
                
                self.attack_line_names = attack_line_names
            
            elif data_key == PlayerStateData.ATTACK_TYPE:
                #set player attack type
                self.attack_type = player_state_dictionary[PlayerStateData.ATTACK_TYPE]
            
            elif data_key == PlayerStateData.STUN_TIMER:
                self.stun_timer = player_state_dictionary[PlayerStateData.STUN_TIMER]
            
            elif data_key == PlayerStateData.PLAY_SOUND:
                self.play_sound_indicator = player_state_dictionary[PlayerStateData.PLAY_SOUND]
    
    def sync_player_state_to_server(self, player_state_dictionary):
        """sets the current state of the player and any state changes associated with a
        change in player state"""
        
        player_state = player_state_dictionary[PlayerStateData.PLAYER_STATE]
        
        if player_state == player.PlayerStates.ATTACKING:
            attack_sequence = player_state_dictionary[PlayerStateData.ATTACK_SEQUENCE]
            
            if attack_sequence != self.attack_sequence:
                self.reset_point_damage()
                self.attack_sequence = attack_sequence
        
        self.player_state = player_state
    
    def set_player_state(self, player_state):
        self.player_state = player_state
    
    def get_player_state(self):
        return self.player_state
    
    def get_attack_type(self):
        return self.attack_type
    
    def get_attack_lines(self):
        return \
            dict([(line_name, self.model.lines[line_name]) for line_name in self.attack_line_names])
    
    def set_neutral_state(self):
        pass
    
    def update_point_damage(self, point_damage_dictionary):
        
        self.point_name_to_point_damage = point_damage_dictionary
    
    def handle_events(self):
        
        self.set_previous_point_positions()
        
        self.sync_to_server_data()
        
        self.set_outline_color()
        #player.draw_model(self)
        
        if self.play_sound_indicator:
            self.play_sound()
            
            self.play_sound_indicator = False

class LocalPlayer(NetworkPlayer):
    
    def __init__(self, player_position):
        
        NetworkPlayer.__init__(self, player_position)
        
        self.update_timer = 0
    
    def build_player_state_dictionary(self):
        
        player_state = self.get_player_state()
        
        player_state_dictionary = \
            {
                PlayerStateData.POINT_POSITIONS : self.get_player_point_positions(),
                PlayerStateData.POINT_DAMAGES : self.point_name_to_point_damage,
                PlayerStateData.PLAYER_STATE : player_state,
                PlayerStateData.HEALTH : self.health_meter,
                PlayerStateData.STUN_TIMER : self.stun_timer,
                PlayerStateData.PLAY_SOUND : self.play_sound_indicator
            }
        
        if player_state == player.PlayerStates.ATTACKING:
            player_state_dictionary[PlayerStateData.ATTACK_SEQUENCE] = self.attack_sequence
            player_state_dictionary[PlayerStateData.ATTACK_LINE_NAMES] = self.get_attack_line_names()
            player_state_dictionary[PlayerStateData.ATTACK_TYPE] = self.get_attack_type()
        
        return player_state_dictionary
    
    def get_attack_line_names(self):
        
        return [line_name for line_name in self.get_attack_lines().keys()]
    
    def set_player_state(self, player_state):
        """sets the current state of the player"""
        
        if self.actions[player_state].test_state_change(self):
            self.actions[player_state].set_player_state(self)
            
            if self.get_player_state() == player.PlayerStates.ATTACKING:
                self.attack_sequence += 1

class LocalHumanPlayer(humanplayer.HumanPlayer, LocalPlayer):
    
    def __init__(self, position, player_position):
        humanplayer.HumanPlayer.__init__(self, position)
        LocalPlayer.__init__(self, player_position)
    
    def handle_events(self):
        humanplayer.HumanPlayer.handle_events(self)
        self.update_timer += gamestate.time_passed
        
        if self.update_timer > 30:
            self.update_timer = 0
            player_state_dictionary = self.build_player_state_dictionary()
            
            versusclient.update_player_state(player_state_dictionary, self.player_position)

class LocalBot(aiplayer.Bot, LocalPlayer):
    
    def __init__(self, position, player_position):
        aiplayer.Bot.__init__(self, position)
        LocalPlayer.__init__(self, player_position)
    
    def handle_events(self, opponent):
        aiplayer.Bot.handle_events(self, opponent)
        self.update_timer += gamestate.time_passed
        
        if self.update_timer > 30:
            self.update_timer = 0
            player_state_dictionary = self.build_player_state_dictionary()
            
            versusclient.update_player_state(player_state_dictionary, self.player_position)

gamestate.stage = stage.ScrollableStage(447, 0, gamestate._WIDTH)

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
chatting = False

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
    global chatting
    
    chatting = False
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
    
    gamestate.screen.blit(gamestate.stage.background_image, (0,0))
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
    global chatting
    
    chatting = False
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
    global chatting
    
    exit_button.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect(exit_button.position, (exit_button.width,exit_button.height)))
    
    for player_position, current_player in players.iteritems():
        if current_player.player_type == player.PlayerTypes.BOT:
            for other_player_position in get_other_player_positions(player_position):
                current_player.handle_events(players[other_player_position])
        
        else:
            current_player.handle_events()
    
    if pygame.K_t in wotsuievents.keys_pressed:
        chatting = True
        
        if versusclient.local_player_is_in_match():
            players[versusclient.get_local_player_position()].handle_input_events = False
    
    if (pygame.K_RETURN in wotsuievents.keys_pressed or
    pygame.K_ESCAPE in wotsuievents.keys_pressed):
        chatting = False
        
        if versusclient.local_player_is_in_match():
            players[versusclient.get_local_player_position()].handle_input_events = True    
    
    handle_interactions()
    
    gamestate.stage.scroll_background(
        [current_player.model for current_player in players.values()]
    )
    gamestate.stage.draw(gamestate.screen)
    
    for current_player in players.values():
        player.draw_model(current_player, gamestate.screen)
        player.draw_reflection(current_player, gamestate.screen)
    
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
                    #if you're a spectator go to the main menu
                    versusclient.listener.close()
                    versusclient.unload()
                    exit()
                    gamestate.mode = gamestate.Modes.MAINMENU
    
    if versusclient.get_connection_status() != versusclient.ConnectionStatus.DISCONNECTED:
        if versusclient.listener.server_mode == versusserver.ServerModes.MOVESET_SELECT:
            exit()
            
            #This must be called here to make sure that the player states get set to None. If
            #not a new match cannot be joined
            versusclient.clear_player_states()
            
            gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
        
        if versusclient.get_connection_status() == versusclient.ConnectionStatus.DISCONNECTED:
            #TODO - goto mainmenu if hosting
            exit()
            
            #This must be called here to make sure that the player states get set to None. If
            #not a new match cannot be joined
            versusclient.clear_player_states()
            
            gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
        
        versusclient.get_network_messages()
        versusclient.listener.Pump()
    
    if gamestate.hosting:
        versusserver.server.Pump()

def handle_interactions():
    """changes the state of each player according to their interactions.  The state of
    the remote player isn't actually affected by this function.  So, differences in the
    state of the two clients will be synced after each request from the server"""
    
    global players
    
    #a dictionary of player positions that have already interacted.  This dictinoary is
    #used to ensure that interactions between players are only done once.
    handled_player_interactions = {}
    
    for player_position, current_player in players.iteritems():
        
        if player_position not in handled_player_interactions.keys():
            handled_player_interactions[player_position] = []
        
        for other_player_position in get_other_player_positions(player_position):
            
            if other_player_position not in handled_player_interactions.keys():
                handled_player_interactions[other_player_position] = []
            
            if (not player_position in handled_player_interactions[other_player_position] and
            not other_player_position in handled_player_interactions[player_position]):
                
                if current_player.get_player_state() == player.PlayerStates.ATTACKING:
                    
                    other_player = players[other_player_position]
                    
                    versusmode.handle_attacks(current_player, other_player)
                    
                    handled_player_interactions[player_position].append(other_player_position)
                    handled_player_interactions[other_player_position].append(player_position)

def set_player(player_position, player):
    global players
    
    players[player_position] = player

def get_other_player_positions(player_position):
    global players
    
    return [position for position in players.keys() if position != player_position]

def get_local_player_state_dictionary():
    global players
    
    local_player_position = versusclient.get_local_player_position()
    local_player = players[local_player_position]
    
    player_state_dictionary = \
        {
            PlayerStateData.POINT_POSITIONS : local_player.get_player_point_positions(),
            PlayerStateData.POINT_DAMAGES : local_player.point_name_to_point_damage,
            PlayerStateData.PLAYER_STATE : local_player.get_player_state(),
            PlayerStateData.HEALTH : local_player.health_meter,
            PlayerStateData.ATTACK_SEQUENCE : local_player.attack_sequence
        }
    
    return player_state_dictionary
