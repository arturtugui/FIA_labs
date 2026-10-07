"""Compare pure backtracking with Task 3's propagation-enhanced solver.

Change ANSWER_KEY below to compare both solvers on another complete board.
Run from this folder with ``python show_task_3.py``.
"""

from minesweeper_solver import (
    backtrack_constraint,
    backtracking_solve,
    is_won,
    parse_board,
)


# A small complete answer key that is easy to inspect. Replace this variable
# with another answer key to demonstrate a different game.
ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""


key_grid = parse_board(ANSWER_KEY)
pure_steps = backtracking_solve(ANSWER_KEY)
combined_steps = backtrack_constraint(ANSWER_KEY)

# The solver starts with every cell hidden, regardless of the supplied key.
starting_board = []
for _ in key_grid:
    starting_board.append(["X"] * len(key_grid[0]))

print("Task 3 comparison: pure backtracking vs. backtracking + propagation")
print("Both solvers use this same 5x5 answer key, the one from show_task_1_back_solve.py.")
print(f"Pure backtracking: {len(pure_steps)} click(s)")
print(f"Backtracking + propagation: {len(combined_steps)} click(s)")
print(f"Click-count difference: {len(pure_steps) - len(combined_steps):+d} (positive means propagation used fewer)")
print("\nCombined solver's starting board:")
print("\n".join(" ".join(row) for row in starting_board))

# Each record is one real click plus the visible board after the game engine
# reveals its result. The solver may also mark mines proved by its reasoning.
for move_number, (cell, board_after) in enumerate(combined_steps, start=1):
    print(f"\nMove {move_number}: clicked {cell}")
    print("Board after the click:")
    print(board_after)

if not combined_steps:
    print("\nNo click was needed.")
elif is_won(ANSWER_KEY, combined_steps[-1][1]):
    print(f"\nBacktracking + propagation solver result: won in {len(combined_steps)} click(s).")
else:
    final_cell = combined_steps[-1][0]
    final_value = parse_board(ANSWER_KEY)[final_cell[0]][final_cell[1]]
    if final_value == "M":
        print(f"\nBacktracking + propagation solver result: lost after {len(combined_steps)} click(s); the final click hit a mine.")
    else:
        print("\nBacktracking + propagation solver result: stopped before a win or a mine hit.")

if pure_steps and is_won(ANSWER_KEY, pure_steps[-1][1]):
    pure_result = "won"
elif pure_steps:
    pure_cell = pure_steps[-1][0]
    pure_result = "lost" if parse_board(ANSWER_KEY)[pure_cell[0]][pure_cell[1]] == "M" else "stopped"
else:
    pure_result = "no click needed"
print(f"Pure backtracking result: {pure_result}.")
