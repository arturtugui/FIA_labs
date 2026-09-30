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

import random
from typing import NamedTuple


# FOUNDATION FUNCTIONS

class Constraint(NamedTuple):
    """One clue's remaining rule for the hidden cells around it.

    ``hidden_cells`` lists the unknown coordinates. ``mines_needed`` says how
    many of those cells must be mines; the others must therefore be safe.
    """

    hidden_cells: list[tuple[int, int]]
    mines_needed: int

def parse_board(text: str) -> list[list[str]]:
    """Convert a space-separated board string into a list of rows.

    Blank lines around or inside the board are ignored. Rows must have the
    same number of cells, and cells must use the lab's notation.
    """
    # The notation separates cells with spaces. split() also tolerates extra
    # whitespace, which makes copied board strings less fragile.
    rows = [line.split() for line in text.splitlines() if line.split()]
    if not rows:
        raise ValueError("A board must contain at least one row.")

    # Later coordinate operations assume a rectangular board, so reject a
    # ragged input at the boundary instead of letting it fail unpredictably.
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Every board row must have the same number of cells.")

    allowed_cells = {"X", "M", ".", "1", "2", "3", "4", "5", "6", "7", "8"}
    if any(cell not in allowed_cells for row in rows for cell in row):
        raise ValueError("Board contains a cell symbol outside the lab notation.")
    return rows


def format_board(grid: list[list[str]]) -> str:
    """Convert rows of cells back to the lab's space-separated notation.

    The formatted string has no trailing newline, so parse/format round trips
    are consistent for inputs with or without a final newline.
    """
    # Validate before joining: malformed rows would create misleading output.
    if not grid or not grid[0]:
        raise ValueError("A board must contain at least one cell.")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("Every board row must have the same number of cells.")
    return "\n".join(" ".join(row) for row in grid)


def generate_key(rows: int, columns: int, mine_count: int, seed: int) -> str:
    """Generate a reproducible answer key with exactly ``mine_count`` mines.

    A local random-number generator keeps this function deterministic without
    changing random choices elsewhere in the program. Safe cells show the
    number of adjacent mines, or ``.`` when that number is zero.
    """
    # Validate before sampling: dimensions must describe cells, and the mine
    # count must fit in the population from which we choose.
    if rows < 1 or columns < 1:
        raise ValueError("Board dimensions must both be positive.")
    if not 0 <= mine_count <= rows * columns:
        raise ValueError("Mine count must fit within the board.")

    # Sample unique coordinates so the generated board has exactly the
    # requested number of mines, with no duplicates.
    all_cells = [(row, column)
                 for row in range(rows)
                 for column in range(columns)]
    # A local generator makes the seed reproducible without changing random
    # choices made elsewhere in the program.
    randomizer = random.Random(seed)

    # Store locations in a set so checking each surrounding coordinate for a
    # mine is quick while clue numbers are calculated.
    mines = set(randomizer.sample(all_cells, mine_count))

    answer = []
    for row in range(rows):
        answer_row = []
        for column in range(columns):
            if (row, column) in mines:
                answer_row.append("M")
                continue

            adjacent_mines = 0
            # A clue counts the eight surrounding positions. Skipping the
            # center and off-board positions handles edges and corners too.
            for row_change in (-1, 0, 1):
                for column_change in (-1, 0, 1):
                    if row_change == 0 and column_change == 0:
                        continue
                    neighbour = (row + row_change, column + column_change)
                    if neighbour in mines:
                        adjacent_mines += 1

            # The lab represents a safe cell with no adjacent mines as a dot.
            answer_row.append(str(adjacent_mines) if adjacent_mines else ".")

        answer.append(answer_row)

    return format_board(answer)


def neighbours(row: int, column: int, rows: int, columns: int) -> list[tuple[int, int]]:
    """Return the in-bounds cells touching ``(row, column)`` (up to eight)."""
    nearby = []
    # Inspect the surrounding 3x3 square; the center is the cell itself, not a
    # neighbour, and positions outside the board are discarded below.
    for row_change in (-1, 0, 1):
        for column_change in (-1, 0, 1):
            if row_change == 0 and column_change == 0:
                continue
            neighbour_row = row + row_change
            neighbour_column = column + column_change
            if 0 <= neighbour_row < rows and 0 <= neighbour_column < columns:
                nearby.append((neighbour_row, neighbour_column))
    return nearby


