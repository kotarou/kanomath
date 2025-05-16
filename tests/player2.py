import kanomath.cards as card
from kanomath.player2 import Player2
import pytest

from kanomath.zones import Deck


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

        player.hand.seed_with_cards([
            card.AetherWildfire(player, "test"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b")
        ])

        assert player.hand.contains_card_name("Aether Wildfire")
        assert player.hand.contains_card_name("Zap")
        assert not player.hand.contains_card_name("Blazing Aether")

        player.arsenal.seed_with_cards([
            card.BlazingAether(player, "test"),
        ])

        assert player.arsenal.contains_card_name("Blazing Aether")
        assert not player.arsenal.contains_card_name("Aether Wildfire")

        player.braino.turn_evaluate_state()

        assert player.braino.wf_hand
        assert player.braino.blazing_arsenal
        
        assert not player.braino.wf_arsenal
        assert not player.braino.wf_banish
        assert not player.braino.blazing_hand
        assert not player.braino.blazing_banish
        assert not player.braino.lesson_arsenal
        assert not player.braino.lesson_banish
        assert not player.braino.lesson_hand

        assert player.braino.has_wf
        assert player.braino.has_blazing
        assert not player.braino.has_lesson

        assert player.braino.hand_usable_pitch == 9


        player.arsenal.seed_with_cards([
            card.AetherWildfire(player, "test"),
        ])
        player.braino.turn_evaluate_state()

        assert player.braino.hand_usable_pitch == 9

        player.hand.seed_with_cards([
            card.AetherWildfire(player, "test"),
            card.BlazingAether(player, "test"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b")
        ])
        player.braino.turn_evaluate_state()

        # Test the player correctly recognizes that the second wildfire in hand is pitchable, but the blazing still is not
        assert player.braino.wf_arsenal 
        assert (player.braino.wf_arsenal or player.braino.wf_banish) 
        assert (player.braino.has_blazing or player.braino.has_lesson)
        assert not player.braino.wf_hand

        assert player.braino.hand_usable_pitch == 7

        # # Has aether wildfire to begin combo
        # self.wf_hand    = self.player.hand.contains_card("Aether Wildfire")
        # self.wf_arsenal = self.player.arsenal.contains_card("Aether Wildfire")
        # self.wf_banish  = self.player.banish.contains_card("Aether Wildfire")
        # self.has_wf     = self.wf_hand or self.wf_arsenal or self.wf_banish # self.has_wf = self.player.access_to_card_name("Aether Wildfire")
        
        # # Has finisher to end combo
        # self.blazing_hand    = self.player.hand.contains_card("Blazing Aether")
        # self.blazing_arsenal = self.player.arsenal.contains_card("Blazing Aether")
        # self.blazing_banish  = self.player.banish.contains_card("Blazing Aether")
        # self.has_blazing     = self.blazing_hand or self.blazing_arsenal or self.blazing_banish

        # # Has lesson to finiid combo finisher
        # self.lesson_hand    = self.player.hand.contains_card("Lesson in Lava")
        # self.lesson_arsenal = self.player.arsenal.contains_card("Lesson in Lava")
        # self.lesson_banish  = self.player.banish.contains_card("Lesson in Lava")
        # self.has_lesson     = self.lesson_hand or self.lesson_arsenal or self.lesson_banish

        # #   - Opportunistically looking for potions to extend combo
        # self.num_epots = self.player.arena.count_cards_name("epot")
        # self.num_dpots = self.player.arena.count_cards_name("dpot")
        # self.num_cpots = self.player.arena.count_cards_name("cpot")

        # # How many cards does the player want to draw
        # self.count_kindles = self.player.count_combo_access_card("Kindle", allow_banish = False)

        # self.topdeck_actions = []


    def test_opt_setup_potions(self):

        player = Player2()

        player.deck.seed_with_cards([           
            card.AetherArc(player, "test"),
            card.EnergyPotion(player, "test"),
            card.SonicBoom(player, "test"),
            card.AetherDart(player, "test", "b"),
            card.AetherQuickening(player, "test", "b"),
        ])

        deck_test_size = player.deck.size

        player.hand.seed_with_cards([
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b")
        ])

        player.arsenal.seed_with_cards([
            card.BlazingAether(player, "test"),
        ])

        player.braino.turn_evaluate_state()
        assert player.braino.state == "setup"
        # In this case, the player should have opted the enregy potion to top and the two blues to bottom in an order we don't care about
        # They remain in setup because we want that energy potion
        player.opt(3)

        assert player.deck.cards[0].card_name == "Energy Potion"
        assert player.deck.cards[1].card_name == "Aether Dart"
        assert player.braino.state == "setup"
        assert player.braino.topdeck_actions[0] == "kano"

    def test_opt_setup_switch_combo(self):
        
        player = Player2()

        player.deck.seed_with_cards([           
            card.AetherWildfire(player, "test"),
            card.AetherArc(player, "test"),
            card.SonicBoom(player, "test"),
            card.EnergyPotion(player, "test"),
            card.AetherDart(player, "test", "b"),
            card.AetherQuickening(player, "test", "b"),
        ])

        deck_test_size = player.deck.size

        player.hand.seed_with_cards([
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b"),
            card.Zap(player, "test", "b")
        ])

        player.arsenal.seed_with_cards([
            card.BlazingAether(player, "test"),
        ])

        player.braino.turn_evaluate_state()

        assert player.braino.state == "setup"

        # In this case, the player should have opted the WF to bottom, and left the Aether Arc on top, as they are finshing for potions
        # However, as they've seen what they need to go off, they should switch to a ready to combo state
        player.opt(2)
        assert player.deck.cards[0].card_name == "Aether Wildfire"
        assert player.deck.cards[1].card_name == "Aether Arc"

        assert player.braino.topdeck_actions[0] == "kano"
        assert player.braino.topdeck_actions[1] == "draw"

        assert player.deck.size == deck_test_size
        assert player.braino.state == "topdeck_combo"