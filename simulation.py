import os
import time
import math
from functools import reduce
from collections import deque
import pygame
import mathfuncs
import animation
import playerconstants
from wotsprot.rencode import serializable
from enumerations import MatchStates, PlayerTypes, ClashResults, \
PlayerPositions, PlayerStates, LineNames, PointNames, SimulationDataKeys, \
SimulationActionTypes, InputActionTypes, EventTypes, EventStates

class SimulationClock():
    """A pickleable clock"""
    def __init__(self, frame_rate):
        #the target time between each tick in seconds
        tick_time = max(1 / float(frame_rate), 0)
        
        #execution should stop until the next tick time if tick is called.
        self.next_tick_time = time.clock() + tick_time
    
    def tick(self, frame_rate):
        """pause execution until the next tick time.  If the current time has
        passed the next tick time, update the next tick time to match the 
        frame rate starting from the current time and continue execution."""
        
        current_time = time.clock()
        tick_time = max(1 / float(frame_rate), 0)
        
        if current_time > self.next_tick_time:
            self.next_tick_time = current_time + tick_time
            
        else:
            time.sleep(
                min(
                    tick_time,
                    self.next_tick_time - current_time
                )
            )
             
            self.next_tick_time += tick_time

class SimulationRenderingInfo():
    def __init__(
        self,
        match_state,
        match_time,
        player_rendering_info_dictionary,
        attack_result_rendering_info
    ):
        self.match_state = match_state
        self.match_time = match_time
        self.player_rendering_info_dictionary = player_rendering_info_dictionary
        self.attack_result_rendering_info = attack_result_rendering_info
    
    def _pack(self):
        return (self.match_state, self.match_time,
        self.player_rendering_info_dictionary, self.attack_result_rendering_info)

class AttackResultRenderingInfo():
    def __init__(
        self,
        attack_point,
        knockback_vector,
        attack_damage,
        attack_type,
        clash_indicator,
        clash_position
    ):
        self.attack_point = attack_point
        self.knockback_vector = knockback_vector
        self.attack_damage = attack_damage
        self.attack_type = attack_type
        self.clash_indicator = clash_indicator
        self.clash_position = clash_position
    
    def _pack(self):
        return (self.attack_point, self.knockback_vector, self.attack_damage, 
        self.attack_type, self.clash_indicator, self.clash_position)

class PlayerRenderingInfo():
    def __init__(
        self,
        player_model,
        player_state,
        player_outline_color,
        player_health_color,
        health_percentage,
        animation_name,
        frame_index,
        attack_type,
        player_events
    ):
        self.player_model = player_model
        self.player_state = player_state
        self.player_outline_color = player_outline_color
        self.player_health_color = player_health_color
        self.health_percentage = health_percentage
        self.animation_name = animation_name
        self.frame_index = frame_index
        self.attack_type = attack_type
        self.events = player_events
    
    def _pack(self):
        return (self.player_model, self.player_state,
        self.player_outline_color, self.player_health_color, 
        self.health_percentage, self.animation_name, self.frame_index,
        self.attack_type, self.events)

