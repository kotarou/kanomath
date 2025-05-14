from kanomath.zones import Arena, Arsenal, Banish, Deck, Discard, Hand, Pitch, Zone


class Player2:
    
    # This will be used to identify card owners when needed in print statements
    id = "player"

    # We have a few relevant zones
    hand: Hand
    arena: Arena
    pitch: Pitch
    discard: Discard
    banish: Banish
    deck: Deck
    
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

        self.hand = Hand(self.base_intellect)
        self.arena = Arena()
        self.arsenal = Arsenal(self.max_cards_in_arsenal)
        self.pitch = Pitch()
        self.discard = Discard()
        self.banish = Banish()
        self.deck = Deck()

    

    def get_zone_by_name(zone_name: str) -> Zone:

        match zone_name:
            case "hand":
                return self.hand
            case "deck":
                return self.deck
            case "discard" | "grave" | "graveyard":
                return self.discard
            case "pitch":
                return self.pitch               
            case "banish" | "exile":
                return self.banish     
            case "arena":
                return self.arena        
            case _:
                raise Exception("Attempting to access zone that doesn't exist: {zone_name}")