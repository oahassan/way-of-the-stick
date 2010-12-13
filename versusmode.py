import pygame
from wotsfx import Effect
import wotsuievents
import gamestate
import player
import humanplayer
import aiplayer
import button
import stage
import stick
import mathfuncs
import math

class PlayerTypes:
    HUMAN = 'HUMAN'
    BOT = 'BOT'

class MatchStates:
    READY = 'ready'
    FIGHT = 'fight'
    END = 'end'

gamestate.stage = stage.ScrollableStage(447, 0, gamestate._WIDTH)

initialized = False
human = None
bot = None
fight_label = None
ready_label = None
human_wins_label = None
bot_wins_label = None
match_state = None
exit_button = button.ExitButton()
exit_indicator = False
versus_mode_start_time = None
fight_start_time = None
fight_end_time = None
fight_end_timer = None
versus_mode_start_timer = None
fight_start_timer = None
fps_label = None
player_type = None
bot_type = None
point_effects = {}

stun_channel = None
hit_sound = pygame.mixer.Sound("./sounds/hit-sound.ogg")
clash_sound = pygame.mixer.Sound("./sounds/clash-sound.ogg")

def init():
    global initialized
    global players
    global human
    global bot
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global match_state
    global fight_end_timer
    global versus_mode_start_timer
    global fight_start_timer
    global fps_label
    global player_type
    global bot_type
    global point_effects
    
    point_effects = {}
    fps_label = button.Label((20,20), str(gamestate.clock.get_fps()),(0,0,0),30)
    match_state = MatchStates.READY
    fight_end_timer = 0
    versus_mode_start_timer = 0
    fight_start_timer = 0
    
    ready_label = button.Label((0,0),'READY...',(0,0,0),100)
    ready_label_position = ((gamestate._WIDTH / 2) - (ready_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (ready_label.height / 2))
    ready_label.set_position(ready_label_position)
    
    fight_label = button.Label((0,0),'FIGHT!',(0,0,0),100)
    fight_label_position = ((gamestate._WIDTH / 2) - (fight_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (fight_label.height / 2))
    fight_label.set_position(fight_label_position)
    
    human_wins_label = button.Label((0,0),'YOU WIN!',(0,0,0),100)
    human_wins_label_position = ((gamestate._WIDTH / 2) - (human_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (human_wins_label.height / 2))
    human_wins_label.set_position(human_wins_label_position)
    
    bot_wins_label = button.Label((0,0),'BOT WINS!',(0,0,0),100)
    bot_wins_label_position = ((gamestate._WIDTH / 2) - (bot_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (bot_wins_label.height / 2))
    bot_wins_label.set_position(bot_wins_label_position)
    
    if player_type == PlayerTypes.BOT:
        new_player = aiplayer.Bot((0, 0))
    else:
        new_player = humanplayer.HumanPlayer((0, 0))
    
    
    if bot_type == PlayerTypes.HUMAN:
        second_player = humanplayer.HumanPlayer((0, 0))
    else:
        second_player = aiplayer.Bot((0, 0))
    
    
    human = new_player
    human.init_state()
    human.model.move_model((200, 367))
    
    bot = second_player
    bot.init_state()
    bot.model.move_model((500, 367))
    bot.color = (0,255,0)
    
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
    initialized = True
    
    gamestate.frame_rate = 60
    gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS
    
    gamestate.screen.blit(gamestate.stage.background_image, (0,0))
    gamestate.new_dirty_rects.append(pygame.Rect((0,0),(gamestate._WIDTH, gamestate._HEIGHT)))

def exit():
    global initialized
    global players
    global human
    global bot
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global match_state
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    global point_effects
    
    point_effects = {}
    ready_label = None
    fight_label = None
    human_wins_label = None
    bot_wins_label = None
    match_state = None
    versus_mode_start_timer = None
    fight_start_timer = None
    fight_end_timer = None
    human = None
    bot = None
    players = []
    initialized = False
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.NONE
    gamestate.drawing_mode = gamestate.DrawingModes.UPDATE_ALL
    gamestate.frame_rate = 20
    
def handle_events():
    global exit_button
    global exit_indicator
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global match_state
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    global fps_label
    global effects
    
    exit_button.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect(exit_button.position, (exit_button.width,exit_button.height)))
    
    fps_label.set_text(str(gamestate.clock.get_fps()))
    fps_label.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect(fps_label.position,(fps_label.width,fps_label.height)))
    
    if versus_mode_start_timer < 3000:
        ready_label.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(pygame.Rect(ready_label.position,(ready_label.width,ready_label.height)))
        
        versus_mode_start_timer += gamestate.clock.get_time()
    else:
        fight_start_timer += gamestate.clock.get_time()
        match_state = MatchStates.FIGHT
        
        if fight_start_timer < 1000:
            fight_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(fight_label.position,(fight_label.width,fight_label.height)))
    
    if bot.health_meter == 0:
        match_state = MatchStates.END
        
        if fight_end_timer < 8000:
            fight_end_timer += gamestate.clock.get_time()
            human_wins_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(human_wins_label.position, \
                                             (human_wins_label.width, \
                                              human_wins_label.height)))
            
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()
    elif human.health_meter == 0:
        match_state = MatchStates.END
        
        if fight_end_timer < 8000:
            fight_end_timer += gamestate.clock.get_time()
            bot_wins_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(bot_wins_label.position, \
                                             (bot_wins_label.width, \
                                              bot_wins_label.height)))
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()
    
    if ((exit_indicator == False) and 
    ((match_state == MatchStates.FIGHT) or (match_state == MatchStates.END))):
        if player_type == PlayerTypes.HUMAN:
            human.handle_events()
        else:
            human.handle_events(bot)
        
        if bot_type == PlayerTypes.BOT:
            bot.handle_events(human)
        else:
            bot.handle_events()
        
        handle_interactions()
        
        gamestate.stage.scroll_background([human.model, bot.model])
        gamestate.stage.draw(gamestate.screen)
        player.draw_model(human, gamestate.screen)
        player.draw_reflection(human, gamestate.screen)
        player.draw_model(bot, gamestate.screen)
        player.draw_reflection(bot, gamestate.screen)
        
    if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
        if exit_button.contains(wotsuievents.mouse_pos):
            exit_indicator = True
            exit_button.color = button.Button._SlctdColor
            exit_button.symbol.color = button.Button._SlctdColor
    elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
        if exit_indicator == True:
            exit_indicator = False
            exit_button.color = button.Button._InactiveColor
            exit_button.symbol.color = button.Button._InactiveColor
            
            if exit_button.contains(wotsuievents.mouse_pos):
                gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
                exit()

