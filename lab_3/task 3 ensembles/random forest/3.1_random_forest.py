"""Random forest on the 94 encoded features, with settings chosen by leave-one-out on the training rows.

How a random forest classifies a mushroom:
1. Build many decision trees (here 300). Each tree is trained on a bootstrap sample:
   123 mushrooms drawn at random *with replacement* from the 123 training mushrooms,
   so some appear several times and on average about 37% are left out.
2. At every split, a tree may only choose among a random subset of the columns
   (`max_features`). This makes the trees different from each other, so their
   mistakes partly cancel out when they vote.
3. Every tree gives its class probabilities for the mushroom; the forest averages them
   and predicts the family with the highest average.

Settings tried (all scored by leave-one-out macro F1 on the 123 training rows):
- max_features: "sqrt" (sqrt(94) ~ 9 columns per split) or 0.3 (30% ~ 28 columns per split);
- class_weight: None (every mushroom counts the same) or "balanced_subsample"
  (mistakes on small families cost more, recomputed for each tree's bootstrap sample).
n_estimators is fixed at 300: more trees only make the vote more stable, never worse.

Out-of-bag (OOB) check: each tree never saw ~37% of the training mushrooms, so those
mushrooms can be predicted by the trees that did not see them. This gives a second
training-only estimate without using the test set.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# The shared helpers live one folder up, in "task 3 ensembles/".
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ensemble_common import (  # noqa: E402
    RANDOM_STATE, comparison_table, importance_by_feature, importance_table, load_encoded,
    markdown_table, per_family_table, plot_importances, results_table, scores, tune_by_leave_one_out,
)


OUTPUT_DIR = Path(__file__).parent
N_TREES = 300
GRID = [
    {"max_features": "sqrt", "class_weight": None},
    {"max_features": "sqrt", "class_weight": "balanced_subsample"},
    {"max_features": 0.3, "class_weight": None},
    {"max_features": 0.3, "class_weight": "balanced_subsample"},
]


def make_forest(params: dict, oob: bool = False) -> RandomForestClassifier:
    """A 300-tree random forest with the given settings and a fixed random seed."""
    return RandomForestClassifier(n_estimators=N_TREES, random_state=RANDOM_STATE, oob_score=oob,
                                  n_jobs=-1 if oob else 1, **params)


def main() -> None:
    """Tune on train by leave-one-out, fit the chosen forest, evaluate once on test, write outputs."""
    train, test, features = load_encoded()
    X_train, y_train = train[features].to_numpy(dtype=float), train["family"]
    X_test, y_test = test[features].to_numpy(dtype=float), test["family"]

    # --- Choose the settings: leave-one-out on the training rows only ---
    print("Leave-one-out tuning (this takes a minute):")
    tuning, best = tune_by_leave_one_out(make_forest, GRID, X_train, y_train)
    best_label = ", ".join(f"{key}={value}" for key, value in best.items())
    loo_correct = int(tuning.loc[tuning["Macro F1"].idxmax(), "Correct"])

    # --- Final forest: all 123 training rows, chosen settings, test set used once ---
    forest = make_forest(best, oob=True).fit(X_train, y_train)
    train_self = forest.predict(X_train)
    test_predictions = forest.predict(X_test)
    test_accuracy, test_macro_f1 = scores(y_test, test_predictions)

    # Out-of-bag predictions: the family with the highest average probability among the
    # trees that did not see the mushroom (rows never left out by any tree would be NaN).
    oob_probabilities = forest.oob_decision_function_
    has_oob = ~np.isnan(oob_probabilities).any(axis=1)
    oob_predictions = forest.classes_[np.nanargmax(np.nan_to_num(oob_probabilities, nan=-1), axis=1)]
    oob_accuracy, oob_macro_f1 = scores(y_train[has_oob], oob_predictions[has_oob])

    majority_family = y_train.value_counts().sort_index().idxmax()
    results = results_table(loo_correct, len(y_train), int((train_self == y_train).sum()),
                            int((test_predictions == y_test).sum()), len(y_test))
    comparison = comparison_table("Random forest (Task 3.1)", y_test, test_predictions, majority_family)
    top_columns = importance_table(features, forest.feature_importances_)
    by_feature = importance_by_feature(features, forest.feature_importances_)

    # --- Outputs ---
    plot_importances(top_columns, "Random forest: 15 most important columns", OUTPUT_DIR / "3.1_feature_importance.png")
    pd.DataFrame(
        {"name": test["name"], "actual_family": y_test, "predicted_family": test_predictions,
         "correct": y_test.to_numpy() == test_predictions}
    ).to_csv(OUTPUT_DIR / "3.1_test_predictions.csv", index=False, encoding="utf-8-sig")
    tuning.to_csv(OUTPUT_DIR / "3.1_tuning.csv", index=False)

    summary = (
        "# Task 3.1 Random forest\n\n"
        f"{N_TREES} trees, inputs: the {len(features)} encoded columns from Task 2.4. Settings chosen by "
        "leave-one-out macro F1 on the training rows.\n\n"
        "## Choosing the settings (leave-one-out on the training rows)\n\n"
        + markdown_table(tuning)
        + f"\n\nChosen: **{best_label}**.\n\n"
        "## Results\n\n"
        + markdown_table(results)
        + f"\n\nTest macro F1: {test_macro_f1:.3f}. Out-of-bag estimate on the training rows "
        f"({int(has_oob.sum())} of {len(y_train)} mushrooms had out-of-bag trees): accuracy "
        f"{oob_accuracy * 100:.1f}%, macro F1 {oob_macro_f1:.3f}.\n\n"
        "## Comparison with the earlier models (same 50 test mushrooms)\n\n"
        + markdown_table(comparison)
        + "\n\n## Feature importance\n\n"
        "Importance = how much a column reduced the impurity of the tree nodes, averaged over all trees "
        "(the values sum to 1). It is biased towards columns with many possible split points (the numeric "
        "columns) and does not say in which direction a column pushes the prediction.\n\n"
        "![Feature importance](3.1_feature_importance.png)\n\n"
        + markdown_table(top_columns)
        + "\n\nSummed per original feature:\n\n"
        + markdown_table(by_feature)
        + "\n\n## Per-family test scores\n\n"
        + markdown_table(per_family_table(y_test, test_predictions))
        + "\n"
    )
    (OUTPUT_DIR / "3.1_random_forest_summary.md").write_text(summary, encoding="utf-8")

    print(f"Chosen: {best_label}")
    print(results.to_string(index=False))
    print(f"Test accuracy {test_accuracy:.3f} | macro F1 {test_macro_f1:.3f}")
    print(f"OOB accuracy {oob_accuracy:.3f} | OOB macro F1 {oob_macro_f1:.3f} | rows with OOB {int(has_oob.sum())}")
    print(comparison.to_string(index=False))
    print(by_feature.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
