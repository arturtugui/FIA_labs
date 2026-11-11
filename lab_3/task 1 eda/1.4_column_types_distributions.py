"""Document column roles/types and plot key dataset distributions for Task 1."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_PLOT_DIR = Path(__file__).parent / "plots"
TYPE_TABLE_PATH = Path(__file__).parent / "1.4_01_column_types.md"

NUMERIC_RANGE_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]
FEATURE_TYPES = {
    "cap-diameter": ("Numeric interval", "Range; represented by midpoint for class distribution plots."),
    "cap-shape": ("Multi-valued categorical", "A cell may list more than one nominal code."),
    "Cap-surface": ("Multi-valued categorical", "A cell may list more than one nominal code; some values are blank."),
    "cap-color": ("Multi-valued categorical", "A cell may list more than one nominal code."),
    "does-bruise-or-bleed": ("Binary categorical", "Observed codes are [f] and [t]."),
    "gill-attachment": ("Multi-valued categorical", "A cell may list more than one nominal code; some values are blank."),
    "gill-spacing": ("Single-valued categorical", "One nominal code per nonblank cell; no order assumed."),
    "gill-color": ("Multi-valued categorical", "A cell may list more than one nominal code."),
    "stem-height": ("Numeric interval", "Range; represented by midpoint for class distribution plots."),
    "stem-width": ("Numeric interval", "Range; represented by midpoint for class distribution plots."),
    "stem-root": ("Single-valued categorical", "One nominal code per nonblank cell; many cells are blank."),
    "stem-surface": ("Multi-valued categorical", "A cell may list more than one nominal code; some values are blank."),
    "stem-color": ("Multi-valued categorical", "A cell may list more than one nominal code."),
    "veil-type": ("Single-valued categorical", "One observed code; most cells are blank."),
    "veil-color": ("Multi-valued categorical", "A cell may list more than one nominal code; many cells are blank."),
    "has-ring": ("Binary categorical", "Observed codes are [t] and [f]."),
    "ring-type": ("Multi-valued categorical", "A cell may list more than one nominal code; a few cells are blank."),
    "Spore-print-color": ("Multi-valued categorical", "A cell may list more than one nominal code; many cells are blank."),
    "habitat": ("Multi-valued categorical", "A cell may list more than one nominal code."),
    "season": ("Multi-valued categorical", "A cell may list more than one nominal code."),
}


def load_catalogue(path: Path) -> pd.DataFrame:
    """Load the source CSV with its semicolon delimiter and preserve blanks."""
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def markdown_table(data: pd.DataFrame) -> str:
    """Format a DataFrame as a Markdown table without optional packages."""
    headers = [str(column) for column in data.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_sidecar(path: Path, title: str, note: str, data: pd.DataFrame) -> None:
    """Write a plot's exact data and a short explanation to a Markdown file."""
    path.write_text(f"# {title}\n\n{note}\n\n{markdown_table(data)}\n", encoding="utf-8")


def parse_numeric_midpoint(value: str) -> float:
    """Convert a bracketed numeric range to its midpoint; a singleton has zero width."""
    if not value.strip():
        return float("nan")
    contents = value.strip().strip("[]")
    tokens = [token.strip() for token in contents.split(",") if token.strip()]
    numbers = [float(token) for token in tokens]
    if len(numbers) == 1:
        low = high = numbers[0]
    elif len(numbers) == 2:
        low, high = numbers
    else:
        raise ValueError(f"Unexpected numeric range format: {value!r}")
    if low > high:
        raise ValueError(f"Numeric range has min > max: {value!r}")
    return (low + high) / 2


def create_column_type_table(data: pd.DataFrame) -> pd.DataFrame:
    """Build a role/type/description row for each source column."""
    rows = []
    for column in data.columns:
        if column == "name":
            role, variable_type, note = "Identifier", "Nominal text", "Species name; not a model feature."
        elif column == "family":
            role, variable_type, note = "Classification target", "Nominal categorical", "Predicted by the Task 2–4 classifiers."
        elif column == "class":
            role, variable_type, note = "Analysis label", "Binary categorical", "Separate label for analysis and cluster comparison."
        else:
            role = "Feature"
            variable_type, note = FEATURE_TYPES[column]
        rows.append(
            {
                "Column": column,
                "Role": role,
                "Variable type": variable_type,
                "Notes": note,
            }
        )
    return pd.DataFrame(rows)


