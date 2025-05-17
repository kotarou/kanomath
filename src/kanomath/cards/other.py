from __future__ import annotations
from .card import Card2, CardCyle, WizardInstant, WizardNAA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player2 import Player2

class Gem(Card2):

    block = 0
    cost = 0
    card_type = "resource"
    card_subtye = "gem"
    
    def __init__(self, owner: Player2, zone: str):
        super().__init__(owner, zone)
    
    def on_play(self):
        raise Exception("Cannot play a resource card")

class GazeTheAges(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Gaze the Ages"
        self.cost = 0 
        self.colour = "blue"
        WizardNAA.__init__(self, owner, zone)

    def on_play(self):
        # opt 2
        # If player has played another wizard NAA, go to hand
        pass

class CinderingForesight(WizardNAA, CardCyle):

    def __init__(self, owner: Player2, zone: str, colour: str = "r"):
        self.card_name = "Cindering Foresight"
        self.cost = 0 
        self.block = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        pass    
    
class Kindle(WizardInstant):

    card_name = "Kindle"

    def __init__(self, owner: Player2, zone: str):
        self.cost = 0 
        self.colour = "red"
        WizardInstant.__init__(self, owner, zone)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        pass    

class EyeOfOphidia(Gem):

    card_name = "Eye of Ophidia"
    card_class = "generic"
    _colour = "blue"
    
    def __init__(self, owner: Player2, zone: str):
        Gem.__init__(self, owner, zone)

    def on_pitch(self):
        self.controller.opt(2)  

class WillOfArcana(Gem):

    card_name = "will of Arcana"
    crd_class = "wizard"
    _colour = "blue"
    
    def __init__(self, owner: Player2, zone: str):
        Gem.__init__(self, owner, zone)

    def on_pitch(self):
        self.controller.gain_amp(1)  