class MatchSimulation():
    def __init__(
        self,
        pipe_connection,
        timestep=20, 
        player_type_dictionary=None, 
        player_dictionary=None
    ):
        self.pipe_connection = pipe_connection
        self.timestep = timestep
        self.accumulator = 0
        self.player_type_dictionary = player_type_dictionary
        self.player_dictionary = player_dictionary
        self.clock = SimulationClock(100)
        self.attack_resolver = AttackResolver()
        self.current_attack_result = None
        self.collision_handler = CollisionHandler()
        self.match_time = 0
        self.match_state = MatchStates.READY
        self.pause = False
    
    def run(self):
        while 1:
            while self.pipe_connection.poll():
                message = self.pipe_connection.recv()
                
                if message == 'STOP':
                    return
                
                elif message == 'PAUSE':
                    self.pause = not self.pause
                else:
                    if not self.pause:
                        player_keys_pressed, time_passed = message
                        self.step(player_keys_pressed, time_passed)
                    
                    self.pipe_connection.send(self.get_rendering_info())
                    
                    for player in self.player_dictionary.values():
                        player.clear_events() 
            
            self.clock.tick(100)
    
    def step(self, player_keys_pressed, time_passed):
        """update the state of the players in the simulation"""
        
        self.accumulator += time_passed
        
        while self.accumulator > self.timestep:
            self.update_simulation_state(player_keys_pressed)
            self.accumulator -= self.timestep
    
    def update_simulation_state(self, player_keys_pressed):
        self.update_match_state()
        self.update_player_states(player_keys_pressed)
        self.match_time += self.timestep
    
    def update_match_state(self):
        
        match_state = self.get_match_state()
        self.match_state = match_state
        self.handle_match_state(match_state)
    
    def update_player_states(self, player_keys_pressed):
        self.handle_interactions()
        self.handle_player_events(player_keys_pressed, self.timestep)
    
    def handle_match_state(self, match_state):
        
        if (match_state == MatchStates.READY or 
        match_state == MatchStates.NO_CONTEST):
            for player in self.player_dictionary.values():
                player.handle_input_events = False
            
        elif match_state == MatchStates.FIGHT:
            for player in self.player_dictionary.values():
                player.handle_input_events = True
            
        elif match_state == MatchStates.PLAYER1_WINS:
            player2 = self.player_dictionary[PlayerPositions.PLAYER2]
            player2.handle_input_events == False
            player2.set_stun_timeout(10000)
            player2.is_invincible = False
            
        elif match_state == MatchStates.PLAYER2_WINS:
            player1 = self.player_dictionary[PlayerPositions.PLAYER1]
            player1.handle_input_events == False
            player1.set_stun_timeout(10000)
            player1.is_invincible = False
            
    def get_rendering_info(self):
        return SimulationRenderingInfo(
            self.match_state,
            self.match_time,
            self.get_player_rendering_info_dictionary(),
            self.get_attack_result_rendering_info()
        )
    
    def get_match_state(self):
        match_state = MatchStates.FIGHT
        
        if self.match_time < 3000:
            return MatchStates.READY
        else:
            #just check if the game is over
            if (self.player_dictionary[PlayerPositions.PLAYER1].health_meter <= 0 and
            self.player_dictionary[PlayerPositions.PLAYER2].health_meter <= 0):
                match_state = MatchStates.NO_CONTEST
                    
            elif self.player_dictionary[PlayerPositions.PLAYER1].health_meter <= 0:
                match_state = MatchStates.PLAYER2_WINS
                
            elif self.player_dictionary[PlayerPositions.PLAYER2].health_meter <= 0:
                match_state = MatchStates.PLAYER1_WINS
            else:
                match_state = MatchStates.FIGHT
        
        return match_state
    
    def get_player_rendering_info_dictionary(self):
        return_rendering_dictionary = {}
        
        for player_position, player in self.player_dictionary.iteritems():
            attack_type = None
            
            if player.action.action_state == PlayerStates.ATTACKING:
                attack_type = player.action.attack_type
            
            return_rendering_dictionary[player_position] = PlayerRenderingInfo(
                player.model,
                player.get_player_state(),
                player.outline_color,
                player.health_color,
                player.health_meter / player.health_max,
                player.action.animation.name,
                player.action.last_frame_index,
                attack_type,
                player.events
            )
        
        return return_rendering_dictionary
    
    def get_attack_result_rendering_info(self):
        if self.current_attack_result != None:
            attack_point = self.current_attack_result.attack_point
            
            if self.current_attack_result.clash_indicator:
                #There isn't an attack type after a clash
                return AttackResultRenderingInfo(
                    attack_point,
                    self.current_attack_result.knockback_vector,
                    self.current_attack_result.attacker.get_point_damage(attack_point.name),
                    None,
                    self.current_attack_result.clash_indicator,
                    self.current_attack_result.clash_position
                )
            else:
                attack_type = None
                attacker_action = self.current_attack_result.attacker.action
                
                if attacker_action.action_state == PlayerStates.ATTACKING:
                    attack_type = attacker_action.attack_type
                    
                elif attacker_action.action_state == PlayerStates.TRANSITION:
                    attack_type = attacker_action.last_action.attack_type
                else:
                    attack_type = None
                
                return AttackResultRenderingInfo(
                    attack_point,
                    self.current_attack_result.knockback_vector,
                    self.current_attack_result.attacker.get_point_damage(
                        attack_point.name
                    ),
                    attack_type,
                    self.current_attack_result.clash_indicator,
                    self.current_attack_result.clash_position
                )
        else:
            return None
      
    def handle_player_events(self, player_keys_pressed, timestep):
        """Advance player animations according to the current pygame events"""
        
        for player_position, active_player in self.player_dictionary.iteritems():
            player_type = self.player_type_dictionary[player_position]
            
            if player_type == PlayerTypes.HUMAN:
                active_player.handle_events(
                    player_keys_pressed[player_position],
                    timestep
                )
            elif player_type == PlayerTypes.BOT:
                [active_player.handle_events(other_player, timestep) 
                for other_player_position, other_player 
                in self.player_dictionary.iteritems()
                if not other_player_position == player_position]
            else:
                raise Exception(
                    "Invalid Player Type: " + player_type
                )
    
    def handle_interactions(self):
        """determine the effects of attacks on each player"""
    
        attack_result = self.get_attack_result()
        self.current_attack_result = attack_result
        
        if attack_result != None:
            if attack_result.clash_indicator:
                self.collision_handler.handle_blocked_attack_collision(
                    attack_result.attacker,
                    attack_result.receiver
                )
            else:
                self.collision_handler.handle_unblocked_attack_collision(
                    attack_result
                )
    
    def get_attack_result(self):
        attack_result = None
        
        player1 = self.player_dictionary[PlayerPositions.PLAYER1]
        player2 = self.player_dictionary[PlayerPositions.PLAYER2]
        
        if self.test_overlap(
            player1.get_enclosing_rect(), 
            player2.get_enclosing_rect()
        ):
            if (player1.get_player_state() == PlayerStates.ATTACKING and
            (not player2.is_invincible or (player2.is_invincible and player2.get_player_state() == PlayerStates.STUNNED))):
                attack_result = self.attack_resolver.get_attack_result(
                    player1, 
                    player2
                )
                
            elif (player2.get_player_state() == PlayerStates.ATTACKING and
            (not player1.is_invincible or (player1.is_invincible and player1.get_player_state() == PlayerStates.STUNNED))):
                attack_result = self.attack_resolver.get_attack_result(
                    player2, 
                    player1
                )
                
            else:
                pass #no attack result
        
        return attack_result
    
    def test_overlap(self, rect1, rect2):
        """a fast test if two players could possibly be attacking each other"""
        
        overlap = True
        rect1_pos = (rect1.left, rect1.top)
        rect2_pos = (rect2.left, rect2.top)
        
        if ((rect1_pos[0] > (rect2_pos[0] + rect2.width)) or
            ((rect1_pos[0] + rect1.width) < rect2_pos[0]) or
            (rect1_pos[1] > (rect2_pos[1] + rect2.height)) or
            ((rect1_pos[1] + rect1.height) < rect2_pos[1])):
            overlap = False
        
        return overlap

