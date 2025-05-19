from kanomath.game import Game

from loguru import logger
import sys
from functools import partialmethod
from typing import TYPE_CHECKING

# Eventually import argparse for info


if __name__ == "__main__":
    
    logger_format = (
    # "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        # "<cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        # "<level>{message}</level>"
        "{message}"
    )

    logger.remove(0) # remove the default handler configuration
    logger.add(sys.stdout, level="DEBUG", serialize=False, format=logger_format)

    logger.level("action", no=15, color="<light-cyan>", icon="A")
    logger.level("effect", no=15, color="<light-blue>", icon="E")

    logger.__class__.action = partialmethod(logger.__class__.log, "action")
    logger.__class__.effect = partialmethod(logger.__class__.log, "effect") 

    # setattr(logger, 'action', partialmethod(logger.__class__.log, "action"))


    # def action(self, input: str):
    #     logger.log("ACTION", input)

    # logger.action = types.MethodType(action, logger) # type: ignore

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


