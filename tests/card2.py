from kanomath.cards.other import CinderingForesight
from kanomath.cards.onhits import AetherWildfire
from kanomath.cards.potions import EnergyPotion
from kanomath.player import Player
import pytest


class TestCard2:

    # player: Player
    
    def test_creating_cards(self):

        player = Player()

        # Test the creation of a potion, a card with multiple predefined properties
        epot = EnergyPotion(player, "arena")
        assert epot.pitch == 3
        assert epot.colour == "blue"
        assert epot.block == 0
        assert epot.zone == "arena"

        # Test the creation of aether wildfire, a majestic with only one version
        wildfire = AetherWildfire(player, "hand")
        assert wildfire.pitch == 1
        assert wildfire.colour == "red"
        assert wildfire.block == 3
        assert wildfire.zone == "hand"

        # Test the creation of a card that has a default pitch assumption (in this case, red)
        cindering = CinderingForesight(player, "arsenal")
        assert cindering.pitch == 1
        assert cindering.colour == "red"
        assert cindering.block == 2
        assert cindering.zone == "arsenal"

        # Test the creation of card with non-default colour shorthand used
        cindering = CinderingForesight(player, "arsenal", "y")
        assert cindering.pitch == 2
        assert cindering.colour == "yellow"

       # Test the creation of card with non-default colour
        cindering = CinderingForesight(player, "arsenal", "blue")
        assert cindering.pitch == 3
        assert cindering.colour == "blue"