from .interface import WizardNAA
from kanomath.player import Player


class GazeTheAges(WizardNAA):

    def __init__(self, owner: Player, zone: str):
        self.cardName = "Gaze the Ages"
        self.cost = 0 
        self.colour = "blue"
        WizardNAA.__init__(self, owner, zone)

    def on_play(self):
        # opt 2
        # If player has played another wizard NAA, go to hand
        pass

class CinderingForesight(WizardNAA):

    def __init__(self, owner: Player, zone: str, colour: str = "r"):
        self.cardName = "Cindering Foresight"
        self.cost = 0 
        self.block = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        pass    
    
