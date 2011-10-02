import multiprocessing
import copy
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
import animation
import mathfuncs
import versusmode
from versusmode import VersusModeState
from simulation import ServerSimulation, ClientSimulation
from playerutils import Transition
from playerconstants import TRANSITION_ACCELERATION, STUN_ACCELERATION
from enumerations import InputActionTypes, MatchStates, SimulationDataKeys, \
SimulationActionTypes, PlayerStates, PlayerPositions

class NetworkPlayer(humanplayer.HumanPlayer):
    
    def __init__(self, position, player_position):
        humanplayer.HumanPlayer.__init__(self, position)
        self.player_position = player_position
    
    def sync_to_server_state(self, player_state):
        """syncs a players state to that given from the server"""
        
        self.set_health(player_state.health)
        self.direction = player_state.direction
        self.model.time_passed = player_state.animation_run_time
        self.model.velocity = player_state.velocity
        self.sync_action_state(player_state.action_data)
        self.model.move_model(player_state.reference_position)
    
    def sync_action_state(self, action_data):
        
        action_state = action_data.action_state
        
        if action_state == PlayerStates.STUNNED:
            #set data to generate knockback animation
            self.model.set_absolute_point_positions(
                action_data.first_frame_point_positions
            )
            self.interaction_vector = action_data.interaction_vector
            self.knockback_vector = action_data.knockback_vector
            self.interaction_point = self.model.points[
                action_data.interaction_point_name
            ]
            
            action = self.actions[action_state]
            
            action.set_animation(self)
            action.set_player_state(self)
        
        elif action_state == PlayerStates.TRANSITION:
            
            action = self.create_transition(action_data)
            action.set_player_state(self)
        
        elif action_state == PlayerStates.JUMPING:
            player.jump_timer = action_data.timer
            
            self.actions[action_state].set_player_state(self)
        
        elif action_state == PlayerStates.ATTACKING:
            self.actions[action_data.animation_name].set_player_state(self)
        
        elif action_state == PlayerStates.WALKING:
            if self.direction == PlayerStates.FACING_LEFT:
                self.walk_left_action.set_player_state(self)
                
            elif self.direction == PlayerStates.FACING_RIGHT:
                self.walk_right_action.set_player_state(self)
                
            else:
                raise Exception("Invalid Direction: " + str(action_data.direction))
                
        elif action_state == PlayerStates.RUNNING:
            if self.direction == PlayerStates.FACING_LEFT:
                self.run_left_action.set_player_state(self)
                
            elif self.direction == PlayerStates.FACING_RIGHT:
                self.run_right_action.set_player_state(self)
                
            else:
                raise Exception("Invalid Direction: " + str(action_data.direction))
                
        else:
            self.actions[action_state].set_player_state(self)
    
    def create_transition(self, action_data):
        action = Transition()
        action.direction = action_data.direction
        action.last_action = self.get_action(
            action_data.direction, 
            action_data.last_action_state,
            action_data.last_action_animation_name
        )
        action.next_action = self.get_action(
            action_data.direction, 
            action_data.next_action_state,
            action_data.next_action_animation_name
        )
        
        self.set_animation_from_frame_point_positions(
            action,
            action_data.first_frame_point_positions,
            animation.get_frame_point_positions(
                action.next_action.right_animation,
                action.next_action.right_animation.frames[0]
            ),
            TRANSITION_ACCELERATION
        )
        
        return action
    
    def get_action(self, direction, action_state, animation_name, new_action=None):
        action = None
        
        if action_state == PlayerStates.WALKING:
            if direction == PlayerStates.FACING_LEFT:
                action = self.walk_left_action
                
            elif direction == PlayerStates.FACING_RIGHT:
                action = self.walk_right_action
                
            else:
                raise Exception("Invalid Direction: " + str(direction))
                
        elif action_state == PlayerStates.RUNNING:
            if direction == PlayerStates.FACING_LEFT:
                action = self.run_left_action
                
            elif direction == PlayerStates.FACING_RIGHT:
                action = self.run_right_action
                
            else:
                raise Exception("Invalid Direction: " + str(direction))
        elif action_state == PlayerStates.ATTACKING:
            action = self.actions[
                animation_name
            ]
        
        else:
            action = self.actions[action_state]
        
        return action
    
    def set_animation_from_frame_point_positions(
        self,
        action,
        first_frame_point_positions,
        last_frame_point_positions,
        acceleration
    ):
        action_animation = animation.Animation()
        action_animation.frames = []
        action_animation.point_names = self.action.animation.point_names
        
        action_animation.frames.append(
            self.save_point_positions_to_frame(
                self.action.animation.frames[0],
                self.action.animation.point_names,
                first_frame_point_positions
            )
        )
        action_animation.frames.append(
            self.save_point_positions_to_frame(
                self.action.animation.frames[0],
                self.action.animation.point_names,
                last_frame_point_positions
            )
        )
        
        action_animation.set_frame_deltas()
        action_animation.set_animation_deltas()
        action_animation.set_animation_point_path_data(acceleration)
        
        action.right_animation = action_animation
        action.left_animation = action_animation
        action.animation = action_animation
    
    def save_point_positions_to_frame(self, frame, point_names, point_positions):
        """Creates a frame with ids that match the given frame with points at the given
        positions."""
        
        save_frame = copy.deepcopy(frame)
        
        for point_name, point_id in point_names.iteritems():
            position = point_positions[point_name]
            save_frame.point_dictionary[point_id].pos = (position[0], position[1])
            save_frame.point_dictionary[point_id].name = point_name
        
        return save_frame

