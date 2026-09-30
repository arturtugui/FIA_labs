"""Small, repeatable checks for roadmap steps 1.1 and 1.4.

Run the concise pass/fail checks with::

    python test_foundation.py

Add ``--show`` to print examples and explanation of what each check verifies::

    python test_foundation.py --show

The generated clue test independently counts adjacent mines rather than
calling a future answer-key validator implementation.
"""

import argparse
import sys
import unittest

from minesweeper_solver import format_board, generate_key, parse_board


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check roadmap steps 1.1 and 1.4.")
    parser.add_argument("--show", action="store_true",
                        help="print example boards and test explanations")
    SHOW_EXAMPLES = parser.parse_args().show
    # unittest has its own command-line parser, so pass it only the script name.
    unittest.main(argv=[sys.argv[0]])
