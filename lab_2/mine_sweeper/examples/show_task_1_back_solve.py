"""Show the complete move trace from an all-hidden board."""

from pathlib import Path
import sys

# The solver module is in the parent folder because this demo lives in examples/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import backtracking_solve, is_won, parse_board


# This is the corrected 5x5 answer key from the lab example.
ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""

key_grid = parse_board(ANSWER_KEY)
steps = backtracking_solve(ANSWER_KEY)
print(f"Backtracking made {len(steps)} click(s).\n")
starting_grid = []
for _ in key_grid:
    starting_grid.append(["X"] * len(key_grid[0]))
print("Starting board (all cells hidden):")
print("\n".join(" ".join(row) for row in starting_grid))

for move_number, (cell, board_after) in enumerate(steps, start=1):
    print(f"\nAfter press {move_number}: clicked {cell}")
    print(board_after)
    print()

last_board = steps[-1][1] if steps else ""
if last_board and is_won(ANSWER_KEY, last_board):
    print("Result: game won")
elif last_board:
    last_cell = steps[-1][0]
    if parse_board(last_board)[last_cell[0]][last_cell[1]] == "M":
        print("Result: game lost (the clicked cell was a mine)")
    else:
        print("Result: stopped before a win or loss")
else:
    print("Result: no click was needed")