def handle_interactions():
    global human
    global bot
    
    if bot.get_player_state() == player.PlayerStates.ATTACKING:
        handle_attacks(bot, human)
    elif human.get_player_state() == player.PlayerStates.ATTACKING:
        handle_attacks(human, bot)

def get_player(input_player):
    global human
    
    return_name = 'bot'
    
    if input_player == human:
        return_name = 'human'
    
    return return_name

def handle_attacks(attacker, receiver):
    if test_overlap(attacker.get_enclosing_rect(), receiver.get_enclosing_rect()):
        attacker_attack_hitboxes = get_hitbox_dictionary(attacker.get_attack_lines())
        
        if receiver.get_player_state() == player.PlayerStates.ATTACKING:
            receiver_attack_hitboxes = get_hitbox_dictionary(receiver.get_attack_lines())
            colliding_line_names = test_attack_collision(attacker_attack_hitboxes, receiver_attack_hitboxes)
            
            if colliding_line_names:
                # draw_attacker_hitboxes(attacker_attack_hitboxes)
                # draw_attacker_hitboxes(receiver_attack_hitboxes)
                
                handle_blocked_attack_collision(attacker, receiver,attacker_attack_hitboxes, receiver_attack_hitboxes)
            else:
                attacker_hitboxes = get_hitbox_dictionary(attacker.model.lines)
                colliding_line_names = test_attack_collision(receiver_attack_hitboxes, attacker_hitboxes)
                
                if colliding_line_names:
                    # print('block1, attacker:' + get_player(receiver))
                    # print('receiver line name: ' + colliding_line_names[0])
                    # print('attacker line name: ' + colliding_line_names[1])
                    colliding_lines = (receiver.model.lines[colliding_line_names[0]], \
                                       attacker.model.lines[colliding_line_names[1]])
                    # draw_attacker_hitboxes(receiver_attack_hitboxes)
                    # draw_receiver_hitboxes(attacker_hitboxes)
                    
                    handle_unblocked_attack_collision(receiver, attacker, receiver_attack_hitboxes, attacker_hitboxes)
                else:
                    receiver_hitboxes = get_hitbox_dictionary(receiver.model.lines)
                    colliding_line_names = test_attack_collision(attacker_attack_hitboxes, receiver_hitboxes)
                    
                    if colliding_line_names:
                        # print('block2, attacker:' + get_player(attacker))
                        # print('receiver_line_name: ' + colliding_line_names[1])
                        # print('attacker_line_name: ' + colliding_line_names[0])
                        colliding_lines = (attacker.model.lines[colliding_line_names[0]], \
                                           receiver.model.lines[colliding_line_names[1]])
                        # draw_attacker_hitboxes(attacker_attack_hitboxes)
                        # draw_receiver_hitboxes(receiver_hitboxes)
                        
                        handle_unblocked_attack_collision(attacker, receiver, attacker_attack_hitboxes, receiver_hitboxes)
        else:
            receiver_hitboxes = get_hitbox_dictionary(receiver.model.lines)
            colliding_line_names = test_attack_collision(attacker_attack_hitboxes, receiver_hitboxes)
            
            if colliding_line_names:
                # print('block3, attacker:' + get_player(receiver))
                # print('receiver_line_name: ' + colliding_line_names[1])
                # print('attacker_line_name: ' + colliding_line_names[0])
                colliding_lines = (attacker.model.lines[colliding_line_names[0]], \
                                   receiver.model.lines[colliding_line_names[1]])
                # draw_attacker_hitboxes(attacker_attack_hitboxes)
                # draw_receiver_hitboxes(receiver_hitboxes)
                
                handle_unblocked_attack_collision(attacker, receiver, attacker_attack_hitboxes, receiver_hitboxes)
    
    for effect in point_effects.values():
        effect.update(gamestate.time_passed)
        gamestate.new_dirty_rects.append(pygame.Rect(effect.get_enclosing_rect()))
        effect.draw_ellipse_effect(gamestate.screen)
    
    dead_effects = []
    
    for point_id, effect in point_effects.iteritems():
        if effect.effect_over():
            dead_effects.append(point_id)
    
    for point_id in dead_effects:
        del point_effects[point_id]