class OnlineVersusModeState(VersusModeState):
    def __init__(self):
        VersusModeState.__init__(self)
        chatting = False
    
    def init(self):
        print("hosting: " + str(gamestate.hosting))
        self.register_network_callbacks()
        self.init_match_state_variables()
        self.init_rendering_objects()
        self.init_simulation_objects()
        self.set_GUI_module_variables()
        self.init_stage()
        self.init_screen()
        
        self.initialized = True
        self.exit_indicator = False
        self.chatting = False

    def register_network_callbacks(self):
        if gamestate.hosting:
            versusclient.listener.register_callback(
                versusserver.ClientActions.UPDATE_INPUT_STATE,
                self.sync_simulation_input_to_client
            )
        else:
            versusclient.listener.register_callback(
                versusserver.ClientActions.UPDATE_SIMULATION_STATE,
                self.sync_simulation_state_to_server
            )

    def init_simulation_objects(self):
        
        self.simulation_connection, input_connection = multiprocessing.Pipe()
        player_position = versusclient.get_local_player_position()
        
        if gamestate.hosting:
            self.match_simulation = ServerSimulation(
                input_connection,
                player_dictionary=self.player_dictionary,
                player_type_dictionary=self.player_type_dictionary,
                player_position=player_position
            )
        else:
            self.match_simulation = ClientSimulation(
                input_connection,
                player_dictionary=self.player_dictionary,
                player_type_dictionary=self.player_type_dictionary,
                player_position=player_position
            )

    def exit(self):
        print("exiting")
        self.unregister_network_callbacks()
        self.end_simulation()
        self.cleanup_rendering_objects()
        self.cleanup_match_state_variables()
        self.reset_GUI_variables()
        self.initialized = False
        self.chatting = False
        gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
    
    def end_simulation(self):
        
        self.simulation_connection.send('STOP')
        self.simulation_connection.close()
        self.simulation_process.terminate()
        self.simulation_process.join()
        self.simulation_connection = None
        gamestate.processes.remove(self.simulation_process)
        self.simulation_process = None
        self.match_simulation = None
    
    def unregister_network_callbacks(self):
        if gamestate.hosting:
            versusclient.listener.clear_callbacks(
                versusserver.ClientActions.UPDATE_INPUT_STATE
            )
        else:
            versusclient.listener.clear_callbacks(
                versusserver.ClientActions.UPDATE_SIMULATION_STATE
            )

    def handle_events(self):
        
        if self.exit_indicator == False and self.simulation_process == None:
            self.start_match_simulation()
        
        if gamestate.devmode:
            self.fps_label.set_text(str(gamestate.clock.get_fps()))
            self.fps_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.fps_label.position,
                    (self.fps_label.width, self.fps_label.height)
                )
            )
        
        if self.exit_indicator == False:
            simulation_rendering_info = None
            
            while self.simulation_connection.poll():
                data = self.simulation_connection.recv()
                action = data[SimulationDataKeys.ACTION]
                
                if action == SimulationActionTypes.STEP:
                    self.update_simulation_rendering(
                        data[SimulationDataKeys.RENDERING_INFO]
                    )
                else:
                    if versusclient.local_player_is_in_match():
                        if gamestate.hosting:
                            if action == SimulationActionTypes.GET_STATE:
                                versusclient.listener.update_simulation_state(
                                    data[SimulationDataKeys.SIMULATION_STATE]
                                )
                            
                        else:
                            if action == SimulationActionTypes.UPDATE_INPUT:
                                versusclient.listener.send_input_to_host(
                                    data
                                )
                        
                    else:
                        pass #do nothing because this is a spectator
            
            self.render_simulation()
            
            self.clean_expired_effects()
            
            self.handle_match_state()
        
        if self.simulation_connection != None:
            self.update_simulation()
        
        self.handle_network_events()
        self.handle_exit_events()

    def update_simulation(self):
        self.simulation_connection.send(
            {
                SimulationDataKeys.ACTION : SimulationActionTypes.STEP,
                SimulationDataKeys.KEYS_PRESSED : self.build_player_keys_pressed(), 
                SimulationDataKeys.TIME_PASSED : gamestate.time_passed
            }
        )
    
    def build_player_keys_pressed(self):
        keys_pressed = {
            PlayerPositions.PLAYER1 : [],
            PlayerPositions.PLAYER2 : []
        }
        
        if versusclient.local_player_is_in_match():
            player_position = versusclient.get_local_player_position()
            keys_pressed[player_position] = wotsuievents.keys_pressed
        
        return keys_pressed
    
    def sync_simulation_state_to_server(self, server_data):
        
        simulation_data = {
            SimulationDataKeys.ACTION : SimulationActionTypes.UPDATE_STATE,
            SimulationDataKeys.SIMULATION_STATE : server_data[
                versusserver.DataKeys.SIMULATION_STATE
            ]
        }
        
        self.simulation_connection.send(simulation_data)

    def sync_simulation_input_to_client(self, client_data):
        
        client_data[SimulationDataKeys.ACTION] = SimulationActionTypes.UPDATE_INPUT
        
        self.simulation_connection.send(client_data)

    def handle_network_events(self):
        if versusclient.get_connection_status() != versusclient.ConnectionStatus.DISCONNECTED:
            
            if versusclient.listener.server_mode == versusserver.ServerModes.MOVESET_SELECT:
                print("match exited")
                self.exit()
                
                #This must be called here to make sure that the player states get set to None. If
                #not a new match cannot be joined
                versusclient.clear_player_states()
                
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
            
            versusclient.get_network_messages()
            versusclient.listener.Pump()
            
        else:
            print("disconnected")
            self.exit()
            #This must be called here to make sure that the player states get set to None. If
            #not a new match cannot be joined
            versusclient.clear_player_states()
            
            gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECT
        
        if gamestate.hosting:
            versusserver.server.Pump()

    def handle_match_state(self):
        
        if self.match_state == MatchStates.READY:
            self.ready_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.ready_label.position,
                    (self.ready_label.width, self.ready_label.height)
                )
            )
            
        elif self.match_state == MatchStates.FIGHT and self.match_time < 4000:
            self.fight_start_timer += gamestate.clock.get_time()
            self.match_state = MatchStates.FIGHT
            gamestate.new_dirty_rects.append(
                pygame.Rect(
                    self.fight_label.position,
                    (self.fight_label.width, self.fight_label.height)
                )
            )
        
        elif self.match_state == MatchStates.PLAYER1_WINS:
            
            if self.fight_end_timer < 8000:
                self.fight_end_timer += gamestate.clock.get_time()
                self.player1_wins_label.draw(gamestate.screen)
                
                gamestate.new_dirty_rects.append(
                    pygame.Rect(
                        self.player1_wins_label.position, 
                        (self.player1_wins_label.width, self.player1_wins_label.height)
                    )
                )
                
            else:
                versusclient.listener.end_match()
        elif self.match_state == MatchStates.PLAYER2_WINS:
            
            if self.fight_end_timer < 8000:
                self.fight_end_timer += gamestate.clock.get_time()
                self.player2_wins_label.draw(gamestate.screen)
                gamestate.new_dirty_rects.append(
                    pygame.Rect(
                        self.player2_wins_label.position,
                        (self.player2_wins_label.width, self.player2_wins_label.height)
                    )
                )
            else:
                versusclient.listener.end_match()

    def handle_chat_events(self):
        
        if pygame.K_t in wotsuievents.keys_pressed:
            self.chatting = True
            
            if versusclient.local_player_is_in_match():
                players[versusclient.get_local_player_position()].handle_input_events = False
        
        if (pygame.K_RETURN in wotsuievents.keys_pressed or
        pygame.K_ESCAPE in wotsuievents.keys_pressed):
            self.chatting = False
            
            if versusclient.local_player_is_in_match():
                players[versusclient.get_local_player_position()].handle_input_events = True

    def handle_exit_events(self):
        
        self.exit_button.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(
            pygame.Rect(
                self.exit_button.position, 
                (self.exit_button.width, self.exit_button.height)
            )
        )
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if self.exit_button.contains(wotsuievents.mouse_pos):
                self.exit_indicator = True
                self.exit_button.color = button.Button._SlctdColor
                self.exit_button.symbol.color = button.Button._SlctdColor
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if self.exit_indicator == True:
                self.exit_indicator = False
                self.exit_button.color = button.Button._InactiveColor
                self.exit_button.symbol.color = button.Button._InactiveColor
                
                if self.exit_button.contains(wotsuievents.mouse_pos):
                    if versusclient.local_player_is_in_match():
                        versusclient.listener.end_match()
                    else:
                        #if you're a spectator go to the main menu
                        versusclient.listener.close()
                        versusclient.unload()
                        gamestate.mode = gamestate.Modes.MAINMENU
                
                self.exit()

local_state = OnlineVersusModeState()

def init():
    global local_state
    
    local_state.init()

def initialized():
    global local_state
    
    return local_state.initialized()

def handle_events():
    global local_state
    
    local_state.handle_events()

def set_player(player_position, player):
    global local_state
    
    local_state.player_dictionary[player_position] = player
