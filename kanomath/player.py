from deck import Deck
from card import Card, SetupCards, ComboCoreCards, ComboExtensionCards, sortArsenalPlayPriority, sortSetupPlayPriority, sortArsenalPriority
from functools import reduce
from util import partition, kprint

class Player:
    pitch: int
    damage: int
    epots: int
    turn: int
    
    intellect = 4
    ap = 0
    arsenalLimit = 1
    hand = list[Card]

    amp = 0

    deck: Deck
    banish  = []
    discard = []
    pitch   = []
    arena   = []
    arsenal = []

    # Cards the player settings have prevented from being sarsenalled when they otherwise would (e.g. blazng)
    skipArsenal = []

    comboExecuted = False
    tunicCounters = 0
    resources = 0

    arsenalBlazing = True
    arsenalKindle = True
    playClarity = True
    ipEnergyPotions = True
    ipNonCoreComboPieces = True
    aggressivelyKanoNonBlues = True
    usesTunic = False
    
    wentFirst = True
    turnPlayer = ''
    
    def __init__(self):
        self.pitch = 0
        self.damage = 0
        self.turn = 0
        self.ap = 0

        self.amp = 0
    
        self.epots = 0
        self.dpots = 0
        self.cpots = 0

        self.turnPlayer = "self" if self.wentFirst else "opponent"

        self.deck = Deck()
        self.hand = self.deck.draw(4)

        if(not self.arsenalBlazing):
            self.skipArsenal.append("Blazing Aether")
        if(not self.arsenalKindle):
            self.skipArsenal.append("Kindle")

        # if(not self.playClarity):
        #     self.potionPriority.remove("Clarity Potion")

    # Prioritise potions
    def playPriority(self, card):
        if(card.cardName in self.potionPriority):
            return self.potionPriority.index(card.cardName)
        else:
            return 10

    # Prioritise combo pieces, then potions
    def arsenalPriority(self, card):
        if(card.cardName in self.comboArsenalPriority):
            return self.comboArsenalPriority.index(card.cardName)
        elif(card.cardName in self.potionPriority):
            return 10 + self.potionPriority.index(card.cardName)
        else:
            return 50

    # Prioritise combo pieces, then potions
    def kanoMyTurnPriority(self, card):
        if(card.cardName in self.potionPriority):
            return self.potionPriority.index(card.cardName)
        else:
            return 50

    def ragsPriority(self, card):
        if(card.cardName in self.comboPriority):
            return self.comboPriority.index(card.cardName)
        else:
            return 10

    def simulateOpponentTurn(self):
        self.turnPlayer = "player"
        if(self.assessComboReadiness()):
            print("Choosing to combo.")
            self.combo()
        elif(self.opponentForces()):
            print("Opponent has forced combo.")
            self.combo()
        else:
            pass
            # print("Passing Opponent's turn without issue.")

        return
    
    def opponentForces(self):
        return False

    def playCard(self, card, zone, **kwargs):

        asInstant = kwargs.get('asInstant', False)
        needsRemove = kwargs.get('removeFromZone', False)

        # Remove the card from its previous zone
        # Sometimes we don't need to do this, because we're iterating in a way where a list split makes more sense
        if(needsRemove):
            if(zone == "hand"):
                self.hand.pop(self.hand.index(card))
            elif(zone == "banish"):
                self.banish.pop(self.banish.index(card))
            elif(zone == "arsenal"):
                self.arsenal.pop(self.arsenal.index(card))
            elif(zone == "deck"):
                self.deck.cards.pop(self.deck.cards.index(card))
        
        # And put it in the discard
        # TODO: potions shouldn;t go to discard until their activation
        self.discard.append(card)

        card.play(self, asInstant=asInstant)
    
    def pitchCard(self, card, zone, **kwargs):
        
        needsRemove = kwargs.get('removeFromHand', False)

        # Assume we are either setting up, or combing
        # This is a pretty coarse assumption for now
        # TODO: implement pressure, tempo turns, and aether spindle pitch strategies
        cardRole = "combo" if self.turnPlayer == "opponent" else "setup"
        
        # Remove the pitched card from hand
        if(needsRemove):
            if(zone == "hand"):
                self.hand.pop(self.hand.index(card))
        # And place it into the pitch zone
        self.pitch.append(card)
        
        # Trigger pitch effects for the given card
        card.triggerPitchEffects(self, role=cardRole)
     

        # Return resources gained by this sequence
        self.resources += card.pitch
    


        

    # We're going to make some huge assumptions in this, because otherwise its just too complex to reaosnably write
    def combo(self):
        self.comboExecuted = 1
        
        comboHasWildfire = False
        comboHasBlazing = False
        ragsACard = False
        comboCards = []

        comboResources = 0

        # Begin by using energy potions
        self.iterateCardZone(self.arena, lambda x : x.cardName == "Energy Potion", "activate")

        # TODO: activate one clarity potion to try find a blue to rags off
        # Then, attempt to have a good hit underneath to kano into
        # If we see a top priority red and no blues, we'll kano the red, bottom anything else, then blind the topdeck of clarity again
        

        # # If we use tunic, check we can use counters, otherwise gain spellfrie resources
        # if(self.usesTunic and self.tunicCounters == 3):
        #     comboResources += 1
        # else:
        #     # TODO: Don't blindly assume spellfire when no tunic
        #     comboResources += 1

        # # We begin by assuming that the card in arsenal will be played at the correct time, and treat it otherwise as a card in hand that costs 1 to play out
        # arsenalName = self.arsenalcardName if self.arsenal else ""
        # if(arsenalName in self.comboPriority):
        #     comboResources -= 1
        #     comboCards.append(self.arsenal)

        # # Now, we need to work out which card in hand is going to be rags'd 
        # potentialRagsPieces = filter(self.hand[:], lambda x : xcardName in self.comboPriority)
        # potentialRagsPieces.sort(key=self.ragsPriority)

        # # Avoid the case where we rags wildfire after having one in arsenal
        # # TODO: make this work for more than just blazing, when appropriate
        # # TODO: work out how to judge what would be appropriate
        # blazingInHand = False
        # blazingIndex = -1
        # for i in range(len(potentialRagsPieces)):
        #     card = potentialRagsPieces[i]
        #     if(card.cardName == "Blazing Aether"):
        #         blazingInHand = True
        #         blazingIndex = i
        #         break
        
        # # In the case where we would wildfire from arsenal and have another in hand, instead rags the blazing
        # # We use the list ordering here just because I may want to manipulate this list later, when deja vu are properly implemented
        # # TODO: work for any combo piece, not just blazing
        # if(blazingInHand and arsenalName == "Aether  Wildfire" and potentialRagsPieces[0].cardName == "Aether Wildfire"):
        #     potentialRagsPieces.insert(0, potentialRagsPieces.pop(blazingIndex))
        # comboCards.append(potentialRagsPieces.pop())


        # # Incredibly rough and ready rags activation
        # # For early versions, we're going to assume that this card is always used as a resource
        # # TODO: deja vu interactions
        # self.hand.append(self.deck.draw(1))
        
        # # First pass is to remove the kindles
        
        # # Pitch all non-combo pieces
        # self.iterateCardZone(self.hand, lambda x : x.cardName not in self.comboPriority, "pitch")

           
        




    def assessComboReadiness(self):
        # kprint("Assessing combo readiness skipped")
        cards = self.hand[:]

        if(len(self.arsenal)):
            cards.extend(self.arsenal)

        cardNames = list(card.cardName for card in cards)

        # handPitch = sum(card.pitch for card in self.hand)
        # Pretend for now that a kindle on average draws a yellow
        handPitch = 0
        for card in self.hand:
            if card.cardName == "Kindle":
                handPitch +=2
            else:
                handPitch += card.pitch
        
        totalPitch = handPitch + 2 * self.epots
        
        # Tunic and spellfire
        if(self.usesTunic and self.tunicCounters == 3):
            totalPitch += 1
        else:
            totalPitch += 1 
        

        if("Blazing Aether" in cardNames and "Aether Wildfire" in cardNames and totalPitch > 10):
            print(f"  Player can potentially combo here")
            print(f"  Hand: {self.hand}")
            print(f"  Arsenal: {self.arsenal}")
            print(f"  Epots: {self.epots}, Dpots: {self.dpots}, Cpots: {self.cpots}")
            

            if("Energy Potion" in cardNames):
                print("  Choosing to wait to play epot out")
            else:
                return True
        
        return False




    def simulatePlayerTurn(self):
        # Note that because we simulate turns seperately, a player will never enter their turn with potential combo
        # If the payer could feasibly combo given game state, we will have executed it and ended this simulation
        self.turnPlayer = "player"
        self.turn += 1
        self.ap = 1
        self.resources = 0
        self.pitch = []
        
        # Handle tunic
        # This is included because in a super fast game, missing tunic is a viable worry to test for
        if(self.usesTunic and self.tunicCounters < 3):
            self.tunicCounters += 1

        kprint(f"Beginning turn {self.turn}. {len(self.hand)} cards in hand, {self.deck.cardsLeft}/{self.deck.deckSize} cards remaining in deck, {len(self.banish)} cards banished.")

        # We'll split cards into these buckets
        cardsToPlay     = []
        cardsToArsenal  = []
        cardsToBlock    = []
        cardsToPitch    = []
        cardsToHold     = []

        
        # Begin with arsenal; we want to play out any stored potion
        # While in real play it can be optimal to play from hand instead of arsenal, here I assume we want our arsenal card to be free ASAP.
        if(self.hasSetupInArsenal() and self.ap > 0):
            # While not really needed, lets make sure to play the best arsenal piece we can in case we ever get two somehow
            self.arsenal.sort(key=sortArsenalPlayPriority)
            card = self.arsenal[-1]
            
            kprint(f"Choosing to play {card} from arsenal.", 1)
            self.playCard(card, "arsenal", removeFromZone=True)


        for card in self.hand:
            # kprint(f"{card}")
            name = card.cardName

            # If we have a potion, we want to play it
            if(name in SetupCards.keys()):
                cardsToPlay.append(card)
            
            # If we have a combo piece, we want to arsenal it
            # Player perference can override whether a blazing goes into the arsenal sort here
            # TODO: Use sortArsenalPriority to be willing to arsenal extenders 
            elif(name in ComboCoreCards.keys() and not (card.cardName in self.skipArsenal)):
                cardsToArsenal.append(card)

            # If the card is blue, we want to pitch it to find more potions
            # Note that all blue setup pieces are already filtered by this point
            elif(card.pitch == 3):
                cardsToPitch.append(card)

            # All other cards are blocked with
            else:
                cardsToBlock.append(card)
        

        # If we have action points left over, lets play relevant cards out
        cardsToPlay.sort(key=sortSetupPlayPriority)

        while(self.ap > 0 and len(cardsToPlay)):
            card = cardsToPlay.pop()
            self.playCard(card, "hand")
            kprint(f"Choosing to play {card} from hand.", 1)
        
        # Any card we were considering playing could instead be arsenalled
        if(len(cardsToPlay)):
            cardsToArsenal = cardsToArsenal + cardsToPlay
        
        cardsToArsenal.sort(key=sortArsenalPriority)
        
        # Skip ahead, and arsenal any card we want to arsenal
        if(len(cardsToArsenal) > 0 and len(self.arsenal) < self.arsenalLimit):
            card = cardsToArsenal.pop()
            self.arsenal.append(card)
            kprint(f"Choosing to arsenal {card}.", 1)
        
        # At this point we have some cards we'd like to arsenal, some cards we'd ike to blockm with, and some cards we'd like to pitch
        # If we've set the flag to IP on energy poitions, hold it
        if(len(cardsToArsenal)):
            if(self.ipEnergyPotions):
                potions, rest = partition(lambda x : x.cardName == "Energy Potion", cardsToArsenal)
                cardsToHold.extend(potions)
                cardsToArsenal = rest
                # cardsToPitch.extend(rest)
            
            # Potential TODO: add flag and code for IPing for other types of potion, like deja vu

            # Hold core cards
            hold, donthold = partition(lambda x : x.cardName in ComboCoreCards, cardsToArsenal)
            cardsToHold.extend(hold)

            # Potential TODO: add flag and code for IPing for non core combo cards

            # Allocate any remaining cards
            blue, nonblue = partition(lambda x : x.pitch == 3, donthold)
            cardsToPitch.extend(blue)
            cardsToBlock.extend(nonblue)

        # Lets see if we're pitching away non-blue cards, or pretending to block with them
        # It only make sense to kano with them if we can hit a multiple of three pitch
        # Potential TODO: add a mid strategy where tunic is used with yellows
        # Potential TODO: add a mid strategy where yellow+yellow or yellow+red are used, but not red,red,red
        if(self.aggressivelyKanoNonBlues):
            # reverse, to sort from greatest to smallest
            cardsToBlock.sort(key=lambda card : card.pitch, reverse=True)
            # kprint(f"Aggressive block check: {cardsToBlock}", 2)
            checked = []
            totalPitch = 0
            for card in cardsToBlock:
                checked.append(card)
                totalPitch += card.pitch
                if(totalPitch >= 3):
                    # kprint(f"Adding {checked} to pitch", 2)
                    cardsToPitch.extend(checked)
                    checked = []
                    totalPitch -= 3
            cardsToBlock = checked
        
        # For each card we're pitching, check top of deck, then either play it if its a potion, brick, or banish it
        # When we brick, just kano entire hand at it anyway
        # Potentional optimization is to Ip self on good blues
        for card in cardsToPitch:
            self.pitchCard(card, "hand")
        
        # Do some Kanos
        numKanos = self.resources // 3
        kprint(f"Pitching {cardsToPitch} to Kano {numKanos} times.", 1)
        for i in range(numKanos):
            # Break if a kano fails or we want to leave the top of deck as is
            if(not self.kano()):
                break

        # Block with blocky cards
        # TODO: this should be the only block that needs to be tweaked for the hand to properly match cardsToHold
        if(len(cardsToBlock)):
            kprint(f"Blocking with {cardsToBlock}.", 1)
        for card in cardsToBlock:
            self.discard.append(card)
            self.hand.remove(card)

        if(len(cardsToHold)):
            kprint(f"Holding {cardsToHold} for next turn.", 1)
        
        # kprint(f"Hand ({len(self.hand)}), Hold ({len(cardsToHold)})")
        # This ideally won;t be needed, need to check everything else works
        self.hand = cardsToHold

        self.drawUp()

        


        


        
        # We assume any cards that are note

            
    def draw(self, num):

        cards = self.deck.draw(num)

        self.hand = self.hand + cards

        # if(num == 1):
        #     self.hand.append()
        # elif(num > 1):
        #     self.hand.extend(self.deck.draw(num))
        # elif(num == 0):
            
    
    # Draw up to your intellect, while potentially IPing ouselves with some cards
    def drawUp(self, ip = []):
        self.hand = ip if ip else self.hand
        self.draw(self.intellect - len(self.hand))

    # Iterate over cards 
    def iterateCardZone(self, zone, selectFunc, action):
        # Create a copy of the target zone
        executeCards, keepCards = partition(selectFunc, zone)

        for card in executeCards:
            # We don't support playing cards here, because kindle is a bitch
            # if(action == "play"):
            #     self.playCard(card, zone, removeFromZone = False)
            if(action == "pitch"):
                self.pitchCard(card, zone, removeFromZone = False)
            elif(action == "activate"):
                self.activateCard(card, zone, removeFromZone = False)

        zone = keepCards
        
    def hasSetupInArsenal(self):
        return any(card.cardName in SetupCards for card in self.arsenal)

    # Return True if we successfully played the top card, False otherwise
    def kano(self):
        if(len(self.deck.cards) == 0):
            kprint("Kanoing revealed the deck is in fact empty.", 2)
            return False
        
        topDeck = self.deck.cards[0]
        name = topDeck.cardName
        
        # Check if its a card that works with kano's ability
        if(topDeck.cardType != "action"):
            kprint(f"Kano bricked on {topDeck}.", 2)
            return False

        # Otherwise, lets work out what to do with it
        # Potential TODO: play out pressure cards, or spindle
        # Potential TODO: banish extra blazings if we see them too early, or have more (either 2 more in deck, or one in arsenal)
        if(name in ComboCoreCards.keys()):
            kprint(f"Kano reveals {topDeck}. Leaving it on top of deck.", 2)
            return False
        elif(name in ComboExtensionCards.keys()):
            kprint(f"Kano reveals {topDeck}. Leaving it in banish for now.", 2)
            self.banish.append(topDeck)
            self.deck.cards.pop(0)
        elif(name in SetupCards.keys()):
            kprint(f"Kano reveals {topDeck}. Playing it.", 2)
            self.playCard(topDeck, "deck", asInstant=True, removeFromZone=True)
        else:
            kprint(f"Kano reveals {topDeck}. Leaving it in banish.", 2)
            self.banish.append(topDeck)
            self.deck.cards.pop(0)
        
        return True




