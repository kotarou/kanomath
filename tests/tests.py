from kanomath.player import Player
from kanomath.card import Card
import pytest

class TestArsenal:

    player: Player
    
    def test_action_spell(self):
        self.player = Player()
        self.player.arsenal = [Card("Zap", 3, "action")]
        
        directResult = self.player.playNamedCardFromZone("Zap", "arsenal")
        playerTrackingResult = self.player.cardsPlayedThisTurn == 1
        cardEnteredDiscard = self.player.hasCardInZone("Zap", "discard")
        cardInArsenal = self.player.hasCardInZone("Zap", "arsenal")

        assert directResult
        assert playerTrackingResult
        assert cardEnteredDiscard
        assert not cardInArsenal

    
    




     
# Card("Energy Potion", 3, "action"),
# Card("Potion of Deja Vu", 3, "action"),
# Card("Kindle", 1, "instant"),