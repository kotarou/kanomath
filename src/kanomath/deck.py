from .card import Card
# from collections import deque
from collections.abc import Sequence
import random

class Deck:
    
    deckSize = 60
    cards = []
    data = {}

    @property
    def cardsLeft(self):
        return len(self.cards)

    def __init__(self):
        
        self.cards = [
            Card("Aether Spindle", 1, 2, arcane = 4),
            Card("Aether Spindle", 1, 2, arcane = 4),
            Card("Aether Spindle", 1, 0, arcane = 4),
            Card("Aether Wildfire", 1, 2, arcane = 4),  
            Card("Aether Wildfire", 1, 2, arcane = 4),
            Card("Aether Wildfire", 1, 2, arcane = 4),
            Card("Blazing Aether", 1, 0, arcane = 0),
            Card("Blazing Aether", 1, 0, arcane = 0),
            Card("Blazing Aether", 1, 0, arcane = 0),
            Card("Overflow the Aetherwell", 1, 0, arcane = 3),
            Card("Overflow the Aetherwell", 1, 0, arcane = 3),
            Card("Overflow the Aetherwell", 1, 0, arcane = 3),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Aether Arc", 3, 0, arcane = 1),
            Card("Aether Arc", 3, 0, arcane = 1),
            Card("Aether Arc", 3, 0, arcane = 1),
            Card("Arcane Twining", 3, 0, arcane = 1),
            Card("Arcane Twining", 3, 0, arcane = 1),
            Card("Arcane Twining", 3, 0, arcane = 1),
            Card("Destructive Aethertide", 3, 0, arcane = 1),
            Card("Destructive Aethertide", 3, 0, arcane = 1),
            Card("Destructive Aethertide", 3, 0, arcane = 1),
            Card("Energy Potion", 3, 0),
            Card("Energy Potion", 3, 0),
            Card("Energy Potion", 3, 0),
            Card("Eye of Ophidia", 3, 0, cardType = "gem"),
            Card("Gaze the Ages", 3, 0),
            Card("Gaze the Ages", 3, 0),
            Card("Gaze the Ages", 3, 0),
            Card("Open the Flood Gates", 3, 2, arcane = 1),
            Card("Open the Flood Gates", 3, 2, arcane = 1),
            Card("Open the Flood Gates", 3, 2, arcane = 1),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Pop the Bubble", 3, 0, arcane = 1),
            Card("Pop the Bubble", 3, 0, arcane = 1),
            Card("Pop the Bubble", 3, 0, arcane = 1),
            Card("Potion of Deja Vu", 3, 0),
            Card("Potion of Deja Vu", 3, 0),
            Card("Prognosticate", 3, 0, arcane = 1),
            Card("Prognosticate", 3, 0, arcane = 1),
            # Card("Prognosticate", 3, 0, arcane = 1),
            # Card("Sap", 3, 0, arcane = 1),
            # Card("Sap", 3, 0, arcane = 1),
            # Card("Sap", 3, 0, arcane = 1),
            Card("Will of Arcana", 3, 0, cardType = "gem"),
            
            Card("Kindle", 1, 0, cardType = "instant"),
            Card("Kindle", 1, 0, cardType = "instant"),
            Card("Kindle", 1, 0, cardType = "instant"),
            Card("Aether Flare", 1, 1, arcane = 3),
            Card("Aether Flare", 1, 1, arcane = 3),
            Card("Aether Flare", 1, 1, arcane = 3),

            Card("Open the Flood Gates", 2, 2, arcane = 2),
            Card("Open the Flood Gates", 2, 2, arcane = 2),
            Card("Open the Flood Gates", 2, 2, arcane = 2),

            Card("Open the Flood Gates", 1, 2, arcane = 3),
            Card("Open the Flood Gates", 1, 2, arcane = 3),
            Card("Open the Flood Gates", 1, 2, arcane = 3),
           
            # Card("Swell Tidings", 1, 2, arcane = 5),
            # Card("Swell Tidings", 1, 2, arcane = 5),
        ] 

        self.deckSize = len(self.cards)

        random.shuffle(self.cards)

        # i = 0
        # for card in self.cards:
        #     i += 1
        #     print(f"Initial deck order: {i} - {card.cardName}")


    def opt(self, optnum):
        optResultSize = min(len(self.cards), optnum)
        optResults = []
        for i in range(optResultSize):
            optResults.append(self.cards.pop(0))

        # statement = ", ".join(map(lambda x : x.name, optResults))
        # print(f"        Attempting to opt {optnum}, showing {optResultSize}: {statement}")
        return optResults


    def optBack(self, top, bottom):
        # print(f"Putting back {top} to top, and {bottom} to bot.")
        if(top is None):
            raise Exception("Top card cannot be null")
        if(bottom is None):
            raise Exception("Bottom card cannot be null")

        if(isinstance(top, Card)):
            self.cards.insert(0, top)
        elif(isinstance(top, Sequence)):
            # We reverse this because it makes the most sense that the first element is the top card
            top.reverse()
            for card in top:
                self.cards.insert(0, card)
        else:
            print("yo what the fuck")
        
        if(isinstance(bottom, Card)):
            self.cards.append(bottom)
        else:
            for card in bottom:
                self.cards.append(card)
   
    def draw(self, drawNum):
        actualDraws = min(len(self.cards), drawNum)
        results, self.cards = self.cards[:actualDraws], self.cards[actualDraws:]
        
        print(f"Player drew {results}.")
        return results
    

    def contains(self, target: str | Card) -> bool:

        if isinstance(target, Card):
            target = target.cardName
        
        for card in self.cards:
            if card.cardName == target:
                return True
        
        return False