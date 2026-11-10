"""Tests for Phase 4 / lab Task 3: backtracking with propagation.

Run from this folder with ``python test_task_3.py``.
"""

import argparse
import itertools
import sys
import unittest
from pathlib import Path

# Allow this file to run directly from tests/ as well as through discovery.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import (
    Constraint,
    _assignment_is_consistent,
    _find_frontier_solution,
    _find_frontier_solution_with_propagation,
    _frontier_cells,
    _propagate_assignments,
    backtrack_constraint,
    backtracking_solve,
    generate_key,
    is_won,
    parse_board,
)


def chain_constraints():
    """Make a small CSP where one guess triggers a chain of basic deductions.

    The constraints mean:
      A: a + b = 1
      B: b + c + d = 1
      C: c + d = 1

    If search first tries ``b = safe``, A forces ``a = mine``. Then choosing
    ``c = safe`` makes both B and C force ``d = mine``. This lets us see the
    difference between branching on each value and propagating consequences.
    """
    a = (0, 0)
    b = (0, 1)
    c = (0, 2)
    d = (0, 3)
    return [
        Constraint(hidden_cells=[a, b], mines_needed=1),
        Constraint(hidden_cells=[b, c, d], mines_needed=1),
        Constraint(hidden_cells=[c, d], mines_needed=1),
    ]


class PropagationSearchTests(unittest.TestCase):
    def test_propagation_follows_forced_values_until_a_fixpoint(self):
        constraints = chain_constraints()
        b = (0, 1)
        c = (0, 2)
        a = (0, 0)
        d = (0, 3)

        # Assuming b is safe makes A require a mine in a. After also assuming
        # c safe, constraints B and C both require d to be a mine.
        after_first_guess = _propagate_assignments(constraints, {b: 0})
        self.assertEqual(after_first_guess, {b: 0, a: 1})

        after_second_guess = _propagate_assignments(
            constraints,
            {b: 0, c: 0},
        )
        self.assertEqual(after_second_guess, {b: 0, a: 1, c: 0, d: 1})

    def test_propagation_rejects_a_contradictory_branch(self):
        constraints = chain_constraints()
        # A needs one mine, but this branch assigns both neighbours safe.
        impossible = _propagate_assignments(
            constraints,
            {(0, 0): 0, (0, 1): 0},
        )
        self.assertIsNone(impossible)

    def test_propagation_search_has_the_same_solutions_as_pure_search(self):
        constraints = chain_constraints()
        cells = _frontier_cells(constraints)
        pure_solutions = set()
        propagated_solutions = set()

        # Enumerate every complete assignment for this tiny four-cell example.
        # The pure consistency check defines the expected solution set, while
        # the propagation search must accept exactly those same assignments.
        for values in itertools.product((0, 1), repeat=len(cells)):
            complete_assignment = dict(zip(cells, values))
            if _assignment_is_consistent(constraints, complete_assignment):
                pure_solutions.add(values)

            propagated_result = _find_frontier_solution_with_propagation(
                constraints,
                fixed_choices=complete_assignment,
            )
            if propagated_result is not None:
                propagated_solutions.add(values)

        self.assertEqual(pure_solutions, propagated_solutions)
        self.assertEqual(len(pure_solutions), 2)

    def test_propagation_reduces_branching_on_the_chain_example(self):
        constraints = chain_constraints()
        pure_node_count = {"nodes": 0}
        propagated_node_count = {"nodes": 0}

        pure_solution = _find_frontier_solution(
            constraints,
            search_stats=pure_node_count,
        )
        propagated_solution = _find_frontier_solution_with_propagation(
            constraints,
            search_stats=propagated_node_count,
        )

        self.assertIsNotNone(pure_solution)
        self.assertIsNotNone(propagated_solution)
        self.assertTrue(_assignment_is_consistent(constraints, pure_solution))
        self.assertTrue(
            _assignment_is_consistent(constraints, propagated_solution)
        )
        self.assertLess(
            propagated_node_count["nodes"],
            pure_node_count["nodes"],
        )

    def test_combined_solver_produces_valid_traces_on_generated_games(self):
        # Use identical fixed-seed keys so both algorithms face the same games.
        for seed in range(100):
            answer_key = generate_key(9, 9, 10, seed=seed)
            pure_steps = backtracking_solve(answer_key)
            propagated_steps = backtrack_constraint(answer_key)

            self.assertTrue(pure_steps, msg=f"pure solver seed={seed}")
            self.assertTrue(propagated_steps, msg=f"combined solver seed={seed}")

            # The two algorithms use the same move policy, so compare results
            # on each generated board while validating the combined trace.
            pure_won = is_won(answer_key, pure_steps[-1][1])
            combined_won = is_won(answer_key, propagated_steps[-1][1])
            self.assertGreaterEqual(
                int(combined_won),
                int(pure_won),
                msg=f"combined solver lost a game pure solver won (seed={seed})",
            )

            key_grid = parse_board(answer_key)
            previous_grid = [["X"] * len(key_grid[0]) for _ in key_grid]
            for step_number, (clicked_cell, board_after) in enumerate(
                propagated_steps,
                start=1,
            ):
                clicked_row, clicked_column = clicked_cell
                self.assertEqual(
                    previous_grid[clicked_row][clicked_column],
                    "X",
                    msg=f"seed={seed}, step={step_number}: clicked a visible cell",
                )

                after_grid = parse_board(board_after)
                for row in range(len(key_grid)):
                    for column in range(len(key_grid[0])):
                        old_value = previous_grid[row][column]
                        new_value = after_grid[row][column]
                        if old_value == new_value:
                            continue

                        self.assertEqual(old_value, "X")
                        if new_value == "M":
                            self.assertEqual(key_grid[row][column], "M")
                        else:
                            self.assertEqual(new_value, key_grid[row][column])

                # A mine can only end the trace; safe clicks must eventually
                # finish in a win if they are the final recorded move.
                if key_grid[clicked_row][clicked_column] == "M":
                    self.assertEqual(step_number, len(propagated_steps))
                    self.assertEqual(after_grid[clicked_row][clicked_column], "M")

                previous_grid = after_grid

            final_cell = propagated_steps[-1][0]
            final_key_value = key_grid[final_cell[0]][final_cell[1]]
            if final_key_value != "M":
                self.assertTrue(is_won(answer_key, propagated_steps[-1][1]))


