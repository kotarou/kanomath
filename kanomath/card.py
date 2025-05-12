from colored import Fore, Style
from util import partition, kprint
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

    def __init__(self, name, pitch, cardType="action"):
        self.cardName = name
        self.pitch = pitch
        self.cardType = cardType

    def triggerPitchEffects(self, player, **kwargs):
        role = kwargs.get('role', False)

        # TODO: role of setup kano
        # TODO: role of combo

        if(self.cardName == "will of Arcana"):
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
                        top.append(optcard)
                    else:
                        bottom.append(optcard)
                # Potions > combo pieces > other
                if(len(top)):
                    top.sort(key=sortKanoSetupPriority)
                
                # output += f"(opting top({len(top)}), bottom({len(bottom)})) "
                kprint(f"Opting with Eye. Top: {top}, Bottom: {bottom}", 2)
                player.deck.optBack(top, bottom)

            if(role == "combo"):
                player.deck.optBack(optCards, [])



        return
        
    def play(self, player, **kwargs):

        asInstant = kwargs.get('asInstant', False)

        if(self.cardType == "action" and not asInstant):
            player.ap -= 1

        if(self.cardName == "Energy Potion"):
            player.epots += 1
        elif(self.cardName == "Potion of Deja Vu"):
            player.dpots += 1
        elif(self.cardName == "Clarity Potion"):
            player.cpots += 1
        elif(self.cardName == "Kindle"):
            player.amp += 1
            # We assume all kindles are optimally resolved
            player.draw(1)

        return

    def onResolve():
        return

SetupCards = {
    "Energy Potion": 10,
    "Potion of Deja Vu": 8,
    "Clarity Potion": 2
}

ComboCoreCards = {
    "Aether Wildfire": 10,
    "Blazing Aether": 8,
    "Kindle": 3,
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
        return 50 + SetupCards[name]
    elif(name in ComboCoreCards.keys()):
        return 30 + ComboCoreCards[name]
    return 0

def sortArsenalPriority(card):
    name = card.cardName
    if(name in ComboCoreCards.keys()):
        return 50 + ComboCoreCards[name]
    elif(name in ComboExtensionCards.keys()):
        return 30 + ComboExtensionCards[name]
    elif(name in SetupCards.keys()):
        return 20 + SetupCards[name]   
    return 0

def sortSetupPlayPriority(card):
    if(card.cardName in SetupCards.keys()):
        return SetupCards[card.cardName]   
    return 0