from kanomath.game import Game
from src.kanomath.player import Player
from src.kanomath.opponent import Opponent
from src.kanomath.controller import *
# Eventually import argparse for info

# from src.kanomath.cards import EnergyPotion, AetherDart, AetherWildfire, CinderingForesight, Overflow

if __name__ == "__main__":
    
    # player: Player = Player()
    # opponent: Opponent = Opponent()

    # setupGame(player, opponent)

    # # TODO: Manage first turn of game

    # while(player.deck.cardsLeft and not player.comboExecuted and player.turn < 20):
    #     player.simulatePlayerTurn()
    #     cleanUpTurn(player, opponent)
        
    #     player.simulateOpponentTurn()
    #     cleanUpTurn(player, opponent)

    game: Game  = Game()

    game.setup_game()

    game.run_game_machine()


