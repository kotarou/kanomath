from __future__ import annotations

from loguru import logger
from kanomath.cards import Card
from kanomath.cards.card import COMBO_CORE, COMBO_EXTENDERS
from kanomath.cards.potions import POTIONS
from kanomath.functions import card_is_blue, match_card_name, remove_all_matching, remove_first_matching

from typing import TYPE_CHECKING
if TYPE_CHECKING:

    from kanomath.player import Player

# Braino is responsible for all player decisions
# In theory, braino should play optimally based on some constraints on "personality"

combo_extenders     = ["Overflow the Aetherwell", "Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal", "Sonic Boom"]
combo_big_hitters   = ["Aether Flare", "Lesson in Lava", "Blazing Aether", "Aether Wildfire"]
combo_core_pieces   = ["Kindle", "Aether Wildfire", "Lesson in Lava", "Blazing Aether"]

combo_draw_2        = ["Open the Flood Gates", "Tome of Aetherwind", "Tome of Fyendal"]
combo_draw_1        = []

class Braino:

    combo_critical_resources = 11

    def __init__(self, player: Player):

        # Initial state
        self.player     = player
        self.state      = "setup"
        self.topdeck_actions = list[str]()

        # Play patterns & decision
        self.use_tunic          = False
        self.use_spellfire      = True

        self.proactively_arsenal_blazing    = False
        self.proactively_arsenal_gaze       = False
        self.play_pitch_risky               = True

        self.rags_card_pitch            = 1
        self.num_epots   = 0
        self.num_dpots   = 0
        self.num_cpots   = 0

        # Tracking variables for the turn
        self.combo_has_wf               = False
        self.combo_has_blazing          = False
        self.combo_has_lesson           = False

        self.combo_pitch_guaranteed     = False
        self.combo_pitch_risky          = False

        self.combo_lesson_find_blazing  = False

        self.combo_ready                = False
        self.combo_ready_if_wf          = False
        self.combo_ready_if_lesson      = False
        self.combo_ready_if_blazing     = False
        self.combo_ready_if_pitch       = False

        

    def evaluate_state(self):

        # What card form hand is going to be used for rags?
        # We assume a card is always rags'd from hand for the relevant methods here, because we're just estimating pitch
        if self.combo_lesson_find_blazing and self.player.combo_card_location("Lesson in Lava") == "hand":
            self.rags_card_pitch = 2
        else:
            if self.player.hand.size:
                self.rags_card_pitch = min(card.pitch for card in self.player.hand.cards)
            else:
                self.rags_card_pitch = 0
        
        self.num_epots = self.player.arena.count_cards_name("Energy Potion")
        self.num_dpots = self.player.arena.count_cards_name("Potion of Deja Vu")
        self.num_cpots = self.player.arena.count_cards_name("Clarity Potion")

        self.topdeck_actions.clear() 

        self.has_wf         = self.player.has_combo_card("Aether Wildfire")
        self.has_blazing    = self.player.has_combo_card("Blazing Aether")
        self.has_lesson     = self.player.has_combo_card("Lesson in Lava")

        self.combo_pitch_guaranteed = self.evaluate_combo_pitch("safe") >= self.combo_critical_resources
        self.combo_pitch_risky      = self.evaluate_combo_pitch("risky") >= self.combo_critical_resources

        self.combo_lesson_find_blazing = self.has_wf and self.has_lesson and not self.has_blazing

        pitch_ready = self.combo_pitch_risky if self.play_pitch_risky else self.combo_pitch_guaranteed

        self.combo_ready                = self.has_wf and pitch_ready and (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_wf          = self.has_blazing and pitch_ready and not self.has_wf
        self.combo_ready_if_lesson      = self.has_wf and pitch_ready and not (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_blazing     = self.has_wf and pitch_ready and not (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_pitch       = self.has_blazing and (self.has_lesson or self.has_blazing) and not pitch_ready

        if self.combo_ready:
            self.state = "combo"

    def evaluate_combo_pitch(self, strategy: str = "safe"):

        total_pitch = 0
        num_kindles = 0

        for card in self.player.hand.cards:

            if card.card_type == "Kindle":
                num_kindles += 1
                continue
            
            total_pitch += card.pitch
        
        # Chest
        if (self.use_tunic and self.player.tunic_counters == 3) or self.use_spellfire:
            total_pitch += 1
        
        # Energy potions in arena
        total_pitch += 2 * self.num_epots

        # Chances are, we will use rags
        total_pitch -= self.rags_card_pitch
        draw_card_pitch = 1 if strategy == "safe" else 3

        total_pitch += (draw_card_pitch * num_kindles)  # kindle
        total_pitch -= self.rags_card_pitch
        total_pitch += draw_card_pitch                  # rags

        return total_pitch
        
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
            # print(best_play)

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
            elif current_arsenal.card_name == best_arsenal.card_name:
                # If the best card is already in the arsenal,  just pass. 
                pass
            else:
                # Play the current arsenal out
                # And switch the intent of our best play to "hold" for next turn
                # TODO logic for when holding arsenal is better
                # logger.debug(f"Want to swap out current arsenal ({current_arsenal}) for {best_arsenal}")

                current_arsenal.intent = "play"
                if best_play is not None and best_play is not current_arsenal:
                    best_play.intent = "hold"
                best_play = current_arsenal
                best_arsenal.intent = "arsenal"
            
                # logger.debug(f"Want to swap out current arsenal ({current_arsenal}) for {best_arsenal}")

            
            option_hold.extend(option_arsenal)
    
        if len(option_hold):
            seen = list[str]()

            if best_arsenal is not None:
                seen.append(best_arsenal.card_name)

            # Remove duplicates, but we're happy to keep potions
            for card in option_hold:
                if card.zone == "arsenal":
                    seen.append(card.card_name)
                    continue

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
        logger.decision(f"Planning to kano {self.kanos_dig_opponent_turn} times with the {pitch_available} availble (other method: {self.evaluate_combo_pitch('safe')})")

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
            
            if (card_is_combo or card_is_extender) and self.has_wf and not self.player.is_player_turn:
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
