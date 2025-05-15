from kanomath.cards.card import Card2
from kanomath.cards.potions import POTIONS
from kanomath.functions import match_card_name, move_cards_to_zone, remove_all_matching, remove_first_matching
import kanomath.zones as zone


class Player2:
    
    # This will be used to identify card owners when needed in print statements
    id = "player"

    # We have a few relevant zones
    hand: zone.Hand
    arena: zone.Arena
    pitch: zone.Pitch
    discard: zone.Discard
    banish: zone.Banish
    deck: zone.Deck
    
    # Core player details
    base_intellect = 4
    current_intellect = 4
    max_cards_in_arsenal = 1

    # Resources
    action_points = 0
    pitch_floating = 0

    # Turn details
    wizard_naa_played = 0
    cards_played = 0
    is_player_turn: bool = False

    # Spell stuff
    amp_wildfire = 0
    amp_next = 0
    amp = 0

    # Equipment status
    rags_activated = True
    chestpiece_activated = False
    stormies_activated = False
    nodes_activated = False

    # Optinal components
    tunic_counters = 0

    # State tracking
    topdeck_is_brick = False
    topdeck_is_safe = False

    def __init__(self):

        self.hand = zone.Hand(self.base_intellect)
        self.arena = zone.Arena()
        self.arsenal = zone.Arsenal(self.max_cards_in_arsenal)
        self.pitch = zone.Pitch()
        self.discard = zone.Discard()
        # We can access cards in banish this turn
        self.banish = zone.Banish()
        # Exiled cards are goneski 
        self.exile = zone.Banish()
        self.deck = zone.Deck()

        self.braino = Braino(self)

    def get_zone_by_name(self, zone_name: str) -> zone.Zone:

        match zone_name:
            case "hand":
                return self.hand
            case "deck":
                return self.deck
            case "discard" | "grave" | "graveyard":
                return self.discard
            case "pitch":
                return self.pitch               
            case "banish" :
                return self.banish  
            case "exile":
                return self.exile     
            case "arena":
                return self.arena        
            case _:
                raise Exception(f"Attempting to access zone that doesn't exist: {zone_name}")
    
    def access_to_card_name(self, card_name: str) -> bool:
        return self.hand.contains_card_name(card_name) or self.arsenal.contains_card_name(card_name) or self.banish.contains_card_name(card_name)

    def gain_pitch(self, num_resources: int):
        
        if num_resources < 1:
            raise Exception(f"Attempting to gain {num_resources} pitch. The minimum to gain is 1. ")

        self.pitch_floating += num_resources

    @property
    def potential_chest_pitch(self) -> int:
        if self.braino.use_tunic:
            return 1 if self.tunic_counters == 3 and not self.chestpiece_activated else 0
        elif self.braino.use_spellfire:
            return 1 if not self.chestpiece_activated else 0
        else:
            return 0

# Braino is responsible for all player decisions
# In theory, braino should play optimally based on some constraints on "personality"
class Braino:

    state : str
    player: Player2

    use_tunic: bool
    use_spellfire: bool

    critical_resources: int = 14

    combo_extenders = ["Overflow the Aetherwell", "Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]
    combo_bighitters = ["Aether Flare", "Lesson in Lava", "Blazing Aether", "Aether Wildfire"]

    def __init__(self, player: Player2):

        self.player = player
        self.state = "setup"

        self.use_tunic = False
        self.use_spellfire = True

        pass

    # This is the number of resources the pklayer needs to see before they'll try combo
    # As a baseline, this is stormies (1), crucible (1), wildfire (2), nodes (1), blind kano maybe hitting floodgates (5), kano hitting blazing (3)
    #   for a total of 13, although 3 of this can come from rags activation
    def assess_critical_resources(self) -> int:
        return 10

    def resolve_opt(self, cards:list[Card2]) -> tuple[list[Card2], list[Card2]]:

        # The first thing to check with the opt is whether it exposes information that might change our state
        opt_has_wf      = any(card.card_name == "Aether Wildfire" for card in cards)
        opt_has_blazing = any(card.card_name == "Blazing Aether" for card in cards)
        opt_has_lesson  = any(card.card_name == "Lesson in Lava" for card in cards)
        opt_has_potion  = any("Potion" in card.card_name for card in cards)
        opt_has_blue    = any(card.pitch == 3 for card in cards)
        
        #   - Has aether wildfire to begin combo
        has_wf = self.player.access_to_card_name("Aether Wildfire")
        #   - Has finisher to end combo
        has_blazing = self.player.access_to_card_name("Blazing Aether")
        has_lesson  = self.player.access_to_card_name("Lesson in Lava")
        #   - Opportunistically looking for potions to extend combo
        num_epots = self.player.arena.count_cards_name("epot")
        num_dpots = self.player.arena.count_cards_name("dpot")
        num_cpots = self.player.arena.count_cards_name("cpot")
        #   - Has resources to pay for combo
        
        see_wf_fix_hand         = (has_blazing or has_lesson) and opt_has_wf and not has_wf
        see_blazing_fix_hand    = has_wf and (opt_has_blazing or opt_has_lesson) and not has_blazing

        # Note that these count might count the player as having one too many resooucres if we need to rags a card from hand
        hand_potential_pitch    = self.player.hand.potential_pitch + (2 * num_epots) + self.player.potential_chest_pitch
        hand_threshold_pitch    = self.assess_critical_resources()
        pitch_needed_to_combo   = hand_threshold_pitch - hand_potential_pitch
        
        # TODO: Need to account for held combo cards here
        # The - 1 vaguely accounts for this in the short term, as its very unlikely we see 3 potions and can;t get them all
        # Theres an edge case for tunic in which using tunic will gfet the second or third potion
        reasonable_kano_activations  = (self.player.hand.potential_pitch - 1) // 3

        if self.state == "setup":

            if not see_wf_fix_hand and not see_blazing_fix_hand and opt_has_potion:
                # We can't use this hand to go off on a combo, given the new information
                # So lets continue to set up

                # Potion priorities are normally simple, epot > dpot > cpot
                # There are edge cases: dpot #1 is maybe better than epot #3, and cpot #1 is better than dpot#2 
                #   Although access to will of arcana or eye complicates that further
                # TODO: actually accommodate for these cases
                # TODO: code specific edge case where spinning will makes double dpot better
                pots, rest = remove_all_matching(cards, match_card_name(POTIONS))
                
                # Very simpoe sort order that puts epots at the top
                pot_order = ["epot", "dpot", "cpot"]
                pots.sort(key= lambda x: pot_order.index(x.card_name_short))

                # We're going to assume that because we haven;t seen a cobo hand fixer, that nothing else matters (apart from kindle)
                # TODO: work on this assumption if it really matters
                kindles, rest = remove_all_matching(rest, match_card_name("Kindle"))

                pots.extend(kindles)
                return pots, rest
            
            if pitch_needed_to_combo < 1 and not self.player.is_player_turn:
                # The conditions under which a cheeky combo could become possible

                pass

                # Strategy here is to put the key card on top
                # Then, work out how many kanos we can, and want to do
                # Put any good combo pieces into those slots
                # Then put blues into slots for rags, kindle draw, 
                # Finally, put blues into combo slots if we can just kill them and don;t need to worry about blind reach

                # top = []
                # rest = []

                # if see_wf_fix_hand:
                #     top, rest = remove_first_matching(cards, match_card_name("Aether Wildfire"))

                # if see_blazing_fix_hand:
                #     top, rest = remove_first_matching(cards, match_card_name("Blazing Aether"))


        return cards, []