class CollisionHandler():
    """updates players that are in an attack collision"""
    
    def handle_unblocked_attack_collision(
        self,
        attack_result
    ):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        #A poor attempt at balancing movesets
        #if attacker.action.attack_type in InputActionTypes.STRONG_ATTACKS:
        #    receiver.set_invincibility()
        
        attack_knockback_vector = attack_result.knockback_vector
        
        if receiver.get_player_state() == PlayerStates.STUNNED:
            
            if receiver.action.grounded:
                receiver.events.append((EventTypes.START, EventStates.STUN_GROUND))
            
            stun_knockback_vector = receiver.knockback_vector
            
            #if self.attacker_is_recoiling(
            #    attack_knockback_vector, 
            #    stun_knockback_vector
            #):
            #    pass
            #else:
            self.apply_collision_physics(attack_result)
            self.apply_attack_damage(attack_result)
            attacker.update_attack_data()
                
        else:
            self.apply_collision_physics(attack_result)
            
            if receiver.get_player_state() in PlayerStates.ATTACKING:
                receiver.handle_attack_end()
            
            receiver.set_player_state(PlayerStates.STUNNED)
            self.apply_attack_damage(attack_result)
            attacker.update_attack_data()

    def apply_attack_damage(self, attack_result):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        damage = attacker.get_point_damage(
            attack_result.attack_point.name
        )
        
        if receiver.health_meter > 0:
            if attacker.attack_landed == False:
                receiver.health_meter = max(0, receiver.health_meter - damage)
            
            receiver.set_stun_timeout(
                min(
                    receiver.stun_timeout + attacker.get_stun_timeout(),
                    playerconstants.STRONG_STUN_TIMEOUT
                )
            )

    def attacker_is_recoiling(
        self,
        attack_knockback_vector, 
        stun_knockback_vector
    ):
        attack_x_sign = mathfuncs.sign(attack_knockback_vector[0])
        attack_y_sign = mathfuncs.sign(attack_knockback_vector[1])
        stun_x_sign = mathfuncs.sign(stun_knockback_vector[0])
        stun_y_sign = mathfuncs.sign(stun_knockback_vector[1])
        
        if (attack_x_sign != stun_x_sign) or (attack_y_sign != stun_y_sign):
            return True
        else:
            return False
    
    def handle_blocked_attack_collision(
        self,
        attacker, 
        receiver
    ):
        
        attacker.handle_attack_end()
        attacker.handle_attack_end()
        attacker.set_neutral_state()
        receiver.set_neutral_state()
        
        separation_vector = self.get_separation_vector(attacker,receiver)
        receiver.model.shift((.5 * separation_vector[0], .5 * separation_vector[1]))
        attacker.model.shift((-.5 * separation_vector[0], -.5 * separation_vector[1]))
        receiver.model.velocity = (0,0)
        receiver.model.accelerate(5 * receiver.knockback_vector[0], \
                                  receiver.knockback_vector[1])
        attacker.model.velocity = (0,0)
        attacker.model.accelerate(-5 * receiver.knockback_vector[0], \
                                  receiver.knockback_vector[1])

    def apply_collision_physics(
        self,
        attack_result
    ):
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        attack_type = attacker.action.attack_type
        
        #if attack_type in InputActionTypes.STRONG_ATTACKS or attack_type in InputActionTypes.QUICK_ATTACKS:
        separation_vector = self.get_separation_vector(attacker,receiver)
        receiver.model.shift((.5 * separation_vector[0], .5 * separation_vector[1]))
        #else:
        #    separation_vector = self.get_separation_vector(attacker,receiver)
        #    receiver.model.shift((0, -1 * abs(.5 * separation_vector[0]) + .5 * separation_vector[1]))
        
        receiver.knockback_vector = list(attack_result.knockback_vector)
        receiver.interaction_point = attack_result.receive_point
        receiver.interaction_vector = self.get_pull_point_deltas(attack_result)
        receiver.pull_point(receiver.interaction_vector)
        receiver.model.velocity = [0,0]
        
        if attack_type in InputActionTypes.STRONG_ATTACKS:
            if (
                (attacker.model.velocity > 0 and 
                attacker.model.velocity[0] > receiver.knockback_vector[0])
            or (attacker.model.velocity < 0 and 
                attacker.model.velocity[0] < receiver.knockback_vector[0])
            ):
                receiver.knockback_vector[0] = attacker.model.velocity[0]
            
            receiver.model.accelerate(
                receiver.knockback_vector[0],
                receiver.knockback_vector[1]
            )
        elif attack_type in InputActionTypes.TRICKY_ATTACKS:
            receiver.model.accelerate(
                0,
                -1 * abs(receiver.knockback_vector[0]) + receiver.knockback_vector[1]
            )
        else:
            receiver.model.accelerate(
                .25 * receiver.knockback_vector[0],
                .25 * receiver.knockback_vector[1]
            )
    
    def get_separation_vector(
        self,
        attacker, 
        receiver
    ):
        """Get the relative position between the attack and receiver.  The y 
        delta is always to negative to make sure the receiver moves up"""
        y_delta = receiver.model.center()[1] - attacker.model.center()[1]
        x_delta = receiver.model.center()[0] - attacker.model.center()[0]
        
        if y_delta > 0:
            y_delta = -1 * y_delta
        
        return (x_delta, y_delta)
    
    def get_pull_point_deltas(
        self,
        attack_result
    ):
        """gets the knockback applied to the interaction point to move the lines in the
        model"""
        
        knockback_vector = attack_result.knockback_vector
        
        x = knockback_vector[0]
        y = knockback_vector[1]
        hypotenuse = math.hypot(x,y)
        
        knockback = 3
        
        if hypotenuse == 0:
            return 0, 0
        else:
            return knockback * x / hypotenuse, knockback * y / hypotenuse

