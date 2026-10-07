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


# A cell assignment maps a coordinate to its assumed status during search:
# 1 means mine and 0 means safe.
Assignment = dict[tuple[int, int], int]


# FOUNDATION FUNCTIONS

class Constraint(NamedTuple):
    """One clue's remaining rule for the hidden cells around it.

    ``hidden_cells`` lists the unknown coordinates. ``mines_needed`` says how
    many of those cells must be mines; the others must therefore be safe.
    """

    hidden_cells: list[tuple[int, int]]
    mines_needed: int


# backtracking_step has no answer key, so it cannot reveal a safe cell's clue.
# Remember which cells it has already checked when the caller feeds the same
# board back in; otherwise a safe/uncertain check would repeat forever.
_BACKTRACKING_STEP_CHECKED: dict[str, set[tuple[int, int]]] = {}

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


# Task 2 -- Constraint propagation

def constraint_propagation(state: str) -> str:  # REQUIRED
    """Mark mines forced by the basic all-mines and all-safe rules.

    This function does not guess or search. Safe deductions are tracked while
    reasoning, because removing a known-safe cell can make another clue force
    its remaining hidden cells to be mines. The output only displays newly
    deduced mines, as required by the lab.
    """
    # Work with two views of the position:
    # - grid is the text we must eventually return;
    # - constraints are the clue equations we use to reason.
    grid = parse_board(state)
    constraints = extract_constraints(state)

    # Keep deductions separate from the displayed board. A deduced safe cell
    # remains X in the result, but is treated as safe during reasoning.
    # For each cell found by reasoning, remember either "M" or "safe".
    # These labels are internal: the requested output only shows new mines.
    deductions: dict[tuple[int, int], str] = {}
    changed = True

    # One clue's deductions can simplify another clue, so make passes until a
    # complete pass discovers no additional cell status.
    while changed:
        changed = False

        # A pass means: revisit every clue using all deductions made so far.
        for constraint in constraints:
            # mines_needed is the clue count after input M marks were
            # subtracted by extract_constraints(). We subtract any additional
            # mines found in earlier propagation passes here.
            remaining_mines = constraint.mines_needed
            unresolved_cells = []

            # Split the clue's original hidden neighbours into three groups:
            # known mines, known safe cells, and cells we still have to decide.
            for cell in constraint.hidden_cells:
                cell_status = deductions.get(cell)
                if cell_status == "M":
                    remaining_mines -= 1
                elif cell_status is None:
                    unresolved_cells.append(cell)
                # A cell marked "safe" belongs in neither group above.

            # An impossible remaining count means the clues contradict each
            # other or the input marks; avoid making deductions from it.
            if remaining_mines < 0 or remaining_mines > len(unresolved_cells):
                raise ValueError("The game state contains contradictory clues.")

            if not unresolved_cells:
                continue

            # All-mines rule: if every unresolved cell is needed to reach the
            # clue's count, all of them must be mines.
            if remaining_mines == len(unresolved_cells):
                # Example: 2 mines still needed among 2 unknown cells means
                # both unknown cells must be mines.
                for cell in unresolved_cells:
                    if deductions.get(cell) != "M":
                        deductions[cell] = "M"
                        changed = True

            # All-safe rule: if the clue already has its full mine count, its
            # other unresolved neighbours must be safe.
            elif remaining_mines == 0:
                # Example: 0 mines still needed among 3 unknown cells means
                # all 3 can be safely excluded as mines.
                for cell in unresolved_cells:
                    if cell not in deductions:
                        deductions[cell] = "safe"
                        changed = True

    # At this point a full pass made no new mine or safe deduction, so the
    # basic rules have reached their fixpoint and another pass cannot help.
    # Only mine deductions are shown in the output. Safe deductions above are
    # internal reasoning facts and leave their original X symbols untouched.
    for (row, column), status in deductions.items():
        if status == "M":
            grid[row][column] = "M"

    return format_board(grid)



# Task 1 -- Backtracking

def _frontier_cells(constraints: list[Constraint]) -> list[tuple[int, int]]:
    """Return unique hidden coordinates that appear in at least one clue."""
    cells = set()
    for constraint in constraints:
        cells.update(constraint.hidden_cells)
    return sorted(cells)


