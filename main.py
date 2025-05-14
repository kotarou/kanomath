
from cards.onhits import AetherWildfire
from cards.other import CinderingForesight
from cards.surge import Overflow
from src.kanomath.player import Player
from src.kanomath.opponent import Opponent
from src.kanomath.controller import *
# Eventually import argparse for info

from cards.potions import EnergyPotion
from cards.vanilla import AetherDart

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
    cindering = CinderingForesight(player, "hand")

    epot.on_play()
    epot.on_activate()

    for card in [epot, adart, overflow, wildfire, cindering]:
        print(f"card {card}, class {card.cardClass}, type {card.cardType}, pitch {card.pitch}, block: {card.block}")

