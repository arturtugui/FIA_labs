"""Small, readable foundation for the Minesweeper CSP lab.

This file currently implements roadmap steps 1.1 (parse/format) and 1.4
(deterministic answer-key generation). Later lab steps can build on these
helpers without changing the board notation.
"""

import random

# FOUNDATION FUNCTIONS

def parse_board(text: str) -> list[list[str]]:
    """Convert a space-separated board string into a list of rows.

    Blank lines around or inside the board are ignored. Rows must have the
    same number of cells, and cells must use the lab's notation.
    """
    # split() handles repeated spaces too; blank lines are not board rows.
    rows = [line.split() for line in text.splitlines() if line.split()]
    if not rows:
        raise ValueError("A board must contain at least one row.")

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
    if rows < 1 or columns < 1:
        raise ValueError("Board dimensions must both be positive.")
    if not 0 <= mine_count <= rows * columns:
        raise ValueError("Mine count must fit within the board.")

    # Sampling distinct coordinates guarantees the requested exact mine count.
    all_cells = [(row, column)
                 for row in range(rows)
                 for column in range(columns)]
    # Use a private generator so calling this helper does not alter global RNG state.
    randomizer = random.Random(seed)

    # Randomly select a fixed number of unique coordinates to place mines, 
    # and convert them into a set for fast O(1) membership lookups.
    mines = set(randomizer.sample(all_cells, mine_count))

    answer = []
    for row in range(rows):
        answer_row = []
        for column in range(columns):
            if (row, column) in mines:
                answer_row.append("M")
                continue

            adjacent_mines = 0
            # Try the surrounding 3x3 area; discard the cell itself and anything
            # outside the board. This same loop naturally handles edges/corners.
            for row_change in (-1, 0, 1):
                for column_change in (-1, 0, 1):
                    if row_change == 0 and column_change == 0:
                        continue
                    neighbour = (row + row_change, column + column_change)
                    if neighbour in mines:
                        adjacent_mines += 1

            # The lab represents a zero clue with a dot instead of the digit 0.
            answer_row.append(str(adjacent_mines) if adjacent_mines else ".")

        answer.append(answer_row)

    return format_board(answer)