def _hidden_neighbour_count(
    grid: list[list[str]],
    cell: tuple[int, int],
) -> int:
    """Count currently hidden neighbours, as a simple information heuristic."""
    rows = len(grid)
    columns = len(grid[0])
    row, column = cell
    hidden_count = 0

    for neighbour_row, neighbour_column in neighbours(row, column, rows, columns):
        if grid[neighbour_row][neighbour_column] == "X":
            hidden_count += 1

    return hidden_count


def _assignment_is_consistent(
    constraints: list[Constraint],
    assignments: Assignment,
) -> bool:
    """Check whether the current search choices can still satisfy all clues.

    ``assignments`` maps a cell coordinate such as ``(row, column)`` to a
    temporary value: 1 means the search is trying that cell as a mine, and 0
    means it is trying the cell as safe. A cell absent from the dictionary has
    not been tried yet.

    The function checks each clue independently and returns False as soon as
    one clue can no longer be satisfied. Returning True means only that no
    contradiction has been found so far; undecided cells may remain.
    """
    for constraint in constraints:
        assigned_mines = 0
        unassigned_count = 0

        # Look only at the hidden neighbours that belong to this clue.
        for cell in constraint.hidden_cells:
            if cell in assignments:
                # Adding a 1 counts a mine; adding a 0 leaves the count alone
                # for a cell the search has assumed safe.
                assigned_mines += assignments[cell]
            else:
                # Any of these cells could still become a mine and help meet
                # the clue's required count.
                unassigned_count += 1

        # If we already chose more mines than the clue allows, undoing a later
        # choice cannot fix this branch: its current assumptions are wrong.
        if assigned_mines > constraint.mines_needed:
            return False

        # Even turning every undecided neighbour into a mine would not be
        # enough here, so no continuation of this branch can satisfy the clue.
        if assigned_mines + unassigned_count < constraint.mines_needed:
            return False

    # Every clue can still reach its target. Search may continue assigning
    # cells; this is not yet proof that the whole board is solved.
    return True


def _find_frontier_solution(
    constraints: list[Constraint],
    fixed_choices: Assignment | None = None,
    search_stats: dict[str, int] | None = None,
) -> Assignment | None:
    """Find one complete assignment that satisfies all frontier clues.

    Args:
        constraints: The clue equations from the current visible game state.
        fixed_choices: Optional assumptions to hold constant while searching.
            For example, ``{(2, 3): 1}`` asks whether cell ``(2, 3)`` can be a
            mine in any valid solution.
        search_stats: Optional caller-owned measurement counter. Its purpose
            is to compare how much branching search methods do; it does not
            change the search or its answer. Each tried value increases the
            ``"nodes"`` count, including failed trials. Automatically deduced
            values do not count.

    The function returns a dictionary assigning every frontier cell 0 (safe)
    or 1 (mine). It returns None when the assumptions make all solutions
    impossible. Cells outside the frontier are not included because no clue
    currently constrains them. The optional ``search_stats`` exists only to
    measure branching effort; the solver works the same if it is omitted.
    Initialize it as ``{"nodes": 0}`` before calling.
    """
    cells = _frontier_cells(constraints)
    assignments = dict(fixed_choices or {})

    # An assumption about an interior cell cannot be checked using frontier
    # clues, so treat that request as having no solution in this search.
    if any(cell not in cells for cell in assignments):
        return None

    # Catch impossible assumptions before starting the recursive search.
    if not _assignment_is_consistent(constraints, assignments):
        return None

    # Cells touching more clues can expose contradictions sooner. Start with
    # row-major order, then stably move high-degree cells to the front so ties
    # are deterministic for the same board.
    def constraint_count(cell: tuple[int, int]) -> int:
        """Count how many separate clues mention this cell."""
        count = 0
        for constraint in constraints:
            if cell in constraint.hidden_cells:
                count += 1
        return count

    ordered_cells = sorted(cells)
    ordered_cells.sort(key=constraint_count, reverse=True)

    def search(next_index: int) -> bool:
        """Try values recursively, leaving a full assignment on success."""
        # Skip cells already decided by fixed_choices; search must not replace
        # the assumption being tested with a different value.
        while next_index < len(ordered_cells) and ordered_cells[next_index] in assignments:
            next_index += 1

        # Reaching the end means every frontier cell has a value. If all clue
        # bounds still hold, these choices form one complete valid world.
        if next_index == len(ordered_cells):
            return _assignment_is_consistent(constraints, assignments)

        cell = ordered_cells[next_index]

        # Try safe first to make the search deterministic. This ordering is a
        # convenience only; it is not evidence that safe is the correct value.
        for value in (0, 1):
            if search_stats is not None:
                # Record the trial so tests can compare search effort. This is
                # measurement only and does not affect the branch decision.
                # Failed trials count because they still took search work.
                search_stats["nodes"] = search_stats.get("nodes", 0) + 1
            assignments[cell] = value

            # If this partial choice has already broken a clue, do not waste
            # time assigning the rest of the cells below this branch.
            if _assignment_is_consistent(constraints, assignments):
                if search(next_index + 1):
                    return True

            # This branch failed. Remove its temporary choice before trying
            # the other value for the same cell.
            del assignments[cell]

        return False

    if search(0):
        return assignments.copy()
    return None