def draw_attacker_hitboxes(hitbox_dictionary):
    for name, hitboxes in hitbox_dictionary.iteritems():
        for hitbox in hitboxes:
            pygame.draw.rect(gamestate.screen, (255,0,0), hitbox, 1)

def draw_receiver_hitboxes(hitbox_dictionary):
    for name, hitboxes in hitbox_dictionary.iteritems():
        for hitbox in hitboxes:
            pygame.draw.rect(gamestate.screen, (0,0,255), hitbox, 1)

def handle_unblocked_attack_collision(
    attacker,
    receiver,
    attacker_hitboxes,
    receiver_hitboxes
):
    global stun_channel
    global point_effects
    
    colliding_line_names = test_attack_collision(attacker_hitboxes, receiver_hitboxes)
    
    colliding_lines = (attacker.model.lines[colliding_line_names[0]], \
                       receiver.model.lines[colliding_line_names[1]])
    
    interaction_points = get_interaction_points(receiver, colliding_lines)
    damage = attacker.get_point_damage(interaction_points[0].name)
    
    attack_knockback_vector = attacker.get_point_position_change(interaction_points[0].name)
    effect_height = max(50, damage)
    effect_width = max(50, .2 * damage)
    fade_rate =  1 / (effect_height / effect_width)
    
    angle_in_degrees = 0
    
    if attack_knockback_vector[0] == 0:
        if mathfuncs.sign(attack_knockback_vector[1]) == 1:
            angle_in_degrees = 0
        else:
            angle_in_degrees = 180
            
    elif attack_knockback_vector[1] == 0:
        if mathfuncs.sign(attack_knockback_vector[0]) == 1:
            angle_in_degrees = 90
        else:
            angle_in_degrees = 270
        
    else:
        angle_in_degrees = math.degrees(
            math.asin(attack_knockback_vector[1] / math.hypot(
                attack_knockback_vector[0], attack_knockback_vector[1]
            ))
        )
    
    if receiver.get_player_state() == player.PlayerStates.STUNNED:
        
        stun_knockback_vector = receiver.knockback_vector
        
        if attacker_is_recoiling(attack_knockback_vector, stun_knockback_vector) and receiver.health_meter > 0:
            pass
        else:
            apply_collision_physics(
                attacker,
                receiver,
                attacker_hitboxes,
                receiver_hitboxes
            )
            receiver.health_meter = max(0, receiver.health_meter - damage)
            receiver.set_stun_timeout(attacker.get_stun_timeout())
            
            if receiver.health_meter == 0:
                receiver.set_stun_timeout(9000)
            
            if not attacker.hit_sound_is_playing():
                attacker.play_hit_sound()
            
            #if not interaction_points[0].id in point_effects:
            #    point_effects[interaction_points[0].id] = Effect(interaction_points[0].pos, angle_in_degrees, effect_width, effect_height, .7, fade_rate, .6)
            
    else:
        apply_collision_physics(attacker, receiver, attacker_hitboxes, receiver_hitboxes)
        receiver.set_player_state(player.PlayerStates.STUNNED)
        receiver.set_stun_timeout(attacker.get_stun_timeout())
        receiver.health_meter = max(0, receiver.health_meter - damage)
        
        if receiver.health_meter == 0:
            receiver.set_stun_timeout(9000)
        
        #if (stun_channel == None or
        #stun_channel.get_busy() == False):
        attacker.play_hit_sound()
        
    if not interaction_points[0].id in point_effects:
        point_effects[interaction_points[0].id] = Effect(interaction_points[0].pos, angle_in_degrees, effect_width, effect_height, .7, fade_rate, .6)
        

