"""Gradient boosting on the 94 encoded features, with settings chosen by leave-one-out on the training rows.

How gradient boosting classifies a mushroom:
1. Start from a simple guess: every family's share in the training data.
2. Build one small tree that corrects the current mistakes: it is trained to predict how
   far off the current probabilities are for each training mushroom. With 23 families,
   each round builds one small tree per family (23 trees per round).
3. Add that tree's correction, multiplied by the learning rate (0.1, so each round only
   fixes a tenth of the error), and repeat for `n_estimators` rounds.
4. The final prediction is the family with the highest probability after all rounds.

Unlike a random forest, where trees are independent and vote, here every tree depends on
the ones before it: the trees are built one after another, each focusing on what the
previous ones still get wrong.

Settings tried (all scored by leave-one-out macro F1 on the 123 training rows):
- n_estimators: 100 or 200 rounds;
- max_depth: 2 or 3 questions per small tree (shallow, because boosting overfits quickly
  on small data).
Fixed: learning_rate = 0.1 (the usual default); subsample = 0.8 (each round uses a random
80% of the training mushrooms, which adds randomness and reduces overfitting).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

# The shared helpers live one folder up, in "task 3 ensembles/".
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ensemble_common import (  # noqa: E402
    RANDOM_STATE, comparison_table, importance_by_feature, importance_table, load_encoded,
    markdown_table, per_family_table, plot_importances, results_table, scores, tune_by_leave_one_out,
)


OUTPUT_DIR = Path(__file__).parent
LEARNING_RATE = 0.1
SUBSAMPLE = 0.8
GRID = [
    {"n_estimators": 100, "max_depth": 2},
    {"n_estimators": 100, "max_depth": 3},
    {"n_estimators": 200, "max_depth": 2},
    {"n_estimators": 200, "max_depth": 3},
]


def make_booster(params: dict) -> GradientBoostingClassifier:
    """Gradient boosting with the given number of rounds and tree depth, and a fixed random seed."""
    return GradientBoostingClassifier(learning_rate=LEARNING_RATE, subsample=SUBSAMPLE,
                                      random_state=RANDOM_STATE, **params)


def main() -> None:
    """Tune on train by leave-one-out, fit the chosen model, evaluate once on test, write outputs."""
    train, test, features = load_encoded()
    X_train, y_train = train[features].to_numpy(dtype=float), train["family"]
    X_test, y_test = test[features].to_numpy(dtype=float), test["family"]

    # --- Choose the settings: leave-one-out on the training rows only ---
    print("Leave-one-out tuning (this takes a few minutes):")
    tuning, best = tune_by_leave_one_out(make_booster, GRID, X_train, y_train)
    best_label = ", ".join(f"{key}={value}" for key, value in best.items())
    loo_correct = int(tuning.loc[tuning["Macro F1"].idxmax(), "Correct"])

    # --- Final model: all 123 training rows, chosen settings, test set used once ---
    booster = make_booster(best).fit(X_train, y_train)
    train_self = booster.predict(X_train)
    test_predictions = booster.predict(X_test)
    test_accuracy, test_macro_f1 = scores(y_test, test_predictions)

    majority_family = y_train.value_counts().sort_index().idxmax()
    results = results_table(loo_correct, len(y_train), int((train_self == y_train).sum()),
                            int((test_predictions == y_test).sum()), len(y_test))
    comparison = comparison_table("Gradient boosting (Task 3.2)", y_test, test_predictions, majority_family)
    top_columns = importance_table(features, booster.feature_importances_)
    by_feature = importance_by_feature(features, booster.feature_importances_)

    # --- Outputs ---
    plot_importances(top_columns, "Gradient boosting: 15 most important columns",
                     OUTPUT_DIR / "3.2_feature_importance.png")
    pd.DataFrame(
        {"name": test["name"], "actual_family": y_test, "predicted_family": test_predictions,
         "correct": y_test.to_numpy() == test_predictions}
    ).to_csv(OUTPUT_DIR / "3.2_test_predictions.csv", index=False, encoding="utf-8-sig")
    tuning.to_csv(OUTPUT_DIR / "3.2_tuning.csv", index=False)

    summary = (
        "# Task 3.2 Gradient boosting\n\n"
        f"Learning rate {LEARNING_RATE}, subsample {SUBSAMPLE}; inputs: the {len(features)} encoded columns "
        "from Task 2.4. Settings chosen by leave-one-out macro F1 on the training rows.\n\n"
        "## Choosing the settings (leave-one-out on the training rows)\n\n"
        + markdown_table(tuning)
        + f"\n\nChosen: **{best_label}**.\n\n"
        "## Results\n\n"
        + markdown_table(results)
        + f"\n\nTest macro F1: {test_macro_f1:.3f}.\n\n"
        "## Comparison with the earlier models (same 50 test mushrooms)\n\n"
        + markdown_table(comparison)
        + "\n\n## Feature importance\n\n"
        "Importance = how much a column reduced the error across all boosting trees (the values sum to 1). "
        "It is biased towards columns with many possible split points (the numeric columns) and does not say "
        "in which direction a column pushes the prediction.\n\n"
        "![Feature importance](3.2_feature_importance.png)\n\n"
        + markdown_table(top_columns)
        + "\n\nSummed per original feature:\n\n"
        + markdown_table(by_feature)
        + "\n\n## Per-family test scores\n\n"
        + markdown_table(per_family_table(y_test, test_predictions))
        + "\n"
    )
    (OUTPUT_DIR / "3.2_gradient_boosting_summary.md").write_text(summary, encoding="utf-8")

    print(f"Chosen: {best_label}")
    print(results.to_string(index=False))
    print(f"Test accuracy {test_accuracy:.3f} | macro F1 {test_macro_f1:.3f}")
    print(comparison.to_string(index=False))
    print(by_feature.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