def _propagate_assignments(
    constraints: list[Constraint],
    current_assignments: Assignment,
) -> Assignment | None:
    """Apply the basic all-mines/all-safe rules to one search branch.

    The input is copied, so deductions made here belong only to this branch.
    ``None`` means that some clue cannot reach its required mine count. A
    returned dictionary includes both the original choices and every value
    forced by repeatedly applying the two basic rules.
    """
    assignments = current_assignments.copy()

    # A deduction from one clue can change what another clue needs. Keep
    # scanning until a full pass adds no more forced assignments.
    made_a_deduction = True
    while made_a_deduction:
        made_a_deduction = False

        for constraint in constraints:
            assigned_mines = 0
            unassigned_cells = []

            # Separate this clue's neighbours into already chosen cells and
            # cells whose value still needs to be decided.
            for cell in constraint.hidden_cells:
                if cell in assignments:
                    assigned_mines += assignments[cell]
                else:
                    unassigned_cells.append(cell)

            mines_still_needed = constraint.mines_needed - assigned_mines

            # Too many assigned mines, or too few undecided cells to supply
            # the remaining mines, means this branch can never be completed.
            if mines_still_needed < 0:
                return None
            if mines_still_needed > len(unassigned_cells):
                return None

            if not unassigned_cells:
                continue

            # If no more mines are needed, every unknown neighbour is safe.
            if mines_still_needed == 0:
                forced_value = 0
            # If every unknown neighbour is needed to reach the clue, all are
            # mines. These are the same two rules used by Task 2.
            elif mines_still_needed == len(unassigned_cells):
                forced_value = 1
            else:
                # This clue alone does not force any of its remaining cells.
                continue

            for cell in unassigned_cells:
                assignments[cell] = forced_value
                made_a_deduction = True

    return assignments


