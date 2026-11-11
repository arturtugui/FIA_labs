"""Audit numeric ranges, compare endpoint correlations, and derive range features."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_PLOT_DIR = Path(__file__).parent / "plots"
DEFAULT_OUTPUT_PATH = LAB3_DIR / "processed_data" / "1.5_numeric_range_features.csv"
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]


def load_data(path: Path) -> pd.DataFrame:
    """Read the original semicolon-delimited CSV and preserve blank strings."""
    return pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")


def parse_range(cell: str) -> tuple[float, float, int] | None:
    """Parse `[min, max]`; a singleton becomes equal endpoints; a blank returns None."""
    value = cell.strip()
    if not value:
        return None
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected range syntax: {cell!r}")
    tokens = [token.strip() for token in value[1:-1].split(",") if token.strip()]
    if len(tokens) not in (1, 2):
        raise ValueError(f"Expected one or two values in range: {cell!r}")
    numbers = [float(token) for token in tokens]
    if len(numbers) == 1:
        return numbers[0], numbers[0], 1
    return numbers[0], numbers[1], 2


def markdown_table(data: pd.DataFrame) -> str:
    """Format a DataFrame as a Markdown table without optional dependencies."""
    headers = [str(column) for column in data.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data.itertuples(index=False, name=None):
        values = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def make_features(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build endpoint/midpoint/width features plus range audit and distribution summaries."""
    feature_data: dict[str, pd.Series] = {"name": data["name"]}
    audits = []
    summary_rows = []
    long_rows = []

    for column in NUMERIC_COLUMNS:
        parsed = [parse_range(cell) for cell in data[column]]
        minimum = pd.Series([item[0] if item else np.nan for item in parsed], index=data.index)
        maximum = pd.Series([item[1] if item else np.nan for item in parsed], index=data.index)
        midpoint = (minimum + maximum) / 2
        width = maximum - minimum
        single_count = sum(item is not None and item[2] == 1 for item in parsed)
        reversed_mask = minimum > maximum
        feature_data[f"{column}__min"] = minimum
        feature_data[f"{column}__max"] = maximum
        feature_data[f"{column}__midpoint"] = midpoint
        feature_data[f"{column}__width"] = width

        audits.append(
            {
                "Numeric column": column,
                "Single-value cells": single_count,
                "Blank cells": int(minimum.isna().sum()),
                "Rows with min > max": int(reversed_mask.sum()),
                "Rows with min = 0": int((minimum == 0).sum()),
                "Largest maximum": float(maximum.max()),
                "Species at largest maximum": "; ".join(data.loc[maximum == maximum.max(), "name"].tolist()),
            }
        )
        for statistic, values in (("min", minimum), ("max", maximum), ("midpoint", midpoint)):
            clean = values.dropna()
            summary_rows.append(
                {
                    "Numeric column": column,
                    "Statistic": statistic,
                    "Count": int(clean.count()),
                    "Median": round(float(clean.median()), 2),
                    "Mean": round(float(clean.mean()), 2),
                    "Minimum": round(float(clean.min()), 2),
                    "Maximum": round(float(clean.max()), 2),
                }
            )
            long_rows.extend(
                {"Numeric column": column, "Statistic": statistic, "Value": value}
                for value in clean
            )

    feature_frame = pd.DataFrame(feature_data)
    audit_frame = pd.DataFrame(audits)
    summary_frame = pd.DataFrame(summary_rows)
    feature_frame.attrs["long_values"] = pd.DataFrame(long_rows)
    return feature_frame, audit_frame, summary_frame


def spearman_by_ranks(first: pd.Series, second: pd.Series) -> float:
    """Calculate Spearman correlation as Pearson correlation of average ranks."""
    ranks_first = first.rank(method="average")
    ranks_second = second.rank(method="average")
    return float(ranks_first.corr(ranks_second, method="pearson"))


