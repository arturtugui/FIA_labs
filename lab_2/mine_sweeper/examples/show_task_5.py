"""Show Task 5 difficulty classifications for editable board positions.

Run from this folder with ``python show_task_5.py``. Edit the states below to
demonstrate positions from the lab or questions from the professor.
"""

from pathlib import Path
import sys

# The solver module is in the parent folder because this demo lives in examples/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import classify_difficulty


EXAMPLES = [
    (
        "Basic propagation",
        "M 1 X",
    ),
    (
        "Advanced propagation",
        "X X X\n1 2 1",
    ),
    (
        "Guess required",
        "X 1 X X X X",
    ),
    (
        "No clues: all cells are unconstrained",
        "X X\nX X",
    ),
]


for description, game_state in EXAMPLES:
    print(f"{description}:")
    print(game_state)
    print("Classification:", classify_difficulty(game_state))
    print()
