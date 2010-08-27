import pygame
import wotsuievents
import gamestate
import player
import humanplayer
import aiplayer
import button
import stage
import stick
import mathfuncs

class PlayerTypes:
    HUMAN = 'HUMAN'
    BOT = 'BOT'

gamestate.stage = stage.Stage(pygame.image.load('arenabkg.png'), 447)

initialized = False
human = None
bot = None
fight_label = None
ready_label = None
human_wins_label = None
bot_wins_label = None
fight_indicator = False
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

def init():
    global initialized
    global players
    global human
    global bot
    global ready_label
    global fight_label
    global human_wins_label
    global bot_wins_label
    global fight_indicator
    global fight_end_timer
    global versus_mode_start_timer
    global fight_start_timer
    global fps_label
    global player_type
    global bot_type
    
    fps_label = button.Label((200,200), str(gamestate.clock.get_fps()),(255,255,255),50)
    fight_indicator = False
    fight_end_timer = 0
    versus_mode_start_timer = 0
    fight_start_timer = 0
    
    ready_label = button.Label((0,0),'READY...',(255,255,255),100)
    ready_label_position = ((gamestate._WIDTH / 2) - (ready_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (ready_label.height / 2))
    ready_label.set_position(ready_label_position)
    
    fight_label = button.Label((0,0),'FIGHT!',(255,255,255),100)
    fight_label_position = ((gamestate._WIDTH / 2) - (fight_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (fight_label.height / 2))
    fight_label.set_position(fight_label_position)
    
    human_wins_label = button.Label((0,0),'YOU WIN!',(255,255,255),100)
    human_wins_label_position = ((gamestate._WIDTH / 2) - (human_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (human_wins_label.height / 2))
    human_wins_label.set_position(human_wins_label_position)
    
    bot_wins_label = button.Label((0,0),'BOT WINS!',(255,255,255),100)
    bot_wins_label_position = ((gamestate._WIDTH / 2) - (bot_wins_label.width / 2), \
                            (gamestate._HEIGHT / 2) - (bot_wins_label.height / 2))
    bot_wins_label.set_position(bot_wins_label_position)
    
    if player_type == PlayerTypes.HUMAN:
        new_player = humanplayer.HumanPlayer((200, 367))
    else:
        new_player = aiplayer.Bot((200, 367))
    
    if bot_type == PlayerTypes.HUMAN:
        second_player = humanplayer.HumanPlayer((500, 367))
    else:
        second_player = aiplayer.Bot((500, 367))
    
    human = new_player
    human.init_state()
    bot = second_player
    bot.init_state()
    bot.color = (0,255,0)
    
    wotsuievents.key_repeat = wotsuievents.KeyRepeat.HIGH
    initialized = True
    
    gamestate.frame_rate = 100
    gamestate.drawing_mode = gamestate.DrawingModes.DIRTY_RECTS
    
    gamestate.stage.draw(gamestate.screen)
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
    global fight_indicator
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    
    ready_label = None
    fight_label = None
    human_wins_label = None
    bot_wins_label = None
    fight_indicator = False
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
    global fight_indicator
    global versus_mode_start_timer
    global fight_start_timer
    global fight_end_timer
    global fps_label
    
    for rect in gamestate.old_dirty_rects:
        rect_surface = pygame.Surface((rect.width,rect.height))
        rect_surface.blit(gamestate.stage.bkg_image,((-rect.left,-rect.top)))
        gamestate.screen.blit(rect_surface,rect.topleft)
    
    exit_button.draw(gamestate.screen)
    gamestate.new_dirty_rects.append(pygame.Rect(exit_button.position, (exit_button.width,exit_button.height)))
    
    # fps_label.set_text(str(gamestate.clock.get_fps()))
    # fps_label.draw(gamestate.screen)
    # gamestate.new_dirty_rects.append(pygame.Rect(fps_label.position,(fps_label.width,fps_label.height)))
    
    if versus_mode_start_timer < 3000:
        ready_label.draw(gamestate.screen)
        gamestate.new_dirty_rects.append(pygame.Rect(ready_label.position,(ready_label.width,ready_label.height)))
        
        versus_mode_start_timer += gamestate.clock.get_time()
    else:
        fight_start_timer += gamestate.clock.get_time()
        fight_indicator = True
        
        if fight_start_timer < 1000:
            fight_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(fight_label.position,(fight_label.width,fight_label.height)))
    
    if bot.health_meter == 0:
        fight_indicator = False
        
        if fight_end_timer < 3000:
            fight_end_timer += gamestate.clock.get_time()
            human_wins_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(human_wins_label.position, \
                                             (human_wins_label.width, \
                                              human_wins_label.height)))
            
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()
    elif human.health_meter == 0:
        fight_indicator = False
        
        if fight_end_timer < 3000:
            fight_end_timer += gamestate.clock.get_time()
            bot_wins_label.draw(gamestate.screen)
            gamestate.new_dirty_rects.append(pygame.Rect(bot_wins_label.position, \
                                             (bot_wins_label.width, \
                                              bot_wins_label.height)))
        else:
            gamestate.mode = gamestate.Modes.VERSUSMOVESETSELECT
            exit()
    
    if exit_indicator == False and fight_indicator:
        if player_type == PlayerTypes.HUMAN:
            human.handle_events()
        else:
            human.handle_events(bot)
        
        #if bot_type == PlayerTypes.BOT:
        #    bot.handle_events(human)
        #else:
        #    bot.handle_events()
        
        #handle_interactions()
    
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
    
    if bot.action.action_state == player.PlayerStates.ATTACKING:
        handle_attacks(bot, human)
    elif human.action.action_state == player.PlayerStates.ATTACKING:
        handle_attacks(human, bot)

def get_player(input_player):
    global human
    
    return_name = 'bot'
    
    if input_player == human:
        return_name = 'human'
    
    return return_name

def handle_attacks(attacker, receiver):
    if attacker.attack_in_range(attacker.action, receiver):
        attacker_attack_hitboxes = get_hitbox_dictionary(attacker.action.attack_lines)
        
        if receiver.action.action_state == player.PlayerStates.ATTACKING:
            receiver_attack_hitboxes = get_hitbox_dictionary(receiver.action.attack_lines)
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

def draw_attacker_hitboxes(hitbox_dictionary):
    for name, hitboxes in hitbox_dictionary.iteritems():
        for hitbox in hitboxes:
            pygame.draw.rect(gamestate.screen, (255,0,0), hitbox, 1)

def draw_receiver_hitboxes(hitbox_dictionary):
    for name, hitboxes in hitbox_dictionary.iteritems():
        for hitbox in hitboxes:
            pygame.draw.rect(gamestate.screen, (0,0,255), hitbox, 1)

def handle_unblocked_attack_collision(attacker, receiver, attacker_hitboxes, receiver_hitboxes):
    apply_collision_physics(attacker, receiver, attacker_hitboxes, receiver_hitboxes)
    receiver.health_meter = max(0, receiver.health_meter - mathfuncs.distance((0,0), receiver.knockback_vector))
    
    receiver.actions[player.PlayerStates.STUNNED].set_player_state(receiver)

def get_separation_vector(attacker, receiver):
    x_delta = receiver.model.position[0] - attacker.model.position[0]
    y_delta = receiver.model.position[1] - attacker.model.position[1]
    
    if y_delta > 0:
        y_delta = -1 * y_delta
    
    return (x_delta, y_delta)
    
def get_knockback_vector(attacker, receiver, attack_point, attack_line_name):
    knockback_vector = None
    frame_index = attacker.action.animation.get_frame_index_at_time(attacker.model.animation_run_time)
    
    if frame_index == 0:
        knockback_vector = (get_direction_sign(attacker, receiver), get_direction_sign(attacker, receiver))
    else:
        knockback_vector = attacker.action.animation.animation_deltas[frame_index][attack_point.name]
    
    return knockback_vector

def get_interaction_points(colliding_lines):
    attacker_line_index = 0
    receiver_line_index = 1
    
    attack_point1 = colliding_lines[attacker_line_index].endPoint1
    attack_point2 = colliding_lines[attacker_line_index].endPoint2
    receiver_point1 = colliding_lines[receiver_line_index].endPoint1
    receiver_point2 = colliding_lines[receiver_line_index].endPoint2
    
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

def apply_collision_physics(attacker, receiver, attacker_hitboxes, receiver_hitboxes):
    separation_vector = get_separation_vector(attacker,receiver)
    receiver.model.shift(separation_vector)
    colliding_line_names = test_attack_collision(attacker_hitboxes, receiver_hitboxes)
    
    colliding_lines = (attacker.model.lines[colliding_line_names[0]], \
                       receiver.model.lines[colliding_line_names[1]])
    
    interaction_points = get_interaction_points(colliding_lines)
    # print('attacker point: ' + interaction_points[0].name)
    # print('receiver point: ' + interaction_points[1].name)
    # print('receiver: ' + get_player(receiver))
    # print('attacker: ' + get_player(attacker))
    attack_point = interaction_points[0]
    receiver.pull_point = interaction_points[1]
    receiver.knockback_vector = get_knockback_vector(attacker, \
                                                     receiver, \
                                                     attack_point, \
                                                     colliding_line_names[0])
    receiver.model.accelerate(receiver.knockback_vector[0]/500, \
                              receiver.knockback_vector[1]/500)

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
    box_count = line.length / 3.5
    
    if box_count > 0:
        for pos in get_hitbox_positions(box_count, line):
            line_rects.append(pygame.Rect(pos, (7,7)))
    else:
        line_rects.append(pygame.Rect(line.endPoint1.pos, (7,7)))
    
    return line_rects

def get_hitbox_positions(box_count, line):
        """gets center of each hitbox on a line.
        
        box_count: the number of hit boxes"""
        hitbox_positions = []
        
        start_pos = line.endPoint1.pixel_pos()
        end_pos = line.endPoint2.pixel_pos()
        
        x_delta = end_pos[0] - start_pos[0]
        y_delta = end_pos[1] - start_pos[1]
        
        length = line.length
        length_to_hit_box_center = 0
        increment = line.length / box_count
        
        hitbox_positions.append((int(end_pos[0] - 3.5), int(end_pos[1] - 3.5)))
        
        length_to_hit_box_center += increment
        x_pos = start_pos[0] + x_delta - ((x_delta / length) * length_to_hit_box_center)
        y_pos = start_pos[1] + y_delta - ((y_delta / length) * length_to_hit_box_center)
        box_center = (x_pos, y_pos)
        
        for i in range(int(box_count)):
            hitbox_positions.append((int(box_center[0] - 3.5), int(box_center[1] - 3.5)))
            
            length_to_hit_box_center += increment
            x_pos = start_pos[0] + x_delta - ((x_delta / length) * length_to_hit_box_center)
            y_pos = start_pos[1] + y_delta - ((y_delta / length) * length_to_hit_box_center)
            box_center = (x_pos, y_pos)
        
        hitbox_positions.append((int(start_pos[0] - 3.5), int(start_pos[1] - 3.5)))
        
        return hitbox_positions