def attacker_is_recoiling(attack_knockback_vector, stun_knockback_vector):
    attack_x_sign = mathfuncs.sign(attack_knockback_vector[0])
    attack_y_sign = mathfuncs.sign(attack_knockback_vector[1])
    stun_x_sign = mathfuncs.sign(stun_knockback_vector[0])
    stun_y_sign = mathfuncs.sign(stun_knockback_vector[1])
    
    if (attack_x_sign != stun_x_sign) or (attack_y_sign != stun_y_sign):
        return True
    else:
        return False

def get_separation_vector(attacker, receiver):
    #x_delta = receiver.model.position[0] - attacker.model.position[0]
    y_delta = receiver.model.position[1] - attacker.model.position[1]
    
    #x_delta, y_delta = get_overlap(attacker, receiver)
    x_delta = 0
    
    if receiver.model.position[0] < attacker.model.position[0]:
        x_delta = receiver.model.position[0] - attacker.model.position[0]
    else:
        x_delta = attacker.model.position[0] - receiver.model.position[0]
    
    if y_delta > 0:
        y_delta = -1 * y_delta
    
    return (x_delta, y_delta)

def get_overlap(attacker, receiver):
    
    attacker_rect = pygame.Rect(*attacker.get_enclosing_rect())
    receiver_rect = pygame.Rect(*receiver.get_enclosing_rect())
    
    x_overlap = 0
    y_overlap = 0
    
    if receiver_rect.centerx > attacker_rect.centerx:
        x_overlap = attacker_rect.right - receiver_rect.left
    else:
        x_overlap = attacker_rect.left - receiver_rect.right
   
    if receiver_rect.centery > attacker_rect.centery:
        y_overlap = receiver_rect.top - attacker_rect.bottom
    else:
       y_overlap = attacker_rect.top - receiver_rect.bottom
   
    return x_overlap, y_overlap

def get_knockback_vector(attacker, attack_point):
    """get the direction and magnitude of the knockback"""
    
    return scale_knockback(attacker.get_point_position_change(attack_point.name))

def get_pull_point_deltas(attacker, attack_point):
    """gets the knockback applied to the interaction point to move the lines in the
    model"""
    
    knockback_vector = attacker.get_point_position_change(attack_point.name)
    
    x = knockback_vector[0]
    y = knockback_vector[1]
    hypotenuse = math.hypot(x,y)
    
    knockback = 3
    
    if hypotenuse == 0:
        return 0, 0
    else:
        return knockback * x / hypotenuse, knockback * y / hypotenuse

