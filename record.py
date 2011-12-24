import os
from datetime import datetime
from glob import glob

from files import _WOTS_DIR, removeDisallowedFilenameChars
from wotsprot.rencode import dumps, loads

RECORD_TYPE = ".rec"
RECORD_DIR = os.path.join(_WOTS_DIR,"Recordings")

if not os.path.exists(RECORD_DIR):
    os.makedirs(RECORD_DIR)
    
class Recording():
    def __init__(
        self,
        timestep,
        moveset1_name,
        moveset2_name,
        file_name=None,
        simulation_snapshots = None
    ):
        self.timestep = timestep
        self.moveset1_name = moveset1_name
        self.moveset2_name = moveset2_name
        self.simulation_snapshots = simulation_snapshots
        
        if simulation_snapshots == None:
            self.simulation_snapshots = []
        
        
        self.file_name = file_name
        
        if file_name == None:
            self.file_name = moveset1_name + "vs" + moveset2_name + str(datetime.now()) + RECORD_TYPE
    
    def _pack(self):
        return (self.timestep, self.moveset1_name, self.moveset2_name, self.file_name,
         self.simulation_snapshots)

def save(recording):
    
    file_path = os.path.join(RECORD_DIR, removeDisallowedFilenameChars(recording.file_name))
    record_data = dumps(recording)
    
    with open(file_path,'wb') as f:
        f.write(record_data)

def load_recording_list():
    return [
        recording_path 
        for recording_path in glob(os.path.join(RECORD_DIR, "*" + RECORD_TYPE))
    ]

def load(recording_path):
    recording = None
    
    with open(recording_path, 'rb') as f:
        recording = loads(f.read())
    
    return recording
