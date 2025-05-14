from colored import Fore, Style
from enum import Enum

from kanomath.player import Player

def print_colour(input: int | str):

    match input:
        case 0 | "p" | "pearl":
            return Fore.grey_0
        case 1 | "r" | "red":
            return Fore.red
        case 2 | "y" | "yellow":
            return Fore.yellow
        case 3 | "b" | "blue":
            return Fore.blue               
        case _:
            return Fore.white

def determine_pitch(colour: str) -> int:

    match colour:
        case "r" | "red":
            return 1
        case "y" | "yellow":
            return 2
        case "b" | "blue":
            return 3
        case _:
            # Also handles pearl
            return 0

def determine_colour(input: str | int) -> str:

    # Match three cases: single letter, number, or sent the correct form anyway

    match input:
        case "r" | 1 | "red":
            return "red"
        case "y" | 2 | "yellow":
            return "yellow"
        case "b" | 3 | "blue":
            return "blue"
        case _:
            # Also handles pearl
            return "pearl"

def determine_arcane_damage(base: int, colour: str) -> int:
    delta = 0

    match colour:
        case "red" | "r":
            delta = 0
        case "yellow" | "y":
            delta = 1        
        case "blue" | "b":
            delta = 2        
        case _:
             delta = 0

    return base - delta

class Card2:

    # Game state details
    controller: Player
    owner: Player
    zone: str

    # Intrinsic card details
    pitch: int
    block: int
    cardClass: str

    # Card details that are later controlled with getter and setter functions for whatever reason
    _cost: int
    _colour: str

    keywords: list[str]

    # Simple coloured detail of the card
    def __str__(self):
        return f"{print_colour(self.colour)}{self.cardName} ({self.pitch}){Style.reset}"

    def __repr__(self):
        return self.__str__()

    def __init__(self, owner: Player, zone = "deck", *args, **kwargs):
        self.zone = zone
        self.owner = owner
        self.controller = owner

        # A subclass might have already set our pitch
        # If not, set it to pearl, not because thats a sane default, but because its easy to spot
        if not hasattr(self, "colour"):
            self.colour   = kwargs.get('colour', "pearl")
        
        # Some subclasses will have initialized this already. 
        if not hasattr(self, "keywords"):
            self.ketwords = []

        

    # In the future, variable costs may become relevant. 
    # This property will interface with that code
    @property
    def cost(self) -> int:
        return self._cost
    @cost.setter
    def cost(self, value):
        self._cost = value
    
    # Our pitch value is determined by our colour, and is not otherwise an intrinsic aspect of the card
    @property
    def pitch(self) -> int:
        return determine_pitch(self.colour)
    
    # Ensure we don't accidentally set our colour using a shorthand "r"
    @property
    def colour(self) -> str:
        return self._colour
    @colour.setter
    def colour(self, value):
        self._colour = determine_colour(value)

    # @property
    # def dealsArcane(self) -> bool:
    #     return self.arcane and self.arcane > 0

    def on_play(self):
        pass

    def on_pitch(self):
        pass

    def on_activate(self):
        pass

class GenericNAA(Card2):
    cardClass = "generic"
    cardType = "action"
    cardSubType = ""

class WizardNAA(Card2):
    cardClass = "wizard"
    cardType = "action"
    cardSubType = ""

    arcaneDealt = 0

    def __init__(self, owner: Player, zone = "deck", *args, **kwargs):

        # Almost all wizard NAA block 3, so setit here as a default
        if not hasattr(self, "block"):
            self.block   = 3

        Card2.__init__(self, owner, zone, *args, **kwargs)


    def on_play(self):
        # Increment the wizardNAA playerd tally for controlling player
        # self.controller.
        pass 

class WizardInstant():
    cardClass = "wizard"
    # We don;t bother differentating pearl and 0 block
    block = 0
    cardType = "instant"