def show_propagation_example():
    """Print one short branch and the search-node comparison it creates."""
    constraints = chain_constraints()
    pure_node_count = {"nodes": 0}
    propagated_node_count = {"nodes": 0}

    _find_frontier_solution(constraints, search_stats=pure_node_count)
    _find_frontier_solution_with_propagation(
        constraints,
        search_stats=propagated_node_count,
    )

    after_guess = _propagate_assignments(constraints, {(0, 1): 0})
    after_next_guess = _propagate_assignments(
        constraints,
        {(0, 1): 0, (0, 2): 0},
    )

    print("\nExample: how one trial can force other cells")
    print("  Start with the trial b = safe.")
    print(f"  Propagation then gives: {after_guess}")
    print("  Also try c = safe.")
    print(f"  Propagation now gives: {after_next_guess}")
    print("  Search nodes count trial mine/safe choices, not forced values.")
    print(f"  Pure backtracking tried {pure_node_count['nodes']} value(s).")
    print(
        "  Backtracking with propagation tried "
        f"{propagated_node_count['nodes']} value(s)."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check Task 3: backtracking with constraint propagation (roadmap Phase 4)."
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="print a small explanation of propagation and search-node counts",
    )
    arguments = parser.parse_args()

    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PropagationSearchTests
    )
    test_result = unittest.TextTestRunner(verbosity=0).run(test_suite)

    if test_result.wasSuccessful():
        print("\nPhase 4 checks passed:")
        print("  - Propagation reaches forced values and rejects contradictions.")
        print("  - Propagation search preserves the pure solver's solutions.")
        print("  - Propagation reduces branching on the demonstration constraints.")
        print("  - Both solvers were compared on 100 fixed-seed 9x9 games.")
        if arguments.show:
            show_propagation_example()

    raise SystemExit(not test_result.wasSuccessful())