class AttackResult():
    
    def __init__(
        self,
        attacker,
        receiver,
        attack_point,
        receive_point,
        knockback_vector,
        clash_indicator,
        clash_position
    ):
        self.attacker = attacker
        self.receiver = receiver
        self.attack_point = attack_point
        self.receive_point = receive_point
        self.knockback_vector = knockback_vector
        self.clash_indicator = clash_indicator
        self.clash_position = clash_position

class AttackResolver():
    def __init__(self):
        self.hitbox_builder = HitboxBuilder()
    
    def get_attack_result(self, attacker, receiver):
        attack_result = None
        clash_indicator = False
        
        attacker_attack_hitboxes = self.hitbox_builder.get_hitbox_dictionary(attacker.get_attack_lines())
        
        if receiver.get_player_state() == PlayerStates.ATTACKING:
            receiver_attack_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                receiver.get_attack_lines()
            )
            colliding_line_names = self.test_attack_collision(
                attacker_attack_hitboxes,
                receiver_attack_hitboxes
            )
            
            if colliding_line_names:
                
                clash_result = self.get_clash_result(
                    attacker,
                    receiver,
                    colliding_line_names
                )
                
                if receiver.is_invincible:
                    #swap attacker and receiver
                    temp = attacker
                    attacker = receiver
                    receiver = temp
                    
                    #reverse the order of the colliding line names to math
                    #that player 2 is now the attacker.
                    colliding_line_names = colliding_line_names[::-1]
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                elif attacker.is_invincible:
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                
                elif clash_result == ClashResults.TIE:
                    clash_indicator = True
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                elif clash_result == ClashResults.WIN:
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                elif clash_result == ClashResults.LOSS:
                    #swap attacker and receiver
                    temp = attacker
                    attacker = receiver
                    receiver = temp
                    
                    #reverse the order of the colliding line names to math
                    #that player 2 is now the attacker.
                    colliding_line_names = colliding_line_names[::-1]
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
            
            else:
                attacker_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                    attacker.model.lines
                )
                colliding_line_names = self.test_attack_collision(
                    receiver_attack_hitboxes,
                    attacker_hitboxes
                )
                
                if attacker.is_invincible:
                    attack_result = None
                
                elif colliding_line_names:
                    #swap attacker and receiver
                    temp = attacker
                    attacker = receiver
                    receiver = temp
                    
                    attack_result = self.build_attack_result(
                        attacker,
                        receiver,
                        colliding_line_names, 
                        clash_indicator
                    )
                    
                else:
                    receiver_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                        receiver.model.lines
                    )
                    colliding_line_names = self.test_attack_collision(
                        attacker_attack_hitboxes, receiver_hitboxes
                    )
                    
                    if colliding_line_names:
                        attack_result = self.build_attack_result(
                            attacker,
                            receiver,
                            colliding_line_names, 
                            clash_indicator
                        )
                        
        else:
            receiver_hitboxes = self.hitbox_builder.get_hitbox_dictionary(
                receiver.model.lines
            )
            colliding_line_names = self.test_attack_collision(
                attacker_attack_hitboxes,
                receiver_hitboxes
            )
            
            if receiver.is_invincible:
                attack_result = None
            
            elif colliding_line_names:
                
                attack_result = self.build_attack_result(
                    attacker,
                    receiver,
                    colliding_line_names, 
                    clash_indicator
                )
        
        return attack_result
    
    def build_attack_result(
        self, 
        attacker, 
        receiver, 
        colliding_line_names, 
        clash_indicator
    ):
        colliding_lines = (
            attacker.model.lines[colliding_line_names[0]],
            receiver.model.lines[colliding_line_names[1]]
        )
        interaction_points = self.get_interaction_points(
            receiver,
            colliding_lines
        )
        
        attack_point = interaction_points[0]
        receive_point = interaction_points[1]
        knockback_vector = self.get_knockback_vector(receiver, attacker, attack_point)
        clash_position = (attack_point.pos[0],attack_point.pos[1])
        
        attack_result = AttackResult(
            attacker,
            receiver,
            attack_point,
            receive_point,
            knockback_vector,
            clash_indicator,
            clash_position
        )
        
        return attack_result
    
    def get_clash_result(self, attacker, receiver, colliding_line_names):
        colliding_lines = (
            receiver.model.lines[colliding_line_names[0]],
            attacker.model.lines[colliding_line_names[1]]
        )
        
        attacker_attack_type = attacker.action.attack_type
        receiver_attack_type = receiver.action.attack_type
        
        if attacker_attack_type == receiver_attack_type:
            return ClashResults.TIE
            
            #interaction_points = self.get_interaction_points(receiver, colliding_lines)
            #attack_damage = attacker.get_point_damage(interaction_points[0].name)
            #block_damage = receiver.get_point_damage(interaction_points[1].name)
            
            #if 5 > abs(attack_damage - block_damage):
            #    return ClashResults.TIE
            #elif attack_damage > block_damage:
            #    return ClashResults.WIN
            #else:
            #    return ClashResults.LOSS
        
        elif attacker_attack_type == self.get_type_clash_winner(attacker_attack_type, receiver_attack_type):
            return ClashResults.WIN
        else:
            return ClashResults.LOSS
    
    def get_type_clash_winner(self, attacker_attack_type, receiver_attack_type):
        if ((attacker_attack_type in InputActionTypes.QUICK_ATTACKS and 
        receiver_attack_type in InputActionTypes.TRICKY_ATTACKS) or
        (attacker_attack_type in InputActionTypes.TRICKY_ATTACKS and 
        receiver_attack_type in InputActionTypes.STRONG_ATTACKS) or
        (attacker_attack_type in InputActionTypes.STRONG_ATTACKS and 
        receiver_attack_type in InputActionTypes.QUICK_ATTACKS)):
            return receiver_attack_type
        else:
            return attacker_attack_type
    
    def get_interaction_points(self, receiver, colliding_lines):
        attacker_line_index = 0
        receiver_line_index = 1
        
        attack_point1 = colliding_lines[attacker_line_index].endPoint1
        attack_point2 = colliding_lines[attacker_line_index].endPoint2
        receiver_point1 = receiver.get_point(PointNames.TORSO_TOP)
        receiver_point2 = receiver.get_point(PointNames.TORSO_BOTTOM)
        
        point_pairs = [
            (attack_point1, receiver_point1),
            (attack_point1, receiver_point2),
            (attack_point2, receiver_point1),
            (attack_point2, receiver_point2)
        ]
        point_distances =  [
            mathfuncs.distance(attack_point1.pos, receiver_point1.pos),
            mathfuncs.distance(attack_point1.pos, receiver_point2.pos),
            mathfuncs.distance(attack_point2.pos, receiver_point1.pos),
            mathfuncs.distance(attack_point2.pos, receiver_point2.pos)
        ]
        
        shortest_distance = min(point_distances)
        
        return point_pairs[point_distances.index(shortest_distance)]

    def test_attack_collision(self, attack_hitbox_dictionary, receiver_hitbox_dictionary):
        colliding_line_names = None
        
        for attack_line_name, attack_hitboxes in attack_hitbox_dictionary.iteritems():
            for receiver_line_name, receiver_hitboxes in receiver_hitbox_dictionary.iteritems():
                for attack_hitbox in attack_hitboxes:
                    if attack_hitbox.collidelist(receiver_hitboxes) > -1:
                        colliding_line_names = (attack_line_name, receiver_line_name)
                        break
                if colliding_line_names:
                    break
            if colliding_line_names:
                break
        
        return colliding_line_names

    def get_knockback_vector(self, receiver, attacker, attack_point):
        """get the direction and magnitude of the knockback"""
        
        vector = attacker.get_point_position_change(attack_point.name)
        
        if (receiver.model.center()[0] > attacker.model.center()[0] and
        vector[0] < 0):
            vector[0] *= -1
        elif (receiver.model.center()[0] < attacker.model.center()[0] and
        vector[0] > 0):
            vector[0] *= -1
        
        return self.scale_knockback(vector)
    
    def scale_knockback(self, knockback_vector):
        """binds the scale of a knockback vector to control stun animation"""
        
        x = knockback_vector[0]
        y = knockback_vector[1]
        hypotenuse = math.hypot(x,y)
        
        knockback = .2
        
        if hypotenuse == 0:
            return 0, 0
        else:
            return 2 * knockback * x / hypotenuse, knockback * y / hypotenuse

