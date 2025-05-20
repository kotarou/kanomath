from kanomath.game import Game

from loguru import logger
import sys
from functools import partialmethod
from typing import TYPE_CHECKING

# Eventually import argparse for info

def setup():
    
    logger_format = (
    # "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        # "<cyan>{function}</cyan>:"
        "<cyan>{name: <15}</cyan>:<cyan>{line}</cyan> | "
        # "<level>{message}</level>"
        "{message}"
    )

    logger.remove(0) # remove the default handler configuration
    logger.add(sys.stdout, level="DEBUG", serialize=False, format=logger_format)
    logger.level("DEBUG", color="<dim><white>")
    
    logger.level("action", no=15, color="<light-cyan>", icon="A")
    logger.level("effect", no=15, color="<light-blue>", icon="E")
    logger.level("decision", no=15, color="<light-green>", icon="D")
    logger.level("system", no=15, color="<magenta>", icon="D")


    logger.__class__.action = partialmethod(logger.__class__.log, "action")
    logger.__class__.effect = partialmethod(logger.__class__.log, "effect") 
    logger.__class__.decision = partialmethod(logger.__class__.log, "decision") 
    logger.__class__.system = partialmethod(logger.__class__.log, "system")


if __name__ == "__main__":
    
    setup()

 

    game: Game  = Game()

    game.setup_game()

    game.run_game_machine()


