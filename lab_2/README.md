# Lab 2 Report — Minesweeper as a CSP

## Task 3 comparison

The lab asks for both solvers to run on the same set of generated boards and to compare moves, wins/losses, and running time. The benchmark file contains 400 validated answer keys under a fixed seed. The default run includes all 100 beginner boards, all 100 denser 9×9 boards, 25 of 100 intermediate boards, 3 of 50 expert boards, and all 50 rectangular boards: **278 games per solver**. The smaller intermediate and expert samples keep the run manageable.

Both solvers use the same fixed top-left opening click and the same deterministic decision rules afterward. Consequently, they play the same boards with the same click choices. A first-click loss is counted separately inside the loss count. “Moves/game” is the mean number of clicks over all games; “moves/won game” is the mean for wins only. Guesses count later clicks made when reasoning could not prove a safe cell; the fixed opening click is excluded.

### How the solver algorithms differ

All three methods turn the visible clues into constraints on hidden frontier
cells. A hidden cell is a variable with two possible values: safe or mine. A
clue such as `2` requires exactly two of its still-hidden neighbours to be
mines, after subtracting mines already marked `M`. The methods differ in how
they find assignments that satisfy those constraints and how much they infer
before branching.

**Pure backtracking (Task 1)** tries one value for a hidden cell, then continues
recursively with another cell. After each choice it checks whether any clue is
already impossible: the choices must not exceed the clue's mine count, and
the unassigned neighbours must still be numerous enough to reach it. If a
branch fails, the solver undoes its latest choice and tries the other value.
Once it finds one complete valid assignment, it tests each cell again with
the opposite value fixed. If that second search finds no valid assignment,
the original value is forced by the clues. This is complete reasoning, but it
can explore many branches before proving that a cell is certain.

**Backtracking with basic propagation (Task 3)** still searches the same mine
and safe choices and uses the same opposite-value checks to distinguish a
possible value from a certain one. The difference is what happens after each
trial: the solver repeatedly applies the basic clue rules. If a clue already
has all the mines it needs, its other hidden neighbours are safe. If every
remaining hidden neighbour is needed to satisfy a clue, they are mines. These
new assignments can trigger more deductions in other clues. A contradictory
branch is rejected as soon as propagation discovers it, and forced values do
not need their own search branches.

**Advanced propagation (Task 6)** adds the subset-difference rule to those
basic deductions. When one clue's unresolved cell set is contained in another
clue's set, subtracting the smaller equation from the larger can determine the
cells that remain. The solver applies this extra rule before branching, then
continues its search with the basic propagation rules. It can prove values
that basic propagation cannot, although checking pairs of constraints costs
additional time. All methods use the same visible clues and safe-cell
selection policy, so a lower search-node count measures less branching work;
it does not by itself guarantee shorter runtime.

| Board suite (games) | Solver | Won | Lost (first click) | Win rate excluding first-click losses | Moves/game (won games only) | Guesses/game | Search nodes/game | Time ms/game (maximum) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 9×9, 10 mines (100) | Pure backtracking | 69 | 31 (9) | 75.8% | 16.53 (22.09) | 0.81 | 1,503 | 33.03 (382) |
|  | Backtracking + propagation | 69 | 31 (9) | 75.8% | 16.53 (22.09) | 0.81 | 124 | 16.92 (177) |
| 9×9, 15 mines (100) | Pure backtracking | 43 | 57 (16) | 51.2% | 19.84 (34.23) | 1.59 | 2,526 | 45.99 (415) |
|  | Backtracking + propagation | 43 | 57 (16) | 51.2% | 19.84 (34.23) | 1.59 | 277 | 25.57 (144) |
| 16×16, 40 mines (25) | Pure backtracking | 15 | 10 (1) | 62.5% | 68.56 (89.00) | 1.08 | 20,370 | 1,076.53 (3,265) |
|  | Backtracking + propagation | 15 | 10 (1) | 62.5% | 68.56 (89.00) | 1.08 | 1,455 | 445.38 (1,124) |
| 16×30, 99 mines (3) | Pure backtracking | 1 | 2 (0) | 33.3% | 65.00 (189.00) | 2.00 | 31,516 | 1,289.51 (3,860) |
|  | Backtracking + propagation | 1 | 2 (0) | 33.3% | 65.00 (189.00) | 2.00 | 2,021 | 645.49 (1,930) |
| 9×12, 16 mines (50) | Pure backtracking | 31 | 19 (8) | 73.8% | 23.54 (35.65) | 0.72 | 2,003 | 47.45 (225) |
|  | Backtracking + propagation | 31 | 19 (8) | 73.8% | 23.54 (35.65) | 0.72 | 148 | 41.66 (234) |
| **Overall (278)** | **Pure backtracking** | **159** | **119 (34)** | **65.2%** | **24.18 (35.38)** | **1.11** | **3,982** | **147.68 (3,860)** |
|  | **Backtracking + propagation** | **159** | **119 (34)** | **65.2%** | **24.18 (35.38)** | **1.11** | **323** | **69.79 (1,930)** |

### What the results show

