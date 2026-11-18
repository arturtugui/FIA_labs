"""Score species by feature-value rarity and assign approximate 70/25/5 tiers."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


LAB3_DIR = Path(__file__).parent.parent
DEFAULT_DATA_PATH = LAB3_DIR / "lab_condition" / "data.csv"
DEFAULT_NUMERIC_PATH = LAB3_DIR / "processed_data" / "1.5_numeric_range_features.csv"
DEFAULT_OUTPUT_PATH = LAB3_DIR / "processed_data" / "1.10_rarity_scores.csv"
DEFAULT_REPORT_PATH = Path(__file__).parent / "plots" / "1.10_rarity_scoring.md"
NUMERIC_COLUMNS = ["cap-diameter", "stem-height", "stem-width"]
EXCLUDED_COLUMNS = {"name", "family", "class", "veil-type"}
NUMERIC_BIN_COUNT = 10


def parse_tokens(cell: str) -> list[str]:
    """Parse a bracketed categorical cell into unique observed tokens."""
    value = cell.strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected categorical cell format: {cell!r}")
    return list(dict.fromkeys(token.strip() for token in value[1:-1].split(",") if token.strip()))


def points_for_frequency(count: int, denominator: int) -> int:
    """Map an observed-value frequency to the agreed rarity-point scale."""
    if count == 1:
        return 10
    frequency = count / denominator
    if frequency < 0.01:
        return 8
    if frequency < 0.05:
        return 5
    if frequency < 0.30:
        return 1
    return 0


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        cells = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def assign_tiers(scores: pd.Series) -> tuple[pd.Series, dict[str, int]]:
    """Cut score groups near 70/25/5 targets without splitting tied scores."""
    total = len(scores)
    target_common = round(total * 0.70)
    target_rare = round(total * 0.25)
    target_legendary = total - target_common - target_rare
    group_counts = scores.value_counts().sort_index()
    boundaries = [0]
    for count in group_counts:
        boundaries.append(boundaries[-1] + int(count))

    best = None
    for common_end in boundaries:
        for rare_end in boundaries:
            if rare_end < common_end:
                continue
            common_count = common_end
            rare_count = rare_end - common_end
            legendary_count = total - rare_end
            cost = (
                abs(common_count - target_common)
                + abs(rare_count - target_rare)
                + abs(legendary_count - target_legendary)
            )
            candidate = (cost, common_end, rare_end)
            if best is None or candidate < best:
                best = candidate

    assert best is not None
    _, common_end, rare_end = best
    ordered = sorted(group_counts.index.tolist())
    cumulative = 0
    score_tiers = {}
    for score in ordered:
        if cumulative < common_end:
            tier = "Common"
        elif cumulative < rare_end:
            tier = "Rare"
        else:
            tier = "Legendary"
        score_tiers[score] = tier
        cumulative += int(group_counts.loc[score])
    tiers = scores.map(score_tiers)
    counts = tiers.value_counts().reindex(["Common", "Rare", "Legendary"], fill_value=0).to_dict()
    return tiers, {key: int(value) for key, value in counts.items()}


def calculate_scores(data: pd.DataFrame, numeric: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate rarity points per feature and normalized species scores."""
    if len(data) != len(numeric):
        raise ValueError("Source and numeric feature tables must have the same row count and order.")
    categorical_features = [
        column for column in data.columns
        if column not in EXCLUDED_COLUMNS and column not in NUMERIC_COLUMNS
    ]
    feature_names = categorical_features + NUMERIC_COLUMNS
    feature_scores: dict[str, pd.Series] = {}

    for feature in categorical_features:
        cells = data[feature].astype(str).str.strip()
        observed = cells.ne("")
        denominator = int(observed.sum())
        token_lists = [parse_tokens(cell) if cell else [] for cell in cells]
        counts: dict[str, int] = {}
        for tokens in token_lists:
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
        per_token_points = {
            token: points_for_frequency(count, denominator)
            for token, count in counts.items()
        }
        feature_scores[feature] = pd.Series(
            [
                float(np.mean([per_token_points[token] for token in tokens])) if tokens else np.nan
                for tokens in token_lists
            ],
            index=data.index,
        )

    numeric_bins = []
    for feature in NUMERIC_COLUMNS:
        subfeature_points = []
        for statistic in ("midpoint", "width"):
            column = f"{feature}__{statistic}"
            values = numeric[column].astype(float)
            bin_codes, bin_edges = pd.cut(
                values,
                bins=NUMERIC_BIN_COUNT,
                labels=False,
                retbins=True,
                include_lowest=True,
                duplicates="drop",
            )
            denominator = int(values.notna().sum())
            counts = bin_codes.value_counts().sort_index()
            point_by_bin = {
                int(code): points_for_frequency(int(count), denominator)
                for code, count in counts.items()
            }
            points = bin_codes.map(point_by_bin).astype(float)
            subfeature_points.append(points)
            for code, count in counts.items():
                numeric_bins.append(
                    {
                        "Derived feature": column,
                        "Bin": int(code) + 1,
                        "Lower bound": round(float(bin_edges[int(code)]), 3),
                        "Upper bound": round(float(bin_edges[int(code) + 1]), 3),
                        "Rows in bin": int(count),
                        "Frequency (%)": round(float(count / denominator * 100), 2),
                        "Rarity points": point_by_bin[int(code)],
                    }
                )
        feature_scores[feature] = (subfeature_points[0] + subfeature_points[1]) / 2

    contribution_frame = pd.DataFrame(feature_scores, index=data.index)
    observed_counts = contribution_frame.notna().sum(axis=1)
    raw_points = contribution_frame.sum(axis=1, skipna=True)
    adjusted_score = raw_points / observed_counts * len(feature_names)
    tiers, _ = assign_tiers(adjusted_score)

    result = pd.DataFrame(
        {
            "name": data["name"],
            "family": data["family"],
            "class": data["class"],
            "observed_scored_features": observed_counts,
            "raw_points_sum": raw_points.round(3),
            "adjusted_score": adjusted_score.round(3),
            "tier": tiers,
        }
    )
    result = pd.concat([result, contribution_frame.add_prefix("points__")], axis=1)
    return result, pd.DataFrame(numeric_bins)