def main() -> None:
    """Run numeric-range audit, save derived features, tables, and plots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--plot-dir", type=Path, default=DEFAULT_PLOT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    data = load_data(args.csv_path)
    features, audit, summaries = make_features(data)
    long_values = features.attrs["long_values"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.plot_dir.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False, encoding="utf-8-sig")

    corr_rows = []
    for column in NUMERIC_COLUMNS:
        parsed = [parse_range(value) for value in data[column]]
        lows = pd.Series([item[0] if item else np.nan for item in parsed], dtype=float)
        highs = pd.Series([item[1] if item else np.nan for item in parsed], dtype=float)
        coefficient = spearman_by_ranks(lows, highs)
        corr_rows.append({"Numeric range": column, "Spearman(min, max)": round(coefficient, 3)})
    correlations = pd.DataFrame(corr_rows)

    outlier_rows = []
    zero_rows = []
    for column in NUMERIC_COLUMNS:
        parsed = [parse_range(value) for value in data[column]]
        endpoints = pd.DataFrame(
            {
                "name": data["name"],
                "minimum": [item[0] if item else np.nan for item in parsed],
                "maximum": [item[1] if item else np.nan for item in parsed],
            }
        )
        # Keep a short, auditable list of the three largest recorded maxima per measure.
        for row in endpoints.nlargest(3, "maximum").itertuples(index=False):
            outlier_rows.append(
                {"Numeric column": column, "Species": row.name, "Minimum": row.minimum, "Maximum": row.maximum}
            )
        for row in endpoints.loc[endpoints["minimum"] == 0].itertuples(index=False):
            zero_rows.append(
                {"Numeric column": column, "Species": row.name, "Minimum": row.minimum, "Maximum": row.maximum}
            )

    audit_path = args.plot_dir / "1.5_01_numeric_range_audit.md"
    audit_path.write_text(
        "# Numeric range audit\n\n"
        "Single-value cells were represented as equal minimum and maximum endpoints. No values were removed.\n\n"
        "## Range checks\n\n" + markdown_table(audit) +
        "\n\n## Spearman correlation between range endpoints\n\n" + markdown_table(correlations) +
        "\n\n## Rows with a zero minimum\n\n" + markdown_table(pd.DataFrame(zero_rows)) +
        "\n\n## Three largest maxima per measurement\n\n" + markdown_table(pd.DataFrame(outlier_rows)) + "\n",
        encoding="utf-8",
    )
    summary_path = args.plot_dir / "1.5_02_numeric_range_distributions.md"
    summary_path.write_text(
        "# Numeric range distribution summaries\n\n"
        "Summary statistics for the observed minimum, maximum, and midpoint values.\n\n"
        + markdown_table(summaries)
        + "\n",
        encoding="utf-8",
    )

    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", context="notebook")
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    for axis, column in zip(axes, NUMERIC_COLUMNS):
        subset = long_values[long_values["Numeric column"] == column]
        sns.boxplot(
            data=subset,
            x="Statistic",
            y="Value",
            order=["min", "max", "midpoint"],
            showfliers=True,
            ax=axis,
        )
        axis.set_title(column)
        axis.set_xlabel("Range statistic")
        axis.set_ylabel("Measurement value (source units)")
    fig.suptitle("Distribution of range endpoints and midpoints", y=1.03)
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.5_02_numeric_range_distributions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    corr_values = correlations.set_index("Numeric range")["Spearman(min, max)"]
    sns.barplot(x=corr_values.index, y=corr_values.values, color="#4C78A8", ax=ax)
    ax.set_ylim(0, 1.05)
    ax.set_title("Spearman correlation between range endpoints")
    ax.set_xlabel("Numeric range column")
    ax.set_ylabel("Spearman correlation")
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.5_03_endpoint_correlations.png", dpi=180)
    plt.close(fig)

    print(f"Rows: {len(data)} | Numeric range columns: {len(NUMERIC_COLUMNS)}")
    print("Range checks:")
    print(audit.to_string(index=False))
    print("\nSpearman correlations:")
    print(correlations.to_string(index=False))
    print(f"\nSaved derived numeric features: {args.output}")
    print(f"Saved audit tables and 2 plots to: {args.plot_dir}")


if __name__ == "__main__":
    main()
