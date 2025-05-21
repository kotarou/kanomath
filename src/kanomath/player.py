from loguru import logger
from kanomath.braino import Braino
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
        
        if action == "wait":
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

        # TODO: assess nodes and crucible activations

        if self.pitch_floating < card.cost:
            self.pitch_best_cards(card.cost -self.pitch_floating )

        if self.pitch_floating >= card.cost:
            self.spend_pitch(card.cost, card.card_name)
            card.on_play()

            if card.card_class == "wizard" and card.card_type == "action":
                self.wizard_naa_played += 1

            if card.deals_arcane and card.arcane_dealt:
                card.on_damage(card.arcane_dealt)


        else:
            # TODO: pitch to play the
            logger.warning(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")
            # raise Exception(f"Cannot afford {card}, cost ({card.cost}), with {self.pitch_floating} resources floating.")



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


    def play_opponent_turn(self, game_first_turn = False):

        # TODO: special handling of first turn opts & etc
        self.prepare_turn()

        opp_turn_pitch      = self.braino.decide_pitch_opp_turn()
        num_kanos_aim       = opp_turn_pitch // 3
        num_kanos_completed = 0
        
        pitch_cards = self.get_cards_by_intent("pitch")
        pitch_cards.sort(key = lambda x : x.pitch, reverse=True)

        logger.decision(f"Aiming to kano up to {num_kanos_aim} times in opponent's turn using {opp_turn_pitch} pitch.")

        should_continue = num_kanos_aim > 0


        while(should_continue):
            
            self.pitch_best_cards(3)

            # If we can't afford to kano any more (chanes are we played a spindle in their turn), then stop
            if self.pitch_floating < 3:
                break
            
            # TODO: assess maybe comboing based on the kano result
            self.kano()
            num_kanos_completed += 1

            # Continue only if 1) we didn;t run out of pitch, and 2) we haven't kano'd as many times as we'd like
            if should_continue:
                should_continue = num_kanos_completed < num_kanos_aim




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
            
        # logger.info(f"Player drew {self.current_intellect - self.hand.size} cards for end of their turn.")
        
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
        #     logger.system(f"Beginning player{'\'s first' if game_first_turn else ''} turn")
        # else:
        #     logger.system(f"Beginning opponent{'\'s first' if game_first_turn else ''} turn")

        self.crucible_used      = False
        self.wizard_naa_played  = 0

    
        self.braino.evaluate_state()

        if game_first_turn or not self.is_player_turn:
            self.braino.cycle_make_initial_decisions()

        logger.info(f"Player hand: {self.hand}, arsenal: {self.arsenal}, arena: {self.arena}.")

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
        

