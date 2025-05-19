from __future__ import annotations

from collections import deque
# from enum import Enum
from typing import Deque
import random
import copy

# from kanomath.functions import add_card_to_zone, move_card_to_zone, move_cards_to_zone

import typing
if typing.TYPE_CHECKING:
    from kanomath.player import Player
    from .cards import Card
    
class Zone:


    @staticmethod
    def move_card_to_zone(card: Card, new_zone_name: str, position = "top"):
        
        old_zone = card.controller.get_zone_by_name(card.zone)
        old_zone.remove_card(card)

        Zone.add_card_to_zone(card, new_zone_name, position)


    @staticmethod
    def add_card_to_zone(card: Card, new_zone_name: str, position = "top"):

        new_zone    = card.controller.get_zone_by_name(new_zone_name)
        add_index   = new_zone.size if position == "bottom" else 0
        new_zone.add_card(card, add_index)



    cards: Deque['Card']
    owner: Player
    zone_name = ""

    def __str__(self):
        str = f"[{self.zone_name}, {self.size} card"

        if self.size == 0:
            return str + "s]"
        elif self.size == 1:
            return str + f": {self.cards[0]}]"
        elif self.size == 2:
            return str + f"s: {self.cards[0]}, {self.cards[1]}]"
        else:
            return str + f"s: {self.cards[0]}, ..., {self.cards[-1]}]"

    def __init__(self, owner: Player):
    # def __init__(self, owner: 'Player2'):
        
        self.owner = owner

        # Some zones will have already constructed this
        if not hasattr(self, "cards"):
            self.cards = deque()  
    
    @property 
    def size(self):
        return len(self.cards)

    @property
    def is_empty(self):
        return self.size == 0
    
    def shuffle(self) -> None:
        random.shuffle(self.cards)

    # Primarily a testing method. WARNING: resets cards in zone
    def seed_with_cards(self, seed_cards: list[Card]) -> None:
        
        if self.size > 0:
            self.cards.clear()

        for card in seed_cards:
            card.zone = self.zone_name
            self.cards.append(card)

    # Remove some random cards
    # def remove_at_random(self, numToTake: int) -> Card2 | list[Card2]:
    #     out = []

    #     if numToTake < 1:
    #         return out

    #     numToTake = min(self.size, numToTake)

    #     for i in range(numToTake):
    #         idx = random.randint(0, self.size)
    #         card = self.cards[idx]
    #         out.append(self.cards.remove(card))

    #     return out
    
    # While probably not ever needed, these methods help me from the framework for later actions
    # def banish_by_index(self, idxs: list[int]) -> None:
        
    #     if len(idxs) > self.size:
    #         raise Exception(f"Attempting to banish more cards than in zone {self}")

    #     for i in sorted(idxs, reverse=True):
    #         # del test_list[i]
    #         card = self.cards[i].copy()
    #         move_card_to_zone(card, "banish")
    #         del self.cards[i]

    def contains_card(self, card: Card) -> bool:
        try:
            idx = self.cards.index(card)
            return True
        except ValueError as ve:
            return False

    def contains_card_name(self, card_name: str) -> bool:
        for card in self.cards:
            if card.card_name == card_name:
                return True
        return False
    
    def count_cards_name(self, card_name: str) -> int:
        count = 0
        for card in self.cards:
            if card.card_name == card_name:
                count += 1
        return count

    def remove_card(self, card) -> Card:

        # TODO: replace with try cach for value error
        idx = self.cards.index(card)

        # raise Exception(f"Attempting to remove {card} from {self}, but it was not present")

        # self.cards.remove(card)
        self.cards.remove(card)
        card.zone = ""
        card.intent = ""

        return card
    
    def add_card(self, card, idx = None):

        if idx is None or idx < 0:
            idx = 0

        if idx == 0:
            self.cards.appendleft(card)
        elif idx >= self.size:
            self.cards.append(card)
        else:
            self.cards.insert(idx, card)
        
        card.zone = self.zone_name
        card.intent = ""


