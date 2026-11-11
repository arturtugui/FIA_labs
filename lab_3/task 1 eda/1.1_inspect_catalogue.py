"""Load and inspect the Lab 3 mushroom catalogue.

The source CSV is kept unchanged in ``lab_condition/data.csv``. This first-step
script displays its semicolon-separated fields as a table and checks that each
record has the same number of fields as the header.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"


def load_catalogue(path: Path) -> pd.DataFrame:
    """Read the semicolon-delimited catalogue, preserving blank cells.

    Args:
        path: Path to the original CSV file.

    Returns:
        The catalogue as a DataFrame, with blank cells preserved as empty strings.
    """
    return pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")


def print_preview(data: pd.DataFrame, limit: int = 5) -> None:
    """Print dataset dimensions and a readable, selected-column preview."""
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")
    print("Headers:")
    print(" | ".join(data.columns))

    selected = ["family", "name", "class", "cap-diameter", "cap-shape", "season"]
    selected = [column for column in selected if column in data.columns]

    if data.empty or not selected:
        print("No records available for preview.")
        return

    print(f"\nFirst {min(limit, len(data))} records (selected columns):")
    print(data.loc[:, selected].head(limit).to_string(index=False))

    print("\nFirst record, all fields (blank values are shown as <blank>):")
    for column, value in data.iloc[0].items():
        print(f"{column}: {value if value else '<blank>'}")


def main() -> None:
    """Parse command-line options and inspect the requested CSV file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"CSV file to inspect (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=LAB3_DIR / "processed_data" / "1_1_readable_catalogue.csv",
        help="Where to save a comma-delimited, spreadsheet-friendly copy.",
    )
    args = parser.parse_args()

    data = load_catalogue(args.csv_path)
    print_preview(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"\nSpreadsheet-friendly CSV saved to: {args.output}")
    delimiter_counts = [line.count(";") for line in args.csv_path.read_text(encoding="utf-8-sig").splitlines()]
    unexpected = [line_number for line_number, count in enumerate(delimiter_counts, start=1) if count != len(data.columns) - 1]
    print(f"\nCSV lines with an unexpected semicolon count: {len(unexpected)}")
    if unexpected:
        print(f"Line numbers: {unexpected}")


if __name__ == "__main__":
    main()
