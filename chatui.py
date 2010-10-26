import pygame
import wotsuievents

from wotsuicontainers import TextBox
import eztext

class MessageEntryBox(TextBox):
    MESSAGE_PROMPT = 'Type your message: '
    
    def __init__(
        self,
        position = (0, 0),
        width = 0,
        font_size = 30
    ):
        TextBox.__init__(
            self,
            width = width,
            position = position,
            text_color = (255, 255, 255),
            font_size = font_size
        )
        
        self.text_entry_box = \
            eztext.Input(
                maxlength = 10000,
                x = position[0],
                y = position[1],
                prompt = MessageEntryBox.MESSAGE_PROMPT,
                color = (255, 255, 255),
                font = pygame.font.Font('freesansbold.ttf', font_size)
            )
        
        self.set_text()
    
    def draw(self, surface):
        """draws the message input box on the screen over any other renderings"""
        
        if self.visible:
            message_surface = pygame.Surface((self.width, self.height))
            
            TextBox.draw(self, message_surface)
            
            surface.blit(message_surface, self.position)
    
    def get_message(self):
        
        return self.text_entry_box.value
    
    def set_text(self):
        self.text = self.text_entry_box.prompt + self.text_entry_box.value
        
        TextBox.set_text(self, self.text)
    
    def clear_text(self):
        self.text_entry_box.value = ''
        self.text_entry_box.update([])
        self.text = self.text_entry_box.prompt + self.text_entry_box.value
        
        TextBox.set_text(self, self.text)
    
    def handle_events(self):
        """handle events that affect the text entry box"""
        
        if pygame.KEYDOWN in wotsuievents.event_types:
            self.text_entry_box.update(wotsuievents.events)
            
            self.set_text()
