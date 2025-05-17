import kanomath.cards as card
from kanomath.functions import create_card_in_zone
from kanomath.player import Player
import pytest


class TestCard2:

    # player: Player
    
    def test_creating_cards(self):

        player = Player()

        # Test the direct creation of a potion, a card with multiple predefined properties
        epot = card.EnergyPotion(player, "arena")
        assert epot.pitch == 3
        assert epot.colour == "blue"
        assert epot.block == 0
        assert epot.zone == "arena"
        assert epot.card_name == "Energy Potion"
        assert epot.card_name_short == "epot"

        # Test creating a card in a zone
        dpot = create_card_in_zone(card.DejaVuPotion, player, "arena")
        assert dpot.pitch == 3
        assert dpot.zone == "arena"
        assert dpot.card_name == "Potion of Deja Vu"
        assert player.arena.contains_card(dpot)
        
        dpot2 = create_card_in_zone(card.DejaVuPotion, player, "hand")
        assert dpot2.zone == "hand"
        assert player.hand.contains_card(dpot2)

        # Test the creation of aether wildfire, a majestic with only one version
        wildfire = card.AetherWildfire(player, "hand")
        assert wildfire.pitch == 1
        assert wildfire.colour == "red"
        assert wildfire.block == 3
        assert wildfire.zone == "hand"

        # Test the creation of a card that has a default pitch assumption (in this case, red)
        cindering = card.CinderingForesight(player, "arsenal")
        assert cindering.pitch == 1
        assert cindering.colour == "red"
        assert cindering.block == 2
        assert cindering.zone == "arsenal"

        # Test the creation of card with non-default colour shorthand used
        cindering = card.CinderingForesight(player, "arsenal", "y")
        assert cindering.pitch == 2
        assert cindering.colour == "yellow"

       # Test the creation of card with non-default colour
        cindering = card.CinderingForesight(player, "arsenal", "blue")
        assert cindering.pitch == 3
        assert cindering.colour == "blue"

    def test_activating_cards(self):

        player = Player()

        # Test the activation of an energy potion from hand
        epot = create_card_in_zone(card.EnergyPotion, player, "arena")
        epot.activate()

        assert player.pitch_floating == 2
        assert not player.arena.contains_card(epot)
        assert player.discard.contains_card(epot)

        # Test we're absolutely not allowed to reactivate a potion
        with pytest.raises(Exception) as error_info:
            epot.activate()
        assert "invalid zone" in str(error_info.value)

        # Test we're not allowed to activate a potion from hand
        dpot = create_card_in_zone(card.DejaVuPotion, player, "hand")
        with pytest.raises(Exception) as error_info:
            dpot.activate()
        assert "invalid zone" in str(error_info.value)