class InputActionTypes():
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
    
    AERIAL_MOVEMENTS = [MOVE_RIGHT, MOVE_LEFT, MOVE_DOWN]
    STUN_MOVEMENTS = [MOVE_RIGHT, MOVE_LEFT, MOVE_DOWN, MOVE_UP]
    
    ATTACKS = [
        WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH,
        WEAK_KICK, MEDIUM_KICK, STRONG_KICK
    ]
    
    PUNCHES = [WEAK_PUNCH, MEDIUM_PUNCH, STRONG_PUNCH]
    KICKS = [WEAK_KICK, MEDIUM_KICK, STRONG_KICK]

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
        WALKING : [WALKING,STANDING,JUMPING,CROUCHING,ATTACKING],
        RUNNING : [RUNNING,STANDING,JUMPING,CROUCHING,ATTACKING],
        CROUCHING : [STANDING,ATTACKING],
        JUMPING : [FLOATING,LANDING,ATTACKING],
        LANDING : [STANDING,CROUCHING,ATTACKING,JUMPING,WALKING],
        FLOATING : [LANDING,ATTACKING],
        ATTACKING : [STANDING, FLOATING],
        STUNNED : [FLOATING,LANDING,STANDING],
        BLOCKING : [STANDING,CROUCHING],
        TRANSITION : [RUNNING]
    }

class AttackTypes():
    PUNCH = "PUNCH"
    KICK = "KICK"
    
    ATTACK_TYPES = [PUNCH, KICK]
