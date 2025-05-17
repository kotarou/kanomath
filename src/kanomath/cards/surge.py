from __future__ import annotations
from .card import CardCyle, WizardNAA, determine_arcane_damage

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player import Player


# The following cards are not implemented because honestly why bother
#   glyph Overlay


class SurgeNAA(WizardNAA):

    keywords = ["surge"]

    def __init__(self, owner: Player, zone: str, colour: str):
        WizardNAA.__init__(self, owner, zone, colour=colour)

    def on_play(self):

        WizardNAA.on_play(self)

        if self.test_surge():
            self.on_surge()

    def test_surge(self):
        # return self.damage_dealt > self.arcane
        pass

    def on_surge(self):
        pass

class SwellTidings(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.card_name = "Swell Tidings"
        self.arcane = 5
        self.cost = 2
        SurgeNAA.__init__(self, owner, zone, "red")

    def on_surge(self):
        pass

class EternalInferno(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.card_name = "Eternal Inferno"
        self.arcane = 4
        self.cost = 1
        self.colour = "red"
        SurgeNAA.__init__(self, owner, zone, "red")

    def on_surge(self):
        pass

class MindWarp(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.card_name = "Mind Warp"
        self.arcane = 2
        self.cost = 0
        SurgeNAA.__init__(self, owner, zone, "yellow")

    def on_surge(self):
        pass


class Overflow(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Overflow the Aetherwell"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class Prognosticate(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Prognosticate"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class FloodGates(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Open the Flood Gates"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 2  
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class AetherQuickening(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Aether Quickening"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class TrailblazingAether(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Trailblazing Aether"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class DestructiveAethertide(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.card_name = "Destructive Aethertide"
        self.arcane = 1
        self.cost = 0
        SurgeNAA.__init__(self, owner, zone, "blue")

    def on_surge(self):
        pass

class PerennialAetherBloom(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Perennial AetherBloom"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class PopTheBubble(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Pop the Bubble"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class Sap(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Sap"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass


class EtchingsOfArcana(SurgeNAA, CardCyle):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.card_name = "Etchings of Arcana"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

