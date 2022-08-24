import random
import numpy as np
from typing import Dict, Generator, Tuple

from .player import Player


class Board:
    EMPTY_CHAR = ""
    STARTING_POS_CHAR = b"@"
    SPECIAL_TILE_CHAR = b"?"
    DEFAULT_CHARS = (EMPTY_CHAR, STARTING_POS_CHAR, SPECIAL_TILE_CHAR)
    SPECIAL_TILES_PERC = 0.10

    def __init__(
        self, player: Player, size: int, special_tiles_dist: Dict[str, float]
    ) -> None:
        self.player = player
        self.size = size
        self.special_tiles_dist = special_tiles_dist
        self.grid = self._init_board()

    def _init_board(self):
        # Allow characters of up to 1-len
        board = np.chararray((self.size, self.size), itemsize=1)
        board[:] = ""

        n_special_tiles = int(self.size * self.size * self.SPECIAL_TILES_PERC)

        # Don't allow center tile.
        all_coords = list(np.ndindex(board.shape))
        all_coords.remove(self.player.position)

        special_tiles = random.sample(all_coords, n_special_tiles)

        for sample_tile in special_tiles:
            x, y = sample_tile
            board[x, y] = self.SPECIAL_TILE_CHAR

        board[self.player.position] = self.STARTING_POS_CHAR
        return board

    def _roll_effect(self) -> str:
        rolled_effect = random.choices(
            population=list(self.special_tiles_dist.keys()),
            weights=list(self.special_tiles_dist.values()),
            k=1,
        )
        return rolled_effect[0]

    def calc_coords(self, x: int, y: int, dx: int, dy: int) -> Tuple[int, int]:
        # Add change in x and y but loop across board if over board dim size.
        new_x = (x + dx) % self.size
        new_y = (y + dy) % self.size
        return (new_x, new_y)

    def find_words(self) -> Generator:
        # For each axis on grid.
        for i in range(0, 2):
            # For each row/col on grid.
            for axis_idx in range(self.grid.shape[i]):
                # Get row or col based on if x or y.
                axis_vals = self.grid[axis_idx, :] if i == 0 else self.grid[:, axis_idx]
                # And find any unique characters.
                unique_chars = np.unique(axis_vals)

                # Skip any row/col with only default characters.
                if all(char in self.DEFAULT_CHARS for char in unique_chars):
                    continue

                words = []
                word = ""
                for char in axis_vals:
                    # On empty space. Stop appending characters to word.
                    if char == "":
                        # If word is not one character, add.
                        if len(word) > 1:
                            words.append(word)
                        # Reset word
                        word = ""
                        continue
                    if char not in self.DEFAULT_CHARS:
                        word += char.decode()

                yield from words

    def place_piece(
        self,
        coord_change: Tuple[int, int],
        char: str,
        *,
        update_player_pos: bool = True
    ):
        dx, dy = coord_change
        current_x, current_y = self.player.position

        # Add change in x and y but loop across board if over board dim size.
        new_x, new_y = self.calc_coords(current_x, current_y, dx, dy)

        landed_on_tile = self.grid[new_x, new_y]

        if landed_on_tile == self.SPECIAL_TILE_CHAR:
            # Roll effect
            effect = self._roll_effect()

            # Apply effect and decay rate based on status
            self.player.status.get(effect) + self.player.status_decay

            # Erase special tile
            self.grid[new_x, new_y] = char

        if landed_on_tile == "" or self.player.status.get("erase").turns != 0:
            self.grid[new_x, new_y] = char

        if update_player_pos:
            self.player.position = (new_x, new_y)
