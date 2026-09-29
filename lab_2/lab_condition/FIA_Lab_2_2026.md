FAF.FIA Autumn 2026

# Lab: Domains, Constraints

Handed out: Wednesday, September 17, 2026

## Domain Expansion... I mean Reduction!

It's harvest season in the quiet villages of Luna City, and the old farmer has been having a wonderful year: his tomatoes are the size of fists, his peppers could win awards, and even the neighbours' goats have stopped breaking through the fence (mostly).

But this morning, the farmer wakes up to a disaster.

A group of local kids, bored after a long summer and armed with an alarming amount of creativity, have spent the night planting homemade "stink capsules" all over his vegetable garden. These little contraptions (sealed plastic bottles filled with a fermented mixture of vinegar, garlic, and something that might have once been a fish; very inventive, right?) are buried just beneath the surface. Step on one, and it pops open, releasing a smell so potent it could make a scarecrow resign. Worse, the rancid liquid soaks into the soil and poisons the roots of whatever grows nearby.

By the time the kids were done, even they had lost track of where everything was buried. They claimed putting them, well, not to be dramatic, but EVERYWHERE. Well, not everywhere everywhere. Maybe like... a lot of places? Helpful!

The farmer, though, is not amused. His peppers are at stake. His tomatoes are at stake. His dignity at the village harvest fair is very much at stake. He stands at the edge of his garden, divided into a neat rectangular grid of plots (Gheorghe is a very organised man), and surveys the damage. A few capsules have already been triggered. Result? The affected plots reek, but at least now he can count exactly how many capsules are buried in the neighbouring plots around each triggered one.

The village council, seeing an opportunity for educational punishment, decides to make the kids fix their own mess. But since the kids have the approximate spatial memory of a goldfish, they turn to you, the one kind hearted adult person nearby, who does something with computers and some type of intelligence.

Your mission: using logic, constraint analysis, and the nose-wrinkling clues from the already-triggered plots, figure out exactly which plots contain buried stink capsules before the old farmer loses his entire harvest (and his patience, which is already running dangerously low).

Each triggered plot tells you how many of its neighbours hide a capsule. The rest is logic. Probably.

## General Guidelines

- Your solution will be evaluated on Minesweeper boards of varying sizes and difficulties chosen by the evaluator. It must handle boards of at least 9 × 9.
- Your submission is a single Python file, based on the provided skeleton `minesweeper_solver.py` (see Submission Format). Automated tests will be run against it.
- The submission may import only the Python standard library. You may use plotting libraries for the heatmap of Task 4, but their import lines must be commented out in the submitted file. You will be asked to run the heatmap on your own machine during the presentation.
- During evaluation you will be given boards you have never seen, so do not hard-code anything.
- Do NOT host your solution in public repositories (e.g. GitHub). Private repositories are fine.
- Plagiarism is NOT tolerated!

## Input Format

Boards are given to you as plain-text strings. Cells are separated by a single space, rows by a newline. A board can be in different states:

**Answer key (ground truth).** Every cell is known. Used to generate games and to check whether a move was safe.

- `M` — a mine
- `1`–`8` — number of adjacent mines
- `.` — zero adjacent mines

```
1 M 1 1 M
M 2 1 1 1
2 2 . . .
M 2 . . .
M 2 . . .
```

**Game state (what the player sees).** Same encoding, plus one extra symbol:

- `X` — a hidden (unrevealed) cell

A fresh game is all `X`; a game in progress mixes `X` with revealed numbers and `.`. The evaluator may hand you a game state at any point of the game, e.g.:

```
X X X X X 1 X X X X
X X X X X X 2 1 1 X
X X X X X 2 2 . . .
X X X X X X 2 . . .
X X X X X X 2 . . .
```

Your program must parse both formats and produce output in the same notation. Mines that your solver has deduced should be printed as `M`; cells that remain undetermined stay `X`.

## Submission Format

You receive a skeleton file `minesweeper_solver.py` with one function per task, each marked `# REQUIRED` and raising `NotImplementedError`. Their names and signatures must not be altered: the tests call them by name, and a renamed or missing function scores zero for that task. You may add any number of helper functions, classes, or constants. Rename the file to `<surname>_<name>.py` before submitting.

Functions that play a game (`backtracking_solve`, `backtrack_constraint`, `advanced_solver`) receive the answer key and start from an all-`X` board. Functions that reason about a position (`backtracking_step`, `constraint_propagation`, `mine_probability`, `classify_difficulty`) receive a game state in any stage. Cells are addressed as `(row, col)`, zero-indexed from the top-left corner.

## Grading Policy

### Task 1 — Backtracking Solver

Model the board as a constraint satisfaction problem: every hidden cell is a variable with domain {mine, safe}, every revealed number is a constraint over its hidden neighbours. Implement a solver based on backtracking.

Two functions are required. `backtracking_step` receives a game state in an arbitrary stage, performs a single step of the algorithm, and returns the cell it checked together with the board after that check; the evaluator will call it repeatedly to inspect what your algorithm does one, two, three steps in. `backtracking_solve` receives an answer key, starts from an all-`X` board and runs until the board is solved or a mine is hit, returning every step taken and the board after each of them.

Functions: `backtracking_step`, `backtracking_solve`. (2p.)

### Task 2 — Constraint Propagation

Given a game state, derive the constraints implied by the revealed numbers and apply the basic propagation rules based on the states of neighbouring cells. Return the same board string with every cell you have deduced to be a mine marked `M` — these are the cells not to click — and nothing else changed. No search is allowed in this task, only propagation.

Function: `constraint_propagation`. (1p.)

### Task 3 — Backtracking + Constraint Propagation

Combine the two: whenever backtracking assigns a value to a cell, immediately propagate the consequences to the affected constraints and shrink the domains of the neighbouring cells.

`backtrack_constraint` has the same contract as `backtracking_solve`: it receives an answer key, plays from an all-`X` board until the game is solved or lost, and returns every step with the board after it.

Run both solvers on the same set of generated boards and compare them in the report on at least: number of moves needed to finish a game, games won / games lost, and running time. The combined solver is expected to be measurably better; explain the numbers.

Function: `backtrack_constraint`. (2p.)

### Task 4 — Mine Probabilities & Risk Heatmap

Minesweeper is famous for positions where logic alone cannot settle every cell, yet the player must still move. Given a game state, compute for every hidden cell on the constraint frontier the probability that it holds a mine. Return the same board string with those cells replaced by their probability, and render the result as a heatmap for the presentation. Your solvers must use these probabilities to choose the least risky cell when no certain move exists.

Function: `mine_probability`. (1.5p.)

### Task 5 — Difficulty Classification

Given a game state, determine the simplest technique from your toolbox (basic propagation, advanced propagation, backtracking, ...) that resolves the current position with 100% confidence, by trying techniques in increasing order of power and reporting the first one that succeeds.

If no technique can reach 100% confidence, the board is classified as requiring a guess; in that case your program must point out the cell(s) or region of the board that make a certain decision impossible.

Function: `classify_difficulty`. (0.5p.)

### Task 6 — Advanced Constraint Propagation

Research and implement at least one propagation technique that goes beyond the basic rules of Task 2, with the goal of maximising the number of cells determined by pure logic before any search or guessing is needed.

`advanced_solver` has the same contract as `backtrack_constraint`. Add it as a third entry in the comparison of Task 3, on the same boards and metrics, and justify your choice of technique(s) in the report.

Function: `advanced_solver`. (1p.)

### Report & Presentation

Clear explanations, report formatting, code quality, comments, docstrings, visualisations where relevant. (1p.)

Good Luck!
