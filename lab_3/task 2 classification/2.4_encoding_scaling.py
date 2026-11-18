"""Turn the prepared data into numbers (dummy columns) and bring numeric columns to the same scale.

Course steps covered: "Models like numbers" and "Bring data to the same scale".
Needed by distance-based models (KNN, K-Means); the disorder tree (Task 2.3) uses the
categories directly and does not need this step.

Rules (everything is learned from the training rows only, then applied to test):
1. Categorical columns -> one 0/1 dummy column per code, named `column=code`.
   A multi-valued cell such as `[f, x]` gets a 1 in both `cap-shape=f` and `cap-shape=x`.
   A code that appears only in the test rows has no column and is ignored.
2. Two-valued single-code columns (`[f]` / `[t]`) keep only the `=t` column: the `=f`
   column would be its exact opposite and would count the same feature twice in a distance.
3. Numeric midpoints -> log1p, then MinMax scaling to 0-1 using the training minimum and
   maximum, so they have the same range as the 0/1 columns. The dummy columns are not scaled.
4. Dummy columns that are identical (or constant) in the training rows are dropped,
   keeping the first column of each identical group.

The script also records why frequency encoding was not used: it maps many different
values to the same number (see the comparison table in the summary).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


TASK2_DIR = Path(__file__).parent
LAB3_DIR = TASK2_DIR.parent
DEFAULT_TRAIN_PATH = LAB3_DIR / "processed_data" / "2.2_train_prepared.csv"
DEFAULT_TEST_PATH = LAB3_DIR / "processed_data" / "2.2_test_prepared.csv"
DEFAULT_TRAIN_OUTPUT = LAB3_DIR / "processed_data" / "2.4_train_encoded.csv"
DEFAULT_TEST_OUTPUT = LAB3_DIR / "processed_data" / "2.4_test_encoded.csv"
DEFAULT_REPORT_PATH = TASK2_DIR / "2.4_encoding_summary.md"
# Kept in the output files so rows can be identified, but never used as model inputs.
NON_FEATURE_COLUMNS = ["family", "name", "class"]


def parse_tokens(cell: str) -> list[str]:
    """Split a canonical cell such as `[f, x]` into its codes `['f', 'x']`."""
    value = cell.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Unexpected categorical cell format: {cell!r}")
    return [token.strip() for token in value[1:-1].split(",") if token.strip()]


def is_binary_single_code(token_rows: list[list[str]]) -> bool:
    """True when every cell has exactly one code and the column only uses `f` and `t`."""
    return all(len(row) == 1 for row in token_rows) and {row[0] for row in token_rows} == {"f", "t"}


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    """Encode categorical columns, scale numeric columns, and write the encoded files and summary."""
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

    # Start the outputs with the identifying columns; feature columns are added below.
    train_out = train[NON_FEATURE_COLUMNS].copy()
    test_out = test[NON_FEATURE_COLUMNS].copy()
    train_features: dict[str, list[int]] = {}
    test_features: dict[str, list[int]] = {}

    # --- Step "Models like numbers": dummy columns per code ---
    encoding_rows = []
    frequency_rows = []
    for column in categorical_columns:
        train_tokens = [parse_tokens(cell) for cell in train[column]]
        test_tokens = [parse_tokens(cell) for cell in test[column]]
        # The list of codes (vocabulary) comes from the training rows only.
        vocabulary = sorted({token for row in train_tokens for token in row})
        binary = is_binary_single_code(train_tokens)
        # For an f/t column, keep only "=t": "=f" is always 1 - "=t" and adds no information.
        kept_codes = ["t"] if binary else vocabulary
        for code in kept_codes:
            name = f"{column}={code}"
            train_features[name] = [int(code in row) for row in train_tokens]
            test_features[name] = [int(code in row) for row in test_tokens]
        unseen = sum(1 for row in test_tokens for token in row if token not in vocabulary)
        encoding_rows.append(
            {
                "Column": column,
                "Codes in training rows": len(vocabulary),
                "Dummy columns created": len(kept_codes),
                "Note": "f/t column: only `=t` kept" if binary else "",
                "Test codes not seen in training (ignored)": unseen,
            }
        )
        # For the report: how frequency encoding would have represented the same column.
        counts = train[column].value_counts()
        frequency_rows.append(
            {
                "Column": column,
                "Distinct cell values": len(counts),
                "Distinct numbers after frequency encoding": counts.nunique(),
                "Values sharing the number 1/123": int((counts == 1).sum()),
            }
        )

    # --- Step "Bring data to the same scale": log1p + MinMax on numeric columns only ---
    scaling_rows = []
    for column in numeric_columns:
        train_log = np.log1p(train[column].astype(float))
        test_log = np.log1p(test[column].astype(float))
        # MinMax parameters are learned from the training rows only.
        low, high = float(train_log.min()), float(train_log.max())
        train_features[column] = ((train_log - low) / (high - low)).round(6).tolist()
        test_features[column] = ((test_log - low) / (high - low)).round(6).tolist()
        scaling_rows.append(
            {
                "Column": column,
                "Train min (original)": round(float(train[column].astype(float).min()), 3),
                "Train max (original)": round(float(train[column].astype(float).max()), 3),
                "log1p min": round(low, 4),
                "log1p max": round(high, 4),
                "Scaled test range": f"{min(test_features[column]):.3f} to {max(test_features[column]):.3f}",
            }
        )

    train_out = pd.concat([train_out, pd.DataFrame(train_features, index=train.index)], axis=1)
    test_out = pd.concat([test_out, pd.DataFrame(test_features, index=test.index)], axis=1)
    feature_names = list(train_features)
    dummy_names = [name for name in feature_names if name not in numeric_columns]

    # Course step "Remove duplicates" applied to the new columns: constant or identical columns.
    constant = [name for name in feature_names if train_out[name].nunique() == 1]
    # Identical dummy columns (same 0/1 values for every training row) carry the same
    # information; keeping all copies would count that information several times in a
    # distance. Keep the first column of each identical group and drop the others.
    duplicate_pairs = []
    dropped_duplicates = []
    seen: dict[tuple, str] = {}
    for name in dummy_names:
        key = tuple(train_out[name])
        if key in seen:
            duplicate_pairs.append(f"`{name}` (same as `{seen[key]}`)")
            dropped_duplicates.append(name)
        else:
            seen[key] = name
    train_out = train_out.drop(columns=dropped_duplicates + constant)
    test_out = test_out.drop(columns=dropped_duplicates + constant)
    feature_names = [name for name in feature_names if name not in dropped_duplicates + constant]
    dummy_names = [name for name in dummy_names if name not in dropped_duplicates + constant]

    for path in (args.train_output, args.test_output, args.report_output):
        path.parent.mkdir(parents=True, exist_ok=True)
    train_out.to_csv(args.train_output, sep=";", index=False, encoding="utf-8-sig")
    test_out.to_csv(args.test_output, sep=";", index=False, encoding="utf-8-sig")

    # --- Preview of the encoded dataframe (for the report) ---
    # How many of the final columns come from each original feature.
    source_of = {name: (name.split("=")[0] if "=" in name else name) for name in feature_names}
    columns_per_feature = (
        pd.Series(source_of).value_counts().reindex(categorical_columns + numeric_columns).dropna()
        .astype(int).rename_axis("Original feature").reset_index(name="Columns in encoded data")
    )
    # First rows of the training data: the original cap-shape cell next to its dummy columns,
    # the two kept f/t columns, and the three scaled size columns (94 columns do not fit on a page).
    cap_shape_columns = [name for name in feature_names if name.startswith("cap-shape=")]
    preview_columns = cap_shape_columns + ["does-bruise-or-bleed=t", "has-ring=t"] + numeric_columns
    preview = pd.concat(
        [train[["name", "family"]], train[["cap-shape"]].rename(columns={"cap-shape": "cap-shape (before)"}),
         train_out[preview_columns]],
        axis=1,
    ).head(6).round({column: 3 for column in numeric_columns})

    report = (
        "# Task 2.4 encoding and scaling\n\n"
        f"Input: {len(categorical_columns)} categorical + {len(numeric_columns)} numeric columns. "
        f"Output: {len(feature_names)} feature columns ({len(dummy_names)} dummy 0/1 columns + "
        f"{len(numeric_columns)} scaled numeric columns) for {len(train_out)} training and "
        f"{len(test_out)} test rows. `family`, `name` and `class` are kept for identification only.\n\n"
        "## Dummy columns per categorical column\n\n"
        + markdown_table(pd.DataFrame(encoding_rows))
        + "\n\n## Numeric scaling (log1p, then MinMax fitted on training rows)\n\n"
        + markdown_table(pd.DataFrame(scaling_rows))
        + "\n\n## Checks on the new columns (course step: remove duplicates)\n\n"
        f"Constant columns in training (dropped): {len(constant)}"
        + (f" ({', '.join(constant)})" if constant else "")
        + f". Dummy columns identical to an earlier column in training (dropped): {len(duplicate_pairs)}"
        + (f": {'; '.join(duplicate_pairs)}" if duplicate_pairs else "")
        + ".\n\n## Encoded dataframe\n\n"
        f"Training data: {len(train_out)} rows x {len(feature_names)} feature columns; test data: "
        f"{len(test_out)} rows x {len(feature_names)} feature columns.\n\n"
        + markdown_table(columns_per_feature)
        + "\n\nFirst rows of the training data (selected columns):\n\n"
        + markdown_table(preview)
        + "\n\n## Why not frequency encoding\n\n"
        "Frequency encoding replaces a value by how often it occurs. Different values with the same "
        "count get the same number, so the model can no longer tell them apart:\n\n"
        + markdown_table(pd.DataFrame(frequency_rows))
        + "\n"
    )
    args.report_output.write_text(report, encoding="utf-8")

    print(markdown_table(pd.DataFrame(encoding_rows)))
    print()
    print(markdown_table(pd.DataFrame(scaling_rows)))
    print()
    print(f"Feature columns: {len(feature_names)} ({len(dummy_names)} dummy + {len(numeric_columns)} numeric)")
    print(markdown_table(columns_per_feature))
    print()
    print(markdown_table(preview))
    print(f"Constant: {constant}")
    print(f"Identical dummy pairs: {duplicate_pairs}")
    print(f"Wrote: {args.train_output}\nWrote: {args.test_output}\nWrote: {args.report_output}")


if __name__ == "__main__":
    main()
