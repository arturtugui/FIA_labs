"""Analyse missing-value patterns in the Lab 3 mushroom catalogue.

Creates a row-missingness histogram, a joint-blank co-occurrence heatmap, and
blank-rate heatmaps by family and class. Row-level and group analyses use the
20 mushroom-description features, excluding family, name, and class.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_PLOT_DIR = Path(__file__).parent / "plots"
NON_FEATURE_COLUMNS = {"family", "name", "class"}


def load_catalogue(path: Path) -> pd.DataFrame:
    """Load the semicolon-delimited source while preserving empty cells."""
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def write_markdown_table(data: pd.DataFrame, path: Path, title: str, note: str) -> None:
    """Write a small Markdown report containing a dataframe as a table."""
    headers = [str(column) for column in data.columns]
    lines = [f"# {title}", "", note, ""]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in data.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_sidecars(data: pd.DataFrame, blank_features: pd.DataFrame, output_dir: Path) -> None:
    """Write Markdown tables with the exact data behind each planned plot."""
    row_empty_counts = blank_features.eq("").sum(axis=1)
    row_percent = row_empty_counts / blank_features.shape[1] * 100
    histogram = (
        row_empty_counts.value_counts()
        .reindex(range(int(row_empty_counts.max()) + 1), fill_value=0)
        .rename_axis("Empty feature columns")
        .reset_index(name="Mushroom count")
    )
    row_details = pd.DataFrame(
        {
            "Data row": np.arange(1, len(data) + 1),
            "Name": data["name"] if "name" in data else "",
            "Empty feature columns": row_empty_counts,
            "Empty feature columns (%)": row_percent.round(1),
        }
    )
    write_markdown_table(
        histogram,
        output_dir / "1.3_01_missingness_per_row.md",
        "Missing feature values per mushroom",
        f"Row counts and percentages use the {blank_features.shape[1]} mushroom-description features, excluding family, name, and class. The second table gives per-mushroom detail.",
    )
    with (output_dir / "1.3_01_missingness_per_row.md").open("a", encoding="utf-8") as report:
        report.write("\n## Per-mushroom detail\n\n")
        report.write("| " + " | ".join(map(str, row_details.columns)) + " |\n")
        report.write("| " + " | ".join("---" for _ in row_details.columns) + " |\n")
        for row in row_details.itertuples(index=False, name=None):
            report.write("| " + " | ".join(str(value) for value in row) + " |\n")

    missing = blank_features.eq("")
    missing_columns = missing.columns[missing.any(axis=0)]
    missing_int = missing.loc[:, missing_columns].astype(int)
    joint_counts = missing_int.T.dot(missing_int)
    write_markdown_table(
        joint_counts.reset_index(names="Feature"),
        output_dir / "1.3_02_missingness_cooccurrence.md",
        "Co-occurrence of empty feature values",
        "Each cell is the number of mushrooms for which both feature columns in that row and column are empty.",
    )

    for group_column, stem in (
        ("family", "1.3_03_missingness_by_family.md"),
        ("class", "1.3_04_missingness_by_class.md"),
    ):
        sizes = data[group_column].value_counts().rename("Mushrooms in group")
        group_rates = blank_features.eq("").groupby(data[group_column]).mean().mul(100)
        group_rates = group_rates.loc[:, group_rates.gt(0).any(axis=0)]
        group_table = group_rates.round(1).join(sizes).reset_index()
        first_column = group_table.columns[-1]
        group_table = group_table[[group_column, first_column] + [
            column for column in group_table.columns if column not in {group_column, first_column}
        ]]
        write_markdown_table(
            group_table,
            output_dir / stem,
            f"Feature missingness by {group_column}",
            "Values are the percentage of mushrooms in each group with a blank for that feature. Only feature columns with at least one blank are shown.",
        )


def save_row_missingness_plot(blank_features: pd.DataFrame, output_dir: Path) -> None:
    """Save a histogram of blank feature counts per mushroom."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    empty_per_row = blank_features.eq("").sum(axis=1)
    upper = int(empty_per_row.max()) if len(empty_per_row) else 0
    bins = np.arange(-0.5, upper + 1.5, 1)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.histplot(empty_per_row, bins=bins, discrete=True, ax=ax, color="#4C78A8")
    ax.set(
        title="Missing feature values per mushroom",
        xlabel=f"Empty feature columns (out of {blank_features.shape[1]})",
        ylabel="Number of mushrooms",
        xticks=range(upper + 1),
    )
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "1.3_01_missingness_per_row.png", dpi=180)
    plt.close(fig)