def _check_matching_boards(answer_key: str, state: str) -> tuple[list[list[str]], list[list[str]]]:
    """Parse a key and state, checking they describe the same board shape."""
    key_grid = parse_board(answer_key)
    state_grid = parse_board(state)
    # The same coordinates must refer to the same cells in both boards, and
    # the answer key must contain truth values rather than hidden cells.
    if len(key_grid) != len(state_grid) or len(key_grid[0]) != len(state_grid[0]):
        raise ValueError("Answer key and game state must have the same dimensions.")
    if any(cell == "X" for row in key_grid for cell in row):
        raise ValueError("The answer key must be complete and contain no hidden cells.")
    return key_grid, state_grid


def reveal_cell(answer_key: str, state: str, row: int, column: int) -> tuple[str, bool]:
    """Click a hidden cell and return ``(updated_state, still_playing)``.

    A mine is shown as ``M`` and ends the game. Clicking a safe numbered cell
    reveals only that cell. Clicking a zero reveals the connected zero region
    and its numbered border using a stack-based flood fill.
    """
    key_grid, state_grid = _check_matching_boards(answer_key, state)
    rows, columns = len(key_grid), len(key_grid[0])
    # Reject invalid or repeated clicks before reading or changing a cell.
    if not (0 <= row < rows and 0 <= column < columns):
        raise ValueError("Clicked coordinates are outside the board.")
    if state_grid[row][column] != "X":
        raise ValueError("Only a hidden cell can be clicked.")

    # A clicked mine ends the game immediately. Reveal it in the returned
    # state so the trace shows which move caused the loss.
    if key_grid[row][column] == "M":
        state_grid[row][column] = "M"
        return format_board(state_grid), False

    # A safe click reveals its value. If it is zero, every neighbour is safe;
    # processing those neighbours recursively reveals the zero area and border.
    pending = [(row, column)]
    while pending:
        current_row, current_column = pending.pop()
        # Multiple zeros can queue the same cell. Process it only once so the
        # flood fill stays finite and does not redo work.
        if state_grid[current_row][current_column] != "X":
            continue

        # The game engine consults the key only at reveal time, then copies the
        # discovered value into the player's visible state.
        state_grid[current_row][current_column] = key_grid[current_row][current_column]

        # Only a zero expands the search. Numbered cells form the border and
        # do not reveal their other neighbours.
        if key_grid[current_row][current_column] == ".":
            pending.extend(neighbours(current_row, current_column, rows, columns))

    return format_board(state_grid), True


def is_won(answer_key: str, state: str) -> bool:
    """Return whether every safe cell in the answer key has been revealed."""
    # parse both
    key_grid, state_grid = _check_matching_boards(answer_key, state)
    # Mines need not be uncovered to win; every cell that is actually safe
    # must have been revealed.
    rows = len(key_grid)
    columns = len(key_grid[0])

    for row in range(rows):
        for column in range(columns):
            cell_is_hidden = state_grid[row][column] == "X"
            cell_is_mine = key_grid[row][column] == "M"

            # An unrevealed mine is fine. An unrevealed safe cell means the
            # player still has part of the board left to solve.
            if cell_is_hidden and not cell_is_mine:
                return False

    return True


def extract_constraints(state: str) -> list[Constraint]:
    """Return one named constraint for each revealed clue.

    Already marked mines are subtracted from the clue. The returned cell
    coordinates are zero-indexed ``(row, column)`` pairs. Clues with no hidden
    neighbours are included with an empty ``hidden_cells`` list and zero
    ``mines_needed``.
    """
    grid = parse_board(state)
    rows, columns = len(grid), len(grid[0])
    constraints = []

    # Each revealed clue becomes an equation: hidden neighbours must contain
    # the clue value minus the mines already identified around it.
    for row in range(rows):
        for column in range(columns):
            clue = grid[row][column]
            if clue not in "12345678.":
                continue

            adjacent_hidden = []
            known_mines = 0
            # Unknowns remain variables in the constraint; known mines are
            # already decided and reduce how many mines the clue still needs.
            for neighbour_row, neighbour_column in neighbours(row, column, rows, columns):
                neighbour = grid[neighbour_row][neighbour_column]
                if neighbour == "X":
                    adjacent_hidden.append((neighbour_row, neighbour_column))
                elif neighbour == "M":
                    known_mines += 1

            clue_value = 0 if clue == "." else int(clue)
            constraints.append(Constraint(
                hidden_cells=adjacent_hidden,
                mines_needed=clue_value - known_mines,
            ))

    return constraints





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
