from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

next_player_id = 0
players = []

class ClientChannel(Channel):
    def Network:
        print(data)
    
    def Network_join_match(data):
        pass
    
    def Network_spectate_match(data):
        pass
    
    def Network_update_player_state(data):
        pass
    
    def Network_player_ready(data):
        pass

class WotsServer(Channel):
    channelClass = ClientChannel
    
    def Connected(self, channel, addr):
        print 'new connection:', channel
