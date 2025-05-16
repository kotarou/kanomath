from __future__ import annotations
from .card import CardCyle, WizardNAA, determine_arcane_damage, determine_pitch, ActivatableNAA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player2 import Player2


class BlazingAether(WizardNAA):

    card_name   = "Blazing Aether"
    cost        = 0

    def __init__(self, owner: Player2, zone: str):
        self.arcane = 0   
        self.colour = "red"    
        WizardNAA.__init__(self, owner, zone)

    def on_damage(self):
        pass

# TODO: This can inherit the class of effects of InstantDiscard
class ArcaneTwining(WizardNAA, ActivatableNAA, CardCyle):

    card_name = "Arcane Twining"
    cost = 0
    activate_from_zone = "hand"

    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.arcane = determine_arcane_damage(3, colour)      
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_activate(self):
        # If in the player's hand
        # amp one
        # then discard
        pass


class PhotonSplicing(WizardNAA, CardCyle):
    
    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Photon Splicing"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1       
        WizardNAA.__init__(self, owner, zone, colour = colour)        

    def on_activate(self):
        # If in the player's hand
        # amp one
        # then discard
        pass


class AetherDart(WizardNAA, CardCyle):
    
    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Aether Dart"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class EmeritusScolding(WizardNAA, CardCyle):

    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Emeritus Scolding"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # In some way handle threatening more damage in their turn
        pass

class ScaldingRain(WizardNAA, CardCyle):
    
    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Scalding Rain"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class VolticBolt(WizardNAA, CardCyle):
    
    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Voltic Bolt"
        self.arcane = determine_arcane_damage(5, colour)
        self.cost = 2      
        WizardNAA.__init__(self, owner, zone, colour)

class Zap(WizardNAA, CardCyle):
    
    card_name = "Zap"

    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class Singe(WizardNAA, CardCyle):
    
    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Singe"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 1      
        WizardNAA.__init__(self, owner, zone, colour)