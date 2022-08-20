# Jumpbble
Jump-based Scrabble roguelike.


## Player Movement
Players can move in the four cardinal direction.
* Mechanic altered with the `Diagonal` effect

Number of spaces is based on the index of the current letter tile:
* A -> 1
* B -> 2
* Blank -> Any number of spaces.

Moves at the edge of the grid continue on the the opposite edge of the grid.

## Effects
Effects are triggered by landing on a special, randomized tile.

Seven effects are implemented:
1. Ordered
2. Diagonal
3. Wildcard
4. Jump
5. Blind
6. Erase
7. Mirror
