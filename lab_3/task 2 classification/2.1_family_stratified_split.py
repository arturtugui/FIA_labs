"""Create a reproducible approximately 70/30 family-stratified split of the Step 1.11 cleaned data."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "processed_data" / "1.11_clean.csv"
DEFAULT_TRAIN_PATH = LAB3_DIR / "processed_data" / "2.1_train.csv"
DEFAULT_TEST_PATH = LAB3_DIR / "processed_data" / "2.1_test.csv"
DEFAULT_REPORT_PATH = Path(__file__).parent / "2.1_split_summary.md"
RANDOM_SEED = 42
TEST_FRACTION = 0.30


def make_split(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split each family while keeping singleton classes in train and all possible families in test."""
    rng = np.random.default_rng(RANDOM_SEED)
    train_indices: list[int] = []
    test_indices: list[int] = []
    summary_rows = []

    for family, group in data.groupby("family", sort=True):
        indices = group.index.to_numpy().copy()
        rng.shuffle(indices)
        count = len(indices)
        if count == 1:
            test_count = 0
        else:
            # Keep at least one member of this family in each set.
            test_count = max(1, int(np.floor(TEST_FRACTION * count + 0.5)))
            test_count = min(test_count, count - 1)
        family_test = indices[:test_count].tolist()
        family_train = indices[test_count:].tolist()
        test_indices.extend(family_test)
        train_indices.extend(family_train)
        summary_rows.append(
            {
                "Family": family,
                "Total rows": count,
                "Train rows": len(family_train),
                "Test rows": len(family_test),
                "Test share (%)": round(len(family_test) / count * 100, 1),
                "In both sets": "Yes" if family_train and family_test else "No",
            }
        )

    train = data.loc[sorted(train_indices)].copy()
    test = data.loc[sorted(test_indices)].copy()
    summary = pd.DataFrame(summary_rows)
    return train, test, summary


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Create the split files and summarize per-family coverage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--train-output", type=Path, default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--test-output", type=Path, default=DEFAULT_TEST_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    train, test, family_summary = make_split(data)
    if set(train.index).intersection(test.index):
        raise RuntimeError("Train and test indices overlap.")
    if len(train) + len(test) != len(data):
        raise RuntimeError("Train and test do not cover every source row exactly once.")

    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.test_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(args.train_output, sep=";", index=False, encoding="utf-8-sig")
    test.to_csv(args.test_output, sep=";", index=False, encoding="utf-8-sig")

    report = (
        "# Task 2 train/test split\n\n"
        f"The source has {len(data)} rows and {data['family'].nunique()} families. A fixed random seed of "
        f"{RANDOM_SEED} was used to shuffle within each family. For every family with at least two rows, "
        "at least one row is placed in each split and the test count is rounded toward 30%. Singleton-family "
        "rows are placed in train so the models can observe those labels; they cannot also appear in test.\n\n"
        f"Train: {len(train)} rows ({len(train) / len(data) * 100:.1f}%). Test: {len(test)} rows "
        f"({len(test) / len(data) * 100:.1f}%). Train contains {train['family'].nunique()} families; test "
        f"contains {test['family'].nunique()} families. The input is the Step 1.11 cleaned file (sorted token "
        "sets, lowercase column names, range midpoints, columns more than 80% blank dropped). Blanks are still "
        "blank: mode imputation and outlier capping are fitted on the training rows afterwards, in Task 2.2.\n\n"
        "## Per-family counts\n\n"
        + markdown_table(family_summary)
        + "\n\nThe test score cannot measure generalization for the singleton families, because their only rows "
        "must stay in train for the model to have examples of those labels. This split is one fixed holdout; "
        "results measured on it can vary with the seed.\n"
    )
    args.report_output.write_text(report, encoding="utf-8")
    print(f"Train rows: {len(train)} ({len(train) / len(data) * 100:.1f}%)")
    print(f"Test rows: {len(test)} ({len(test) / len(data) * 100:.1f}%)")
    print(f"Families in train/test: {train['family'].nunique()}/{test['family'].nunique()}")
    print(f"Wrote: {args.train_output}")
    print(f"Wrote: {args.test_output}")
    print(f"Wrote: {args.report_output}")


if __name__ == "__main__":
    main()
