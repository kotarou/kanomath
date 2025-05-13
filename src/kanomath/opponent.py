from abc import ABC # i.e. Abstract Base Class
from .util import kprint
from .card import Card

class Opponent:

    health = 40
    lastHit = 0

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

class OpponentAction(ABC):

    @property
    def priority(self, opponent):
        return 0

    def precondition(self, opponent):
        return True
    
    def effect(self, opponent, player):
        # e.g. Anothos: player.TakeDamage(6), opponent.useResources(4)
        # e.g. opponent.arsenal(Card)
        pass