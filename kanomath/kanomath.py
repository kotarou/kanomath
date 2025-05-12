from deck import Deck
from player import Player

def main():
    player = Player()

    while(player.deck.cardsLeft and not player.comboExecuted and player.turn < 20):
        player.simulatePlayerTurn()
        player.simulateOpponentTurn()


main()