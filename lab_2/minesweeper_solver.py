"""
Fundamentals of AI -- Laboratory Work: Minesweeper as a CSP

Submission rules:
- Submit THIS file, renamed to ``<surname>_<name>.py``.
- Only the Python standard library may be imported. Plotting libraries may be
  used for Task 4, but their import lines must be commented out in the
  submitted file.
- Do NOT rename or change the signature of any function marked ``# REQUIRED``.
  The evaluator's tests call them by name. You may add helper functions,
  classes and constants freely.

Board notation (cells separated by a space, rows by a newline):

    M      mine
    1-8    number of adjacent mines
    .      revealed cell with zero adjacent mines
    X      hidden cell

Two kinds of board strings are used:
- answer key  -- the complete board, no X (ground truth)
- game state  -- what the player sees, may contain X

Cells are ``(row, col)`` tuples, 0-indexed, top-left is (0, 0).
"""

# Task 1 -- Backtracking
def backtracking_step(state: str) -> tuple[tuple[int, int], str]:  # REQUIRED
    """One step of backtracking on a game state.
    Returns the cell it checked and the board after checking it."""
    raise NotImplementedError

def backtracking_solve(answer_key: str) -> list[tuple[tuple[int, int], str]]:  # REQUIRED
    """Play from an all-X board with pure backtracking until the board is solved
    or a mine is hit. Returns the list of (cell, board_after) for every step."""
    raise NotImplementedError


# Task 2 -- Constraint propagation
def constraint_propagation(state: str) -> str:  # REQUIRED
    """Return the same game state with every cell deduced to be a mine
    marked M. Nothing else is changed."""
    raise NotImplementedError


# Task 3 -- Backtracking + constraint propagation
def backtrack_constraint(answer_key: str) -> list[tuple[tuple[int, int], str]]:  # REQUIRED
    """Same as backtracking_solve, but constraints are propagated after every
    assignment."""
    raise NotImplementedError


# Task 4 -- Mine probabilities
def mine_probability(state: str) -> str:  # REQUIRED
    """Return the same game state where every hidden cell on the constraint
    frontier is replaced by its probability of being a mine."""
    raise NotImplementedError


# Task 5 -- Difficulty classification
def classify_difficulty(state: str) -> str:  # REQUIRED
    """Return the name of the simplest technique that resolves the state with
    100% confidence, or the cells that make a certain decision impossible."""
    raise NotImplementedError


# Task 6 -- Advanced solver
def advanced_solver(answer_key: str) -> list[tuple[tuple[int, int], str]]:  # REQUIRED
    """Same as backtrack_constraint, but using the advanced propagation
    technique(s) described in your report."""
    raise NotImplementedError