def save_cooccurrence_plot(blank_features: pd.DataFrame, output_dir: Path) -> None:
    """Save a heatmap of how often pairs of feature columns are both blank."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    missing = blank_features.eq("")
    missing_columns = missing.columns[missing.any(axis=0)]
    joint_counts = missing.loc[:, missing_columns].astype(int).T.dot(
        missing.loc[:, missing_columns].astype(int)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        joint_counts,
        annot=True,
        fmt="d",
        cmap="mako",
        square=True,
        cbar_kws={"label": "Rows where both columns are empty"},
        ax=ax,
    )
    ax.set_title("Co-occurrence of empty feature values")
    ax.set_xlabel("Feature column")
    ax.set_ylabel("Feature column")
    ax.tick_params(axis="x", labelrotation=45)
    ax.tick_params(axis="y", labelrotation=0)
    fig.tight_layout()
    fig.savefig(output_dir / "1.3_02_missingness_cooccurrence.png", dpi=180)
    plt.close(fig)


def save_group_missingness_plot(
    data: pd.DataFrame,
    blank_features: pd.DataFrame,
    group_column: str,
    output_path: Path,
) -> None:
    """Save a heatmap of feature blank percentages for each group value."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    group_sizes = data[group_column].value_counts()
    ordered_groups = group_sizes.index.tolist()
    blank_rates = (
        blank_features.eq("")
        .groupby(data[group_column])
        .mean()
        .mul(100)
        .reindex(ordered_groups)
    )
    missing_columns = blank_features.columns[blank_features.eq("").any(axis=0)]
    blank_rates = blank_rates.loc[:, missing_columns]

    height = max(5.5, 0.32 * len(blank_rates))
    fig, ax = plt.subplots(figsize=(12, height))
    sns.heatmap(
        blank_rates,
        annot=True,
        fmt=".0f",
        cmap="rocket_r",
        vmin=0,
        vmax=100,
        cbar_kws={"label": "Empty entries within group (%)"},
        ax=ax,
    )
    ax.set_title(f"Feature missingness by {group_column}")
    ax.set_xlabel("Feature column with at least one blank")
    ax.set_ylabel(group_column)
    ax.tick_params(axis="x", labelrotation=45)
    ax.tick_params(axis="y", labelrotation=0)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:
    """Run missingness checks and save the requested plots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"CSV file to analyse (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--plot-dir",
        type=Path,
        default=DEFAULT_PLOT_DIR,
        help=f"Directory for plot files (default: {DEFAULT_PLOT_DIR})",
    )
    args = parser.parse_args()

    data = load_catalogue(args.csv_path)
    feature_columns = [
        column for column in data.columns if column not in NON_FEATURE_COLUMNS
    ]
    blank_features = data.loc[:, feature_columns]
    args.plot_dir.mkdir(parents=True, exist_ok=True)
    row_empty_counts = blank_features.eq("").sum(axis=1)
    feature_missing_rates = blank_features.eq("").mean().mul(100)
    missing_columns = feature_missing_rates[feature_missing_rates > 0]

    print(f"Dataset: {args.csv_path}")
    print(f"Rows: {len(data)} | Feature columns analysed: {len(feature_columns)}")
    print(
        "Empty feature columns per row: "
        f"min={row_empty_counts.min()}, mean={row_empty_counts.mean():.2f}, "
        f"max={row_empty_counts.max()}"
    )
    print("Feature columns with missing values (blank percentage):")
    for column, rate in missing_columns.items():
        print(f"  {column}: {rate:.1f}%")

    prepare_sidecars(data, blank_features, args.plot_dir)
    try:
        import seaborn as sns

        sns.set_theme(style="whitegrid", context="notebook")
        save_row_missingness_plot(blank_features, args.plot_dir)
        save_cooccurrence_plot(blank_features, args.plot_dir)
        for group_column, filename in (
            ("family", "1.3_03_missingness_by_family.png"),
            ("class", "1.3_04_missingness_by_class.png"),
        ):
            save_group_missingness_plot(
                data,
                blank_features,
                group_column,
                args.plot_dir / filename,
            )
    except ImportError as error:
        print(f"\nMarkdown tables saved to: {args.plot_dir}")
        print(f"PNG plots were not generated: {error}")
        print("Install matplotlib and seaborn in the Python environment to generate PNGs.")
        return

    print(f"\nSaved 4 PNG plots and matching Markdown tables to: {args.plot_dir}")


if __name__ == "__main__":
    main()
