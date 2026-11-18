"""Fill categorical blanks with training modes and cap numeric midpoints at the training 99th percentile.

Both the modes and the caps are learned from the 2.1 training rows only and then
applied unchanged to train and test, so no test value influences the training data.

Rules:
- Categorical blanks: replaced by the most frequent complete cell in the training rows
  (cells were already canonicalised as sorted sets in Step 1.11). Ties are broken
  alphabetically so the result is reproducible.
- `ring-type`: every blank occurs with `has-ring = [t]`. Its overall mode `[f]` means
  "no ring", so filling with it would create a contradiction. Instead, the mode is
  taken among training rows with `has-ring = [t]`, ignoring `[f]`.
- Numeric midpoints: values above the training 99th percentile are lowered to it.
  No lower cap is applied: the minimums are 0 (stem-less fungi, kept in Step 1.5).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TASK2_DIR = Path(__file__).parent
LAB3_DIR = TASK2_DIR.parent
DEFAULT_TRAIN_PATH = LAB3_DIR / "processed_data" / "2.1_train.csv"
DEFAULT_TEST_PATH = LAB3_DIR / "processed_data" / "2.1_test.csv"
DEFAULT_TRAIN_OUTPUT = LAB3_DIR / "processed_data" / "2.2_train_prepared.csv"
DEFAULT_TEST_OUTPUT = LAB3_DIR / "processed_data" / "2.2_test_prepared.csv"
DEFAULT_REPORT_PATH = TASK2_DIR / "2.2_preparation_summary.md"
NON_FEATURE_COLUMNS = ["family", "name", "class"]
CAP_QUANTILE = 0.99


def mode_with_tie_break(values: pd.Series) -> tuple[str, int, list[str]]:
    """Return the most frequent nonblank value, its count, and all tied values (alphabetical)."""
    observed = values[values.ne("")]
    counts = observed.value_counts()
    top_count = int(counts.max())
    tied = sorted(counts[counts == top_count].index.tolist())
    return tied[0], top_count, tied


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Fit modes and caps on train, apply them to both splits, and write a summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--test", type=Path, default=DEFAULT_TEST_PATH)
    parser.add_argument("--train-output", type=Path, default=DEFAULT_TRAIN_OUTPUT)
    parser.add_argument("--test-output", type=Path, default=DEFAULT_TEST_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    read = dict(sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    train = pd.read_csv(args.train, **read)
    test = pd.read_csv(args.test, **read)
    numeric_columns = [column for column in train.columns if column.endswith("-midpoint")]
    categorical_columns = [
        column for column in train.columns
        if column not in NON_FEATURE_COLUMNS and column not in numeric_columns
    ]

    # --- Mode imputation (learned from training rows only) ---
    imputation_rows = []
    for column in categorical_columns:
        train_blank = train[column].eq("")
        test_blank = test[column].eq("")
        if not train_blank.any() and not test_blank.any():
            continue
        if column == "ring-type":
            # Blank ring-type only occurs with has-ring = [t]; choose among real ring types.
            ringed = train.loc[train["has-ring"].eq("[t]"), column]
            fill_value, count, tied = mode_with_tie_break(ringed[ringed.ne("[f]")])
            rule = "mode among `has-ring = [t]` rows, excluding `[f]`"
        else:
            fill_value, count, tied = mode_with_tie_break(train[column])
            rule = "training mode"
        train.loc[train_blank, column] = fill_value
        test.loc[test_blank, column] = fill_value
        imputation_rows.append(
            {
                "Column": column,
                "Rule": rule,
                "Fill value": f"`{fill_value}`",
                "Count behind it": count,
                "Tied values": ", ".join(f"`{value}`" for value in tied) if len(tied) > 1 else "none",
                "Train blanks filled": int(train_blank.sum()),
                "Test blanks filled": int(test_blank.sum()),
                "Share of train rows now holding it (%)": round(train[column].eq(fill_value).mean() * 100, 1),
            }
        )

    # --- Upper capping at the training 99th percentile ---
    capping_rows = []
    capped_examples = []
    for column in numeric_columns:
        train_values = train[column].astype(float)
        test_values = test[column].astype(float)
        cap = float(train_values.quantile(CAP_QUANTILE))
        for split_name, values in (("train", train_values), ("test", test_values)):
            frame = train if split_name == "train" else test
            for index in values.index[values > cap]:
                capped_examples.append(
                    {"Split": split_name, "Mushroom": frame.at[index, "name"], "Column": column,
                     "Original": values[index], "Capped to": round(cap, 3)}
                )
        capping_rows.append(
            {
                "Column": column,
                "Training 99th percentile (cap)": round(cap, 3),
                "Train values capped": int((train_values > cap).sum()),
                "Test values capped": int((test_values > cap).sum()),
                "Training max before": train_values.max(),
            }
        )
        train[column] = train_values.clip(upper=cap)
        test[column] = test_values.clip(upper=cap)

    if train[categorical_columns].eq("").any().any() or test[categorical_columns].eq("").any().any():
        raise RuntimeError("Blank categorical cells remain after imputation.")

    for path in (args.train_output, args.test_output, args.report_output):
        path.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(args.train_output, sep=";", index=False, encoding="utf-8-sig")
    test.to_csv(args.test_output, sep=";", index=False, encoding="utf-8-sig")

    report = (
        "# Task 2.2 training-fitted imputation and capping\n\n"
        f"Modes and caps were learned from the {len(train)} training rows and applied to both the training "
        f"and the {len(test)} test rows. No numeric column has blanks, so only categorical columns are imputed.\n\n"
        "## Categorical mode imputation\n\n"
        + markdown_table(pd.DataFrame(imputation_rows))
        + "\n\n## Numeric capping at the training 99th percentile\n\n"
        + markdown_table(pd.DataFrame(capping_rows))
        + "\n\n### Values that were capped\n\n"
        + markdown_table(pd.DataFrame(capped_examples))
        + "\n"
    )
    args.report_output.write_text(report, encoding="utf-8")

    print(markdown_table(pd.DataFrame(imputation_rows)))
    print()
    print(markdown_table(pd.DataFrame(capping_rows)))
    print()
    print(markdown_table(pd.DataFrame(capped_examples)))
    print(f"Wrote: {args.train_output}\nWrote: {args.test_output}\nWrote: {args.report_output}")


if __name__ == "__main__":
    main()
