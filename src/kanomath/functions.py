from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kanomath.cards import Card2
    from kanomath.player2 import Player2


def move_cards_to_zone(cards: Card2 | list[Card2], new_zone: str):
    for card in cards:
        move_card_to_zone(card, new_zone)

def move_card_to_zone(card: Card2, new_zone_name: str, new_controller = None):

    current_zone = card.controller.get_zone_by_name(card.zone)
    card = current_zone.remove_card(card)
    
    add_card_to_zone(card, new_zone_name, new_controller = new_controller)

def add_card_to_zone(card: Card2, new_zone_name: str, new_controller = None):
    
    if new_controller is None:
        new_controller = card.controller

    new_zone = new_controller.get_zone_by_name(new_zone_name)
    new_zone.add_card(card)


def create_card_in_zone(cls: Card2, player: Player2, zone_name: str, *args, **kwargs) -> Card2:

    # TODO: send relevant kwargs along too
    card = cls(player, zone_name)

    add_card_to_zone(card, zone_name, player)

    return card
    