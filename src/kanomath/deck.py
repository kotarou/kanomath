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
            Card("Zap", 3, 0, arcane = 1),
            Card("Zbp", 3, 0, arcane = 1),
            Card("Zcp", 3, 0, arcane = 1),
            Card("Aether Flare", 1, 1, arcane = 3),
            Card("Aether Flare", 1, 1, arcane = 3),
            Card("Aether Spindle", 1, 2, arcane = 4),
            Card("Aether Spindle", 1, 2, arcane = 4),
            Card("Aether Spindle", 1, 0, arcane = 4),
            Card("Energy Potion", 3, 0),
            Card("Energy Potion", 3, 0),
            Card("Energy Potion", 3, 0),
            Card("Blazing Aether", 1, 0, arcane = 0),
            Card("Blazing Aether", 1, 0, arcane = 0),
            Card("Aether Wildfire", 1, 2, arcane = 4),  
            Card("Aether Wildfire", 1, 2, arcane = 4),
            Card("Potion of Deja Vu", 3, 0),
            Card("Eye of Ophidia", 3, 0, cardType = "gem"),
            Card("Will of Arcana", 3, 0, cardType = "gem"),
            Card("Zdp", 3, 0, arcane = 1),
            Card("Zep", 3, 0, arcane = 1),
            Card("Zfp", 3, 0, arcane = 1),
            Card("Zgp", 3, 0, arcane = 1),
            Card("Zhp", 3, 0, arcane = 1),
            Card("Zip", 3, 0, arcane = 1),
            Card("Zjp", 3, 0, arcane = 1),
            Card("Zkp", 3, 0, arcane = 1),
            Card("Zlp", 3, 0, arcane = 1),
            Card("Zmp", 3, 0, arcane = 1),
            Card("Znp", 3, 0, arcane = 1),
            Card("Zop", 3, 0, arcane = 1),
            Card("Kindle", 1, 0, cardType = "instant"),
            # Card("Kindle", 1, "instant"),
            # Card("Kindle", 1, "instant"),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Overflow the Aetherwell", 2, 0, arcane = 2),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Overflow the Aetherwell", 3, 0, arcane = 1),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Lesson in Lava", 2, 1, arcane = 3),
            Card("Zpp", 3, 0, arcane = 1),
            Card("Zqp", 3, 0, arcane = 1),
            Card("Zrp", 3, 0, arcane = 1),
            Card("Zsp", 3, 0, arcane = 1),
            Card("Ztp", 3, 0, arcane = 1),
            Card("Zup", 3, 0, arcane = 1),
            Card("Zvp", 3, 0, arcane = 1),
            Card("Zwp", 3, 0, arcane = 1),
            Card("Zxp", 3, 0, arcane = 1),
            Card("Zyp", 3, 0, arcane = 1),
            Card("Zzp", 3, 0, arcane = 1),
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