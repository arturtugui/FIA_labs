"""Compare the two complete-game solvers on the saved benchmark board suites.

Run from this folder with ``python compare_solvers.py``. Reports are saved in
``results/``. The default run uses at most 25 intermediate and 3 expert boards.
Use ``--suite`` to select a suite or ``--limit`` to override the per-suite limits.
"""

import argparse
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# This script lives one folder below the solver module. Add mine_sweeper/ to
# Python's module search path so it can be run directly from this folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import minesweeper_solver as solver


SUITES_FILE = Path(__file__).with_name("benchmark_boards.txt")
RESULTS_FOLDER = Path(__file__).with_name("results")
SUITE_HEADER = re.compile(
    r"# suite (?P<name>\S+) rows=(?P<rows>\d+) cols=(?P<columns>\d+) mines=(?P<mines>\d+)"
)
BOARD_HEADER = re.compile(r"## board (?P<number>\d+)")


@dataclass
class BoardSuite:
    """A named group of answer boards and the properties they must satisfy."""

    name: str
    rows: int
    columns: int
    mine_count: int
    boards: list[str]


@dataclass
class SolverResults:
    """Totals collected while one solver processes one benchmark suite."""

    wins: int = 0
    losses: int = 0
    first_move_losses: int = 0
    clicks: int = 0
    winning_clicks: int = 0
    guesses: int = 0
    search_nodes: int = 0
    elapsed_seconds: float = 0.0
    longest_game_seconds: float = 0.0


def validate_answer_key(board_text: str, suite: BoardSuite, board_number: int) -> None:
    """Check dimensions, mine total, and every clue before benchmarking a board."""
    grid = solver.parse_board(board_text)

    if len(grid) != suite.rows or len(grid[0]) != suite.columns:
        raise ValueError(
            f"{suite.name}, board {board_number}: expected "
            f"{suite.rows}x{suite.columns}, got {len(grid)}x{len(grid[0])}."
        )

    if any(cell == "X" for row in grid for cell in row):
        raise ValueError(f"{suite.name}, board {board_number}: answer key contains X.")

    actual_mines = sum(cell == "M" for row in grid for cell in row)
    if actual_mines != suite.mine_count:
        raise ValueError(
            f"{suite.name}, board {board_number}: expected {suite.mine_count} mines, "
            f"found {actual_mines}."
        )

    # Validate clue values independently so malformed benchmark data cannot
    # quietly make both solvers look better or worse than they are.
    for row in range(suite.rows):
        for column in range(suite.columns):
            cell = grid[row][column]
            if cell in {"M", "."}:
                continue

            adjacent_mines = 0
            for nearby_row in range(max(0, row - 1), min(suite.rows, row + 2)):
                for nearby_column in range(max(0, column - 1), min(suite.columns, column + 2)):
                    if grid[nearby_row][nearby_column] == "M":
                        adjacent_mines += 1

            if int(cell) != adjacent_mines:
                raise ValueError(
                    f"{suite.name}, board {board_number}: clue at "
                    f"({row}, {column}) is {cell}, but should be {adjacent_mines}."
                )


def read_suites(path: Path) -> list[BoardSuite]:
    """Read suite metadata and each following block of space-separated rows."""
    suites: list[BoardSuite] = []
    current_suite: BoardSuite | None = None
    current_board_rows: list[str] | None = None
    current_board_number = 0

    def finish_board() -> None:
        """Save and validate the board currently being read, if there is one."""
        nonlocal current_board_rows
        if current_board_rows is None:
            return
        if current_suite is None:
            raise ValueError("A board was found before its suite header.")
        if len(current_board_rows) != current_suite.rows:
            raise ValueError(
                f"{current_suite.name}, board {current_board_number}: expected "
                f"{current_suite.rows} rows, found {len(current_board_rows)}."
            )

        board_text = "\n".join(current_board_rows)
        validate_answer_key(board_text, current_suite, current_board_number)
        current_suite.boards.append(board_text)
        current_board_rows = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue

        suite_match = SUITE_HEADER.fullmatch(line)
        if suite_match:
            finish_board()
            current_suite = BoardSuite(
                name=suite_match.group("name"),
                rows=int(suite_match.group("rows")),
                columns=int(suite_match.group("columns")),
                mine_count=int(suite_match.group("mines")),
                boards=[],
            )
            suites.append(current_suite)
            continue

        board_match = BOARD_HEADER.fullmatch(line)
        if board_match:
            finish_board()
            if current_suite is None:
                raise ValueError(f"Line {line_number}: board appears before a suite header.")
            current_board_number = int(board_match.group("number"))
            current_board_rows = []
            continue

        if line.startswith("#"):
            # Allow standalone notes and seed metadata in the text file.
            continue

        if current_board_rows is None:
            raise ValueError(f"Line {line_number}: unexpected content outside a board.")
        current_board_rows.append(line)

    finish_board()

    if not suites:
        raise ValueError(f"No suites were found in {path}.")
    if any(not suite.boards for suite in suites):
        raise ValueError("Every suite must contain at least one board.")
    return suites


