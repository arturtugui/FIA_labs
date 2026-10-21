"""Checks for Task 1. Run with ``python test_task_1.py --show``."""

import argparse
import random
import sys
import unittest
from pathlib import Path

# Allow this file to run directly from tests/ as well as through discovery.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import (
    backtracking_solve,
    backtracking_step,
    generate_key,
    is_won,
    parse_board,
)


ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""

LAB_GAME_STATE = """2 X X X X
X 2 1 1 X
2 2 . . .
X 2 . . .
X 2 . . ."""

SHOW_EXAMPLES = False


def show_game_trace():
    """Display actual presses from the all-hidden start of the game."""
    key_grid = parse_board(ANSWER_KEY)
    starting_grid = [["X" for _ in row] for row in key_grid]
    trace_lines = [
        "Game trace: each move is an actual click, so the board can reveal clues.",
        "Starting board (all cells hidden):",
        "\n".join(" ".join(row) for row in starting_grid),
    ]

    steps = backtracking_solve(ANSWER_KEY)
    for move_number, (cell, state_after) in enumerate(steps, start=1):
        trace_lines.append(f"\nAfter press {move_number}, clicked cell {cell}:")
        trace_lines.append(state_after)

    if steps:
        final_state = steps[-1][1]
        if is_won(ANSWER_KEY, final_state):
            trace_lines.append("\nGame result: won")
        else:
            clicked_row, clicked_column = steps[-1][0]
            if parse_board(final_state)[clicked_row][clicked_column] == "M":
                trace_lines.append("\nGame result: lost (the press hit a mine)")

    # Print the trace in one flushed block so it appears before unittest's
    # progress dots instead of being buffered until the test run ends.
    print("\n".join(trace_lines), flush=True)


class BacktrackingTests(unittest.TestCase):
    def test_step_makes_a_first_guess_on_an_all_hidden_board(self):
        # With no revealed clues, search has no constraints to apply. The
        # documented first-move rule is therefore to choose the top-left cell.
        all_hidden = "X X X\nX X X\nX X X"
        first_cell, board_after_first_check = backtracking_step(all_hidden)
        second_cell, board_after_second_check = backtracking_step(
            board_after_first_check
        )

        self.assertEqual(first_cell, (0, 0))
        self.assertEqual(second_cell, (0, 1))
        # Since this function has no answer key, it can choose a cell but
        # cannot reveal its value; the visible board remains all X.
        self.assertEqual(board_after_first_check, all_hidden)
        self.assertEqual(board_after_second_check, all_hidden)

    def test_step_marks_a_mine_only_when_search_proves_it(self):
        state = LAB_GAME_STATE
        checked_cells = []
        for step_number in range(5):
            cell, after = backtracking_step(state)
            self.assertNotEqual(cell, (-1, -1))
            self.assertNotIn(cell, checked_cells)
            checked_cells.append(cell)

            before_grid = parse_board(state)
            after_grid = parse_board(after)
            for row in range(len(before_grid)):
                for column in range(len(before_grid[0])):
                    if before_grid[row][column] != after_grid[row][column]:
                        self.assertEqual(before_grid[row][column], "X")
                        self.assertEqual(after_grid[row][column], "M")
                        self.assertEqual(parse_board(ANSWER_KEY)[row][column], "M")

            state = after

    def test_step_advances_on_a_fresh_board_and_handles_no_hidden_cells(self):
        fresh_state = "X X X X"
        first_cell, first_board = backtracking_step(fresh_state)
        second_cell, second_board = backtracking_step(first_board)

        self.assertEqual(first_cell, (0, 0))
        self.assertEqual(second_cell, (0, 1))
        self.assertEqual(first_board, fresh_state)
        self.assertEqual(second_board, fresh_state)

        finished_cell, finished_board = backtracking_step(". .\n. .")
        self.assertEqual(finished_cell, (-1, -1))
        self.assertEqual(finished_board, ". .\n. .")

    def test_solver_trace_uses_real_clicks_and_ends_won_or_lost(self):
        steps = backtracking_solve(ANSWER_KEY)
        key_grid = parse_board(ANSWER_KEY)
        self.assertTrue(steps)

        previous_grid = [["X"] * len(key_grid[0]) for _ in range(len(key_grid))]
        lost = False

        for step_number, (cell, state_after) in enumerate(steps, start=1):
            row, column = cell
            self.assertEqual(previous_grid[row][column], "X")
            after_grid = parse_board(state_after)

            # Every newly visible answer must match the key. Search may also
            # mark a proven mine, but it must never mark a safe cell as M.
            for board_row in range(len(key_grid)):
                for board_column in range(len(key_grid[0])):
                    old_cell = previous_grid[board_row][board_column]
                    new_cell = after_grid[board_row][board_column]
                    if old_cell != new_cell:
                        self.assertEqual(old_cell, "X")
                        if new_cell == "M":
                            self.assertEqual(key_grid[board_row][board_column], "M")
                        else:
                            self.assertEqual(new_cell, key_grid[board_row][board_column])

            if key_grid[row][column] == "M":
                self.assertEqual(after_grid[row][column], "M")
                self.assertEqual(step_number, len(steps))
                lost = True
            previous_grid = after_grid

        if lost:
            self.assertFalse(is_won(ANSWER_KEY, steps[-1][1]))
        else:
            self.assertTrue(is_won(ANSWER_KEY, steps[-1][1]))

    def test_solver_terminates_on_reproducible_generated_boards(self):
        number_of_boards = 200

        for seed in range(number_of_boards):
            key = generate_key(9, 9, 10, seed=seed)
            steps = backtracking_solve(key)
            self.assertTrue(steps, msg=f"seed={seed}: solver returned no moves")

            final_board = steps[-1][1]
            final_cell = steps[-1][0]
            final_grid = parse_board(final_board)
            key_grid = parse_board(key)

            if key_grid[final_cell[0]][final_cell[1]] == "M":
                self.assertEqual(final_grid[final_cell[0]][final_cell[1]], "M")
            else:
                self.assertTrue(is_won(key, final_board), msg=f"seed={seed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Minesweeper Task 1 backtracking.")
    parser.add_argument("--show", action="store_true",
                        help="show actual click-by-click game progress")
    SHOW_EXAMPLES = parser.parse_args().show
    if SHOW_EXAMPLES:
        show_game_trace()
    unittest.main(argv=[sys.argv[0]])
