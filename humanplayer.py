import copy
import functools
from random import choice
import pygame
import inputtree
import player
import wotsuievents
import gamestate
import movesetdata
import actionwizard
from controlsdata import get_controls
from enumerations import PlayerStates, CommandDurations, InputActionTypes, CommandCollections
from playercontroller import Controller, InputCommandTypes
from playerutils import ActionFactory, Transition, Action, Attack, JumpAttack

class HumanPlayer(player.Player):
    def __init__(self, position, player_position):
        player.Player.__init__(self, position, player_position)
        self.player_type = player.PlayerTypes.HUMAN
    
    def load_moveset(self, moveset):
        player.Player.load_moveset(self, moveset)
        
        self.actions[PlayerStates.STANDING].set_player_state(self)
    
    def get_attack_actions(self):
        return [
            attack_action
            for attack_action in self.actions.values()
            if attack_action.action_state == PlayerStates.ATTACKING
        ]
    
    def handle_events(self, input_command_types, time_passed):
        
        if self.handle_input_events:
            self.controller.update(input_command_types)
        else:
            self.controller.update(
                InputCommandTypes(
                    [],
                    InputActionTypes.NO_MOVEMENT,
                    [],
                    [],
                    []
                )
            )
        
        self.set_action()
        self.set_motion()
        player.Player.handle_events(self, time_passed)