class HitboxBuilder():
    """creates a list of rects that lie on a set of lines"""
    def get_hitbox_dictionary(self, lines):
        hitboxes = {}
        
        for name, line in lines.iteritems():
            if name == LineNames.HEAD:
                hitboxes[name] = [self.get_circle_hitbox(line)]
            else:
                hitboxes[name] = self.get_line_hitboxes(line)
        
        return hitboxes

    def get_hitboxes(self, lines):
        hitbox_dictionary = self.get_hitbox_dictionary(lines)
        hitbox_lines = []
        
        for hitbox_list in hitbox_dictionary.values():
            hitbox_lines.extend(hitbox_list)
        
        return hitbox_lines

    def get_circle_hitbox(self, circle):
        circle.set_length()
        radius = int(circle.length / 2)
        hitbox = pygame.Rect((circle.center()[0] - radius, \
                              circle.center()[1] - radius), \
                             (circle.length, circle.length))
        
        return hitbox

    def get_line_hitboxes(self, line):
        line_rects = []
        
        line.set_length()
        box_count = line.length / 7
        
        if box_count > 0:
            for pos in self.get_hitbox_positions(box_count, line):
                line_rects.append(pygame.Rect(pos, (14,14)))
        else:
            line_rects.append(pygame.Rect(line.endPoint1.pos, (14,14)))
        
        return line_rects

    def get_hitbox_positions(self, box_count, line):
            """gets top left of each hitbox on a line.
            
            box_count: the number of hit boxes"""
            hitbox_positions = []
            
            start_pos = line.endPoint1.pixel_pos()
            end_pos = line.endPoint2.pixel_pos()
            
            x_delta = end_pos[0] - start_pos[0]
            y_delta = end_pos[1] - start_pos[1]
            
            length = line.length
            length_to_hit_box_center = 0
            increment = line.length / box_count
            
            hitbox_positions.append((int(end_pos[0] - 7), int(end_pos[1] - 7)))
            
            length_to_hit_box_center += increment
            x_pos = start_pos[0] + x_delta - (
                (x_delta / length) * length_to_hit_box_center
            )
            y_pos = start_pos[1] + y_delta - (
                (y_delta / length) * length_to_hit_box_center
            )
            box_center = (x_pos, y_pos)
            
            for i in range(int(box_count)):
                hitbox_positions.append(
                    (int(box_center[0] - 7), int(box_center[1] - 7))
                )
                
                length_to_hit_box_center += increment
                x_pos = start_pos[0] + x_delta - (
                    (x_delta / length) * length_to_hit_box_center
                )
                y_pos = start_pos[1] + y_delta - (
                    (y_delta / length) * length_to_hit_box_center
                )
                box_center = (x_pos, y_pos)
            
            hitbox_positions.append((int(start_pos[0] - 7), int(start_pos[1] - 7)))
            
            return hitbox_positions

