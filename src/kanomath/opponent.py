from abc import ABC

from kanomath.cards.card import Card # i.e. Abstract Base Class

class Opponent:

    health = 40
    lastHit = 0
    id = "opponent"

    def __init__(self):
        pass

    def registerDamage(self, damage:int, source: Card):

        # kprint(f"Opponent took {damage} damage from {source}", 2)

        self.lastHit = damage
        self.health -= damage




    # Opponents have:
    #   a class (guardian, aggor ninja, assassin)
    #   a personaility (aggressive, careful)
    #   a hand & arsenal, 
    #   equipment, generalized to prevention (ab, sv)
    #   maybe tunic
    #   a series of actions

# On the opponent's turn, evaluate all registered actions to see if their preconditions are met
#   Then, rank them by priority
#   Finally, execute them to affect the player and opponent's states in some manner
# To begin these will be simple, and not chain off eachother
#   Examples: 
#       swing anothos at the cost of resources
#       pass turn with a blue in hand
#       play cnc, or cnc+pummel (for initial simplicity opponent will not hold either, nor will they arsenal one)
#       arsenal oasis

# class OpponentAction(ABC):

#     @property
#     def priority(self, opponent):
#         return 0

#     def precondition(self, opponent):
#         return True
    
#     def effect(self, opponent, player):
#         # e.g. Anothos: player.TakeDamage(6), opponent.useResources(4)
#         # e.g. opponent.arsenal(Card)
#         pass

class OpponentType:
    
    opponent_type: str
    strategy: str

    ab: int
    sv: int

    can_oasis: bool

    card_assume_pitch : int
    damage_threat_per_turn : int
    damage_cost_per_turn : int
    damage_cards_per_turn : int
    
    def __init__(self, opponent_type, strategy):
        self.opponent_type  = opponent_type
        self.strategy       = strategy
        self.must_blocks    = ["Aether Spindle", "Aether Flare"]
        
        # A rough and ready approximation of what an opponent might do
        if self.opponent_type == "guardian":
            # Guardians generally run blues
            self.card_assume_pitch = 3
            self.ab = 3
            self.sv = 0
            self.can_oasis = True

            if self.strategy == "aggressive":
                # Aggressive guardians pummel cnc, zealous anothos, etc
                self.damage_threat_per_turn = 10
                self.damage_cost_per_turn = 4
                self.damage_cards_per_turn = 2
            else:
                # Whereas their conservative peers just anothos us
                self.damage_threat_per_turn = 6
                self.damage_cost_per_turn = 4
                self.damage_cards_per_turn = 0

        elif self.opponent_type == "midrange":
            # Midrange decks run a mix of blues and reds and swing a 3 for 7 spending 1 card 
            self.card_assume_pitch = 2
            self.ab = 3
            self.sv = 0
            self.can_oasis = True
            self.damage_threat_per_turn = 7
            self.damage_cost_per_turn = 3
            self.damage_cards_per_turn = 1
        elif self.opponent_type == "assassin":
            # Assassins are a broad category, but lets say they spend 2 cards and 2 pitch to threaten 8
            self.card_assume_pitch = 2
            self.ab = 3
            self.sv = 3
            self.can_oasis = False
            self.damage_threat_per_turn = 8
            self.damage_cost_per_turn = 2
            self.damage_cards_per_turn = 2
        elif self.opponent_type == "ninja":
            # the only relevant ninjas attack with 4 head jabs and do 14 damage off 0 pitch and 4 cards
            self.card_assume_pitch = 1
            self.ab = 1
            self.sv = 1
            self.can_oasis = False
            self.damage_threat_per_turn = 14
            self.damage_cost_per_turn = 0
            self.damage_cards_per_turn = 4
        else:
            raise Exception(f"Invalid opponent type {opponent_type}")

        if self.strategy == "defensive":
            self.must_blocks.append("Lesson in Lava")

        self.starting_life = 40
    
class Opponent2:

    current_life: int
    details: OpponentType

    cards_in_hand: int
    resources_floating: int
       

    def __init__(self, opponent_type, strategy):

        self.details = OpponentType(opponent_type, strategy)
        self.current_life = self.details.starting_life
        self.cards_in_hand = 0

    # def turn_pitch_available(self) -> int:
    #     return self.details.card_assume_pitch * self.cards_in_hand

    # # What is the cost, in lost resources that could be used to defend, of attacking?
    # def attack_cost(self) -> int:
    #     return self.details.damage_cost_per_turn + (self.details.damage_cards_per_turn * self.details.card_assume_pitch)

    # def can_attack(self) -> bool:
    #     return self.details.card_assume_pitch * (self.cards_in_hand - self.details.damage_cards_per_turn) >= self.details.damage_cost_per_turn
    
    # def will_attack(self) -> bool:
        
    #     resources   = self.turn_pitch_available()
    #     attack_cost = self.attack_cost()
    #     spare_pitch = resources - attack_cost

    #     if self.details.strategy == "defensive":
    #         return spare_pitch >= self.details.ab
    #     else:
    #         return spare_pitch > 0
    
    # # As a general rule, an aggressive opponent will only prevent as much as is required to attack back
    # # A midrange opponent is willing to not attack in the next turn to prevent super important on-hits
    # # A defensive opponent will want to block everything but always keep enough resources to ab 3 in their own turn
    # def will_defend_in_player_turn(self, threat: Card2) -> bool:

    #     resources   = self.turn_pitch_available()
    #     attack_cost = self.attack_cost()
    #     spare_pitch = resources - attack_cost

    #     if self.details.strategy == "defensive":
    #         return resources >= 3
    #     if self.details.strategy == "midrange":
    #         if threat.card_name in self.details.must_blocks:
    #             return True
    #         else:
    #             return spare_pitch >= 3
    #     else:
    #         # aggressive
    #         return spare_pitch >= 0
        
    # def use_ab(self, turn_player: str, threat: Card2, damage_threatened: int) -> int:
        
    #     resources   = self.turn_pitch_available()
    #     attack_cost = self.attack_cost()
    #     spare_pitch = resources - attack_cost

    #     resources_used  = 0
    #     cards_used      = 0
    #     prevention      = 0

    #     if turn_player == "player" and self.details.will_defend_in_player_turn():
    #         cards_to_use = spare_pitch // self.details.card_assume_pitch
    #         self.cards_in_hand -= cards_to_use
    #         self.resources_floating +=  cards_to_use * self.details.card_assume_pitch

    #         prevention = min(self.details.ab, self.resources_floating)
    #         self.resources_floating -= prevention
        
    #     return prevention

