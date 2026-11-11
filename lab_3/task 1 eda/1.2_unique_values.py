"""Summarise distinct raw cell values for every column in the Lab 3 catalogue.

Blank cells are counted separately. Bracketed cells are treated as complete
raw entries here; their tokens will be parsed in a later preprocessing step.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"


def main() -> None:
    """Load the source CSV and print unique-value information per column."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"CSV file to inspect (default: {DEFAULT_DATA_PATH})",
    )
    args = parser.parse_args()

    data = pd.read_csv(
        args.csv_path,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    print(f"Dataset: {args.csv_path}")
    print(f"Rows: {len(data)} | Columns: {len(data.columns)}")
    print("Unique values are counted as exact cell contents; blanks are reported separately.")

    feature_columns = [
        column for column in data.columns if column not in {"family", "name", "class"}
    ]
    duplicate_rows = int(data.duplicated().sum())
    duplicate_names = int(data["name"].duplicated().sum()) if "name" in data else 0
    duplicate_profiles = int(data.duplicated(subset=feature_columns).sum())
    print("\nDuplicate checks")
    print(f"Exact duplicate rows: {duplicate_rows}")
    print(f"Repeated names (identifier): {duplicate_names}")
    print(f"Repeated mushroom feature profiles: {duplicate_profiles}")

    for column in data.columns:
        values = data[column]
        nonblank = values[values != ""]
        unique_values = list(pd.unique(nonblank))
        unique_count = len(unique_values)
        entry_count = len(nonblank)
        blank_count = len(values) - entry_count

        print(f"\n{column}")
        print(f"  Distinct nonblank values: {unique_count}")
        print(f"  Nonblank entries: {entry_count} | Blank entries: {blank_count}")

        if entry_count > 0 and unique_count == entry_count:
            print("  Every nonblank entry is unique.")
        elif unique_count < 10:
            print("  Values:")
            for value in unique_values:
                print(f"    - {value}")
        else:
            print(f"  More than 9 distinct values; listing omitted (count: {unique_count}).")

    # Use all CSV columns for this row-level summary. The intervals are
    # lower-inclusive and upper-exclusive, except the final interval includes 100%.
    bands = ["0-<20%", "20-<40%", "40-<60%", "60-<80%", "80-100%"]
    rows_by_band: dict[str, list[int]] = {band: [] for band in bands}
    zero_empty_rows: list[int] = []
    total_columns = len(data.columns)

    print("\nEmpty columns by row")
    print(f"Percentage denominator: all {total_columns} CSV columns.")
    print("Row | Name | Empty columns | Empty % | Band")
    for row_number, (_, row) in enumerate(data.iterrows(), start=1):
        empty_count = int((row == "").sum())
        empty_percent = empty_count / total_columns * 100 if total_columns else 0.0
        band_index = min(int(empty_percent // 20), len(bands) - 1)
        band = bands[band_index]
        rows_by_band[band].append(row_number)
        if empty_count == 0:
            zero_empty_rows.append(row_number)
        name = row.get("name", "") or "<blank>"
        print(f"{row_number:>3} | {name} | {empty_count:>13} | {empty_percent:>6.1f}% | {band}")

    print("\nRows grouped by empty-column percentage")
    print(f"Exactly 0% empty: {len(zero_empty_rows)} rows")
    for band, row_numbers in rows_by_band.items():
        print(f"{band}: {len(row_numbers)} rows")


if __name__ == "__main__":
    main()
