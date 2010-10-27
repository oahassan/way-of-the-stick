import copy
import physics
import animationexplorer
import player
from controlsdata import InputActionTypes

class Bot(player.Player):
    """an algorithm controlled player"""
    
    def __init__(self, position):
        player.Player.__init__(self, position)
        self.actions = {}
        self.player_type = player.PlayerTypes.BOT
    
    def load_moveset(self, moveset):
        self.moveset = moveset
        
        factory = player.ActionFactory()
        
        #load rest animation
        stand_animation = moveset.movement_animations[player.PlayerStates.STANDING]
        stand_action = factory.create_stand(stand_animation)
        self.actions[player.PlayerStates.STANDING] = stand_action
        
        #load walk animation
        walk_animation = moveset.movement_animations[player.PlayerStates.WALKING]
        walk_right_action = factory.create_walk(player.PlayerStates.FACING_RIGHT, \
                                                walk_animation)
        self.actions[player.PlayerStates.WALKING] = [walk_right_action]
        
        walk_left_action = factory.create_walk(player.PlayerStates.FACING_LEFT, \
                                               walk_animation)
        self.actions[player.PlayerStates.WALKING].append(walk_left_action)
        
        #load run animation
        run_animation = moveset.movement_animations[player.PlayerStates.RUNNING]
        run_right_action = factory.create_run(player.PlayerStates.FACING_RIGHT, \
                                             run_animation)
        self.actions[player.PlayerStates.RUNNING] = [run_right_action]
        
        run_left_action = factory.create_run(player.PlayerStates.FACING_LEFT, \
                                            run_animation)
        self.actions[player.PlayerStates.RUNNING].append(run_left_action)
        
        #load jump animation
        jump_animation = moveset.movement_animations[player.PlayerStates.JUMPING]
        jump_action = factory.create_jump(jump_animation)
        self.actions[player.PlayerStates.JUMPING] = jump_action
        
        #load land animation
        land_animation = moveset.movement_animations[player.PlayerStates.LANDING]
        self.actions[player.PlayerStates.LANDING] = factory.create_land(land_animation)
        
        #load float animation
        float_animation = moveset.movement_animations[player.PlayerStates.FLOATING]
        self.actions[player.PlayerStates.FLOATING] = factory.create_float(float_animation)
        
        #load stunned animation
        self.actions[player.PlayerStates.STUNNED] = factory.create_stun()
        
        #load crouch animation
        crouch_animation = moveset.movement_animations[player.PlayerStates.CROUCHING]
        crouch_action = factory.create_crouch(crouch_animation)
        self.actions[player.PlayerStates.CROUCHING] = crouch_action
        
        self.actions[player.PlayerStates.ATTACKING] = []
        
        #load attack actions
        for attack_type, attack_animation in moveset.attack_animations.iteritems():
            
            if attack_type in InputActionTypes.ATTACKS:
                
                attack_action = factory.create_attack(attack_type, attack_animation, self.model)
                
                self.actions[player.PlayerStates.ATTACKING].append(attack_action)
        
        self.actions[player.PlayerStates.STANDING].set_player_state(self)
    
    def handle_events(self, enemy):
        #self.set_action(enemy)
        player.Player.handle_events(self)
    
    def set_action(self, enemy):
        direction = player.PlayerStates.FACING_LEFT
        
        if enemy.model.position[0] > self.model.position[0]:
            direction = player.PlayerStates.FACING_RIGHT
        
        self.direction = direction
        attack = self.get_in_range_attack(enemy)
        
        if attack != None:
            if attack.test_state_change(self):
                attack.set_player_state(self)
        else:
            self.move_towards_enemy(enemy)
    
    def move_towards_enemy(self, enemy):
        x_distance = abs(enemy.model.position[0] - self.model.position[0])
        y_distance = enemy.model.position[1] - self.model.position[1]
        
        movement = None
        
        if x_distance > 150:
            for action in self.actions[player.PlayerStates.RUNNING]:
                if ((action.direction == self.direction) and
                    (self.action != action)):
                    movement = action
                    self.dash_timer = 0
                    break
        elif x_distance <= 150:
            for action in self.actions[player.PlayerStates.WALKING]:
                if ((action.direction == self.direction) and
                    (self.action != action)):
                    movement = action
                    break
        
        if (((self.action.action_state == player.PlayerStates.WALKING) or
            (self.action.action_state == player.PlayerStates.RUNNING)) and
            (y_distance < -20)):
            movement = self.actions[player.PlayerStates.JUMPING]
        
        if ((movement != None) and
            (movement.test_state_change(self))):
            movement.set_player_state(self)
    
    def get_in_range_attack(self, enemy):
        in_range_attack = None
        
        for attack in self.actions[player.PlayerStates.ATTACKING]:
            if self.attack_in_range(attack, enemy):
                in_range_attack = attack
                break
        
        return in_range_attack
