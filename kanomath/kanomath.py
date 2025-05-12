from deck import Deck
from player import Player

def main():
    player = Player()

    while(len(player.deck.cards)):
        player.simulatePlayerTurn()
        player.simulateOpponentTurn()


main()