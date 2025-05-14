
from card.onhits import AetherWildfire
from card.surge import Overflow
from src.kanomath.player import Player
from src.kanomath.opponent import Opponent
from src.kanomath.controller import *
# Eventually import argparse for info

from card.potions import EnergyPotion
from card.vanilla import AetherDart

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
    adart = AetherDart(player, "hand")
    overflow = Overflow(player, "hand", colour = "red")
    wildfire = AetherWildfire(player, "hand")

    epot.on_play()
    epot.on_activate()

    print(f"card {epot}, class {epot.cardClass}, type {epot.cardType}, pitch {epot.pitch}")
    print(f"card {adart}, class {adart.cardClass}, type {adart.cardType}, pitch {adart.pitch}, arcane {adart.arcane}")
    print(f"card {overflow}, class {overflow.cardClass}, type {overflow.cardType}, pitch {overflow.pitch}, arcane {overflow.arcane}")
    print(f"card {wildfire}, class {wildfire.cardClass}, type {wildfire.cardType}, pitch {wildfire.pitch}, arcane {wildfire.arcane}")

