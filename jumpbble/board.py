import random

# import enchant
import numpy as np
from typing import Dict, Generator

from .player import Player


class Board:
    SPECIAL_TILES_PERC = 0.10

    def __init__(
        self, player: Player, size: int, special_tiles_dist: Dict[str, float]
    ) -> None:
        self.size = size
        self.board = np.chararray((size, size))
        self.board[:] = ""

    def _init_board(self):
        board = np.chararray((self.size, self.size))
        board[:] = ""

        n_special_tiles = int(self.size * self.size * self.SPECIAL_TILES_PERC)
        special_tiles = random.sample(self.coords, n_special_tiles)
        print(special_tiles)

    @property
    def coords(self) -> Generator:
        """
        Generate all coordinates of board given its shape.
        """
        return np.ndindex(self.board.shape)

    def _check_valid_move(self):
        pass

    def place_tile(self, x: int, y: int):
        pass
