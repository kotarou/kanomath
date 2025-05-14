from .interface import GenericNAA
from kanomath.player import Player

class Potion(GenericNAA):

    def __init__(self, owner: Player, zone: str):
        self.block = 0
        self.colour = "blue"  
        super().__init__(owner, zone)

    def on_play(self):
        self.controller.arena.append(self)
        self.zone = "arena"

    def on_activate(self):
        print("potion")
        self.controller.discard.append(self)
        self.zone = "discard"


class EnergyPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Energy Potion"       
        super().__init__(owner, zone)

    def on_activate(self):
        # self.controller.adjustResources(2)
        Potion.on_activate(self)

class DejaVuPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Potion of Deja Vu"       
        Potion.__init__(self, owner, zone)

    def on_activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.on_activate(self)

class ClarityPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Clarity Potion"       
        Potion.__init__(self, owner, zone)

    def on_activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.on_activate(self)