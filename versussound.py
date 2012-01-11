from random import choice
import pygame
import mathfuncs
import copy
import settingsdata
from enumerations import InputActionTypes, PlayerStates, PointNames
import time

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

class AttackSoundMap(SoundMap):
    def __init__(self, animation, attack_type):
        SoundMap.__init__(self)
        self.set_frame_sounds(animation, attack_type)
    
    def set_frame_sounds(self, animation, attack_type):
        """Defines sounds for each frame index of the attack"""
        
        self.frame_sounds.append(True)
        
        for frame_index in range(1, len(animation.frames)):
            if attack_type in [InputActionTypes.WEAK_PUNCH, InputActionTypes.MEDIUM_PUNCH, InputActionTypes.STRONG_PUNCH]:
                if (self.test_delta_change(animation, PointNames.RIGHT_HAND, frame_index) 
                or self.test_delta_change(animation, PointNames.LEFT_HAND, frame_index)):
                    self.frame_sounds.append(True)
                else:
                    self.frame_sounds.append(False)
            elif attack_type in [InputActionTypes.WEAK_KICK, InputActionTypes.MEDIUM_KICK, InputActionTypes.STRONG_KICK]:
                if (self.test_delta_change(animation, PointNames.RIGHT_FOOT, frame_index) 
                or self.test_delta_change(animation, PointNames.LEFT_FOOT, frame_index)):
                    self.frame_sounds.append(True)
                else:
                    self.frame_sounds.append(False)
            else:
                self.frame_sounds.append(False)
    
    def test_delta_change(self, animation, point_name, frame_index):
        delta = animation.animation_deltas[frame_index][point_name]
        last_delta = animation.animation_deltas[frame_index - 1][point_name]
        
        if (mathfuncs.sign(delta[0]) != mathfuncs.sign(last_delta[0])):
        #or mathfuncs.sign(delta[1]) != mathfuncs.sign(last_delta[1])):
            return True
        else:
            return False

class FootSoundMap(SoundMap):
    def __init__(self, animation):
        self.set_frame_sounds(animation)
    
    def set_frame_sounds(self, animation):
        frame_sounds = [False for i in range(len(animation.frames))]
        self.add_point_sounds_to_frame_sounds(
            animation,
            PointNames.LEFT_FOOT,
            frame_sounds
        )
        self.add_point_sounds_to_frame_sounds(
            animation,
            PointNames.RIGHT_FOOT,
            frame_sounds
        )
        
        self.frame_sounds = frame_sounds
    
    def add_point_sounds_to_frame_sounds(
        self, 
        animation, 
        point_name, 
        frame_sounds
    ):
        point_sounds = self.get_point_frame_sounds(
            animation, 
            point_name
        )
        self.merge_point_sounds_and_frame_sounds(point_sounds, frame_sounds)
    
    def merge_point_sounds_and_frame_sounds(self, point_sounds, frame_sounds):
        for i in range(len(point_sounds)):
            frame_sounds[i] = frame_sounds[i] or point_sounds[i]
    
    def get_point_frame_sounds(self, animation, point_name):
        point_y_positions = self.get_point_y_positions(animation, point_name)
        point_sounds = []
        
        for i in range(len(point_y_positions)):
            if i == 0:
                if len(point_y_positions) > 1:
                    if point_y_positions[i] > point_y_positions[i + 1]:
                        point_sounds.append(True)
                    else:
                        point_sounds.append(False)
                else:
                    point_sounds.append(False)
                
            elif i == (len(point_y_positions) - 1):
                if point_y_positions[i] > point_y_positions[i - 1]:
                    point_sounds.append(True)
                else:
                    point_sounds.append(False)
            else:
                if (point_y_positions[i] > point_y_positions[i - 1] 
                and point_y_positions[i] > point_y_positions[i + 1]):
                    point_sounds.append(True)
                else:
                    point_sounds.append(False)
        
        return point_sounds
    
    def get_point_y_positions(self, animation, point_name):
        point_id = animation.point_names[point_name]
        
        return [
            frame.point_dictionary[point_id].pos[1]
            for frame
            in animation.frames
        ]

class PlayerSoundMixer():
    def __init__(self, channel_id):
        
        self.play_sound_indicator = True
        self.jump_sound_channel = pygame.mixer.Channel(channel_id)
        self.attack_sound_channel = pygame.mixer.Channel(channel_id)
        self.foot_sound_channel = pygame.mixer.Channel(channel_id)
        self.sound_library = PlayerSoundLibrary()
    
    def play_sound(self, player_position, player_rendering_info):
        player_state = player_rendering_info.player_state
        attack_type = player_rendering_info.attack_type
        
        if player_state in PlayerStates.LATERAL_MOVEMENTS:
            self.start_sound(
                choice(self.sound_library.movement_sounds[player_state]),
                self.foot_sound_channel
            )
        elif player_state == PlayerStates.ATTACKING:
            self.start_sound(
                choice(self.sound_library.attack_sounds[attack_type]),
                self.attack_sound_channel
            )
        elif player_state == PlayerStates.JUMPING:
            jump_sound = self.sound_library.movement_sounds[PlayerStates.JUMPING][0]
            self.start_sound(jump_sound, self.jump_sound_channel)
    
    def start_sound(self, sound, sound_channel):
        if sound_channel == None:
            sound_channel = sound.play()
        else:
            sound_channel.stop()
            sound_channel.play(sound)
    
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
        self.start_time = 0
        self.hit_sound_channel = pygame.mixer.Channel(2)
        self.clash_sound_channel = pygame.mixer.Channel(2)
        self.last_hit_sound = None
    
    def hit_sound_is_playing(self, hit_sound):
        if self.last_hit_sound == None:
            return False
        else:
            return (time.clock() - self.start_time) < self.last_hit_sound.get_length()
    
    def play_hit_sound(self, sound_channel, hit_sound):
        self.last_hit_sound = hit_sound
        self.start_time = time.clock()
        
        if sound_channel == None:
            sound_channel = hit_sound.play()
        else:
            sound_channel.stop()
            sound_channel.play(hit_sound)
    
    def handle_hit_sounds(self, attack_result_rendering_info):
        if attack_result_rendering_info.clash_indicator:
            #pygame.mixer.find_channel(True).play(self.sound_library.clash_sound)
            self.play_hit_sound(self.clash_sound_channel, self.sound_library.clash_sound)
        else:
            hit_sound = self.get_hit_sound(attack_result_rendering_info)
            
            if not self.hit_sound_is_playing(hit_sound) and hit_sound != None:
                self.play_hit_sound(self.hit_sound_channel, hit_sound)
    
    def get_hit_sound(self, attack_result_rendering_info):
        attack_type = attack_result_rendering_info.attack_type
        
        if attack_type == None:
            return None
        
        hit_sound = self.sound_library.hit_sounds[attack_type][0]
        
        return hit_sound
