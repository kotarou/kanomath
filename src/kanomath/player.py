from .deck import Deck
from .opponent import Opponent
from .card import Card, SetupCards, ComboCoreCards, ComboExtensionCards, sortArsenalPlayPriority, sortSetupPlayPriority, sortArsenalPriority
from functools import reduce
from .util import partition, kprint, flatten
from colored import Fore, Style

# from . import deck
# from . import card
# from . import util

# from combo import startCombo

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
    arcaneDamageDealt = 0
    wildfireAmp = 0

    deck: Deck

    banish  = []
    # Where banish cards go after losing relevance
    # We assume a card in banish can be played this turn fir simplicites sake
    exile   = []
    discard = []
    pitch   = []
    arena   = []
    arsenal = []

    cardsPlayedThisTurn = 0
    wizardNAAPlayedThisTurn = 0

    opponent: Opponent = None

    readyToCombo = False

    # Cards the player settings have prevented from being sarsenalled when they otherwise would (e.g. blazng)
    skipArsenal = []

    comboExecuted = False
    stormiesUsed = False
    spellfireUsed = False
    tunicCounters = 0
    resources = 0

    arsenalBlazing = True
    arsenalKindle = True
    playClarity = True
    ipEnergyPotions = True
    ipNonCoreComboPieces = True
    aggressivelyKanoNonBlues = True
    blindKanoOverNodes = True
    usesTunic = False
    
    wentFirst = True
    isOwnTurn = False
    
    def __init__(self):
        self.pitch = 0
        self.damage = 0
        self.turn = 0
        self.ap = 0

        self.amp = 0
    
        self.epots = 0
        self.dpots = 0
        self.cpots = 0

        # self.turnPlayer = "self" if self.wentFirst else "opponent"

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
        
        self.cardsPlayedThisturn = 0
        self.wizardNAAPlayedThisturn = 0
        
        self.isOwnTurn = False
        if(self.assessComboReadiness()):
            print("Choosing to combo.")
            startCombo(self)

            self.comboExecuted = True

        elif(self.opponentForces()):
            print("Opponent has forced combo.")
            # TODO: args
            startCombo(self)
        else:
            pass
            # print("Passing Opponent's turn without issue.")

        return
    
    def opponentForces(self):
        return False

    def playCard(self, card: Card, zone: str | list, **kwargs) -> bool:

        asInstant   = kwargs.get('asInstant', False)
        needsRemove = kwargs.get('removeFromZone', True)
        discard     = kwargs.get('discard', False)
        viaStormies = kwargs.get('stormies', False)

        if zone != "special":
            if isinstance(zone, str):
                zone = self.strToZone(zone)

            # Remove the card from its previous zone
            # Sometimes we don't need to do this, because we're iterating in a way where a list split makes more sense
            if needsRemove:
                zone.pop(zone.index(card))
        
        card.play(self, **kwargs)

        # And put it in the discard
        # Cards generally should manage this themselves
        if(discard):
            self.discard.append(card)
    
    def activateCard(self, card, zone, **kwargs):

        needsRemove = kwargs.get('removeFromZone', True)

        if isinstance(zone, str):
            zone = self.strToZone(zone)

        if needsRemove:
            zone.pop(zone.index(card))

        card.activate(self)

    # Note: this doesn't remove the card from the zone, we just a reference to the card itself
    def getCardFromZone(self, target: str, zone: str | list[Card]) -> Card:
        
        if isinstance(zone, str):
            zone = self.strToZone(zone)

        # if isinstance(target, str):
        for card in zone:
            if card.cardName == target:
                return card
        
        raise Exception(f"Attempted to find {target} in {zone}, but it was missing")
   
    def removeCardFromZone(self, target: str | Card, zone: str | list[Card]) -> Card:
        
        if isinstance(zone, str):
            zone = self.strToZone(zone)

        if isinstance(target, str):
            target = self.getCardFromZone(target, zone)

        # kprint(f"Finding {target} in {zone}")

        return zone.pop(zone.index(target))

    def hasCardInZone(self, targetCardName:str, zone: str | list) -> bool:

        if isinstance(zone, str):
            zone = self.strToZone(zone)

        
        for card in zone:
            if card.cardName == targetCardName:
                return True
        
        return False

    def countCardsInZone(self, targetCardName:str, zone: str | list) -> int:

        count = 0

        if isinstance(zone, str):
            zone = self.strToZone(zone)

        
        for card in zone:
            if card.cardName == targetCardName:
                count += 1
        
        return count

    def playNamedCardFromZone(self, targetCardName:str, zone: str | list) -> bool:

        if isinstance(zone, str):
            zone = self.strToZone(zone)

        for card in zone:
            if card.cardName == targetCardName:
                self.playCard(card, zone)
                return True
        
        return False


    def strToZone(self, zoneName: str) -> list[Card]:
        
        zone = None

        match zoneName:
            case "arsenal":
                zone = self.arsenal
            case "deck":
                zone = self.deck.cards
            case "hand":
                zone = self.hand
            case "banish":
                zone = self.banish
            case "discard":
                zone = self.discard
            case "pitch":
                zone = self.pitch
            case "arena":
                zone = self.arena
            case _:
                raise Exception(f"Attempting to check an invalid card zone {zone}")
            
        return zone

    def pitchCard(self, card, zone, **kwargs):

        # Assume we are either setting up, or combing
        # This is a pretty coarse assumption for now
        # TODO: implement pressure, tempo turns, and aether spindle pitch strategies
        cardRole = "combo" if not self.isOwnTurn else "setup"
        
        # Remove the pitched card from its prior zone
        self.removeCardFromZone(card, zone)
        # And place it into the pitch zone
        self.pitch.append(card)
        
        # Trigger pitch effects for the given card
        card.triggerPitchEffects(self, role=cardRole)
     
        # Return resources gained by this sequence
        self.resources += card.pitch
    
    def assessComboReadiness(self):

        if self.readyToCombo:
            return True

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
        self.turn += 1
        self.ap = 1
        self.resources = 0
        self.pitch = []
        self.cardsPlayedThisturn = 0
        self.wizardNAAPlayedThisturn = 0
        self.isOwnTur = True


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
        
        # At this point we have some cards we'd like to arsenal, some cards we'd ike to block with, and some cards we'd like to pitch
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

            # Only hold a card if we don't already have it in hand or arsenal
            for card in hold:
                allow = True
                if "potion" not in card.cardName:
                    for cardH in cardsToHold:
                        if card.cardName == cardH.cardName:
                            allow = False
                            break 
                    for cardA in self.arsenal:
                        if card.cardName == cardA.cardName:
                            allow = False
                            break 
                if allow:
                    cardsToHold.append(card)
                else:
                    donthold.append(card)

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

            if len(cardsToHold) == 4:
                self.readyToCombo = True
        
        # kprint(f"Hand ({len(self.hand)}), Hold ({len(cardsToHold)})")
        # This ideally won;t be needed, need to check everything else works
        self.hand = cardsToHold

        self.drawUp()
     

            
    def draw(self, num):
        cards = self.deck.draw(num)
        self.hand = self.hand + cards          
    
    def addCardToHand(self, card):
        self.hand.append(card)

    # Draw up to your intellect, while potentially IPing ouselves with some cards
    def drawUp(self, ip = []):
        self.hand = ip if ip else self.hand
        self.draw(self.intellect - len(self.hand))

    # Iterate over cards 
    def iterateCardZone(self, zone, selectFunc, action):
        # Create a copy of the target zone
        executeCards, keepCards = partition(selectFunc, zone)

        for card in executeCards:
            if(action == "play"):
                self.playCard(card, zone)
            if(action == "pitch"):
                self.pitchCard(card, zone)
            elif(action == "activate"):
                self.activateCard(card, zone)

        zone = keepCards
        
    def hasSetupInArsenal(self):
        return any(card.cardName in SetupCards for card in self.arsenal)

    # def amp(self, amount: int) -> int:

    def activateNodes(self):
        if(self.resources < 1):
            raise Exception("Attempting to nodes with 0 resources available.")
        
        self.resources -= 1
        self.amp += 1

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

    def kano2(self) -> Card | None:

        if(self.resources < 3):
            raise Exception("Attempted to kano with insufficient resources")
        self.resources -= 3

        if(len(self.deck.cards) == 0):
            return None
        
        topDeck = flatten(self.deck.opt(1))
        
        # Check if its a card that works with kano's ability
        if(topDeck.cardType != "action"):
            kprint(f"Kano bricked on {topDeck}.", 2)
            self.deck.optBack([topDeck], [])
            return None


        self.banish.append(topDeck)
        return topDeck