class ActionData():
    def __init__(
        self,
        action_state,
        direction
    ):
        self.action_state = action_state
        self.direction = direction
    
    def _pack(self):
        
        return self.action_state, self.direction

class TimedActionData(ActionData):
    def __init__(
        self,
        action_state,
        direction,
        timeout,
        timer
    ):
        ActionData.__init__(
            self, 
            action_state,
            direction
        )
        self.timeout = timeout
        self.timer = timer
    
    def _pack(self):
        return self.action_state, self.direction, self.timeout, self.timer

class AttackActionData(ActionData):
    def __init__(
        self,
        action_state,
        direction,
        animation_name
    ):
        ActionData.__init__(self, action_state, direction)
        self.animation_name = animation_name
    
    def _pack(self):
        return self.action_state, self.direction, self.animation_name

class GeneratedActionData(ActionData):
    def __init__(
        self,
        action_state,
        direction,
        first_frame_point_positions,
        last_frame_point_positions
    ):
        ActionData.__init__(self, action_state, direction)
        self.first_frame_point_positions = first_frame_point_positions
        self.last_frame_point_positions = last_frame_point_positions
    
    def _pack(self):
        return (self.action_state, self.direction, self.first_frame_point_positions,
        self.last_frame_point_positions)

class TransitionActionData(GeneratedActionData):
    def __init__(
        self,
        action_state,
        direction,
        first_frame_point_positions,
        last_action_state,
        last_action_animation_name,
        next_action_state,
        next_action_animation_name
    ):
        ActionData.__init__(
            self, 
            action_state, 
            direction
        )
        self.first_frame_point_positions = first_frame_point_positions
        self.last_action_state = last_action_state
        self.last_action_animation_name = last_action_animation_name
        self.next_action_state = next_action_state
        self.next_action_animation_name = next_action_animation_name
    
    def _pack(self):
        return (self.action_state, self.direction, self.first_frame_point_positions,
        self.last_action_state, self.last_action_animation_name, self.next_action_state,
        self.next_action_animation_name)

class StunActionData(GeneratedActionData, TimedActionData):
    def __init__(
        self,
        action_state,
        direction,
        first_frame_point_positions,
        knockback_vector,
        interaction_vector,
        interaction_point_name,
        timeout,
        timer
    ):
        ActionData.__init__(
            self, 
            action_state,
            direction
        )
        TimedActionData.__init__(
            self,
            action_state,
            direction,
            timeout,
            timer
        )
        
        self.first_frame_point_positions = first_frame_point_positions
        self.knockback_vector = knockback_vector
        self.interaction_vector = interaction_vector
        self.interaction_point_name = interaction_point_name
    
    def _pack(self):
        return (self.action_state, self.direction, self.first_frame_point_positions,
        self.knockback_vector, self.interaction_vector, self.interaction_point_name, 
        self.timeout, self.timer)

class ActionDataFactory():
    
    def create_action_data(self, player):
        return_data = None
        action_state = player.get_player_state()
        
        if action_state == PlayerStates.STUNNED:
            return_data = StunActionData(
                player.get_player_state(),
                player.direction,
                animation.get_frame_point_positions(
                    player.action.animation,
                    player.action.animation.frames[0]
                ),
                player.knockback_vector,
                player.interaction_vector,
                player.interaction_point.name,
                player.stun_timeout,
                player.stun_timer
            )
        
        elif action_state == PlayerStates.TRANSITION:
            return_data = self.create_transition_action_data(player.action)
        
        elif action_state == PlayerStates.JUMPING:
            return_data = TimedActionData(
                player.get_player_state(),
                player.direction,
                player.high_jump_timeout,
                player.jump_timer
            )
        
        elif action_state == PlayerStates.ATTACKING:
            return_data = AttackActionData(
                player.get_player_state(),
                player.direction,
                player.action.right_animation.name
            )
        
        else:
            return_data = ActionData(player.get_player_state(), player.direction)
        
        return return_data
    
    def create_transition_action_data(self, action):
        last_transition_action_data = None
        # action.last_action.action_state == PlayerStates.TRANSITION:
        #    last_transition_action_data = self.create_transition_action_data(
        #        action.last_action
        #    )
        
        return_data = TransitionActionData(
            PlayerStates.TRANSITION,
            action.direction,
            animation.get_frame_point_positions(
                action.animation,
                action.animation.frames[0]
            ),
            action.get_previous_action(action).action_state,
            action.get_previous_action(action).right_animation.name,
            action.next_action.action_state,
            action.next_action.right_animation.name
        )
        
        return return_data

