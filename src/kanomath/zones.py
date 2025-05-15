from collections import deque
from typing import Deque
import random
import copy

from kanomath.functions import move_card_to_zone

from .cards import Card2

import typing
if typing.TYPE_CHECKING:
    from kanomath.player2 import Player2
    
class Zone:

    cards: Deque['Card2']
    # owner: 'Player2'
    zone_name = ""

    def __str__(self):
        str = f"[{self.zone_name}, {self.size} card"

        if self.size == 0:
            return str + "s]"
        elif self.size == 1:
            return str + f": {self.cards[0]}]"
        elif self.size == 2:
            return str + f"s: {self.cards[0]}, {self.cards[0]}]"
        else:
            return str + f"s: {self.cards[0]}, ..., {self.cards[0]}]"


    def __init__(self):
    # def __init__(self, owner: 'Player2'):
        
        # self.owner = owner

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

    # Remove some random cards
    def remove_at_random(self, numToTake: int) -> Card2 | list[Card2]:
        out = []

        if numToTake < 1:
            return out

        numToTake = min(self.size, numToTake)

        for i in range(numToTake):
            idx = random.randint(0, self.size)
            card = self.cards[idx]
            out.append(self.cards.remove(card))

        return out
    
    # While probably not ever needed, these methods help me from the framework for later actions
    # def banish_by_index(self, idxs: list[int]) -> None:
        
    #     if len(idxs) > self.size:
    #         raise Exception(f"Attempting to banish more cards than in zone {self}")

    #     for i in sorted(idxs, reverse=True):
    #         # del test_list[i]
    #         card = self.cards[i].copy()
    #         move_card_to_zone(card, "banish")
    #         del self.cards[i]

    def contains_card(self, card) -> bool:
        try:
            idx = self.cards.index(card)
            return True
        except ValueError as ve:
            return False

    def contains_card_name(self, card_name: str) -> bool:
        for card in self.cards:
            if card.card_name == card_name or card.card_name_short == card_name:
                return True
        return False
    
    def count_cards_name(self, card_name: str) -> int:
        count = 0
        for card in self.cards:
            if card.card_name == card_name or card.card_name_short == card_name:
                count += 1
        return count

    def remove_card(self, card) -> Card2:

        idx = self.cards.index(card)

        if idx == -1:
            raise Exception(f"Attempting to remove {card} from {self}, but it was not present")

        self.cards.remove(card)
        card.zone = ""

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

        


class Deck(Zone):

    opt_incomplete: bool
    zone_name = "deck"

    def __init__(self):
         self.opt_incomplete = False
         Zone.__init__(self)

    def draw(self, num_to_take: int = 1) -> Card2 | list[Card2]:
        
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

    def opt(self, num_to_opt: int) -> list [Card2]:
        
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
    def de_opt(self, top: list[Card2], bot: list[Card2]) -> None:

        if not self.opt_incomplete:
            raise Exception("Attempting to deopt without opting first.")

        # Last card in opt is first card back to top of deck, so we reverse the order
        self.cards.extendleft(reversed(top))
        self.cards.extend(bot)

        self.opt_incomplete = False

    def peek(self) -> Card2 | None:

        if self.is_empty:
            return None
        
        return self.cards[0]
    
    def mill(self, num_cards, target_zone = "discard") -> None:

        if num_cards < 1:
            return
        
        num_cards = min(num_cards, self.size)

        for i in range(num_cards):
            card = self.cards.popleft()
            move_card_to_zone(card, target_zone)


class Hand(Zone):
    
    zone_name = "hand"
    intellect: int

    def __init__(self, intellect):
        self.intellect = intellect

        Zone.__init__(self)
    
    @property
    def potential_pitch(self) -> int:
        pitch = 0
        for card in self.cards:
                pitch += card.pitch
        return pitch



class Arsenal(Zone):

    zone_name = "arsenal"
    capacity: int

    def __init__(self, capacity):
        self.capacity = capacity
        self.cards = deque(maxlen=self.capacity)
        
        Zone.__init__(self)

class Pitch(Zone):
    
    zone_name = "pitch"

    def __init__(self):
        Zone.__init__(self)

class Banish(Zone):
    
    zone_name = "banish"

    def __init__(self):
        Zone.__init__(self)

class Discard(Zone):
    
    zone_name = "discard"

    def __init__(self):
        Zone.__init__(self)

class Arena(Zone):

    zone_name = "arena"
    
    def __init__(self):
        Zone.__init__(self)

    