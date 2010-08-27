import copy
import pygame
import animationexplorer
import player
import wotsuievents
import gamestate
import movesetdata
import actionwizard

class HumanPlayer(player.Player):
    def __init__(self, position):
        player.Player.__init__(self, position)
        self.input_action = None
        self.bound_keys = []
        self.key_bindings = {}
    
    def set_action(self):
        #Change state if key is released
        if (self.input_action != None and
            wotsuievents.key_released(self.input_action.key)):
                if self.input_action.key_release_action != None:
                    self.input_action.key_release_action.set_player_state(self)
                self.input_action = None
        
        for key in wotsuievents.keys_pressed:
            if key in self.key_bindings.keys():
                if self.is_aerial():
                    if key == pygame.K_UP:
                        self.handle_key_input(key)
                    elif ((key in self.moveset.movement_key_to_movement_type.keys())
                    and (self.moveset.movement_key_to_movement_type[key] in movesetdata.MovementTypes.AERIAL_MOVEMENT_TYPES)):
                        self.handle_aerial_motion_input(key)
                    elif key in self.moveset.attack_keys.values():
                        self.handle_key_input(key)
                elif self.action.action_state == player.PlayerStates.STUNNED:
                    if key in self.moveset.movement_key_to_movement_type.keys():
                        self.handle_stun_motion_input(key)
                else:
                    self.handle_key_input(key)
    
    def handle_key_input(self,key):
        for input_action in self.key_bindings[key]:    
            if input_action.action.test_state_change(self):
                input_action.action.set_player_state(self)
                self.input_action = input_action
                break
    
    def handle_aerial_motion_input(self,key):
        movement_type = self.moveset.movement_key_to_movement_type[key]
        
        if movement_type == movesetdata.MovementTypes.MOVE_LEFT:
            self.model.accelerate(-1*self.aerial_acceleration,0)
        elif movement_type == movesetdata.MovementTypes.MOVE_RIGHT:
            self.model.accelerate(self.aerial_acceleration,0)
        # elif movement_type == movesetdata.MovementTypes.MOVE_UP:
            # self.model.accelerate(0,-1*self.aerial_acceleration)
        elif movement_type == movesetdata.MovementTypes.MOVE_DOWN:
            self.model.accelerate(0,5*self.aerial_acceleration)
    
    def handle_stun_motion_input(self,key):
        movement_type = self.moveset.movement_key_to_movement_type[key]
        
        if movement_type == movesetdata.MovementTypes.MOVE_LEFT:
            self.model.accelerate(-1*self.aerial_acceleration,0)
        elif movement_type == movesetdata.MovementTypes.MOVE_RIGHT:
            self.model.accelerate(self.aerial_acceleration,0)
        elif movement_type == movesetdata.MovementTypes.MOVE_UP:
            self.model.accelerate(0,-1*self.aerial_acceleration)
        elif movement_type == movesetdata.MovementTypes.MOVE_DOWN:
            self.model.accelerate(0,5*self.aerial_acceleration)
    
    def load_actions(self):
        factory = player.ActionFactory()
        
        unbound_actions = actionwizard.get_unbound_actions()
        for action_type, animation in unbound_actions.iteritems():
            self.actions[action_type] = self.create_action(action_type, animation)
        input_actions = actionwizard.get_input_actions()
        
        for action_type, key_bindings in input_actions.iteritems():
            for key, action_definition in key_bindings.iteritems():
                animation = action_definition[1]
                direction = action_definition[0]
                input_action = None
                
                if action_type in player.AttackTypes.ATTACK_TYPES:
                    action = factory.create_attack(action_type, animation, self.model)
                    input_action = player.InputAction(action, None, key)
                else:
                    input_action = self.create_action(action_type, \
                                                      animation, \
                                                      direction, \
                                                      key)
                
                if key not in self.key_bindings:
                    self.key_bindings[key] = []
                
                self.key_bindings[key].append(input_action)
    
    def load_moveset(self, moveset):
        self.moveset = moveset
        
        factory = player.ActionFactory()
        
        for movement in player.PlayerStates.UNBOUND_MOVEMENTS:
            if movement == player.PlayerStates.STUNNED:
                self.actions[movement] = self.create_action(movement)
            else:
                movement_animation = moveset.movement_animations[movement]
                self.actions[movement] = self.create_action(movement, movement_animation)
        
        #Set move up actions
        jump_key = moveset.movement_keys[movesetdata.MovementTypes.MOVE_UP]
        jump_action = self.create_action(player.PlayerStates.JUMPING, \
                                         moveset.movement_animations[player.PlayerStates.JUMPING], \
                                         None, \
                                         jump_key)
        self.key_bindings[jump_key] = [jump_action]
        
        #Set move down actions
        crouch_key = moveset.movement_keys[movesetdata.MovementTypes.MOVE_DOWN]
        crouch_action = self.create_action(player.PlayerStates.CROUCHING, \
                                           moveset.movement_animations[player.PlayerStates.CROUCHING], \
                                           None, \
                                           crouch_key)
        self.key_bindings[crouch_key] = [crouch_action]
        
        #Set move right actions
        move_right_key = moveset.movement_keys[movesetdata.MovementTypes.MOVE_RIGHT]
        walk_right_action = self.create_action(player.PlayerStates.WALKING, \
                                               moveset.movement_animations[player.PlayerStates.WALKING], \
                                               player.PlayerStates.FACING_RIGHT, \
                                               move_right_key)
        run_right_action = self.create_action(player.PlayerStates.RUNNING, \
                                               moveset.movement_animations[player.PlayerStates.RUNNING], \
                                               player.PlayerStates.FACING_RIGHT, \
                                               move_right_key)
        self.key_bindings[move_right_key] = [walk_right_action,run_right_action]
        
        #Set move left actions
        move_left_key = moveset.movement_keys[movesetdata.MovementTypes.MOVE_LEFT]
        walk_left_action = self.create_action(player.PlayerStates.WALKING, \
                                              moveset.movement_animations[player.PlayerStates.WALKING], \
                                              player.PlayerStates.FACING_LEFT, \
                                              move_left_key)
        run_left_action = self.create_action(player.PlayerStates.RUNNING, \
                                             moveset.movement_animations[player.PlayerStates.RUNNING], \
                                             player.PlayerStates.FACING_LEFT, \
                                             move_left_key)
        self.key_bindings[move_left_key] = [walk_left_action,run_left_action]
        
        #Set attack actions
        for attack_name, attack_animation in moveset.attack_animations.iteritems():
            if moveset.attack_is_complete(attack_name):
                attack_key = moveset.attack_keys[attack_name]
                attack_type = moveset.attack_types[attack_name]
                attack_action = factory.create_attack(attack_type, attack_animation, self.model)
                input_action = player.InputAction(attack_action, None, attack_key)
                
                self.key_bindings[attack_key] = [input_action]
        
        self.actions[player.PlayerStates.STANDING].set_player_state(self)
    
    def create_action(self, action_type, animation = None, direction = None, key = None):
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
            action = factory.create_jump(animation)
            return_action = player.InputAction(action, \
                                               None, \
                                               key)
        elif action_type == player.PlayerStates.CROUCHING:
            action = factory.create_crouch(animation)
            return_action = player.InputAction(action, \
                                               self.actions[player.PlayerStates.STANDING], \
                                               key)
        elif action_type == player.PlayerStates.WALKING:
            action = factory.create_walk(direction, animation)
            return_action = player.InputAction(action, \
                                               self.actions[player.PlayerStates.STANDING], \
                                               key)
        elif action_type == player.PlayerStates.RUNNING:
            action = factory.create_run(direction, animation)
            return_action = player.InputAction(action, \
                                               self.actions[player.PlayerStates.STANDING], \
                                               key)
        
        return return_action
    
    def handle_events(self):
        self.set_action()
        player.Player.handle_events(self)
