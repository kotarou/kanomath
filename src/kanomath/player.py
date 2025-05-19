from loguru import logger
from kanomath.cards.card import COMBO_CORE, COMBO_EXTENDERS, Card
from kanomath.cards.potions import POTIONS
import typing
from kanomath.functions import card_is_blue, match_card_name, remove_all_matching, remove_first_matching # move_card_to_zone, move_cards_to_zone,
import kanomath.zones as zone
from functools import reduce

class Player:
    
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
    arcane_damage_dealt = 0

    # Turn details
    wizard_naa_played = 0
    cards_played = 0
    is_player_turn: bool = False

    # Spell stuff
    _amp_wildfire = 0
    _amp_next = 0
    _amp = 0

    # Equipment status
    rags_activated = False
    chestpiece_activated = False
    stormies_activated = False
    nodes_activated = False

    # Optinal components
    tunic_counters = 0

    # State tracking
    topdeck_is_brick = False
    topdeck_is_safe = False

    def __init__(self):

        self.hand = zone.Hand(self, self.base_intellect)
        self.arena = zone.Arena(self)
        self.arsenal = zone.Arsenal(self, self.max_cards_in_arsenal)
        self.pitch = zone.Pitch(self)
        self.discard = zone.Discard(self)
        # We can access cards in banish this turn
        self.banish = zone.Banish(self)
        # Exiled cards are goneski 
        self.exile = zone.Banish(self)
        self.deck = zone.Deck(self)

        self.braino = Braino(self)

    @property
    def potential_chest_pitch(self) -> int:
        if self.braino.use_tunic:
            return 1 if self.tunic_counters == 3 and not self.chestpiece_activated else 0
        elif self.braino.use_spellfire:
            return 1 if not self.chestpiece_activated else 0
        else:
            return 0
    
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
            case "arsenal":
                return self.arsenal    
            case _:
                raise Exception(f"Attempting to access zone that doesn't exist: {zone_name}")
    
    def card_name_in_zone(self, card_name: str, zone_name: str) -> bool:

        zone = self.get_zone_by_name(zone_name)
        return zone.contains_card_name(card_name)

    def get_card_by_intent(self, intent:str) -> Card | None:

        if self.arsenal.has_card:
            if self.arsenal.get_card().intent == intent: # type: ignore
                return self.arsenal.get_card() # type: ignore
        
        for card in self.hand.cards:
            if card.intent == intent:
                return card
    
        return None
       
    def get_cards_by_intent(self, intent:str) -> list[Card]:

        output = list[Card]()

        if self.arsenal.has_card:
            if self.arsenal.get_card().intent == intent: # type: ignore
                output.append(self.arsenal.get_card()) # type: ignore
        
        for card in self.hand.cards:
            if card.intent == intent:
                output.append(card)
    
        return output     

    def get_pitch_intent(self) -> int:
        return reduce(lambda result, card: result + card.pitch, self.get_cards_by_intent("pitch"), 0) 

    def access_to_card_name(self, card_name: str, allow_banish: bool = True) -> bool:
        return self.hand.contains_card_name(card_name) or self.arsenal.contains_card_name(card_name) or (allow_banish and self.banish.contains_card_name(card_name))

    def count_combo_access_card(self, card_name: str, allow_banish: bool = True) -> int:
        return self.hand.count_cards_name(card_name) + self.arsenal.count_cards_name(card_name) + (allow_banish and self.banish.count_cards_name(card_name) if allow_banish else 0)

    def make_token(self, token_name):
        pass

    def draw(self, draw_num: int = 1):

        if draw_num < 1:
            raise ValueError(f"Cannot draw fewer than 1 cards ({draw_num}).")
        
        self.deck.draw(draw_num)

    def register_amp_next(self, amp_num: int, source: str):

        if(amp_num < 0):
            raise Exception(f"Cannot amp next spell less than 0 ({amp_num}).")

        self._amp_next += 1
    
    def register_wildfire_amp(self, amp_num: int):

        if(amp_num < 0):
            raise Exception(f"Cannot amp next spell less than 0 ({amp_num}).")

        self._amp_wildfire += 1


    def register_amp(self, amp_num: int, source: str):
        
        if(amp_num < 0):
            raise Exception(f"Cannot amp less than 0 ({amp_num}).")
        
        self._amp += 1

    def gain_pitch(self, num_resources: int):
        
        if num_resources < 1:
            raise Exception(f"Attempting to gain {num_resources} pitch. The minimum to gain is 1. ")

        self.pitch_floating += num_resources
    
    def spend_pitch(self, num_resources: int, reason: str = ""):
        
        if num_resources < 0:
            raise Exception(f"Attempting to spend negative ({num_resources}) pitch on {reason}. The minimum to spend is 0. ")

        self.pitch_floating -= num_resources
        
    def opt(self, opt_num: int) -> None:
        opt_cards = self.deck.opt(opt_num)
        opt_top, opt_bot = self.braino.resolve_opt(opt_cards)
        self.deck.de_opt(opt_top, opt_bot)
        
        logger.decision(f"Opt saw {len(opt_top) + len(opt_bot)} cards. Put {opt_top} to top and {opt_bot} to bottom.")


    def kano(self):

        if self.pitch_floating < 3:
            raise Exception(f"Attempting to kano with {self.pitch_floating} resources. Need 3.")

        if self.deck.size == 0:
            raise Exception(f"Kanoing on an empty deck.")
        
        if len(self.braino.topdeck_actions) and self.braino.topdeck_actions[0] != "kano":
            raise Exception(f"Attempting to kano when the correct topdeck action is {self.braino.topdeck_actions[0]}.")

        self.spend_pitch(3, "kano")
        card    = typing.cast(Card, self.deck.peek())
        action  = self.braino.decide_kano_result(card)

        if action == "brick":
            logger.action(f"Player activated kano, seeing {card} and bricking.")
            # We could set num_kanos to 0 here to stop kanoing
            # But contonueing to kano into bricks allows for more hand cycling
            return
        
        elif action == "assess_combo":
            logger.action(f"Player activated kano, seeing {card}. Switching to assess a cheeky combo kill.")
            # We might be able to go off with this card
            # TODO: implement this
            # For now, assume seeing a combo piece in this situation is just a brick
            return
    
        elif action == "banish":
            logger.action(f"Player activated kano, seeing {card}. Banishing it to thin deck.")
            card.move_to_zone("banish")

        elif action == "play":
            logger.action(f"Player activated kano, seeing {card}. Banishing it to play as an instant.")
            card.move_to_zone("banish")
            self.play_card(card, as_instant=True)

        else:
            raise Exception(f"Attempted to resolve a kano with an illegal outcome ({action}).")

    def play_card(self, card: Card, as_instant = False):

        # TODO: card controller & owner
        # For now not particularly considered, nor fully implemented
        # if card.controller != self.id:
        #     raise Exception("Attempting to play a card we do not control ({card.controller} != {self.id})")

        logger.action(f"Playing {card} from {card.zone} as an {'action' if card.card_type == "action" and not as_instant else 'instant'}.")

        if card.card_type == "action" and not as_instant:
            if self.action_points == 0 or self.is_player_turn == False:
                raise Exception(f"Attempting to play an action when disallowed (Player turn: {self.is_player_turn}, AP: {self.action_points}, as_instant: {as_instant}).")
            else:
                self.action_points -= 1

        if self.pitch_floating >= card.cost:
            # TODO: assess nodes and crucible activations

            # We spend the resources here instead of in the card's play method
            # This avoid an inheritance issue present in earlier code, and also keeps player code in player
            self.spend_pitch(card.cost, card.card_name)
            card.on_play()
            # move_card_to_zone(card, "arsenal")


        else:
            # TODO: pitch to play the
            raise Exception(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")

        if card.card_class == "wizard" and card.card_type == "action":
            self.wizard_naa_played += 1

    def arsenal_card(self, card: Card):

        if self.arsenal.size > 0:
            raise Exception(f"Attempting to arsenal {card} when {self.arsenal.get_card()} is already in the arsenal).")

        print(f"  Arsenalling {card}.")
        zone.Zone.move_card_to_zone(card, "arsenal")

    def pitch_card(self, card: Card):

        if card.pitch == 0:
            raise Exception(f"Attempting to pitch {card} with pitch value {card.pitch}.")

        # print(f"  Pitching {card}. {{r}} {self.pitch_floating} -> {self.pitch_floating + card.pitch}. Hand: {self.hand.size - 1} left.")
        card.on_pitch()


    def play_opponent_turn(self, game_first_turn = False):

        # TODO: special handling of first turn opts & etc
        self.prepare_turn()

        num_kanos_aim       = self.braino.kanos_dig_opponent_turn
        num_kanos_completed = 0

        pitch_cards = self.get_cards_by_intent("pitch")
        pitch_cards.sort(key = lambda x : x.pitch, reverse=True)
       
        # print(f"  Aiming to kano {num_kanos_aim} times in opponent's turn.")

        while(num_kanos_completed < num_kanos_aim):
            
            # print(f"Kanos completed: {num_kanos_completed}. To complete: {num_kanos_aim - num_kanos_completed}. Loop condition {num_kanos_completed < num_kanos_aim} ")

            while(self.pitch_floating < 3):
                if len(pitch_cards):
                    # Ideally pitch efficiently, so take from the beginning of the pitch array
                    card = pitch_cards.pop(0)
                    self.pitch_card(card)
                else:
                    # Aimed to kano more times than we have
                    # Chances are we spent the resources on a kano'd card, or have since decided to hold a card
                    print(f"    Ran out of resources to kano with. Have {self.pitch_floating} floating, but hand is {self.hand} (pitch cards: {pitch_cards})")
                    break
                    # raise Exception(f"Somehow, trying to get more pitch when out of pitch cards. ")
            # print(f"current float: {self.pitch_floating} (bot)")

            # TODO: assess maybe comboing based on the kano result
            self.kano()
            num_kanos_completed += 1

        if game_first_turn:
            # print("  Player drew up for end of first turn.")
            self.hand.draw_up()

        self.pitch_floating     = 0

    def play_own_turn(self, game_first_turn = False):

        self.prepare_turn(game_first_turn)

        # TODO: Don't cheat by pitching all cards at the beginning
        # This is a pretty minor assumption though, as there is no combination of pitch cards that can't be cleared by correct pitching to kano and crible in a turn cycle
        # Pearl cards are a different story, of course.
        potential_pitch_cards   = self.get_cards_by_intent("pitch")
        potential_pitch_cards.sort(key=lambda x: x.pitch)

        # Reverse to iterate nice
        for card in potential_pitch_cards:
            self.pitch_card(card)
        
        potential_action_cards  = self.get_cards_by_intent("play")
    
        # Play out any actions we can
        if len (potential_action_cards):
            # Very simple trick to ignore the issue of wanting to play more than one card: just hold the others
            for potential_action in potential_action_cards[1:]:
                logger.decision(f"Player has too many ({len(potential_action_cards)}) actions to take. Switching intent for {potential_action_cards[1:]} to hold.")
                potential_action.intent = "hold"

            potential_card = potential_action_cards[0]

            if self.pitch_floating < potential_card.cost:
                if potential_card.zone == "hand":
                    # We can't actually pay for the card, so switch it to a pitch card
                    logger.warning(f"Player wants to play {potential_card} from hand, but cannot afford it. Pitching it instead.")
                    potential_card.intent = "pitch"
                    self.pitch_card(potential_card)
                else:
                    logger.error(f"Player wants to play {potential_card} from arsenal, but cannot afford it. Waiting for next turn.")
                    # Fuck, we're stuck with it turn turn
                    pass
            else:

                should_crucible = self.braino.decide_turn_crucible(potential_card)
                if should_crucible:
                    self.activate_crucible()
                
                self.play_card(potential_card)

        while self.pitch_floating >= 3:
            self.kano()
        
        
        potential_arsenal_cards = self.get_cards_by_intent("arsenal")
        if len (potential_arsenal_cards) > 1:
            raise Exception(f"Player has indicated more than one card to put in arsenal: {potential_arsenal_cards}.")
        
        elif len (potential_arsenal_cards) == 1:
            self.arsenal_card(potential_arsenal_cards[0])
            
        logger.info(f"Player drew {self.current_intellect - self.hand.size} cards for end of their turn.")
        
        self.end_turn()

    def activate_crucible(self):
        
        if self.pitch_floating < 1:
            raise Exception(f"Attempting to use crucible with only {self.pitch_floating} resources available (need 1).")

        if self.crucible_used:
            raise Exception(f"Attempting to use crucible a second time in one turn.")

        self.register_amp_next(1, "crucible")
        self.crucible_used = True


    def prepare_turn(self, game_first_turn = False):

        self.is_player_turn = not self.is_player_turn
        
        if self.is_player_turn:
            self.action_points  = 1
            logger.system(f"Beginning player{'\'s first' if game_first_turn else ''} turn")
        else:
            logger.system(f"Beginning opponent{'\'s first' if game_first_turn else ''} turn")

        self.crucible_used      = False
        self.wizard_naa_played  = 0

    
        self.braino.evaluate_state()

        logger.info(f"Player hand: {self.hand}, arsenal: {self.arsenal}, arena: {self.arena}.")

        if game_first_turn or not self.is_player_turn:
            self.braino.cycle_make_initial_decisions()

    def end_turn(self):

        # First, clean up pitch & banish
        for idx in reversed(range(self.pitch.size)):
            card = self.pitch.cards[idx]

            zone.Zone.move_card_to_zone(card, "deck", "bottom")
            card.on_turn_end()
        
        for idx in reversed(range(self.banish.size)):
            card = self.banish.cards[idx]

            zone.Zone.move_card_to_zone(card, "exile")
            card.on_turn_end()


        if self.is_player_turn:
            self.hand.draw_up()

        self.action_points      = 0        
        self.pitch_floating     = 0
        


# Braino is responsible for all player decisions
# In theory, braino should play optimally based on some constraints on "personality"
class Braino:

    state : str
    player: Player

    critical_resources: int = 14

    combo_extenders     = ["Overflow the Aetherwell", "Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]
    combo_big_hitters   = ["Aether Flare", "Lesson in Lava", "Blazing Aether", "Aether Wildfire"]
    combo_core_pieces   = ["Kindle", "Aether Wildfire", "Lesson in Lava", "Blazing Aether"]

    combo_draw_2        = ["Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal"]
    combo_draw_1        = []

    topdeck_actions     = []

    num_kanos_possible: int

    def __init__(self, player: Player):

        # Initial state
        self.player = player
        self.state  = "setup"

        # Play patterns & decision
        self.use_tunic          = False
        self.use_spellfire      = True

        self.proactively_arsenal_blazing    = False
        self.proactively_arsenal_gaze       = False




        pass

    def evaluate_state(self):
        # Has aether wildfire to begin combo
        self.wf_hand    = self.player.hand.contains_card_name("Aether Wildfire")
        self.wf_arsenal = self.player.arsenal.contains_card_name("Aether Wildfire")
        self.wf_banish  = self.player.banish.contains_card_name("Aether Wildfire")
        self.has_wf     = self.wf_hand or self.wf_arsenal or self.wf_banish # self.has_wf = self.player.access_to_card_name("Aether Wildfire")
        
        # Has finisher to end combo
        self.blazing_hand    = self.player.hand.contains_card_name("Blazing Aether")
        self.blazing_arsenal = self.player.arsenal.contains_card_name("Blazing Aether")
        self.blazing_banish  = self.player.banish.contains_card_name("Blazing Aether")
        self.has_blazing     = self.blazing_hand or self.blazing_arsenal or self.blazing_banish

        # Has lesson to find combo finisher
        self.lesson_hand    = self.player.hand.contains_card_name("Lesson in Lava")
        self.lesson_arsenal = self.player.arsenal.contains_card_name("Lesson in Lava")
        self.lesson_banish  = self.player.banish.contains_card_name("Lesson in Lava")
        self.has_lesson     = self.lesson_hand or self.lesson_arsenal or self.lesson_banish

        # Always prioritize playing from arsenal over hand, if possible
        # Hitting the blazing is generally better than second wf
        # We thus mark ourselfs as not having the WF in hand, to pitch it
        if self.wf_hand and (self.wf_arsenal or self.wf_banish) and (self.has_blazing or self.has_lesson):
            self.wf_hand = False

        # Always prefer Wf blazing over double blazing
        if self.blazing_hand and (self.blazing_arsenal or self.blazing_banish) and self.has_wf:
            self.blazing_hand = False

        # Double lesson too complex right now
        # TODO: account for double lesson lines
        if self.lesson_hand and (self.lesson_arsenal or self.lesson_banish) and self.has_wf:
            self.lesson_hand = False

        #   - Opportunistically looking for potions to extend combo
        self.num_epots = self.player.arena.count_cards_name("epot")
        self.num_dpots = self.player.arena.count_cards_name("dpot")
        self.num_cpots = self.player.arena.count_cards_name("cpot")

        # How many cards does the player want to draw
        self.count_kindles      = self.player.count_combo_access_card("Kindle", allow_banish = False)
        self.hand_kindle_count  = self.player.hand.count_cards_name("Kindle")

        self.topdeck_actions = []
        self.kanos_dig_opponent_turn = 0

    @property
    def hand_usable_pitch(self) -> int:
        hand_pitch    = self.player.hand.potential_pitch 
        
        if self.wf_hand:
            hand_pitch -= 1
        if self.blazing_hand:
            hand_pitch -= 1
        if self.lesson_hand:
            hand_pitch -= 2

        hand_pitch -= self.hand_kindle_count


        return hand_pitch



    # This is the number of resources the pklayer needs to see before they'll try combo
    # As a baseline, this is stormies (1), crucible (1), wildfire (2), nodes (1), blind kano maybe hitting floodgates (5), kano hitting blazing (3)
    #   for a total of 13, although 3 of this can come from rags activation
    def assess_critical_resources(self) -> int:
        return 10

    def resolve_opt(self, opt_cards:list[Card]) -> tuple[list[Card], list[Card]]:

        # print("Entering opt method")

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

        # If we're setting up, there are two primary outcomes: either we continue to filter top of deck, or we opportunistically go for the combo if we see an integral card
        if self.state == "setup":

            # print(f"wf: {see_wf_fix_hand}, blazing: {see_blazing_fix_hand}, lesson: {see_lesson_fix_hand}, pots: {opt_has_potion}")

            if not see_wf_fix_hand and not see_blazing_fix_hand and not see_lesson_fix_hand and opt_has_potion:
                # print("  Entering 'opt saw potion' section")
                # We can't use this hand to go off on a combo, given the new information
                # So lets continue to set up

                # Firstly, lets get potions to the top so we can kano them
                pots = self.opt_top_potions(opt_cards)
                
                # Then lets get relevant combo pieces to the top
                combo_pieces = self.opt_top_combo(opt_cards)

                # Finally, lets put spindle at the top because we might be able to combo with it later
                # We only want one spindle: two is too many in general (as we want to kano a potion we see from the spindle, so we don't want to kano twice into two spindleS)
                # TODO: match only red spindles, we don't care about blues in this context (if they are run)
                spindle = remove_first_matching(opt_cards, match_card_name("Aether Spindle"))

                # TODO: If we see Will and are close to comboing, keep it on top if we're not planning to kano more in the current turn
                # TODO: Likewise, if we see Eye, might be good to leave it on top

                self.topdeck_actions = ["kano"] * len(pots)

                if spindle is None:
                    return pots + combo_pieces, opt_cards
                else:
                    return pots + combo_pieces + [spindle], opt_cards
            
            if pitch_needed_to_combo < 1 and not self.player.is_player_turn:
                print("  Entering 'end setup, fuck it lets go' section")
                # The conditions under which a cheeky combo could become possible

                if see_wf_fix_hand or see_blazing_fix_hand or see_lesson_fix_hand:
                    assume_kanos_used = 0

                    top = []
                    bottom = []

                    if see_wf_fix_hand:
                    # Get the wildfire to first opt
                        wf = remove_first_matching(opt_cards, match_card_name("Aether Wildfire"))

                        if wf is not None:
                            top.append(wf)
                            assume_kanos_used += 1
                    
                    print(f" 2 - top:{top}")

                    if see_blazing_fix_hand or assume_kanos_used < reasonable_kano_activations:
                        # If we need a blazing, or another one would be nice for the combo
                        temp_blazings = remove_all_matching(opt_cards, match_card_name("Blazing Aether"))
                                                                       
                        # Slightly complicated here, as we might want to double blazing them if we somehow saw 2
                        # TODO: add logic to assess combo cost, to see if we really want / need either 2 blazings (see_blazing_fix_hand), or another (if we already have one)
                        num_blazings_to_kano = min(reasonable_kano_activations - assume_kanos_used, len(temp_blazings))
                        blazings = temp_blazings[:num_blazings_to_kano]

                        if num_blazings_to_kano < len(temp_blazings):
                            # Remember, array slice start index is inclusive, so add +1
                            bottom.extend(temp_blazings[num_blazings_to_kano + 1:])

                        top.extend(blazings)   
                        assume_kanos_used += len(blazings)    

                        print(f" 3 - top:{top}")  


                    if see_lesson_fix_hand or assume_kanos_used < reasonable_kano_activations:
                        # In case we see two lessons
                        temp_lessons = remove_all_matching(opt_cards, match_card_name("Lesson in Lava"))
                                                                    
                        num_lessons_to_kano = min((reasonable_kano_activations - assume_kanos_used) // 2, len(temp_lessons))
                        lessons = temp_lessons[:num_lessons_to_kano]

                        if num_lessons_to_kano < len(temp_lessons):
                            # Remember, array slice start index is inclusive, so add +1
                            bottom.extend(temp_lessons[num_lessons_to_kano + 1:])

                        top.extend(lessons)
                        assume_kanos_used += len(lessons)

                        print(f" 4 - top:{top}")

                    # After these, we can put any interesting combo cards to the top
                    combo_pieces = self.opt_top_combo(opt_cards, self.combo_extenders)
                    top.extend(combo_pieces)
                    print(f" 5 - top:{top}")
                    assume_kanos_used += len(combo_pieces)

                    self.topdeck_actions = ["kano"] * len(top)
                    
                    # Finally we can put a single blue to the top to draw off rags
                    blue = remove_first_matching(opt_cards, card_is_blue)

                    if blue is not None:
                        print(f" blue is {blue}")
                        top.append(blue)
                        self.topdeck_actions.append("draw")
                    
                    # There is an arguement to put xaps to the top here if the combo will be lethal with themn, to avoid over-extension
                    # TODO: Implement this when its safe to go for the small combo to just kill
                    bottom.extend(opt_cards)

                    self.state = "topdeck_combo"
                    return top, bottom

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

        # If we reached this state and are opting, we've hit a fairly rare case
        # Probably a cindering foresight was played which revealed a missing combo piece, and then we pitched eye
        # Otherwise, chances are gaze the ages was involved and is making life a little more complex
        
        # For now, assume that any opt during a cobo is the same as during the topdeck
        elif self.state == "topdeck_combo" or self.state == "combo":
            print("  Entering 'we're alrerady going' section")
            # If we're opting less than the currently known topdeck details, just pass
            opt_leave_num = min(len(opt_cards), len(self.topdeck_actions))

            if opt_leave_num == len(opt_cards):
                return opt_cards, []

            print(f"    Pre-opt, we're expecting to ignore the first {opt_leave_num} cards of the opt")

            opt_cards_top   = opt_cards[:opt_leave_num]      
            opt_cards_bot   = opt_cards[opt_leave_num:]

            # There is basically two options for topdeck cards here: we want to see hits, or we want to see blues to draw
            # Draw case is easy, and we address it forst because probably this deep into a turn, we need the extender blues
            # TODO: investigate case where we're in top_deck combo, opting, and see a blazing that is better than drawing

            # We draw 1 off rags, and one per kindle
            opt_draws_already_allocated = self.topdeck_actions.count("draw")
            combo_draws_cards = 0 if self.player.rags_activated else 1
            combo_draws_cards += self.count_kindles
            combo_draws_including_opt = combo_draws_cards

            print(f"    Pre-opt, we're expecting to draw {combo_draws_cards} cards this combo")

            for i in range(len(opt_cards_top)):
                card = opt_cards_top[i]
                # Little sanity check
                action = self.topdeck_actions[i] if i < len(self.topdeck_actions) else "blind"

                # We for whatever reason might be drawing a card that otherwise could be kano'd as a combo extender
                # For ease of implementation, lets assume that decision was correct
                # TODO: Could investgate this assumption as a sanity check
                if card.card_name in self.combo_draw_2 and action != "draw":
                    combo_draws_including_opt += 2
                elif card.card_name in self.combo_draw_1 and action != "draw":
                    combo_draws_including_opt += 1

                # A kindle we'll draw will mean we draw another card this turn
                # A kindle  we're not drawing needs to be in the other awway
                if card.card_name == "Kindle":
                    combo_draws_including_opt += 1
            
            print(f"    Considering opt, we're now expecting to draw {combo_draws_including_opt} cards this combo")

            kindles = remove_all_matching(opt_cards_bot, match_card_name("Kindle"))

            if combo_draws_cards > 0:
                print(f"      As we are drawing cards, putting{len(kindles)} to top of opt")
                for kindle in kindles:
                    opt_cards_top.append(kindle)
                    self.topdeck_actions.append("draw")

            print(f"    Post kindles, top: {opt_cards_top}, bot: {opt_cards_bot}")


            # if combo_draws_including_opt <= opt_draws_already_allocated and len(opt_cards_bot) > 0:
                
            # Lets put combo extenders to top
            # TODO: consider player pitch availble (urgh) to see if floodgates is actually appropriate
            extenders = self.opt_top_combo_extenders(opt_cards_bot)

            for card in extenders:
                opt_cards_top.append(card)
                self.topdeck_actions.append("kano")

            print(f"    Post extenders, top: {opt_cards_top}, bot: {opt_cards_bot}")


            # As well as super important kano pieces
            blazings = remove_all_matching(opt_cards_bot, match_card_name("Blazing Aether"))

            for card in blazings:
                opt_cards_top.append(card)
                self.topdeck_actions.append("kano")

            print(f"    Post blazings, top: {opt_cards_top}, bot: {opt_cards_bot}")


            # Allocate blues for those draws
            # TODO: proactively try to draw kindle into another blue
            if combo_draws_including_opt > opt_draws_already_allocated:
                draws_unaccounted = combo_draws_cards - opt_draws_already_allocated
                # TODO: implement logic for when gaze the ages is better to kano, then draw
                # Chances are thats rare if we're this deep into the method though, we're opting lots to get here
                blues = remove_all_matching(opt_cards_bot, card_is_blue)
                print(f"    With blues removed, top: {opt_cards_top}, bot: {opt_cards_bot}, blues: {blues}")
                
                for i in range(draws_unaccounted):
                    if i < len(blues):
                        opt_cards_top.append(blues[i])
                        self.topdeck_actions.append("draw")
                        opt_draws_already_allocated += 1

            print(f"    Post draw allocations, top: {opt_cards_top}, bot: {opt_cards_bot}")

            return opt_cards_top, opt_cards_bot
        
        
        # elif self.state == "combo_topdeck":

        return opt_cards, []

    def opt_top_potions(self, opt_cards:list[Card]) -> list[Card]:                
        # Potion priorities are normally simple, epot > dpot > cpot
        # There are edge cases: dpot #1 is maybe better than epot #3, and cpot #1 is better than dpot#2 
        #   Although access to will of arcana or eye complicates that further
        # TODO: actually accommodate for these cases
        # TODO: code specific edge case where spinning will makes double dpot better
        pots = remove_all_matching(opt_cards, match_card_name(POTIONS))
        
        # Very simpoe sort order that puts epots at the top
        pot_order = ["Energy Potion", "Potion of Deja Vu", "Clarity Potion"]
        pots.sort(key= lambda x: pot_order.index(x.card_name))

        return pots
    
    def opt_top_combo(self, opt_cards:list[Card], target_cards:list[str] = []) -> list[Card]: 
            
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
        
        top =  remove_all_matching(opt_cards, match_card_name(target_cards))

        return top

    def opt_top_combo_extenders(self, opt_cards:list[Card], target_cards:list[str] = []) -> list[Card]: 
            
        # We get passed a list of cards we want for the combo
        if not len(target_cards):
            target_cards = self.combo_extenders.copy()

        top = remove_all_matching(opt_cards, match_card_name(target_cards))

        # Very simple sort ordering
        # TODO: Actually care about pitch here (complex af)
        extender_priority = ["Open the Flood Gates", "Overflow the Aetherwell"]
        top.sort(key= lambda x: extender_priority.index(x.card_name) if x in extender_priority else 0)
        
        return top
    
    def cycle_make_initial_decisions(self):

        # TODO: assess opponent to make decisions

        # Initial variable setup
        pitch_to_hold   = 0

        option_unassinged   = self.player.hand.cards + self.player.arsenal.cards
        option_play_turn    = list[Card]()
        option_arsenal      = list[Card]()
        option_hold         = list[Card]()
        option_pitch_turn   = list[Card]()
        option_pitch_opp    = list[Card]()
        
        for card in option_unassinged:
            card.intent = ""

        best_play: Card | None      = None    
        best_arsenal: Card | None   = None

        for idx in reversed(range(len(option_unassinged))):
            card = option_unassinged[idx]
            
            # logger.debug(f"Assessing {card} ({card.zone}), action pri: {self.assign_action_priority(card)}, arsenal pri:{self.assign_arsenal_priority(card)}")
            
            if self.assign_action_priority(card):
                option_play_turn.append(card)
                option_unassinged.remove(card)
            
            elif self.assign_arsenal_priority(card):
                option_arsenal.append(card)
                option_unassinged.remove(card)   

        option_play_turn.sort(key = lambda x: self.assign_action_priority(x), reverse=True)

        if len(option_play_turn):
            best_play    = option_play_turn.pop(0)

            if self.assign_action_priority(best_play) > 0:
                best_play.intent = "play"
                # We might want to hold some of these other actions though
                option_arsenal.extend(option_play_turn)
            else:
                logger.warning(f"Best play for player sucks: {option_play_turn}")
                option_unassinged.append(best_play)

            option_unassinged.extend(option_play_turn)

        option_arsenal.sort(key = lambda x: self.assign_arsenal_priority(x), reverse=True)


        if len(option_arsenal):
            current_arsenal = self.player.arsenal.get_card()
            best_arsenal    = option_arsenal.pop(0)

            if current_arsenal is None:
                best_arsenal.intent = "arsenal"
            else:
                # Use names here for special case where we have the same card in arsenal
                if current_arsenal.card_name is not best_arsenal.card_name:
                    
                    # TODO logic for when holding arsenal is better
                    current_arsenal.intent = "play"
                    if best_play is not None:
                        best_play.intent = "hold"
                    best_play = current_arsenal
            
            option_hold.extend(option_arsenal)
    
        if len(option_hold):
            seen = list[str]()

            if best_arsenal is not None:
                seen.append(best_arsenal.card_name)

            # Remove duplicates, but we're happy to keep potions
            for card in option_hold:
                if card.card_name in seen and not "Potion" in card.card_name:
                    option_unassinged.append(card)
                    continue
                if self.assign_arsenal_priority(card) < 5:
                    option_unassinged.append(card)
                    continue
                else:
                    seen.append(card.card_name)
                    card.intent = "hold"
        
        # At this point all cards are flagged as arsenal, hold, or play
        # Lets work out how much pitcvh we want to hold for next turn

        if best_play is not None:
            pitch_to_hold = best_play.cost

            if best_play.card_name in ["Aether Spindle", "Aether Flare"]:
                # A kano, and a crucible
                pitch_to_hold += 4
            elif best_play.card_name in ["Aether Spindle", "Aether Flare"]:
                # Crucible
                # TODO: When AB is considered, worth considering it here
                pitch_to_hold += 1
        
        
        option_unassinged = list(filter(lambda x: x.intent not in ["arsenal", "play", "hold"], option_unassinged))

        for card in option_unassinged:
            card.intent = "pitch"

        pitch_available = sum(x.pitch for x in option_unassinged) - pitch_to_hold

        self.kanos_dig_opponent_turn = pitch_available // 3 if pitch_available > 0 else 0

    # Decide what action should be taken with a topdeck card
    def decide_kano_result(self, card: Card):

        card_is_brick   = card.card_type != "action"

        if card_is_brick:
            return "brick"

        card_is_potion  = card.card_name in POTIONS
        card_is_combo   = card.card_name in COMBO_CORE
        card_is_extender= card.card_name in COMBO_EXTENDERS
        
        if self.state == "setup":

            if card_is_potion:
                return "play"
            
            if card_is_combo or card_is_extender and self.has_wf:
                return "assess_combo"
        
        if self.state == "topdeck_combo" or self.state == "combo":
            return "play"
        
        return "banish"
    
    def decide_turn_crucible(self, card: Card):

        if self.player.pitch_floating >= card.cost + 1:
            return True
        else:
            return False
            
    def assign_arsenal_priority(self, card: Card):
        
        # Combo priority: Wildfire = Kindle > Lesson > (maybe) Blazing Aether
        # Then, potion priority Energy Potion > Potion of Deja Vu > Clarity Potion
        # Then, actions: Aether Spindle > Aether Flare
        
        # current_arsenal = self.player.arsenal.get_card()
        
        if card.card_name == "Aether Wildfire":
            return 10
        
        if card.card_name == "Kindle":
            return 10

        if card.card_name == "Blazing Aether":
            
            num_left = self.player.deck.count_cards_name("Blazing Aether") == 0

            if self.proactively_arsenal_blazing or num_left == 0:
                return 10
            else:
                return 2
            
        if card.card_name == "Lesson in Lava":
            
            if not self.has_blazing:
                return 8
            else:
                return 4
            
        if card.card_name == "Cindering Foresight" and card.colour == "red":
            return 5
            
        if card.card_name == "Energy Potion":
            return 6
        if card.card_name == "Potion of Deja Vu":
            return 5        
        if card.card_name == "Clarity Potion":
            return 4

        if card.card_name == "Aether Spindle" and card.colour == "red":
            return 3       
        if card.card_name == "Aether Flare" and card.colour == "red":
            return 2
        
        if card.card_name == "Gaze the Ages" and self.proactively_arsenal_gaze:
            return 1
             
        return 0

    def assign_action_priority(self, card: Card):
                      
        if card.card_name == "Energy Potion":
            return 10
        if card.card_name == "Potion of Deja Vu":

            if self.num_dpots:
                return 4
            else:
                return 9    
               
        if card.card_name == "Clarity Potion":
            if self.num_cpots:
                return 3
            else:
                return 8
    
        # High priority if to find a wildfire if we lack one
        # TODO: if we resolve this in this fashion, should resolve kanos then play action
        if card.card_name == "Lesson in Lava" and not self.has_wf:
            return 7
            
        if card.card_name == "Aether Spindle" and card.colour == "red":
            # if self.player.pitch_floating >= 6:
            return 2
            # elif self.player.pitch_floating >= 3:
            #     return 4
            # elif self.player.pitch_floating >= 2:
            #     return 3
            # else:
            #     return 0
        
        if card.card_name == "Aether Flare" and card.colour == "red":
            # if self.player.pitch_floating >= 5:
            return 1
            # else:
            #     return 0

        # TODO: Consider playing gaze at action speed
        # TODO: Consider playing cindering at action speed
             
        return 0
