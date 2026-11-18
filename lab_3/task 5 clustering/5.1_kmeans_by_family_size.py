"""K-Means on subsets of families, with k equal to the number of families in the subset.

Runs (family sizes counted over all 173 mushrooms):
- families with more than 10 mushrooms -> 5 families, k = 5
- families with more than 6 mushrooms  -> 10 families, k = 10
- families with more than 2 mushrooms  -> 15 families, k = 15
- all families                         -> 23 families, k = 23
Only the mushrooms of the included families are clustered. If the features grouped
mushrooms by family, each cluster would then contain one family.

K-Means only sees the 94 encoded feature columns; family, class and name are
not used for clustering, only for checking the result afterwards.

Two simple scores per run:
- Purity: share of mushrooms that belong to the largest family of their cluster.
  1.0 = every cluster contains a single family.
- Family togetherness: for each family, the share of its mushrooms that sit in the same
  cluster (its most common one), averaged over the families. 1.0 = no family is split.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write image files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


TASK5_DIR = Path(__file__).parent
LAB3_DIR = TASK5_DIR.parent
ENCODED_FILES = [LAB3_DIR / "processed_data" / "2.4_train_encoded.csv",
                 LAB3_DIR / "processed_data" / "2.4_test_encoded.csv"]
NON_FEATURE_COLUMNS = ["family", "name", "class"]
MIN_SIZES = [11, 7, 3, 1]  # "more than 10", "more than 6", "more than 2", all
RANDOM_STATE = 42

# Chart colours: validated 8-colour categorical palette + neutral text/grid colours.
SURFACE, TEXT, TEXT_MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = ["o", "^", "s"]  # 8 colours x 3 shapes = 24 unique styles


def short(family: str) -> str:
    """Family name without the word 'Family', for compact labels."""
    return family.replace(" Family", "")


def style_axis(ax) -> None:
    """Recessive grid and spines, muted tick labels."""
    ax.set_facecolor(SURFACE)
    ax.set_axisbelow(True)
    ax.grid(color=GRID, linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_MUTED, labelsize=8)


def scatter_panel(ax, points, groups, order, styles, title, explained, show_count: bool = True) -> None:
    """One PCA panel: a colour/marker per group, legend to the right."""
    for group in order:
        mask = (groups == group).to_numpy()
        colour, marker = styles[group]
        label = f"{group} ({int(mask.sum())})" if show_count else group
        ax.scatter(points[mask, 0], points[mask, 1], s=38, color=colour, marker=marker,
                   edgecolors=SURFACE, linewidths=0.7, label=label, zorder=3)
    ax.set_xlabel(f"PCA axis 1 ({explained[0] * 100:.1f}%)", color=TEXT, fontsize=9)
    ax.set_ylabel(f"PCA axis 2 ({explained[1] * 100:.1f}%)", color=TEXT, fontsize=9)
    ax.set_title(title, color=TEXT, loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=7, labelcolor=TEXT_MUTED, loc="upper left", bbox_to_anchor=(1.01, 1))
    style_axis(ax)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Run K-Means for each family-size threshold, draw the maps, and summarise how clusters match families."""
    sys.stdout.reconfigure(encoding="utf-8")
    data = pd.concat([pd.read_csv(path, sep=";", encoding="utf-8-sig") for path in ENCODED_FILES],
                     ignore_index=True)
    features = [column for column in data.columns if column not in NON_FEATURE_COLUMNS]
    X_all = data[features].to_numpy(dtype=float)

    # One PCA map for all 173 mushrooms, so every run is drawn on the same axes.
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    points_all = pca.fit_transform(X_all)
    explained = pca.explained_variance_ratio_

    # Same colour/marker for a family in every figure (ordered by family size).
    family_size = data["family"].value_counts().sort_index().sort_values(ascending=False, kind="stable")
    family_styles = {short(f): (PALETTE[i % 8], MARKERS[i // 8]) for i, f in enumerate(family_size.index)}

    score_rows, crosstab_sections = [], []
    for min_size in MIN_SIZES:
        families = family_size[family_size >= min_size].index.tolist()
        mask = data["family"].isin(families).to_numpy()
        subset = data[mask].copy()
        k = len(families)
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X_all[mask])
        subset["cluster_id"] = kmeans.labels_

        # Label each cluster with its largest family, e.g. "C3: Russula 8/12", to make the map readable.
        counts = pd.crosstab(subset["cluster_id"], subset["family"])
        majority = counts.idxmax(axis=1)
        cluster_names = {cid: f"C{cid + 1}: {short(majority[cid])} {counts.loc[cid].max()}/{counts.loc[cid].sum()}"
                         for cid in counts.index}
        subset["cluster"] = subset["cluster_id"].map(cluster_names)
        # Remember every mushroom's cluster for this run (blank for mushrooms not in this run).
        data.loc[mask, f"cluster_k{k}"] = [f"C{cid + 1}" for cid in kmeans.labels_]
        cluster_order = [cluster_names[cid] for cid in sorted(cluster_names)]
        cluster_styles = {name: (PALETTE[i % 8], MARKERS[i // 8]) for i, name in enumerate(cluster_order)}

        # Scores.
        purity = counts.max(axis=1).sum() / len(subset)
        togetherness_per_family = counts.max(axis=0) / counts.sum(axis=0)
        togetherness = float(togetherness_per_family.mean())
        # A family "gets its own cluster" if it is the largest family of at least one cluster.
        own_cluster = sorted({short(f) for f in majority})
        label = "all families" if min_size == 1 else f"more than {min_size - 1} mushrooms"
        score_rows.append({
            "Families included": label, "Families = k": k, "Mushrooms": len(subset),
            "Purity": round(float(purity), 3), "Family togetherness": round(togetherness, 3),
            "Families that are the largest in some cluster": f"{len(own_cluster)} of {k}",
        })

        # Map: left coloured by cluster, right coloured by family.
        points = points_all[mask]
        fig, axes = plt.subplots(1, 2, figsize=(17, 6.6), dpi=140)
        fig.patch.set_facecolor(SURFACE)
        scatter_panel(axes[0], points, subset["cluster"], cluster_order, cluster_styles,
                      f"K-Means clusters, k = {k} (label: largest family, its count / cluster size)", explained,
                      show_count=False)
        family_order = [short(f) for f in families]
        scatter_panel(axes[1], points, subset["family"].map(short), family_order, family_styles,
                      f"Real families ({k} families, {len(subset)} mushrooms)", explained)
        heading = "All families" if min_size == 1 else f"Families with {label}"
        fig.suptitle(f"{heading}: K-Means with k = {k}", color=TEXT, x=0.01, ha="left", fontsize=13)
        fig.tight_layout()
        fig.savefig(TASK5_DIR / f"5.1_k{k}_map.png", facecolor=SURFACE)
        plt.close(fig)

        # Cross-table: families (rows) x clusters (columns). The largest family of each cluster
        # (the one in the cluster's label on the map) is shown in bold; the last row is the cluster size.
        table = counts.T.reindex(families)
        column_max = table.max(axis=0)
        cells = table.apply(lambda column: [f"**{v}**" if v == column_max[column.name] and v > 0 else str(v)
                                            for v in column])
        cells.columns = [f"C{cid + 1}" for cid in table.columns]
        cells.insert(0, "Family (mushrooms)", [f"{short(f)} ({int(family_size[f])})" for f in table.index])
        size_row = {"Family (mushrooms)": "**Cluster size**",
                    **{f"C{cid + 1}": str(int(counts.loc[cid].sum())) for cid in counts.index}}
        cells = pd.concat([cells, pd.DataFrame([size_row])], ignore_index=True)
        crosstab_sections.append(f"## k = {k} ({label}, {len(subset)} mushrooms)\n\n![map](5.1_k{k}_map.png)\n\n"
                                 + markdown_table(cells))
        (TASK5_DIR / f"5.1_k{k}_table.md").write_text(markdown_table(cells) + "\n", encoding="utf-8")

    scores = pd.DataFrame(score_rows)
    scores.to_csv(TASK5_DIR / "5.1_scores.csv", index=False)
    # Cluster of every mushroom in every run (used in Task 6 to compare with the classifiers).
    assignment_columns = ["name", "family", "class"] + [c for c in data.columns if c.startswith("cluster_k")]
    data[assignment_columns].to_csv(TASK5_DIR / "5.1_cluster_assignments.csv", index=False, encoding="utf-8-sig")
    summary = (
        "# Task 5.1 K-Means with k = number of families, on subsets of families\n\n"
        + markdown_table(scores) + "\n\n" + "\n\n".join(crosstab_sections) + "\n"
    )
    (TASK5_DIR / "5.1_kmeans_by_family_size_summary.md").write_text(summary, encoding="utf-8")
    print(scores.to_string(index=False))
    for section in crosstab_sections[:2]:
        print(section.split("\n\n", 2)[-1])
        print()


if __name__ == "__main__":
    main()
