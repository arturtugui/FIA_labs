"""Grow a multi-way decision tree by choosing, at every node, the question with the least average disorder.

Method (as taught in class):
1. Disorder of a set of mushrooms: D = -sum(p_i * log2(p_i)), where p_i is the share
   of family i in the set. D = 0 for a homogeneous set (one family only).
2. For every possible question, split the mushrooms by their answer and compute the
   average disorder: sum over branches of (branch size / set size) * D(branch).
3. Ask the question with the least average disorder, then repeat steps 2-3 inside
   each branch using only the mushrooms that reached that branch.
4. Stop when a branch is homogeneous (or when no question can split it any further).

Question types:
- Categorical column: one branch per complete cell value present at the node, so
  mushrooms listing `[x]`, `[f]` and `[f, x]` go to three different branches.
- Numeric midpoint: a yes/no question "midpoint <= t?", where t is chosen so the
  mushrooms at that node are split as evenly as possible into two groups. Because t
  depends on the mushrooms at the node, the same column can be asked again deeper down.

Input: the Task 2.2 prepared files (no blanks; numeric midpoints capped).
"""

from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd


# File locations: this script lives in "task 2 classification/decision tree/",
# so the lab_3 folder is two levels up.
TREE_DIR = Path(__file__).parent
LAB3_DIR = TREE_DIR.parent.parent
DEFAULT_TRAIN_PATH = LAB3_DIR / "processed_data" / "2.2_train_prepared.csv"
DEFAULT_TEST_PATH = LAB3_DIR / "processed_data" / "2.2_test_prepared.csv"

# Columns that are never used as questions:
# - family: the label we are trying to predict (using it would be cheating);
# - name:   a unique identifier, it would only let the tree memorise mushrooms;
# - class:  edibility, kept as a separate analysis label, not a family feature.
NON_FEATURE_COLUMNS = ["family", "name", "class"]


# ---------------------------------------------------------------------------
# Tree structure
# ---------------------------------------------------------------------------

@dataclass
class Node:
    """A question node (feature set) or a leaf (feature is None), with its training families."""

    # Family predicted if a mushroom stops at this node (majority family of its training rows).
    prediction: str
    # How many training mushrooms of each family reached this node, e.g. {"Russula Family": 3}.
    class_counts: dict[str, int]
    # Disorder of the training mushrooms at this node (0 means all of one family).
    disorder: float
    # The question asked here. None means this node is a leaf (no question is asked).
    feature: str | None = None
    # True for a numeric "midpoint <= threshold?" question, False for a categorical one.
    is_numeric: bool = False
    # Cut value for a numeric question; unused for categorical questions.
    threshold: float | None = None
    # Average disorder of the branches created by the chosen question (shown in the report).
    average_disorder: float | None = None
    # One child per answer.
    # Categorical: complete cell value -> child. Numeric: "Yes" (<= t) / "No" (> t) -> child.
    children: dict[str, "Node"] = field(default_factory=dict)

    @property
    def size(self) -> int:
        """Number of training mushrooms that reached this node."""
        return sum(self.class_counts.values())


# ---------------------------------------------------------------------------
# Disorder and question scoring
# ---------------------------------------------------------------------------

def disorder(labels: list[str]) -> float:
    """Return D = -sum(p * log2 p) over the families in `labels` (0 for a homogeneous set).

    Example: 4 mushrooms, 2 Russula + 2 Bolete -> p = 0.5 and 0.5
    -> D = -(0.5*log2 0.5 + 0.5*log2 0.5) = 1.0 (maximally mixed for two families).
    4 mushrooms, all Russula -> p = 1 -> D = -(1*log2 1) = 0 (homogeneous).
    """
    total = len(labels)
    if total == 0:
        return 0.0
    # Counter gives the number of mushrooms per family; count / total is that family's share p.
    value = -sum((count / total) * math.log2(count / total) for count in Counter(labels).values())
    # A homogeneous set gives -(1 * log2 1) = -0.0 in floating point; report it as plain 0.0.
    return value if value > 0 else 0.0


def majority(labels: list[str]) -> str:
    """Most frequent family; ties are broken alphabetically for reproducibility."""
    counts = Counter(labels)
    # Sort by count descending (-count), then by name, and take the first one.
    return sorted(counts, key=lambda label: (-counts[label], label))[0]


