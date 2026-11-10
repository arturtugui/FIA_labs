"""Hand-editable checks for Task 5 difficulty classification."""

import argparse
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Allow this file to run directly from tests/ as well as through discovery.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import classify_difficulty


# Change these positions to demonstrate how the classifier moves up the
# technique ladder as simpler kinds of reasoning get stuck.
EXAMPLES = [
    (
        "basic propagation",
        "M 1 X",
        "Basic propagation can prove at least one hidden cell.",
    ),
    (
        "advanced subset propagation",
        "X X X\n1 2 1",
        "Advanced propagation can prove at least one hidden cell.",
    ),
    (
        "guess because the frontier is ambiguous",
        "X 1 X X X X",
        "Guess required: no certain move; uncertain frontier cells: "
        "(0, 0), (0, 2); unconstrained hidden cells: "
        "(0, 3), (0, 4), (0, 5).",
    ),
    (
        "guess because there are no clues",
        "X X\nX X",
        "Guess required: no clue touches a hidden cell; "
        "all 4 hidden cells are unconstrained.",
    ),
    (
        "already solved",
        "1 M\n1 1",
        "Solved: no hidden cells remain.",
    ),
    (
        "Task 4 heatmap example",
        "X X 2 X X\n2 3 3 3 X\n. 1 M 2 X\n. 1 1 2 X\nX X . X X",
        "Basic propagation can prove at least one hidden cell.",
    ),
]

SHOW_EXAMPLES = False


class DifficultyClassificationTests(unittest.TestCase):
    def test_examples(self):
        for description, state, expected in EXAMPLES:
            with self.subTest(example=description):
                result = classify_difficulty(state)
                if SHOW_EXAMPLES:
                    print(f"\nExample: {description}")
                    print("Game state:")
                    print(state)
                    print("Classification:")
                    print(result)
                self.assertEqual(result, expected)

    def test_backtracking_is_reported_after_both_propagators_get_stuck(self):
        # This state has two equally possible mine locations, so neither
        # propagation method can prove a value. Mock the final search result
        # to check the classifier's ordering without relying on a puzzle whose
        # deduction pattern may be difficult to inspect by eye.
        with patch("minesweeper_solver._analyse_frontier") as analyse:
            analyse.return_value = ({(0, 0): 0, (0, 2): 1}, [], [(0, 0)])
            result = classify_difficulty("X 1 X")

        self.assertEqual(result, "Backtracking can prove at least one hidden cell.")
        analyse.assert_called_once()

    def test_contradictory_clues_are_reported_as_invalid(self):
        self.assertEqual(
            classify_difficulty("2 X"),
            "Invalid state: the visible clues contradict one another.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--show",
        action="store_true",
        help="print the example boards and their difficulty classifications",
    )
    arguments, unittest_arguments = parser.parse_known_args()
    SHOW_EXAMPLES = arguments.show
    unittest.main(argv=[sys.argv[0], *unittest_arguments])