def _find_frontier_solution_with_propagation(
    constraints: list[Constraint],
    fixed_choices: Assignment | None = None,
    search_stats: dict[str, int] | None = None,
) -> Assignment | None:
    """Find one valid frontier assignment, propagating after every guess.

    Unlike ``_find_frontier_solution``, each trial value is immediately sent
    through ``_propagate_assignments``. Forced neighbours are filled in before
    choosing another branch cell, and an impossible branch is abandoned at
    once.

    ``search_stats`` is an optional measurement counter supplied by the
    caller, usually as ``{"nodes": 0}``. Its purpose is to compare the work
    done by this search with pure backtracking; it does not affect which
    assignments are accepted or the solver's game decisions. Each trial mine
    or safe value adds one to ``search_stats["nodes"]``. Values filled by
    propagation do not count because they are deductions, not branches. The
    dictionary is changed in place so the caller can read the count afterward.
    """
    cells = _frontier_cells(constraints)
    assignments = dict(fixed_choices or {})

    # A fixed choice can only be checked when it belongs to a clue constraint.
    if any(cell not in cells for cell in assignments):
        return None

    # Propagate assumptions before branching; they may already prove values or
    # reveal that the caller's hypothesis contradicts a clue.
    propagated_assignments = _propagate_assignments(constraints, assignments)
    if propagated_assignments is None:
        return None
    assignments = propagated_assignments

    # As in the pure solver, prioritize cells shared by more clues. This helps
    # contradictions appear early and keeps the search order deterministic.
    def constraint_count(cell: tuple[int, int]) -> int:
        count = 0
        for constraint in constraints:
            if cell in constraint.hidden_cells:
                count += 1
        return count

    ordered_cells = sorted(cells)
    ordered_cells.sort(key=constraint_count, reverse=True)

    def search(current_assignments: Assignment, next_index: int) -> Assignment | None:
        """Return a completed assignment, or None if this branch fails."""
        # Propagation may have filled cells that appear later in the order, so
        # skip them instead of making a redundant mine/safe guess.
        while (
            next_index < len(ordered_cells)
            and ordered_cells[next_index] in current_assignments
        ):
            next_index += 1

        if next_index == len(ordered_cells):
            return current_assignments.copy()

        cell = ordered_cells[next_index]

        # Try safe first, matching the pure solver's deterministic order.
        for value in (0, 1):
            if search_stats is not None:
                # Record actual branch work for comparison. Automatically
                # forced values below are deductions, so they are not counted.
                search_stats["nodes"] = search_stats.get("nodes", 0) + 1

            # Each branch gets its own copy. Deductions from one assumption
            # must not leak into the alternative assumption.
            branch_assignments = current_assignments.copy()
            branch_assignments[cell] = value

            # Immediately propagate this choice. A contradiction kills this
            # branch; otherwise continue with all of its forced consequences.
            propagated_branch = _propagate_assignments(
                constraints,
                branch_assignments,
            )
            if propagated_branch is None:
                continue

            solution = search(propagated_branch, next_index + 1)
            if solution is not None:
                return solution

        return None

    return search(assignments, 0)


def _analyse_frontier(
    constraints: list[Constraint],
    search_stats: dict[str, int] | None = None,
) -> tuple[
    Assignment,
    list[tuple[int, int]],  # forced_mine_cells
    list[tuple[int, int]],  # forced_safe_cells
]:
    """Find one valid world, then separate certain cells from undecided ones.

    The returned triple is ``(one_solution, forced_mines, forced_safe)``.
    Here, a "world" means one possible mine/safe choice for every hidden cell
    touched by a visible clue. The solver does not know which world is the real
    board; it only knows that any world satisfying all clues is still possible.

    The function works in two passes:

    1. Find one complete assignment that obeys every clue. If none exists,
       the visible board contradicts itself.
    2. For each cell in that assignment, temporarily force the opposite value
       and search again. If no solution exists under that opposite value, the
       original value must be the same in every valid world, so it is certain.

    For example, suppose the first solution says a cell is a mine. If another
    valid solution exists with that cell safe, it is not a proven mine and is
    left out of both certainty lists. If no such solution exists, it goes in
    ``forced_mines``. The same reasoning identifies ``forced_safe`` cells.
    """
    first_solution = _find_frontier_solution(constraints, search_stats=search_stats)
    if first_solution is None:
        raise ValueError("The game state contains contradictory clues.")

    # These lists contain proofs, not merely the values from the first world.
    # A cell goes here only after the opposite-value search fails.
    forced_mines = []
    forced_safe = []

    for cell, value_in_solution in first_solution.items():
        # A value in one solution is not necessarily certain. Ask whether a
        # second solution exists with the opposite value; if not, this cell is
        # the same in every valid world and is therefore logically forced.
        opposite_value = 1 - value_in_solution
        opposite_solution = _find_frontier_solution(
            constraints,
            fixed_choices={cell: opposite_value},
            search_stats=search_stats,
        )

        if opposite_solution is None:
            if value_in_solution == 1:
                forced_mines.append(cell)
            else:
                forced_safe.append(cell)

    return first_solution, sorted(forced_mines), sorted(forced_safe)


