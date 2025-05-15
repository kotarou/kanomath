
from .card import WizardNAA, determine_arcane_damage
from kanomath.player2 import Player2

class AetherArc(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Aether Arc"
        self.arcane = 1
        self.cost = 0
        self.colour = "blue"
        WizardNAA.__init__(self, owner, zone)

    def on_damage(self):
        pass

class AetherSpindle(WizardNAA):

    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Aether Spindle"
        self.arcane = determine_arcane_damage(4, colour)
        self.cost = 2
        WizardNAA.__init__(self, owner, zone, colour)

    def on_damage(self):
        pass

class AetherFlare(WizardNAA):

    def __init__(self, owner: Player2, zone: str, colour: str = "b"):
        self.card_name = "Aether Flare"
        self.arcane = determine_arcane_damage(3, colour)
        self.cost = 1 
        WizardNAA.__init__(self, owner, zone, colour)

    def on_damage(self):
        pass

class AetherWildfire(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Aether Wildfire"
        self.arcane = 4
        self.cost = 2
        self.colour = "red"
        WizardNAA.__init__(self, owner, zone)

    def on_damage(self):
        pass

class LessonInLava(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Lesson in Lava"
        self.arcane = 3
        self.cost = 1 
        self.colour = "yellow"
        WizardNAA.__init__(self, owner, zone)

    def on_damage(self):
        pass

class SonicBoom(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Sonic Boom"
        self.arcane = 3
        self.cost = 2
        self.colour = "yellow"
        WizardNAA.__init__(self, owner, zone)

    def on_damage(self):
        pass