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
    FACING_RIGHT : 0
    FACING_LEFT : 1
    STANDING : 2
    WALKING : 3
    RUNNING : 4
    JUMPING : 5
    FLOATING : 6
    LANDING : 7
    ATTACKING : 8
    CROUCHING : 9
    STUNNED : 10
    BLOCKING : 11
    TRANSITION : 12
}
PLAYER_STATE_VALUES_REVERSE = dict([[v,k] for k,v in PLAYER_STATE_VALUES.iteritems()])

ATTACK_TYPE_VALUES = {
    WEAK_PUNCH : 1,
    MEDIUM_PUNCH : 2,
    STRONG_PUNCH : 3,
    WEAK_KICK : 4,
    MEDIUM_KICK : 5,
    STRONG_KICK : 6
}
ATTACK_TYPE_VALUES_REVERSE = dict([[v,k] for k,v in ATTACK_TYPE_VALUES.iteritems()])

def encode_point_positions(point_position_dictionary):
    encoded_positions = []
    
    for point_name in PointNames.POINT_NAMES:
        encoded_positions.extend(point_position_dictionary[point_name])
    
    return struct.pack('>dddddddddddddddddddddd', *encoded_positions)

def decode_point_positions(encoded_string):
    positions = struct.unpack('>dddddddddddddddddddddd', encoded_string)
    point_positions_dictionary = {}
    
    for i in range(len(PointNames.POINT_NAMES)):
        point_name = PointNames.POINT_NAMES[i]
        x_position = positions[i*2]
        y_position = positions[i*2+1]
        
        point_positions_dictionary[point_name] = (x_position, y_positions)
    
    return point_positions_dictionary

def encode_point_damages(point_damage_dictionary):
    encoded_damages = []
    
    for point_name in PointNames.POINT_NAMES:
        encoded_damages.extend(point_damage_dictionary[point_name])
    
    return struct.pack('>ddddddddddd', *encoded_damages)

def decode_point_damages(encoded_string):
    point_damages = struct.unpack('>ddddddddddd', encoded_string)
    
    return dict(zip(PointNames.POINT_NAMES, point_damages))

def encode_datatype(data_type):
    global DATATYPE_VALUES
    
    return struct.pack('>H', DATATYPE_VALUES[data_type])

def decode_datatype(encoded_string):
    global DATATYPE_VALUES_REVERSE
    
    return DATATYPE_VALUES_REVERSE[struct.unpack('>H', encoded_string)]

def encode_attack_line_names(line_names):
    global LINE_VALUES
    encoded_names = []
    
    for name in line_names:
        encoded_names.append(LINE_VALUES[name])
    
    return struct.pack('>HHHH', *encoded_names)

def decode_attack_line_names(encoded_string):
    global LINE_VALUES_REVERSE
    
    encoded_names = struct.unpack('>HHHH', encoded_string)
    
    return [LINE_VALES_REVERSE[name_code] for name_code in encoded_names]

def encode_player_state(player_state):
    global PLAYER_STATE_VALUES
    
    return struct.pack('>H', PLAYER_STATE_VALUES[player_state])

def decode_player_state(encoded_string):
    global PLAYER_STATE_VALUES_REVERSE
    
    return PLAYER_STATE_VALUES_REVERSE[struct.unpack('>H', encoded_string)]

def encode_health(player_health):
    return struct.pack('>H', player_health)

def decode_health(encoded_string):
    return struct.unpack('>H', encoded_string)

def encode_stun_timer(stun_timer):
    return struct.pack('>d', stun_timer)

def decode_stun_timer(encoded_string):
    return struct.unpack('>d', encoded_string)

def encode_sound_indicator(sound_indicator):
    return struct.pack('>?', sound_indicator)

def decode_sound_indicator(encoded_string):
    return struct.unpack('>?', encoded_string)

def encode_attack_sequence(attack_sequence):
    return struct.pack('>H', attack_sequence)

def decode_attack_sequence(encoded_string):
    return struct.unpack('>H', encoded_string)

def encode_attack_type(attack_type):
    global ATTACK_TYPE_VALUES
    
    return struct.pack('>H', ATTACK_TYPE_VALUES[attack_type])

def decode_attack_type(encoded_string):
    global ATTACK_TYPE_VALUES_REVERSE
    
    return ATTACK_TYPE_VALUES_REVERSE[struct.unpack('>H', encoded_string)]

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

def encode_player_state_dictioanry(player_state_dictionary):
    global ENCODING_FUNCS
    
    encoded_dictionary = {}
    
    for key, value in player_state_dictionary.iteritems():
        encoded_dictionary[encode_data_type(key)] = \
            ENCODING_FUNCS[key](value)
    
    return encoded_dictionary

def decode_player_state_dictionary(encoded_dictionary):
    global DECODING_FUNCS
    
    decoded_dictionary = {}
    
    for key, value in encoded_dictionary.iteritems():
        decoded_key = decode_data_type(key)
        
        decoded_dictionary[decoded_key] = \
            DECODING_FUNCS[decoded_key](value)
    
    return decoded_dictionary
