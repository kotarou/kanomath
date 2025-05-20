## Examples of incorrect lines taken that should be addressed
----

INFO     | kanomath.player:435 | Player hand: [4 cards: Sap [pitch], will of Arcana [pitch], Potion of Deja Vu [play], Overflow the Aetherwell [pitch]], arsenal: [size 1, cards: Blazing Aether], arena: [size 1, cards: Potion of Deja Vu].  
decision | kanomath.player:310 | Aiming to kano 2 times in opponent's turn.  
action   | kanomath.player:243 | Player activated kano, seeing Gaze the Ages. Banishing it to thin deck.  
action   | kanomath.player:243 | Player activated kano, seeing Aether Spindle. Banishing it to thin deck.  
INFO     | kanomath.player:435 | Player hand: [2 cards: Potion of Deja Vu [play], Overflow the Aetherwell [pitch]], arsenal: [size 1, cards: Blazing Aether], arena: [size 1, cards: Potion of Deja Vu].  
action   | kanomath.player:262 | Playing Potion of Deja Vu [play] from hand as an action.  

Incorrect line taken: 
- banish Gaze the Ages to thin, 
- banish Aether Spindle to thin, 
- pitch away overflow red, 
- play dpot #2 as action
  
Correct line: 
- banish both cards, 
- choose to instead pitch the dpot (as one is already played) to crucible -> spindle.
    - if a potion is seen, put it to top
    - else bottom as per normal
- play gaze
    - if a potion is seen, put it to top
    - bottom as per normal
- choose (somehow) to either blind kano the gaze, or crucible overflow as actions, then surge kano

----

INFO     | kanomath.player:492 | Player hand: [4 cards: Aether Wildfire [arsenal], Destructive Aethertide [pitch], Overflow the Aetherwell [pitch], Overflow the Aetherwell [pitch]], arsenal: [size 0, cards: none], arena: [size 0, cards: none].  
action   | kanomath.player:243 | Player activated kano, seeing Prognosticate. Banishing it to thin deck.  
action   | kanomath.player:247 | Player activated kano, seeing Gaze the Ages. Banishing it to play as an instant.  
action   | kanomath.player:262 | Playing Gaze the Ages from banish as an instant.  
decision | kanomath.player:211 | Opt saw 2 cards. Put [] to top and [Sap, Pop the Bubble] to bottom.  

Incorrect line taken: 
- banish Prognosticate to thin, 
- banish Gaze the Ages to thin, 
- play Gaze the Ages

Correct line
- banish Prognosticate to thin, 
- banish Gaze the Ages to thin, 
- play Prognosticate, as it is 0 cost, and enables gaze
- play Gaze the Ages

----

INFO     | kanomath.player:492 | Player hand: [4 cards: Overflow the Aetherwell [pitch], Aether Spindle [play], Aether Arc [pitch], Arcane Twining [pitch]], arsenal: [size 0, cards: none], arena: [size 0, cards: none].  
action   | kanomath.player:262 | Playing Aether Spindle [play] from hand as an action.  
action   | kanomath.player:243 | Player activated kano, seeing Blazing Aether. Banishing it to thin deck.  
action   | kanomath.player:243 | Player activated kano, seeing Pop the Bubble. Banishing it to thin deck.  

Incorrect line taken: 
- Play spindle
- banish Blazing Aether to thin, 
- banish Pop the Bubble to thin, 
- play Gaze the Ages

Correct line
- Play spindle
- check number of blazings in the deck, then choose to banish banish Blazing Aether or not to play
- kano if banishing blazing, banish Pop the bubble,
- play pop then blazing