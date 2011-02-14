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
    AERIAL_ACTIONS = [InputActionTypes.JUMP, InputActionTypes.NO_MOVEMENT]
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
        InputActionTypes.MOVE_UP
    ]

class PlayerTypes:
    HUMAN = 'Human'
    BOT = 'Bot'
    REMOTE = 'Remote'

class AnimationModes():
    PHYSICS = "PHYSICS"
    KEYFRAME = "KEYFRAME"
    HYBRID = "HYBRID"

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
    
    MOVEMENTS = [STANDING,WALKING,RUNNING,JUMPING,FLOATING, \
                 LANDING,CROUCHING]
    
    UNBOUND_MOVEMENTS = [STANDING,FLOATING,LANDING,STUNNED, \
                        TRANSITION]
    
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
        TRANSITION : []
    }

class AttackTypes():
    PUNCH = "PUNCH"
    KICK = "KICK"
    
    ATTACK_TYPES = [PUNCH, KICK]

class Elevations():
    GROUNDED = "GROUNDED"
    AERIAL = "AERIAL"
