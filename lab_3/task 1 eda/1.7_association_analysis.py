"""Compute descriptive feature-association measures for Task 1."""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
TASK_DIR = Path(__file__).parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_ENCODED_PATH = LAB3_DIR / "processed_data" / "1.6_encoded_features.csv"
DEFAULT_NUMERIC_PATH = LAB3_DIR / "processed_data" / "1.5_numeric_range_features.csv"
DEFAULT_PLOT_DIR = TASK_DIR / "plots"
NON_FEATURE_COLUMNS = {"family", "name", "class"}
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]


def load_data(path: Path) -> pd.DataFrame:
    """Load the original CSV with semicolon delimiter and blanks preserved."""
    return pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")


def markdown_table(data: pd.DataFrame) -> str:
    """Format a DataFrame as Markdown without optional packages."""
    headers = [str(column) for column in data.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def corrected_cramers_v(first: pd.Series, second: pd.Series) -> float:
    """Calculate bias-corrected Cramer's V for two categorical/binary vectors."""
    table = pd.crosstab(first, second).to_numpy(dtype=float)
    n = table.sum()
    rows, columns = table.shape
    if n <= 1 or min(rows, columns) <= 1:
        return 0.0
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        chi_squared = np.nansum(np.where(expected > 0, (table - expected) ** 2 / expected, 0))
    phi_squared = chi_squared / n
    phi_squared_corrected = max(0.0, phi_squared - ((columns - 1) * (rows - 1)) / (n - 1))
    rows_corrected = rows - ((rows - 1) ** 2) / (n - 1)
    columns_corrected = columns - ((columns - 1) ** 2) / (n - 1)
    denominator = min(columns_corrected - 1, rows_corrected - 1)
    return float(np.sqrt(phi_squared_corrected / denominator)) if denominator > 0 else 0.0


def mutual_information_bits(first: pd.Series, second: pd.Series) -> float:
    """Compute empirical mutual information in bits for two categorical vectors."""
    table = pd.crosstab(first, second).to_numpy(dtype=float)
    n = table.sum()
    if n == 0:
        return 0.0
    joint = table / n
    first_marginal = joint.sum(axis=1, keepdims=True)
    second_marginal = joint.sum(axis=0, keepdims=True)
    denominator = first_marginal @ second_marginal
    mask = joint > 0
    return float(np.sum(joint[mask] * np.log2(joint[mask] / denominator[mask])))


def correlation_ratio(categories: pd.Series, measurements: pd.Series) -> float:
    """Compute eta, the association ratio between a categorical and numeric variable."""
    values = pd.to_numeric(measurements, errors="coerce")
    valid = values.notna() & categories.notna()
    values = values[valid]
    groups = categories[valid]
    if len(values) == 0 or values.nunique() <= 1:
        return 0.0
    grand_mean = values.mean()
    between = sum(
        len(group_values) * (group_values.mean() - grand_mean) ** 2
        for _, group_values in values.groupby(groups)
    )
    total = ((values - grand_mean) ** 2).sum()
    return float(np.sqrt(between / total)) if total > 0 else 0.0


def main() -> None:
    """Generate categorical and numeric association matrices and plots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--encoded", type=Path, default=DEFAULT_ENCODED_PATH)
    parser.add_argument("--numeric", type=Path, default=DEFAULT_NUMERIC_PATH)
    parser.add_argument("--plot-dir", type=Path, default=DEFAULT_PLOT_DIR)
    args = parser.parse_args()

    data = load_data(args.csv_path)
    encoded = pd.read_csv(args.encoded, encoding="utf-8-sig")
    numeric = pd.read_csv(args.numeric, encoding="utf-8-sig")
    if not (len(data) == len(encoded) == len(numeric)):
        raise ValueError("Source, encoded, and numeric tables must have the same row count and order.")

    categorical_columns = [
        column for column in data.columns
        if column not in NON_FEATURE_COLUMNS and column not in NUMERIC_COLUMNS
    ]
    token_columns = {
        feature: [column for column in encoded.columns if column.startswith(feature + "=")]
        for feature in categorical_columns
    }
    means = pd.DataFrame(np.nan, index=categorical_columns, columns=categorical_columns, dtype=float)
    categorical_pairs = []
    for first, second in combinations(categorical_columns, 2):
        values = [
            corrected_cramers_v(encoded[first_token], encoded[second_token])
            for first_token in token_columns[first]
            for second_token in token_columns[second]
        ]
        mean_value = float(np.mean(values)) if values else 0.0
        max_value = float(np.max(values)) if values else 0.0
        means.loc[first, second] = means.loc[second, first] = mean_value
        categorical_pairs.append(
            {
                "Feature A": first,
                "Feature B": second,
                "Mean corrected Cramer's V across token pairs": round(mean_value, 3),
                "Maximum corrected Cramer's V across token pairs": round(max_value, 3),
                "Token-pair comparisons": len(values),
            }
        )
    categorical_matrix = means.fillna(0)
    categorical_matrix_rounded = categorical_matrix.round(3)

    numeric_columns = [
        f"{column}__{measure}"
        for column in NUMERIC_COLUMNS
        for measure in ("midpoint", "width")
    ]
    numeric_values = numeric[numeric_columns].apply(pd.to_numeric)
    numeric_spearman = numeric_values.rank(method="average").corr(method="pearson").round(3)

    targets = {"family": data["family"], "class": data["class"]}
    feature_target_rows = []
    for feature, columns in token_columns.items():
        for target_name, target in targets.items():
            token_scores = [
                (mutual_information_bits(encoded[column], target), column)
                for column in columns
            ]
            best_score, best_token = max(token_scores, default=(0.0, ""))
            feature_target_rows.append(
                {
                    "Feature": feature,
                    "Target label": target_name,
                    "Token with largest MI": best_token,
                    "Maximum token MI (bits)": round(best_score, 3),
                    "Mean token MI (bits)": round(float(np.mean([score for score, _ in token_scores])), 3) if token_scores else 0.0,
                }
            )
    categorical_target = pd.DataFrame(feature_target_rows)
    target_heatmap = categorical_target.pivot(
        index="Feature", columns="Target label", values="Maximum token MI (bits)"
    ).reindex(index=categorical_columns)

    eta_rows = []
    eta_matrix = pd.DataFrame(index=NUMERIC_COLUMNS, columns=["family", "class"], dtype=float)
    for feature in NUMERIC_COLUMNS:
        midpoint = numeric[f"{feature}__midpoint"]
        for target_name, target in targets.items():
            eta = correlation_ratio(target, midpoint)
            eta_matrix.loc[feature, target_name] = eta
            eta_rows.append(
                {
                    "Numeric feature": feature,
                    "Categorical label": target_name,
                    "Correlation ratio eta": round(eta, 3),
                }
            )
    eta_table = pd.DataFrame(eta_rows)

    args.plot_dir.mkdir(parents=True, exist_ok=True)
    pair_table = pd.DataFrame(categorical_pairs).sort_values(
        "Mean corrected Cramer's V across token pairs", ascending=False
    )
    (args.plot_dir / "1.7_01_categorical_associations.md").write_text(
        "# Categorical feature associations\n\n"
        "Token-level bias-corrected Cramer's V values are averaged for each pair of original categorical features. The table gives the mean and maximum across token pairs; this grouped summary is descriptive and can hide which exact token pair drives an association. Blank values have all-zero token indicators; missingness was analysed separately.\n\n"
        "## Mean grouped association matrix\n\n" + markdown_table(categorical_matrix_rounded.reset_index(names="Feature")) +
        "\n\n## Pair summaries\n\n" + markdown_table(pair_table) + "\n",
        encoding="utf-8",
    )
    numeric_spearman_path = args.plot_dir / "1.7_02_numeric_spearman.md"
    numeric_spearman_path.write_text(
        "# Numeric feature Spearman correlations\n\n"
        "Spearman correlations use the six midpoint and width features, calculated as Pearson correlations of their ranks.\n\n"
        + markdown_table(numeric_spearman.reset_index(names="Feature")) + "\n",
        encoding="utf-8",
    )
    target_path = args.plot_dir / "1.7_03_categorical_feature_target_mi.md"
    target_path.write_text(
        "# Categorical features versus family and class\n\n"
        "Mutual information is computed between each binary token-presence indicator and the target label. The maximum token MI per original feature is reported as a screening summary; it is not an unbiased measure of whole-feature importance, and scores are descriptive on this small dataset.\n\n"
        + markdown_table(categorical_target.sort_values(["Target label", "Maximum token MI (bits)"], ascending=[True, False]))
        + "\n",
        encoding="utf-8",
    )
    eta_path = args.plot_dir / "1.7_04_numeric_feature_target_eta.md"
    eta_path.write_text(
        "# Numeric features versus family and class\n\n"
        "Eta summarizes how much numeric midpoint values vary between the categories of each label. Values are descriptive and do not imply causation.\n\n"
        + markdown_table(eta_table)
        + "\n",
        encoding="utf-8",
    )

    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="white", context="notebook")
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(categorical_matrix, cmap="viridis", vmin=0, vmax=1, annot=True, fmt=".2f", annot_kws={"size": 6}, ax=ax)
    ax.set_title("Mean bias-corrected Cramer's V across token pairs")
    ax.set_xlabel("Categorical source feature")
    ax.set_ylabel("Categorical source feature")
    ax.tick_params(axis="x", labelrotation=55)
    ax.tick_params(axis="y", labelrotation=0)
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.7_01_categorical_associations.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 8))
    sns.heatmap(numeric_spearman, cmap="vlag", vmin=-1, vmax=1, center=0, annot=True, fmt=".2f", square=True, ax=ax)
    ax.set_title("Spearman correlation of numeric midpoint and width features")
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.7_02_numeric_spearman.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    sns.heatmap(target_heatmap, cmap="magma", annot=True, fmt=".2f", cbar_kws={"label": "Maximum token MI (bits)"}, ax=ax)
    ax.set_title("Categorical feature token associations with labels")
    ax.set_xlabel("Target label")
    ax.set_ylabel("Categorical source feature")
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.7_03_categorical_feature_target_mi.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(eta_matrix.astype(float), cmap="magma", vmin=0, vmax=1, annot=True, fmt=".2f", cbar_kws={"label": "Correlation ratio eta"}, ax=ax)
    ax.set_title("Numeric midpoint associations with labels")
    ax.set_xlabel("Target label")
    ax.set_ylabel("Numeric feature")
    fig.tight_layout()
    fig.savefig(args.plot_dir / "1.7_04_numeric_feature_target_eta.png", dpi=180)
    plt.close(fig)

    print(f"Rows: {len(data)} | Categorical source features: {len(categorical_columns)}")
    print(f"Cramer's V token-pair comparisons: {len(categorical_pairs)} grouped feature pairs")
    print("Top categorical MI feature/token by family:")
    print(categorical_target[categorical_target["Target label"] == "family"].nlargest(5, "Maximum token MI (bits)").to_string(index=False))
    print("\nNumeric eta summary:")
    print(eta_table.to_string(index=False))
    print(f"\nSaved association tables and 4 plots to: {args.plot_dir}")


if __name__ == "__main__":
    main()
