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
        self.start_time = 0
    
    def play_sound(self, frame_index):
        sound = self.frame_sounds[frame_index]
        
        if sound != None and not self.sound_is_playing(sound):
            
            self.start_sound(sound)
    
    def start_sound(self, sound):
        
        self.start_time = time.clock()
        pygame.mixer.find_channel(True).play(sound)
    
    def sound_is_playing(self, sound):
        
        return (time.clock() - self.start_time) < sound.get_length()

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
        
        if (mathfuncs.sign(delta[0]) != mathfuncs.sign(last_delta[0])):
        #or mathfuncs.sign(delta[1]) != mathfuncs.sign(last_delta[1])):
            return True
        else:
            return False

class FootSoundMap(SoundMap):
    def __init__(self, animation, foot_sounds):
        self.set_frame_sounds(animation, foot_sounds)
    
    def play_sound(self, frame_index):
        for sound in self.frame_sounds[frame_index]:
            
            self.start_sound(sound)
    
    def set_frame_sounds(self, animation, foot_sounds):
        frame_sounds = [[] for i in range(len(animation.frames))]
        self.add_point_sounds_to_frame_sounds(
            animation,
            PointNames.LEFT_FOOT,
            foot_sounds,
            frame_sounds
        )
        self.add_point_sounds_to_frame_sounds(
            animation,
            PointNames.RIGHT_FOOT,
            foot_sounds,
            frame_sounds
        )
        
        self.frame_sounds = frame_sounds
    
    def add_point_sounds_to_frame_sounds(
        self, 
        animation, 
        point_name, 
        foot_sounds,
        frame_sounds
    ):
        point_sounds = self.get_point_frame_sounds(
            animation, 
            foot_sounds, 
            point_name
        )
        self.merge_point_sounds_and_frame_sounds(point_sounds, frame_sounds)
    
    def merge_point_sounds_and_frame_sounds(self, point_sounds, frame_sounds):
        for i in range(len(point_sounds)):
            frame_sounds[i].extend(point_sounds[i])
    
    def get_point_frame_sounds(self, animation, foot_sounds, point_name):
        point_y_positions = self.get_point_y_positions(animation, point_name)
        point_sounds = []
        
        for i in range(len(point_y_positions)):
            if i == 0:
                if len(point_y_positions) > 1:
                    if point_y_positions[i] > point_y_positions[i + 1]:
                        point_sounds.append([choice(foot_sounds)])
                    else:
                        point_sounds.append([])
                else:
                    point_sounds.append([])
                
            elif i == (len(point_y_positions) - 1):
                if point_y_positions[i] > point_y_positions[i - 1]:
                    point_sounds.append([choice(foot_sounds)])
                else:
                    point_sounds.append([])
            else:
                if (point_y_positions[i] > point_y_positions[i - 1] 
                and point_y_positions[i] > point_y_positions[i + 1]):
                    point_sounds.append([choice(foot_sounds)])
                else:
                    point_sounds.append([])
        
        return point_sounds
    
    def get_point_y_positions(self, animation, point_name):
        point_id = animation.point_names[point_name]
        
        return [
            frame.point_dictionary[point_id].pos[1]
            for frame
            in animation.frames
        ]

class PlayerSoundMixer():
    def __init__(self, player):
        
        self.play_sound_indicator = True
        self.sound_channel = None
        self.sound_library = PlayerSoundLibrary()
        self.sound_maps = {}
        self.create_sound_maps(player)
        self.last_player_state = PlayerStates.STANDING
    
    def create_sound_maps(self, player):
        for action in player.get_attack_actions():
            
            self.sound_maps[action.right_animation.name] = AttackSoundMap(
                action.right_animation,
                self.sound_library.attack_sounds[action.attack_type][0],
                action.attack_type
            )
        
        for action in player.get_foot_actions():
            
            self.sound_maps[action.right_animation.name] = FootSoundMap(
                action.right_animation,
                self.sound_library.movement_sounds[PlayerStates.WALKING]
            )
    
    def play_sound(self, player_state, animation_name, frame_index):
        
        if (player_state 
        in [PlayerStates.WALKING, PlayerStates.RUNNING, PlayerStates.ATTACKING]):
            self.sound_maps[animation_name].play_sound(frame_index)
        elif player_state == PlayerStates.JUMPING:
            if self.last_player_state != PlayerStates.JUMPING:
                jump_sound = self.sound_library.movement_sounds[PlayerStates.JUMPING][0]
                pygame.mixer.find_channel().play(jump_sound)
        #elif player_state in self.movement_sounds.keys():
        #    sound = choice(self.movement_sounds[player_state])
        #    self.start_sound(sound)
        
        self.last_player_state = player_state
    
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
        self.start_time = 0
    
    def hit_sound_is_playing(self, hit_sound):
        return (time.clock() - self.start_time) < hit_sound.get_length()
    
    def play_hit_sound(self, hit_sound):
        
        self.start_time = time.clock()
        pygame.mixer.find_channel(True).play(hit_sound)
    
    def handle_hit_sounds(self, attack_result_rendering_info):
        if attack_result_rendering_info.clash_indicator:
            pygame.mixer.find_channel(True).play(self.sound_library.clash_sound)
            
        else:
            hit_sound = self.get_hit_sound(attack_result_rendering_info)
            
            if not self.hit_sound_is_playing(hit_sound) and hit_sound != None:
                self.play_hit_sound(hit_sound)
    
    def get_hit_sound(self, attack_result_rendering_info):
        attack_type = attack_result_rendering_info.attack_type
        
        if attack_type == None:
            return None
        
        hit_sound = self.sound_library.hit_sounds[attack_type][0]
        
        return hit_sound
