"""Compare all classifiers from Tasks 2 and 3 on the same 50 test mushrooms with several metrics.

Inputs: the saved test predictions of every model (no model is retrained here), the
training split (for the majority baseline and family sizes) and the Step 1.10 rarity tiers.

Metrics (all computed on the 50 test mushrooms):
- Accuracy: share of mushrooms classified correctly. Kept only as a reference, because
  the 13 Tricholoma test mushrooms dominate it.
- Balanced accuracy: the average recall over the families present in the test set,
  so every family counts equally ("on average, what share of each family is found?").
- Macro F1: the average F1 over families (precision and recall combined), every family
  counted equally; also punishes predicting a family wrongly (low precision).
- Weighted F1: the same F1 values, but averaged with each family weighted by its number
  of test mushrooms. Comparing it with macro F1 shows how much the big families carry a model.
- Matthews correlation coefficient (MCC): one number from the whole confusion matrix,
  from -1 (always wrong) through 0 (no better than chance) to 1 (perfect).

Uncertainty: the 50 test mushrooms are resampled with replacement 2000 times (bootstrap)
to get a 95% range for each score and for the difference between two models.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write image files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, matthews_corrcoef, recall_score,
)


TASK4_DIR = Path(__file__).parent
LAB3_DIR = TASK4_DIR.parent
PREDICTION_FILES = {
    "Disorder tree": LAB3_DIR / "task 2 classification" / "decision tree" / "2.3_test_predictions.csv",
    "KNN (k = 3)": LAB3_DIR / "task 2 classification" / "knn" / "2.5_test_predictions.csv",
    "Random forest": LAB3_DIR / "task 3 ensembles" / "random forest" / "3.1_test_predictions.csv",
    "Gradient boosting": LAB3_DIR / "task 3 ensembles" / "gradient boosting" / "3.2_test_predictions.csv",
}
TRAIN_PATH = LAB3_DIR / "processed_data" / "2.1_train.csv"
CLEAN_PATH = LAB3_DIR / "processed_data" / "1.11_clean.csv"
TIER_PATH = LAB3_DIR / "processed_data" / "1.10_rarity_scores.csv"
N_BOOTSTRAP = 2000
RANDOM_STATE = 42

# Chart colours: validated palette slot 1, sequential blue ramp, neutral text/grid colours.
SURFACE, TEXT, TEXT_MUTED, GRID, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
BLUE_RAMP = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def metric_values(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """All five metrics for one model. Never-predicted families score 0 instead of raising an error."""
    return {
        "Accuracy": accuracy_score(actual, predicted),
        "Balanced accuracy": balanced_accuracy_score(actual, predicted),
        "Macro F1": f1_score(actual, predicted, average="macro", zero_division=0),
        "Weighted F1": f1_score(actual, predicted, average="weighted", zero_division=0),
        "MCC": matthews_corrcoef(actual, predicted),
    }


def bootstrap(actual: np.ndarray, predictions: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Accuracy and macro F1 of every model on N_BOOTSTRAP resamples of the test set.

    The same resampled mushrooms are used for every model in a given round, so differences
    between two models can be compared round by round (a paired comparison).
    """
    rng = np.random.default_rng(RANDOM_STATE)
    results = {name: np.zeros((N_BOOTSTRAP, 2)) for name in predictions}
    for round_number in range(N_BOOTSTRAP):
        sample = rng.integers(0, len(actual), len(actual))  # 50 positions drawn with replacement
        for name, predicted in predictions.items():
            results[name][round_number] = (
                accuracy_score(actual[sample], predicted[sample]),
                f1_score(actual[sample], predicted[sample], average="macro", zero_division=0),
            )
    return results


def interval(values: np.ndarray) -> tuple[float, float]:
    """Middle 95% of the bootstrap values."""
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def style_axis(ax) -> None:
    """Recessive grid and spines, muted tick labels."""
    ax.set_facecolor(SURFACE)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9)