def _analyse_frontier_with_propagation(
    constraints: list[Constraint],
    search_stats: dict[str, int] | None = None,
) -> tuple[
    Assignment,
    list[tuple[int, int]],  # forced_mine_cells
    list[tuple[int, int]],  # forced_safe_cells
]:
    """Find certain frontier values using search with forward propagation.

    The method is the same as ``_analyse_frontier``: find one valid world,
    then test whether each cell can take its opposite value. The difference is
    that every search branch immediately propagates the basic rules, allowing
    it to skip forced assignments and reject impossible branches earlier.
    """
    first_solution = _find_frontier_solution_with_propagation(
        constraints,
        search_stats=search_stats,
    )
    if first_solution is None:
        raise ValueError("The game state contains contradictory clues.")

    forced_mines = []
    forced_safe = []

    for cell, value_in_solution in first_solution.items():
        # A cell is certain only if no valid world exists with the other value.
        opposite_value = 1 - value_in_solution
        opposite_solution = _find_frontier_solution_with_propagation(
            constraints,
            fixed_choices={cell: opposite_value},
            search_stats=search_stats,
        )

        if opposite_solution is None:
            if value_in_solution == 1:
                forced_mines.append(cell)
            else:
                forced_safe.append(cell)

    return first_solution, sorted(forced_mines), sorted(forced_safe)


def backtracking_step(state: str) -> tuple[tuple[int, int], str]:  # REQUIRED
    """Search-check one hidden cell and return its coordinate and board text.

    This function demonstrates one backtracking check without playing a real
    click. Its steps are:

    1. Read the visible board and turn its numbered clues into constraints.
    2. Choose a hidden frontier cell (one mentioned by a clue) that this
       function has not checked yet. If there are no clues, choose any hidden
       cell because there is not enough information to constrain it.
    3. Ask the search twice: can the clues still be satisfied if this cell is
       a mine, and can they still be satisfied if it is safe?
    4. If only the mine assumption works, mark the cell ``M`` because the
       clues prove it is a mine. If both values work, it is uncertain. If only
       safe works, it is known safe but remains ``X`` because this function
       has no answer key to reveal its number.

    The return value is ``(checked_coordinate, resulting_board_text)``. Since
    an unchanged board gives the function no visible way to remember a prior
    safe/uncertain check, ``_BACKTRACKING_STEP_CHECKED`` stores those checks
    between calls. This is only demonstration progress: a real click would
    reveal a safe cell and change the board. If no hidden cells remain, the
    function returns ``((-1, -1), unchanged_board)``.
    """
    grid = parse_board(state)
    constraints = extract_constraints(state)
    frontier = _frontier_cells(constraints)
    hidden_cells = []
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            if grid[row][column] == "X":
                hidden_cells.append((row, column))

    if not hidden_cells:
        return (-1, -1), format_board(grid)

    # A frontier cell touches at least one revealed clue, so the equations can
    # test its two possible values. At the all-X start there are no equations;
    # selecting a cell then only demonstrates the lack of available evidence.
    candidates = frontier or hidden_cells
    board_text = format_board(grid)
    already_checked = _BACKTRACKING_STEP_CHECKED.get(board_text, set())
    unchecked = [cell for cell in candidates if cell not in already_checked]

    # When every current candidate was already checked, start over. This keeps
    # the function usable even when the caller requests extra steps.
    if not unchecked:
        already_checked = set()
        unchecked = candidates

    cell = unchecked[0]
    checked_now = set(already_checked)
    checked_now.add(cell)

    if frontier:
        # These are two independent hypothetical searches. Each search keeps
        # this cell fixed and tries to complete assignments for the other
        # frontier cells. A returned assignment means the assumption fits all
        # visible clues; None means it leads to a contradiction.
        mine_possible = _find_frontier_solution(
            constraints,
            fixed_choices={cell: 1},
        ) is not None
        safe_possible = _find_frontier_solution(
            constraints,
            fixed_choices={cell: 0},
        ) is not None

        if not mine_possible and not safe_possible:
            raise ValueError("The game state contains contradictory clues.")

        # Compare the two answers. If both are possible, the clues do not tell
        # us which value is real. If only safe is possible, the cell is safe,
        # but stays hidden because this step function has no key to reveal it.
        # Only mine-possible and safe-impossible justifies writing M here.
        if mine_possible and not safe_possible:
            grid[cell[0]][cell[1]] = "M"
            result = format_board(grid)
            _BACKTRACKING_STEP_CHECKED[result] = checked_now
            if len(_BACKTRACKING_STEP_CHECKED) > 1000:
                _BACKTRACKING_STEP_CHECKED.clear()
            return cell, result

    # A safe or uncertain result is not written into the board: X is the only
    # symbol available for an unrevealed safe cell, and this function has no
    # key to reveal its number. Save the check so the next call moves on.
    _BACKTRACKING_STEP_CHECKED[board_text] = checked_now
    if len(_BACKTRACKING_STEP_CHECKED) > 1000:
        _BACKTRACKING_STEP_CHECKED.clear()
    return cell, format_board(grid)


