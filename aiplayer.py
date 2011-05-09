from random import choice
import copy
import pygame
import gamestate
import physics
import animationexplorer
from player import Player, PlayerTypes
from stick import LineNames
from enumerations import PlayerStates, CommandDurations, InputActionTypes, AttackTypes
from playerutils import ActionFactory, Transition, Action, Attack

class Bot(Player):
    """an algorithm controlled player"""
    
    def __init__(self, position):
        Player.__init__(self, position)
        self.actions = {}
        self.player_type = PlayerTypes.BOT
        
        #a dictionary mapping attacks to a list of rects for each frame
        self.attack_rects = {}
        self.attack_rect_deltas = {}
        
    def load_moveset(self, moveset):
        self.moveset = moveset
        
        factory = ActionFactory(self)
        
        #load rest animation
        stand_animation = moveset.movement_animations[PlayerStates.STANDING]
        stand_action = factory.create_stand(stand_animation)
        self.actions[PlayerStates.STANDING] = stand_action
        
        #load walk animation
        walk_animation = moveset.movement_animations[PlayerStates.WALKING]
        walk_action = factory.create_walk(walk_animation)
        self.actions[PlayerStates.WALKING] = walk_action
        
        #load run animation
        run_animation = moveset.movement_animations[PlayerStates.RUNNING]
        run_action = factory.create_run(run_animation)
        self.actions[PlayerStates.RUNNING] = run_action
        
        #load jump animation
        jump_animation = moveset.movement_animations[PlayerStates.JUMPING]
        jump_action = factory.create_jump(jump_animation)
        self.actions[PlayerStates.JUMPING] = jump_action
        
        #load land animation
        land_animation = moveset.movement_animations[PlayerStates.LANDING]
        self.actions[PlayerStates.LANDING] = factory.create_land(land_animation)
        
        #load float animation
        float_animation = moveset.movement_animations[PlayerStates.FLOATING]
        self.actions[PlayerStates.FLOATING] = factory.create_float(float_animation)
        
        #load stunned action
        self.actions[PlayerStates.STUNNED] = factory.create_stun()
        
        #load transition action
        self.actions[PlayerStates.TRANSITION] = Transition()
                
        #load crouch animation
        crouch_animation = moveset.movement_animations[PlayerStates.CROUCHING]
        crouch_action = factory.create_crouch(crouch_animation)
        self.actions[PlayerStates.CROUCHING] = crouch_action
        
        self.actions[PlayerStates.ATTACKING] = []
        
        #load attack actions
        for attack_name in moveset.get_attacks():
            
            attack_action = factory.create_attack(
                moveset.get_attack_type(attack_name),
                moveset.attack_animations[attack_name],
                self.model
            )
                
            self.actions[PlayerStates.ATTACKING].append(attack_action)
        
        self.actions[PlayerStates.STANDING].set_player_state(self)
        self.set_attack_rect_data()
    
    def set_attack_rect_data(self):
        """build a list of rects bounding the attack lines in each frame of an
        attack animation.  Each rect's position is relative the first rect and
        the first rect's position is (0,0)"""
        
        for attack in self.actions[PlayerStates.ATTACKING]:
            attack_rects = self.get_attack_rects(
                attack.right_animation,
                attack.attack_type
            )
            self.attack_rects[attack.right_animation.name] = attack_rects
            
            initial_position = attack_rects[0].topleft
            self.attack_rect_deltas[attack.right_animation.name] = \
                [(rect.left - initial_position[0], rect.top - initial_position[1]) for rect in attack_rects]
    
    def get_attack_rects(self, attack_animation, attack_type):
        """creates a rect surrounding the attack lines for each frame in
        the given animation"""
        
        return_rects = []
        
        for frame in attack_animation.frames:
            return_rects.append(self.get_attack_rect(frame, attack_type))
        
        initial_position = return_rects[0].topleft
        
        for frame_rect in return_rects:
            frame_rect.move(-initial_position[0], -initial_position[1])
        
        return return_rects
    
    def get_attack_rect(self, frame, attack_type):
        attack_line_names = None
        
        if (attack_type in InputActionTypes.PUNCHES or
        attack_type == AttackTypes.PUNCH):
            attack_line_names = Attack.PUNCH_LINE_NAMES
        elif (attack_type in InputActionTypes.KICKS or
        attack_type == AttackTypes.KICK):
            attack_line_names = Attack.KICK_LINE_NAMES
        
        frame_rect = None
        
        for line in frame.lines():
            if line.name in attack_line_names:
                if frame_rect == None:
                    frame_rect = pygame.Rect(line.get_enclosing_rect())
                else:
                    frame_rect.union_ip(pygame.Rect(line.get_enclosing_rect()))
        
        return frame_rect
    
    def handle_events(self, enemy, time_passed):
        if self.handle_input_events:
            self.set_action(enemy)
        
        Player.handle_events(self, time_passed)
    
    def get_direction(self, enemy):
        direction = PlayerStates.FACING_LEFT
        
        if enemy.model.position[0] > self.model.position[0]:
            direction = PlayerStates.FACING_RIGHT
        
        return direction
    
    def set_action(self, enemy):
        
        attack = None
        
        if self.action.action_state != PlayerStates.ATTACKING:
            attack = self.get_in_range_attack(enemy)
        
        next_action = None
        
        if attack != None:
            if attack.test_state_change(self):
                next_action = attack
        else:
            next_action = self.move_towards_enemy(enemy)
        
        if next_action != None:
            next_action.direction = self.get_direction(enemy)
        
        if (next_action != None
        and next_action != self.action
        and self.get_player_state() != PlayerStates.TRANSITION):
            self.transition(next_action)
    
    def move_towards_enemy(self, enemy):
        x_distance = abs(enemy.model.position[0] - self.model.position[0])
        y_distance = enemy.model.position[1] - self.model.position[1]
        
        movement = None
        
        if x_distance > 150:
            action = self.actions[PlayerStates.RUNNING]
            
            if self.action != action:
                movement = action
                self.dash_timer = 0
        
        elif x_distance <= 150:
            action = self.actions[PlayerStates.WALKING]
            
            if self.action != action:
                movement = action
        
        if (((self.action.action_state == PlayerStates.STANDING) or
            (self.action.action_state == PlayerStates.WALKING) or
            (self.action.action_state == PlayerStates.RUNNING)) and
            (y_distance < -20) and
            (self.model.velocity[0] > 0)):
            movement = self.actions[PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(self))):
            return movement
        else:
            return None
    
    def get_in_range_attack(self, enemy):
        in_range_attacks = []
        
        if self.is_aerial():
            in_range_attacks = [attack for attack in self.actions[PlayerStates.ATTACKING] if self.aerial_attack_in_range(attack, enemy)]
        else:
            in_range_attacks = [attack for attack in self.actions[PlayerStates.ATTACKING] if self.attack_in_range(attack, enemy)]
        
        if len(in_range_attacks) > 0:
            return choice(in_range_attacks)
        else:
            return None
    
    def aerial_attack_in_range(self, attack, enemy):
        bottom_right_top_left = self.model.get_top_left_and_bottom_right()
        bottom_right = bottom_right_top_left[1]
        top_left = bottom_right_top_left[0]
        
        attack_range_point = top_left
        
        if self.direction == PlayerStates.FACING_LEFT:
            attack_range_point = (bottom_right[0] - attack.range[0], \
                                  top_left[1])
        
        attack_rect = pygame.Rect(attack_range_point, (attack.range[0], attack.range[1]))
        enemy_rect = pygame.Rect(enemy.model.position, (enemy.model.width, enemy.model.height))
        
        in_range = attack_rect.colliderect(enemy_rect)
        
        return in_range
    
    def attack_in_range(self, attack, enemy):
        
        attack_rect_deltas = self.attack_rect_deltas[attack.right_animation.name]
        attack_rects = self.set_rect_positions(
            self.get_initial_attack_rect(attack),
            self.attack_rects[attack.right_animation.name],
            attack_rect_deltas
        )
        
        enemy_rect = pygame.Rect(enemy.model.position, (enemy.model.width, enemy.model.height))
        
        in_range = enemy_rect.collidelist(attack_rects)
        
        return in_range > -1
    
    def set_rect_positions(
        self,
        initial_rect,
        attack_rects,
        attack_rect_deltas
    ): 
        new_rects = []
        
        for i in range(len(attack_rects)):
            rect = attack_rects[i]
            delta = None
            
            if self.model.orientation == physics.Orientations.FACING_RIGHT:
                delta = (
                    initial_rect.left - rect.left + attack_rect_deltas[i][0],
                    initial_rect.top - rect.top + attack_rect_deltas[i][1]
                )
            else:
                 delta = (
                    initial_rect.left - rect.left - attack_rect_deltas[i][0],
                    initial_rect.top - rect.top + attack_rect_deltas[i][1]
                )   
            
            new_rect = rect.move(*delta)
            new_rects.append(new_rect)
            
            #debugging code
            #pygame.draw.rect(gamestate.screen, (255,0,0), new_rect, 1)
            #gamestate.new_dirty_rects.append(new_rect)
        
        return new_rects
    
    def get_initial_attack_rect(self, attack):
        animation = attack.right_animation
        attack_rect = self.get_attack_rect(
            animation.frames[0],
            attack.attack_type
        )
        
        current_position = self.model.position
        
        if self.is_aerial() == False:
            rect = self.get_enclosing_rect()
            
            current_position = (
                current_position[0],
                rect.bottom - animation.frames[0].image_height()
            )
        
        animation_position = animation.frames[0].get_reference_position()
        
        if self.model.orientation == physics.Orientations.FACING_LEFT:
            animation_position = (
                animation_position[0] + animation.frames[0].image_width(),
                animation_position[1]
            )
        
        attack_rect = attack_rect.move(
            current_position[0] - animation_position[0],
            current_position[1] - animation_position[1]
        )
        
        #debugging code
        #pygame.draw.rect(gamestate.screen, (0,0,255), attack_rect)
        #gamestate.new_dirty_rects.append(attack_rect)
        
        return attack_rect
