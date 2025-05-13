from kanomath.player import Player
from kanomath.card import Card
import pytest

class TestCardEffects:

    # player: Player
    
    def test_arsenal(self):
        player = Player()
        player.arsenal = [Card("Zap", 3, "action")]
        
        # Test the card reports as played
        assert player.playNamedCardFromZone("Zap", "arsenal")

        # Test the player tracked the card as played
        assert player.cardsPlayedThisTurn == 1

        # Test the card correctly went to discard
        assert player.hasCardInZone("Zap", "discard")

        # Test the card is no longer in arsenal
        assert not player.hasCardInZone("Zap", "arsenal")

        player.arsenal = [Card("Zap", 3, "action"), Card("Zap", 3, "action")]
        player.discard = []
        player.playNamedCardFromZone("Zap", "arsenal")

        # Test that, when two identical cards are in arsenal, only one is played
        assert player.hasCardInZone("Zap", "arsenal")
        assert player.hasCardInZone("Zap", "discard")


    def test_arena(self):
        player = Player()
        player.arena = [  
            Card("Potion of Deja Vu", 3, "action"), 
            Card("Clarity Potion", 3, "action")
        ]

        player.hand = [Card("Energy Potion", 3, "action"), Card("Energy Potion", 3, "action"), Card("Clarity Potion", 3, "action")]

        # Test the card reports as played
        assert player.playNamedCardFromZone("Energy Potion", "hand")

        # Test the potion arrived in the arena
        assert player.hasCardInZone("Energy Potion", "arena")
        assert player.hasCardInZone("Energy Potion", player.arena)

        # Test the potion did not go to discard
        assert not player.hasCardInZone("Energy Potion", "discard")

        # Test we have exactly one energy potion left in hand
        assert sum(card.cardName == "Energy Potion" for card in player.hand) == 1

        player.resources = 0
        player.iterateCardZone(player.arena, lambda x : x.cardName == "Energy Potion", "activate")

        # Test cracking an epot gave us resources
        assert player.resources == 2

        # Test it went to discard
        assert player.hasCardInZone("Energy Potion", "discard")
        assert not player.hasCardInZone("Energy Potion", "arena")

        # Ensure we didn't activate anything else
        assert player.hasCardInZone("Potion of Deja Vu", "arena")
        assert player.hasCardInZone("Clarity Potion", "arena")

    




     
# Card("Energy Potion", 3, "action"),
# Card("Potion of Deja Vu", 3, "action"),
# Card("Kindle", 1, "instant"),