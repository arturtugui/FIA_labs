"""Demonstrate Task 4 using the user's partially revealed SMALL board.

Run from this folder with ``python show_task_4_small.py``. The output SVG is
written to ``output/task_4_heatmap_small.svg``.
"""

from pathlib import Path
import sys

# The visualization script is under task4_heatmap/, while the solver is in
# this file's parent directory.
mine_sweeper_folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(mine_sweeper_folder))
sys.path.insert(0, str(mine_sweeper_folder / "task4_heatmap"))

from heatmap_task_4 import create_heatmap, display_heatmap


# Edit this state to show probabilities for another position.
SMALL = """X X 2 X X
2 3 3 3 X
. 1 M 2 X
. 1 1 2 X
X X . X X"""


output_path = (
    Path(__file__).resolve().parents[1]
    / "task4_heatmap"
    / "output"
    / "task_4_heatmap_small.svg"
)
probability_board = create_heatmap(SMALL, output_path)
opened_in_browser = display_heatmap(output_path)

print("Input game state:")
print(SMALL)
print("\nProbability board:")
print(probability_board)
if opened_in_browser:
    print("\nThe SVG heatmap is open in your default browser.")
else:
    print(f"\nCould not open a browser automatically. SVG saved at: {output_path}")
