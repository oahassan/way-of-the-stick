import shelve

SETTINGS_DB_FILE_NM = "settings.dat"

class SETTING_NAMES:
    MUSIC_VOLUME = "music volume"
    SOUND_VOLUME = "sound volume"

def open_settings_shelf():
    actions = shelve.open(SETTINGS_DB_FILE_NM, "c")
    
    if ActionDictionaries.INPUT_ACTIONS not in actions:
        actions[ActionDictionaries.INPUT_ACTIONS] = {}
    
    if ActionDictionaries.UNBOUND_ACTIONS not in actions:
        actions[ActionDictionaries.UNBOUND_ACTIONS] = {}
    
    return actions

def save_sound_volume(volume):
    settings = shelve.open(SETTINGS_DB_FILE_NM, 'c')
    
    settings[SETTING_NAMES.SOUND_VOLUME] = volume
    
    settings.close()

def get_sound_volume():
    return_volume = 0
    
    settings = shelve.open(SETTINGS_DB_FILE_NM, 'c')
    
    return_volume = settings[SETTING_NAMES.SOUND_VOLUME]
    
    settings.close()
    
    return return_volume

def save_music_volume(volume):
    settings = shelve.open(SETTINGS_DB_FILE_NM, 'c')
    
    settings[SETTING_NAMES.MUSIC_VOLUME] = volume
    
    settings.close()

def get_music_volume():
    return_volume = 0
    
    settings = shelve.open(SETTINGS_DB_FILE_NM, 'c')
    
    return_volume = settings[SETTING_NAMES.MUSIC_VOLUME]
    
    settings.close()
    
    return return_volume
