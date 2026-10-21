"""Checks for Task 6: advanced constraint propagation and advanced_solver."""

import random
import sys
import unittest
from pathlib import Path

# Allow this file to run directly from tests/ as well as through discovery.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import (
    advanced_constraint_propagation,
    advanced_solver,
    backtrack_constraint,
    constraint_propagation,
    format_board,
    generate_key,
    is_won,
    parse_board,
    reveal_cell,
)


class AdvancedPropagationTests(unittest.TestCase):
    def test_one_two_one_wall_finds_corner_mines(self) -> None:
        state = "X X X\n1 2 1"
        basic = constraint_propagation(state)
        advanced = advanced_constraint_propagation(state)

        self.assertEqual(basic, state)
        self.assertEqual(advanced, "M X M\n1 2 1")

    def test_identical_hidden_sets_do_not_crash(self) -> None:
        state = "X X\n1 1"
        self.assertEqual(constraint_propagation(state), state)
        self.assertEqual(advanced_constraint_propagation(state), state)

    def test_advanced_finds_at_least_as_many_mines_as_basic(self) -> None:
        randomizer = random.Random(2026)
        for seed in range(200):
            answer_key = generate_key(9, 9, 10, seed)
            grid = parse_board(answer_key)
            state_grid = [["X" if cell != "M" else "X" for cell in row] for row in grid]

            for _ in range(3):
                hidden_cells = [
                    (row, column)
                    for row in range(9)
                    for column in range(9)
                    if state_grid[row][column] == "X"
                ]
                if not hidden_cells:
                    break

                row, column = randomizer.choice(hidden_cells)
                if grid[row][column] == "M":
                    continue

                state, still_playing = reveal_cell(
                    answer_key,
                    format_board(state_grid),
                    row,
                    column,
                )
                if not still_playing:
                    break
                state_grid = parse_board(state)

                basic_grid = parse_board(constraint_propagation(state))
                advanced_grid = parse_board(advanced_constraint_propagation(state))

                for row_index in range(9):
                    for column_index in range(9):
                        if basic_grid[row_index][column_index] == "M":
                            self.assertEqual(
                                advanced_grid[row_index][column_index],
                                "M",
                                msg=f"seed={seed}, state=\n{state}",
                            )
                        if advanced_grid[row_index][column_index] == "M":
                            self.assertEqual(
                                grid[row_index][column_index],
                                "M",
                                msg=f"seed={seed}, state=\n{state}",
                            )


class AdvancedSolverTests(unittest.TestCase):
    def test_advanced_solver_produces_valid_traces(self) -> None:
        for seed in range(20):
            answer_key = generate_key(9, 9, 10, seed)
            steps = advanced_solver(answer_key)
            self.assertTrue(steps)

            previous_state = None
            for click, state in steps:
                self.assertEqual(parse_board(state)[click[0]][click[1]] != "X", True)
                if previous_state is not None:
                    self.assertNotEqual(state, previous_state)
                previous_state = state

            final_state = steps[-1][1]
            self.assertTrue(is_won(answer_key, final_state) or "M" in final_state)

    def test_advanced_solver_is_at_least_as_strong_as_backtrack_constraint(self) -> None:
        wins_basic = 0
        wins_advanced = 0
        for seed in range(50):
            answer_key = generate_key(9, 9, 10, seed + 400)
            basic_steps = backtrack_constraint(answer_key)
            advanced_steps = advanced_solver(answer_key)

            if is_won(answer_key, basic_steps[-1][1]):
                wins_basic += 1
            if is_won(answer_key, advanced_steps[-1][1]):
                wins_advanced += 1

            self.assertLessEqual(len(advanced_steps), len(basic_steps))
        self.assertGreaterEqual(wins_advanced, wins_basic)


if __name__ == "__main__":
    unittest.main()
