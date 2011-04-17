import pygame
import settingsdata

class PlayerSoundLibrary():
    def __init__(self, attack_actions, run_action, walk_action):
        self.movement_sounds = {
            PlayerStates.WALKING : [
                pygame.mixer.Sound("sounds/step1-sound.ogg"),
                pygame.mixer.Sound("sounds/step2-sound.ogg"),
                pygame.mixer.Sound("sounds/step3-sound.ogg"),
                pygame.mixer.Sound("sounds/step4-sound.ogg")
            ],
            PlayerStates.RUNNING : [
                pygame.mixer.Sound("sounds/step1-sound.ogg"),
                pygame.mixer.Sound("sounds/step2-sound.ogg"),
                pygame.mixer.Sound("sounds/step3-sound.ogg"),
                pygame.mixer.Sound("sounds/step4-sound.ogg")
            ],
            PlayerStates.JUMPING : [
                pygame.mixer.Sound("sounds/jump-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.movement_sounds)
        
        self.attack_sounds = {
            InputActionTypes.WEAK_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.MEDIUM_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.STRONG_PUNCH : [
                pygame.mixer.Sound("sounds/punch-sound.ogg")
            ],
            InputActionTypes.WEAK_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ],
            InputActionTypes.MEDIUM_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ],
            InputActionTypes.STRONG_KICK : [
                pygame.mixer.Sound("sounds/kick-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.attack_sounds)
        
        self.hit_sounds = {
            InputActionTypes.WEAK_PUNCH : [
                pygame.mixer.Sound("sounds/hit-sound.ogg")
            ],
            InputActionTypes.MEDIUM_PUNCH : [
                pygame.mixer.Sound("sounds/medium-hit-sound.ogg")
            ],
            InputActionTypes.STRONG_PUNCH : [
                pygame.mixer.Sound("sounds/strong-hit-sound.ogg")
            ],
            InputActionTypes.WEAK_KICK : [
                pygame.mixer.Sound("sounds/hit-sound.ogg")
            ],
            InputActionTypes.MEDIUM_KICK : [
                pygame.mixer.Sound("sounds/medium-hit-sound.ogg")
            ],
            InputActionTypes.STRONG_KICK : [
                pygame.mixer.Sound("sounds/strong-hit-sound.ogg")
            ]
        }
        self.set_sound_volumes(self.hit_sounds)
    
    def set_sound_volumes(self, sound_dict):
        for sound_list in sound_dict.values():
            for sound in sound_list:
                sound.set_volume(settingsdata.get_sound_volume())

class SoundMap():
    def __init__(self):
        self.frame_sounds = []
        self.frame_sound_index = 0
        self.current_sound_channel = None
        self.last_frame_index = 0
        self.current_sound_channel = None

class GroundMovementSoundMap(SoundMap):
    def __init__(self):
        self.point_on_ground = {
            stick.PointNames.RIGHT_HAND : False,
            stick.PointNames.LEFT_HAND : False,
            stick.PointNames.RIGHT_FOOT : False,
            stick.PointNames.LEFT_FOOT : False
        }
    
        self.init_points_on_ground(player)
    
    def play_sounds(self, player):
        
        for point_name, on_ground in self.point_on_ground.iteritems():
            if player.model.points[point_name].pos[1] <= gamestate.stage.ground.position[1]:
                if not on_ground:
                    player.play_sound_indicator = True
                    self.point_on_ground[point_name] = True
            else:
                if on_ground:
                    self.point_on_ground[point_name] = False
    
    def init_points_on_ground(self, player):
        for point_name in self.point_on_ground.keys():
            if player.model.points[point_name].pos[1] <= gamestate.stage.ground.position[1]:
                self.point_on_ground[point_name] = True
            else:
                self.point_on_ground[point_name] = False

class AttackSoundMap(SoundMap):
    def __init__(self):
        SoundMap.__init__(self)
        
        self.hit_sound = None
        self.hit_sound_channel = None
    
    def reset(self):
        self.last_frame_index = 0
        self.frame_sound_index = 0
    
    def set_frame_sounds(self):
        """Defines sounds for each frame index of the attack"""
        
        self.frame_sounds.append(True)
        
        for frame_index in range(1, len(self.right_animation.frames) - 1):
            if self.attack_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.MEDIUM_PUNCH, InputActionTypes.STRONG_PUNCH]:
                self.frame_sounds.append(
                    self.test_delta_change(stick.PointNames.RIGHT_HAND, frame_index) or
                    self.test_delta_change(stick.PointNames.LEFT_HAND, frame_index)
                )
            else:
                self.frame_sounds.append(
                    self.test_delta_change(stick.PointNames.RIGHT_FOOT, frame_index) or
                    self.test_delta_change(stick.PointNames.LEFT_FOOT, frame_index)
                )
    
    def test_delta_change(self, point_name, frame_index):
        delta = self.right_animation.animation_deltas[frame_index][point_name]
        last_delta = self.right_animation.animation_deltas[frame_index - 1][point_name]
        
        if (mathfuncs.sign(delta[0]) != mathfuncs.sign(last_delta[0])): #or
        #mathfuncs.sign(delta[1]) != mathfuncs.sign(last_delta[1])):
            return True
        else:
            return False

class PlayerSoundMixer():
    def __init__(self, sound_library):
        
        self.play_sound_indicator = True
        self.sound_channel = None
        self.hit_sound_channel = None
    
    def play_sound(self, player_state):
        
        if not self.movement_sound_is_playing():
            if player_state == PlayerStates.ATTACKING:
                sound = choice(self.attack_sounds[self.get_attack_type()])
                self.start_sound(sound)
                
            elif player_state in self.movement_sounds.keys():
                sound = choice(self.movement_sounds[player_state])
                self.start_sound(sound)
    
    def start_sound(self, sound):
        if self.sound_channel == None:
            self.sound_channel = sound.play()
        else:
            self.sound_channel.stop()
            self.sound_channel = sound.play()
    
    def movement_sound_is_playing(self):
        if (self.sound_channel == None or
            self.sound_channel.get_busy() == False):
            return False
        else:
            return True
    
    def hit_sound_is_playing(self):
        if (self.hit_sound_channel == None or
            self.hit_sound_channel.get_busy() == False):
            return False
        else:
            return True
    
    def play_hit_sound(self):
        if self.get_attack_type() in self.hit_sounds.keys():
            self.hit_sound_channel = choice(self.hit_sounds[self.get_attack_type()]).play()
        else:
            self.hit_sound_channel =  pygame.mixer.Sound().play()

def handle_hit_sounds(attack_result):
    if attack_result.clash_indicator:
        clash_sound.play()
    else:
        attacker = attack_result.attacker
        receiver = attack_result.receiver
        
        if receiver.get_player_state() == player.PlayerStates.STUNNED:
            
            if not attacker.hit_sound_is_playing():
                attacker.play_hit_sound()
                
        else:
            
            attacker.play_hit_sound()
