"""Show the Task 6 advanced solver on the Task 1 example board.

Run from this folder with ``python examples/show_task_6.py``. Replace
ANSWER_KEY with another complete board to demonstrate advanced propagation on
a different game.
"""

from pathlib import Path
import sys

# The solver module is in the parent folder because this demo lives in examples/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import advanced_solver, is_won, parse_board


# This is the same complete answer key used by show_task_1_back_solve.py.
ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""


key_grid = parse_board(ANSWER_KEY)
steps = advanced_solver(ANSWER_KEY)

starting_board = []
for _ in key_grid:
    starting_board.append(["X"] * len(key_grid[0]))

print("Task 6: advanced propagation on the Task 1 example board")
print(f"The advanced solver made {len(steps)} click(s).")
print("\nStarting board (all cells hidden):")
print("\n".join(" ".join(row) for row in starting_board))

for move_number, (cell, board_after) in enumerate(steps, start=1):
    print(f"\nAfter press {move_number}: clicked {cell}")
    print(board_after)

if not steps:
    print("\nResult: no click was needed")
elif is_won(ANSWER_KEY, steps[-1][1]):
    print(f"\nResult: game won in {len(steps)} click(s)")
else:
    last_cell = steps[-1][0]
    if parse_board(steps[-1][1])[last_cell[0]][last_cell[1]] == "M":
        print("\nResult: game lost (the clicked cell was a mine)")
    else:
        print("\nResult: stopped before a win or loss")
