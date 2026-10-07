"""Show Task 4 probabilities and create a heatmap from the Task 3 example.

From this directory, run ``python show_task_4.py``. The answer key below is
the same 5x5 board used by ``show_task_3.py``; only the first safe click is
revealed before calculating the frontier probabilities.
"""

import sys
from pathlib import Path

# The solver and Task 4 heatmap helper live in sibling folders of examples/.
mine_sweeper_folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(mine_sweeper_folder))
sys.path.insert(0, str(mine_sweeper_folder / "task4_heatmap"))

from minesweeper_solver import format_board, parse_board, reveal_cell
from heatmap_task_4 import create_heatmap, display_heatmap


# Keep this board identical to the answer key shown in show_task_3.py.
ANSWER_KEY = """2 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . ."""


key_grid = parse_board(ANSWER_KEY)
all_hidden_grid = []
for _ in key_grid:
    all_hidden_grid.append(["X"] * len(key_grid[0]))

all_hidden_state = format_board(all_hidden_grid)

# Reveal the same top-left cell as the solver's fixed opening move. Its clue
# creates three frontier cells whose probabilities can be compared by eye.
game_state, still_playing = reveal_cell(
    ANSWER_KEY,
    all_hidden_state,
    0,
    0,
)
if not still_playing:
    raise RuntimeError("The Task 3 example's opening click unexpectedly hit a mine.")

output_folder = Path(__file__).resolve().parents[1] / "task4_heatmap" / "output"
heatmap_path = output_folder / "task_4_heatmap_task3.svg"
probability_board = create_heatmap(game_state, heatmap_path)
opened_in_browser = display_heatmap(heatmap_path)

print("Task 4: mine probabilities on the Task 3 example board")
print("Visible game state after clicking (0, 0):")
print(game_state)
print("\nProbability board (only constrained hidden cells receive probabilities):")
print(probability_board)
if opened_in_browser:
    print("\nThe SVG heatmap is open in your default browser.")
else:
    print(f"\nCould not open a browser automatically. SVG saved at: {heatmap_path}")
