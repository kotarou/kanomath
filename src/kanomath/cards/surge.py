from .interface import WizardNAA, determine_arcane_damage
from src.kanomath.player import Player

# The following cards are not implemented because honestly why bother
#   glyph Overlay


class SurgeNAA(WizardNAA):

    keywords = ["surge"]

    def __init__(self, owner: Player, zone: str, colour: str):
        WizardNAA.__init__(self, owner, zone, colour=colour)

    def on_play(self):

        WizardNAA.on_play()

        if self.test_surge():
            self.on_surge()

    def test_surge(self):
        return self.damageDealt > self.arcane

    def on_surge(self):
        pass

class SwellTidings(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Swell Tidings"
        self.arcane = 5
        self.cost = 2
        self.colour = "red"
        SurgeNAA.__init__(self, owner, zone)

    def on_surge(self):
        pass

class EternalInferno(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Eternal Inferno"
        self.arcane = 4
        self.cost = 1
        self.colour = "red"
        SurgeNAA.__init__(self, owner, zone)

    def on_surge(self):
        pass

class MindWarp(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Mind Warp"
        self.arcane = 2
        self.cost = 0
        self.colour = "yellow"
        SurgeNAA.__init__(self, owner, zone)

    def on_surge(self):
        pass


class Overflow(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Overflow the Aetherwell"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class Prognosticate(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Prognosticate"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class FloodGates(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Open the Flood Gates"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 2  
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class AetherQuickening(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Aether Quickening"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class TrailblazingAether(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Trailblazing Aether"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class DestructiveAethertide(SurgeNAA):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Destructive Aethertide"
        self.arcane = 1
        self.cost = 0
        self.pitch = 3
        SurgeNAA.__init__(self, owner, zone)

    def on_surge(self):
        pass

class PerennialAetherBloom(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Perennial AetherBloom"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class PopTheBubble(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Pop the Bubble"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

class Sap(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Sap"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass


class EtchingsOfArcana(SurgeNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Etchings of Arcana"
        self.arcane = determine_arcane_damage(1, colour)
        self.cost = 0 
        SurgeNAA.__init__(self, owner, zone, colour)

    def on_surge(self):
        pass

