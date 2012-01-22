import os
import pygame
import settingsdata
import gamestate

wait_music_path = os.path.join("music","single_hit.wav")
versusmode_music_path = os.path.join("music","versusmode.wav")
versusmovesetselect_music_path = os.path.join("music","446457_Logical_Defiance___Mist_of.mp3")
current_game_mode = None
current_song_path = ""

def init():
    pygame.mixer.music.load(wait_music_path)
    pygame.mixer.music.set_volume(settingsdata.get_music_volume())
    pygame.mixer.music.play(-1)
    current_game_mode = gamestate.mode
    current_song_path = wait_music_path

def set_volume(volume_level):
    pygame.mixer.music.set_volume(volume_level)

def update():
    global current_game_mode
    global current_song_path
    
    if (current_game_mode != gamestate.mode):
        new_music_path = get_music_path()
        
        if new_music_path != current_song_path:
            pygame.mixer.music.fadeout(1000)
            pygame.mixer.music.load(new_music_path)
            pygame.mixer.music.set_volume(settingsdata.get_music_volume())
            pygame.mixer.music.play(-1)
            current_song_path = new_music_path
        
        current_game_mode = gamestate.mode

def get_music_path():
    if (gamestate.mode == gamestate.Modes.VERSUSMOVESETSELECT or 
    gamestate.mode == gamestate.Modes.STAGESELECT):
        return versusmovesetselect_music_path
    elif gamestate.mode == gamestate.Modes.VERSUSMODE:
        return gamestate.stage.music
    else:
        return wait_music_path
