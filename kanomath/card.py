class Card:
    name: str
    cost: int
    pitch: int
    deckLimit: int = 3

    cardType: str
    subType: str

    def __init__(self, name, pitch, cardType="action"):
        self.name = name
        self.pitch = pitch
        self.cardType = cardType

    def onPitch():
        return
        
    def play(self, player, **kwargs):

        asInstant = kwargs.get('asInstant', False)

        if(self.cardType == "action" and not asInstant):
            player.ap -= 1

        if(self.name == "Energy Potion"):
            player.epots += 1
        elif(self.name == "Potion of Deja Vu"):
            player.dpots += 1
        elif(self.name == "Potion of Deja Vu"):
            player.dpots += 1
        
        return

    def onResolve():
        return
