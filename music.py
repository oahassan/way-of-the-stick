import os
import pygame
import settingsdata
import gamestate

wait_music_path = os.path.join("music","single_hit.wav")

current_game_mode = None

def init():
    pygame.mixer.music.load(wait_music_path)
    pygame.mixer.music.set_volume(settingsdata.get_music_volume())
    pygame.mixer.music.play(-1)

def set_volume(volume_level):
    pygame.mixer.music.set_volume(volume_level)