def balanced_threshold(values: np.ndarray) -> float | None:
    """Pick the cut between two distinct sorted values that splits the rows most evenly.

    Example: values [2, 4, 4, 6, 9] -> possible cuts 3, 5, 7.5.
    Cut 3 gives 1 vs 4 rows, cut 5 gives 3 vs 2 rows, cut 7.5 gives 4 vs 1 rows,
    so 5 is chosen (difference of 1 row). With repeated values a perfect 50/50 split
    is not always possible, which is why we look for the smallest difference.
    """
    unique = np.unique(values)  # sorted distinct values
    if len(unique) < 2:
        return None  # all mushrooms have the same value: this column cannot split them
    best_threshold, best_gap = None, None
    # Only cuts halfway between two neighbouring distinct values make sense:
    # any other cut in the same gap would send exactly the same mushrooms left/right.
    for low, high in zip(unique[:-1], unique[1:]):
        threshold = (low + high) / 2.0
        left = int(np.sum(values <= threshold))       # mushrooms answering "Yes"
        gap = abs(left - (len(values) - left))        # |Yes group - No group|
        if best_gap is None or gap < best_gap:  # first (lowest) threshold wins ties
            best_threshold, best_gap = float(threshold), gap
    return best_threshold


def candidate_questions(
    data: pd.DataFrame, labels: list[str], features: list[str], numeric: set[str]
) -> list[dict]:
    """Return every question that splits the rows into 2+ branches, with its average disorder.

    `data` and `labels` contain only the mushrooms that reached the current node,
    so the same function is used at the root and inside every branch.
    """
    candidates = []
    total = len(labels)
    label_array = np.array(labels)
    for feature in features:
        # Build the branches of this question as boolean masks: groups[answer][i] is True
        # when mushroom i gives that answer.
        if feature in numeric:
            # Numeric column: one yes/no question, cut so the two groups are as equal as possible.
            values = data[feature].to_numpy(dtype=float)
            threshold = balanced_threshold(values)
            if threshold is None:
                continue
            groups = {"Yes": values <= threshold, "No": values > threshold}
        else:
            # Categorical column: one branch per complete cell value seen at this node,
            # so "[x]", "[f]" and "[f, x]" are three separate answers.
            values = data[feature].to_numpy()
            branch_values = sorted(set(values))
            if len(branch_values) < 2:
                # Every mushroom here gives the same answer (e.g. the column was already
                # asked higher up): the question would not separate anything.
                continue
            threshold = None
            groups = {value: values == value for value in branch_values}
        # Average disorder = sum over branches of (branch size / node size) * D(branch).
        # mask.sum() is the branch size; label_array[mask] are the families in that branch.
        average = sum(
            mask.sum() / total * disorder(label_array[mask].tolist()) for mask in groups.values()
        )
        candidates.append(
            {"feature": feature, "is_numeric": feature in numeric, "threshold": threshold,
             "average_disorder": float(average), "groups": groups}
        )
    return candidates


# ---------------------------------------------------------------------------
# Building the tree and using it
# ---------------------------------------------------------------------------

def grow(data: pd.DataFrame, labels: list[str], features: list[str], numeric: set[str]) -> Node:
    """Recursively ask the least-disorder question until every branch is homogeneous."""
    # Every node remembers its training families, so it can still predict something
    # if a test mushroom has an answer that has no branch here (see predict()).
    node = Node(prediction=majority(labels), class_counts=dict(Counter(labels)), disorder=disorder(labels))

    # Stop 1: the set is homogeneous (one family) -> this node becomes a leaf.
    if node.disorder == 0.0:
        return node

    # Score every possible question using only the mushrooms at this node.
    candidates = candidate_questions(data, labels, features, numeric)

    # Stop 2: no question separates these mushrooms (identical features, different families).
    # This never happens on the current data (0 such groups), but the code must not loop forever.
    if not candidates:
        return node  # identical feature rows with different families: cannot be split

    # Choose the question with the least average disorder.
    # Ties keep the earlier column in the dataset order, so the tree is reproducible.
    best = min(candidates, key=lambda c: (c["average_disorder"], features.index(c["feature"])))
    node.feature = best["feature"]
    node.is_numeric = best["is_numeric"]
    node.threshold = best["threshold"]
    node.average_disorder = best["average_disorder"]

    # Repeat the whole procedure inside each branch, passing on only the mushrooms
    # that gave that answer. Every branch is strictly smaller than this node
    # (a question always creates at least 2 non-empty branches), so the recursion ends.
    label_array = np.array(labels)
    for answer, mask in best["groups"].items():
        node.children[answer] = grow(data[mask], label_array[mask].tolist(), features, numeric)
    return node


