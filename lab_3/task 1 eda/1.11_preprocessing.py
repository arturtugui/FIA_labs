"""Apply the fixed-rule preprocessing steps that do not learn anything from the data.

Steps (applied to all 173 rows, before any train/test split):
1. Standardise column names to lowercase (`Cap-surface` -> `cap-surface`).
2. Canonicalise every categorical cell as a set: trim spaces, remove repeated
   tokens and sort them, so `[x, f]`, `[f, x]` and `[f ,x]` all become `[f, x]`.
3. Replace each numeric range `[min, max]` by its midpoint; a single value is a
   zero-width range, so its midpoint is that value.
4. Drop the feature columns that are more than 80% blank.

Blanks are kept as empty strings here. Mode imputation and outlier capping learn
values from the data, so they are fitted later on the training rows only (Task 2.2).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_OUTPUT_PATH = LAB3_DIR / "processed_data" / "1.11_clean.csv"
DEFAULT_REPORT_PATH = Path(__file__).parent / "plots" / "1.11_preprocessing.md"
NON_FEATURE_COLUMNS = ["family", "name", "class"]
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]
DROP_THRESHOLD_PERCENT = 80.0


def canonical_cell(cell: str) -> str:
    """Return a categorical cell as a sorted, de-duplicated token set; blank stays blank."""
    value = cell.strip()
    if not value:
        return ""
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected categorical cell format: {cell!r}")
    tokens = sorted({token.strip() for token in value[1:-1].split(",") if token.strip()})
    return "[" + ", ".join(tokens) + "]"


def range_midpoint(cell: str) -> float:
    """Read `[min, max]` (or a single `[value]`) and return the midpoint."""
    value = cell.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected numeric range format: {cell!r}")
    numbers = [float(part.strip()) for part in value[1:-1].split(",") if part.strip()]
    if len(numbers) == 1:
        return numbers[0]
    if len(numbers) == 2:
        return (numbers[0] + numbers[1]) / 2.0
    raise ValueError(f"Expected one or two numbers in range: {cell!r}")


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Clean the raw catalogue with fixed rules and write the cleaned file plus a log."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    raw = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")

    # Step 1: one naming convention for every column.
    renamed = {column: column.strip().lower() for column in raw.columns}
    renamed_changes = [(old, new) for old, new in renamed.items() if old != new]
    data = raw.rename(columns=renamed)
    data = data.apply(lambda column: column.str.strip())
    feature_columns = [column for column in data.columns if column not in NON_FEATURE_COLUMNS]
    categorical_columns = [column for column in feature_columns if column not in NUMERIC_COLUMNS]

    # Step 2: the same set written in a different order/spacing becomes one value.
    canonical_rows = []
    for column in categorical_columns:
        before = data[column]
        after = before.map(canonical_cell)
        changed = before.ne(after)
        canonical_rows.append(
            {
                "Column": column,
                "Distinct values before": before[before.ne("")].nunique(),
                "Distinct values after": after[after.ne("")].nunique(),
                "Cells rewritten": int(changed.sum()),
            }
        )
        data[column] = after
    canonical_summary = pd.DataFrame(canonical_rows)
    canonical_summary = canonical_summary[canonical_summary["Cells rewritten"] > 0]

    # Step 3: each range is represented by its midpoint (no numeric blanks exist; Step 1.5).
    numeric_rows = []
    for column in NUMERIC_COLUMNS:
        if data[column].eq("").any():
            raise ValueError(f"Unexpected blank numeric cell in {column}")
        midpoint_column = f"{column}-midpoint"
        data[midpoint_column] = data[column].map(range_midpoint)
        numeric_rows.append(
            {
                "Source column": column,
                "New column": midpoint_column,
                "Min": data[midpoint_column].min(),
                "Median": data[midpoint_column].median(),
                "Max": data[midpoint_column].max(),
            }
        )
    data = data.drop(columns=NUMERIC_COLUMNS)

    # Step 4: drop feature columns that are more than 80% blank.
    blank_percent = {column: data[column].eq("").mean() * 100 for column in categorical_columns}
    dropped = sorted(
        (column for column, percent in blank_percent.items() if percent > DROP_THRESHOLD_PERCENT),
        key=lambda column: -blank_percent[column],
    )
    data = data.drop(columns=dropped)
    kept_with_blanks = [
        column for column in categorical_columns
        if column not in dropped and blank_percent[column] > 0
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")

    drop_table = pd.DataFrame(
        {"Column": dropped, "Blank (%)": [f"{blank_percent[column]:.1f}" for column in dropped]}
    )
    remaining_table = pd.DataFrame(
        {
            "Column": kept_with_blanks,
            "Blank (%)": [f"{blank_percent[column]:.1f}" for column in kept_with_blanks],
            "Blank cells": [int(data[column].eq("").sum()) for column in kept_with_blanks],
        }
    )
    report = (
        "# Step 1.11 fixed-rule preprocessing\n\n"
        f"Input: {len(raw)} rows x {raw.shape[1]} columns. Output: {len(data)} rows x {data.shape[1]} columns.\n\n"
        "## Column names\n\n"
        + "\n".join(f"- `{old}` -> `{new}`" for old, new in renamed_changes)
        + "\n\n## Categorical cells rewritten as sorted sets\n\n"
        + markdown_table(canonical_summary)
        + "\n\n## Numeric ranges replaced by midpoints\n\n"
        + markdown_table(pd.DataFrame(numeric_rows))
        + f"\n\n## Columns dropped (more than {DROP_THRESHOLD_PERCENT:.0f}% blank)\n\n"
        + markdown_table(drop_table)
        + "\n\n## Kept columns that still contain blanks (filled in Task 2.2)\n\n"
        + markdown_table(remaining_table)
        + "\n"
    )
    args.report_output.write_text(report, encoding="utf-8")

    print(f"Rows x columns: {raw.shape} -> {data.shape}")
    print(f"Renamed: {renamed_changes}")
    print(f"Cells rewritten as sorted sets: {int(canonical_summary['Cells rewritten'].sum())}")
    print(f"Dropped: {dropped}")
    print(f"Kept columns with blanks: {kept_with_blanks}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.report_output}")


if __name__ == "__main__":
    main()