class PlayerState():
    def __init__(
        self,
        animation_run_time,
        keys_pressed,
        action_data,
        reference_position,
        velocity,
        health,
        direction
    ):
        self.animation_run_time = animation_run_time
        self.keys_pressed = keys_pressed
        self.action_data = action_data
        self.reference_position = reference_position
        self.velocity = velocity
        self.health = health
        self.direction = direction
    
    def __eq__(self, x):
       
        return (
            self.animation_run_time == x.animation_run_time and
            self.action_data.action_state == x.action_data.action_state and
            self.reference_position == x.reference_position and
            self.velocity == x.velocity and
            self.health == x.health and
            self.direction == x.direction
        )
    
    def _pack(self):
        return (self.animation_run_time, self.keys_pressed, self.action_data,
        self.reference_position, self.velocity, self.health, self.direction)

class SimulationState():
    def __init__(
        self,
        player_states,
        match_time
    ):
        self.player_states = player_states
        self.match_time = match_time
    
    def __eq__(self, z):
        return reduce(
            lambda x, y: x and y,
            [
                self.player_states[player_position] == z.player_states[player_position]
                for player_position
                in self.player_states.keys()
            ]
        )
    
    def __ne__(self, z):
        return not self.__eq__(z)
    
    def _pack(self):
        return (self.player_states, self.match_time)

class NetworkedSimulation(MatchSimulation):
    def __init__(
        self,
        pipe_connection,
        timestep=20,
        player_type_dictionary=None,
        player_dictionary=None,
        player_position=PlayerPositions.NONE
    ):
        MatchSimulation.__init__(
            self,
            pipe_connection,
            timestep = timestep,
            player_type_dictionary = player_type_dictionary,
            player_dictionary = player_dictionary
        )
        
        self.player_position = player_position
        self.state_history = []
        self.input_history = []
        self.action_data_factory = ActionDataFactory()
        self.broadcast_interval = 60
        self.broadcast_timer = 0
    
    def step(self, player_keys_pressed, time_passed):
        """update the state of the players in the simulation"""
        
        self.accumulator += time_passed
        
        while self.accumulator > self.timestep:
            
            self.update_simulation_state(player_keys_pressed)
            
            self.state_history.append(self.get_simulation_state())
            self.input_history.append(
                self.get_updated_player_keys_pressed(player_keys_pressed)
            )
            self.accumulator -= self.timestep
    
    def handle_player_events(self, player_keys_pressed, timestep):
        """Advance player animations according to the current pygame events"""
        
        for player_position, active_player in self.player_dictionary.iteritems():
            player_type = self.player_type_dictionary[player_position]
            
            if player_type == PlayerTypes.HUMAN:
                active_player.handle_events(
                    player_keys_pressed[player_position],
                    timestep
                )
            elif player_type == PlayerTypes.BOT:
                [active_player.handle_events(other_player, timestep) 
                for other_player_position, other_player 
                in self.player_dictionary.iteritems()
                if not other_player_position == player_position]
            elif player_type == PlayerTypes.REMOTE:
                active_player.handle_events(
                    timestep
                )
            else:
                raise Exception(
                    "Invalid Player Type: " + player_type
                )
    
    def get_updated_player_keys_pressed(self, player_keys_pressed):
        """sync player keys pressed to ai decisions"""
        
        return dict([
            (player_position, player.get_last_input())
            for player_position, player in self.player_dictionary.iteritems()
        ])
    
    def get_simulation_state(self):
        player_state_dictionary = dict(
            [
                (player_position, self.get_player_state(player))
                for player_position, player 
                in self.player_dictionary.iteritems()
            ]
        )
        
        return SimulationState(
            player_state_dictionary,
            self.match_time
        )
    
    def get_player_state(self, player):
        inputs = []
        
        if len(self.input_history) > 1:
            inputs = self.input_history[-1]
        
        return PlayerState(
            player.model.animation_run_time,
            inputs,
            self.action_data_factory.create_action_data(player),
            player.model.position,
            player.model.velocity,
            player.health_meter,
            player.direction
        )
    
    def get_history_index(self, input_match_time):
        
        return_index = None
        
        time_difference = self.match_time - input_match_time
        
        if time_difference > 0:
            return_index = -1 - int(time_difference / self.timestep)
        elif time_difference == 0:
            return_index = -1
        
        return return_index
    
    def replay(self, input_step_count):
        for i in range(input_step_count,0,-1):
            self.update_match_state()
            
            self.update_player_states(
                self.input_history[-i]
            )
            self.state_history.append(
                self.get_simulation_state()
            )

