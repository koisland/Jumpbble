import random

# import enchant
import numpy as np
from typing import Dict

from .player import Player


class Board:
    SPECIAL_TILES_PERC = 0.10

    def __init__(
        self, player: Player, size: int, special_tiles_dist: Dict[str, float]
    ) -> None:
        self.player = player
        self.size = size
        self.special_tiles_dist = special_tiles_dist.items()
        self.board = self._init_board()

    def _init_board(self):
        board = np.chararray((self.size, self.size))
        board[:] = "-"

        n_special_tiles = int(self.size * self.size * self.SPECIAL_TILES_PERC)
        all_coords = list(np.ndindex(board.shape))
        special_tiles = random.sample(all_coords, n_special_tiles)

        for sample_tile in special_tiles:
            x, y = sample_tile
            board[x, y] = "?"

    def _check_valid_move(self):
        pass

    def _roll_effect(self):
        pass

    def place_tile(self, x: int, y: int):
        pass
