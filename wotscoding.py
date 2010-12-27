import struct
from stick import LineNames, PointNames
from player import PlayerStates
from controlsdata import InputActionTypes

class PlayerStateData:
    POINT_POSITIONS = "point positions"
    POINT_DAMAGES = "point damages"
    PLAYER_STATE = "player state"
    HEALTH = "health"
    ATTACK_SEQUENCE = "attack sequence"
    ATTACK_LINE_NAMES = "attack line names"
    ATTACK_TYPE = "attack type"
    STUN_TIMER = "stun timer"
    PLAY_SOUND = "play sound"

DATATYPE_VALUES = {
    PlayerStateData.POINT_POSITIONS : 0,
    PlayerStateData.POINT_DAMAGES : 1,
    PlayerStateData.PLAYER_STATE : 2,
    PlayerStateData.HEALTH : 3,
    PlayerStateData.ATTACK_SEQUENCE : 4,
    PlayerStateData.ATTACK_LINE_NAMES : 5,
    PlayerStateData.ATTACK_TYPE : 6,
    PlayerStateData.STUN_TIMER : 7,
    PlayerStateData.PLAY_SOUND : 8
}
DATATYPE_VALUES_REVERSE = dict([[v,k] for k,v in DATATYPE_VALUES.iteritems()])

DATATYPE_LENGTHS = {
    PlayerStateData.POINT_POSITIONS : 0,
    PlayerStateData.POINT_DAMAGES : 1,
    PlayerStateData.PLAYER_STATE : 2,
    PlayerStateData.HEALTH : 3,
    PlayerStateData.ATTACK_SEQUENCE : 4,
    PlayerStateData.ATTACK_LINE_NAMES : 5,
    PlayerStateData.ATTACK_TYPE : 6,
    PlayerStateData.STUN_TIMER : 7,
    PlayerStateData.PLAY_SOUND : 8
}

LINE_VALUES = {
    LineNames.HEAD : 1,
    LineNames.LEFT_UPPER_ARM : 2,
    LineNames.LEFT_FOREARM : 3,
    LineNames.RIGHT_UPPER_ARM : 4,
    LineNames.RIGHT_FOREARM : 5,
    LineNames.TORSO : 6,
    LineNames.LEFT_UPPER_LEG : 7,
    LineNames.LEFT_LOWER_LEG : 8,
    LineNames.RIGHT_UPPER_LEG : 9,
    LineNames.RIGHT_LOWER_LEG : 0
}
LINE_VALUES_REVERSE = dict([[v,k] for k,v in LINE_VALUES.iteritems()])

PLAYER_STATE_VALUES = {
    PlayerStates.FACING_RIGHT : 0,
    PlayerStates.FACING_LEFT : 1,
    PlayerStates.STANDING : 2,
    PlayerStates.WALKING : 3,
    PlayerStates.RUNNING : 4,
    PlayerStates.JUMPING : 5,
    PlayerStates.FLOATING : 6,
    PlayerStates.LANDING : 7,
    PlayerStates.ATTACKING : 8,
    PlayerStates.CROUCHING : 9,
    PlayerStates.STUNNED : 10,
    PlayerStates.BLOCKING : 11,
    PlayerStates.TRANSITION : 12
}
PLAYER_STATE_VALUES_REVERSE = dict([[v,k] for k,v in PLAYER_STATE_VALUES.iteritems()])

ATTACK_TYPE_VALUES = {
    InputActionTypes.WEAK_PUNCH : 1,
    InputActionTypes.MEDIUM_PUNCH : 2,
    InputActionTypes.STRONG_PUNCH : 3,
    InputActionTypes.WEAK_KICK : 4,
    InputActionTypes.MEDIUM_KICK : 5,
    InputActionTypes.STRONG_KICK : 6
}
ATTACK_TYPE_VALUES_REVERSE = dict([[v,k] for k,v in ATTACK_TYPE_VALUES.iteritems()])

def encode_point_positions(point_position_dictionary):
    encoded_positions = []
    
    for point_name in PointNames.POINT_NAMES:
        encoded_positions.extend(point_position_dictionary[point_name])
    
    #return struct.pack('>dddddddddddddddddddddd', *encoded_positions)
    return encoded_positions

def decode_point_positions(encoded_string):
    positions = encoded_string #struct.unpack('>dddddddddddddddddddddd', encoded_string)
    point_positions_dictionary = {}
    
    for i in range(len(PointNames.POINT_NAMES)):
        point_name = PointNames.POINT_NAMES[i]
        x_position = positions[i*2]
        y_position = positions[i*2+1]
        
        point_positions_dictionary[point_name] = (x_position, y_position)
    
    return point_positions_dictionary

def encode_point_damages(point_damage_dictionary):
    encoded_damages = []
    
    for point_name in PointNames.POINT_NAMES:
        encoded_damages.append(point_damage_dictionary[point_name])
    
    #return struct.pack('>ddddddddddd', *encoded_damages)
    return encoded_damages

def decode_point_damages(encoded_string):
    point_damages = encoded_string #struct.unpack('>ddddddddddd', encoded_string)
    
    return dict(zip(PointNames.POINT_NAMES, point_damages))

