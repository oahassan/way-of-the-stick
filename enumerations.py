# AI

class ApproachTypes:
    RUN = 0
    WALK = 1
    STAND = 2
    RUN_JUMP = 3
    WALK_JUMP = 4
    STAND_JUMP = 5
    
    APPROACH_TYPES = [RUN, WALK, STAND, RUN_JUMP, WALK_JUMP, STAND_JUMP]

class Difficulties:
    EASY = 1
    MEDIUM = 2
    HARD = 3
    CHALLENGE = 4

# networking
class ServerDiscovery:
    ADDRESS = 0
    NAME = 1

class PlayerDataKeys:
    MOVESET_NAME = 0
    COLOR = 1
    DIFFICULTY = 2
    PLAYER_TYPE = 3
    SIZE = 4
    PLAYER_POSITION = 5

class PlayerSelectActions:
    SET_MOVESET = "set_moveset"
    SET_COLOR = "set_color"
    SET_SIZE = "set_size"
    SET_DIFFICULTY = "set_difficulty"
    SET_PLAYER_TYPE = "set_player_type"
    GET_MOVESET = "get_moveset"
    GET_COLOR = "get_color"
    GET_SIZE = "get_size"
    GET_DIFFICULTY = "get_difficulty"
    GET_PLAYER_TYPE = "get_player_type"

class SimulationDataKeys:
    ACTION = 0
    KEYS_PRESSED = 1
    TIME_PASSED = 2
    MATCH_TIME = 3
    SIMULATION_STATE = 4
    PLAYER_STATE = 5
    RENDERING_INFO = 6
    PLAYER_POSITION = 7

class SimulationActionTypes:
    STEP = 0
    GET_STATE = 1
    UPDATE_STATE = 2
    STOP = 3
    GET_INPUT = 4
    UPDATE_INPUT = 5

# Controls

class CommandHandlerTypes:
    GROUND_MOVEMENT = "ground movement"
    AERIAL_MOVEMENT = "aerial movement"
    STUN_MOVEMENT = "stun movement"
    ATTACK = "attack"    
    
    COMMAND_HANDLER_TYPES = [
        GROUND_MOVEMENT,
        AERIAL_MOVEMENT,
        STUN_MOVEMENT,
        ATTACK
    ]

class CommandDurations:
    TAP = "tap"
    HOLD = "hold"

class InputActionTypes():
    NO_MOVEMENT = 'nomovement'
    MOVE_RIGHT = 'moveright'
    MOVE_LEFT = 'moveleft'
    MOVE_UP = 'moveup'
    MOVE_DOWN = 'movedown'
    BLOCK = 'block'
    WEAK_PUNCH = 'weakpunch'
    MEDIUM_PUNCH = 'mediumpunch'
    STRONG_PUNCH = 'strongpunch'
    WEAK_KICK = 'weakkick'
    MEDIUM_KICK = 'mediumkick'
    STRONG_KICK = 'strongkick'
    FORWARD = "forward"
    JUMP = "jump"
    
    INPUT_ACTION_TYPES = [
        NO_MOVEMENT, MOVE_RIGHT, MOVE_LEFT,
        MOVE_DOWN, MOVE_UP, FORWARD, JUMP,
        WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH,
        WEAK_KICK, MEDIUM_KICK, STRONG_KICK
    ]
    
    ATTACKS = [
        WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH,
        WEAK_KICK, MEDIUM_KICK, STRONG_KICK
    ]
    MOVEMENTS = [
        MOVE_RIGHT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, JUMP
    ]
    
    PUNCHES = [WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH]
    KICKS = [WEAK_KICK, MEDIUM_KICK, STRONG_KICK]
    
    QUICK_ATTACKS = [WEAK_PUNCH, WEAK_KICK]
    TRICKY_ATTACKS = [MEDIUM_PUNCH, MEDIUM_KICK]
    STRONG_ATTACKS = [STRONG_PUNCH, STRONG_KICK]
    
    ATTACK_TYPES = [QUICK_ATTACKS, TRICKY_ATTACKS, STRONG_ATTACKS]

