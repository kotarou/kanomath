from __future__ import annotations
from .card import CardCyle, WizardSpell, Card

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player import Player

class AetherArc(WizardSpell):

    card_name   = "Aether Arc"
    arcane      = 1
    cost        = 0
    colour      = "blue"
        
    def on_damage(self, damage_dealt: int):
        self.controller.make_token("Ponder")

class AetherSpindle(WizardSpell, CardCyle):

    card_name   = "Aether Spindle"
    cost        = 2

    def __init__(self, owner: Player, zone: str, colour: str = "red"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        self.arcane = Card.determine_numeric_property(4, colour)
        self.colour = Card.format_colour_string(colour)

    def on_damage(self, damage_dealt:int):
        self.controller.opt(damage_dealt)

class AetherFlare(WizardSpell, CardCyle):

    card_name   = "Aether Flare"
    cost        = 3

    def __init__(self, owner: Player, zone: str, colour: str = "red"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        self.arcane = Card.determine_numeric_property(1, colour)
        self.colour = Card.format_colour_string(colour)

    def on_damage(self, damage_dealt:int):
        self.controller.register_amp_next(damage_dealt, "aether flare")

class AetherWildfire(WizardSpell):

    card_name   = "Aether Wildfire"
    arcane      = 4
    cost        = 2
    colour      = "red"
        
    def on_damage(self, damage_dealt: int):
        self.controller.register_wildfire_amp(damage_dealt)

class LessonInLava(WizardSpell):

    card_name   = "Lesson in Lava"
    arcane      = 3
    cost        = 1
    colour      = "yellow"
        
    def on_damage(self, damage_dealt: int):
        pass


class SonicBoom(WizardSpell):

    card_name   = "Sonic Boom"
    arcane      = 3
    cost        = 2
    colour      = "yellow"

    def on_damage(self, damage_dealt: int):
        pass