from card import Card
# from collections import deque
from collections.abc import Sequence
import random

class Deck:
    deckSize = 60
    cards = []
    data = {}

    def __init__(self):
        
        self.cards = [
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Aether Spindle", 1, "action"),
            Card("Aether Spindle", 1, "action"),
            Card("Aether Spindle", 1, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Energy Potion", 3, "action"),
            Card("Blazing Aether", 1, "action"),
            Card("Aether Wildfire", 1, "action"),
            Card("Potion of Deja Vu", 3, "action"),
            Card("Eye of Ophidia", 3, "gem"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action"),
            Card("Zap", 3, "action")
        ] 

        random.shuffle(self.cards)

        i = 0
        for card in self.cards:
            i += 1
            print(f"Initial deck order: {i} - {card.name}")


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
        
        statement = ", ".join(map(lambda x : x.name, results))
        print(f"Player drew {statement}.")
        return results