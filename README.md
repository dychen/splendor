# Splendor
Training an AI over the board game Splendor (original, not the expansions)
https://en.wikipedia.org/wiki/Splendor_(game)

Using card data from here:
https://drive.google.com/file/d/0B4yyYVH10iE5VlBFME9QelBVUnc/edit

# Playing
```
$ python game.py

[Long printout of game state, see "Board state" section below]

>> Move? [t3/t2/r/b/br] [data]:
# Possible moves:

# Take three gems
>> t3 [5-element array of the number of gems to take of each color in the order: W,U,G,R,B]
# E.g.
>> t3 1 1 1 0 0 # Take one white, one blue, and one green gem. Takes zero red or black gems.
>> t3 0 1 0 1 1 # Take one blue, one red, and one black gem.
>> t3 1 0 0 0 1 # Take one white and one black gem - do this if taking more puts you over the stack limit.

# Take two gems
>> t2 [5-element array of the number of gems to take - should always have one 2 and four 0s]
# E.g.
>> t2 0 0 2 0 0 # Take two green gems.
>> t2 0 0 0 2 0 # Take two red gems.
# Remember that you cannot take two if the corresponding gem stack is below 4.
# If you want to take only 1 gem, use t3 ("take 3") instead (e.g. t3 1 0 0 0 0).

# Reserve a card
>> r [tier - 1, 2, or 3] [index - 0, 1, 2, or 3]
# These are zero-indexed, so 0 is the first card, 1 is the second, etc.
# E.g.
>> r 1 0 # Reserve the first card in Tier 1
>> r 2 1 # Reserve the second card in Tier 2
>> r 3 3 # Reserve the last card in Tier 3

# Buy a card from the board
>> b [tier - 1, 2, or 3] [index - 0, 1, 2, or 3]
# Again, these are zero-indexed
# E.g.
>> b 1 0 # Buy the first card in Tier 1
>> b 3 2 0 Buy the third card in Tier 3
>> b 0 1 # INVALID - can't buy from Tier 0 (tier - 0, index - 1)

# Buy a card from reserves
>> br [index - 0, 1, 2, or 3]
>> br 0 # Buy the first card in your reserve
>> br 1 # Buy the second card in your reserve
```

# Board state
```
=====NEW STATE=====
=TIER 1= # Tier 1 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=TIER 2= # Tier 2 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=TIER 3= # Tier 3 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=NOBLES= # Nobles
[Noble 1]
[Noble 2]
[Noble 3]
[Noble 4]
=GEMS=
[Number of each gem on the board in the following order: White, Blue, Green, Red, Black]
# ^ This gem order is used in all places that use a gem array (e.g. card cost)
=PLAYER [i]= # For each player
  POINTS: [Number of victory points for each player - max of 15]
  NORM GEMS: [Number of each gem the player has in order: W,U,G,R,B] AND [Player gold count]
  CARD GEMS: [Number of gems the player has from cards in order: W,U,G,R,B]
  TOTL GEMS: [Effective total gems the player has from gems + cards] AND [Player gold count]
    CARD: [Card the player owns]
    ...
    RESERVED: [Card the player has reserved]
    ...
    NOBLE: [Noble that has visited the player]
    ...
========END========
```

# Cards
Read card state (7-element array) as follows:
```
[White cost, Blue cost, Green cost, Red cost, Black cost, Gem bonus color (always +1), Points/prestige]
```

# Nobles
Read noble state (6-element array) as follows:
```
[White cost, Blue cost, Green cost, Red cost, Black cost, Points/prestige]
```

# TODOs/Rules questions (unresolved)?
* Can you reserve a card if the gold stack is depleted? Currently, it throws an error
* Add gold to each player's gem limit and handle the case when the player already has 10 gems and reserves a card
* Implement blind reservations
