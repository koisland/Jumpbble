import sys
import json
import pygame
import random
import traceback
import pathlib
import enchant
from typing import Dict, Tuple, Any, List
from itertools import chain
from collections import defaultdict, deque

from .board import Board
from .player import Player


class Jumpbble:
    BOARD_DIM = 15
    BOARD_BG_COLOR = (202, 164, 114)
    BOARD_GRID_COLOR = (200, 200, 200)
    BOARD_GRID_PLAYER_COLOR = (255, 0, 0)
    BOARD_GRID_POSSIBLE_MOVE_COLOR = (
        (255, 128, 0),
        (255, 255, 0),
        (128, 255, 0),
        (0, 255, 0),
        (0, 255, 128),
        (0, 255, 255),
        (0, 128, 255),
        (0, 0, 255),
    )
    BOARD_FONT_COLOR = (101, 67, 33)
    BOARD_WORD_COLOR = (0, 100, 0)
    WINDOW_X = 450
    WINDOW_Y = 675
    BOARD_BLOCK_WIDTH = WINDOW_X // BOARD_DIM

    N_TILES = 7
    STARTING_POS = (7, 7)
    CFG_DIR = pathlib.Path(__file__).parents[1].joinpath("config")
    RES_DIR = pathlib.Path(__file__).parents[1].joinpath("resources")
    BG_MUSIC = RES_DIR.joinpath("audio", "HoliznaCC0_NPC_Theme.mp3")

    def __init__(self) -> None:
        self.player = Player(position=self.STARTING_POS)
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
        # Assign letter spaces to letters. If letter is wildcard or the length of board, give 0.
        # The length of board is for balance as would always land on same position otherwise.
        self.letter_spaces = {
            letter: (0 if letter == "*" or i == self.BOARD_DIM else i)
            for i, letter in enumerate(list(self.letters), 1)
        }

        # Initialize bag order from random sample.
        self.bag = deque(random.sample(self.letters_dist, len(self.letters_dist)))
        # Give n tiles.
        self.current_tiles = [self.bag.popleft() for _ in range(self.N_TILES)]
        # Selected tile_index
        self.selected_tile = 0
        # Init word checker.
        self.dictionary = enchant.Dict("en_US")
        self.all_words = set()
        self.all_word_pos = set()

        # Debug stuff.
        self.debug_mode = False
        self.debug_input = ""

    def _load_special_tiles(self) -> Dict[str, float]:
        """
        Load special tiles.

        :return: special tiles dictionary where key is effect and value is percent probability.
        """
        try:
            with open(self.CFG_DIR.joinpath("special_tiles.json")) as json_stream:
                return json.load(json_stream)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def _load_letters(self) -> Dict[str, Dict[str, int]]:
        """
        Load letters with number and point value.

        :return: all letters and their movement values and score
        """
        try:
            with open(self.CFG_DIR.joinpath("letters.json")) as json_stream:
                return json.load(json_stream)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def _debug_mode(self, event) -> None:
        # Escape to exit.
        if event.key == pygame.K_ESCAPE:
            print("Exiting debug mode.")
            self.debug_mode = False
            self.debug_input = ""
        # Enter and execute command.
        if event.key == pygame.K_RETURN:
            print(self.debug_input)
            if effect := self.player.status.get(self.debug_input):
                effect + 3
        # Allow editing
        elif event.key == pygame.K_BACKSPACE:
            self.debug_input = self.debug_input[:-1]
            print(self.debug_input)
        # Allow jumping to any position.
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x_px, y_px = pygame.mouse.get_pos()
            current_x, current_y = self.player.position
            clicked_x, clicked_y = (
                x_px // self.BOARD_BLOCK_WIDTH,
                y_px // self.BOARD_BLOCK_WIDTH,
            )
            d_xy = (clicked_x - current_x, clicked_y - current_y)

            self._exec_move(d_xy, self.current_tiles[self.selected_tile])
        else:
            # Add input.
            self.debug_input += event.unicode
            print(self.debug_input)

    def start(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode([self.WINDOW_X, self.WINDOW_Y])
        pygame.display.set_caption("Jumpbble")
        # Setup music
        pygame.mixer.init()
        pygame.mixer.music.load(self.BG_MUSIC)
        pygame.mixer.music.play(-1)

        BOARD_ELEMS = self._get_grid_elem()
        BOARD_CHAR_FONT = pygame.font.SysFont("Arial", 25)
        UI_CHAR_FONT = pygame.font.SysFont("Arial", 25)
        # UI_STATS_FONT = pygame.font.SysFont("Arial", 20)

        self.MOVEMENT_KEYS = {
            pygame.K_w: lambda n_space: (0, n_space * -1),
            pygame.K_a: lambda n_space: (n_space * -1, 0),
            pygame.K_s: lambda n_space: (0, n_space),
            pygame.K_d: lambda n_space: (n_space, 0),
            pygame.K_q: lambda n_space: (n_space * -1, n_space * -1),
            pygame.K_e: lambda n_space: (n_space, n_space * -1),
            pygame.K_z: lambda n_space: (n_space * -1, n_space),
            pygame.K_x: lambda n_space: (n_space, n_space),
        }
        self.MOVEMENT_DIAG_KEYS = (pygame.K_q, pygame.K_e, pygame.K_z, pygame.K_x)
        TILE_KEYS = {
            key: i
            for i, key in enumerate(
                (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                    pygame.K_6,
                    pygame.K_7,
                )
            )
        }

        current_char = self.current_tiles[self.selected_tile]
        n_spaces = self.letter_spaces.get(current_char)
        # Get possible coords that player can land on to render.
        possible_new_coords = self._get_poss_new_coords(n_spaces)

        while True:
            screen.fill(self.BOARD_BG_COLOR)
            self._render_ui(screen)
            self._render_board(screen, BOARD_ELEMS, BOARD_CHAR_FONT)
            self._render_curr_chars(screen, UI_CHAR_FONT)
            self._render_stats(screen, UI_CHAR_FONT)

            # Game over.
            if len(self.current_tiles) == 0:
                self._render_game_over(screen)
                pygame.quit()
                sys.exit(0)
            try:
                current_char = self.current_tiles[self.selected_tile]
                n_spaces = self.letter_spaces.get(current_char)
                possible_new_coords = self._get_poss_new_coords(n_spaces)
            except (IndexError, KeyError):
                continue

            # Render colors. If blind, disable.
            if self.player.is_affected("blind") is False:
                for rgb, (poss_x, poss_y) in zip(
                    self.BOARD_GRID_POSSIBLE_MOVE_COLOR, possible_new_coords
                ):
                    self._render_block(
                        screen,
                        BOARD_ELEMS,
                        poss_x,
                        poss_y,
                        char=None,
                        char_font=BOARD_CHAR_FONT,
                        block_color=rgb,
                    )

            for event in pygame.event.get():
                # Update score after each event.
                for word, word_pos in self.board.find_words():
                    score = self._get_score(word)
                    if score != 0:
                        # Add positions of words to render.
                        for pos in word_pos:
                            self.all_word_pos.add(pos)

                        if word not in self.all_words:
                            self.all_words.add(word)
                            self.player.score += score

                            # If valid word, allow player to jump.
                            self.player.status.get("jump") + 1

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Cycle through letters
                if event.type == pygame.MOUSEBUTTONUP and event.button == 4:
                    if self.selected_tile >= 1:
                        self.selected_tile -= 1
                if event.type == pygame.MOUSEBUTTONUP and event.button == 5:
                    if self.selected_tile < self.N_TILES - 1:
                        self.selected_tile += 1

                # Enable placing on grid by mouse-click.
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    x_px, y_px = pygame.mouse.get_pos()
                    current_x, current_y = self.player.position
                    clicked_x, clicked_y = (
                        x_px // self.BOARD_BLOCK_WIDTH,
                        y_px // self.BOARD_BLOCK_WIDTH,
                    )
                    d_xy = (clicked_x - current_x, clicked_y - current_y)

                    # Jump or wildcard tile.
                    if any([self.player.is_affected("jump"), n_spaces == 0]):
                        self._exec_move(d_xy, current_char)
                    # Allow clicking if move within possible_new_coords.
                    elif (clicked_x, clicked_y) in possible_new_coords:
                        self._exec_move(d_xy, current_char)

                if event.type == pygame.KEYDOWN:
                    # Toggle between tiles.
                    if self.debug_mode:
                        self._debug_mode(event)
                        break

                    if event.key == pygame.K_ESCAPE and self.debug_mode is False:
                        print("In debug mode.")
                        self.debug_mode = True
                        break

                    if event.key in TILE_KEYS:
                        self.selected_tile = TILE_KEYS[event.key]

                    # If wildcard effect or tile, allow any letter.
                    if self.player.is_affected("wildcard") or current_char == '*':
                        wildcard = str(event.unicode).upper()
                        if wildcard in self.letters:
                            self.current_tiles[self.selected_tile] = wildcard
                            break
                        else:
                            break

                    current_char = self.current_tiles[self.selected_tile]
                    n_spaces = self.letter_spaces.get(current_char)
                    possible_new_coords = self._get_poss_new_coords(n_spaces)

                    # For movement.
                    if event.key in self.MOVEMENT_KEYS:
                        # Ignore input if not diagonal movement key.
                        if all(
                            [
                                self.player.is_affected("diagonal"),
                                event.key not in self.MOVEMENT_DIAG_KEYS,
                            ]
                        ):
                            continue
                        if coord_change_func := self.MOVEMENT_KEYS.get(event.key):
                            d_xy = coord_change_func(n_spaces)

                        self._exec_move(d_xy, current_char)

            pygame.display.update()

    def _get_score(self, word: str) -> int:
        if self.dictionary.check(word):
            word_score = sum(
                self.letters[letter.upper()]["Score"] for letter in list(word)
            )
            return word_score
        else:
            return 0

    def _next_letter(self, char: str) -> str:
        letter_list = list(self.letters)
        idx = (letter_list.index(char) + 1) % len(self.letters)
        return letter_list[idx]

    def _exec_move(self, d_xy: Tuple[int, int], current_char: str):
        # Remove placed tile from tiles and replenish tiles.
        self.current_tiles.pop(self.selected_tile)

        try:
            if self.player.is_affected("ordered"):
                next_letter = self._next_letter(current_char)
                # Keep iterating until the next letter found from current character.
                while next_letter not in self.bag:
                    next_letter = self._next_letter(next_letter)

                # Find index of next letter and remove it.
                self.bag.remove(next_letter)
                next_tile = next_letter
            else:
                next_tile = self.bag.popleft()
            self.current_tiles.extend(next_tile)
        except IndexError:
            pass

        # Mirror move by multiple change in x and y by -1.
        if self.player.is_affected("mirror"):
            mirrored_d_xy = [d_var * -1 for d_var in d_xy]
            self.board.place_piece(mirrored_d_xy, current_char, update_player_pos=False)

        # Place tile on board.
        self.board.place_piece(d_xy, current_char)

        # Decay any status effect.
        for _, status in self.player.status.items():
            status - 1

    def _get_poss_new_coords(self, n_spaces) -> List[int]:
        coords = []
        for key, coord_change_func in self.MOVEMENT_KEYS.items():
            # If player affected by diagonal, only move diagonally.
            if all(
                [
                    self.player.is_affected("diagonal"),
                    key not in self.MOVEMENT_DIAG_KEYS,
                ]
            ):
                continue

            coords.append(
                self.board.calc_coords(
                    *coord_change_func(n_spaces), *self.player.position
                )
            )
        return coords

    def _render_game_over(self, screen):
        pass

    def _render_ui(self, screen):
        x_ui_start_pos, y_ui_start_pos = [5, self.WINDOW_X + 5]
        # Draw UI bbox.
        ui_rect = pygame.Rect(
            x_ui_start_pos,
            y_ui_start_pos,
            self.WINDOW_X - 10,
            self.WINDOW_Y - self.WINDOW_X - 10,
        )
        pygame.draw.rect(screen, self.BOARD_FONT_COLOR, ui_rect, 2)

    def _render_stats(self, screen, char_font):
        x_stat_start_pos, y_stat_start_pos = (200, self.WINDOW_X)
        current_effects = [
            f"{status_name}: {status.turns}"
            for status_name, status in self.player.status.items()
            if status.turns != 0
        ]

        stat_texts = [
            f"Level: {self.player.level}",
            f"Tiles Left: {len(self.bag)}",
            f"Score: {self.player.score}",
            f"Words: {len(self.all_words)}",
            "Status:",
        ]
        for i, stat_text in enumerate(stat_texts, 1):
            screen.blit(
                char_font.render(stat_text, True, self.BOARD_FONT_COLOR),
                (x_stat_start_pos, y_stat_start_pos + (25 * i)),
            )
            if i == len(stat_texts):
                for n_effect, effect in enumerate(current_effects, 1):
                    effect = effect.capitalize()
                    screen.blit(
                        char_font.render(effect, True, self.BOARD_FONT_COLOR),
                        (
                            x_stat_start_pos + 25,
                            y_stat_start_pos + (25 * i) + (25 * n_effect),
                        ),
                    )

    def _render_curr_chars(self, screen, char_font):

        x_curr_char_start_pos, y_curr_char_start_pos = (30, self.WINDOW_X)

        for i, char in enumerate(self.current_tiles, 1):
            curr_char_opt_text = f"{i} - {char} ({self.letter_spaces.get(char)})"
            # Show selected char by adding '<'.
            if i == (self.selected_tile + 1):
                curr_char_opt_text = f"{curr_char_opt_text} <"
            screen.blit(
                char_font.render(curr_char_opt_text, True, self.BOARD_FONT_COLOR),
                (x_curr_char_start_pos, y_curr_char_start_pos + (25 * i)),
            )

    def _get_grid_elem(self) -> Dict[Tuple[int, int], Dict[str, Any]]:
        ui_grid = defaultdict(dict)
        for x in range(0, self.WINDOW_X, self.BOARD_BLOCK_WIDTH):
            for y in range(0, self.WINDOW_X, self.BOARD_BLOCK_WIDTH):
                rect = pygame.Rect(x, y, self.BOARD_BLOCK_WIDTH, self.BOARD_BLOCK_WIDTH)
                x_coord, y_coord = (
                    x // self.BOARD_BLOCK_WIDTH,
                    y // self.BOARD_BLOCK_WIDTH,
                )
                ui_grid[(x_coord, y_coord)]["rect"] = rect
                ui_grid[(x_coord, y_coord)]["px_coord"] = (x, y)
        return ui_grid

    def _render_block(self, screen, board_elems, x, y, char, char_font, block_color):
        rect = board_elems[(x, y)]["rect"]
        x_px_pos, y_px_pos = board_elems[(x, y)]["px_coord"]

        if char is None:
            # Render character in grid.
            screen.blit(
                char_font.render(char, True, self.BOARD_FONT_COLOR),
                (x_px_pos, y_px_pos),
            )

        pygame.draw.rect(screen, block_color, rect, 2)

    def _render_board(self, screen, board_elems, char_font):
        for x in range(self.board.grid.shape[0]):
            for y in range(self.board.grid.shape[1]):
                rect = board_elems[(x, y)]["rect"]
                x_px_pos, y_px_pos = board_elems[(x, y)]["px_coord"]

                board_char = self.board.grid[x, y]

                # Set border color for current tile player is on.
                if (x, y) == self.player.position:
                    block_color = self.BOARD_GRID_PLAYER_COLOR
                else:
                    block_color = self.BOARD_GRID_COLOR

                # Format character so fit within grid.
                if board_char == self.board.SPECIAL_TILE_CHAR:
                    char_pos = (x_px_pos + 6, y_px_pos + 5)
                else:
                    char_pos = (x_px_pos + 3, y_px_pos + 3)

                # Render character in grid.
                font_color = (
                    self.BOARD_WORD_COLOR
                    if (x, y) in self.all_word_pos
                    else self.BOARD_FONT_COLOR
                )
                screen.blit(char_font.render(board_char, True, font_color), char_pos)

                pygame.draw.rect(screen, block_color, rect, 2)

    def reset(self):
        pass

    def load(self):
        pass

    def save(self):
        pass
