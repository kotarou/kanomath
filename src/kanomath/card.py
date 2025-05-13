from colored import Fore, Style
from .util import kprint, flatten
# from enum import Enum

# class Color(Enum):
#     RED = 1
#     YELLOW = 2
#     BLUE = 3

class Card:
    cardName: str
    cost: int
    pitch: int
    deckLimit: int = 3

    cardType: str
    subType: str

    
    arcaneDamage: int

    @property
    def doesArcane(self) -> bool:
        # TODO: blazing aether, scour
        return self.arcaneDamage > 0




    def __str__(self):
        match self.pitch:
            case 0:
                return f"{Fore.grey}{self.cardName}{Style.reset}"
            case 1:
                return f"{Fore.red}{self.cardName} ({self.pitch}){Style.reset}"
            case 2:
                return f"{Fore.yellow}{self.cardName} ({self.pitch}){Style.reset}"
            case 3:
                return f"{Fore.blue}{self.cardName} ({self.pitch}){Style.reset}"                
            case _:
                return f"{self.cardName} ({self.pitch}){Style.reset}"

    def __repr__(self):
        return self.__str__()

    def __init__(self, name, pitch, cost, **kwargs):

        self.cardType       = kwargs.get("cardType", "action")
        self.arcaneDamage   = kwargs.get("arcane", 0)

        self.cardName = name
        self.pitch = pitch
        self.cost = cost

    def triggerPitchEffects(self, player, **kwargs):
        role = kwargs.get('role', False)

        # TODO: role of setup kano
        # TODO: role of combo

        if(self.cardName == "Will of Arcana"):
            player.amp += 1

        elif(self.cardName == "Eye of Ophidia"):
            # Eye is pretty complex, and this behaviour can be improved
            # For now, bottom anything that isn't a combo piece or potion

            optCards = player.deck.opt(2)
            top = []
            bottom = []

            if(role == "setup"):
                for optcard in optCards:
                    if(optcard.cardName in SetupCards.keys() or optcard.cardName in ComboCoreCards.keys()):
                        if(optcard.cardType == "action"):
                            top.append(optcard)
                    else:
                        bottom.append(optcard)
                # Potions > combo pieces > other
                if(len(top)):
                    top.sort(key=sortKanoSetupPriority)
                
                kprint(f"Opting with Eye. Saw: {optCards}, Top: {top}, Bottom: {bottom}", 2)
                player.deck.optBack(top, bottom)

            if(role == "combo"):
                player.deck.optBack(optCards, [])



        return
        
    def play(self, player, **kwargs):

        asInstant       = kwargs.get('asInstant', False)
        targetPlayer    = kwargs.get('targetPlayer', None)

        if(player.resources < self.cost):
            kprint(f"Cannot pay for {self}'s resource cost ({self.cost}) with {player.resources}")
            return 

        player.resources -= self.cost


        if(self.cardType == "action" and not asInstant):
            player.ap -= 1

        if(self.cardName == "Energy Potion"):
            player.epots += 1
        elif(self.cardName == "Potion of Deja Vu"):
            player.arena.append(self) 
            player.dpots += 1
        elif(self.cardName == "Clarity Potion"):
            player.arena.append(self) 
            player.cpots += 1

        # 
        if("Potion" in self.cardName):
            player.arena.append(self) 
        elif(self.cardName == "Gaze The Ages"):
            # TODO: Simulate Gaze going back to hand
            # if(player.gazeActivated) etc
            player.discard.append(self)
            pass
        else:
            player.discard.append(self)


        if(self.cardName == "Kindle"):
            player.amp += 1
            topDeck = flatten(player.deck.draw(1))
            
            kprint(f"Playing {self}, amping 1, and drawing {topDeck}", 1)

            if(topDeck.cardName == "Kindle"):
                topDeck.play(player, **kwargs)
            else:
                player.addCardToHand(topDeck)

        

        # Handle arcane damage
        # Slightly hacky approach, but this lets us determine blazing damage 
        arcaneToDeal = self.arcaneDamage
        dealsArcane = self.doesArcane
        # kprint(f"Target of {self} is {targetPlayer}")
        if targetPlayer is not None:

            if self.cardName == "Blazing Aether" and player.arcaneDamageDealt > 0:
                dealsArcane = True
                arcaneToDeal = player.arcaneDamageDealt

            if dealsArcane:
                arcaneToDeal = arcaneToDeal + player.amp + player.wildfireAmp
                player.amp = 0

                targetPlayer.registerDamage(arcaneToDeal, self)

                damageDealt =  targetPlayer.lastHit

                if self.cardName == "Aether Wildfire":
                    kprint(f"{self} hit, amping all spells by {damageDealt}", 2)
                    player.wildfireAmp = damageDealt
                elif self.cardName == "Aether Flare":
                    kprint(f"{self} hit, amping the next spell by {damageDealt}", 2)
                    player.amp = damageDealt
                elif self.cardName == "Overflow the Aetherwell":
                    kprint(f"{self} hit for {damageDealt}. Surge gain 2 [r].", 2)
                    if damageDealt > self.arcaneDamage:
                        player.resources += 2
                elif self.cardName == "Open the Flood Gates":
                    kprint(f"{self} hit for {damageDealt}. Surge draw 2 cards", 2)
                    if damageDealt > self.arcaneDamage:
                        player.draw(2)
                else:
                    kprint(f"{self} dealt {damageDealt} damage.", 2)

                player.arcaneDamageDealt += damageDealt

        player.cardsPlayedThisTurn += 1
        return 

    def activate(self, player):

        if(self.cardName == "Energy Potion"):
            player.resources += 2

        player.discard.append(self)

        return

SetupCards = {
    "Energy Potion": 2,
    "Potion of Deja Vu": 4,
    "Clarity Potion": 10
}

ComboCoreCards = {
    "Aether Wildfire": 1,
    "Blazing Aether": 4,
    "Kindle": 6,
}

ComboExtensionCards = {
    "Kindle": 4,
    "Overflow the Aetherwell": 6,
    "Open the Flood Gates": 6,
    "Aether Flare": 8,
}

def sortArsenalPlayPriority(card):
    if(card.cardName in SetupCards.keys()):
        return SetupCards[card.cardName]   
    return 0

def sortKanoSetupPriority(card):
    name = card.cardName
    if(name in SetupCards.keys()):
        return SetupCards[name]
    elif(name in ComboCoreCards.keys()):
        return 10 + ComboCoreCards[name]
    return 0

def sortArsenalPriority(card):
    name = card.cardName
    if(name in ComboCoreCards.keys()):
        return ComboCoreCards[name]
    # elif(name in ComboExtensionCards.keys()):
    #     return 10 + ComboExtensionCards[name]
    elif(name in SetupCards.keys()):
        return 20 + SetupCards[name]   
    return 0

def sortSetupPlayPriority(card):
    if(card.cardName in SetupCards.keys()):
        return SetupCards[card.cardName]   
    return 0