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

        self.rags_card_pitch    = 1
        self.num_epots          = 0
        self.num_dpots          = 0
        self.num_cpots          = 0

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

        # What card from hand is going to be used for rags?
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
        self.pitch_ready            = self.combo_pitch_risky if self.play_pitch_risky else self.combo_pitch_guaranteed


        self.combo_lesson_find_blazing = self.has_wf and self.has_lesson and not self.has_blazing

        self.combo_ready                = self.has_wf and self.pitch_ready and (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_wf          = self.has_blazing and self.pitch_ready and not self.has_wf
        self.combo_ready_if_lesson      = self.has_wf and self.pitch_ready and not (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_blazing     = self.has_wf and self.pitch_ready and not (self.combo_has_lesson or self.combo_has_blazing)
        self.combo_ready_if_pitch       = self.has_blazing and (self.has_lesson or self.has_blazing) and not self.pitch_ready

        if self.combo_ready:
            self.state = "combo"

    def evaluate_combo_pitch(self, strategy: str = "safe", use_rags: bool = True):

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
        
        draw_card_pitch = 1 if strategy == "safe" else 3

        if use_rags:
            total_pitch -= self.rags_card_pitch
            total_pitch += draw_card_pitch              # rags

        total_pitch += (draw_card_pitch * num_kindles)  # kindle

        return total_pitch
        
    def resolve_opt(self, opt_cards:list[Card]) -> tuple[list[Card], list[Card]]:

        # Initial variables
        opt_data = OptData()

        for card in opt_cards:
            if card.card_name == "Aether Wildfire":
                opt_data.has_wf      = True
            elif  card.card_name == "Blazing Aether":
                opt_data.has_blazing = True
            elif card.card_name == "Lesson in Lava":
                opt_data.has_lesson  = True
            elif "Potion" in card.card_name:
                opt_data.has_potion  = True
            elif card.card_name == "Open the Flood Gates" or card.card_name == "Overflow the Aetherwell":
                opt_data.has_surge   = True            
            elif card.card_name == "Tome of Aetherwind" or card.card_name == "Tome of Fyendal":
                opt_data.has_tome    = True   

            if card.pitch == 3:
                opt_data.has_blue    = True


        # state changes
        if self.state == "setup":

            # We could switch to a combo here
            if self.combo_ready_if_wf and opt_data.has_wf:
                self.state = "topdeck_combo"
            elif self.combo_ready_if_blazing and opt_data.has_blazing:
                self.state = "topdeck_combo"
            elif self.combo_ready_if_lesson and opt_data.has_lesson:
                self.state = "topdeck_combo"
            elif self.pitch_ready and (opt_data.has_blazing or opt_data.has_lesson) and opt_data.has_wf:
                self.state = "topdeck_combo"

        
        # Perform opt

        if self.state == "setup":
            return self.resolve_opt_setup(opt_cards, opt_data)
        
        elif self.state == "topdeck_combo":
            return self.resolve_opt_topdeck(opt_cards, opt_data)
        
        elif self.state == "combo":
            return self.resolve_opt_combo(opt_cards, opt_data)

        else:
            raise Exception("Opting in invalid state")


    def resolve_opt_setup(self, opt_cards:list[Card], opt_data: OptData) -> tuple[list[Card], list[Card]]:

        top = list[Card]()

        pot_priority    = {
            "Energy Potion":        10,
            "Potion of Deja Vu":    8 if self.num_dpots == 0 else 4,
            "Clarity Potion":       6 if self.num_cpots == 0 else 2
        }
        pots            = remove_all_matching(opt_cards, match_card_name(list(pot_priority.keys())))

        pots.sort(key= lambda x: pot_priority[x.card_name], reverse = True)
        top.extend(pots)

        # We don't want to keep flood gates / overflow while not comboing
        combo_priority  = {
            "Lesson in Lava":           11 if (not self.has_wf and opt_data.has_wf) else (8 if not (self.has_blazing or self.has_lesson) else 6),
            "Aether Wildfire":          10 if not self.has_wf else 1,
            "Blazing Aether":           9 if not (self.has_blazing or self.has_lesson) else 7,
            "Kindle":                   8,
            "Tome of Aetherwind":       4,
            "Tome of Fyendal":          4,
            "Gaze the Ages":            4,
            "Aether Spindle":           3,
        }

        # If we are playing NAA in our turn, gaze the ages is a good card to top
        action_card = self.player.get_card_by_intent("play")
        if self.player.wizard_naa_played > 0 or (action_card is not None and action_card.card_class == "wizard"):
            combo_priority["Gaze the ages"] = 4



        #"Open the Flood Gates", "Overflow the Aetherwell", "Sonic Boom", "Aether Flare"
        combo_pieces    = remove_all_matching(opt_cards, match_card_name(list(combo_priority.keys())))
        combo_pieces.sort(key= lambda x: combo_priority[x.card_name], reverse = True)

        top.extend(combo_pieces)
        # TODO: topdeck actions

        return top, opt_cards

    
    def resolve_opt_combo(self, opt_cards:list[Card], opt_data: OptData) -> tuple[list[Card], list[Card]]:
            
        top = list[Card]()

        # TODO: these need to be far more precise, especially regarding pitch access
        # However, for now they'll suffice
        combo_priority  = {
            "Lesson in Lava":           11 if (not self.has_wf and opt_data.has_wf) else (8 if not (self.has_blazing or self.has_lesson) else 6),
            "Aether Wildfire":          10 if not self.has_wf else 1,
            "Blazing Aether":           9 if not (self.has_blazing or self.has_lesson) else 7,
            "Kindle":                   8,
            "Open the Flood Gates":     8,
            "Overflow the Aetherwell":  6,
            "Sonic Boom":               5,
            "Tome of Aetherwind":       4,
            "Tome of Fyendal":          4,
            "Gaze the Ages":            4,
            "Aether Flare":             2
        }

        combo_pieces    = remove_all_matching(opt_cards, match_card_name(list(combo_priority.keys())))
        combo_pieces.sort(key= lambda x: combo_priority[x.card_name], reverse = True)

        top.extend(combo_pieces)
        # TODO: topdeck actions

        return top, opt_cards

    def resolve_opt_topdeck(self, opt_cards:list[Card], opt_data: OptData) -> tuple[list[Card], list[Card]]:
            
        top = list[Card]()

        # TODO: these need to be far more precise, especially regarding pitch access. Needs blues underneath.
        # However, for now they'll suffice
        combo_priority  = {
            "Lesson in Lava":           11 if (not self.has_wf and opt_data.has_wf) else (8 if not (self.has_blazing or self.has_lesson) else 6),
            "Aether Wildfire":          10 if not self.has_wf else 1,
            "Blazing Aether":           9 if not (self.has_blazing or self.has_lesson) else 7,
            "Kindle":                   8,
            "Open the Flood Gates":     8,
            "Overflow the Aetherwell":  6,
            "Sonic Boom":               5,
            "Tome of Aetherwind":       4,
            "Tome of Fyendal":          4,
            "Gaze the Ages":            4,
            "Aether Flare":             0
        }

        combo_pieces    = remove_all_matching(opt_cards, match_card_name(list(combo_priority.keys())))
        combo_pieces.sort(key= lambda x: combo_priority[x.card_name], reverse = True)

        top.extend(combo_pieces)
        # TODO: topdeck actions

        return top, opt_cards

    
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
            if card.intent != "" and card.intent != "pitch":
                raise Exception(f"{card} should not have intent, as it is unassigned")
            if card.zone == "arsenal":
                raise Exception(f"Cannot pitch {card} from arsenal!")
            
            card.intent = "pitch"

        # pitch_available = sum((x.pitch if not x.intent == "play" else 0) for x in option_unassinged) - pitch_to_hold

        # self.kanos_dig_opponent_turn = pitch_available // 3 if pitch_available > 0 else 0
        # logger.decision(f"Planning to kano {self.kanos_dig_opponent_turn} times with the {pitch_available} available (other method: {self.evaluate_combo_pitch('safe')})")

    def decide_pitch_opp_turn(self) -> int:

        free_pitch      = 0
        pitch_next_turn = 0
        play_card       = self.player.get_card_by_intent("play")

        for card in self.player.hand:
            if card.intent == "pitch":
                free_pitch += card.pitch

        if play_card is not None:
            pitch_next_turn += play_card.cost

            # Save three more pitch for a kano afterward
            # Reasonably no player will ever play either without a crucible pump
            if play_card.card_name == "Aether Spindle" or play_card.card_name == "Aether Spindle":
                pitch_next_turn += 4
        
            # We always want the crucible pump
            # Just in case a SV1 deck wants to fuck with us I guess?
            if play_card.card_name == "Lesson in Lava" :
                pitch_next_turn += 1

        # return max((free_pitch - pitch_next_turn) // 3, 0)
        return max(free_pitch - pitch_next_turn, 0)

        



    # Decide what action should be taken with a topdeck card
    def decide_kano_result(self, card: Card):

        card_is_brick   = card.card_type != "action"

        if card.card_name == "Aether Wildfire" and self.player.is_player_turn:
            return "wait"

        if card_is_brick:
            return "brick"

        card_is_potion  = card.card_name in POTIONS
        card_is_setup   = card.card_name in ["Gaze the Ages", "Aether Spindle"]
        card_is_combo   = card.card_name in COMBO_CORE
        card_is_extender= card.card_name in COMBO_EXTENDERS
        
        if self.state == "setup":

            if card_is_potion or card_is_setup:
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

        if card.card_name == "Aether Spindle" and card.colour == "red":
            if card.zone == "arsenal":
                return 7
            
            # if self.player.pitch_floating >= 6:
            return 2
            # elif self.player.pitch_floating >= 3:
            #     return 4
            # elif self.player.pitch_floating >= 2:
            #     return 3
            # else:
            #     return 0

        # High priority if to find a wildfire if we lack one
        # TODO: if we resolve this in this fashion, should resolve kanos then play action
        if card.card_name == "Lesson in Lava" and not self.has_wf:
            return 6
            

        
        if card.card_name == "Aether Flare" and card.colour == "red":
            # if self.player.pitch_floating >= 5:
            return 1
            # else:
            #     return 0

        # TODO: Consider playing gaze at action speed
        # TODO: Consider playing cindering at action speed
             
        return 0

class OptData:

    def __init__(self):
        self.has_wf      = False
        self.has_blazing = False
        self.has_lesson  = False
        self.has_potion  = False
        self.has_surge   = False
        self.has_tome    = False
        self.has_blue    = False