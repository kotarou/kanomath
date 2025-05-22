from __future__ import annotations

from kanomath.cards.vanilla import ScaldingRain, Zap
from .card import Card, CardCyle, WizardNAA, WizardSpell

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player import Player


# The following cards are not implemented because honestly why bother
#   Glyph Overlay

class SurgeNAA(WizardSpell):

    # TODO: maybe add surge keyword

    def on_damage(self, damage_dealt: int):
        if self.test_surge():
            self.on_surge()

    def test_surge(self):
        return self.damage_dealt > self.arcane

    def on_surge(self):
        pass

class SwellTidings(SurgeNAA):

    card_name   = "Swell Tidings"
    arcane      = 5
    cost        = 2
    colour      = "red"

    def on_surge(self):
        self.controller.make_token("Ponder")

class EternalInferno(SurgeNAA):

    card_name   = "Eternal Inferno"
    arcane      = 4
    cost        = 1
    colour      = "red"

    def on_surge(self):
        pass

class MindWarp(SurgeNAA):

    card_name   = "Mind Warp"
    arcane      = 2
    cost        = 0
    colour      = "yellow"

    def on_surge(self):
        pass


class Overflow(SurgeNAA, Zap):

    card_name   = "Overflow the Aetherwell"

    def on_surge(self):
        self.controller.gain_pitch(2)

class Prognosticate(SurgeNAA, Zap):

    card_name   = "Prognosticate"
   
    def on_surge(self):
        self.controller.opt(1)


class FloodGates(SurgeNAA, CardCyle):

    card_name   = "Open the Flood Gates"
    cost        = 2 

    def __init__(self, owner: Player, zone: str, colour: str = "blue"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        self.arcane = Card.determine_numeric_property(3, colour)
        self.colour = Card.format_colour_string(colour)

    def on_surge(self):
        self.controller.draw_card(2)

class AetherQuickening(SurgeNAA, ScaldingRain):

    card_name   = "Aether Quickening"

    def on_surge(self):
        self.controller.action_points += 1

class TrailblazingAether(SurgeNAA, Zap):

    card_name   = "Trailblazing Aether"

    def on_surge(self):
        self.controller.action_points += 1

class DestructiveAethertide(SurgeNAA):

    card_name   = "Destructive Aethertide"
    arcane      = 1
    cost        = 0
    colour      = "blue"

    def on_surge(self):
        pass

class PerennialAetherBloom(SurgeNAA, Zap):

    card_name = "Perennial AetherBloom"

    def on_surge(self):
        self.resolve_to_zone = "deck"

class PopTheBubble(SurgeNAA, Zap):

    card_name   = "Pop the Bubble"

    def on_surge(self):
        pass

class Sap(SurgeNAA, Zap):

    card_name   = "Sap"

    def on_surge(self):
        pass


class EtchingsOfArcana(SurgeNAA, Zap):

    card_name   = "Etchings of Arcana"

    def on_surge(self):
        pass