# Entry point to the combo
# A kano combo essentially has three phases: seed damage, extensions, finisher
#   This typically takes the form of aether wildfire -> some stuff -> blazing

# We're going to make some huge assumptions in this. 
# First, we will assume the player is successfully able to pitch out all cards and resolve all kindles optimally
# Second, we will assume that the timing of all pitching does not matter, nor does when stormies or crucible enter the stack
# Finally, we will assume the player does not use waning moon, and never leaves a spell on the stack to play another card
# This has a few implications: gaze the ages for example is of very limited use as is (TODO) 

def startCombo(player: Player):
    
    kprint("--- Starting to Combo ---")

    # Gain resources, either through tunic, or spellfire
    if(player.usesTunic and player.tunicCounters == 3):
        kprint("Activating tunic for 1 resource", 1)
        player.resources += 1
        player.tunicCounters = 0
    elif not player.spellfireUsed:
        kprint("Activating spellfire cloak for 1 [r]", 1)
        # TODO: Don't blindly assume spellfire when no tunic
        player.spellfireUsed = True
        player.resources += 1

    # Crack Energy Potions
    numEPots = player.countCardsInZone("Energy Potion", "arena")
    player.iterateCardZone(player.arena, lambda x : x.cardName == "Energy Potion", "activate")
    kprint(f"{numEPots} Energy Potions activated. Player has {player.resources} [r] available", 1)

    # Kindle is a special case, and when played, if another kindle is drawn, will autoplay that kindle too
    # We thus can trust that all kindles have resolved and are gone past this
    player.iterateCardZone(player.hand, lambda x : x.cardName == "Kindle", "play")
    player.iterateCardZone(player.arsenal, lambda x : x.cardName == "Kindle", "play")

    # Our hand + arsenal consists of two types of cards now: resources, and combo pieces
    # Start by pulling out the combo seed
    seed, seedZone = identifyComboSeed(player)

    # While we're not playing the card yet, lets move it out of the way of following analyses
    player.removeCardFromZone(seed, seedZone)

    if seedZone == "arsenal":
        player.stormiesUsed = True
        player.resources -= 1

    # kprint(f"Combo seed identified: {seed}, played from {seedZone}.", 1)


    # Likewise, lets get the finisher
    finish, finishZone = identifyComboFinish(player)
    if finish is not None:
        player.removeCardFromZone(finish, finishZone)

        if finishZone == "arsenal":
            player.stormiesUsed = True
            player.resources -= 1

        # kprint(f"Combo finish identified: {finish}, played from {finishZone}.", 1)
    else: 
        kprint(f"No combo finish found. Let us pray.", 1)


    # Pitch all remaining cards
    # TODO: when we use deja vu potions, gaze, or hail mary topdeck with blue overflow / floodgates they need to be kept here

    statement = f"{len(player.hand)} cards pitched {player.hand}. Player has "
    player.iterateCardZone(player.hand, lambda x : x.pitch > 0, "pitch")
    kprint(statement+ f"{player.resources} [r] available", 1)

    if player.amp > 0:
        kprint(f"Player has amp {player.amp} ready for {seed}.", 1)

    # Work out the resources situation
    spareResources = player.resources
    finishReserveResources = finish.cost
    # Remove resources for seed
    spareResources -= seed.cost
    # Remove resources for finisher
    if finish.cardName == "Lesson in Lava":
        # Special case where lesson needs to be followed by kano blazing
        finishReserveResources += 3
    
    spareResources -= finishReserveResources

    spareResources = kanoExtensions(player, spareResources)
    if spareResources > 0:
        # Crucible
        spareResources -= 1
        player.resources -= 1
        player.amp += 1
        kprint(f"Crucible used to amp 1.", 2)
    
    kprint(f"Combo ready to go off. Seed: {seed} w/ amp {player.amp}, extensions {player.banish}, finish {finish}, with {spareResources} [r] remaining for nodes activations")

    executeCombo(player, seed, finish, spareResources, finishReserveResources)
    


    

