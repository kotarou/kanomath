from __future__ import annotations
from .card import Card, CardCyle, WizardInstant, WizardNAA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player import Player

def determine_cindering_opt(colour: str) -> int:
    match colour:
        case "red" | "r":
            return 3
        case "yellow" | "y":
            return 2        
        case "blue" | "b":
            return 1        
        case _:
            return 3


class Gem(Card):

    block = 0
    cost = 0
    card_type = "resource"
    card_subtye = "gem"
    
    def __init__(self, owner: Player, zone: str):
        super().__init__(owner, zone)
    
    def on_play(self):
        raise Exception("Cannot play a resource card")

class GazeTheAges(WizardNAA):

    def __init__(self, owner: Player, zone: str):
        self.card_name = "Gaze the Ages"
        self.cost = 0 
        self.colour = "blue"
        WizardNAA.__init__(self, owner, zone)

    def on_play(self):
        # opt 2
        # If player has played another wizard NAA, go to hand
        pass

class CinderingForesight(WizardNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        self.card_name = "Cindering Foresight"
        self.cost = 0 
        self.block = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        self.controller.opt(determine_cindering_opt(self.colour))
        self.controller.register_amp_next(1,"Cindering Foresight")
        WizardNAA.on_play(self)
        pass    
    
class Kindle(WizardInstant):

    card_name = "Kindle"

    def __init__(self, owner: Player, zone: str):
        self.cost = 0 
        self.colour = "red"
        WizardInstant.__init__(self, owner, zone)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        self.controller.register_amp(1,"Kindle")
        WizardInstant.on_play(self)
        pass    

class EyeOfOphidia(Gem):

    card_name = "Eye of Ophidia"
    card_class = "generic"
    _colour = "blue"
    
    def __init__(self, owner: Player, zone: str):
        Gem.__init__(self, owner, zone)

    def on_pitch(self):
        self.controller.opt(2)
        Card.on_pitch(self)  

class WillOfArcana(Gem):

    card_name = "will of Arcana"
    crd_class = "wizard"
    _colour = "blue"
    
    def __init__(self, owner: Player, zone: str):
        Gem.__init__(self, owner, zone)

    def on_pitch(self):
        self.controller.register_amp(1, "Will of Arcana")
        Card.on_pitch(self)  