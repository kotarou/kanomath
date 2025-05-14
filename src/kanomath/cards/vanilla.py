from .interface import WizardNAA, determine_arcane_damage, determine_pitch
from kanomath.player import Player


# TODO: This can inherit the class of effects of InstantDiscard
class ArcaneTwining(WizardNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Arcane Twining"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0       
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_activate(self):
        # If in the player's hand
        # amp one
        # then discard
        pass


class PhotonSplicing(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Photon Splicing"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1       
        WizardNAA.__init__(self, owner, zone, colour = colour)        

    def on_activate(self):
        # If in the player's hand
        # amp one
        # then discard
        pass


class AetherDart(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Aether Dart"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class EmeritusScolding(WizardNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Emeritus Scolding"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # In some way handle threatening more damage in their turn
        pass

class ScaldingRain(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Scalding Rain"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 1       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class VolticBolt(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Voltic Bolt"
        self.arcane = determine_arcane_damage(5, colour)
        self.cost = 2      
        WizardNAA.__init__(self, owner, zone, colour)

class Zap(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Aether Dart"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 0       
        WizardNAA.__init__(self, owner, zone, colour = colour)

class Singe(WizardNAA):
    
    def __init__(self, owner: Player, zone: str, colour: str = "b"):
        self.cardName = "Singe"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 1      
        WizardNAA.__init__(self, owner, zone, colour)