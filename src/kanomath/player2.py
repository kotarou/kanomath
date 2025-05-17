from kanomath.cards.card import COMBO_CORE, COMBO_EXTENDERS, Card2
from kanomath.cards.potions import POTIONS
import typing
from kanomath.functions import card_is_blue, match_card_name, move_card_to_zone, move_cards_to_zone, remove_all_matching, remove_first_matching
import kanomath.zones as zone
from functools import reduce

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
            case _:
                raise Exception(f"Attempting to access zone that doesn't exist: {zone_name}")
    
    def card_name_in_zone(self, card_name: str, zone_name: str) -> bool:

        zone = self.get_zone_by_name(zone_name)
        return zone.contains_card_name(card_name)

    def get_card_by_intent(self, intent:str) -> Card2 | None:

        if self.arsenal.has_card:
            if self.arsenal.get_card().intent == intent: # type: ignore
                return self.arsenal.get_card() # type: ignore
        
        for card in self.hand.cards:
            if card.intent == intent:
                return card
    
        return None
       
    def get_cards_by_intent(self, intent:str) -> list[Card2]:

        output = list[Card2]()

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

    def gain_pitch(self, num_resources: int):
        
        if num_resources < 1:
            raise Exception(f"Attempting to gain {num_resources} pitch. The minimum to gain is 1. ")

        self.pitch_floating += num_resources
    
    def spend_pitch(self, num_resources: int):
        
        if num_resources < 0:
            raise Exception(f"Attempting to spend negative ({num_resources}) pitch. The minimum to spend is 0. ")

        self.pitch_floating += num_resources
        
    def opt(self, opt_num: int) -> None:
        opt_cards = self.deck.opt(opt_num)
        print(f"Seeing {opt_cards} when opting {opt_num}")
        opt_top, opt_bot = self.braino.resolve_opt(opt_cards)
        print(f"  Then, putting {opt_top} to top and {opt_bot} to bottom.")
        print(f"  {len(self.braino.topdeck_actions)} card(s) on top of deck will be acted on this turn, with action(s): {self.braino.topdeck_actions}.")


        self.deck.de_opt(opt_top, opt_bot)

    def gain_amp(self, amp_num: int):

        if(amp_num < 1):
            raise Exception(f"Cannot amp less than 1 ({amp_num}).")

        self.amp += 1

    def kano(self):
        
        if self.pitch_floating < 3:
            raise Exception(f"Attempting to kano with {self.pitch_floating} resources. Need 3.")

        if self.deck.size == 0:
            raise Exception(f"Kanoing on an empty deck.")
        
        if len(self.braino.topdeck_actions) and self.braino.topdeck_actions[0] != "kano":
            raise Exception(f"Attempting to kano when the correct topdeck action is {self.braino.topdeck_actions[0]}.")

        self.pitch_floating -= 3

        card = typing.cast(Card2, self.deck.peek())

        action = self.braino.decide_kano_result(card)

        print(f"Braino has decided to {action} the {card}.")

        if action == "brick":
            # We could set num_kanos to 0 here to stop kanoing
            # But contonueing to kano into bricks allows for more hand cycling
            return
        
        elif action == "assess_combo":
            # We might be able to go off with this card
            # TODO: implement this
            # For now, assume seeing a combo piece in this situation is just a brick
            return
    
        elif action == "banish":
            # Just banish the card and ignore it
            move_card_to_zone(card, "banish")

        elif action == "play":
            move_card_to_zone(card, "banish")
            self.play_card(card, as_instant=True)

        else:
            raise Exception(f"Attempted to resolve a kano with an illegal outcome ({action}).")

    def play_card(self, card: Card2, as_instant = False):

        # TODO: card controller & owner
        # For now not particularly considered, nor fully implemented
        # if card.controller != self.id:
        #     raise Exception("Attempting to play a card we do not control ({card.controller} != {self.id})")
        
        if card.card_type == "action" and not as_instant:
            if self.action_points == 0 or self.is_player_turn == False:
                raise Exception(f"Attempting to play an action when disallowed (Player turn: {self.is_player_turn}, AP: {self.action_points}, as_instant: {as_instant}).")
            else:
                self.action_points -= 1

        if self.pitch_floating >= card.cost:
            # TODO: assess nodes and crucible activations
            card.on_play()

        else:
            # TODO: pitch to play the
            raise Exception(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")

        if card.card_class == "wizard" and card.card_type == "action":
            self.wizard_naa_played += 1


    def play_opponent_turn(self, game_first_turn = False):

        # TODO: special handling of first turn opts & etc

        num_kanos_aim       = self.braino.kanos_dig_opponent_turn
        num_kanos_completed = 0

        pitch_cards = self.get_cards_by_intent("pitch")
        pitch_cards.sort(key = lambda x : x.pitch, reverse=True)

        while(num_kanos_completed < num_kanos_aim):
            
            while(self.pitch_floating < 3):
                if len(pitch_cards):
                    card = pitch_cards.pop(0)
                    card.on_pitch()
                else:
                    raise Exception(f"Somehow, trying to get more pitch when out of pitch cards. ")
            
            # TODO: assess maybe comboing based on the kano result
            self.kano()
            num_kanos_completed += 1

        if game_first_turn:
            self.hand.draw_up()

    def play_own_turn(self, game_first_turn = False):


        pass


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

    combo_draw_2        = ["Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal"]
    combo_draw_1        = []

    topdeck_actions     = []

    num_kanos_possible: int

    def __init__(self, player: Player2):

        self.player = player
        self.state = "setup"

        self.use_tunic = False
        self.use_spellfire = True

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

    def resolve_opt(self, opt_cards:list[Card2]) -> tuple[list[Card2], list[Card2]]:

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

    def opt_top_potions(self, opt_cards:list[Card2]) -> list[Card2]:                
        # Potion priorities are normally simple, epot > dpot > cpot
        # There are edge cases: dpot #1 is maybe better than epot #3, and cpot #1 is better than dpot#2 
        #   Although access to will of arcana or eye complicates that further
        # TODO: actually accommodate for these cases
        # TODO: code specific edge case where spinning will makes double dpot better
        pots = remove_all_matching(opt_cards, match_card_name(POTIONS))
        
        # Very simpoe sort order that puts epots at the top
        pot_order = ["epot", "dpot", "cpot"]
        pots.sort(key= lambda x: pot_order.index(x.card_name_short))

        return pots
    
    def opt_top_combo(self, opt_cards:list[Card2], target_cards:list[str] = []) -> list[Card2]: 
            
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

    def opt_top_combo_extenders(self, opt_cards:list[Card2], target_cards:list[str] = []) -> list[Card2]: 
            
        # We get passed a list of cards we want for the combo
        if not len(target_cards):
            target_cards = self.combo_extenders.copy()

        top = remove_all_matching(opt_cards, match_card_name(target_cards))

        # Very simple sort ordering
        # TODO: Actually care about pitch here (complex af)
        extender_priority = ["Open the Flood Gates", "Overflow the Aetherwell"]
        top.sort(key= lambda x: extender_priority.index(x.card_name_short) if x in extender_priority else 0)
        
        return top
    
    def cycle_make_initial_decisions(self):

        # Eventually decisions here will be made based on opponent actions

        # Decision tree here is simple
        # First, any cards that _have_ to be held for the combo are set aside

        # We identify any cards that would be good to arsenal, and if we can clear out the arsenal at action speed next turn

        # Then, we assess any interesting action speed plays
        #   - play a potion
        #   - play aether spindle with 2 blues in hand to find and kano potions
        #   - play aether flare with 2 blues in hand to push damage
        #   - play lesson in lava to hunt for a combo piece

        # We then use spare resources to kano in their turn
        # This could change our evaluations of what to do in our turn
        #   - We play out potions, spindles, flares, sonic boom, tome of aetherwind
        #   - We banish zaps and leave them there
        #   - We get sad on bricks
        #   - If we see a relevant combo pieces, we either:
        #       - Swith to comboing if its relevant
        #       - Leave it on top for next turn

        # We then allow their turn to end, and execute ours

        pitch_to_hold   = 0

        action_play_priority    = ["Energy Potion", "Potion of Deja Vu", "Aether Spindle", "Clarity Potion", "Lesson in Lava", "Aether Flare"]
        # TODO: consider arsenalling blazing
        arsenal_target_priority = ["Aether Wildfire", "Kindle", "Energy Potion", "Potion of Deja Vu", "Lesson in Lava", "Aether Spindle", "Aether Flare", "Cindering Foresight"]
        arsenal_combo_pieces    = ["Aether Wildfire", "Kindle"]
        cards_to_hold           = ["Aether Wildfire", "Kindle", "Energy Potion", "Blazing Aether", "Lesson in Lava", "Potion of Deja Vu"]

        spindle_optimal_pitch  = 6
        flare_optimal_pitch    = 5
        
        spindle_minimum_pitch  = 3
        flare_minimum_pitch    = 5

        card_play_options       = list[Card2]()
        card_arsenal_options    = list[Card2]()
        card_hold_options       = list[Card2]()

        # We don't want to play lesson if we have the combo pieces already
        if self.has_wf:
            action_play_priority.remove("Lesson in Lava")

        # We might want to play the arsenal out
        if self.player.arsenal.has_card:
            arsenal_card = self.player.arsenal.get_card()

            if arsenal_card is not None and arsenal_card.card_name in action_play_priority:
                card_play_options.append(arsenal_card)
            
        # We might want to play or arsenal a card in hand
        for hand_card in self.player.hand.cards:
            if hand_card.card_name in arsenal_target_priority:
                card_arsenal_options.append(hand_card)
            
            if hand_card.card_name in action_play_priority:
                card_play_options.append(hand_card)

        # Sort the arrays, such that the leftmost is the card we most want
        card_play_options.sort(key=lambda x: action_play_priority.index(x.card_name))
        card_arsenal_options.sort(key=lambda x: arsenal_target_priority.index(x.card_name))

        wants_to_arsenal = len(card_arsenal_options) > 0

        if wants_to_arsenal:
            if self.player.arsenal.has_card:
                if arsenal_target_priority.index(self.player.arsenal.get_card().card_name) < arsenal_target_priority.index(card_arsenal_options[0].card_name): # type: ignore

                    # If the arsenal is a higher prioirty than the "best" option, don't arsenal a card
                    # Unless, we're going to play the arsenal out anyway

                    if len(card_play_options) and card_play_options[0].zone == "arsenal":
                        card_play_options[0].intent = "play"
                        card_arsenal_options[0].intent = "arsenal"

                else:

                    # The card in arsenal is a lower priority than one in hand
                    # Its now our first priority to play
                    self.player.arsenal.get_card().intent = "play" # type: ignore
                    card_arsenal_options[0].intent = "arsenal"
            else:
                card_arsenal_options[0].intent = "arsenal"

        # Allocate the card to play 
        if not any(card.intent == "play" for card in card_play_options):
            card_play_options[0].intent = "play"

        # Note all other cards as hold or pitch as needed
        for card in self.player.hand.cards:
            if card.intent != "play" and card.intent != "arsenal":
                if card.card_name in cards_to_hold:
                    card.intent = "hold"
                else:
                    card.intent = "pitch"
        
        action_card = self.player.get_card_by_intent("play")
        pitch_intent = self.player.get_pitch_intent()

        # Work out how many resources we should be holding
        if action_card is not None:

            if action_card.card_name == "Aether Spindle":
                if pitch_intent >= spindle_optimal_pitch:
                    pitch_to_hold = spindle_optimal_pitch
                elif pitch_intent > spindle_minimum_pitch:
                    pitch_to_hold = spindle_minimum_pitch
                else:
                    raise Exception(f"Decided on an action to play spindle, but have no way of paying for it")
        
            elif action_card.card_name == "Aether Flare":
                if pitch_intent >= flare_optimal_pitch:
                    pitch_to_hold = flare_optimal_pitch
                elif pitch_intent > flare_minimum_pitch:
                    pitch_to_hold = flare_minimum_pitch
                else:
                    raise Exception(f"Decided on an action to play aether flare, but have no way of paying for it")
                
            else:
                pitch_to_hold = action_card.cost

        # Use the rest to kano
        spare_pitch = pitch_intent - pitch_to_hold

        self.kanos_dig_opponent_turn = spare_pitch // 3

    # Decide what action should be taken with a topdeck card
    def decide_kano_result(self, card: Card2):

        card_is_brick   = card.card_type != "action"

        if card_is_brick:
            return "brick"

        card_is_potion  = card.card_name in POTIONS
        card_is_combo   = card.card_name in COMBO_CORE
        card_is_extender= card.card_name in COMBO_EXTENDERS
        
        if self.state == "setup":

            if card_is_potion:
                return "play"
            
            if card_is_combo or card_is_extender:
                return "assess_combo"
        
        if self.state == "topdeck_combo" or self.state == "combo":
            return "play"
        
        return "banish"
            



