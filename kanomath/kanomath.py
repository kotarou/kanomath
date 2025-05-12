from deck import Deck
from player import Player

def main():
    player = Player()

    while(player.deck.cardsLeft and not player.comboExecuted):
        player.simulatePlayerTurn()
        player.simulateOpponentTurn()


main()