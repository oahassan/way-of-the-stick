import pygame
import mathfuncs
import copy
import settingsdata
from enumerations import InputActionTypes, PlayerStates, PointNames

class SoundLibrary():
    def set_sound_volumes(self, sound_dict):
        for sound_list in sound_dict.values():
            for sound in sound_list:
                sound.set_volume(settingsdata.get_sound_volume())

class PlayerSoundLibrary(SoundLibrary):
    def __init__(self):
        
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

class SoundMap():
    def __init__(self):
        self.frame_sounds = []
        self.sound_channel = None
    
    def play_sound(self, frame_index):
        
        if not self.sound_is_playing():
            if self.frame_sounds[frame_index] != None:
                self.start_sound(self.frame_sounds[frame_index])
    
    def start_sound(self, sound):
        if self.sound_channel == None:
            self.sound_channel = sound.play()
        else:
            self.sound_channel.stop()
            self.sound_channel = sound.play()
    
    def sound_is_playing(self):
        if (self.sound_channel == None or
            self.sound_channel.get_busy() == False):
            return False
        else:
            return True

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
    def __init__(self, animation, attack_sound, attack_type):
        SoundMap.__init__(self)
        self.set_frame_sounds(animation, attack_sound, attack_type)
    
    def set_frame_sounds(self, animation, attack_sound, attack_type):
        """Defines sounds for each frame index of the attack"""
        
        self.frame_sounds.append(attack_sound)
        
        for frame_index in range(1, len(animation.frames)):
            if attack_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.MEDIUM_PUNCH, InputActionTypes.STRONG_PUNCH]:
                if (self.test_delta_change(animation, PointNames.RIGHT_HAND, frame_index) 
                or self.test_delta_change(animation, PointNames.LEFT_HAND, frame_index)):
                    self.frame_sounds.append(attack_sound)
                else:
                    self.frame_sounds.append(None)
            elif attack_type in [InputActionTypes.WEAK_KICK, InputActionTypes.MEDIUM_KICK, InputActionTypes.STRONG_KICK]:
                if (self.test_delta_change(animation, PointNames.RIGHT_FOOT, frame_index) 
                or self.test_delta_change(animation, PointNames.LEFT_FOOT, frame_index)):
                    self.frame_sounds.append(attack_sound)
                else:
                    self.frame_sounds.append(None)
            else:
                self.frame_sounds.append(None)
    
    def test_delta_change(self, animation, point_name, frame_index):
        delta = animation.animation_deltas[frame_index][point_name]
        last_delta = animation.animation_deltas[frame_index - 1][point_name]
        
        if (mathfuncs.sign(delta[0]) != mathfuncs.sign(last_delta[0])): #or
        #mathfuncs.sign(delta[1]) != mathfuncs.sign(last_delta[1])):
            return True
        else:
            return False
        

class PlayerSoundMixer():
    def __init__(self, player):
        
        self.play_sound_indicator = True
        self.sound_channel = None
        self.sound_library = PlayerSoundLibrary()
        self.sound_maps = {}
        self.create_sound_maps(player)
    
    def create_sound_maps(self, player):
        for action in player.get_attack_actions():
            
            self.sound_maps[action.right_animation.name] = AttackSoundMap(
                action.right_animation,
                self.sound_library.attack_sounds[action.attack_type][0],
                action.attack_type
            )
    
    def play_sound(self, player_state, animation_name, frame_index):
        
        if player_state == PlayerStates.ATTACKING:
            self.sound_maps[animation_name].play_sound(frame_index)
        
        #elif player_state in self.movement_sounds.keys():
        #    sound = choice(self.movement_sounds[player_state])
        #    self.start_sound(sound)
    
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

class AttackResultSoundLibrary(SoundLibrary):
    def __init__(self):
        
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
        
        self.clash_sound = pygame.mixer.Sound("./sounds/clash-sound.ogg")
        self.clash_sound.set_volume(settingsdata.get_sound_volume())

class AttackResultSoundMixer():
    def __init__(self):
        self.sound_library = AttackResultSoundLibrary()
        self.sound_channel = None
    
    def hit_sound_is_playing(self):
        if (self.sound_channel == None or
            self.sound_channel.get_busy() == False):
            return False
        else:
            return True
    
    def play_hit_sound(self, attack_type):
        if not self.hit_sound_is_playing():
            self.sound_channel = self.sound_library.hit_sounds[attack_type][0].play()
    
    def handle_hit_sounds(self, attack_result_rendering_info):
        if attack_result_rendering_info.clash_indicator:
            self.sound_channel = self.sound_library.clash_sound.play()
            
        elif not self.hit_sound_is_playing():
            self.play_hit_sound(attack_result_rendering_info.attack_type)
