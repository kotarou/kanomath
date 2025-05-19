from __future__ import annotations
from colored import Fore, Style

from typing import TYPE_CHECKING, override

from kanomath.zones import Zone
if TYPE_CHECKING:
    from kanomath.player import Player

# from kanomath.functions import move_card_to_zone

COMBO_CORE      = ["Aether Wildfire", "Blazing Aether", "Lesson in Lava"]
COMBO_EXTENDERS = ["Open the Flood Gates", "Overflow the Aetherwell", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]

# TODO: replace this with logger colours
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

class Card:

    @staticmethod
    def determine_pitch(card_colour: str) -> int:
        ''' Determine a card's pitch value from its colour. '''
        match card_colour:
            case "r" | "red":
                return 1
            case "y" | "yellow":
                return 2
            case "b" | "blue":
                return 3
            case "p" | "peral":
                return 0
            case _:
                raise ValueError(f"format_colour_string called with invalid string ({card_colour}).")


    @staticmethod
    def format_colour_string(colour_string: str | int) -> str:
        ''' Takes an short-hand input string (e.g. "r", "2", "yellow") and returns a properly formatted colour name'''
        match colour_string:
            case "r" | 1 | "red":
                return "red"
            case "y" | 2 | "yellow":
                return "yellow"
            case "b" | 3 | "blue":
                return "blue"
            case _:
                raise ValueError(f"format_colour_string called with invalid string ({colour_string}).")

    @staticmethod
    def determine_numeric_property(default_value: int, card_colour: str) -> int:
        ''' Assuming all numeric properties differ by 1, returns the numeric property when compared to a red version of the card.'''
        delta = 0

        match card_colour:
            case "red" | "r":
                delta = 0
            case "yellow" | "y":
                delta = 1        
            case "blue" | "b":
                delta = 2        
            case _:
                delta = 0

        return default_value - delta

    def __init__(self, owner: Player, zone: str = "deck", *args, **kwargs):
        
        # Core card components
        self.owner: Player      = owner
        self.controller: Player = owner
        self.zone: str          = zone
      
        if not hasattr(self, "colour"):
            self.colour =  Card.format_colour_string(kwargs.get('colour', "pearl"))

        # Defaults
        self.keywords           = list[str]()
        self.is_rainbow         = False
        self.resolve_to_zone    = "discard"

        # Stuff that will be set later
        self.block: int
        self.card_class: str
        self.card_type: str
        self.card_name: str
        self.cost: int

        # What the player plans to do with this card, this turn cycle
        self.intent: str        = ""

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

    @property
    def pitch(self) -> int:
        return Card.determine_pitch(self.colour)
    
    def on_play(self):
        Zone.move_card_to_zone(self, self.resolve_to_zone)
        pass

    def on_resolve(self):
        ''' 
        Once we have finished playing a card, control what hapens to it.

        Generally, we move the card to its resolution zone: subclasses whould take care of all other details.
        '''

        # Rough assumption that cards resolving to deck always go to the bottom
        if self.resolve_to_zone == "deck":
            Zone.move_card_to_zone(self, self.resolve_to_zone, "bottom")
        else:
            Zone.move_card_to_zone(self, self.resolve_to_zone)


    def on_pitch(self) -> int:
        Zone.move_card_to_zone(self, "pitch")
        self.controller.gain_pitch(self.pitch)
        return self.pitch

    def on_turn_end(self):
        pass

class ActivatableNAA(Card):
    card_type           = "action"
    card_subtype        = ""
    activate_to_zone    = "discard"

    def on_activate(self):
        Zone.move_card_to_zone(self, self.activate_to_zone)

class CardCyle():
    is_rainbow = True

class GenericNAA(Card):
    card_class      = "generic"
    card_type       = "action"
    card_sub_type   = ""

class WizardCard():
    card_class      = "wizard"

class WizardInstant(Card):
    
    card_class  = "wizard"
    card_type   = "instant"
    # In future, might need to use something more robust than 0 to represent instant blocks, if I'm trying to get rid of them from hand. 
    block       = 0

class WizardNAA(Card):

    card_class      = "wizard"
    card_type       = "action"
    card_sub_type   = ""

    @override
    def on_resolve(self):
        self.controller.wizard_naa_played += 1
        Card.on_resolve(self)

class WizardSpell(WizardNAA):

    # Blazing Aether, Chain Lightning, etc, will need to override this
    @property
    def deals_arcane(self) -> bool:
        return True
    
    def on_damage(self, damage_dealt: int):
        pass

    def on_play(self):
        # TODO: deal arcane damage
        pass
