import sys
import json
import pygame
import random
import traceback
import pathlib
from typing import Dict
from itertools import chain

from .board import Board
from .player import Player


class Jumpbble:
    BOARD_DIM = 15
    BOARD_BG_COLOR = (202, 164, 114)
    BOARD_GRID_COLOR = (200, 200, 200)
    BOARD_FONT_COLOR = (101, 67, 33)
    WINDOW_X = 450
    WINDOW_Y = 600
    BOARD_BLOCK_WIDTH = WINDOW_X // BOARD_DIM

    CFG_DIR = pathlib.Path(__file__).parents[1].joinpath("config")

    def __init__(self):
        self.turns = 0
        self.player = Player(char=b"@")
        self.board = Board(
            player=self.player,
            size=self.BOARD_DIM,
            special_tiles_dist=self._load_special_tiles(),
        )
        self.letters = self._load_letters()
        # Generate all letters based on number.
        self.letters_dist = list(
            chain(
                *[[letter] * mdata["Number"] for letter, mdata in self.letters.items()]
            )
        )
        # Initialize bag order from random sample.
        self.bag_idx = 0
        self.bag = random.sample(self.letters_dist, len(self.letters_dist))

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
        screen = pygame.display.set_mode([self.WINDOW_X, self.WINDOW_Y])
        pygame.display.set_caption("Jumpbble")

        board_char_font = pygame.font.SysFont("Arial", 25)
        ui_next_char_font = pygame.font.SysFont("Arial", 100)
        ui_char_font = pygame.font.SysFont("Arial", 50)
        ui_stats_font = pygame.font.SysFont("Arial", 30)

        while True:
            screen.fill(self.BOARD_BG_COLOR)
            self._render_ui(screen, ui_stats_font)
            self._render_board(screen, board_char_font)
            self._render_next_chars(screen, ui_next_char_font, ui_char_font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        print("Moving W")
                        self.bag_idx += 1
                    elif event.key == pygame.K_a:
                        print("Moving A")
                    elif event.key == pygame.K_s:
                        print("Moving S")
                    elif event.key == pygame.K_d:
                        print("Moving D")
                    elif self.player.is_affected("diagonal"):
                        print("Moving diagonally.")

            pygame.display.update()

    def _render_ui(self, screen, char_font):
        x_ui_rect, y_ui_rect = [5, self.WINDOW_X + 5]
        # Draw UI bbox.
        ui_rect = pygame.Rect(
            x_ui_rect, y_ui_rect, self.WINDOW_X - 10, self.WINDOW_Y - self.WINDOW_X - 10
        )
        pygame.draw.rect(screen, self.BOARD_FONT_COLOR, ui_rect, 2)

        x_middle_ui_rect = ((self.WINDOW_X - 10) - x_ui_rect) // 2
        stats_rect = pygame.Rect(
            x_middle_ui_rect,
            y_ui_rect,
            (self.WINDOW_X - 10) // 2,
            self.WINDOW_Y - self.WINDOW_X - 10,
        )
        pygame.draw.rect(screen, self.BOARD_FONT_COLOR, stats_rect, 2)

        # Draw index of current character, # characters left, # characters placed
        x_middle_ui_rect = ((self.WINDOW_X - 10) - x_ui_rect) // 2
        current_idx_msg = f"Current: {self.bag_idx + 1}"
        left_msg = f"Left: {len(self.bag) - (self.bag_idx + 1)}"
        score_msg = f"Score: {1}"

        screen.blit(
            char_font.render(current_idx_msg, True, self.BOARD_FONT_COLOR),
            (x_middle_ui_rect + 30, y_ui_rect + 20),
        )
        screen.blit(
            char_font.render(left_msg, True, self.BOARD_FONT_COLOR),
            (x_middle_ui_rect + 30, y_ui_rect + 55),
        )
        screen.blit(
            char_font.render(score_msg, True, self.BOARD_FONT_COLOR),
            (x_middle_ui_rect + 30, y_ui_rect + 90),
        )

    def _render_next_chars(self, screen, next_char_font, char_font):

        x_pos, y_pos = 30, self.WINDOW_X + 30

        for i, char in enumerate(self.bag[self.bag_idx :], 1):
            if i == 4:
                break
            # Render the immediate next character with larger font.
            if i == 1:
                screen.blit(
                    next_char_font.render(char, True, self.BOARD_FONT_COLOR),
                    (x_pos, y_pos),
                )
            else:
                screen.blit(
                    char_font.render(char, True, self.BOARD_FONT_COLOR),
                    (x_pos + (40 * i - 1), y_pos),
                )

    def _render_board(self, screen, char_font):
        for x in range(0, self.WINDOW_X, self.BOARD_BLOCK_WIDTH):
            for y in range(0, self.WINDOW_X, self.BOARD_BLOCK_WIDTH):
                rect = pygame.Rect(x, y, self.BOARD_BLOCK_WIDTH, self.BOARD_BLOCK_WIDTH)
                x_coord, y_coord = (
                    x // self.BOARD_BLOCK_WIDTH,
                    y // self.BOARD_BLOCK_WIDTH,
                )

                board_char = self.board.grid[x_coord, y_coord]
                # Format character so fit within grid.
                if board_char == self.player.char:
                    char_pos = (x + 3, y + 3)
                elif board_char == self.board.SPECIAL_TILE_CHAR:
                    char_pos = (x + 6, y + 5)
                else:
                    char_pos = (x, y)

                # Render characte in grid.
                screen.blit(
                    char_font.render(board_char, True, self.BOARD_FONT_COLOR), char_pos
                )
                pygame.draw.rect(screen, self.BOARD_GRID_COLOR, rect, 1)

    def reset(self):
        pass

    def load(self):
        pass

    def save(self):
        pass