Wins, losses, guesses, and move counts are identical between these two versions. That is expected here: pure backtracking and backtracking with propagation are both complete for the visible frontier constraints, and both use the same fixed click policy. Propagation changes the work needed to reach a decision, not which deductions are logically certain. This is why Task 3's improvement is most visible in search cost rather than game outcome.

Across the 278 games, propagation reduced the measured search nodes from 3,982 to 323 per game on average—about **12.3 times fewer**—and average runtime from 147.68 ms to 69.79 ms, about **53% lower**. Each suite also used fewer nodes with propagation. For example, the intermediate suite dropped from 20,370 to 1,455 nodes per game, while the expert sample dropped from 31,516 to 2,021.

The solver's `search nodes` metric counts each attempted safe-or-mine value during frontier search, including attempts that fail. Values filled by propagation are deductions and do not count as branch attempts. These counts aggregate the solver's searches for a consistent assignment and its tests of whether cells can take the opposite value. This definition is useful for comparing these two implementations, but may differ from the node definition in other Minesweeper benchmarks.

The unchanged win rate does not mean propagation did no useful work: the node counts and elapsed time show that it avoided many branches. Runtime is hardware- and load-dependent; search-node counts are the more stable measure. The expert result is based on only three boards, so it is illustrative rather than a strong statistical estimate. The intermediate result uses 25 boards.

## Task 4 — mine probabilities and risk heatmap

The calculation follows these steps:

1. Turn every visible number into a constraint on its hidden neighbours and
   subtract mines already marked `M` from the required count.
2. Group frontier cells into connected regions. Cells are in the same region
   when they are linked by one or more shared clue constraints. Different
   regions can be counted separately because no visible clue connects them.
3. For each region, recursively try safe and mine values for undecided cells.
   After every trial, apply basic propagation. If a clue cannot be satisfied,
   discard that branch immediately. When every cell has a value and all clues
   hold, count that assignment as one valid world.
4. For each cell, divide the number of valid worlds where it is a mine by the
   total number of valid worlds in its region. For example, if it is a mine
   in one of four equally valid arrangements, its mine probability is `0.25`.

The returned board keeps revealed clues as they are, replaces frontier `X`
cells with probabilities rounded to two decimal places, and leaves hidden cells
outside the frontier as `X`. The visible clues provide no information to
calculate a risk for those unconstrained cells.

When neither basic nor advanced reasoning proves a safe move, all solvers use
these probabilities to select the frontier cell with the lowest mine risk. If
several cells have equal risk, the solver prefers the one with more hidden
neighbours, then uses row/column order for a repeatable choice.

The presentation helper writes a standalone SVG heatmap using only Python's
standard library. Green represents lower mine risk, yellow represents
intermediate risk, and red represents higher risk; hidden cells outside the
frontier are gray. The two editable examples are
`examples/show_task_4.py` (the Task 3 board after its opening click) and
`examples/show_task_4_small.py` (the small partially revealed board). Their
SVGs are saved under `task4_heatmap/output/` and opened in a browser by the show
scripts.

## Task 6 comparison — advanced propagation

Task 6 adds pairwise subset-difference propagation to the solver. It compares
two clue constraints when the hidden cells of one are a subset of the other.
Subtracting the smaller constraint from the larger one can prove that the cells
left over are safe or mines, without guessing or running backtracking.

### Why this advanced technique was chosen

Each revealed number can be written as a small equation. For example,
`{A, B} = 1` means exactly one of hidden cells A and B is a mine. If another
clue gives `{A, B, C} = 1`, subtracting the first equation from the second
leaves `{C} = 0`; C is therefore safe. If the larger clue instead required two
mines, subtraction would give `{C} = 1`, proving C is a mine.

This subset rule was chosen because it extends the basic all-safe/all-mine
rules using only relationships already present in the visible clues. It is
deterministic and sound: it only assigns a cell when the equations require that
value in every valid board. It also fits naturally into the existing
constraint-propagation loop, which can repeat basic and subset deductions
until no new value follows. Unlike a larger search, it can prove some cells
without trying mine/safe branches. The rule has a limit: it only gains new
information when one unresolved clue-cell set is contained in another (or the
sets overlap in a way covered by the implemented difference rule). It can
leave valid positions unresolved, in which case the solver continues to
backtracking and Task 4's risk-based guessing.

Board source: `benchmark_boards.txt` (400 validated answer boards). This run
uses the selected 16 boards listed below. All three solvers play the same
boards using the same deterministic policy: a corner opening and, when no safe
cell is proven, the least-risky frontier guess.

Timing measures solving only. Search nodes count tried safe/mine branch values,
including failed trials. Values fixed directly by propagation are deductions,
so they are not counted as search nodes. Guesses count clicks where clue
reasoning did not prove a safe cell; the opening click is excluded.

### beginner_9x9_10 (10 boards)

| Solver | Won | Lost (first move) | Win % excl. first move | Moves/game | Moves/won game | Guesses/game | Search nodes/game | ms/game (max) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure backtracking | 7 | 3 (1) | 77.8% | 17.90 | 24.29 | 1.00 | 1,471 | 36.64 (100) |
| Backtracking + propagation | 7 | 3 (1) | 77.8% | 17.90 | 24.29 | 1.00 | 99 | 19.37 (33) |
| Advanced solver | 7 | 3 (1) | 77.8% | 17.90 | 24.29 | 1.00 | 82 | 246.91 (563) |