def _solve_game(
    answer_key: str,
    use_propagation: bool,
    game_stats: dict[str, int] | None = None,
) -> list[tuple[tuple[int, int], str]]:
    """Run one game using either pure search or search with propagation.

    This shared game loop keeps the two strategies comparable. The input is
    the complete answer key, but the solver acts as if it is playing from
    scratch. It first creates an all-``X`` view, then repeats the following
    turn until all safe cells are revealed or a guess hits a mine:

    1. Build constraints using only numbers visible in the current game view.
       A clue such as ``2`` means exactly two of its still-hidden neighbours
       must be mines, after subtracting any already marked ``M`` cells.
    2. Search the possible mine/safe assignments that fit those constraints.
       If ``use_propagation`` is true, apply the basic rules after every trial
       value. Mark values that are forced in every assignment. These marks do
       not count as clicks; they record what the visible clues prove.
    3. Prefer a cell proven safe. If no such cell exists, choose a plausible
       safe frontier cell that can still satisfy the clues and prefer one with
       more hidden neighbours, since its reveal may give more information.
       If no frontier cell can be safe, guess outside the frontier.
    4. Reveal the chosen cell and update the visible board. A zero clue also
       reveals its connected safe area, so one click can expose many cells.

    The answer key is used by ``is_won`` to know when the game is complete and
    by ``reveal_cell`` to simulate what a click reveals. It does not help
    choose the next coordinate. Each returned item is
    ``(clicked_coordinate, board_after_click)``. A final board can also contain
    ``M`` marks for mines proved by the search.
    """
    key_grid = parse_board(answer_key)
    if any(cell == "X" for row in key_grid for cell in row):
        raise ValueError("backtracking_solve requires a complete answer key.")

    rows, columns = len(key_grid), len(key_grid[0])
    grid = [["X" for _ in range(columns)] for _ in range(rows)]
    steps = []

    # A win means every safe cell is visible. Mines may remain hidden or be
    # marked M because they are not cells the player needs to click.
    while not is_won(answer_key, format_board(grid)):
        state = format_board(grid)
        constraints = extract_constraints(state)
        frontier = _frontier_cells(constraints)

        # Select one search implementation for this entire turn. The pure
        # version checks only whether partial assignments can still fit. The
        # Task 3 version also fills any values forced by the basic rules.
        if use_propagation:
            analyse_frontier = _analyse_frontier_with_propagation
            find_frontier_solution = _find_frontier_solution_with_propagation
        else:
            analyse_frontier = _analyse_frontier
            find_frontier_solution = _find_frontier_solution

        if frontier:
            # Analyze only the visible clues. No answer-key cells are used to
            # decide these deductions or the next click. ``one_solution`` is
            # just one consistent possibility; only the two forced lists are
            # safe to treat as facts about every possible board.
            _, forced_mines, forced_safe = analyse_frontier(
                constraints,
                search_stats=game_stats,
            )

            # Mark every logically forced mine so future clue equations can
            # subtract it. These are deductions, not clicks.
            for mine_row, mine_column in forced_mines:
                grid[mine_row][mine_column] = "M"

            # A forced-safe cell is guaranteed not to lose the game. Prefer it
            # over guessing because its click must reveal useful information.
            safe_to_click = []
            for cell in forced_safe:
                row, column = cell
                if grid[row][column] == "X":
                    safe_to_click.append(cell)

            if safe_to_click:
                # A proven-safe click cannot lose. Use row-major order so the
                # same visible board always produces a reproducible choice.
                cell_to_click = safe_to_click[0]
            else:
                if game_stats is not None:
                    # This turn needs a guess because search proved no hidden
                    # frontier cell safe. The fixed opening click is excluded.
                    game_stats["guesses"] = game_stats.get("guesses", 0) + 1

                # No safe value is forced. Find cells that can be safe in at
                # least one consistent world, then prefer the click that would
                # reveal the most nearby information. This is still a guess.
                possible_safe_guesses = []
                for candidate in frontier:
                    candidate_row, candidate_column = candidate
                    if grid[candidate_row][candidate_column] != "X":
                        continue
                    safe_assumption_works = find_frontier_solution(
                        constraints,
                        fixed_choices={candidate: 0},
                        search_stats=game_stats,
                    ) is not None
                    if safe_assumption_works:
                        possible_safe_guesses.append(candidate)

                if possible_safe_guesses:
                    # A cell with more hidden neighbours can expose a more
                    # useful clue, or open a larger region if its value is 0.
                    # The candidates are already row-major, so ties stay
                    # reproducible by keeping the first equally scored cell.
                    cell_to_click = possible_safe_guesses[0]
                    best_information_score = _hidden_neighbour_count(
                        grid, cell_to_click
                    )

                    for candidate in possible_safe_guesses[1:]:
                        information_score = _hidden_neighbour_count(grid, candidate)
                        if information_score > best_information_score:
                            cell_to_click = candidate
                            best_information_score = information_score
                else:
                    # Every frontier cell may be a mine. Look for a hidden
                    # cell outside the frontier; with no clue it is a guess.
                    unconstrained = []
                    for row in range(rows):
                        for column in range(columns):
                            cell = (row, column)
                            if grid[row][column] == "X" and cell not in frontier:
                                unconstrained.append(cell)
                    if not unconstrained:
                        # All remaining cells are known mines, so they cannot
                        # be clicked. Mark them and the next loop detects a win.
                        for row in range(rows):
                            for column in range(columns):
                                if grid[row][column] == "X":
                                    grid[row][column] = "M"
                        continue
                    cell_to_click = unconstrained[0]
        else:
            # At the start there are no clues. Choose a corner for the first
            # click; it has fewer neighbours and often opens useful information.
            # If the board later has another clue-free area, that click is also
            # a guess, while the fixed opening click is excluded from the count.
            if steps and game_stats is not None:
                game_stats["guesses"] = game_stats.get("guesses", 0) + 1

            hidden_cells = []
            for row in range(rows):
                for column in range(columns):
                    if grid[row][column] == "X":
                        hidden_cells.append((row, column))
            if not hidden_cells:
                break
            cell_to_click = (0, 0) if grid[0][0] == "X" else hidden_cells[0]

        # This is the boundary between reasoning and simulating the click: all
        # choices above used only visible information. Now the engine consults
        # the key to show what the chosen click actually reveals.
        next_state, still_playing = reveal_cell(
            answer_key,
            format_board(grid),
            cell_to_click[0],
            cell_to_click[1],
        )
        steps.append((cell_to_click, next_state))
        grid = parse_board(next_state)

        # A mine click ends the game; its M is visible in the final trace board.
        if not still_playing:
            break

    return steps


def backtracking_solve(answer_key: str) -> list[tuple[tuple[int, int], str]]:  # REQUIRED
    """Play from an all-hidden board using pure backtracking only."""
    return _solve_game(answer_key, use_propagation=False)


# Task 3 -- Backtracking + constraint propagation
def backtrack_constraint(answer_key: str) -> list[tuple[tuple[int, int], str]]:  # REQUIRED
    """Play from an all-hidden board using backtracking with propagation.

    Whenever search tries a mine/safe value, the basic all-mines and all-safe
    rules are applied to a fixpoint before search branches again. Forced cells
    are therefore assigned without extra guesses, and contradictions stop a
    branch as soon as they appear. The returned click trace has the same format
    as ``backtracking_solve``.
    """
    return _solve_game(answer_key, use_propagation=True)


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