def predict(node: Node, row: pd.Series) -> tuple[str, bool]:
    """Follow the answers down the tree. Returns (family, used_fallback).

    If a test mushroom has a categorical value that no training mushroom had at that
    node, there is no branch to follow; the node's majority family is returned instead.
    """
    # Keep answering questions until a leaf (a node without a question) is reached.
    while node.feature is not None:
        if node.is_numeric:
            # Numeric question: compare with the cut chosen during training.
            answer = "Yes" if float(row[node.feature]) <= node.threshold else "No"
        else:
            # Categorical question: the answer is the mushroom's complete cell value.
            answer = row[node.feature]
        if answer not in node.children:
            # Unseen answer (e.g. a gill-color combination never seen in training at
            # this node): stop here and use the most common family of this node.
            return node.prediction, True
        node = node.children[answer]
    return node.prediction, False


# ---------------------------------------------------------------------------
# Printing the tree
# ---------------------------------------------------------------------------

def question_text(node: Node) -> str:
    """Readable form of the question asked at a node."""
    if node.is_numeric:
        return f"Is {node.feature} <= {node.threshold:g}?"
    return f"What is {node.feature}?"


def leaf_text(node: Node) -> str:
    """Readable form of a leaf: the predicted family and how many training rows reached it."""
    if node.disorder == 0.0:
        return f"→ {node.prediction} (n={node.size})"
    # Only reachable through "Stop 2" in grow(): show the families that could not be separated.
    mix = ", ".join(f"{label}: {count}" for label, count in sorted(node.class_counts.items()))
    return f"→ {node.prediction} (n={node.size}, NOT homogeneous: {mix})"


def tree_lines(node: Node, indent: str = "") -> list[str]:
    """Render the tree with one line per question, branch and leaf."""
    lines = [f"{indent}{question_text(node)}  [n={node.size}, D={node.disorder:.3f}, "
             f"average D after question={node.average_disorder:.3f}]"]
    answers = list(node.children)
    for position, answer in enumerate(answers):
        child = node.children[answer]
        last = position == len(answers) - 1
        # "├──" for middle branches, "└──" for the last one; the vertical bar "│"
        # continues only below branches that still have siblings after them.
        connector, extension = ("└── ", "    ") if last else ("├── ", "│   ")
        if child.feature is None:
            # Leaf: answer and predicted family on one line.
            lines.append(f"{indent}{connector}{answer} {leaf_text(child)}")
        else:
            # Another question: print the answer, then the subtree indented below it.
            lines.append(f"{indent}{connector}{answer}:")
            lines.extend(tree_lines(child, indent + extension))
    return lines


def tree_stats(node: Node, depth: int = 0) -> tuple[int, int, int]:
    """Return (question nodes, leaves, maximum depth)."""
    if node.feature is None:
        return 0, 1, depth
    questions, leaves, max_depth = 1, 0, depth
    for child in node.children.values():
        q, l, d = tree_stats(child, depth + 1)
        questions, leaves, max_depth = questions + q, leaves + l, max(max_depth, d)
    return questions, leaves, max_depth


# ---------------------------------------------------------------------------
# Evaluation and report helpers
# ---------------------------------------------------------------------------

