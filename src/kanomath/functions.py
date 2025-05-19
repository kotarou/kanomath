from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING
from types import FunctionType, LambdaType
if TYPE_CHECKING:
    from kanomath.cards import Card
    from kanomath.player import Player

T = TypeVar('T')

# def move_cards_to_zone(cards: list[Card], new_zone: str):
#     for card in cards:
#         move_card_to_zone(card, new_zone)

# def move_card_to_zone(card: Card, new_zone_name: str):

#     current_zone = card.controller.get_zone_by_name(card.zone)
#     card = current_zone.remove_card(card)
    
#     add_card_to_zone(card, new_zone_name)

# def add_card_to_zone(card: Card, new_zone_name: str):


#     new_zone = card.controller.get_zone_by_name(new_zone_name)
#     new_zone.add_card(card)



# def create_card_in_zone(cls: function, player: Player, zone_name: str, *args, **kwargs) -> Card:

#     # TODO: send relevant kwargs along too
#     card = cls(player, zone_name) # type: ignore

#     add_card_to_zone(card, zone_name)

#     return card

def remove_first_matching(input: list[T], predicate: function) -> T | None:
# def remove_first_matching(input: list[T], predicate: function) -> tuple[T | None, list[T]]:
    
    r1 = None

    for i in range(len(input)):
        if predicate(input[i]): # type: ignore
            r1 = input.pop(i)
            break

    # return r1, 
    return r1

# def remove_all_matching(input: list[T], predicate: function) -> tuple[list[T], list[T]]:
def remove_all_matching(input: list[T], predicate: function) -> list[T]:
    
    r1 = []

    for item in input:
        if predicate(item): # type: ignore
            # print(f"      indicating {item} should be removed")
            r1.append(item)

    for item in r1:
        # print(f"      removing {item}")
        input.remove(item)

    # return r1, input
    return r1


def match_card_name(card_name: str | list[str]) -> function:

    if isinstance(card_name, str):
        return lambda x : x.card_name == card_name 
    else:
        return lambda x : x.card_name in card_name 

def match_card_pitch(pitch: int) -> function:
    return lambda x : x.pitch == pitch 

def card_is_red(card: Card):
    return card.colour == "red"
def card_is_yellow(card: Card):
    return card.colour == "yellow"
def card_is_blue(card: Card):
    return card.colour == "blue"
def card_is_pearl(card: Card):
    return card.colour == "pearl"