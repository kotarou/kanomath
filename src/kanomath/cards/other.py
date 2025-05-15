from .card import WizardNAA
from kanomath.player2 import Player2


class GazeTheAges(WizardNAA):

    def __init__(self, owner: Player2, zone: str):
        self.card_name = "Gaze the Ages"
        self.cost = 0 
        self.colour = "blue"
        WizardNAA.__init__(self, owner, zone)

    def on_play(self):
        # opt 2
        # If player has played another wizard NAA, go to hand
        pass

class CinderingForesight(WizardNAA):

    def __init__(self, owner: Player2, zone: str, colour: str = "r"):
        self.card_name = "Cindering Foresight"
        self.cost = 0 
        self.block = 2
        WizardNAA.__init__(self, owner, zone, colour = colour)

    def on_play(self):
        # One of the only cards that cares about its colour in its resolution
        # opt some amount
        # amp 1 (kind of)
        pass    
    
