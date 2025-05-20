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

        num_kanos_aim       = self.braino.decide_kanos_opp_turn()
        logger.decision(f"Aiming to kano {num_kanos_aim} times in opponent's turn.")


        num_kanos_completed = 0

        pitch_cards = self.get_cards_by_intent("pitch")
        pitch_cards.sort(key = lambda x : x.pitch, reverse=True)
       

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
        

