from kanomath.player2 import Player2
import pytest


class TestCard2:

    # player: Player
    
    def test_creating_player(self):

        player = Player2()
        assert player.hand is not None
        assert player.action_points == 0
        assert player.arsenal.capacity == 1

        # # Sanity Check
        # if self.use_spellfire and self.use_tunic:
        #     self.use_tunic = False
