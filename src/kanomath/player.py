from loguru import logger
from kanomath.braino import KRESULT, Braino, StateData
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
    _arcane_dealt = 0

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
    def statedata(self) -> StateData:
        return self.braino.statedata
    
    def get_zone_by_name(self, zone_name: str) -> zone.Zone:
        """ Returns a zone within the player"""

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
        
        for card in self.hand:
            if card.intent == intent:
                return card
    
        return None
       
    def get_cards_by_intent(self, intent:str) -> list[Card]:

        output = list[Card]()

        if self.arsenal.has_card:
            if self.arsenal.get_card().intent == intent: # type: ignore
                output.append(self.arsenal.get_card()) # type: ignore
        
        for card in self.hand:
            if card.intent == intent:
                output.append(card)
    
        return output     

    def has_combo_card(self, card_name: str) -> bool:
        
        return self.hand.contains_card_name(card_name) or self.arsenal.contains_card_name(card_name) or self.banish.contains_card_name(card_name)

    def combo_card_location(self, card_name: str) -> str:

        if self.banish.contains_card_name(card_name):
            return "banish"

        if self.arsenal.contains_card_name(card_name):
            return "arsenal"

        if self.hand.contains_card_name(card_name):
            return "hand"
        
        raise Exception(f"Attempting to find combo piece ({card_name}) when it is not present.")

    # def get_pitch_intent(self) -> int:
    #     return reduce(lambda result, card: result + card.pitch, self.get_cards_by_intent("pitch"), 0) 

    # def access_to_card_name(self, card_name: str, allow_banish: bool = True) -> bool:
    #     return self.hand.contains_card_name(card_name) or self.arsenal.contains_card_name(card_name) or (allow_banish and self.banish.contains_card_name(card_name))

    # def count_combo_access_card(self, card_name: str, allow_banish: bool = True) -> int:
    #     return self.hand.count_cards_name(card_name) + self.arsenal.count_cards_name(card_name) + (allow_banish and self.banish.count_cards_name(card_name) if allow_banish else 0)

    def register_amp_next(self, amp_num: int, source: str):

        if(amp_num < 0):
            raise ValueError(f"Cannot amp next spell less than 0 ({amp_num}).")

        self._amp_next += 1
    
    def register_wildfire_amp(self, amp_num: int):

        if(amp_num < 0):
            raise ValueError(f"Cannot amp next spell less than 0 ({amp_num}).")

        self._amp_wildfire += 1

    def register_amp(self, amp_num: int, source: str):
        
        if(amp_num < 0):
            raise ValueError(f"Cannot amp less than 0 ({amp_num}).")
        
        self._amp += 1

    def register_arcane_damage(self, amp_num: int, source: str):
        
        if(amp_num < 1):
            return
        
        self._arcane_dealt += amp_num

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

    def make_token(self, token_name):
        pass

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

        if action == KRESULT.BRICK:
            logger.action(f"Player activated kano, seeing {card} and bricking.")
            # We could set num_kanos to 0 here to stop kanoing
            # But contonueing to kano into bricks allows for more hand cycling
            return
        
        if action == KRESULT.WAIT:
            logger.action(f"Player activated kano, seeing {card} and waiting to draw it next turn.")
            # We could set num_kanos to 0 here to stop kanoing
            # But contonueing to kano into bricks allows for more hand cycling
            return

        elif action == "assess_combo":
            logger.action(f"Player activated kano, seeing {card}. Switching to assess a cheeky combo kill.")
            # We might be able to go off with this card
            # TODO: implement this
            # For now, assume seeing a combo piece in this situation is just a brick
            return
    
        elif action == KRESULT.BANISH:
            logger.action(f"Player activated kano, seeing {card}. Banishing it to thin deck.")
            card.move_to_zone("banish")

        elif action == KRESULT.PLAY:
            logger.action(f"Player activated kano, seeing {card}. Banishing it to play as an instant.")
            card.move_to_zone("banish")

            self.play_card(card, as_instant=True)

        else:
            raise Exception(f"Attempted to resolve a kano with an illegal outcome ({action}).")



    def pitch_best_cards(self, target_pitch: int):

        # Need 1: R > Y > B
        # Need 2: RR > Y > B
        # Need 3: RRR > YR > B > YY
        # General strategy is to pitch until we hit exact, and if we would overhsoot, instead skip the first card we checked and try again

        min_idx = 0
        pitch_cards = list[Card]()
        solution = False
        attempt_optimal = True
        
        while not solution:
            
            pitch_cards.clear()
            pitch_candidates = self.get_cards_by_intent("pitch")
            pitch_candidates.sort(key = lambda x : x.pitch) # smallest first
            pitch   = self.pitch_floating
            
            for idx in range(min_idx, len(pitch_candidates)):
                card = pitch_candidates[idx]
        
                pitch += card.pitch
                pitch_cards.append(card)

                if pitch == target_pitch or (not attempt_optimal and pitch > target_pitch):
                    solution = True
                    break
                elif pitch > target_pitch and attempt_optimal:
                    min_idx += 1
                    break
                else:
                    continue
            
            if min_idx >= len(pitch_candidates) - 1:
                # There is no optimal pitch solution
                if attempt_optimal:
                    attempt_optimal = False
                    min_idx = 0
                else:
                    break

        pitch_total = sum(x.pitch for x in pitch_cards)

        if pitch_total < target_pitch:
            logger.warning(f"Pitching {pitch_cards} was insufficient ({pitch_total} / {target_pitch}).")
            # raise Exception(f"Pitching {pitch_cards} was insufficient ({pitch_total} / {target_pitch}). Hand is {self.hand}")
        else:
            for card in pitch_cards:
                self.pitch_card(card)

    def activate_crucible(self):
        
        if self.pitch_floating < 1:
            raise Exception(f"Attempting to use crucible with only {self.pitch_floating} resources available (need 1).")

        if self.crucible_used:
            raise Exception(f"Attempting to use crucible a second time in one turn.")

        self.register_amp_next(1, "crucible")
        self.crucible_used = True


    def prepare_turn(self, game_first_turn = False):

        self.is_player_turn     = not self.is_player_turn
        
        if self.is_player_turn:
            self.action_points  = 1

        self.crucible_used      = False
        self.wizard_naa_played  = 0

        self._arcane_dealt      = 0
        self._amp_wildfire      = 0
        self._amp_next          = 0
        self._amp               = 0

        self.braino.evaluate_state()

        if game_first_turn or not self.is_player_turn:
            self.braino.cycle_make_initial_decisions()
        
        self.braino.evaluate_state2()

        logger.info(f"Player hand: {self.hand}, arsenal: {self.arsenal}, arena: {self.arena}.")


    def play_opponent_turn(self, game_first_turn = False):
        """ Once in this method, all preperation for the turn is complete. We simply need to execute the turn: no decisions should be made. """
       
        if self.statedata.kano_opp_turn:
            self.pitch_best_cards(3)
            self.kano()
        
        self.play_out_banish()


    def play_own_turn(self, game_first_turn = False):

        # Pitch all cards to begin our turn. 
        # This works out in theory, because theres no method by which any comboination of cards can't be cleared by kanoing
        #   or pitching to crucible in both turns
        for card in self.get_cards_by_intent("pitch"):
            self.pitch_card(card)

        action_card = self.get_card_by_intent("play")

        # Some actions - e.g., gaze the ages - want a card to be played first
        # Others don't care about the card being played, they simply need information
        if self.statedata.kano_before_action and self.pitch_floating >= 3:
            self.kano()

        if action_card is not None:
            # TODO: make crucible decision here
            self.play_card(action_card)

        if self.statedata.kano_after_action:

            while self.pitch_floating >=3:
                self.kano()

        self.play_out_banish()

        # Clean up any remaining pitch
        while self.pitch_floating >=3:
            self.kano()


    def play_out_banish(self) -> None:

        for idx in reversed(range(len((self.banish.cards)))):
            card = self.banish.cards[idx]

            if self.pitch_floating >= card.cost:
                self.play_card(card, True)



    def end_turn(self, game_first_turn = False):

        # EoT tokens trigger here
        #

        # Arsenal a card
        if self.is_player_turn:
            potential_arsenal_cards = self.get_cards_by_intent("arsenal")
            if len (potential_arsenal_cards) > 1:
                raise Exception(f"Player has indicated more than one card to put in arsenal: {potential_arsenal_cards}.")
        
            elif len (potential_arsenal_cards) == 1:
                self.arsenal_card(potential_arsenal_cards[0])

        # Move cards in pitch to bottom of deck
        for idx in reversed(range(self.pitch.size)):
            card = self.pitch.cards[idx]

            zone.Zone.move_card_to_zone(card, "deck", "bottom")
            card.on_turn_end()
        
        # Move cards in banish to exile, so we can ignore them
        for idx in reversed(range(self.banish.size)):
            card = self.banish.cards[idx]

            zone.Zone.move_card_to_zone(card, "exile")
            card.on_turn_end()

        # Untapping happens here, if that should ever be relevant
        ##

        # Clear turn variables
        self.action_points      = 0        
        self.pitch_floating     = 0
        
        # Draw up
        if self.is_player_turn or game_first_turn:
            self.hand.draw_up()



    def arsenal_card(self, card: Card):

        if self.arsenal.size > 0:
            raise Exception(f"Attempting to arsenal {card} when {self.arsenal.get_card()} is already in the arsenal).")

        # print(f"  Arsenalling {card}.")
        zone.Zone.move_card_to_zone(card, "arsenal")

    def pitch_card(self, card: Card):

        if card.pitch == 0:
            raise Exception(f"Attempting to pitch {card} with pitch value {card.pitch}.")

        # print(f"  Pitching {card}. {{r}} {self.pitch_floating} -> {self.pitch_floating + card.pitch}. Hand: {self.hand.size - 1} left.")
        card.on_pitch()
    
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

        # TODO: assess nodes and crucible activations

        if self.pitch_floating < card.cost:
            self.pitch_best_cards(card.cost -self.pitch_floating )

        if self.pitch_floating >= card.cost:
            self.spend_pitch(card.cost, card.card_name)
            
            card.on_play()
            card.on_resolve()

            if card.card_class == "wizard" and card.card_type == "action":
                self.wizard_naa_played += 1

            if card.deals_arcane and card.arcane_dealt:
                card.on_damage(card.arcane_dealt)

            if card.zone == "hand":
                # Its a gaze the ages, and has come back to hand
                card.intent = "pitch"
                self.pitch_card(card)
                logger.debug("spun a gaze the ages")



        else:
            # TODO: pitch to play the
            logger.warning(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")
            # raise Exception(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")
    
    def draw_card(self, draw_num: int = 1):

        if draw_num < 1:
            raise ValueError(f"Cannot draw fewer than 1 cards ({draw_num}).")
        
        self.deck.draw(draw_num)