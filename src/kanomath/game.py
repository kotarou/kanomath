from kanomath.functions import move_cards_between_zones, move_cards_to_zone
from kanomath.opponent import Opponent
from kanomath.player2 import Player2


class Game:

    current_turn: int
    player_goes_first: bool
    player_num_turns: int = 0

    player: Player2
    opponent: Opponent

    @property
    def game_should_continue(self) -> bool:
        # TODO: opponent or player dead
        return True

    def __init__(self):
        pass

    def setup_game(self):
        self.player = Player2()
        self.opponent = Opponent()


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
            self.run_opponent_turn()
            self.run_player_turn()


        # Begin with the first turn, which is slightly unusual

    def run_first_turn(self, turn_player: Player2 | Opponent):

        if turn_player.id == "player":
            self.run_player_turn()
            # TODO: Opponent draw up
        else:
            self.run_opponent_turn()
            # TODO: Player draw up
        self.cleanup_turn()    


    def run_opponent_turn(self):
        # TODO: opponent turn

        self.cleanup_turn()

    
    def run_player_turn(self):

        # TODO: player turn
        self.cleanup_turn()


    def cleanup_turn(self):        
        
        # At the end, clean up the player's banish
        # TODO: This should be a method on player, seeing as it assumes the same owner and all
        move_cards_between_zones(self.player, "banish", "exile")