def plot_metrics(table: pd.DataFrame, path: Path) -> None:
    """One small panel per metric, models as horizontal bars with the value printed on each bar."""
    metrics = ["Accuracy", "Balanced accuracy", "Macro F1", "Weighted F1", "MCC"]
    models = table["Model"].tolist()[::-1]  # barh draws bottom-up; reverse so the table order reads top-down
    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 3.6), dpi=150, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    for ax, metric in zip(axes, metrics):
        values = table.set_index("Model").loc[models, metric].to_numpy(dtype=float)
        ax.barh(models, values, color=BLUE, height=0.62, zorder=3)
        for y_position, value in enumerate(values):
            ax.annotate(f"{value:.2f}", (max(value, 0), y_position), xytext=(3, 0), textcoords="offset points",
                        va="center", fontsize=8, color=TEXT_MUTED)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.5, 1])
        ax.set_title(metric, color=TEXT, fontsize=10, loc="left")
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        style_axis(ax)
    fig.suptitle("All models on the 50 test mushrooms (higher is better)", color=TEXT, x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def plot_intervals(table: pd.DataFrame, path: Path) -> None:
    """Accuracy and macro F1 per model with their 95% bootstrap ranges."""
    models = table["Model"].tolist()[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), dpi=150, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    for ax, metric in zip(axes, ["Accuracy", "Macro F1"]):
        rows = table.set_index("Model").loc[models]
        for y_position, (_, row) in enumerate(rows.iterrows()):
            low, high = row[f"{metric} low"], row[f"{metric} high"]
            ax.plot([low, high], [y_position, y_position], color=BLUE, linewidth=2, zorder=2)
            ax.plot(row[metric], y_position, "o", color=BLUE, markersize=8, markeredgecolor=SURFACE,
                    markeredgewidth=2, zorder=3)
            ax.annotate(f"{row[metric]:.2f}  ({low:.2f}–{high:.2f})", (high, y_position), xytext=(6, 0),
                        textcoords="offset points", va="center", fontsize=8, color=TEXT_MUTED)
        ax.set_yticks(range(len(models)), models)
        ax.set_xlim(0, 1.05)
        ax.set_title(f"{metric}: value and 95% range", color=TEXT, fontsize=10, loc="left")
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        style_axis(ax)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def plot_confusion(actual: np.ndarray, predicted: np.ndarray, title: str, path: Path) -> None:
    """Confusion matrix: rows = real family, columns = predicted family, numbers = mushrooms."""
    rows = sorted(set(actual))
    columns = sorted(set(actual) | set(predicted))
    matrix = confusion_matrix(actual, predicted, labels=columns)
    matrix = pd.DataFrame(matrix, index=columns, columns=columns).loc[rows, columns]
    short = lambda name: name.replace(" Family", "")
    colour_map = LinearSegmentedColormap.from_list("blue_ramp", BLUE_RAMP)
    # Colour by the share of each real family (row), so small families are as visible as big ones.
    shares = matrix.div(matrix.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(10.5, 7.5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.imshow(shares.to_numpy(), cmap=colour_map, vmin=0, vmax=1, aspect="auto")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            count = matrix.iat[i, j]
            if count:
                ax.text(j, i, str(count), ha="center", va="center", fontsize=8,
                        color="#ffffff" if shares.iat[i, j] > 0.55 else TEXT)
            # Outline the "correct" cell of each row (real family = predicted family), so a dark
            # cell elsewhere in the row is clearly a mistake.
            if matrix.index[i] == matrix.columns[j]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=TEXT_MUTED,
                                           linewidth=1.2, zorder=3))
    ax.set_xticks(range(len(columns)), [short(c) for c in columns], rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(rows)), [short(r) for r in rows], fontsize=8)
    ax.set_xlabel("Predicted family", color=TEXT)
    ax.set_ylabel("Real family", color=TEXT)
    ax.set_title(title + "\nnumbers = mushrooms; outlined cells = correct; shade = share of the real family",
                 color=TEXT, loc="left", fontsize=11)
    ax.tick_params(colors=TEXT_MUTED)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Compute all metrics, intervals, per-family and per-group results, and write tables and figures."""
    sys.stdout.reconfigure(encoding="utf-8")  # the Windows console cannot print some characters otherwise
    # Expected: some models predict families that have no test mushrooms (e.g. a singleton family);
    # balanced accuracy then warns. Those predictions simply count as wrong, which is what we want.
    warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
    # --- Load predictions; every file covers the same 50 test mushrooms in the same order ---
    frames = {name: pd.read_csv(path, encoding="utf-8-sig") for name, path in PREDICTION_FILES.items()}
    first = next(iter(frames.values()))
    for name, frame in frames.items():
        if not frame[["name", "actual_family"]].equals(first[["name", "actual_family"]]):
            raise ValueError(f"{name} predictions are not aligned with the other models")
    names = first["name"].to_numpy()
    actual = first["actual_family"].to_numpy()
    train = pd.read_csv(TRAIN_PATH, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    majority = train["family"].value_counts().sort_index().idxmax()
    predictions = {f"Always {majority.replace(' Family', '')}": np.array([majority] * len(actual))}
    predictions.update({name: frame["predicted_family"].to_numpy() for name, frame in frames.items()})

    # --- 1. All metrics + bootstrap ranges ---
    boot = bootstrap(actual, predictions)
    rows = []
    for name, predicted in predictions.items():
        values = metric_values(actual, predicted)
        acc_low, acc_high = interval(boot[name][:, 0])
        f1_low, f1_high = interval(boot[name][:, 1])
        rows.append({"Model": name, **values, "Correct": int((predicted == actual).sum()),
                     "Accuracy low": acc_low, "Accuracy high": acc_high,
                     "Macro F1 low": f1_low, "Macro F1 high": f1_high})
    table = pd.DataFrame(rows)
    display = table[["Model", "Correct", "Accuracy", "Balanced accuracy", "Macro F1", "Weighted F1", "MCC"]].copy()
    display["Correct"] = display["Correct"].map(lambda c: f"{c}/{len(actual)}")
    display = display.round(3)
    ranges = pd.DataFrame(
        {"Model": table["Model"],
         "Accuracy (95% range)": [f"{row['Accuracy']:.3f} ({row['Accuracy low']:.3f} to {row['Accuracy high']:.3f})"
                                  for _, row in table.iterrows()],
         "Macro F1 (95% range)": [f"{row['Macro F1']:.3f} ({row['Macro F1 low']:.3f} to {row['Macro F1 high']:.3f})"
                                  for _, row in table.iterrows()]}
    )

    # Paired differences: best model (by macro F1) minus every other model, on the same resamples.
    best = table.loc[table["Macro F1"].idxmax(), "Model"]
    difference_rows = []
    for name in predictions:
        if name == best:
            continue
        for column, metric in ((0, "Accuracy"), (1, "Macro F1")):
            diff = boot[best][:, column] - boot[name][:, column]
            low, high = interval(diff)
            difference_rows.append({"Comparison": f"{best} minus {name}", "Metric": metric,
                                    "Difference": round(float(np.mean(diff)), 3),
                                    "95% range": f"{low:+.3f} to {high:+.3f}",
                                    "Clear difference?": "yes" if low > 0 else "no (range includes 0)"})
    differences = pd.DataFrame(difference_rows)

    # --- 2. Recall per family (which families each model finds) ---
    families = sorted(set(actual))
    family_size = pd.read_csv(CLEAN_PATH, sep=";", dtype=str, keep_default_na=False,
                              encoding="utf-8-sig")["family"].value_counts()
    recall_rows = []
    for family in families:
        mask = actual == family
        row = {"Family": family.replace(" Family", ""), "Mushrooms in dataset": int(family_size[family]),
               "Test mushrooms": int(mask.sum())}
        for name, predicted in predictions.items():
            row[name] = f"{int((predicted[mask] == family).sum())}/{int(mask.sum())}"
        recall_rows.append(row)
    recall_table = pd.DataFrame(recall_rows).sort_values(["Mushrooms in dataset", "Family"], ascending=[False, True])

    # --- 3. Accuracy by family size group ---
    def size_group(family: str) -> str:
        size = family_size[family]
        return "Large (13–43 mushrooms)" if size >= 13 else "Medium (5–11)" if size >= 5 else "Small (2–3)"
    groups = np.array([size_group(f) for f in actual])
    group_rows = []
    for group in ["Large (13–43 mushrooms)", "Medium (5–11)", "Small (2–3)"]:
        mask = groups == group
        row = {"Family size group": group, "Families": len(set(actual[mask])), "Test mushrooms": int(mask.sum())}
        for name, predicted in predictions.items():
            correct = int((predicted[mask] == actual[mask]).sum())
            row[name] = f"{correct}/{int(mask.sum())} ({correct / mask.sum() * 100:.0f}%)"
        group_rows.append(row)
    group_table = pd.DataFrame(group_rows)

    # --- 4. Accuracy by rarity tier (Step 1.10) ---
    tiers = pd.read_csv(TIER_PATH, sep=None, engine="python", encoding="utf-8-sig").set_index("name")["tier"]
    test_tiers = np.array([tiers[n] for n in names])
    tier_rows = []
    for tier in ["Common", "Rare", "Legendary"]:
        mask = test_tiers == tier
        row = {"Tier": tier, "Test mushrooms": int(mask.sum())}
        for name, predicted in predictions.items():
            correct = int((predicted[mask] == actual[mask]).sum())
            row[name] = f"{correct}/{int(mask.sum())}" if mask.any() else "-"
        tier_rows.append(row)
    tier_table = pd.DataFrame(tier_rows)

    # --- Figures and files ---
    model_rows = table[table["Model"] != f"Always {majority.replace(' Family', '')}"]
    plot_metrics(table, TASK4_DIR / "4.1_metrics.png")
    plot_intervals(model_rows, TASK4_DIR / "4.1_uncertainty.png")
    plot_confusion(actual, predictions[best], f"{best}: real versus predicted family (test set)",
                   TASK4_DIR / "4.1_confusion_matrix_best_model.png")
    display.to_csv(TASK4_DIR / "4.1_metrics.csv", index=False)

    summary = (
        "# Task 4.1 Comparison of all models (50 test mushrooms)\n\n"
        "## All metrics\n\n" + markdown_table(display)
        + "\n\n![Metrics](4.1_metrics.png)\n\n"
        "## 95% ranges (bootstrap, 2000 resamples of the test set)\n\n" + markdown_table(ranges)
        + "\n\n![Uncertainty](4.1_uncertainty.png)\n\n"
        f"## Is {best} clearly better? (paired bootstrap differences)\n\n" + markdown_table(differences)
        + "\n\n## Test mushrooms found per family (recall as found / total)\n\n" + markdown_table(recall_table)
        + "\n\n## Accuracy by family size\n\n" + markdown_table(group_table)
        + "\n\n## Accuracy by rarity tier (Step 1.10)\n\n" + markdown_table(tier_table)
        + f"\n\n## Confusion matrix of {best}\n\n![Confusion matrix](4.1_confusion_matrix_best_model.png)\n"
    )
    (TASK4_DIR / "4.1_model_comparison_summary.md").write_text(summary, encoding="utf-8")

    for frame in (display, ranges, differences, recall_table, group_table, tier_table):
        print(frame.to_string(index=False))
        print()


if __name__ == "__main__":
    main()
