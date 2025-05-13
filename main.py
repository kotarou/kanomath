from src.kanomath import Player
# Eventually import argparse for info


if __name__ == "__main__":
    
    player: Player = Player()

    while(player.deck.cardsLeft and not player.comboExecuted and player.turn < 20):
        player.simulatePlayerTurn()
        player.simulateOpponentTurn()