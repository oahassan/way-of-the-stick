import os
import pygame
import settingsdata
import gamestate

wait_music_path = os.path.join("music","single_hit.wav")
versusmode_music_path = os.path.join("music","versusmode.wav")

current_game_mode = None

def init():
    pygame.mixer.music.load(wait_music_path)
    pygame.mixer.music.set_volume(settingsdata.get_music_volume())
    pygame.mixer.music.play(-1)

def set_volume(volume_level):
    pygame.mixer.music.set_volume(volume_level)

def update():
    global current_game_mode
    
    if (gamestate.mode == gamestate.Modes.VERSUSMODE and
    current_game_mode != gamestate.mode):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(versusmode_music_path)
        pygame.mixer.music.set_volume(settingsdata.get_music_volume())
        pygame.mixer.music.play(-1)
        current_game_mode = gamestate.mode
    
    elif (gamestate.mode != gamestate.Modes.VERSUSMODE and
    not current_game_mode is None):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(wait_music_path)
        pygame.mixer.music.set_volume(settingsdata.get_music_volume())
        pygame.mixer.music.play(-1)
        current_game_mode = None
