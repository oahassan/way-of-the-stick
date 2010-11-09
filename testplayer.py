import pygame
import player
import gamestate
from controlsdata import InputActionTypes

class TestPlayer(player.Player):
    def __init__(self):
        player.Player.__init__(self, (0,0))
        
        self.action = None
        
    def load_action(self, action_type, animation):
        factory = player.ActionFactory()
        
        self.action = self.create_action(action_type, animation)
        self.action.animation = self.action.right_animation
        self.action.set_player_state(self)
        position = (250, gamestate.stage.ground.position[1] - self.model.height)
        
        self.model.move_model(position)
    
    def handle_events(self):
        time_passed = gamestate.clock.get_time()
        self.model.time_passed = time_passed
        
        self.action.move_player(self)
        
        player.draw_model(self)
    
    def create_action(self, action_type, animation = None, direction = player.PlayerStates.FACING_RIGHT, key = pygame.K_UP):
        return_action = None
        factory = player.ActionFactory()
        
        if action_type == player.PlayerStates.STANDING:
            return_action = factory.create_stand(animation)
        elif action_type == player.PlayerStates.LANDING:
            return_action = factory.create_land(animation)
        elif action_type == player.PlayerStates.FLOATING:
            return_action = factory.create_float(animation)
        elif action_type == player.PlayerStates.STUNNED:
            return_action = factory.create_stun()
        elif action_type == player.PlayerStates.JUMPING:
            return_action = factory.create_jump(animation)
            
        elif action_type == player.PlayerStates.CROUCHING:
            return_action = factory.create_crouch(animation)
            
        elif action_type == player.PlayerStates.WALKING:
            return_action = factory.create_walk(direction, animation)
            
        elif action_type == player.PlayerStates.RUNNING:
            return_action = factory.create_run(direction, animation)
        
        elif action_type in InputActionTypes.ATTACKS:
            return_action = factory.create_attack(action_type, animation, self.model)
                    
        return return_action
    
    def handle_animation_end(self):
        self.time_passed = 0
        self.action.set_player_state(self)
        
        position = (250, gamestate.stage.ground.position[1] - self.model.height)
        self.model.move_model(position)