class Deck(Zone):

    opt_incomplete: bool
    zone_name = "deck"

    def __init__(self, owner):
         self.opt_incomplete = False
         Zone.__init__(self, owner)

    def draw(self, num_to_take: int = 1) -> Card | list[Card]:
        
        if self.opt_incomplete:
            raise Exception("Attempting to draw cards while an opt is in progress.")

        if num_to_take < 1 or self.is_empty:
            return []
        
        if num_to_take == 1 or self.size == 1:
            return self.cards.popleft()
        
        num_to_take = min(self.size, num_to_take)

        out = []
        for i in range(num_to_take):
            out.append(self.cards.popleft())

        return out

    def opt(self, num_to_opt: int) -> list [Card]:
        
        if self.opt_incomplete:
            raise Exception("Attempting to opt while another opt is in progress.")

        if self.is_empty or num_to_opt < 1:
            return []
        
        num_to_opt = min(self.size, num_to_opt)

        out = []
        for i in range(num_to_opt):
            out.append(self.cards.popleft())

        if len(out):
            self.opt_incomplete = True
        
        return out

    # After we have opted, return two lists of cards back to top and bottom of deck
    def de_opt(self, top: list[Card], bot: list[Card]) -> None:

        if not self.opt_incomplete:
            raise Exception("Attempting to deopt without opting first.")

        # Last card in opt is first card back to top of deck, so we reverse the order
        for card in reversed(top):
            self.cards.appendleft(card)
        for card in bot:
            self.cards.append(card)

        self.opt_incomplete = False

    # After we have opted, return two lists of cards back to top and bottom of deck
    def bottom_card(self, card: Card) -> None:

        self.cards.append(card)


    def peek(self) -> Card | None:

        if self.is_empty:
            return None
        
        return self.cards[0]
    
    def mill(self, num_cards, target_zone = "discard") -> None:

        if num_cards < 1:
            return
        
        num_cards = min(num_cards, self.size)

        for i in range(num_cards):
            card = self.cards.popleft()
            Zone.move_card_to_zone(card, target_zone)


class Hand(Zone):
    
    zone_name = "hand"
    intellect: int

    def __init__(self, owner, intellect):
        self.intellect = intellect

        Zone.__init__(self, owner)

    def __repr__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[zone.hand: size {self.size}, cards: {str_cards}]"

    def __str__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[size {self.size}, cards: {str_cards}]"

    @property
    def potential_pitch(self) -> int:
        pitch = 0
        for card in self.cards:
                pitch += card.pitch
        return pitch

    def draw_up(self):

        num_to_draw = self.owner.current_intellect - self.size
        cards = self.owner.deck.draw(num_to_draw)

        if isinstance(cards, list):
            for card in cards:
                Zone.add_card_to_zone(card, "hand")
        else:
            Zone.add_card_to_zone(cards, "hand")

        # print(f"Player's hand for next turn: {self.cards}.")


class Arsenal(Zone):

    zone_name = "arsenal"
    capacity: int

    @property
    def has_card(self):
        return self.size > 0
    
    # TODO: support multiple arsenals eventually
    def get_card(self) -> Card | None:
        return self.cards[0] if self.size > 0 else None

    def __init__(self, owner, capacity):
        self.capacity = capacity
        self.cards = deque(maxlen=self.capacity)
        
        Zone.__init__(self, owner)

    def __repr__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[zone.arsenal: size {self.size}, cards: {str_cards}]"

    def __str__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[size {self.size}, cards: {str_cards}]"

class Pitch(Zone):
    
    zone_name = "pitch"

    def __init__(self, owner):
        Zone.__init__(self, owner)

class Banish(Zone):
    
    zone_name = "banish"

    def __init__(self, owner):
        Zone.__init__(self, owner)

class Discard(Zone):
    
    zone_name = "discard"

    def __init__(self, owner):
        Zone.__init__(self, owner)

class Arena(Zone):

    zone_name = "arena"
    
    def __init__(self, owner):
        Zone.__init__(self, owner)
    
    def __repr__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[zone.arena: size {self.size}, cards: {str_cards}]"

    def __str__(self):
        str_cards = "none" if self.size == 0 else ', '.join(str(x) for x in self.cards)
        return f"[size {self.size}, cards: {str_cards}]"
    