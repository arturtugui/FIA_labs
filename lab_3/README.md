# FIA LAB 3

1. Exploratory data analysis

## Step 1.1 — Load and inspect the catalogue

- the initial data.csv has in the 1st row all the column names and all the subsequent rows dont seem to have multiple entries per cell

- so i made a script that puts each ; in its own cell

- `processed_data/1_1_readable_catalogue.csv` - one row per mushroom and one column per
  field, so the data can be inspected in a spreadsheet without changing the
  original semicolon-delimited source.


## Step 1.2 — Unique values and missingness

* 1.2.1 row analysis

Unique values below mean distinct, nonblank raw cell contents. Bracketed values
such as `[x, f]` are counted as one cell value here. Empty-cell percentages for
columns use all 173 rows.

| Statistic | family | name | class | cap-diameter | cap-shape | Cap-surface | cap-color | does-bruise-or-bleed | gill-attachment | gill-spacing | gill-color | stem-height | stem-width | stem-root | stem-surface | stem-color | veil-type | veil-color | has-ring | ring-type | Spore-print-color | habitat | season |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Unique values | 23 | 173 | 2 | 51 | 27 | 40 | 67 | 2 | 8 | 3 | 59 | 46 | 48 | 5 | 14 | 41 | 1 | 7 | 2 | 13 | 8 | 21 | 10 |
| Empty cells (%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 23.1% | 0.0% | 0.0% | 16.2% | 41.0% | 0.0% | 0.0% | 0.0% | 84.4% | 62.4% | 0.0% | 94.8% | 87.9% | 0.0% | 4.0% | 89.6% | 0.0% | 0.0% |

Columns with fewer than 5 unique cell values:

| Column | Values |
|---|---|
| class | `p`, `e` |
| does-bruise-or-bleed | `[f]`, `[t]` |
| gill-spacing | `[c]`, `[d]`, `[f]` |
| veil-type | `[u]` |
| has-ring | `[t]`, `[f]` |

* 1.2.2 columns types

For this analysis, `name` is the identifier, `family` is the classification target, `class` is a separate analysis label, and the remaining 20 mushroom-description columns are features.

* 1.2.3 row analysis

The following table groups rows by the percentage of their 23 columns that are
empty. The bands include their lower bound and exclude their upper bound, except
for the final band. Exactly 0% is also shown separately.

| Empty columns per row (% of 23) | Number of rows |
|---|---:|
| Exactly 0% | 0 |
| 0–<20% | 50 |
| 20–<40% | 123 |
| 40–<60% | 0 |
| 60–<80% | 0 |
| 80–100% | 0 |

Rows have 2–8 empty columns, averaging 5.03 empty columns per row.

* 1.2.4 row duplicates

I checked for exact duplicate rows, repeated `name` identifiers, and repeated
mushroom feature profiles (the 20 description columns, excluding `family`,
`name`, and `class`). All three checks found 0 duplicates. A repeated identifier
is one kind of duplicate, but identical records or feature profiles are separate
checks.

## Step 1.3 — Missingness patterns

Missingness was analysed across the 20 mushroom-description features; `family`,
`name`, and `class` were excluded from row-level feature counts. A blank is
treated as an unrecorded value at this stage. These plots describe the pattern
but do not establish why a value is blank.

### Missing feature values per mushroom

![Histogram of empty feature columns per mushroom](<task 1 eda/plots/1.3_01_missingness_per_row.png>)

**Figure 1.** The number of empty feature columns ranges from 2 to 8 per
mushroom, with a mean of 5.03. No row is almost entirely blank: even the most
incomplete rows have 12 of the 20 feature values recorded. The most common
count is 5 empty feature columns (65 mushrooms).

Out of the 20 feature columns, 9 have at least one blank cell; the other 11 have no blanks and are therefore omitted from the missingness heatmaps.

### Co-occurrence of blank values

![Heatmap of feature blank co-occurrence](<task 1 eda/plots/1.3_02_missingness_cooccurrence.png>)

**Figure 2.** Blanks frequently occur together in the sparse veil and spore
features: `veil-type` and `veil-color` are both blank in 152 rows;
`veil-type` and `Spore-print-color` are both blank in 147 rows. The diagonal
shows each feature's total blank count. These are raw joint counts, so large
values partly reflect that the individual columns are often blank; co-occurrence
alone does not show whether the relationship is stronger than expected by
chance or explain why values are missing.

### Missingness by family

![Heatmap of feature missingness by family](<task 1 eda/plots/1.3_03_missingness_by_family.png>)

**Figure 3.** Missingness varies substantially across families. For example,
`veil-type` is recorded for all eight Amanita entries (0% blank) but is blank
for nearly all other families; the Markdown table in `task 1 eda/plots/` gives
family sample sizes and exact percentages. This suggests blanks are not evenly
distributed across the catalogue. The plot cannot determine whether that
pattern reflects biology, recording practices, or both. Rates for families
with very few examples are especially unstable.

### Missingness by class

![Heatmap of feature missingness by class](<task 1 eda/plots/1.3_04_missingness_by_class.png>)

**Figure 4.** The `e` and `p` groups have broadly similar blank rates for many
features. Some differences remain—for example, `stem-surface` is blank in
68.8% of `e` rows and 57.3% of `p` rows, while `Spore-print-color` is blank in
93.5% and 86.5%, respectively. These descriptive differences do not establish
a meaningful association, particularly with the small dataset.

### Follow-up: pairwise missingness after accounting for family

To check whether two features are blank together more often than expected
within the same families, I compared their observed co-occurrence with the
co-occurrence expected if their missingness were independent within each family.

![Heatmap of pairwise blank co-occurrence after accounting for family](<task 1 eda/plots/1.3_05_family_adjusted_cooccurrence.png>)

**Figure 5.** Each cell shows the observed joint blank rate minus the expected
joint blank rate within families, in percentage points. The largest absolute
deviation is +3.34 percentage points for `gill-attachment` and `stem-surface`.
The small deviations indicate that, after accounting for each feature's blank
rate within each family, no pair has a large extra co-occurrence in this
dataset. These are descriptive comparisons, not significance tests; see the
[full pairwise table](<task 1 eda/plots/1.3_05_family_adjusted_cooccurrence.md>).

### Follow-up: blanks in related features

The cross-tabs below compare blank status in one column with the value in a
related column. Percentages are calculated within each row group.

| `has-ring` value | Mushrooms | `ring-type` blank | `ring-type` recorded | Blank within group |
|---|---:|---:|---:|---:|
| `[f]` | 130 | 0 | 130 | 0.0% |
| `[t]` | 43 | 7 | 36 | 16.3% |

All 7 blank `ring-type` values occur when `has-ring` is `[t]`; none occur when
it is `[f]`.

| `veil-type` status | Mushrooms | `veil-color` blank | `veil-color` recorded | Blank within group |
|---|---:|---:|---:|---:|
| Blank | 164 | 152 | 12 | 92.7% |
| Recorded | 9 | 0 | 9 | 0.0% |

All 9 rows with recorded `veil-type` also have `veil-color` recorded. However,
12 rows have a recorded `veil-color` while `veil-type` is blank. The full
cross-tabs are in [1.3_06_related_feature_blanks.md](<task 1 eda/plots/1.3_06_related_feature_blanks.md>).

These relationships show how blanks align with recorded values, but cannot
establish whether a blank means “not applicable” or “not recorded.” Keep the
source values unchanged, and do not drop a column solely because its overall
blank percentage is high; make that decision feature by feature and document
the evidence.

The PNGs remain in `task 1 eda/plots/`; matching `.md` files in that folder
contain the underlying values for each figure.