class ServerSimulation(NetworkedSimulation):
    
    def run(self):
        while 1:
            while self.pipe_connection.poll():
                data = self.pipe_connection.recv()
                action_type = data[SimulationDataKeys.ACTION]
                
                if action_type == SimulationActionTypes.STOP or data == 'STOP':
                    raise Exception("Terminating Simulation Process!")
                
                elif action_type == SimulationActionTypes.STEP:
                    self.step(
                        data[SimulationDataKeys.KEYS_PRESSED], 
                        data[SimulationDataKeys.TIME_PASSED]
                    )
                    self.pipe_connection.send(
                        {
                            SimulationDataKeys.ACTION : SimulationActionTypes.STEP,
                            SimulationDataKeys.RENDERING_INFO : self.get_rendering_info()
                        }
                    )
                    
                    self.broadcast_timer += data[SimulationDataKeys.TIME_PASSED]
                    
                    if self.broadcast_timer > self.broadcast_interval:
                        state = self.get_simulation_state()
                        #print([player_dat.action_data for player_dat in state.player_states.values()])
                        self.pipe_connection.send(
                            {
                                SimulationDataKeys.ACTION : SimulationActionTypes.GET_STATE,
                                SimulationDataKeys.SIMULATION_STATE : state
                            }
                        )
                        self.broadcast_timer = 0
                    
                    for player in self.player_dictionary.values():
                        player.clear_events() 
                       
                elif action_type == SimulationActionTypes.UPDATE_INPUT:
                    self.sync_to_client(
                        data[SimulationDataKeys.MATCH_TIME],
                        data[SimulationDataKeys.PLAYER_POSITION],
                        data[SimulationDataKeys.KEYS_PRESSED]
                    )
                
                elif action_type == SimulationActionTypes.UPDATE_STATE:
                    pass #Since hosts are the authority they don't get checked against
                    #remote simulation states.
                else:
                    raise Exception("Invalid Action Type: " + str(action_type))
            
            self.clock.tick(100)
    
    def sync_to_client(self, match_time, player_position, keys_pressed):
        """replay the given number of steps with a client's inputs"""
        
        history_index = self.get_history_index(match_time)
        
        self.state_history = self.state_history[:history_index]
        
        for member in keys_pressed:
            if self.input_history[history_index][player_position] != member[player_position]:
                self.input_history[history_index][player_position] = member[player_position]
                self.replay(len(self.input_history) - len(self.state_history))
    
    def send_simulation_state(self):
        self.pipe_connection.send(self.get_simulation_state())

class ClientSimulation(NetworkedSimulation):
    
    def run(self):
        while 1:
            while self.pipe_connection.poll():
                data = self.pipe_connection.recv()
                
                if data == 'STOP':
                    raise Exception("Terminating Simulation Process!")
                
                action_type = data[SimulationDataKeys.ACTION]
                
                if action_type == SimulationActionTypes.STEP:
                    self.step(
                        data[SimulationDataKeys.KEYS_PRESSED], 
                        data[SimulationDataKeys.TIME_PASSED]
                    )
                
                    self.pipe_connection.send(
                        {
                            SimulationDataKeys.ACTION : SimulationActionTypes.STEP,
                            SimulationDataKeys.RENDERING_INFO : self.get_rendering_info()
                        }
                    )
                    
                    for player in self.player_dictionary.values():
                        player.clear_events() 
                    
                    if self.player_position != PlayerPositions.NONE:
                        
                        if self.match_time % 120 == 0 and len(self.input_history) >= 1:
                            self.pipe_connection.send(
                                {
                                    SimulationDataKeys.ACTION : SimulationActionTypes.UPDATE_INPUT,
                                    SimulationDataKeys.KEYS_PRESSED : self.input_history[-6:-1],
                                    SimulationDataKeys.PLAYER_POSITION : self.player_position,
                                    SimulationDataKeys.MATCH_TIME : self.match_time
                                }
                            )
                elif action_type == SimulationActionTypes.UPDATE_STATE:
                    try:
                        self.sync_to_server_state(
                            data[SimulationDataKeys.SIMULATION_STATE]
                        )
                    except:
                       print(self.state_history)
                       print(self.input_history)
                       raise 
                
                elif action_type == SimulationActionTypes.UPDATE_INPUT:
                    
                    pass #clients should only update against the player state of the
                    #host
                else:
                    raise Exception("Invalid Action Type: " + str(action_type))
            
            self.clock.tick(100)
    
    def sync_to_server_state(self, server_simulation_state):
        #sync players to simulation state
        
        #get matching history index. NOTE - history index is negative
        #history_index = self.get_history_index(server_simulation_state.match_time)
        
        #if history_index != None and abs(history_index) < len(self.state_history):
        #    client_simulation_state = self.state_history[history_index]
            
        #    if client_simulation_state != server_simulation_state:
                
        #        self.state_history = self.state_history[:history_index]
                #sync player states to simulation state
        for player_position, player_state in server_simulation_state.player_states.iteritems():
            self.player_dictionary[player_position].sync_to_server_state(
                player_state
            )
            
            #change history to match
        #    self.state_history.append(server_simulation_state)
            
            #replay from point in history
        #    self.replay(len(self.input_history) - len(self.state_history))

serializable.register(PlayerState)
serializable.register(SimulationState)
serializable.register(ActionData)
serializable.register(TimedActionData)
serializable.register(AttackActionData)
serializable.register(GeneratedActionData)
serializable.register(TransitionActionData)
serializable.register(StunActionData)
