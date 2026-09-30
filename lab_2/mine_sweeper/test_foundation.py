"""Repeatable checks for the Minesweeper Phase 1 foundation.

Run concise pass/fail checks with::

    python test_foundation.py

Add ``--show`` to print examples and explanation of what each check verifies::

    python test_foundation.py --show

The generated clue test independently counts adjacent mines. Game-engine and
constraint tests use small examples whose behavior can be inspected by hand.
"""

import argparse
import sys
import unittest

from minesweeper_solver import (
    extract_constraints,
    Constraint,
    format_board,
    generate_key,
    is_won,
    neighbours,
    parse_board,
    reveal_cell,
)


SHOW_EXAMPLES = False


class FoundationTests(unittest.TestCase):
    def test_parse_and_format_round_trip(self):
        if SHOW_EXAMPLES:
            print("\n[1.1] Parse/format: cells are separated by whitespace; formatting uses one space.")
        examples = [
            "X X X\nX 1 M",
            "1 M 1\n2 2 .\n. . .",
            "X\nM\n.",
            "X X X\n1 2 3\n\n",  # optional trailing newline and blank line
        ]
        for board_text in examples:
            with self.subTest(board=board_text):
                parsed = parse_board(board_text)
                formatted = format_board(parsed)
                if SHOW_EXAMPLES:
                    print("Input:\n" + board_text.rstrip())
                    print("Parsed rows:", parsed)
                    print("Formatted again:\n" + formatted)
                self.assertEqual(formatted, board_text.strip())

    def test_parse_rejects_ragged_boards(self):
        if SHOW_EXAMPLES:
            print("\n[1.1] Invalid shape: a row with fewer cells should be rejected.")
        with self.assertRaises(ValueError):
            parse_board("X X\nX")

    def test_generator_is_repeatable_and_has_exact_mine_count(self):
        if SHOW_EXAMPLES:
            print("\n[1.4] Same seed should make the same 9x9 board with exactly 10 mines.")
        first = generate_key(9, 9, 10, seed=17)
        second = generate_key(9, 9, 10, seed=17)
        if SHOW_EXAMPLES:
            print("Generated board (seed 17):\n" + first)
            print("Mine count:", sum(row.count("M") for row in parse_board(first)))
        self.assertEqual(first, second)
        self.assertEqual(sum(row.count("M") for row in parse_board(first)), 10)

    def test_generated_clues_match_adjacent_mines_for_100_seeds(self):
        if SHOW_EXAMPLES:
            print("\n[1.4] Independently checking every safe clue on 100 generated boards.")
        for seed in range(100):
            board = parse_board(generate_key(9, 9, 10, seed))
            rows, columns = len(board), len(board[0])
            for row in range(rows):
                for column in range(columns):
                    if board[row][column] == "M":
                        continue
                    nearby = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            nr, nc = row + dr, column + dc
                            if ((dr or dc) and 0 <= nr < rows and 0 <= nc < columns
                                    and board[nr][nc] == "M"):
                                nearby += 1
                    expected = str(nearby) if nearby else "."
                    self.assertEqual(board[row][column], expected,
                                     msg=f"seed={seed}, cell={(row, column)}")
        if SHOW_EXAMPLES:
            print("Checked 100 seeds: each safe cell matches its adjacent mine count.")

    def test_generator_accepts_rectangular_boards_and_zero_mines(self):
        if SHOW_EXAMPLES:
            print("\n[1.4] A 1x5 board with zero mines should contain five zero clues.")
        board = parse_board(generate_key(1, 5, 0, seed=4))
        if SHOW_EXAMPLES:
            print("Generated board:\n" + format_board(board))
        self.assertEqual(board, [[".", ".", ".", ".", "."]])

    def test_generator_rejects_impossible_sizes(self):
        if SHOW_EXAMPLES:
            print("\n[1.4] Invalid dimensions or mine counts should raise ValueError.")
        for args in ((0, 4, 1, 1), (3, 0, 0, 1), (2, 2, 5, 1), (2, 2, -1, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                generate_key(*args)

    def test_numbered_click_reveals_only_the_clicked_cell(self):
        if SHOW_EXAMPLES:
            print("\n[1.5] Clicking a numbered cell reveals that cell and no others.")
        key = "1 M 1\n1 1 1\n. . ."
        state = "X X X\nX X X\nX X X"
        updated, still_playing = reveal_cell(key, state, 0, 0)
        if SHOW_EXAMPLES:
            print("State after click at (0, 0):\n" + updated)
        self.assertTrue(still_playing)
        self.assertEqual(updated, "1 X X\nX X X\nX X X")

    def test_zero_click_flood_fills_zero_region_and_numbered_border(self):
        if SHOW_EXAMPLES:
            print("\n[1.5] Clicking a zero reveals its connected zero area and numbered border.")
        key = generate_key(9, 9, 10, seed=3)
        key_grid = parse_board(key)
        zero = next((r, c) for r in range(9) for c in range(9)
                    if key_grid[r][c] == ".")
        state = "\n".join(" ".join("X" for _ in range(9)) for _ in range(9))
        updated, still_playing = reveal_cell(key, state, *zero)
        updated_grid = parse_board(updated)
        if SHOW_EXAMPLES:
            print(f"Clicked zero at {zero}; revealed board:\n{updated}")

        self.assertTrue(still_playing)
        # Every opened cell must match the key, and no mine can be opened by a zero.
        for r in range(9):
            for c in range(9):
                if updated_grid[r][c] != "X":
                    self.assertNotEqual(key_grid[r][c], "M")
                    self.assertEqual(updated_grid[r][c], key_grid[r][c])
        # Flood fill stops at numbered cells: only zeros expand the search.
        for r in range(9):
            for c in range(9):
                if updated_grid[r][c] == ".":
                    for nr, nc in neighbours(r, c, 9, 9):
                        self.assertNotEqual(updated_grid[nr][nc], "X")

    def test_mine_click_loses_and_win_detection_checks_all_safe_cells(self):
        if SHOW_EXAMPLES:
            print("\n[1.5] Mine click reports a loss; winning requires all safe cells revealed.")
        key = "M 1\n1 1"
        empty = "X X\nX X"
        lost_state, still_playing = reveal_cell(key, empty, 0, 0)
        if SHOW_EXAMPLES:
            print("After clicking the mine:\n" + lost_state)
        self.assertFalse(still_playing)
        self.assertEqual(lost_state, "M X\nX X")
        self.assertFalse(is_won(key, lost_state))

        state = empty
        for cell in ((0, 1), (1, 0), (1, 1)):
            state, still_playing = reveal_cell(key, state, *cell)
            self.assertTrue(still_playing)
        if SHOW_EXAMPLES:
            print("After revealing every safe cell:\n" + state)
        self.assertTrue(is_won(key, state))

    def test_extract_constraints_counts_hidden_cells_and_known_mines(self):
        if SHOW_EXAMPLES:
            print("\n[1.6] Extract a clue's hidden neighbours and subtract an already marked mine.")
        state = "M 1 X\nX X X"
        constraints = extract_constraints(state)
        if SHOW_EXAMPLES:
            print("State:\n" + state)
            print("(hidden neighbours, mines still needed):", constraints)
        self.assertEqual(len(constraints), 1)
        constraint = constraints[0]
        self.assertEqual(constraint.hidden_cells,
                         [(0, 2), (1, 0), (1, 1), (1, 2)])
        self.assertEqual(constraint.mines_needed, 0)
        self.assertIsInstance(constraint, Constraint)

    def test_extract_constraints_handles_zero_and_edge_clues(self):
        if SHOW_EXAMPLES:
            print("\n[1.6] A zero clue means no remaining mines; an edge clue has only in-bounds neighbours.")
        constraint = extract_constraints(". X\nX X")[0]
        self.assertEqual(constraint.hidden_cells, [(0, 1), (1, 0), (1, 1)])
        self.assertEqual(constraint.mines_needed, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Phase 1 Minesweeper foundation steps.")
    parser.add_argument("--show", action="store_true",
                        help="print example boards and test explanations")
    SHOW_EXAMPLES = parser.parse_args().show
    # unittest has its own command-line parser, so pass it only the script name.
    unittest.main(argv=[sys.argv[0]])
