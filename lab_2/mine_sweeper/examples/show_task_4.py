"""Compute and display Task 4 probabilities for an editable game state.

Run from this folder with ``python show_task_4.py``. Replace GAME_STATE with
any partially revealed board to calculate its frontier mine probabilities.
"""

import sys
from pathlib import Path

# The solver and heatmap helper are in sibling folders of examples/.
mine_sweeper_folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(mine_sweeper_folder))
sys.path.insert(0, str(mine_sweeper_folder / "task4_heatmap"))

from heatmap_task_4 import create_heatmap, display_heatmap


# Supply the visible game state directly. This is a clockwise-rotated version
# of the small example, with one former zero at (2, 2) marked as a known mine.
# Nearby clues were updated so the state remains consistent. The probability
# calculation uses only this visible state, not an answer key.
GAME_STATE = """X X 2 X X
2 3 3 3 X
. 1 M 2 X
. 1 1 2 X
X X . X X"""


output_folder = mine_sweeper_folder / "task4_heatmap" / "output"
heatmap_path = output_folder / "task_4_heatmap.svg"
probability_board = create_heatmap(GAME_STATE, heatmap_path)
opened_in_browser = display_heatmap(heatmap_path)

print("Task 4: mine probabilities for the supplied game state")
print("Input game state:")
print(GAME_STATE)
print("\nProbability board (only constrained hidden cells receive probabilities):")
print(probability_board)
if opened_in_browser:
    print("\nThe SVG heatmap is open in your default browser.")
else:
    print(f"\nCould not open a browser automatically. SVG saved at: {heatmap_path}")
