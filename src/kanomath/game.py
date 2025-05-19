from loguru import logger
import kanomath.cards as card
# from kanomath.functions import move_card_to_zone
from kanomath.opponent import Opponent
from kanomath.player import Player
from kanomath.zones import Zone

class Game:

    current_turn: int
    player_goes_first: bool
    player_num_turns: int = 0

    player: Player
    opponent: Opponent

    @property
    def game_should_continue(self) -> bool:
        return self.player.braino.state != "combo" and self.player_num_turns < 10 and self.player.deck.size > 1

    def __init__(self):
        pass

    def setup_game(self):
        self.player = Player()
        self.opponent = Opponent()

        self.player.deck.seed_with_cards([
            card.AetherFlare(self.player, "test", "red"),
            card.AetherFlare(self.player, "test", "red"),
            card.AetherFlare(self.player, "test", "red"),

            card.AetherSpindle(self.player, "test", "red"),
            card.AetherSpindle(self.player, "test", "red"),
            card.AetherSpindle(self.player, "test", "red"),
            
            card.AetherWildfire(self.player, "test"),
            card.AetherWildfire(self.player, "test"),
            card.AetherWildfire(self.player, "test"),

            card.BlazingAether(self.player, "test"),
            card.BlazingAether(self.player, "test"),
            card.BlazingAether(self.player, "test"),

            # TODO: logic for this card is annoying AF           
            # card.CinderingForesight(self.player, "test", "red"),
            # card.CinderingForesight(self.player, "test", "red"),

            card.Kindle(self.player, "test"),
            card.Kindle(self.player, "test"),
            card.Kindle(self.player, "test"),

            card.Overflow(self.player, "test", "red"),
            card.Overflow(self.player, "test", "red"),
            card.Overflow(self.player, "test", "red"),

            card.LessonInLava(self.player, "test"),
            card.LessonInLava(self.player, "test"),
            card.LessonInLava(self.player, "test"),

            card.Overflow(self.player, "test", "yellow"),
            card.Overflow(self.player, "test", "yellow"),
            card.Overflow(self.player, "test", "yellow"),

            card.AetherArc(self.player, "test"),
            card.AetherArc(self.player, "test"),
            card.AetherArc(self.player, "test"),

            card.ArcaneTwining(self.player, "test", "blue"),
            card.ArcaneTwining(self.player, "test", "blue"),
            card.ArcaneTwining(self.player, "test", "blue"),

            card.DestructiveAethertide(self.player, "test"),
            card.DestructiveAethertide(self.player, "test"),
            card.DestructiveAethertide(self.player, "test"),

            card.EnergyPotion(self.player, "test"),
            card.EnergyPotion(self.player, "test"),
            card.EnergyPotion(self.player, "test"),

            card.EyeOfOphidia(self.player, "test"),

            card.GazeTheAges(self.player, "test"),
            card.GazeTheAges(self.player, "test"),
            card.GazeTheAges(self.player, "test"),

            card.FloodGates(self.player, "test", "blue"),
            card.FloodGates(self.player, "test", "blue"),
            card.FloodGates(self.player, "test", "blue"),

            card.Overflow(self.player, "test", "blue"),
            card.Overflow(self.player, "test", "blue"),
            card.Overflow(self.player, "test", "blue"),

            card.PopTheBubble(self.player, "test", "blue"),
            card.PopTheBubble(self.player, "test", "blue"),
            card.PopTheBubble(self.player, "test", "blue"),

            card.DejaVuPotion(self.player, "test"),
            card.DejaVuPotion(self.player, "test"),

            card.Prognosticate(self.player, "test", "blue"),
            card.Prognosticate(self.player, "test", "blue"),
            card.Prognosticate(self.player, "test", "blue"),

            card.Sap(self.player, "test", "blue"),
            card.Sap(self.player, "test", "blue"),
            card.Sap(self.player, "test", "blue"),

            card.WillOfArcana(self.player, "test"),
        ])

        self.player.deck.shuffle()
        self.player.hand.draw_up()

        # For now
        # TODO: alternate, and track differences
        self.player_goes_first = True
    
    def run_game_machine(self):

        if self.player_goes_first:
            self.run_first_turn(self.player)
        else:
            self.run_first_turn(self.opponent)
            self.run_player_turn()
    
        while self.game_should_continue:
            self.run_opponent_turn(False)
            self.run_player_turn()

        logger.system(f"Game reached endstate {self.player.braino.state} on turn {self.player_num_turns}, with {self.player.deck.size} cards left in deck.")


            
            


        # Begin with the first turn, which is slightly unusual

    def run_first_turn(self, turn_player: Player | Opponent):

        # logger.info("Running first turn.")

        if turn_player.id == "player":

            # self.player.braino.evaluate_state()
            # self.player.braino.cycle_make_initial_decisions()

            self.run_player_turn(True)
            # TODO: Opponent draw up
        else:
            self.run_opponent_turn(True)
            # TODO: Player draw up
        # self.cleanup_turn()    


    def run_opponent_turn(self, game_first_turn):

        # logger.info("-----")
        # logger.info(f"Running opponent turn. Hand: {self.player.hand}, Arsenal: {self.player.arsenal} ")

        # self.player.braino.evaluate_state()
        # self.player.braino.cycle_make_initial_decisions()
        
        self.player.play_opponent_turn(game_first_turn)
        # self.cleanup_turn()

    
    def run_player_turn(self, game_first_turn: bool = False):

        # logger.info(f"Running player turn. Hand: {self.player.hand}. Arsenal: {self.player.arsenal}. Arena: {self.player.arena}")

        self.player_num_turns += 1

        # self.player.braino.evaluate_state()
        self.player.play_own_turn(game_first_turn)
        
    #     self.cleanup_turn()



    # def cleanup_turn(self):        
        
    #     # At the end, clean up the player's banish
    #     # TODO: This should be a method on player, seeing as it assumes the same owner and all
    #     # move_cards_between_zones(self.player, "banish", "exile")

    #     for idx in reversed(range(self.player.banish.size)):
    #         card = self.player.banish.cards[idx]

    #         Zone.move_card_to_zone(card, "exile")

        
