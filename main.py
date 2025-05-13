from src.kanomath.player import Player
from src.kanomath.opponent import Opponent
from src.kanomath.controller import *
# Eventually import argparse for info


if __name__ == "__main__":
    
    player: Player = Player()
    opponent: Opponent = Opponent()

    # TODO: Manage first turn of game

    while(player.deck.cardsLeft and not player.comboExecuted and player.turn < 20):
        player.simulatePlayerTurn()
        cleanUpTurn(player, opponent)
        
        player.simulateOpponentTurn()
        cleanUpTurn(player, opponent)