def main() -> None:
    """Generate a scored species table and report-ready tier audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--numeric", type=Path, default=DEFAULT_NUMERIC_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    data = pd.read_csv(args.csv_path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    numeric = pd.read_csv(args.numeric, encoding="utf-8-sig")
    scored, numeric_bins = calculate_scores(data, numeric)
    feature_count = sum(column.startswith("points__") for column in scored.columns)
    counts = scored["tier"].value_counts().reindex(["Common", "Rare", "Legendary"], fill_value=0).to_dict()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.output, index=False, encoding="utf-8-sig")

    total = len(scored)
    summary_rows = []
    for tier in ("Common", "Rare", "Legendary"):
        rows = scored[scored["tier"] == tier]
        summary_rows.append(
            {
                "Tier": tier,
                "Species": len(rows),
                "Share (%)": round(len(rows) / total * 100, 1),
                "Score range": f"{rows['adjusted_score'].min():g}–{rows['adjusted_score'].max():g}",
                "Median score": round(float(rows["adjusted_score"].median()), 3),
                "Mean observed scored features": round(float(rows["observed_scored_features"].mean()), 2),
            }
        )
    tier_summary = pd.DataFrame(summary_rows)
    legendary_species = scored[scored["tier"] == "Legendary"].sort_values(
        "adjusted_score", ascending=False
    )[["name", "family", "class", "adjusted_score"]].rename(
        columns={"name": "Species", "family": "Family", "class": "Class", "adjusted_score": "Score"}
    )
    family_table = pd.crosstab(scored["family"], scored["tier"]).reindex(
        columns=["Common", "Rare", "Legendary"], fill_value=0
    )
    class_table = pd.crosstab(scored["class"], scored["tier"]).reindex(
        columns=["Common", "Rare", "Legendary"], fill_value=0
    )
    missing_count = data[[c for c in data.columns if c not in EXCLUDED_COLUMNS]].apply(
        lambda row: sum(str(value).strip() == "" for value in row), axis=1
    )
    completeness_corr = scored["adjusted_score"].rank().corr(missing_count.rank(), method="pearson")
    mode_description = "; ".join(
        f"{tier}: {counts[tier]} ({counts[tier] / total * 100:.1f}%)"
        for tier in ("Common", "Rare", "Legendary")
    )
    notes = (
        "# Rarity score and provisional tiers\n\n"
        "## Scoring method\n\n"
        "Each observed feature value receives points using its frequency within that feature: a categorical "
        "token seen in one row, or a numeric bin containing one row, gets 10 points; otherwise <1% gets 8, "
        "<5% gets 5, <30% gets 1, and >=30% gets 0. "
        "For multi-valued categorical cells, token points are averaged within the feature so a cell with "
        "more listed tokens does not automatically score higher. Numeric midpoint and width values are "
        f"each grouped into {NUMERIC_BIN_COUNT} equal-width bins before assigning points; the midpoint/width "
        "points are averaged into one contribution per original numeric feature. `name`, `family`, and "
        "`class` are excluded. `veil-type` is excluded from this score in line with the proposed >90%-missing "
        "column removal, but the source data is unchanged. Missing features are omitted from the raw sum; "
        f"the sum is normalized to the same {feature_count}-feature scale using the number of observed "
        "scored features. The score is descriptive, not a biological measure of rarity.\n\n"
        "## Tier cut rule\n\n"
        "Species are ordered by adjusted score, targeting about 70% Common, 25% Rare, and 5% Legendary. "
        "Equal scores are kept together; when a tied score crosses a target boundary, tier sizes can differ "
        "slightly from the target proportions.\n\n"
        f"## Result\n\nTier assignment: {mode_description}. The score's Spearman correlation with the number "
        f"of missing feature cells is {completeness_corr:.3f}; this checks whether completeness still "
        "tracks the score after normalization.\n\n"
        + markdown_table(tier_summary)
        + "\n\n## Tier counts by family\n\n"
        + markdown_table(family_table.reset_index())
        + "\n\n## Tier counts by class\n\n"
        + markdown_table(class_table.reset_index())
        + "\n\n## Species assigned Legendary\n\n"
        + markdown_table(legendary_species)
        + "\n\n## Numeric bins and assigned points\n\n"
        + markdown_table(numeric_bins)
        + "\n\nThe per-species score file includes the adjusted score, tier, raw point sum, observed-feature count, "
        "and each feature's point contribution. Review the tied cut scores and species profiles before treating "
        "these provisional tiers as final.\n"
    )
    args.report.write_text(notes, encoding="utf-8")
    print(f"Rows scored: {len(scored)} | scored feature components: {feature_count}")
    print("Tier counts: " + mode_description)
    print(f"Spearman(score, missing feature count): {completeness_corr:.3f}")
    print(f"Saved scores: {args.output}")
    print(f"Saved report: {args.report}")


if __name__ == "__main__":
    main()
