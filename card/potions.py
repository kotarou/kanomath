from .interface import NAA, Generic, Card2
from src.kanomath.player import Player

class Potion(Card2, Generic, NAA):

    def __init__(self, owner: Player, zone: str):
        self.block = 0
        self.pitch = 3    
        Card2.__init__(self, owner, zone)

    def play(self):
        self.controller.arena.append(self)
        self.zone = "arena"

    def activate(self):
        print("potion")
        self.controller.discard.append(self)
        self.zone = "discard"


class EnergyPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Energy Potion"       
        Potion.__init__(self, owner, zone)

    def activate(self):
        # self.controller.adjustResources(2)
        Potion.activate(self)

class DejaVuPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Potion of Deja Vu"       
        Potion.__init__(self, owner, zone)

    def activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.activate(self)

class ClarityPotion(Potion):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Clarity Potion"       
        Potion.__init__(self, owner, zone)

    def activate(self):
        # TODO: Generate a decision for the player
        #   Then, recieve a ordered lsit of cards from player decision
        #   And then put those to top of deck 
        Potion.activate(self)