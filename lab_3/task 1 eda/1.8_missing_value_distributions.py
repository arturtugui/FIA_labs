"""Summarize blank counts and observed token frequencies for sparse columns."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_CSV_PATH = LAB3_DIR / "processed_data" / "1.8_missing_value_distributions.csv"
DEFAULT_REPORT_PATH = Path(__file__).parent / "plots" / "1.8_missing_value_distributions.md"
EXCLUDED_COLUMNS = {"family", "name", "class"}


def markdown_table(frame: pd.DataFrame) -> str:
    """Format a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def summarize(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Count blank cells and frequencies of complete recorded cell values."""
    total_rows = len(data)
    summary_rows = []
    value_rows = []
    for column in data.columns:
        if column in EXCLUDED_COLUMNS:
            continue
        cells = data[column].astype(str).str.strip()
        blank_count = int(cells.eq("").sum())
        if blank_count == 0:
            continue
        observed_cells = cells[cells.ne("")]
        value_counts = observed_cells.value_counts().sort_index()
        highest = int(value_counts.max())
        modes = [value for value, count in value_counts.items() if count == highest]
        summary_rows.append(
            {
                "Column": column,
                "Blank rows": blank_count,
                "Blank (%)": round(blank_count / total_rows * 100, 1),
                "Nonblank rows": total_rows - blank_count,
                "Most frequent complete cell value(s)": "; ".join(modes),
                "Frequency of each mode": highest,
            }
        )
        for value, count in value_counts.items():
            value_rows.append(
                {
                    "Column": column,
                    "Blank rows": blank_count,
                    "Complete cell value as recorded": value,
                    "Rows with this complete value": int(count),
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(value_rows)


def main() -> None:
    """Write the sparse-column frequency table as CSV and Markdown."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    summary, value_details = summarize(data)
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    value_details.to_csv(args.csv_output, index=False, encoding="utf-8-sig")

    notes = (
        "# Missing-column value frequencies\n\n"
        f"The table covers the {len(summary)} feature columns that contain at least one blank, "
        f"out of {len(data)} rows. Each complete cell is counted as recorded: for example, `[g, h]` "
        "stays one value and is not split into separate token counts. The summary shows each column's "
        "mode, including ties; the detailed table lists every complete value and its count. "
        "Blank cells are not imputed or counted as a value. "
        "The three numeric range columns have no blanks, so no range needs a median-based fill here.\n\n"
        + "## Blank counts and most frequent complete values\n\n"
        + markdown_table(summary)
        + "\n\n## Counts for every complete cell value\n\n"
        + markdown_table(value_details)
        + "\n"
    )
    args.report_output.write_text(notes, encoding="utf-8")
    print(f"Rows: {len(data)} | Feature columns with blanks: {len(summary)}")
    print(summary.to_string(index=False))
    print(f"Saved CSV table: {args.csv_output}")
    print(f"Saved Markdown table: {args.report_output}")


if __name__ == "__main__":
    main()
