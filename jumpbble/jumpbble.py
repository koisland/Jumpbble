import sys
import json
import pygame

# import random
import traceback
import pathlib
from typing import Dict

from .board import Board
from .player import Player


class Jumpbble:
    BOARD_SIZE = 15
    BOARD_BG_COLOR = (202, 164, 114)
    BOARD_GRID_COLOR = (200, 200, 200)
    WINDOW_DIM = 400
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

    def start(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode([self.WINDOW_DIM] * 2)
        # clock = pygame.time.Clock()
        screen.fill(self.BOARD_BG_COLOR)

        while True:
            self._render_grid(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        print("Moving W")
                    elif event.key == pygame.K_a:
                        print("Moving A")
                    elif event.key == pygame.K_s:
                        print("Moving S")
                    elif event.key == pygame.K_d:
                        print("Moving D")
                    elif self.player.is_affected("diagonal"):
                        print("Moving diagonally.")

            pygame.display.update()

    def _render_grid(self, screen):
        block_width = block_height = 400 // self.BOARD_SIZE
        for x in range(0, self.WINDOW_DIM, block_width):
            for y in range(0, self.WINDOW_DIM, block_height):
                rect = pygame.Rect(x, y, block_width, block_height)
                pygame.draw.rect(screen, self.BOARD_GRID_COLOR, rect, 1)

    def reset(self):
        pass

    def load(self):
        pass

    def save(self):
        pass
