from .player import Player
from .opponent import Opponent

def setupGame(player: Player, opponent: Opponent):
    player.opponent = opponent

def cleanUpTurn(player: Player, opponent: Opponent):
    
    # Clean up resources
    player.resources = 0
    player.comboResourcesAllocated = 0
    player.comboResourcesSpare = 0

    player.ap = 0
    player.amp = 0
    player.wildfireAmp = 0
    player.arcaneDamageDealt = 0
    
    player.wizardNAAPlayedThisTurn = 0
    player.cardsPlayedThisTurn = 0

    # Cards previously banished go to "exile", which is just a fancy name for "banished and no longer touchable for purposes"
    # This is easier than tracking if a card in banish is playable or not this turn: we assume all are
    player.exile.extend(player.banish) 
    player.banish = []
    
    player.deck.optBack([], player.pitch)
    player.pitch = []

    player.isOwnTurn = False