class CommandCollections():
    GROUND_MOVEMENTS = [
        InputActionTypes.MOVE_RIGHT, InputActionTypes.MOVE_LEFT, 
        InputActionTypes.MOVE_DOWN, InputActionTypes.MOVE_UP, InputActionTypes.JUMP,
        InputActionTypes.NO_MOVEMENT
    ]
    AERIAL_MOVEMENTS = [
        InputActionTypes.MOVE_RIGHT, InputActionTypes.MOVE_LEFT, 
        InputActionTypes.MOVE_DOWN, InputActionTypes.MOVE_UP,
        InputActionTypes.NO_MOVEMENT
    ]
    
    STUN_MOVEMENTS = [
        InputActionTypes.MOVE_RIGHT, InputActionTypes.MOVE_LEFT, 
        InputActionTypes.MOVE_DOWN, InputActionTypes.MOVE_UP
    ]
    ATTACK_ACTIONS = [
        InputActionTypes.WEAK_PUNCH, InputActionTypes.MEDIUM_PUNCH, 
        InputActionTypes.STRONG_PUNCH, InputActionTypes.WEAK_KICK, 
        InputActionTypes.MEDIUM_KICK, InputActionTypes.STRONG_KICK,
        InputActionTypes.MOVE_RIGHT, InputActionTypes.MOVE_LEFT, 
        InputActionTypes.FORWARD, InputActionTypes.MOVE_DOWN,
        InputActionTypes.MOVE_UP, InputActionTypes.JUMP   
    ]
    AERIAL_ACTIONS = [InputActionTypes.JUMP, InputActionTypes.NO_MOVEMENT]
    AERIAL_ACTIONS.extend(ATTACK_ACTIONS)

class PlayerTypes:
    HUMAN = 'HUMAN'
    BOT = 'BOT'
    REMOTE = 'REMOTE'

class MatchStates:
    READY = 1
    FIGHT = 2
    PLAYER1_WINS = 3
    PLAYER2_WINS = 4
    NO_CONTEST = 5

class ClashResults:
    WIN = 'win'
    LOSS = 'loss'
    TIE = 'tie'
    NONE = 'None'

class AnimationModes():
    PHYSICS = "PHYSICS"
    KEYFRAME = "KEYFRAME"
    HYBRID = "HYBRID"

# rendering

class EffectTypes:
    LEFT_RUN_SMOKE = 0
    RIGHT_RUN_SMOKE = 1
    JUMP_SMOKE = 2
    FALL_SMOKE = 3

class LineLengths:
    HEAD = 35
    TORSO = 60
    UPPER_ARM = 40
    FOREARM = 40
    UPPER_LEG = 50
    LOWER_LEG = 50

# player state

class EventTypes():
    START = 0
    STOP = 1

class EventStates():
    STUN_GROUND = 0
    ATTACK_HIT = 1
    FOOT_SOUND = 2
    ATTACK_SOUND = 3
    COLLISION_START = 4

class PlayerStates():
    FACING_RIGHT = 'FACING_RIGHT'
    FACING_LEFT = 'FACING_LEFT'
    STANDING = 'STANDING'
    WALKING = 'WALKING'
    RUNNING = 'RUNNING'
    JUMPING = 'JUMPING'
    FLOATING = 'FLOATING'
    LANDING = 'LANDING'
    ATTACKING = 'ATTACKING'
    CROUCHING = 'CROUCHING'
    STUNNED = 'STUNNED'
    BLOCKING = 'BLOCKING'
    TRANSITION = 'TRANSITION'
    
    GROUND_STATES = [STANDING, CROUCHING, WALKING, RUNNING, LANDING]
    
    MOVEMENTS = [STANDING,WALKING,RUNNING,JUMPING,FLOATING, \
                 LANDING,CROUCHING]
    
    UNBOUND_MOVEMENTS = [STANDING,FLOATING,LANDING,STUNNED, \
                        TRANSITION]
    
    LATERAL_MOVEMENTS = [RUNNING, WALKING]
    
    PRESSED_KEY_STATE_TRANSITIONS = {
        STANDING : [WALKING,RUNNING,JUMPING,CROUCHING,ATTACKING],
        WALKING : [STANDING,JUMPING,CROUCHING,ATTACKING],
        RUNNING : [STANDING,JUMPING,CROUCHING,ATTACKING],
        CROUCHING : [STANDING,ATTACKING],
        JUMPING : [FLOATING,LANDING,ATTACKING],
        LANDING : [STANDING,CROUCHING,ATTACKING,JUMPING,WALKING],
        FLOATING : [LANDING,ATTACKING],
        ATTACKING : [],
        STUNNED : [],
        BLOCKING : [STANDING,CROUCHING],
        TRANSITION : [RUNNING]
    }