def plot_distributions(data: pd.DataFrame, plot_dir: Path) -> None:
    """Create family/class count plots, a family-class stacked plot, and numeric plots."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", context="notebook")

    family_counts = data["family"].value_counts().sort_values(ascending=False)
    family_table = family_counts.rename_axis("Family").reset_index(name="Mushroom count")
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(data=family_table, x="Family", y="Mushroom count", color="#4C78A8", ax=ax)
    ax.set(title="Mushroom counts by family", xlabel="Family", ylabel="Number of mushrooms")
    ax.tick_params(axis="x", labelrotation=65)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    fig.tight_layout()
    fig.savefig(plot_dir / "1.4_02_family_distribution.png", dpi=180)
    plt.close(fig)
    write_sidecar(
        plot_dir / "1.4_02_family_distribution.md",
        "Mushroom counts by family",
        "Counts are sorted from largest to smallest family.",
        family_table,
    )

    class_counts = data["class"].value_counts().sort_index()
    class_table = class_counts.rename_axis("Class code").reset_index(name="Mushroom count")
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(data=class_table, x="Class code", y="Mushroom count", color="#F58518", ax=ax)
    ax.set(title="Mushroom counts by class code", xlabel="Class code", ylabel="Number of mushrooms")
    fig.tight_layout()
    fig.savefig(plot_dir / "1.4_03_class_distribution.png", dpi=180)
    plt.close(fig)
    write_sidecar(
        plot_dir / "1.4_03_class_distribution.md",
        "Mushroom counts by class code",
        "Counts are shown for the recorded class labels; their biological meaning should follow the course data definition.",
        class_table,
    )

    family_order = family_counts.index.tolist()
    classes = sorted(data["class"].unique())
    family_class = (
        pd.crosstab(data["family"], data["class"])
        .reindex(index=family_order, columns=classes, fill_value=0)
        .rename_axis("Family")
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(13, 6))
    bottom = pd.Series(0, index=family_class.index, dtype=int)
    palette = dict(zip(classes, sns.color_palette("Set2", n_colors=len(classes))))
    for class_code in classes:
        values = family_class[class_code]
        ax.bar(family_class["Family"], values, bottom=bottom, label=class_code, color=palette[class_code])
        bottom += values
    ax.set(
        title="Class composition within each family",
        xlabel="Family (sorted by size)",
        ylabel="Number of mushrooms",
    )
    ax.tick_params(axis="x", labelrotation=65)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    ax.legend(title="Class code")
    fig.tight_layout()
    fig.savefig(plot_dir / "1.4_04_class_by_family.png", dpi=180)
    plt.close(fig)
    write_sidecar(
        plot_dir / "1.4_04_class_by_family.md",
        "Class counts by family",
        "Each row gives the counts used in the stacked bar chart; families are sorted by total size in the plot.",
        family_class,
    )

    numeric_long_rows = []
    for column in NUMERIC_RANGE_COLUMNS:
        for index, raw_value in data[column].items():
            numeric_long_rows.append(
                {
                    "name": data.at[index, "name"],
                    "class": data.at[index, "class"],
                    "measurement": column,
                    "midpoint": parse_numeric_midpoint(raw_value),
                }
            )
    numeric_long = pd.DataFrame(numeric_long_rows).dropna(subset=["midpoint"])
    stats = (
        numeric_long.groupby(["measurement", "class"])["midpoint"]
        .agg(count="count", mean="mean", median="median", std="std", min="min", max="max")
        .round(2)
        .reset_index()
    )

    fig, axes = plt.subplots(1, len(NUMERIC_RANGE_COLUMNS), figsize=(15, 5))
    for ax, column in zip(axes, NUMERIC_RANGE_COLUMNS):
        subset = numeric_long[numeric_long["measurement"] == column]
        sns.boxplot(data=subset, x="class", y="midpoint", order=classes, color="#72B7B2", ax=ax)
        sns.stripplot(
            data=subset,
            x="class",
            y="midpoint",
            order=classes,
            color="#333333",
            alpha=0.35,
            size=3,
            jitter=0.18,
            ax=ax,
        )
        ax.set_title(column)
        ax.set_xlabel("Class code")
        ax.set_ylabel("Range midpoint (source units)")
    fig.suptitle("Numeric range midpoints by class", y=1.03)
    fig.tight_layout()
    fig.savefig(plot_dir / "1.4_05_numeric_by_class.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    write_sidecar(
        plot_dir / "1.4_05_numeric_by_class.md",
        "Numeric range midpoints by class",
        "Each bracketed measurement was represented by its midpoint. A single-value entry was treated as a zero-width range, so its midpoint equals that value. The table reports descriptive statistics used to interpret the boxplots.",
        stats,
    )


def main() -> None:
    """Generate the Task 1 column-type table and distribution plots."""
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
        help=f"Directory for plots and matching tables (default: {DEFAULT_PLOT_DIR})",
    )
    parser.add_argument(
        "--type-table",
        type=Path,
        default=TYPE_TABLE_PATH,
        help=f"Markdown column-type table (default: {TYPE_TABLE_PATH})",
    )
    args = parser.parse_args()

    data = load_catalogue(args.csv_path)
    type_table = create_column_type_table(data)
    args.type_table.parent.mkdir(parents=True, exist_ok=True)
    args.plot_dir.mkdir(parents=True, exist_ok=True)
    args.type_table.write_text(
        "# Column roles and variable types\n\n"
        "Categorical letter codes are treated as labels; no meanings or order are assumed without a data dictionary.\n\n"
        + markdown_table(type_table)
        + "\n",
        encoding="utf-8",
    )
    plot_distributions(data, args.plot_dir)

    print(f"Rows: {len(data)} | Columns: {len(data.columns)}")
    print(f"Saved column type table: {args.type_table}")
    print("Saved 4 plots and matching Markdown data tables to:")
    print(args.plot_dir)
    print("\nClass counts:")
    print(data["class"].value_counts().sort_index().to_string())
    print("\nLargest and smallest family sizes:")
    sizes = data["family"].value_counts().sort_values(ascending=False)
    print(sizes.head(3).to_string())
    print("...")
    print(sizes.tail(3).to_string())


if __name__ == "__main__":
    main()