def executeCombo(player, seed, finish, spareResources, finishReserveResources):
    kprint(f"Player has {player.resources} resources, of which {spareResources} are free, and {finishReserveResources} are reserved for finisher.", 1)

    # Seed is special
    executeComboPiece(player, seed, "special", spareResources > 0)
    
    # We'll use this to avoid cards we can;t afford
    # For now, nothing spcial in the ordeirng of cards. TODO: later
    idx = 0
    while len(player.banish) > idx:
        card = player.banish[idx]
        # 
        if player.resources - card.cost >= finishReserveResources:
            # kprint(f"Playing {card}")
            executeComboPiece(player, card, "banish", False)
        else:
            # We can't play this card, so lets go to the next
            idx += 1

    executeComboPiece(player, finish, "special", False)


    if len(player.banish):
        kprint(f"{Fore.dark_red_1}Cards left unplayed in banish: {player.banish}.{Style.reset}", 1)
    else:
        kprint(f"{Fore.green}All possible cards played.{Style.reset}", 1)

    if len(player.hand):
        kprint(f"{Fore.dark_red_1}Cards left unpitched in hand: {player.hand}.{Style.reset}", 1)
    else:
        kprint(f"{Fore.green}All possible cards pitched.{Style.reset}", 1)

    if player.resources > 0:
        kprint(f"{Fore.dark_red_1}Player failed to use resources: {player.resources}.{Style.reset}", 1)
    else:
        kprint(f"{Fore.green}All possible pitch used.{Style.reset}", 1)

    kprint(f"Combo dealt {player.arcaneDamageDealt} damage on turn {player.turn}.", 1)



