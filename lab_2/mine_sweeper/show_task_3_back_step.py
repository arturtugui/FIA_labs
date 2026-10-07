"""Show one search check on an editable game state (not an actual click)."""

from minesweeper_solver import backtracking_step


# Replace this with another game state to demonstrate a different position.
# It uses the clues from the lab's example; X cells are the cells to reason about.
# The zero clues make this constraint-consistent position unlikely to arise
# from normal flood-fill play, but backtracking_step is specified for any state.
GAME_STATE = """2 X X X X
X 2 1 1 X
2 2 . . .
X 2 . . .
X 2 . . ."""

# This function has no answer key, so it cannot simulate a click or reveal a
# safe cell's value. It checks whether this cell can be a mine or safe, and
# writes M only when search proves it must be a mine.
cell, board_after_check = backtracking_step(GAME_STATE)

print("This is a backtracking hypothesis check, not a game press.")
print("Board before the check:")
print(GAME_STATE)
print(f"Cell checked: {cell}")
print("Board after the check (M appears only if search proves a mine):")
print(board_after_check)
print("\nFor actual press-by-press reveals, run show_task_3_back_solve.py.")
