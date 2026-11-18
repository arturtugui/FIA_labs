"""Shared helpers for the Task 3 ensemble scripts (Random Forest, Gradient Boosting).

Both ensembles use exactly the same protocol as KNN in Task 2.5, so all models can be
compared fairly:
- inputs: the 94 encoded columns from Task 2.4 (123 training and 50 test mushrooms);
- settings (hyperparameters) chosen by leave-one-out macro F1 on the training rows only;
- the test set is used once, at the end, with the chosen settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")  # write image files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import LeaveOneOut, cross_val_predict


TASK3_DIR = Path(__file__).parent
LAB3_DIR = TASK3_DIR.parent
TRAIN_PATH = LAB3_DIR / "processed_data" / "2.4_train_encoded.csv"
TEST_PATH = LAB3_DIR / "processed_data" / "2.4_test_encoded.csv"
# Earlier models' test predictions, read back for the comparison table.
EARLIER_MODELS = {
    "Disorder tree (Task 2.3)": LAB3_DIR / "task 2 classification" / "decision tree" / "2.3_test_predictions.csv",
    "KNN, k = 3 (Task 2.5)": LAB3_DIR / "task 2 classification" / "knn" / "2.5_test_predictions.csv",
    "Random forest (Task 3.1)": TASK3_DIR / "random forest" / "3.1_test_predictions.csv",
}
NON_FEATURE_COLUMNS = ["family", "name", "class"]
RANDOM_STATE = 42  # fixed seed: the ensembles are random, this makes every run identical

# Chart colours (validated palette slot 1 + neutral text/grid colours).
SURFACE, TEXT, TEXT_MUTED, GRID, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"


def load_encoded() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Read the Task 2.4 encoded train/test tables and return them with the feature column names."""
    train = pd.read_csv(TRAIN_PATH, sep=";", encoding="utf-8-sig")
    test = pd.read_csv(TEST_PATH, sep=";", encoding="utf-8-sig")
    features = [column for column in train.columns if column not in NON_FEATURE_COLUMNS]
    return train, test, features


def scores(actual, predicted) -> tuple[float, float]:
    """Accuracy and macro F1 (families in truth or predictions; never-predicted families score 0)."""
    return (
        float(accuracy_score(actual, predicted)),
        float(f1_score(actual, predicted, average="macro", zero_division=0)),
    )


def tune_by_leave_one_out(
    make_model: Callable[[dict], object], grid: list[dict], X: np.ndarray, y: pd.Series
) -> tuple[pd.DataFrame, dict]:
    """Score every setting in `grid` by leave-one-out on the training rows; return the table and the best setting.

    For each setting, every training mushroom is predicted by a model fitted on the other 122.
    The best setting has the highest macro F1; ties keep the earlier (simpler) setting in the grid.
    """
    rows = []
    for params in grid:
        # n_jobs=-1 runs the 123 leave-one-out fits in parallel on all CPU cores.
        predictions = cross_val_predict(make_model(params), X, y, cv=LeaveOneOut(), n_jobs=-1)
        accuracy, macro_f1 = scores(y, predictions)
        rows.append({**{key: str(value) for key, value in params.items()},
                     "Accuracy": round(accuracy, 3), "Macro F1": round(macro_f1, 3),
                     "Correct": int((predictions == y).sum())})
        print(f"  {params} -> accuracy {accuracy:.3f}, macro F1 {macro_f1:.3f}")
    table = pd.DataFrame(rows)
    # idxmax returns the first position with the highest value, so ties keep the earlier setting.
    best_position = int(table["Macro F1"].idxmax())
    return table, grid[best_position]


def per_family_table(actual, predicted) -> pd.DataFrame:
    """Precision, recall and F1 for every family present in the test set or the predictions."""
    labels = sorted(set(actual) | set(predicted))
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=labels, zero_division=0
    )
    return pd.DataFrame({"Family": labels, "Test support": support, "Precision": precision.round(3),
                         "Recall": recall.round(3), "F1": f1.round(3)})


