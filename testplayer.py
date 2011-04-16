import pygame
from player import Player, draw_model
from playerutils import ActionFactory
from enumerations import PlayerStates, AttackTypes
import gamestate
import math

from controlsdata import InputActionTypes

class TestPlayer(Player):
    def __init__(self):
        Player.__init__(self, (0,0))
        
        self.action = None
        
    def load_action(self, action_type, animation):
        factory = ActionFactory()
        
        self.action = self.create_action(action_type, animation)
        self.action.animation = self.action.right_animation
        
        #position model to be on ground when its synced to the first frame
        self.set_initial_position()
        self.action.set_player_state(self)
    
    def set_initial_position(self):
        self.model.set_frame_point_pos(self.action.animation.frame_deltas[0])
        position = (250, math.ceil(gamestate.stage.ground.position[1] - self.model.height))
        
        self.model.move_model(position)
    
    def handle_events(self):
        time_passed = gamestate.clock.get_time()
        self.model.time_passed = time_passed
        
        self.action.move_player(self)
        
        draw_model(self, gamestate.screen)
    
    def create_action(self, action_type, animation = None, direction = PlayerStates.FACING_RIGHT, key = pygame.K_UP):
        return_action = None
        factory = ActionFactory()
        
        if action_type == PlayerStates.STANDING:
            return_action = factory.create_stand(animation)
        elif action_type == PlayerStates.LANDING:
            return_action = factory.create_land(animation)
        elif action_type == PlayerStates.FLOATING:
            return_action = factory.create_float(animation)
        elif action_type == PlayerStates.STUNNED:
            return_action = factory.create_stun()
        elif action_type == PlayerStates.JUMPING:
            return_action = factory.create_jump(animation)
            
        elif action_type == PlayerStates.CROUCHING:
            return_action = factory.create_crouch(animation)
            
        elif action_type == PlayerStates.WALKING:
            return_action = factory.create_walk(animation)
            
        elif action_type == PlayerStates.RUNNING:
            return_action = factory.create_run(animation)
        
        elif (action_type in InputActionTypes.ATTACKS or
        action_type in AttackTypes.ATTACK_TYPES):
            return_action = factory.create_attack(action_type, animation, self.model)
                    
        return return_action
    
    def handle_animation_end(self):
        self.model.time_passed = 0
        self.set_initial_position()
        self.action.set_player_state(self)