def run_solver(use_propagation: bool, boards: list[str]) -> SolverResults:
    """Play every board and collect outcome, guessing, search, and timing data."""
    results = SolverResults()
    for answer_key in boards:
        # Counters are local to a single game, then accumulated below. Search
        # nodes count tried safe/mine branch values; forced deductions do not.
        game_stats = {"nodes": 0, "guesses": 0}
        start_time = time.perf_counter()
        steps = solver._solve_game(
            answer_key,
            use_propagation=use_propagation,
            game_stats=game_stats,
        )
        game_seconds = time.perf_counter() - start_time
        results.elapsed_seconds += game_seconds
        results.longest_game_seconds = max(results.longest_game_seconds, game_seconds)
        results.clicks += len(steps)
        results.guesses += game_stats["guesses"]
        results.search_nodes += game_stats["nodes"]

        # The last recorded state describes the board after the solver's final
        # click. Zero clicks cannot win a non-empty Minesweeper game.
        if steps and solver.is_won(answer_key, steps[-1][1]):
            results.wins += 1
            results.winning_clicks += len(steps)
        else:
            results.losses += 1
            key_grid = solver.parse_board(answer_key)
            first_row, first_column = steps[0][0]
            if key_grid[first_row][first_column] == "M":
                results.first_move_losses += 1
    return results


def print_suite_results(name: str, board_count: int, plain: SolverResults,
                        propagated: SolverResults) -> str:
    """Format the game and search measures as a Markdown table."""
    table_lines = [
        f"## {name} ({board_count} boards)",
        "",
        "| Solver | Won | Lost (first move) | Win % excl. first move | "
        "Moves/game | Moves/won game | Guesses/game | Search nodes/game | ms/game (max) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for solver_name, results in (
        ("pure backtracking", plain),
        ("backtracking + propagation", propagated),
    ):
        games_after_opening_mine = board_count - results.first_move_losses
        win_rate_after_opening = (
            100 * results.wins / games_after_opening_mine
            if games_after_opening_mine
            else 0.0
        )
        average_winning_moves = (
            results.winning_clicks / results.wins if results.wins else 0.0
        )
        table_lines.append(
            f"| {solver_name} | {results.wins} | {results.losses} "
            f"({results.first_move_losses}) | {win_rate_after_opening:.1f}% "
            f"| {results.clicks / board_count:.2f} "
            f"| {average_winning_moves:.2f} "
            f"| {results.guesses / board_count:.2f} "
            f"| {results.search_nodes / board_count:.0f} "
            f"| {results.elapsed_seconds * 1000 / board_count:.2f} "
            f"({results.longest_game_seconds * 1000:.0f}) |"
        )
    return "\n".join(table_lines)


