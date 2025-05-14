
from src.kanomath.player import Player
from src.kanomath.opponent import Opponent
from src.kanomath.controller import *
# Eventually import argparse for info

from card.potions import EnergyPotion

if __name__ == "__main__":
    
    player: Player = Player()
    # opponent: Opponent = Opponent()

    # setupGame(player, opponent)

    # # TODO: Manage first turn of game

    # while(player.deck.cardsLeft and not player.comboExecuted and player.turn < 20):
    #     player.simulatePlayerTurn()
    #     cleanUpTurn(player, opponent)
        
    #     player.simulateOpponentTurn()
    #     cleanUpTurn(player, opponent)

    epot = EnergyPotion(player, "arena")

    epot.play()
    epot.activate()

    print(epot)
    print(epot.cardClass)
    print(epot.cardType)
    print(epot.pitch)
    print(epot.block)
