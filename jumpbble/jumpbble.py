import sys
import json

# import random
import traceback
import pathlib
from typing import Dict

from .board import Board
from .player import Player


class Jumpbble:
    BOARD_SIZE = 15
    CFG_DIR = pathlib.Path(__file__).parents[1].joinpath("config")

    def __init__(self):
        self.turns = 0
        self.player = Player(char="@")
        self.board = Board(
            player=self.player,
            size=self.BOARD_SIZE,
            special_tiles_dist=self._load_special_tiles(),
        )
        self.letters = self._load_letters()

    def _load_special_tiles(self) -> Dict[str, float]:
        try:
            with open(self.CFG_DIR.joinpath("special_tiles.json")) as json_stream:
                return json.load(json_stream)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def _load_letters(self) -> Dict[str, float]:
        try:
            with open(self.CFG_DIR.joinpath("letters.json")) as json_stream:
                return json.load(json_stream)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def start(self):
        self.turns += 1

    def reset(self):
        pass

    def load(self):
        pass

    def save(self):
        pass