def main() -> None:
    """Parse options, validate the complete file, then compare selected suites."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file", type=Path, default=SUITES_FILE,
        help="benchmark text file (default: benchmark_boards.txt beside this script)",
    )
    parser.add_argument("--suite", help="run only the suite with this exact name")
    parser.add_argument(
        "--limit", type=int,
        help="run only the first N boards in each selected suite (overrides default limits)",
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive number")

    suites = read_suites(args.file)
    if args.suite:
        suites = [suite for suite in suites if suite.name == args.suite]
        if not suites:
            parser.error(f"unknown suite {args.suite!r}; use --help after checking suite names")

    total_boards = sum(len(suite.boards) for suite in suites)
    print(f"Validated {total_boards} boards from {args.file.name}.")
    print("Running benchmark suites; progress will be shown here.")

    totals_plain = SolverResults()
    totals_propagated = SolverResults()
    total_count = 0
    report_sections = [
        "# Minesweeper Solver Benchmark",
        "",
        f"Board source: `{args.file.name}` ({total_boards} validated answer boards).",
        "Both solvers play the same selected boards using the same deterministic "
        "click policy. Timing measures solving only.",
        "",
        "Search nodes count tried safe/mine branch values, including failed "
        "trials. Values forced by propagation are deductions and are not counted.",
        "Guesses count clicks made when clue reasoning did not prove a safe cell; "
        "the fixed opening click is excluded.",
        "",
    ]

    # Bound the expensive large-board suites by default while keeping every
    # board in the smaller suites. --limit explicitly overrides these caps.
    default_limits = {
        "intermediate_16x16_40": 25,
        "expert_16x30_99": 3,
    }

    for suite_index, suite in enumerate(suites):
        board_limit = args.limit or default_limits.get(suite.name, len(suite.boards))
        boards = suite.boards[:board_limit]
        print(f"Running {suite.name}: {len(boards)} of {len(suite.boards)} boards...", flush=True)
        # Alternate which solver runs first per suite to reduce systematic
        # timing bias from one implementation always running first.
        if suite_index % 2 == 0:
            plain = run_solver(use_propagation=False, boards=boards)
            propagated = run_solver(use_propagation=True, boards=boards)
        else:
            propagated = run_solver(use_propagation=True, boards=boards)
            plain = run_solver(use_propagation=False, boards=boards)

        report_sections.append(
            print_suite_results(suite.name, len(boards), plain, propagated)
        )
        print(f"Finished {suite.name}.", flush=True)
        totals_plain.wins += plain.wins
        totals_plain.losses += plain.losses
        totals_plain.first_move_losses += plain.first_move_losses
        totals_plain.clicks += plain.clicks
        totals_plain.winning_clicks += plain.winning_clicks
        totals_plain.guesses += plain.guesses
        totals_plain.search_nodes += plain.search_nodes
        totals_plain.elapsed_seconds += plain.elapsed_seconds
        totals_plain.longest_game_seconds = max(
            totals_plain.longest_game_seconds, plain.longest_game_seconds
        )
        totals_propagated.wins += propagated.wins
        totals_propagated.losses += propagated.losses
        totals_propagated.first_move_losses += propagated.first_move_losses
        totals_propagated.clicks += propagated.clicks
        totals_propagated.winning_clicks += propagated.winning_clicks
        totals_propagated.guesses += propagated.guesses
        totals_propagated.search_nodes += propagated.search_nodes
        totals_propagated.elapsed_seconds += propagated.elapsed_seconds
        totals_propagated.longest_game_seconds = max(
            totals_propagated.longest_game_seconds, propagated.longest_game_seconds
        )
        total_count += len(boards)

    if len(suites) > 1:
        report_sections.append(
            print_suite_results("Overall", total_count, totals_plain, totals_propagated)
        )

    # Each section may already include Markdown spacing; trimming first keeps
    # the report readable without large blank gaps between its tables.
    report_text = "\n\n".join(section.strip() for section in report_sections)

    # Give every execution its own report so earlier benchmark results remain
    # available for comparisons. Add a counter only if the name already exists.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_FOLDER / f"benchmark_{timestamp}.md"
    duplicate_number = 2
    while report_path.exists():
        report_path = RESULTS_FOLDER / f"benchmark_{timestamp}_{duplicate_number}.md"
        duplicate_number += 1

    report_path.write_text(report_text + "\n", encoding="utf-8")
    print(f"Benchmark complete. Full results saved to {report_path.name}.")


if __name__ == "__main__":
    main()
