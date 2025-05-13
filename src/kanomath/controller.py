from .player import Player
from .opponent import Opponent

def cleanUpTurn(player: Player, opponent: Opponent):
    
    # Clean up resources
    player.resources = 0
    player.ap = 0
    player.amp = 0
    
    # Cards previously banished go to "exile", which is just a fancy name for "banished and no longer touchable for purposes"
    # This is easier than tracking if a card in banish is playable or not this turn: we assume all are
    player.exile.extend(player.banish) 
    player.banish = []
    
    player.deck.optBack([], player.pitch)
    player.pitch = []

    player.isOwnTurn = False


