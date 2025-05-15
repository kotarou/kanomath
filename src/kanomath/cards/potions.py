from __future__ import annotations

from kanomath.functions import move_card_to_zone
from .card import ActivatableNAA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player2 import Player2



POTIONS = ["Energy Potion", "Potion of Deja Vu", "Clarity Potion"]

class Potion(ActivatableNAA):

    block = 0
    card_class = "generic"

    resolve_to_zone = "arena"
    activate_from_zone = "arena"

    def __init__(self, owner: Player2, zone: str):
        self.colour = "blue"

        super().__init__(owner, zone)

    # def on_play(self):
    #     self.controller.arena.append(self)
    #     self.zone = "arena"

    def on_activate(self):
        ActivatableNAA.on_activate(self)

    #     if self.can_activate:
    #         move_card_to_zone(self, self.activate_to_zone)



class EnergyPotion(Potion):

    card_name = "Energy Potion"
    card_name_short = "epot"

    def __init__(self, owner: Player2, zone: str):      
        super().__init__(owner, zone)

    def on_activate(self):
        self.controller.gain_pitch(2)
        Potion.on_activate(self)

class DejaVuPotion(Potion):

    card_name = "Potion of Deja Vu"
    card_name_short = "dpot"

    def __init__(self, owner: Player2, zone: str):       
        Potion.__init__(self, owner, zone)

    def on_activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.on_activate(self)

class ClarityPotion(Potion):

    card_name = "Clarity Potion" 
    card_name_short = "cpot"

    def __init__(self, owner: Player2, zone: str):
        Potion.__init__(self, owner, zone)

    def on_activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.on_activate(self)