class AttackTypes():
    PUNCH = "PUNCH"
    KICK = "KICK"
    
    ATTACK_TYPES = [PUNCH, KICK]

class Elevations():
    GROUNDED = "GROUNDED"
    AERIAL = "AERIAL"

class PlayerPositions:
    NONE = "none"
    PLAYER1 = "player1"
    PLAYER2 = "player2"

# Stick Data

class PointNames:
    HEAD_TOP = "headtop"
    TORSO_TOP = "torsotop"
    TORSO_BOTTOM = "torobottom"
    LEFT_ELBOW = "leftelbow"
    LEFT_HAND = "lefthand"
    RIGHT_ELBOW = "rightelbow"
    RIGHT_HAND = "righthand"
    LEFT_KNEE = "leftknee"
    LEFT_FOOT = "leftfoot"
    RIGHT_KNEE = "rightknee"
    RIGHT_FOOT = "rightfoot"
    POINT_NAMES = [HEAD_TOP,TORSO_TOP,TORSO_BOTTOM,LEFT_ELBOW, \
                   LEFT_HAND,RIGHT_ELBOW,RIGHT_HAND,LEFT_KNEE, \
                   LEFT_FOOT,RIGHT_KNEE,RIGHT_FOOT]

class LineNames:
    HEAD = "head"
    LEFT_UPPER_ARM = "leftupperarm"
    LEFT_FOREARM = "leftforearm"
    RIGHT_UPPER_ARM = "rightupperarm"
    RIGHT_FOREARM = "rightforearm"
    TORSO = "torso"
    LEFT_UPPER_LEG = "leftupperleg"
    LEFT_LOWER_LEG = "leftlowerleg"
    RIGHT_UPPER_LEG = "rightupperleg"
    RIGHT_LOWER_LEG = "rightlowerleg"

LINE_TO_POINTS = dict([(LineNames.HEAD, [PointNames.HEAD_TOP,PointNames.TORSO_TOP]),
                       (LineNames.LEFT_UPPER_ARM, [PointNames.TORSO_TOP,PointNames.LEFT_ELBOW]),
                       (LineNames.LEFT_FOREARM, [PointNames.LEFT_ELBOW,PointNames.LEFT_HAND]),
                       (LineNames.RIGHT_UPPER_ARM, [PointNames.TORSO_TOP,PointNames.RIGHT_ELBOW]),
                       (LineNames.RIGHT_FOREARM, [PointNames.RIGHT_ELBOW,PointNames.RIGHT_HAND]),
                       (LineNames.TORSO, [PointNames.TORSO_TOP,PointNames.TORSO_BOTTOM]),
                       (LineNames.LEFT_UPPER_LEG, [PointNames.TORSO_BOTTOM,PointNames.LEFT_KNEE]),
                       (LineNames.LEFT_LOWER_LEG, [PointNames.LEFT_KNEE,PointNames.LEFT_FOOT]),
                       (LineNames.RIGHT_UPPER_LEG, [PointNames.TORSO_BOTTOM,PointNames.RIGHT_KNEE]),
                       (LineNames.RIGHT_LOWER_LEG, [PointNames.RIGHT_KNEE,PointNames.RIGHT_FOOT])])
