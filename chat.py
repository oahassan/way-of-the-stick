import pygame
import wotsuievents
import gamestate
import versusclient
from versusserver import ClientActions, DataKeys
from chatui import MessageEntryBox, NetworkMessageNotification

entry_box = None
loaded_indicator = False
network_message_notifications = []

def load():
    global entry_box
    global loaded_indicator
    global network_message_notifications
    
    network_message_notifications = []
    loaded_indicator = True
    entry_box = MessageEntryBox((50,0), 700, 20)
    entry_box.hide()

def unload():
    global entry_box
    global loaded_indicator
    global network_message_notifications
    
    network_message_notifications = None
    loaded_indicator = False
    entry_box = None

def handle_events():
    global loaded_indicator
    global entry_box
    global network_message_notifications
    
    if not loaded_indicator:
        load()
    
    if entry_box.visible:
        if pygame.K_ESCAPE in wotsuievents.keys_pressed:
            close_entry_box()
        
        elif pygame.K_RETURN in wotsuievents.keys_pressed:
            
            if versusclient.connected():
                versusclient.send_chat_message(entry_box.get_message())
            
            close_entry_box()
        
        else:
            entry_box.handle_events()    
        
    else:
        if pygame.K_t in wotsuievents.keys_pressed:
            entry_box.show()
    
    if versusclient.connected():
        remove_expired_network_message_notifications()
        get_new_network_message_notifications()
        layout_network_message_notifications()
        
        time_passed = gamestate.clock.get_time()
        
        for notification in network_message_notifications:
            
            if gamestate.drawing_mode == gamestate.DrawingModes.DIRTY_RECTS:
                gamestate.new_dirty_rects.append(
                    pygame.Rect(notification.position,
                    (notification.width, notification.height))
                )
            
            notification.draw(gamestate.screen)
            notification.update(time_passed)
    
    if gamestate.drawing_mode == gamestate.DrawingModes.DIRTY_RECTS:
        gamestate.new_dirty_rects.append(
            pygame.Rect(entry_box.position,
            (entry_box.width, entry_box.height))
        )
    
    entry_box.draw(gamestate.screen)

def close_entry_box():
    entry_box.clear_text()
    entry_box.hide()

def get_new_network_message_notifications():
    received_data = versusclient.listener.pop_received_data()
    
    for data in received_data:
        if (data[DataKeys.ACTION] == 
        ClientActions.SPECTATOR_JOINED):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[DataKeys.NICKNAME] + " is now spectating."
                )
            )
        
        elif (data[DataKeys.ACTION] == ClientActions.PLAYER_DISCONNECTED):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[DataKeys.NICKNAME] + " has left the game."
                )
            )
        
        elif (data[DataKeys.ACTION] == ClientActions.PLAYER_JOINED_MATCH):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[DataKeys.NICKNAME] + " has joined the game."
                )
            )
        
        elif (data[DataKeys.ACTION] == ClientActions.MATCH_FULL):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    "The match is full."
                )
            )
        
        elif (data[DataKeys.ACTION] == ClientActions.RECEIVE_CHAT_MESSAGE):
            
            network_message_notifications.append(
                NetworkMessageNotification(
                    data[DataKeys.NICKNAME] + ": " + data[DataKeys.MESSAGE],
                    10000
                )
            )
        
        else:
            #TODO - Raise invalid value error here
            pass

def remove_expired_network_message_notifications():
    global network_message_notifications
    
    removable_messages = \
        [notification \
        for notification in network_message_notifications if notification.expired()]
    
    [network_message_notifications.remove(notification) \
    for notification in removable_messages]

def layout_network_message_notifications():
    global network_message_notifications
    
    network_message_count = len(network_message_notifications)
    
    row_count = min(5, network_message_count)
    
    first_row_position = (50, 10)
    current_row_position = first_row_position
    
    for notification in network_message_notifications:
        notification.set_position(current_row_position)
        
        current_row_position = (50, current_row_position[1] + notification.height)
