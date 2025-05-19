from __future__ import annotations
from .card import Card, CardCyle, WizardNAA, WizardSpell, ActivatableNAA

from typing import TYPE_CHECKING, override
if TYPE_CHECKING:
    from kanomath.player import Player

class Zap(WizardSpell, CardCyle):
    
    card_name   = "Zap"
    cost        = 0

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        base_arcane = 3
        self.arcane = Card.determine_numeric_property(base_arcane, colour)  
        self.colour = Card.format_colour_string(colour)    

class ScaldingRain(WizardSpell, CardCyle):
    
    card_name   = "Scalding Rain"
    cost        = 1

    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        base_arcane = 4
        self.arcane = Card.determine_numeric_property(base_arcane, colour)   
        self.colour = Card.format_colour_string(colour)   

class VolticBolt(WizardSpell, CardCyle):
    
    card_name   = "Voltic Bolt"
    cost        = 2

    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        base_arcane = 5
        self.arcane = Card.determine_numeric_property(base_arcane, colour)   
        self.colour = Card.format_colour_string(colour)   


class BlazingAether(WizardSpell):

    card_name   = "Blazing Aether"
    cost        = 0
    colour      = "red" 

    @property
    def deals_arcane(self) -> bool:
        return self.arcane > 0

    @property
    def arcane(self) -> int:
        return self.controller.arcane_damage_dealt


class ArcaneTwining(Zap, ActivatableNAA):

    card_name           = "Arcane Twining"
    activate_from_zone  = "hand"
    activate_from_zone  = "discard"

    def on_activate(self):
        self.controller.register_amp(1, "Arcane Twining")
        ActivatableNAA.on_activate(self)


class PhotonSplicing(ScaldingRain, ActivatableNAA):

    card_name           = "Photon Splicing"
    activate_from_zone  = "hand"
    activate_from_zone  = "discard"

    def on_activate(self):
        self.controller.register_amp(1, "Photon Splicing")
        ActivatableNAA.on_activate(self)


class AetherDart(Zap, CardCyle):
    
    card_name = "Aether Dart"


class EmeritusScolding(WizardSpell, CardCyle):
    
    card_name   = "Emeritus Scolding"
    cost        = 2
    
    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        colour_base_arcane = 4
        self.base_arcane = Card.determine_numeric_property(colour_base_arcane, colour)   
        self.colour = Card.format_colour_string(colour)   
    
    @property
    def arcane(self) -> int:
        return self.base_arcane if self.controller.is_player_turn else self.base_arcane + 2


class Singe(WizardSpell, CardCyle):
    
    card_name   = "Singe"
    cost        = 1

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        WizardSpell.__init__(self, owner, zone, colour=colour)
        base_arcane = 3
        self.arcane = Card.determine_numeric_property(base_arcane, colour)  
        self.colour = Card.format_colour_string(colour)    