from colored import Fore, Style
from enum import Enum

from src.kanomath.player import Player

def PrintColor(pitch: int):

    match pitch:
        case 0:
            return Fore.grey
        case 1:
            return Fore.red
        case 2:
            return Fore.yellow
        case 3:
            return Fore.blue               
        case _:
            return Fore.white


class Card2:

    zone: str

    pitch: int
    block: int
    _cost: int
    
    arcane: int

    controller: Player
    owner: Player

    cardClass: str = "generic"

    keywords: list[str]

    def __init__(self, owner: Player, zone = "deck"):
        self.zone = zone
        self.keywords = []

        self.owner = owner
        self.controller = owner

    def __str__(self):
        return f"{PrintColor(self.pitch)}{self.cardName}{Style.reset}"

    def __repr__(self):
        return self.__str__()

    # In the future, variable costs may become relevant. 
    # This property will interface with that code
    @property
    def cost(self) -> int:
        return self._cost
    
    @property
    def dealsArcane(self) -> bool:
        return self.arcane and self.arcane > 0

    def play(self):
        pass

    def pitch(self):
        pass

    def activate(self):
        pass



class Wizard(Card2):
    cardClass = "wizard"
    
    def play(self):
        # Increment the wizardNAA playerd tally for controlling player
        # self.controller.
        pass

class Generic():
    cardClass = "generic"

class NAA():
    cardType = "action"
    cardSubType = ""

class Instant():
    cardType = "instant"
