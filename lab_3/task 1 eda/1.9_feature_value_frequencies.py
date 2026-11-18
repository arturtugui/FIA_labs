"""Calculate observed value frequencies for each prediction feature."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_NUMERIC_PATH = LAB3_DIR / "processed_data" / "1.5_numeric_range_features.csv"
DEFAULT_CSV_PATH = LAB3_DIR / "processed_data" / "1.9_feature_value_frequencies.csv"
DEFAULT_REPORT_PATH = Path(__file__).parent / "plots" / "1.9_feature_value_frequencies.md"
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]
EXCLUDED_COLUMNS = {"family", "name", "class"}


def parse_tokens(cell: str) -> list[str]:
    """Parse one categorical cell as its separate observed tokens."""
    value = cell.strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected categorical cell format: {cell!r}")
    return list(dict.fromkeys(token.strip() for token in value[1:-1].split(",") if token.strip()))


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def calculate_frequencies(data: pd.DataFrame, numeric: pd.DataFrame) -> pd.DataFrame:
    """Calculate token prevalence or exact derived numeric-value frequency."""
    rows = []
    for feature in data.columns:
        if feature in EXCLUDED_COLUMNS or feature in NUMERIC_COLUMNS:
            continue
        cells = data[feature].astype(str).str.strip()
        observed = cells.ne("")
        denominator = int(observed.sum())
        token_counts: dict[str, int] = {}
        for cell in cells[observed]:
            for token in parse_tokens(cell):
                token_counts[token] = token_counts.get(token, 0) + 1
        for token, count in token_counts.items():
            rows.append(
                {
                    "Feature": feature,
                    "Value": token,
                    "Count": count,
                    "Denominator (nonblank rows)": denominator,
                    "Frequency (%)": count / denominator * 100,
                }
            )

    for feature in NUMERIC_COLUMNS:
        for statistic in ("midpoint", "width"):
            column = f"{feature}__{statistic}"
            values = numeric[column]
            counts = values.value_counts().sort_index()
            denominator = int(values.notna().sum())
            for value, count in counts.items():
                rows.append(
                    {
                        "Feature": column,
                        "Value": f"{value:g}",
                        "Count": int(count),
                        "Denominator (nonblank rows)": denominator,
                        "Frequency (%)": float(count / denominator * 100),
                    }
                )

    result = pd.DataFrame(rows)
    result["Frequency (%)"] = result["Frequency (%)"].round(3)
    return result.sort_values(["Feature", "Frequency (%)", "Value"], ascending=[True, False, True])


def main() -> None:
    """Write the per-feature value-frequency CSV and Markdown tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--numeric", type=Path, default=DEFAULT_NUMERIC_PATH)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    numeric = pd.read_csv(args.numeric, encoding="utf-8-sig")
    if len(data) != len(numeric):
        raise ValueError("Source and numeric feature tables must have the same row count and order.")
    result = calculate_frequencies(data, numeric)
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.csv_output, index=False, encoding="utf-8-sig")

    notes = (
        "# Feature value frequencies\n\n"
        "For categorical columns, `Count` is the number of nonblank species rows containing that token; "
        "a token is counted at most once per row. The denominator is the number of nonblank rows in "
        "that source feature, so `Frequency (%) = Count / Denominator × 100`. Since cells can contain several tokens, percentages for one feature can "
        "sum to more than 100%. For the three range columns, midpoint and width were used and exact "
        "numeric values were counted; the denominator is 173 rows. `name`, `family`, and `class` are "
        "excluded. These frequencies are descriptive inputs for later tier design, not tiers themselves.\n\n"
        + markdown_table(result)
        + "\n"
    )
    args.report_output.write_text(notes, encoding="utf-8")
    print(f"Feature-value rows: {len(result)} | Source rows: {len(data)}")
    print(f"Saved CSV table: {args.csv_output}")
    print(f"Saved Markdown table: {args.report_output}")


if __name__ == "__main__":
    main()
