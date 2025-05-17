from __future__ import annotations
from colored import Fore, Style
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.player2 import Player2


from kanomath.functions import move_card_to_zone

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
    controller: Player2
    owner: Player2
    zone: str
    # TODO: explicitly type targets
    # target: 

    # Intrinsic card details
    # pitch: int
    block: int
    card_class: str
    card_type: str
    card_name: str
    card_name_short: str

    # Card details that are later controlled with getter and setter functions for whatever reason
    # _cost: int
    cost: int

    # Properties that classes may override
    keywords: list[str]
    
    # Special property for tracking what we plan to do with a card
    intent: str = ""

    # When we play the card, where will it resolve to?
    resolve_to_zone = "discard"

    # Simple coloured detail of the card

    def __str__(self):

        str = print_colour(self.colour) + self.card_name

        if self.is_rainbow:
            str += f" ({self.pitch})"

        str += Style.reset
        
        if self.intent != "":
            str += f" [{self.intent}]"
        return str

    def __repr__(self):
        return self.__str__()

    def __init__(self, owner: Player2, zone = "deck", *args, **kwargs):
        self.zone = zone
        self.owner = owner
        self.controller = owner

        # A subclass might have already set our pitch
        # If not, set it to pearl, not because thats a sane default, but because its easy to spot
        if not hasattr(self, "colour"):
            self.colour   = kwargs.get('colour', "pearl")
        
        # Some subclasses will have initialized this already. 
        if not hasattr(self, "keywords"):
            self.keywords = []

        if not hasattr(self, "card_name_short"):
            self.card_name_short = self.card_name

        if not hasattr(self, "is_rainbow"):
            self.is_rainbow = False

        if not hasattr(self, "card_type"):
            self.card_type = "naa"

    # In the future, variable costs may become relevant. 
    # This property will interface with that code
    # @property
    # def cost(self) -> int:
    #     return self._cost
    # @cost.setter
    # def cost(self, value):
    #     self._cost = value
    
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
        move_card_to_zone(self, self.resolve_to_zone)
        self.controller.spend_pitch(self.cost)
        pass

    def on_pitch(self) -> int:
        move_card_to_zone(self, "pitch")
        self.controller.gain_pitch(self.pitch)
        return self.pitch

COMBO_CORE      = ["Aether Wildfire", "Blazing Aether", "Lesson in Lava"]
COMBO_EXTENDERS = ["Open the Flood Gates", "Overflow the Aetherwell", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]

class ActivatableNAA(Card2):
    card_type = "action"
    card_subtype = ""

    activate_to_zone = "discard"
    activate_from_zone: str

    def on_activate(self):
        pass

    def activate(self):
        if self.can_activate:
            self.on_activate()
            move_card_to_zone(self, self.activate_to_zone)
        else:
            raise Exception(f"Invalid activation of {self}. Reason: {self.activation_error_reason}")

    @property
    def can_activate(self):
        return self.zone == self.activate_from_zone

    @property
    def activation_error_reason(self):
        if self.zone != self.activate_from_zone:
            return "invalid zone"
        return "unknown"


class GenericNAA(Card2):
    cardClass = "generic"
    cardType = "action"
    cardSubType = ""

class CardCyle():
    is_rainbow = True

class WizardNAA(Card2):
    cardClass = "wizard"
    cardType = "action"
    cardSubType = ""

    arcaneDealt = 0

    def __init__(self, owner: Player2, zone = "deck", *args, **kwargs):

        # Almost all wizard NAA block 3, so setit here as a default
        if not hasattr(self, "block"):
            self.block   = 3

        Card2.__init__(self, owner, zone, *args, **kwargs)

    def on_play(self):
        Card2.on_play(self)

class WizardInstant(Card2):
    cardClass = "wizard"
    # We don;t bother differentating pearl and 0 block
    block = 0
    cardType = "instant"

    def __init__(self, owner: Player2, zone = "deck", *args, **kwargs):
        Card2.__init__(self, owner, zone, *args, **kwargs)

