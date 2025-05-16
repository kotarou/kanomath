from kanomath.cards.card import Card2
from kanomath.cards.potions import POTIONS
from kanomath.functions import card_is_blue, match_card_name, move_cards_to_zone, remove_all_matching, remove_first_matching
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

    combo_extenders     = ["Overflow the Aetherwell", "Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]
    combo_big_hitters   = ["Aether Flare", "Lesson in Lava", "Blazing Aether", "Aether Wildfire"]
    combo_core_pieces   = ["Kindle", "Aether Wildfire", "Lesson in Lava", "Blazing Aether"]

    def __init__(self, player: Player2):

        self.player = player
        self.state = "setup"

        self.use_tunic = False
        self.use_spellfire = True

        pass

    def turn_evaluate_state(self):
        #   - Has aether wildfire to begin combo
        self.has_wf = self.player.access_to_card_name("Aether Wildfire")
        #   - Has finisher to end combo
        self.has_blazing = self.player.access_to_card_name("Blazing Aether")
        self.has_lesson  = self.player.access_to_card_name("Lesson in Lava")
        #   - Opportunistically looking for potions to extend combo
        self.num_epots = self.player.arena.count_cards_name("epot")
        self.num_dpots = self.player.arena.count_cards_name("dpot")
        self.num_cpots = self.player.arena.count_cards_name("cpot")

        self.topdeckactions = []

    # This is the number of resources the pklayer needs to see before they'll try combo
    # As a baseline, this is stormies (1), crucible (1), wildfire (2), nodes (1), blind kano maybe hitting floodgates (5), kano hitting blazing (3)
    #   for a total of 13, although 3 of this can come from rags activation
    def assess_critical_resources(self) -> int:
        return 10

    def resolve_opt(self, opt_cards:list[Card2]) -> tuple[list[Card2], list[Card2]]:

        # The first thing to check with the opt is whether it exposes information that might change our state
        opt_has_wf      = any(card.card_name == "Aether Wildfire" for card in opt_cards)
        opt_has_blazing = any(card.card_name == "Blazing Aether" for card in opt_cards)
        opt_has_lesson  = any(card.card_name == "Lesson in Lava" for card in opt_cards)
        opt_has_potion  = any("Potion" in card.card_name for card in opt_cards)
        opt_has_blue    = any(card.pitch == 3 for card in opt_cards)

        #   - Has resources to pay for combo
        see_wf_fix_hand         = (self.has_blazing or self.has_lesson) and opt_has_wf and not self.has_wf
        see_blazing_fix_hand    = self.has_wf and opt_has_blazing and not self.has_blazing
        see_lesson_fix_hand     = self.has_wf and opt_has_lesson and not self.has_blazing

        # Note that these count might count the player as having one too many resooucres if we need to rags a card from hand
        hand_potential_pitch    = self.player.hand.potential_pitch + (2 * self.num_epots) + self.player.potential_chest_pitch
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

                # Firstly, lets get potions to the top so we can kano them
                pots, opt_cards = self.opt_top_potions(opt_cards)
                
                # Then lets get relevant combo pieces to the top
                combo_pieces, opt_cards = self.opt_top_combo(opt_cards)

                # Finally, lets put spindle at the top because we might be able to combo with it later
                # We only want one spindle: two is too many in general (as we want to kano a potion we see from the spindle, so we don't want to kano twice into two spindleS)
                # TODO: match only red spindles, we don't care about blues in this context (if they are run)
                spindle, opt_cards = remove_first_matching(opt_cards, match_card_name("Aether Spindle"))

                # TODO: If we see Will and are close to comboing, keep it on top if we're not planning to kano more in the current turn
                # TODO: Likewise, if we see Eye, might be good to leave it on top

                self.topdeckactions = ["kano"] * len(pots)

                if spindle is None:
                    return pots + combo_pieces, opt_cards
                else:
                    return pots + combo_pieces + [spindle], opt_cards
            
            if pitch_needed_to_combo < 1 and not self.player.is_player_turn:
                # The conditions under which a cheeky combo could become possible

                if see_wf_fix_hand or see_blazing_fix_hand or see_lesson_fix_hand:

                    assume_kanos_used = 0

                    top = []
                    bottom = []

                    if see_blazing_fix_hand:
                    # Get the wildfire to first opt
                        wf, opt_cards = remove_first_matching(opt_cards, match_card_name("Aether Wildfire"))

                        if wf is not None:
                            top.append(wf)
                            assume_kanos_used += 1
                    
                    if see_blazing_fix_hand or assume_kanos_used < reasonable_kano_activations:
                        # If we need a blazing, or another one would be nice for the combo
                        temp_blazings, opt_cards = remove_all_matching(opt_cards, match_card_name("Blazing Aether"))
                                                                       
                        # Slightly complicated here, as we might want to double blazing them if we somehow saw 2
                        # TODO: add logic to assess combo cost, to see if we really want / need either 2 blazings (see_blazing_fix_hand), or another (if we already have one)
                        num_blazings_to_kano = min(reasonable_kano_activations - assume_kanos_used, len(temp_blazings))
                        blazings = temp_blazings[:num_blazings_to_kano]

                        if num_blazings_to_kano < len(temp_blazings):
                            # Remember, array slice start index is inclusive, so add +1
                            bottom.extend(temp_blazings[num_blazings_to_kano + 1:])

                        top.extend(blazings)   
                        assume_kanos_used += len(blazings)      


                    if see_lesson_fix_hand or assume_kanos_used < reasonable_kano_activations:
                            # In case we see two lessons
                            temp_lessons, opt_cards = remove_all_matching(opt_cards, match_card_name("Lesson in Lava"))
                                                                        
                            num_lessons_to_kano = min((reasonable_kano_activations - assume_kanos_used) // 2, len(temp_lessons))
                            lessons = temp_lessons[:num_lessons_to_kano]

                            if num_lessons_to_kano < len(temp_lessons):
                                # Remember, array slice start index is inclusive, so add +1
                                bottom.extend(temp_lessons[num_lessons_to_kano + 1:])

                            top.extend(lessons)
                            assume_kanos_used += len(lessons)

                    # After these, we can put any interesting combo cards to the top
                    combo_pieces, opt_cards = self.opt_top_combo(opt_cards, self.combo_extenders)
                    top.extend(combo_pieces)
                    assume_kanos_used += len(combo_pieces)

                    self.topdeckactions = ["kano"] * len(top)
                    
                    # Finally we can put a single blue to the top to draw off rags
                    blue = remove_first_matching(opt_cards, card_is_blue)

                    if blue is not None:
                        top.append(blue)
                        self.topdeckactions.append("draw")
                    
                    bottom.extend(opt_cards)

                    self.state = "combo_topdeck"
                    return top, bottom

                        


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


        return opt_cards, []

    def opt_top_potions(self, opt_cards:list[Card2]) -> tuple[list[Card2], list[Card2]]:                
        # Potion priorities are normally simple, epot > dpot > cpot
        # There are edge cases: dpot #1 is maybe better than epot #3, and cpot #1 is better than dpot#2 
        #   Although access to will of arcana or eye complicates that further
        # TODO: actually accommodate for these cases
        # TODO: code specific edge case where spinning will makes double dpot better
        pots, rest = remove_all_matching(opt_cards, match_card_name(POTIONS))
        
        # Very simpoe sort order that puts epots at the top
        pot_order = ["epot", "dpot", "cpot"]
        pots.sort(key= lambda x: pot_order.index(x.card_name_short))

        return pots, rest
    
    def opt_top_combo(self, opt_cards:list[Card2], target_cards:list[str] = []) -> tuple[list[Card2], list[Card2]]: 
            
        # We get passed a list of cards we want for the combo
        if not len(target_cards):
            target_cards = self.combo_core_pieces.copy()

            # Some of these cards might be useful in duplicate during a combo turn
            # For now, assume we don't want to practively work towards having two of them in a combo
            # TODO: Identify when I might want this, and then implement relevant logic
            if self.has_wf:
                target_cards.remove("Aether Wildfire")
            if self.has_lesson:
                target_cards.remove("Lesson in Lava")
            if self.has_blazing:
                target_cards.remove("Blazing Aether")
        
        
        return remove_all_matching(opt_cards, match_card_name(target_cards))
    