def per_family_scores(actual: list[str], predicted: list[str]) -> tuple[pd.DataFrame, float, float]:
    """Accuracy, macro F1, and per-family precision/recall/F1 over families in truth or predictions."""
    actual_array, predicted_array = np.array(actual), np.array(predicted)
    rows = []
    for label in sorted(set(actual) | set(predicted)):
        # Treat this family as "positive" and every other family as "negative".
        tp = int(np.sum((actual_array == label) & (predicted_array == label)))  # correctly found
        fp = int(np.sum((actual_array != label) & (predicted_array == label)))  # wrongly given this label
        fn = int(np.sum((actual_array == label) & (predicted_array != label)))  # missed
        # Precision: of the mushrooms predicted as this family, how many really are.
        # Recall: of the mushrooms of this family, how many were found.
        # A family never predicted (or absent from the test set) gets 0 instead of dividing by 0.
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"Family": label, "Test support": int(np.sum(actual_array == label)),
                     "Precision": precision, "Recall": recall, "F1": f1})
    table = pd.DataFrame(rows)
    accuracy = float(np.mean(actual_array == predicted_array))
    # Macro F1 gives every family the same weight, so small families count as much as Tricholoma.
    macro_f1 = float(table["F1"].mean())  # average the unrounded F1 values
    return table.round(3), accuracy, macro_f1


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def main() -> None:
    """Grow the tree on the training rows, evaluate on the test rows, and write the outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--test", type=Path, default=DEFAULT_TEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=TREE_DIR)
    args = parser.parse_args()

    # Read everything as text and keep empty cells as "" (the prepared files have none left).
    read = dict(sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    train = pd.read_csv(args.train, **read)
    test = pd.read_csv(args.test, **read)

    # Every remaining column is a question the tree may ask; midpoint columns are numeric.
    features = [column for column in train.columns if column not in NON_FEATURE_COLUMNS]
    numeric = {column for column in features if column.endswith("-midpoint")}
    for frame in (train, test):
        for column in numeric:
            frame[column] = frame[column].astype(float)
    y_train = train["family"].tolist()
    y_test = test["family"].tolist()

    # Rows with identical features but different families can never be separated.
    # If this is 0, a fully grown tree is guaranteed to reach 100% training accuracy.
    conflicts = int((train.groupby(features)["family"].nunique() > 1).sum())

    # Build the tree from the training mushrooms only; the test mushrooms are not seen here.
    # reset_index gives positions 0..n-1 so the boolean masks line up with the rows.
    tree = grow(train.reset_index(drop=True), y_train, features, numeric)
    questions, leaves, depth = tree_stats(tree)

    # Worked example for the report: average disorder of every possible first question.
    # This repeats the root calculation from grow() so it can be shown as a table.
    root_candidates = candidate_questions(train.reset_index(drop=True), y_train, features, numeric)
    root_table = pd.DataFrame(
        [{"Question": (f"Is {c['feature']} <= {c['threshold']:g}?" if c["is_numeric"]
                       else f"What is {c['feature']}?"),
          "Branches": len(c["groups"]),
          "Average disorder": round(c["average_disorder"], 4)}
         for c in sorted(root_candidates, key=lambda c: c["average_disorder"])]
    )
    # Break the chosen root question down branch by branch: n_b, D(branch), and n_b/n * D(branch).
    # Summing the "Weighted disorder" column gives the root's average disorder.
    chosen = min(root_candidates, key=lambda c: (c["average_disorder"], features.index(c["feature"])))
    label_array = np.array(y_train)
    root_branch_rows = []
    for answer, mask in chosen["groups"].items():
        branch_labels = label_array[mask].tolist()
        root_branch_rows.append(
            {"Answer": answer, "Mushrooms": int(mask.sum()),
             "Families in branch": len(set(branch_labels)),
             "Branch disorder": round(disorder(branch_labels), 4),
             "Weight (n_b / n)": round(mask.sum() / len(y_train), 4),
             "Weighted disorder": round(mask.sum() / len(y_train) * disorder(branch_labels), 4)}
        )
    root_branch_table = pd.DataFrame(root_branch_rows).sort_values("Mushrooms", ascending=False)

    # Training accuracy: how well the tree fits the mushrooms it was built from.
    train_predictions = [predict(tree, row)[0] for _, row in train.iterrows()]
    # Test accuracy: how well it does on mushrooms it has never seen (the honest estimate).
    test_results = [predict(tree, row) for _, row in test.iterrows()]
    test_predictions = [family for family, _ in test_results]
    fallbacks = sum(used for _, used in test_results)  # test rows that hit an unseen answer
    train_accuracy = float(np.mean(np.array(train_predictions) == np.array(y_train)))
    family_table, test_accuracy, test_macro_f1 = per_family_scores(y_test, test_predictions)

    # Baseline: always predict the most common training family. A useful model must beat it.
    baseline_family = majority(y_train)
    baseline_accuracy = float(np.mean(np.array(y_test) == baseline_family))
    _, _, baseline_macro_f1 = per_family_scores(y_test, [baseline_family] * len(y_test))

    # --- Write outputs: full tree, per-mushroom predictions, and the Markdown summary ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tree_text = "\n".join(tree_lines(tree))
    (args.output_dir / "2.3_tree.txt").write_text(tree_text + "\n", encoding="utf-8")
    predictions = pd.DataFrame(
        {"name": test["name"], "actual_family": y_test, "predicted_family": test_predictions,
         "correct": np.array(y_test) == np.array(test_predictions),
         "used_majority_fallback": [used for _, used in test_results]}
    )
    predictions.to_csv(args.output_dir / "2.3_test_predictions.csv", index=False, encoding="utf-8-sig")

    summary = (
        "# Task 2.3 multi-way decision tree (least average disorder)\n\n"
        "## Method\n\n"
        "Disorder of a set: `D = -sum(p_i * log2 p_i)` over the families in the set (0 when homogeneous). "
        "For a question, the average disorder is `sum_b (n_b / n) * D(branch b)`. At every node the question "
        "with the least average disorder is asked; each branch is then treated the same way using only its "
        "own mushrooms, until every branch is homogeneous. A categorical question has one branch per complete "
        "cell value at that node (`[x]`, `[f]` and `[f, x]` are three branches). A numeric question is "
        "`midpoint <= t?`, with `t` splitting the node's mushrooms as evenly as possible into two groups.\n\n"
        f"Features ({len(features)}): " + ", ".join(f"`{f}`" for f in features) + ". "
        "`family` is the target; `name` and `class` are not used.\n\n"
        "## Tree size\n\n"
        f"{questions} question nodes, {leaves} leaves, maximum depth {depth}. Groups of identical training "
        f"feature rows with different families (impossible to separate): {conflicts}.\n\n"
        "## Root question: average disorder of every candidate\n\n"
        f"The {len(y_train)} training mushrooms have disorder D = {tree.disorder:.4f} "
        f"({len(set(y_train))} families).\n\n"
        + markdown_table(root_table)
        + f"\n\nChosen root question: **{question_text(tree)}** "
        f"(average disorder {tree.average_disorder:.4f}). Its branches:\n\n"
        + markdown_table(root_branch_table)
        + "\n\n## Results\n\n"
        f"Training accuracy: {train_accuracy:.3f} ({int(round(train_accuracy * len(y_train)))}/{len(y_train)}).\n\n"
        f"Test accuracy: {test_accuracy:.3f} ({int(round(test_accuracy * len(y_test)))}/{len(y_test)}); "
        f"macro F1 over families in the test set or predictions: {test_macro_f1:.3f}. "
        f"Majority baseline (always `{baseline_family}`): accuracy {baseline_accuracy:.3f}, "
        f"macro F1 {baseline_macro_f1:.3f}.\n\n"
        f"Test mushrooms that reached a node with an answer no training mushroom had there (predicted with "
        f"that node's majority family instead): {fallbacks} of {len(y_test)}.\n\n"
        + markdown_table(family_table)
        + "\n\nThe full tree is in `2.3_tree.txt`; per-mushroom test predictions are in "
        "`2.3_test_predictions.csv`.\n"
    )
    (args.output_dir / "2.3_tree_summary.md").write_text(summary, encoding="utf-8")

    # Short console summary so the main numbers are visible right after running.
    print(f"Features: {len(features)} | train/test rows: {len(train)}/{len(test)} | conflicts: {conflicts}")
    print(f"Tree: {questions} questions, {leaves} leaves, depth {depth}")
    print(f"Root: {question_text(tree)} | D {tree.disorder:.4f} -> average D {tree.average_disorder:.4f}")
    print(f"Train accuracy: {train_accuracy:.3f}")
    print(f"Test accuracy: {test_accuracy:.3f} | macro F1: {test_macro_f1:.3f} | fallbacks: {fallbacks}")
    print(f"Baseline ({baseline_family}): accuracy {baseline_accuracy:.3f} | macro F1 {baseline_macro_f1:.3f}")
    print(root_table.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
