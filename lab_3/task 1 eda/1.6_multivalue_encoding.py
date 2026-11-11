"""Multi-hot encode categorical sets and summarize dimensionality and rare tokens."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_NUMERIC_PATH = LAB3_DIR / "processed_data" / "1.5_numeric_range_features.csv"
DEFAULT_OUTPUT_DIR = LAB3_DIR / "processed_data"
DEFAULT_REPORT_DIR = Path(__file__).parent / "plots"
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]
NON_FEATURE_COLUMNS = {"family", "name", "class"}


def parse_tokens(cell: str) -> list[str]:
    """Parse a bracketed set of categorical codes; map blanks to an empty list."""
    value = cell.strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected categorical cell format: {cell!r}")
    return [token.strip() for token in value[1:-1].split(",") if token.strip()]


def markdown_table(data: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table without optional dependencies."""
    headers = [str(column) for column in data.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    """Encode categorical features, retain selected blank indicators, and report rare tokens."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--numeric", type=Path, default=DEFAULT_NUMERIC_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()

    source = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    numeric = pd.read_csv(args.numeric, encoding="utf-8-sig")
    if len(source) != len(numeric):
        raise ValueError("Numeric features and source catalogue have different row counts.")

    categorical_columns = [
        column for column in source.columns
        if column not in NON_FEATURE_COLUMNS and column not in NUMERIC_COLUMNS
    ]
    categorical_blocks = []
    token_rows = []
    feature_summary_rows = []
    blank_rates = source[categorical_columns].eq("").mean()

    for column in categorical_columns:
        parsed = [parse_tokens(value) for value in source[column]]
        tokens = sorted({token for row_tokens in parsed for token in row_tokens})
        block_data = {
            f"{column}={token}": [int(token in row_tokens) for row_tokens in parsed]
            for token in tokens
        }
        block = pd.DataFrame(block_data, index=source.index)
        categorical_blocks.append(block)
        nonblank_rows = sum(bool(row_tokens) for row_tokens in parsed)
        multi_rows = sum(len(row_tokens) > 1 for row_tokens in parsed)
        feature_summary_rows.append(
            {
                "Source feature": column,
                "Tokens": len(tokens),
                "Nonblank rows": nonblank_rows,
                "Rows with multiple tokens": multi_rows,
                "Average tokens per nonblank row": round(
                    sum(map(len, parsed)) / nonblank_rows, 2
                ) if nonblank_rows else 0,
                "Blank rate (%)": round(float(blank_rates[column]) * 100, 1),
            }
        )
        for token in tokens:
            count = int(block[f"{column}={token}"].sum())
            token_rows.append(
                {
                    "Encoded feature": f"{column}={token}",
                    "Source feature": column,
                    "Token": token,
                    "Species containing token": count,
                }
            )

    categorical_encoded = pd.concat(categorical_blocks, axis=1)
    missing_indicator_columns = [
        column for column in categorical_columns
        if 0.15 <= float(blank_rates[column]) <= 0.80
    ]
    missing_indicators = pd.DataFrame(
        {
            f"{column}__blank": source[column].eq("").astype(int)
            for column in missing_indicator_columns
        },
        index=source.index,
    )
    six_numeric = numeric[
        [f"{column}__{measure}" for column in NUMERIC_COLUMNS for measure in ("midpoint", "width")]
    ].copy()
    encoded = pd.concat([categorical_encoded, missing_indicators, six_numeric], axis=1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    encoded.to_csv(args.output_dir / "1.6_encoded_features.csv", index=False, encoding="utf-8-sig")
    metadata = pd.DataFrame(
        {
            "row_id": range(1, len(source) + 1),
            "name": source["name"],
            "family": source["family"],
            "class": source["class"],
        }
    )
    metadata.to_csv(args.output_dir / "1.6_row_metadata.csv", index=False, encoding="utf-8-sig")

    token_table = pd.DataFrame(token_rows)
    rare_tokens = token_table[token_table["Species containing token"] <= 2].sort_values(
        ["Source feature", "Species containing token", "Token"]
    )
    feature_summary = pd.DataFrame(feature_summary_rows)
    overview = pd.DataFrame(
        [
            {"Encoding component": "Categorical token indicators", "Columns": categorical_encoded.shape[1]},
            {"Encoding component": "Explicit blank indicators", "Columns": missing_indicators.shape[1]},
            {"Encoding component": "Numeric midpoint and width features", "Columns": six_numeric.shape[1]},
            {"Encoding component": "Total encoded model features", "Columns": encoded.shape[1]},
        ]
    )
    report = args.report_dir / "1.6_01_multivalue_encoding.md"
    report.write_text(
        "# Multi-hot encoding summary\n\n"
        "Each observed token becomes its own binary feature, so a cell such as `[x, f]` sets both token columns to 1. Blank categorical cells set all token indicators for that source feature to 0. For features with 15%-80% blanks, an explicit blank indicator is added; sparse features above 80% remain represented by their token-presence indicators. No token was merged or removed at this EDA stage.\n\n"
        "## Encoded dimensionality\n\n" + markdown_table(overview) +
        "\n\n## Per-feature token and blank summary\n\n" + markdown_table(feature_summary) +
        "\n\nThe `row_id` in `1.6_row_metadata.csv` preserves source-row alignment. `name`, `family`, and `class` are stored separately and are not part of the model-feature matrix. Optional per-cell token counts are summarized above but are not added as model columns.\n",
        encoding="utf-8",
    )
    rare_path = args.report_dir / "1.6_02_rare_tokens.md"
    rare_path.write_text(
        "# Rare categorical tokens\n\n"
        "Tokens appearing in one or two species are listed for review. They are retained in the encoded matrix for now; feature selection can assess them later.\n\n"
        + markdown_table(rare_tokens)
        + "\n",
        encoding="utf-8",
    )

    print(f"Rows: {len(source)} | Categorical source features: {len(categorical_columns)}")
    print(f"Multi-hot token columns: {categorical_encoded.shape[1]}")
    print(f"Explicit blank indicators: {missing_indicators.shape[1]} ({', '.join(missing_indicator_columns)})")
    print(f"Numeric midpoint/width columns: {six_numeric.shape[1]}")
    print(f"Total model features: {encoded.shape[1]}")
    print(f"Tokens appearing in <=2 species: {len(rare_tokens)}")
    print(f"Saved encoded features: {args.output_dir / '1.6_encoded_features.csv'}")
    print(f"Saved metadata: {args.output_dir / '1.6_row_metadata.csv'}")
    print(f"Saved Markdown summaries to: {args.report_dir}")


if __name__ == "__main__":
    main()