def executeComboPiece(player: Player, card: Card, zone: str | list[Card], useNodes: bool):  
    
    if useNodes:
        kprint(f"Using nodes for spell below this line", 3)
        player.activateNodes()
    
    player.playCard(card, zone, targetPlayer = player.opponent)






def identifyComboSeed(player: Player) -> tuple[Card, str | list[Card]]:

    # Prioritise playing anything we banished luckily, then arsenal cards, and finally cards in hand
    # Note that in special cases of low resources, this may not be correct, and instead we want to ignore arsenal and only use banish and hand cards
    # TODO: consider that special case
    zones = ["arsenal", "banish", "hand"]
    # In the case we're forced to combo, we may not have wilfdire. If so, heres a rough list of cards to play, in order of piroity
    # TODO: Make this controllable
    seeds = ["Aether Wildfire", "Aether Flare", "Sonic Boom", "Open the Flood Gates", "Overflow the Aetherwell", "Aether Spindle"]

    for zone in zones:
        for seed in seeds:
            if zone == "arsenal" and player.stormiesUsed:
                continue
            if player.hasCardInZone(seed, zone):
                return (player.getCardFromZone(seed, zone), zone)
    
    kprint(f"Somewhat direly, we have no combo seed, and instead must die")
    raise Exception("Death and dishnour upon your family, you've tried to combo without a seed card.")

def identifyComboFinish(player: Player) -> tuple[Card, str | list[Card]]:

    # Prioritise playing anything we banished luckily, then arsenal cards, and finally cards in hand
    # Note that in special cases of low resources, this may not be correct, and instead we want to ignore arsenal and only use banish and hand cards
    # TODO: consider that special case
    zones = ["arsenal", "banish", "hand"]
    # In the case we're forced to combo, we may not have Blazing Aether. 
    # TODO: Make this controllable
    seeds = ["Blazing Aether"]

    # Lesson in Lava is a special case, as it isn't the final spell, but instead one that then finds the real finisher
    # However, its only useful as a finisher if there are blazings left
    if player.deck.contains("Blazing Aether"):
        seeds.append("Lesson in Lava")

    for zone in zones:
        for seed in seeds:
            if zone == "arsenal" and player.stormiesUsed:
                continue
            if player.hasCardInZone(seed, zone):
                return (player.getCardFromZone(seed, zone), zone)
    
    kprint(f"We don't like not having a finisher, but raw damage might do the trick!")
    return (None, None)

# Returns how many resources are spare at this point
def kanoExtensions(player: Player, spareResources: int) -> int:
    # kprint(f"Method entry. {spareResources} remaining.") 
    # Kano a few times and lets see what we can add to the combo
    # player.blindKanoOverNodes for now controls whether we would prefer to fish for a 0 cost at 3 resources remaining, or if we'd rather use nodes
    threshold = 3 if player.blindKanoOverNodes else 2

    while spareResources >= threshold:
        # kprint(f"Have {spareResources} resources spare. Kanoing")
        spareResources -= 3
        card = player.kano2()
        if card is None:
            break

        spareResources -= card.cost        

    # kprint(f"Method exit. {spareResources} remaining.") 
    return spareResources

    



    
    



# We're going to make some huge assumptions in this, because otherwise its just too complex to reaosnably write
    # def combo(self):
    #     self.comboExecuted = 1
        
    #     comboHasWildfire = False
    #     comboHasBlazing = False
    #     ragsACard = False
    #     comboCards = []

    #     comboResources = 0



        # TODO: activate one clarity potion to try find a blue to rags off
        # Then, attempt to have a good hit underneath to kano into
        # If we see a top priority red and no blues, we'll kano the red, bottom anything else, then blind the topdeck of clarity again
        



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
