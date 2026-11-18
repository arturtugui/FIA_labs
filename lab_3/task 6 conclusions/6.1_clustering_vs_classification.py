"""Compare the K-Means clusters (Task 5) with the classifiers' test results (Task 4).

Uses the k = 23 run of Task 5 (all 173 mushrooms, one cluster per family) and the
test predictions of the best classifier (random forest) and of KNN. Nothing is retrained.

Two comparisons:
1. Per family: how well the classifiers found the family's test mushrooms versus how
   together the family stays in the clusters (share of its mushrooms in its most common
   cluster, and whether it is the largest family of that cluster).
2. Per test mushroom: the "cluster family" is the largest family of the mushroom's cluster.
   For each random forest prediction we check whether the classifier and the cluster point
   to the same family, and, for mistakes, whether the wrong prediction is the cluster family
   (the mushroom looks like the family it was confused with).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


TASK6_DIR = Path(__file__).parent
LAB3_DIR = TASK6_DIR.parent
ASSIGNMENTS = LAB3_DIR / "task 5 clustering" / "5.1_cluster_assignments.csv"
FOREST = LAB3_DIR / "task 3 ensembles" / "random forest" / "3.1_test_predictions.csv"
KNN = LAB3_DIR / "task 2 classification" / "knn" / "2.5_test_predictions.csv"
K = 23


def short(family: str) -> str:
    """Family name without the word 'Family'."""
    return family.replace(" Family", "")


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Build the per-family and per-mushroom comparisons and write them to a summary file."""
    sys.stdout.reconfigure(encoding="utf-8")
    clusters = pd.read_csv(ASSIGNMENTS, encoding="utf-8-sig")
    cluster_column = f"cluster_k{K}"
    forest = pd.read_csv(FOREST, encoding="utf-8-sig")
    knn = pd.read_csv(KNN, encoding="utf-8-sig")

    # Largest family of every cluster (ties: alphabetical), computed over all 173 mushrooms.
    counts = pd.crosstab(clusters[cluster_column], clusters["family"])
    cluster_family = counts.apply(lambda row: sorted(row[row == row.max()].index)[0], axis=1)
    clusters["cluster_family"] = clusters[cluster_column].map(cluster_family)

    # --- 1. Per family (families that have test mushrooms) ---
    family_rows = []
    for family in sorted(forest["actual_family"].unique(), key=lambda f: (-int((clusters["family"] == f).sum()), f)):
        members = clusters[clusters["family"] == family]
        main_cluster = members[cluster_column].value_counts().sort_index().idxmax()
        together = members[cluster_column].value_counts().max() / len(members)
        test_mask = forest["actual_family"] == family
        family_rows.append({
            "Family": short(family), "Mushrooms": len(members),
            "Random forest found (test)": f"{int(forest.loc[test_mask, 'correct'].sum())}/{int(test_mask.sum())}",
            "KNN found (test)": f"{int(knn.loc[test_mask, 'correct'].sum())}/{int(test_mask.sum())}",
            "Clusters it is spread over": members[cluster_column].nunique(),
            "Share in its main cluster": f"{together * 100:.0f}%",
            "Largest family of that cluster?": "yes" if cluster_family[main_cluster] == family else
                                               f"no ({short(cluster_family[main_cluster])})",
        })
    family_table = pd.DataFrame(family_rows)

    # --- 2. Per test mushroom (random forest) ---
    merged = forest.merge(clusters[["name", cluster_column, "cluster_family"]], on="name", how="left")
    merged["cluster_says_true_family"] = merged["cluster_family"] == merged["actual_family"]
    merged["cluster_agrees_with_forest"] = merged["cluster_family"] == merged["predicted_family"]
    correct, wrong = merged[merged["correct"]], merged[~merged["correct"]]
    agreement = pd.DataFrame([
        {"Random forest prediction": "Correct", "Test mushrooms": len(correct),
         "Cluster family = real family": f"{int(correct['cluster_says_true_family'].sum())}/{len(correct)}",
         "Cluster family = predicted family": f"{int(correct['cluster_agrees_with_forest'].sum())}/{len(correct)}"},
        {"Random forest prediction": "Wrong", "Test mushrooms": len(wrong),
         "Cluster family = real family": f"{int(wrong['cluster_says_true_family'].sum())}/{len(wrong)}",
         "Cluster family = predicted family": f"{int(wrong['cluster_agrees_with_forest'].sum())}/{len(wrong)}"},
    ])
    mistakes = wrong[["name", "actual_family", "predicted_family", cluster_column, "cluster_family"]].copy()
    for column in ("actual_family", "predicted_family", "cluster_family"):
        mistakes[column] = mistakes[column].map(short)
    mistakes.columns = ["Mushroom", "Real family", "Random forest predicted", "Cluster (k = 23)",
                        "Largest family of that cluster"]

    summary = (
        "# Task 6.1 Clustering (Task 5, k = 23) versus classification (Task 4)\n\n"
        "## Per family\n\n" + markdown_table(family_table)
        + "\n\n## Per test mushroom (random forest)\n\n" + markdown_table(agreement)
        + "\n\n## The random forest's mistakes\n\n" + markdown_table(mistakes) + "\n"
    )
    (TASK6_DIR / "6.1_comparison_summary.md").write_text(summary, encoding="utf-8")
    print(family_table.to_string(index=False))
    print()
    print(agreement.to_string(index=False))
    print()
    print(mistakes.to_string(index=False))


if __name__ == "__main__":
    main()
