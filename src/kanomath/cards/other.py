from __future__ import annotations

from loguru import logger
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

    block       = 0
    cost        = 0
    card_type   = "resource"
    card_subtye = "gem"
    
    def on_play(self):
        raise Exception("Cannot play a resource card")

class GazeTheAges(WizardNAA):

    card_name   = "Gaze the Ages"
    cost        = 0
    colour      = "blue"

    def on_play(self):
        self.controller.opt(2)

        if self.controller.wizard_naa_played > 0:
            self.resolve_to_zone = "hand"
    
    def on_turn_end(self):
        
        if self.resolve_to_zone == "hand":
            self.resolve_to_zone = "discard"


class CinderingForesight(WizardNAA, CardCyle):

    card_name   = "Cindering Foresight"
    cost        = 0 
    block       = 2

    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        self.controller.opt(Card.determine_numeric_property(3, self.colour))
        self.controller.register_amp_next(1,"Cindering Foresight")    
    
class Kindle(WizardInstant):

    card_name   = "Kindle"
    cost        = 0
    colour      = "red"

    def on_play(self):
        self.controller.register_amp(1,"Kindle")

        if self.controller.hand.size == 0:
            self.controller.draw(1) 
        else:
            logger.debug("Kindle was played without being able to draw")
            # raise Exception("You idiot you played a kindle without being able to draw")

class EyeOfOphidia(Gem):

    card_name   = "Eye of Ophidia"
    card_class  = "generic"
    colour      = "blue"
    
    def on_pitch(self):
        self.controller.opt(2)
        return Card.on_pitch(self)  

class WillOfArcana(Gem):

    card_name   = "will of Arcana"
    card_class  = "wizard"
    colour      = "blue"
    
    def on_pitch(self):
        self.controller.register_amp(1, "Will of Arcana")
        return Card.on_pitch(self)  