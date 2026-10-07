"""Quick demo: replace GAME_STATE with any game-state board and run this file."""

from pathlib import Path
import sys

# The solver module is in the parent folder because this demo lives in examples/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import constraint_propagation


# Change this board to the position you want to demonstrate.
GAME_STATE = """2 X X X X
X 2 1 1 X
2 2 . . .
X 2 . . .
X 2 . . ."""

# Basic propagation marks only cells that are certainly mines.
result = constraint_propagation(GAME_STATE)

print("Input board:")
print(GAME_STATE)
print("\nAfter constraint propagation:")
print(result)