### dense_9x9_15 (5 boards)

| Solver | Won | Lost (first move) | Win % excl. first move | Moves/game | Moves/won game | Guesses/game | Search nodes/game | ms/game (max) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure backtracking | 1 | 4 (3) | 50.0% | 9.40 | 32.00 | 1.60 | 1,330 | 29.02 (128) |
| Backtracking + propagation | 1 | 4 (3) | 50.0% | 9.40 | 32.00 | 1.60 | 197 | 17.88 (71) |
| Advanced solver | 1 | 4 (3) | 50.0% | 9.40 | 32.00 | 1.60 | 185 | 157.51 (705) |

### intermediate_16x16_40 (1 board)

| Solver | Won | Lost (first move) | Win % excl. first move | Moves/game | Moves/won game | Guesses/game | Search nodes/game | ms/game (max) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure backtracking | 0 | 1 (0) | 0.0% | 2.00 | 0.00 | 1.00 | 15 | 2.19 (2) |
| Backtracking + propagation | 0 | 1 (0) | 0.0% | 2.00 | 0.00 | 1.00 | 7 | 0.97 (1) |
| Advanced solver | 0 | 1 (0) | 0.0% | 2.00 | 0.00 | 1.00 | 7 | 2.54 (3) |

### Overall (16 boards)

| Solver | Won | Lost (first move) | Win % excl. first move | Moves/game | Moves/won game | Guesses/game | Search nodes/game | ms/game (max) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure backtracking | 8 | 8 (4) | 66.7% | 14.25 | 25.25 | 1.19 | 1,336 | 32.11 (128) |
| Backtracking + propagation | 8 | 8 (4) | 66.7% | 14.25 | 25.25 | 1.19 | 124 | 17.75 (71) |
| Advanced solver | 8 | 8 (4) | 66.7% | 14.25 | 25.25 | 1.19 | 110 | 203.70 (705) |

### What the Task 6 results show

The advanced solver reaches exactly the same game outcomes, moves, and guesses
as the other solvers. This is expected because all solvers use the same answer
boards and the same click policy; advanced propagation changes how the solver
proves a decision, rather than changing the decision itself.

Its main improvement is in the amount of search. Across the 16 selected boards,
basic propagation needs 124 search nodes per game on average, while the subset
rule reduces this to 110: about **11% fewer** branch attempts. Compared with
pure backtracking, the advanced solver uses about **92% fewer** nodes (110
instead of 1,336). The improvement is present on both 9×9 suites: 99 to 82
nodes for beginner boards and 197 to 185 for dense boards. On the single
intermediate board, both propagation variants need seven nodes.

The lower node count does not make the advanced solver faster in this Python
implementation. It averages 203.70 ms per game, compared with 17.75 ms for
basic propagation. The subset-difference rule repeatedly compares pairs of
constraints and their cell sets. For this small benchmark, that extra work
costs more time than the avoided search branches save. The maximum times also
show that some boards trigger much more subset checking than others.

Therefore, search nodes are the useful measure of Task 6's logical power:
the advanced rule proves more values before branching. Runtime is an
implementation-dependent cost that could be reduced later by avoiding repeated
constraint-pair comparisons or caching derived constraints. The 16-board sample
is deliberately small, especially its one intermediate board, so its timing
results are illustrative rather than a stable performance claim.

## Task 5 — difficulty classification

The classifier looks only at the visible game state. It turns each revealed
number into a constraint over its still-hidden neighbours, subtracting any
mines already marked by the player. It does not consult an answer key, so every
reported deduction must follow from the clues.

It tries the available methods in increasing order of power:

1. **Basic propagation:** repeatedly apply Task 2's two rules. If a clue still
   needs zero mines, its remaining hidden neighbours are safe. If it needs a
   mine in every remaining hidden neighbour, they are all mines. Deductions
   from one clue can simplify another, so the pass repeats until it reaches a
   point where no more values are forced.
2. **Advanced propagation:** start again from the visible clues, apply the
   basic rules, and also compare pairs of constraints using Task 6's
   subset-difference rule. Repeat until this stronger set of rules reaches a
   point where it cannot prove another value.
3. **Backtracking:** if propagation cannot prove a cell, find one assignment
   that satisfies all frontier clues. Then, for each assigned cell, search
   again with its value reversed. If no valid assignment exists with the
   reversed value, that cell must have the value in the first assignment. If
   both values produce valid boards, the clues do not determine that cell.

The classifier reports the first method that proves at least one hidden
frontier cell safe or mined. This tells which simplest technique can make a
certain move from the current position; it does not claim that technique has
classified every hidden cell on the board. When even backtracking finds no
certain frontier cell, the result says a guess is required and lists the
ambiguous frontier coordinates. It also lists hidden cells outside every clue's
frontier separately, because the visible numbers place no constraint on those
cells. Coordinates in that explanation are zero-indexed `(row, column)` pairs.
