"""Follow up on missingness patterns from Step 1.3.

Compare pairwise blank co-occurrence with an independence baseline overall and
within families, then inspect blanks in related ring and veil columns. Outputs
are written to the existing plots folder as Markdown tables and a heatmap.
"""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "plots"
NON_FEATURE_COLUMNS = {"family", "name", "class"}


def load_catalogue(path: Path) -> pd.DataFrame:
    """Load the semicolon-delimited catalogue while preserving blank cells."""
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def markdown_table(data: pd.DataFrame) -> str:
    """Format a DataFrame as a Markdown table without extra dependencies."""
    headers = [str(column) for column in data.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data.itertuples(index=False, name=None):
        values = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def pairwise_missingness(blank_flags: pd.DataFrame, families: pd.Series) -> pd.DataFrame:
    """Compare observed pairwise blanks with overall and within-family baselines."""
    output = []
    total_rows = len(blank_flags)
    family_groups = blank_flags.groupby(families, sort=False)

    for first, second in combinations(blank_flags.columns, 2):
        observed_joint = int((blank_flags[first] & blank_flags[second]).sum())
        p_first = float(blank_flags[first].mean())
        p_second = float(blank_flags[second].mean())
        expected_overall = total_rows * p_first * p_second

        expected_within_family = 0.0
        for _, group in family_groups:
            size = len(group)
            expected_within_family += size * float(group[first].mean()) * float(group[second].mean())

        output.append(
            {
                "Feature A": first,
                "Feature B": second,
                "Both blank (rows)": observed_joint,
                "Expected overall (rows)": round(expected_overall, 2),
                "Overall excess (percentage points)": round(
                    100 * (observed_joint - expected_overall) / total_rows, 2
                ),
                "Expected within families (rows)": round(expected_within_family, 2),
                "Within-family excess (percentage points)": round(
                    100 * (observed_joint - expected_within_family) / total_rows, 2
                ),
            }
        )

    return pd.DataFrame(output).sort_values(
        "Within-family excess (percentage points)", key=lambda values: values.abs(), ascending=False
    )


def conditional_table(data: pd.DataFrame, row_column: str, blank_column: str) -> pd.DataFrame:
    """Return blank/nonblank counts and within-row-group blank percentages."""
    blank_status = data[blank_column].eq("").map({True: "Blank", False: "Recorded"})
    counts = pd.crosstab(data[row_column], blank_status).reindex(
        columns=["Blank", "Recorded"], fill_value=0
    )
    counts.insert(0, "Group rows", counts.sum(axis=1))
    percentages = pd.crosstab(
        data[row_column],
        blank_status,
        normalize="index",
    ).reindex(columns=["Blank", "Recorded"], fill_value=0).mul(100).round(1)
    percentages.columns = [f"{column} (%)" for column in percentages.columns]
    return counts.join(percentages).reset_index()


def save_pairwise_plot(pairwise: pd.DataFrame, columns: list[str], output_path: Path) -> None:
    """Plot within-family excess co-missingness in percentage points."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    matrix = pd.DataFrame(np.nan, index=columns, columns=columns, dtype=float)
    for _, row in pairwise.iterrows():
        first = row["Feature A"]
        second = row["Feature B"]
        excess = row["Within-family excess (percentage points)"]
        matrix.loc[first, second] = excess
        matrix.loc[second, first] = excess

    values = matrix.to_numpy(dtype=float)
    limit = max(float(np.nanmax(np.abs(values))), 0.1)
    fig, ax = plt.subplots(figsize=(11, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".1f",
        cmap="vlag",
        center=0,
        vmin=-limit,
        vmax=limit,
        mask=matrix.isna(),
        cbar_kws={"label": "Observed minus within-family expected joint blanks (pp)"},
        ax=ax,
    )
    ax.set_title("Pairwise blank co-occurrence after accounting for family")
    ax.set_xlabel("Feature column")
    ax.set_ylabel("Feature column")
    ax.tick_params(axis="x", labelrotation=45)
    ax.tick_params(axis="y", labelrotation=0)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:
    """Run family-adjusted co-occurrence and related-feature checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"CSV file to analyse (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    data = load_catalogue(args.csv_path)
    feature_columns = [column for column in data.columns if column not in NON_FEATURE_COLUMNS]
    blank_flags = data.loc[:, feature_columns].eq("")
    missing_columns = blank_flags.columns[blank_flags.any(axis=0)].tolist()
    blank_flags = blank_flags.loc[:, missing_columns]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pairwise = pairwise_missingness(blank_flags, data["family"])
    pairwise_note = (
        "For each feature pair, overall expected rows assume independent blanks using the overall rates. "
        "Within-family expected rows use the product of the two blank rates inside each family, then sum "
        "across families. Excess is observed joint blanks minus expected joint blanks, divided by all rows, "
        "in percentage points. Positive values indicate more joint blanks than that baseline; negative "
        "values indicate fewer. This is descriptive, not a significance test; small families make estimates unstable."
    )
    pairwise_path = args.output_dir / "1.3_05_family_adjusted_cooccurrence.md"
    pairwise_path.write_text(
        "# Pairwise missingness and family adjustment\n\n"
        + pairwise_note
        + "\n\n"
        + markdown_table(pairwise)
        + "\n",
        encoding="utf-8",
    )

    related_results = []
    if {"has-ring", "ring-type"}.issubset(data.columns):
        ring = conditional_table(data, "has-ring", "ring-type")
        related_results.append(
            "## Is `ring-type` blank by `has-ring` value?\n\n"
            "Counts and within-row percentages:\n\n"
            + markdown_table(ring)
        )
    if {"veil-type", "veil-color"}.issubset(data.columns):
        veil_status = data["veil-type"].eq("").map({True: "Blank", False: "Recorded"})
        veil = conditional_table(
            data.assign(veil_type_status=veil_status),
            "veil_type_status",
            "veil-color",
        )
        related_results.append(
            "## Is `veil-color` blank by `veil-type` recording status?\n\n"
            "Counts and within-row percentages:\n\n"
            + markdown_table(veil)
        )

    related_path = args.output_dir / "1.3_06_related_feature_blanks.md"
    related_path.write_text(
        "# Missingness in related feature columns\n\n"
        "These cross-tabs show whether one recorded feature's status aligns with blanks in a related column. "
        "They cannot establish whether a blank means absence or was not recorded.\n\n"
        + "\n\n".join(related_results)
        + "\n",
        encoding="utf-8",
    )

    print(f"Rows: {len(data)} | Incomplete feature columns: {len(missing_columns)}")
    print(f"Pairwise comparisons: {len(pairwise)}")
    print("Largest absolute within-family co-missingness deviations:")
    print(
        pairwise[["Feature A", "Feature B", "Overall excess (percentage points)",
                  "Within-family excess (percentage points)"]]
        .head(5)
        .to_string(index=False)
    )
    print(f"\nSaved pairwise table: {pairwise_path}")
    print(f"Saved related-feature cross-tabs: {related_path}")

    try:
        save_pairwise_plot(
            pairwise,
            missing_columns,
            args.output_dir / "1.3_05_family_adjusted_cooccurrence.png",
        )
    except ImportError as error:
        print(f"PNG heatmap not generated: {error}; Markdown table was saved.")
    else:
        print("Saved heatmap and its same-stem Markdown table.")


if __name__ == "__main__":
    main()