def scale_knockback(knockback_vector):
    """binds the scale of a knockback vector to control stun animation"""
    
    x = knockback_vector[0]
    y = knockback_vector[1]
    hypotenuse = math.hypot(x,y)
    
    knockback = .2
    
    if hypotenuse == 0:
        return 0, 0
    else:
        return 2 * knockback * x / hypotenuse, knockback * y / hypotenuse

def get_interaction_points(receiver, colliding_lines):
    attacker_line_index = 0
    receiver_line_index = 1
    
    attack_point1 = colliding_lines[attacker_line_index].endPoint1
    attack_point2 = colliding_lines[attacker_line_index].endPoint2
    receiver_point1 = receiver.get_point(stick.PointNames.TORSO_TOP) #colliding_lines[receiver_line_index].endPoint1
    receiver_point2 = receiver.get_point(stick.PointNames.TORSO_BOTTOM) #colliding_lines[receiver_line_index].endPoint2
    
    point_pairs = [(attack_point1, receiver_point1), \
                   (attack_point1, receiver_point2), \
                   (attack_point2, receiver_point1), \
                   (attack_point2, receiver_point2)]
    point_distances =  [mathfuncs.distance(attack_point1.pos, receiver_point1.pos), \
                        mathfuncs.distance(attack_point1.pos, receiver_point2.pos), \
                        mathfuncs.distance(attack_point2.pos, receiver_point1.pos), \
                        mathfuncs.distance(attack_point2.pos, receiver_point2.pos)]
    
    shortest_distance = min(point_distances)
    
    return point_pairs[point_distances.index(shortest_distance)]

def handle_blocked_attack_collision(attacker, receiver, attacker_hitboxes, receiver_hitboxes):
    attacker.set_neutral_state()
    receiver.set_neutral_state()
    
    apply_collision_physics(attacker, receiver, attacker_hitboxes, receiver_hitboxes)
    apply_collision_physics(receiver, attacker, receiver_hitboxes, attacker_hitboxes)
    
    clash_sound.play()

def apply_collision_physics(attacker, receiver, attacker_hitboxes, receiver_hitboxes):
    separation_vector = get_separation_vector(attacker,receiver)
    receiver.model.shift(separation_vector)
    colliding_line_names = test_attack_collision(attacker_hitboxes, receiver_hitboxes)
    
    colliding_lines = (attacker.model.lines[colliding_line_names[0]], \
                       receiver.model.lines[colliding_line_names[1]])
    
    interaction_points = get_interaction_points(receiver, colliding_lines)
    # print('attacker point: ' + interaction_points[0].name)
    # print('receiver point: ' + interaction_points[1].name)
    # print('receiver: ' + get_player(receiver))
    # print('attacker: ' + get_player(attacker))
    attack_point = interaction_points[0]
    receiver.knockback_vector = get_knockback_vector(attacker, attack_point)
    receiver.interaction_point = interaction_points[1]
    receiver.interaction_vector = get_pull_point_deltas(attacker, attack_point)
    receiver.pull_point(receiver.interaction_vector)
    receiver.model.velocity = (0,0)
    receiver.model.accelerate(receiver.knockback_vector[0], \
                              receiver.knockback_vector[1])

def get_direction_sign(attacker, receiver):
    receiver_pos = receiver.model.position
    attacker_pos = attacker.model.position
    direction_sign = -1
    
    if receiver_pos[0] > attacker_pos[0]:
        direction_sign = 1
    
    return direction_sign

def test_attack_collision(attack_hitbox_dictionary, receiver_hitbox_dictionary):
    colliding_line_names = None
    
    for attack_line_name, attack_hitboxes in attack_hitbox_dictionary.iteritems():
        for receiver_line_name, receiver_hitboxes in receiver_hitbox_dictionary.iteritems():
            for attack_hitbox in attack_hitboxes:
                if attack_hitbox.collidelist(receiver_hitboxes) > -1:
                    colliding_line_names = (attack_line_name, receiver_line_name)
                    break
            if colliding_line_names:
                break
        if colliding_line_names:
            break
    
    return colliding_line_names

