"""Hand-editable checks for Task 2: basic constraint propagation.

Run the concise test report with::

    python test_task_2.py

Print each example board and the deduction made with::

    python test_task_2.py --show

Add or edit entries in HAND_CASES to demonstrate other positions in class.
The random-state check verifies that deductions are sound on generated games.
"""

import argparse
import random
import sys
import unittest

from minesweeper_solver import (
    constraint_propagation,
    format_board,
    generate_key,
    parse_board,
    reveal_cell,
)


# Each item is (description, game state, expected output). These are short
# positions that can be changed easily to demonstrate another example.
HAND_CASES = [
    (
        "one hidden neighbour must be a mine",
        "1 1\nX 1",
        "1 1\nM 1",
    ),
    (
        "one mine among two hidden cells is still ambiguous",
        "X 1 X",
        "X 1 X",
    ),
    (
        "a board with no hidden cells stays unchanged",
        "M 1\n1 1",
        "M 1\n1 1",
    ),
    (
        "existing mine marks are kept",
        "M 1 X",
        "M 1 X",
    ),
    (
        "safe deductions can help force a mine in a later clue",
        "X X X\n1 1 .",
        "M X X\n1 1 .",
    ),
]

SHOW_EXAMPLES = False


class ConstraintPropagationTests(unittest.TestCase):
    def test_hand_written_examples(self):
        # These fixed examples show both rules, an undecided position, and a
        # small chain where learning a safe cell helps another clue.
        for description, state, expected in HAND_CASES:
            with self.subTest(example=description):
                actual = constraint_propagation(state)

                if SHOW_EXAMPLES:
                    print(f"\nExample: {description}")
                    print("Input state:\n" + state)
                    print("Deduced board:\n" + actual)
                    print("Expected board:\n" + expected)

                self.assertEqual(actual, expected)

    def test_only_newly_deduced_mines_change_the_board(self):
        state = "1 X X\nM 2 X"
        result = constraint_propagation(state)
        original_grid = parse_board(state)
        result_grid = parse_board(result)

        # The function's output contract allows only hidden-to-mine changes;
        # safe deductions are useful internally but must remain X visibly.
        for row in range(len(original_grid)):
            for column in range(len(original_grid[0])):
                original_cell = original_grid[row][column]
                result_cell = result_grid[row][column]
                if original_cell != result_cell:
                    self.assertEqual(original_cell, "X")
                    self.assertEqual(result_cell, "M")

    def test_repeated_propagation_is_idempotent(self):
        for _, state, _ in HAND_CASES:
            once = constraint_propagation(state)
            twice = constraint_propagation(once)
            self.assertEqual(twice, once)

    def test_deductions_are_sound_on_generated_game_states(self):
        number_of_states = 600
        if SHOW_EXAMPLES:
            print(f"\nChecking mine deductions against {number_of_states} generated game states.")

        for seed in range(number_of_states):
            # Generate the same board every time the test is run for this seed.
            key = generate_key(9, 9, 10, seed=seed)
            key_grid = parse_board(key)
            # The game starts with every cell hidden. We reveal only safe cells
            # below, using the same reveal function a real game would use.
            state_grid = [["X" for _ in range(9)] for _ in range(9)]

            # Reveal a reproducible set of safe cells through the game engine,
            # so the test positions obey the actual Minesweeper reveal rules.
            safe_cells = [
                (row, column)
                for row in range(9)
                for column in range(9)
                if key_grid[row][column] != "M"
            ]
            # A fixed seed makes the selected clicks repeatable for debugging.
            random.Random(seed).shuffle(safe_cells)
            state = format_board(state_grid)
            for row, column in safe_cells[:1 + seed % 12]:
                if parse_board(state)[row][column] == "X":
                    state, still_playing = reveal_cell(key, state, row, column)
                    self.assertTrue(still_playing)

            # Ask the solver for mine marks, then compare those marks with the
            # answer key, which acts as the test's ground-truth oracle.
            deduced_state = constraint_propagation(state)
            before = parse_board(state)
            after = parse_board(deduced_state)

            for row in range(9):
                for column in range(9):
                    if before[row][column] != after[row][column]:
                        # The contract permits only X -> M changes, and every
                        # newly marked mine must match the generated answer key.
                        self.assertEqual(before[row][column], "X")
                        self.assertEqual(after[row][column], "M")
                        self.assertEqual(key_grid[row][column], "M",
                                         msg=f"seed={seed}, cell={(row, column)}")

            # Newly found mines become input facts; another pass must not add
            # deductions that were missed the first time.
            self.assertEqual(constraint_propagation(deduced_state), deduced_state)

        if SHOW_EXAMPLES:
            print("All deductions matched the answer keys; repeated runs were unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Minesweeper Task 2 propagation.")
    parser.add_argument("--show", action="store_true",
                        help="print hand examples and randomized-check progress")
    SHOW_EXAMPLES = parser.parse_args().show
    # unittest has its own argument parser; only pass it the script name.
    unittest.main(argv=[sys.argv[0]])
