import select, socket, struct
import re

import pygame

from wotsprot import channel, protocol
import wotsuievents
import wotsuicontainers
import gamestate
import menupage
import button
import onlineversusmovesetselectloader
import versusclient
import versusserver
import serverselectui
from enumerations import ServerDiscovery


VALID_IPV4_ADDRESS_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

connect_button = None
join_match_button = None
server_address_input = None
server_list = None
server_finder = None

exit_button = None
exit_indicator = False

loaded = False

class LanServerFinder(socket.socket):
    def __init__(self):
        
        #initialize socket
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setblocking(0)
        self.bind(('',protocol.SERVER_DISCOVERY_PORT))
        
        addrinfo = socket.getaddrinfo(protocol.SERVER_DISCOVERY_GROUP, None)[0]
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
        
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    def Receive(self):
        """returns whether network actions were received"""
        
        try:
            payload, remote_address = self.recvfrom(protocol.MAX_PACKET_SIZE)
            
            if protocol.validate_broadcast_packet(payload):
                
                data = protocol.get_data(payload)
                
                if type(dict()) == type(data) and data.has_key('action'):
                    self.handle_network_callback(data)
                elif data == protocol.KEEPALIVE_PAYLOAD:
                    pass
                else:
                    print("OOB data (no such Network_action):", data) 
            
            return True
        except:
            return False
    
    def handle_network_callback(self, data):
        [getattr(self, n)(data) for n in ('Network', 'Network_' + data['action']) if hasattr(self, n)]
    
    def Network_acknowledge_server(self, data):
        add_server_to_server_list(data[ServerDiscovery.ADDRESS])

def add_server_to_server_list(ip_address):
    global server_list
    
    server_list.add_server_address(ip_address)

def load():
    global exit_button
    global exit_indicator
    global loaded
    global connect_button
    global server_address_input
    global server_list
    global server_finder
    
    exit_button = button.ExitButton()
    exit_indicator = False
    loaded = True
    
    server_address_input = None
    connect_button = button.SelectableLabel((550,100), "Connect", 32)
    connect_button.inactivate()
    server_address_input = wotsuicontainers.TextEntryBox(
        "Enter Server:  ",
        position = (50, 100)
    )
    server_list = serverselectui.ServerTable((50, 130))
    
    server_finder = LanServerFinder()
    
def unload():
    global exit_button
    global exit_indicator
    global loaded
    global connect_button
    global server_address_input
    global server_list
    global server_finder
    
    exit_button = None
    exit_indicator = False
    loaded = False
    connect_button = None
    server_address_input = None
    server_list = None
    
    server_finder.close()
    server_finder = None

def handle_events():
    global exit_button
    global exit_indicator
    global connect_button
    global loaded
    global server_address_input
    global server_list
    global server_finder
    
    if not loaded:
        load()
    else:
        while server_finder.Receive():
            pass
        
        server_address_input.handle_events()
        server_list.handle_events()
        exit_button.draw(gamestate.screen)
        connect_button.draw(gamestate.screen)
        server_address_input.draw(gamestate.screen)
        server_list.draw(gamestate.screen)
        
        if server_list.selected_row != None:
            server_address_input.set_text(server_list.selected_row.get_address())
        
        if (re.match(VALID_IPV4_ADDRESS_REGEX, server_address_input.get_input()) and
        connect_button.active == False):
            connect_button.activate()
        elif (not re.match(VALID_IPV4_ADDRESS_REGEX, server_address_input.get_input()) and
        connect_button.active):
            connect_button.inactivate()
        
        if pygame.MOUSEBUTTONDOWN in wotsuievents.event_types:
            if exit_button.contains(wotsuievents.mouse_pos):
                exit_indicator = True
                exit_button.color = button.Button._SlctdColor
                exit_button.symbol.color = button.Button._SlctdColor
            
            if connect_button.contains(wotsuievents.mouse_pos) and connect_button.active:
                connect_button.handle_selected()
            
        elif pygame.MOUSEBUTTONUP in wotsuievents.event_types:
            if exit_indicator == True:
                exit_indicator = False
                exit_button.color = button.Button._InactiveColor
                exit_button.symbol.color = button.Button._InactiveColor
                
                if exit_button.contains(wotsuievents.mouse_pos):
                    unload()
                    gamestate.mode = gamestate.Modes.ONLINEMENUPAGE
            
            elif connect_button.contains(wotsuievents.mouse_pos) and connect_button.selected:
                connect_button.handle_selected()
                
                unload()
                gamestate.mode = gamestate.Modes.ONLINEVERSUSMOVESETSELECTLOADER
                onlineversusmovesetselectloader.load(versusserver.get_lan_ip_address())
