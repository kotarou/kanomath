from __future__ import annotations

# from kanomath.functions import move_card_to_zone
from .card import ActivatableNAA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player import Player

POTIONS = ["Energy Potion", "Potion of Deja Vu", "Clarity Potion"]

class Potion(ActivatableNAA):

    card_class  = "generic"
    block       = 0
    cost        = 0
    colour      = "blue"
    
    resolve_to_zone     = "arena"
    activate_from_zone  = "arena"

class EnergyPotion(Potion):

    card_name       = "Energy Potion"
    card_name_short = "epot"

    def on_activate(self):
        self.controller.gain_pitch(2)
        Potion.on_activate(self)

class DejaVuPotion(Potion):

    card_name       = "Potion of Deja Vu"
    card_name_short = "dpot"

    def on_activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.on_activate(self)

class ClarityPotion(Potion):

    card_name       = "Clarity Potion" 
    card_name_short = "cpot"

    def on_activate(self):
        self.controller.opt(2)
        Potion.on_activate(self)