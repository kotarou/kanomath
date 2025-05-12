from deck import Deck
from card import Card
from functools import reduce

class Player:
    pitch: int
    damage: int
    epots: int
    turn: int
    
    intellect = 4
    ap = 0
    hand = list[Card]

    deck: Deck
    banish = []
    discard = []
    arsenal = None

    arsenalBlazing = False
    arsenalKindle = True
    playClarity = True
    ipEnergyPotions = True
    
    comboPriority = [
        "Aether Wildfire",
        "Kindle",
        "Blazing Aether",
    ]

    comboArsenalPriority = [
        "Aether Wildfire",
        "Kindle",
        "Blazing Aether"
    ]

    potionPriority = [
        "Energy Potion",
        "Potion of Deja Vu",
        "Clarity Potion"
    ]

    def __init__(self):
        self.pitch = 0
        self.damage = 0
        self.turn = 0
        self.ap = 0
    
        self.epots = 0
        self.dpots = 0
        self.cpots = 0

        self.deck = Deck()
        self.hand = self.deck.draw(4)

        if(not self.arsenalBlazing):
            self.comboArsenalPriority.remove("Blazing Aether")
        
        if(not self.arsenalKindle):
            self.comboArsenalPriority.remove("Kindle")

        if(not self.playClarity):
            self.potionPriority.remove("Clarity Potion")

    # Prioritise potions
    def playPriority(self, card):
        if(card.name in self.potionPriority):
            return self.potionPriority.index(card.name)
        else:
            return 10

    # Prioritise combo pieces, then potions
    def arsenalPriority(self, card):
        if(card.name in self.comboArsenalPriority):
            return self.comboArsenalPriority.index(card.name)
        elif(card.name in self.potionPriority):
            return 10 + self.potionPriority.index(card.name)
        else:
            return 50

    # Prioritise combo pieces, then potions
    def kanoMyTurnPriority(self, card):
        if(card.name in self.potionPriority):
            return self.potionPriority.index(card.name)
        else:
            return 50

    def clearArsenal(self):
        self.discard.append(self.arsenal)
        self.arsenal = None

    def simulateOpponentTurn(self):
        self.assessComboReadiness()
        return

    def assessComboReadiness(self):
        cards = self.hand[:]

        if(self.arsenal):
            cards.append(self.arsenal)

        cardNames = list(card.name for card in cards)

        handPitch = sum(card.pitch for card in self.hand)
        totalPitch = handPitch + 2 * self.epots

        if("Blazing Aether" in cardNames and "Aether Wildfire" in cardNames and totalPitch > 8):
            print(f"Player can potentially combo here: Hand(above), Arsenal({self.arsenal.name if self.arsenal else 'None'}), epots({self.epots})")


    def simulatePlayerTurn(self):
        # Note that because we simulate turns seperately, a player will never enter their turn with potential combo
        # If the payer could feasibly combo given game state, we will have executed it and ended this simulation
        self.turn += 1
        self.ap = 1

        print(f"Beginning turn {self.turn}")

        potentialPlays = []
        potentialArsenals = []
        pretendBlocks = []
        potentialPitches = []
        potentialIP = []

        
        # Begin with arsenal; we want to play out any stored potion
        # A potential optimization is to play an epot from hand over an different arsenaled potion,
        #   however, for now we take the approach that clearing arsenal is optimal whenever possible
        #   in order to maximize the probability of arsenalling a combo piece.
        if(self.arsenal and self.ap == 1):
            if(self.arsenal.name in self.potionPriority):
                self.arsenal.play(self)
                print(f"    Choosing to play {self.arsenal.name} from arsenal.")
                self.clearArsenal()



        for card in self.hand:
            # If we have a potion, we want to play it
            if(card.name in self.potionPriority):
                potentialPlays.append(card)
                continue
            
            # If we have a combo piece, we want to arsenal it
            if(card.name in self.comboPriority):
                potentialArsenals.append(card)
                continue

            # We will pitch all blues to kano for more potion chances
            if(card.pitch == 3):
                potentialPitches.append(card)
                continue

            # All other cards are blocked with
            else:
                pretendBlocks.append(card)
                continue
        


        potentialPlays.sort(key=self.playPriority)
        
        # While we have AP and cards we could play, play them
        while(self.ap > 0 and len(potentialPlays)):
            card = potentialPlays.pop(0)
            card.play(self)
            print(f"    Choosing to play {card.name} from hand.")
        
        # Any card we were considering playing could instead be arsenalled
        if(len(potentialPlays)):
            potentialArsenals = potentialArsenals + potentialPlays
        
        potentialArsenals.sort(key=self.arsenalPriority)

        # Skip ahead, and arsenal any card we want to arsenal
        if(not self.arsenal and len(potentialArsenals)):
            self.arsenal = potentialArsenals.pop(0)
            print(f"    Choosing to arsenal {self.arsenal.name}.")
        
        # Check if we want to hold any card for combo or next turn
        # Otherwise, if its a blue, we'll kano with it
        # Otherwise, we pretend we blocked with it
        # A potential improvement here is to kano with multiple cards (e.g. a red+yellow)
        for card in potentialArsenals:
            if(card.name == "Energy Potion" and self.ipEnergyPotions):
                potentialIP.append(card)
            elif(card.name in self.comboPriority):
                potentialIP.append(card)
            elif(card.pitch == 3):
                potentialPitches.append(card)
            else:
                pretendBlocks.append(card)
        
        # For each card we're pitching, check top of deck, then either play it if its a potion, brick, or banish it
        # When we brick, just kano entire hand at it anyway
        # Potentional optimization is to Ip self on good blues
        for card in potentialPitches:
            output = f"    Pitching {card.name} to Kano "
            # Eye is pretty complex, and this behaviour can be improved
            # For now, bottom anything that isn't a combo piece or potion
            if(card.name == "Eye of Ophidia"):
                opt = self.deck.opt(2)
                top = []
                bottom = []

                for optcard in opt:
                    if(optcard.name in self.potionPriority or optcard.name in self.comboPriority):
                        top.append(optcard)
                    else:
                        bottom.append(optcard)
                # Potions > combo pieces > other
                if(len(top)):
                    top.sort(key=self.kanoMyTurnPriority)
                
                output += f"(opting top({len(top)}), bottom({len(bottom)})) "
                self.deck.optBack(top, bottom)

            topCards = self.deck.opt(1)
            top = None
            if(len(topCards) == 1):
                top = topCards[0]
            
            if(top is None):
                print("Deck is out of cards")
                break

            if(top.name in self.potionPriority):
                output += f"and playing {top.name}."
                top.play(self, asInstant=True)
            # Potential improvement is to banish e.g. blazing aethers while there is more than 1 left
            elif(top.name in self.comboPriority):
                output += f"and choosing to not play {top.name}."
                self.deck.optBack(top, [])
            elif(top.cardType != "action"):
                output += f"and bricking on {top.name}."
                self.deck.optBack(top, [])
            else:
                output += f"and banishing {top.name}."
                self.banish.append(top)
            print(output)

        for card in pretendBlocks:
            print(f"    Pretending we blocked with {card.name}.")
            self.discard.append(card)

        for card in potentialIP:
            print(f"    Holding {card.name} for next turn.")
            self.discard.append(card)

        # Draw for end of turn
        if(len(potentialIP)):
            statement = ", ".join(map(lambda x : x.name, potentialIP))
            print(f"Cards held to combo: {statement}.")
        self.hand = potentialIP + self.deck.draw(self.intellect - len(potentialIP))
        # hand, deck = self.deck[:self.intellect], self.deck[self.intellect:]

        


        


        
        # We assume any cards that are note

            