def comparison_table(new_name: str, y_test: pd.Series, new_predictions: np.ndarray,
                     majority_family: str) -> pd.DataFrame:
    """Test accuracy and macro F1 of the majority baseline, the earlier models, and the new model."""
    rows = []
    baseline = np.array([majority_family] * len(y_test))
    accuracy, macro_f1 = scores(y_test, baseline)
    rows.append((f"Always predict {majority_family.replace(' Family', '')}", accuracy, macro_f1,
                 int((baseline == y_test).sum())))
    for name, path in EARLIER_MODELS.items():
        if path.exists() and name != new_name:
            earlier = pd.read_csv(path, encoding="utf-8-sig")
            accuracy, macro_f1 = scores(earlier["actual_family"], earlier["predicted_family"])
            rows.append((name, accuracy, macro_f1, int(earlier["correct"].sum())))
    accuracy, macro_f1 = scores(y_test, new_predictions)
    rows.append((f"**{new_name}**", accuracy, macro_f1, int((new_predictions == y_test).sum())))
    return pd.DataFrame(
        [{"Model": name, "Test accuracy": f"{acc * 100:.1f}% ({correct}/{len(y_test)})",
          "Test macro F1": f"{f1:.3f}"} for name, acc, f1, correct in rows]
    )


def importance_table(features: list[str], importances: np.ndarray, top: int = 15) -> pd.DataFrame:
    """The `top` encoded columns with the highest importance."""
    frame = pd.DataFrame({"Column": features, "Importance": importances})
    return frame.sort_values("Importance", ascending=False).head(top).round(4).reset_index(drop=True)


def importance_by_feature(features: list[str], importances: np.ndarray) -> pd.DataFrame:
    """Sum the importances of all dummy columns that come from the same original feature."""
    source = [name.split("=")[0] for name in features]
    frame = pd.DataFrame({"Original feature": source, "Importance": importances})
    return (frame.groupby("Original feature")["Importance"].sum().sort_values(ascending=False)
            .round(4).reset_index())


def plot_importances(table: pd.DataFrame, title: str, path: Path) -> None:
    """Horizontal bar chart of the most important columns (largest at the top)."""
    ordered = table.iloc[::-1]  # barh draws bottom-up, so reverse to put the largest on top
    fig, ax = plt.subplots(figsize=(8, 0.34 * len(ordered) + 1.4), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.barh(ordered["Column"], ordered["Importance"], color=BLUE, height=0.7, zorder=3)
    for y_position, value in enumerate(ordered["Importance"]):
        ax.annotate(f"{value:.3f}", (value, y_position), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8, color=TEXT_MUTED)
    ax.set_xlabel("Importance (share of the total impurity decrease)", color=TEXT)
    ax.set_title(title, color=TEXT, loc="left", fontsize=12)
    ax.set_xlim(0, float(ordered["Importance"].max()) * 1.18)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def results_table(loo_correct: int, n_train: int, train_self_correct: int,
                  test_correct: int, n_test: int) -> pd.DataFrame:
    """The Data / Mushrooms / Correct / Accuracy table used for every model in the README."""
    return pd.DataFrame(
        [
            {"Data": "Training, each mushroom predicted from the other 122 (leave-one-out)",
             "Mushrooms": n_train, "Correctly classified": loo_correct,
             "Accuracy": f"{loo_correct / n_train * 100:.1f}%"},
            {"Data": "Training, model fitted on all 123 and asked about the same mushrooms",
             "Mushrooms": n_train, "Correctly classified": train_self_correct,
             "Accuracy": f"{train_self_correct / n_train * 100:.1f}%"},
            {"Data": "Test (never seen)", "Mushrooms": n_test, "Correctly classified": test_correct,
             "Accuracy": f"{test_correct / n_test * 100:.1f}%"},
        ]
    )


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)