def encode_datatype(data_type):
    global DATATYPE_VALUES
    
    #return struct.pack('>H', DATATYPE_VALUES[data_type])
    return DATATYPE_VALUES[data_type]

def decode_datatype(encoded_string):
    global DATATYPE_VALUES_REVERSE
    
    #return DATATYPE_VALUES_REVERSE[struct.unpack('>H', encoded_string)[0]]
    return DATATYPE_VALUES_REVERSE[encoded_string]

def encode_attack_line_names(line_names):
    global LINE_VALUES
    encoded_names = []
    
    for name in line_names:
        encoded_names.append(LINE_VALUES[name])
    
    #return struct.pack('>HHHH', *encoded_names)
    return encoded_names

def decode_attack_line_names(encoded_string):
    global LINE_VALUES_REVERSE
    
    encoded_names = encoded_string #struct.unpack('>HHHH', encoded_string)
    
    return [LINE_VALUES_REVERSE[name_code] for name_code in encoded_names]

def encode_player_state(player_state):
    global PLAYER_STATE_VALUES
    
    #return struct.pack('>H', PLAYER_STATE_VALUES[player_state])
    return PLAYER_STATE_VALUES[player_state]

def decode_player_state(encoded_string):
    global PLAYER_STATE_VALUES_REVERSE
    
    #return PLAYER_STATE_VALUES_REVERSE[struct.unpack('>H', encoded_string)[0]]
    return PLAYER_STATE_VALUES_REVERSE[encoded_string]

def encode_health(player_health):
    #return struct.pack('>H', player_health)
    return player_health

def decode_health(encoded_string):
    #return struct.unpack('>H', encoded_string)[0]
    return encoded_string

def encode_stun_timer(stun_timer):
    #return struct.pack('>d', stun_timer)
    return stun_timer

def decode_stun_timer(encoded_string):
    #return struct.unpack('>d', encoded_string)[0]
    return encoded_string

def encode_sound_indicator(sound_indicator):
    #return struct.pack('>?', sound_indicator)
    return sound_indicator

def decode_sound_indicator(encoded_string):
    #return struct.unpack('>?', encoded_string)[0]
    return encoded_string

def encode_attack_sequence(attack_sequence):
    #return struct.pack('>H', attack_sequence)
    return attack_sequence

def decode_attack_sequence(encoded_string):
    #return struct.unpack('>H', encoded_string)[0]
    return encoded_string

def encode_attack_type(attack_type):
    global ATTACK_TYPE_VALUES
    
    #return struct.pack('>H', ATTACK_TYPE_VALUES[attack_type])
    return ATTACK_TYPE_VALUES[attack_type]

def decode_attack_type(encoded_string):
    global ATTACK_TYPE_VALUES_REVERSE
    
    #return ATTACK_TYPE_VALUES_REVERSE[struct.unpack('>H', encoded_string)[0]]
    return ATTACK_TYPE_VALUES_REVERSE[encoded_string]

ENCODING_FUNCS = {
    PlayerStateData.POINT_POSITIONS : encode_point_positions,
    PlayerStateData.POINT_DAMAGES : encode_point_damages,
    PlayerStateData.PLAYER_STATE : encode_player_state,
    PlayerStateData.HEALTH : encode_health,
    PlayerStateData.ATTACK_SEQUENCE : encode_attack_sequence,
    PlayerStateData.ATTACK_LINE_NAMES : encode_attack_line_names,
    PlayerStateData.ATTACK_TYPE : encode_attack_type,
    PlayerStateData.STUN_TIMER : encode_stun_timer,
    PlayerStateData.PLAY_SOUND : encode_sound_indicator
}

DECODING_FUNCS = {
    PlayerStateData.POINT_POSITIONS : decode_point_positions,
    PlayerStateData.POINT_DAMAGES : decode_point_damages,
    PlayerStateData.PLAYER_STATE : decode_player_state,
    PlayerStateData.HEALTH : decode_health,
    PlayerStateData.ATTACK_SEQUENCE : decode_attack_sequence,
    PlayerStateData.ATTACK_LINE_NAMES : decode_attack_line_names,
    PlayerStateData.ATTACK_TYPE : decode_attack_type,
    PlayerStateData.STUN_TIMER : decode_stun_timer,
    PlayerStateData.PLAY_SOUND : decode_sound_indicator
}

def encode_player_state_dictionary(player_state_dictionary):
    global ENCODING_FUNCS
    
    encoded_dictionary = {}
    
    for key, value in player_state_dictionary.iteritems():
        encoded_dictionary[encode_datatype(key)] = \
            ENCODING_FUNCS[key](value)
    
    return encoded_dictionary

def decode_player_state_dictionary(encoded_dictionary):
    global DECODING_FUNCS
    
    decoded_dictionary = {}
    
    for key, value in encoded_dictionary.iteritems():
        decoded_key = decode_datatype(key)
        
        decoded_dictionary[decoded_key] = \
            DECODING_FUNCS[decoded_key](value)
    
    return decoded_dictionary
