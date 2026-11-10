"""Tests for lab Task 4: exact mine probabilities on the constraint frontier."""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# Keep imports working when the full test suite is started from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import (
    _choose_least_risky_frontier_cell,
    mine_probability,
    parse_board,
    reveal_cell,
)


TASK_3_ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""


class MineProbabilityTests(unittest.TestCase):
    def test_symmetric_single_clue_gives_equal_probabilities(self):
        # Exactly one of the two hidden neighbours must be a mine.
        self.assertEqual(mine_probability("X 1 X"), "0.50 1 0.50")

    def test_probability_is_fraction_of_all_consistent_worlds(self):
        # The corner clue needs two mines among three symmetric neighbours.
        result = parse_board(mine_probability("2 X X\nX X X"))
        self.assertEqual(result[0][1], "0.67")
        self.assertEqual(result[1][0], "0.67")
        self.assertEqual(result[1][1], "0.67")
        # The cells outside the corner clue's frontier stay hidden.
        self.assertEqual(result[0][2], "X")
        self.assertEqual(result[1][2], "X")

    def test_known_mines_are_subtracted_from_the_clue(self):
        # The marked mine satisfies the 1; the only other neighbour is safe.
        self.assertEqual(mine_probability("M 1 X"), "M 1 0.00")

    def test_separate_frontier_regions_are_counted_independently(self):
        result = mine_probability("X 1 X X X X 1 X")
        self.assertEqual(result, "0.50 1 0.50 X X 0.50 1 0.50")

    def test_no_frontier_leaves_all_hidden_cells_unclassified(self):
        self.assertEqual(mine_probability("X X\nX X"), "X X\nX X")

    def test_task_three_answer_key_can_be_used_for_task_four_demo(self):
        # Use the same answer key as show_task_3.py, but reveal only its first
        # clicked cell so the heatmap has a clue and a non-trivial frontier.
        all_hidden = "X X X X X\nX X X X X\nX X X X X\nX X X X X\nX X X X X"
        partial_state, still_playing = reveal_cell(
            TASK_3_ANSWER_KEY,
            all_hidden,
            0,
            0,
        )
        self.assertTrue(still_playing)

        probability_grid = parse_board(mine_probability(partial_state))
        self.assertEqual(probability_grid[0][0], "2")
        self.assertEqual(probability_grid[0][1], "0.67")
        self.assertEqual(probability_grid[1][0], "0.67")
        self.assertEqual(probability_grid[1][1], "0.67")

    def test_contradictory_clue_is_rejected(self):
        with self.assertRaises(ValueError):
            mine_probability("2 X")

    def test_solver_guess_prefers_the_lower_probability_frontier_cell(self):
        visible_grid = parse_board("X 1 X")
        frontier_cells = [(0, 0), (0, 2)]
        probabilities = parse_board("0.25 1 0.75")

        # Isolate the click-choice rule from probability enumeration itself:
        # the left candidate is visibly less risky than the right one.
        with patch(
            "minesweeper_solver._probability_grid",
            return_value=probabilities,
        ):
            chosen_cell = _choose_least_risky_frontier_cell(
                visible_grid,
                frontier_cells,
            )

        self.assertEqual(chosen_cell, (0, 0))


if __name__ == "__main__":
    unittest.main()
