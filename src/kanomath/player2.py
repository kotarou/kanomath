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
        self.banish = zone.Banish()
        self.deck = zone.Deck()

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
            case "banish" | "exile":
                return self.banish     
            case "arena":
                return self.arena        
            case _:
                raise Exception(f"Attempting to access zone that doesn't exist: {zone_name}")
    

    def gain_pitch(self, num_resources: int):
        
        if num_resources < 1:
            raise Exception(f"Attempting to gain {num_resources} pitch. The minimum to gain is 1. ")

        self.pitch_floating += num_resources
