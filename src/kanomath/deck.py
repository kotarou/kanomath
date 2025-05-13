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
            Card("Zap", 3, "action"),
            Card("Zbp", 3, "action"),
            Card("Zcp", 3, "action"),
            # Card("Aether Spindle", 1, "action"),
            # Card("Aether Spindle", 1, "action"),
            Card("Aether Spindle", 1, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Blazing Aether", 1, "action"),
            Card("Aether Wildfire", 1, "action"),
            Card("Blazing Aether", 1, "action"),
            Card("Aether Wildfire", 1, "action"),
            Card("Potion of Deja Vu", 3, "action"),
            Card("Eye of Ophidia", 3, "gem"),
            Card("Will of Arcana", 3, "gem"),
            Card("Zdp", 3, "action"),
            Card("Zep", 3, "action"),
            Card("Zfp", 3, "action"),
            Card("Zgp", 3, "action"),
            Card("Zhp", 3, "action"),
            Card("Zip", 3, "action"),
            Card("Zjp", 3, "action"),
            Card("Zkp", 3, "action"),
            Card("Zlp", 3, "action"),
            Card("Zmp", 3, "action"),
            Card("Znp", 3, "action"),
            Card("Zop", 3, "action"),
            Card("Kindle", 1, "instant"),
            # Card("Kindle", 1, "instant"),
            # Card("Kindle", 1, "instant"),
            Card("Overflow the Aetherwell", 2, "action"),
            Card("Overflow the Aetherwell", 2, "action"),
            Card("Overflow the Aetherwell", 2, "action"),
            Card("Overflow the Aetherwell", 3, "action"),
            Card("Overflow the Aetherwell", 3, "action"),
            Card("Overflow the Aetherwell", 3, "action"),
            # Card("Lesson in Lava", 2, "action"),
            # Card("Lesson in Lava", 2, "action"),
            # Card("Lesson in Lava", 2, "action"),
            # Card("Zpp", 3, "action"),
            # Card("Zqp", 3, "action"),
            # Card("Zrp", 3, "action"),
            # Card("Zsp", 3, "action"),
            # Card("Ztp", 3, "action"),
            # Card("Zup", 3, "action"),
            # Card("Zvp", 3, "action"),
            # Card("Zwp", 3, "action"),
            # Card("Zxp", 3, "action"),
            # Card("Zyp", 3, "action"),
            # Card("Zzp", 3, "action"),
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