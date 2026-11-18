"""K-Nearest Neighbours on all 94 encoded features, with k chosen by leave-one-out on the training rows.

How KNN classifies a mushroom:
1. Compute its distance to every training mushroom (Euclidean distance over the 94
   columns from Task 2.4). On the 0/1 dummy columns, the squared distance is simply the
   number of codes on which two mushrooms disagree; the three scaled size columns
   add at most 1 each.
2. Take the k training mushrooms with the smallest distance (its "nearest neighbours").
3. Predict the family that occurs most often among them (majority vote).
   A tied vote goes to the alphabetically first family (scikit-learn's behaviour).

Choosing k without using the test set (leave-one-out cross-validation):
for each candidate k, every training mushroom is predicted from the other 122
training mushrooms. The k with the best macro F1 is chosen (ties -> smaller k), and
only then is the test set used, once, to measure the final result.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write image files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.neighbors import KNeighborsClassifier


KNN_DIR = Path(__file__).parent
LAB3_DIR = KNN_DIR.parent.parent
DEFAULT_TRAIN_PATH = LAB3_DIR / "processed_data" / "2.4_train_encoded.csv"
DEFAULT_TEST_PATH = LAB3_DIR / "processed_data" / "2.4_test_encoded.csv"
NON_FEATURE_COLUMNS = ["family", "name", "class"]
K_VALUES = [1, 3, 5, 7, 9, 11, 13, 15]  # odd values make tied votes less likely

# Chart colours (validated categorical pair + neutral text/grid colours).
SURFACE, TEXT, TEXT_MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"


def make_knn(k: int) -> KNeighborsClassifier:
    """KNN with Euclidean distance and an equal vote for each of the k neighbours.

    `algorithm="brute"` compares against every training mushroom, so neighbours at equal
    distance are always taken in the same (file) order and results are reproducible.
    """
    return KNeighborsClassifier(n_neighbors=k, metric="euclidean", weights="uniform", algorithm="brute")


def scores(actual: pd.Series, predicted: np.ndarray) -> tuple[float, float]:
    """Accuracy and macro F1 (families in truth or predictions; never-predicted families score 0)."""
    return (
        float(accuracy_score(actual, predicted)),
        float(f1_score(actual, predicted, average="macro", zero_division=0)),
    )


def per_family_table(actual: pd.Series, predicted: np.ndarray) -> pd.DataFrame:
    """Precision, recall and F1 for every family present in the test set or the predictions."""
    labels = sorted(set(actual) | set(predicted))
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=labels, zero_division=0
    )
    return pd.DataFrame(
        {"Family": labels, "Test support": support, "Precision": precision.round(3),
         "Recall": recall.round(3), "F1": f1.round(3)}
    )


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def plot_k_selection(k_table: pd.DataFrame, best_k: int, baseline_accuracy: float, path: Path) -> None:
    """Line chart of leave-one-out accuracy and macro F1 for each k, marking the chosen k."""
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    series = [("Accuracy", "Leave-one-out accuracy", BLUE), ("Macro F1", "Leave-one-out macro F1", ORANGE)]
    for column, label, colour in series:
        ax.plot(k_table["k"], k_table[column], color=colour, linewidth=2, marker="o", markersize=8,
                markeredgecolor=SURFACE, markeredgewidth=2, label=label, zorder=3)
        # Direct label at the right end of each line, in text colour (identity comes from the marker).
        last = k_table.iloc[-1]
        ax.annotate(column, (last["k"], last[column]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TEXT_MUTED)
    ax.axhline(baseline_accuracy, color=GRAY, linewidth=1.5, linestyle=(0, (4, 3)), zorder=2,
               label="Always predict Tricholoma (accuracy)")
    ax.axvline(best_k, color=GRAY, linewidth=1, linestyle=":", zorder=1)
    ax.set_xticks(k_table["k"])
    ax.set_ylim(0, max(0.7, float(k_table[["Accuracy", "Macro F1"]].max().max()) + 0.08))
    # Label the chosen k near the top of the plot (after the y-range is fixed), clear of the lines.
    ax.annotate(f"chosen k = {best_k}", (best_k, ax.get_ylim()[1]), xytext=(4, -12),
                textcoords="offset points", fontsize=9, color=TEXT_MUTED)
    ax.set_xlim(k_table["k"].min() - 0.6, k_table["k"].max() + 2.2)
    ax.set_xlabel("k (number of nearest neighbours that vote)", color=TEXT)
    ax.set_ylabel("Score on training rows (leave-one-out)", color=TEXT)
    ax.set_title("KNN on all 94 features: choosing k", color=TEXT, loc="left", fontsize=12)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_MUTED)
    ax.legend(frameon=False, fontsize=9, loc="lower left", labelcolor=TEXT_MUTED)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    """Choose k by leave-one-out on train, evaluate once on test, and write the outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--test", type=Path, default=DEFAULT_TEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=KNN_DIR)
    args = parser.parse_args()

    train = pd.read_csv(args.train, sep=";", encoding="utf-8-sig")
    test = pd.read_csv(args.test, sep=";", encoding="utf-8-sig")
    features = [column for column in train.columns if column not in NON_FEATURE_COLUMNS]
    X_train, y_train = train[features].to_numpy(dtype=float), train["family"]
    X_test, y_test = test[features].to_numpy(dtype=float), test["family"]

    # --- Choose k: leave-one-out on the training rows only ---
    # Each training mushroom is predicted by a model fitted on the other 122.
    # Note: the six single-mushroom families can never be predicted correctly here,
    # because when their only mushroom is left out, no example of that family remains.
    k_rows = []
    for k in K_VALUES:
        loo_predictions = cross_val_predict(make_knn(k), X_train, y_train, cv=LeaveOneOut())
        accuracy, macro_f1 = scores(y_train, loo_predictions)
        k_rows.append({"k": k, "Accuracy": round(accuracy, 3), "Macro F1": round(macro_f1, 3),
                       "Correct": int((loo_predictions == y_train).sum())})
    k_table = pd.DataFrame(k_rows)
    # Macro F1 is the selection metric because it counts every family equally (the data is imbalanced).
    best_k = int(k_table.sort_values(["Macro F1", "k"], ascending=[False, True]).iloc[0]["k"])
    best_row = k_table[k_table["k"] == best_k].iloc[0]

    # Baseline for comparison: always predict the most common training family.
    majority_family = y_train.value_counts().sort_index().idxmax()
    loo_baseline = float(np.mean([
        # Leaving one mushroom out can only lower its own family's count by one.
        family == y_train.drop(index).value_counts().sort_index().idxmax()
        for index, family in y_train.items()
    ]))

    # --- Final model: fit on all 123 training rows with the chosen k, test once ---
    model = make_knn(best_k).fit(X_train, y_train)
    train_with_self = model.predict(X_train)  # each mushroom is its own nearest neighbour here
    test_predictions = model.predict(X_test)
    train_self_accuracy, _ = scores(y_train, train_with_self)
    test_accuracy, test_macro_f1 = scores(y_test, test_predictions)
    baseline_test_accuracy, baseline_test_f1 = scores(y_test, np.array([majority_family] * len(y_test)))
    family_table = per_family_table(y_test, test_predictions)

    # How many test votes were ties (e.g. 3 neighbours from 3 different families)?
    # Those predictions are decided by the alphabetical tie-break, not by a real majority.
    _, test_neighbours = model.kneighbors(X_test)
    tied = []
    for positions in test_neighbours:
        vote_counts = y_train.iloc[positions].value_counts()
        tied.append(len(vote_counts) > 1 and vote_counts.iloc[0] == vote_counts.iloc[1])
    tied = np.array(tied)
    correct = test_predictions == y_test.to_numpy()
    vote_table = pd.DataFrame(
        [
            {"Vote": "Clear majority", "Test mushrooms": int((~tied).sum()),
             "Correct": int(correct[~tied].sum()),
             "Accuracy": f"{correct[~tied].mean() * 100:.1f}%" if (~tied).any() else "-"},
            {"Vote": "Tied (decided alphabetically)", "Test mushrooms": int(tied.sum()),
             "Correct": int(correct[tied].sum()),
             "Accuracy": f"{correct[tied].mean() * 100:.1f}%" if tied.any() else "-"},
        ]
    )

    # Worked example: the nearest neighbours of the first test mushroom.
    distances, neighbour_positions = model.kneighbors(X_test[:1])
    example = test.iloc[0]
    example_table = pd.DataFrame(
        {"Neighbour": [train.iloc[p]["name"] for p in neighbour_positions[0]],
         "Family": [train.iloc[p]["family"] for p in neighbour_positions[0]],
         "Distance": distances[0].round(3)}
    )
    example_prediction = test_predictions[0]

    # --- Outputs ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Save the exact dataframes the model was trained and tested on (identifier columns
    # family/name/class + the 94 feature columns), so the KNN input can be inspected directly.
    # .pkl stores the pandas DataFrame object itself (reload with pd.read_pickle);
    # .csv is the same table as plain text, for opening in a spreadsheet.
    train.to_pickle(args.output_dir / "2.5_knn_train_data.pkl")
    test.to_pickle(args.output_dir / "2.5_knn_test_data.pkl")
    train.to_csv(args.output_dir / "2.5_knn_train_data.csv", sep=";", index=False, encoding="utf-8-sig")
    test.to_csv(args.output_dir / "2.5_knn_test_data.csv", sep=";", index=False, encoding="utf-8-sig")
    plot_path = args.output_dir / "2.5_k_selection.png"
    plot_k_selection(k_table, best_k, loo_baseline, plot_path)
    k_table.to_csv(args.output_dir / "2.5_k_selection.csv", index=False)
    pd.DataFrame(
        {"name": test["name"], "actual_family": y_test, "predicted_family": test_predictions,
         "correct": y_test.to_numpy() == test_predictions}
    ).to_csv(args.output_dir / "2.5_test_predictions.csv", index=False, encoding="utf-8-sig")

    n_train, n_test = len(y_train), len(y_test)
    results_table = pd.DataFrame(
        [
            {"Data": "Training, each mushroom predicted from the other 122 (leave-one-out)",
             "Mushrooms": n_train, "Correctly classified": int(best_row["Correct"]),
             "Accuracy": f"{best_row['Accuracy'] * 100:.1f}%"},
            {"Data": "Training, mushroom itself included among the neighbours",
             "Mushrooms": n_train, "Correctly classified": int((train_with_self == y_train).sum()),
             "Accuracy": f"{train_self_accuracy * 100:.1f}%"},
            {"Data": "Test (never seen)", "Mushrooms": n_test,
             "Correctly classified": int((test_predictions == y_test).sum()),
             "Accuracy": f"{test_accuracy * 100:.1f}%"},
        ]
    )
    summary = (
        "# Task 2.5 KNN on all 94 features\n\n"
        f"Inputs: the {len(features)} encoded columns from Task 2.4 ({n_train} training and {n_test} test "
        "mushrooms). Euclidean distance, equal votes, tied votes go to the alphabetically first family.\n\n"
        "## Choosing k (leave-one-out on the training rows)\n\n"
        + markdown_table(k_table)
        + f"\n\nChosen k = **{best_k}** (highest leave-one-out macro F1; ties go to the smaller k). "
        f"Always predicting `{majority_family}` scores {loo_baseline:.3f} leave-one-out accuracy.\n\n"
        f"![k selection]({plot_path.name})\n\n"
        "## Results\n\n"
        + markdown_table(results_table)
        + f"\n\nTest macro F1: {test_macro_f1:.3f}. Always predicting `{majority_family}` on test: "
        f"accuracy {baseline_test_accuracy:.3f}, macro F1 {baseline_test_f1:.3f}.\n\n"
        "## Clear versus tied votes on the test set\n\n"
        + markdown_table(vote_table)
        + "\n\n"
        f"## Example: nearest neighbours of test mushroom `{example['name']}` ({example['family']})\n\n"
        + markdown_table(example_table)
        + f"\n\nPrediction: **{example_prediction}** "
        + ("(correct)." if example_prediction == example["family"] else "(wrong).")
        + "\n\n## Per-family test scores\n\n"
        + markdown_table(family_table)
        + "\n"
    )
    (args.output_dir / "2.5_knn_summary.md").write_text(summary, encoding="utf-8")

    print(k_table.to_string(index=False))
    print(f"Chosen k: {best_k} | LOO baseline accuracy: {loo_baseline:.3f}")
    print(results_table.to_string(index=False))
    print(f"Test macro F1: {test_macro_f1:.3f} | baseline test acc {baseline_test_accuracy:.3f}, F1 {baseline_test_f1:.3f}")
    print(vote_table.to_string(index=False))
    print(f"Example {example['name']} ({example['family']}) -> {example_prediction}")
    print(example_table.to_string(index=False))


if __name__ == "__main__":
    main()