def test_overlap(rect1, rect2):
    overlap = True
    rect1_pos = (rect1.left, rect1.top)
    rect2_pos = (rect2.left, rect2.top)
    
    if ((rect1_pos[0] > (rect2_pos[0] + rect2.width)) or
        ((rect1_pos[0] + rect1.width) < rect2_pos[0]) or
        (rect1_pos[1] > (rect2_pos[1] + rect2.height)) or
        ((rect1_pos[1] + rect1.height) < rect2_pos[1])):
        overlap = False
    
    return overlap

def get_hitbox_dictionary(lines):
    hitboxes = {}
    
    for name, line in lines.iteritems():
        if name == stick.LineNames.HEAD:
            hitboxes[name] = [get_circle_hitbox(line)]
        else:
            hitboxes[name] = get_line_hitboxes(line)
    
    return hitboxes

def get_hitboxes(lines):
    hitbox_dictionary = get_hitbox_dictionary(lines)
    hitbox_lines = []
    
    for hitbox_list in hitbox_dictionary.values():
        hitbox_lines.extend(hitbox_list)
    
    return hitbox_lines

def get_circle_hitbox(circle):
    circle.set_length()
    radius = int(circle.length / 2)
    hitbox = pygame.Rect((circle.center()[0] - radius, \
                          circle.center()[1] - radius), \
                         (circle.length, circle.length))
    
    return hitbox

def get_line_hitboxes(line):
    line_rects = []
    
    line.set_length()
    box_count = line.length / 7
    
    if box_count > 0:
        for pos in get_hitbox_positions(box_count, line):
            line_rects.append(pygame.Rect(pos, (14,14)))
    else:
        line_rects.append(pygame.Rect(line.endPoint1.pos, (14,14)))
    
    return line_rects

def get_hitbox_positions(box_count, line):
        """gets top left of each hitbox on a line.
        
        box_count: the number of hit boxes"""
        hitbox_positions = []
        
        start_pos = line.endPoint1.pixel_pos()
        end_pos = line.endPoint2.pixel_pos()
        
        x_delta = end_pos[0] - start_pos[0]
        y_delta = end_pos[1] - start_pos[1]
        
        length = line.length
        length_to_hit_box_center = 0
        increment = line.length / box_count
        
        hitbox_positions.append((int(end_pos[0] - 7), int(end_pos[1] - 7)))
        
        length_to_hit_box_center += increment
        x_pos = start_pos[0] + x_delta - ((x_delta / length) * length_to_hit_box_center)
        y_pos = start_pos[1] + y_delta - ((y_delta / length) * length_to_hit_box_center)
        box_center = (x_pos, y_pos)
        
        for i in range(int(box_count)):
            hitbox_positions.append((int(box_center[0] - 7), int(box_center[1] - 7)))
            
            length_to_hit_box_center += increment
            x_pos = start_pos[0] + x_delta - ((x_delta / length) * length_to_hit_box_center)
            y_pos = start_pos[1] + y_delta - ((y_delta / length) * length_to_hit_box_center)
            box_center = (x_pos, y_pos)
        
        hitbox_positions.append((int(start_pos[0] - 7), int(start_pos[1] - 7)))
        
        return hitbox_positions

class AttackResolver():
    """Applies the effect of collisions on each player involved in them."""
    
    def __init__(self):
        self.resolved_player_states = {}
        self.player_knockback_vectors = {}
        self.player_hitboxes = {}
        self.player_collisions = ()
    
    def reset():
        """resets the dictionaries of an AttackResolver"""
        self.resolved_player_states = {}
        self.player_knockback_vectors = {}
        self.player_hitboxes = {}
        self.player_collisions = {}
    
    def resolve_collisions(self, players):
        """applies the effects of collisions between a set of players"""
        #get attacking players
        #for each attacking player
        #   get knockbcak vectors from player attack
        #   get damage from player attaack
        
        #get collisions
        #for each collision:
        #   set post collision player states
        pass
    
    def get_collisions(self, players):
        #get attacking players
        #for each attacking player
        #   for each overlapping player       
        #       create a collision
        #       if an equivalent collision doesn't exist add it to the collisions dictionary
        pass
    
    def get_post_collision_player_states(self):
        #for each collision
        #   if both players are attacking resolve attack attack collision
        #   if one player is attacking resolve unblocked collision
        pass
