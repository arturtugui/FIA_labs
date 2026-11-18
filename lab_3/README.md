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

## Step 1.4 — Column types and distributions

The table records each column's role and variable type. The letter codes are
treated as categorical values; their biological meanings are not assumed
because no data dictionary was supplied.

| Column | Role | Variable type | Notes |
|---|---|---|---|
| family | Classification target | Nominal categorical | Predicted in Tasks 2–4. |
| name | Identifier | Nominal text | Species name; not a model feature. |
| class | Analysis label | Binary categorical | Separate label for analysis and cluster comparison. |
| cap-diameter | Feature | Numeric interval | Range; midpoint used for the numeric distribution plot. |
| cap-shape | Feature | Multi-valued categorical | Cell may list more than one nominal code. |
| Cap-surface | Feature | Multi-valued categorical | May list multiple codes; some cells are blank. |
| cap-color | Feature | Multi-valued categorical | Cell may list more than one nominal code. |
| does-bruise-or-bleed | Feature | Binary categorical | Observed values are `[f]` and `[t]`. |
| gill-attachment | Feature | Multi-valued categorical | May list multiple codes; some cells are blank. |
| gill-spacing | Feature | Single-valued categorical | One nominal code per nonblank cell; no order assumed. |
| gill-color | Feature | Multi-valued categorical | Cell may list more than one nominal code. |
| stem-height | Feature | Numeric interval | Range; midpoint used for the numeric distribution plot. |
| stem-width | Feature | Numeric interval | Range; midpoint used for the numeric distribution plot. |
| stem-root | Feature | Single-valued categorical | One nominal code per nonblank cell; many cells are blank. |
| stem-surface | Feature | Multi-valued categorical | May list multiple codes; some cells are blank. |
| stem-color | Feature | Multi-valued categorical | Cell may list more than one nominal code. |
| veil-type | Feature | Single-valued categorical | One observed code; most cells are blank. |
| veil-color | Feature | Multi-valued categorical | May list multiple codes; many cells are blank. |
| has-ring | Feature | Binary categorical | Observed values are `[t]` and `[f]`. |
| ring-type | Feature | Multi-valued categorical | May list multiple codes; a few cells are blank. |
| Spore-print-color | Feature | Multi-valued categorical | May list multiple codes; many cells are blank. |
| habitat | Feature | Multi-valued categorical | Cell may list more than one nominal code. |
| season | Feature | Multi-valued categorical | Cell may list more than one nominal code. |

### Family distribution

![Mushroom counts by family](<task 1 eda/plots/1.4_02_family_distribution.png>)

**Figure 6.** The family sizes are imbalanced: Tricholoma has 43 mushrooms
and Russula has 27, while six families have only one mushroom each. This
imbalance will matter when choosing and evaluating family classifiers. The
[family count table](<task 1 eda/plots/1.4_02_family_distribution.md>) lists all 23 counts.

### Class distribution

![Mushroom counts by class code](<task 1 eda/plots/1.4_03_class_distribution.png>)

**Figure 7.** The recorded class counts are 96 `p` and 77 `e`. This is a
moderate imbalance. The plot shows the codes as recorded and does not assign
them a biological meaning.

### Class composition by family

![Class composition within each family](<task 1 eda/plots/1.4_04_class_by_family.png>)

**Figure 8.** The class mix differs across families. For example, Tricholoma
has 23 `e` and 20 `p` mushrooms, while Russula has 11 `e` and 16 `p`; some
families contain only one recorded class. The single-mushroom families cannot
support a reliable conclusion about their class proportions. See the [family-by-class table](<task 1 eda/plots/1.4_04_class_by_family.md>) for all counts.

### Numeric ranges by class

![Numeric range midpoints by class](<task 1 eda/plots/1.4_05_numeric_by_class.png>)

This figure uses **boxplots** to compare the distributions of three numeric
measurements between the recorded class codes. Each panel is one measurement;
the x-axis shows the class code and the y-axis shows the range midpoint in the
source units. Each small gray dot represents one mushroom. Dots are shifted
slightly sideways only to make overlapping observations easier to see.

In each box, the horizontal line marks the **median**. The box covers the
middle half of the observations, from the 25th percentile to the 75th
percentile. The **whiskers** extend to the most extreme observations within
1.5 times the box height (the interquartile range); dots beyond them are
flagged by the boxplot rule as potential outliers. That flag does not mean the
measurement is wrong or should be removed.

We use these plots to compare typical measurement values and their spread
between the two class groups, while also seeing each mushroom's value. Each
bracketed range was represented by its midpoint; a single-value entry was
treated as a zero-width range. The median cap diameter is 6.5 for `e` and 5.0
for `p`; median stem height is 6.0 and 5.5; median stem width is 12.5 and 7.5,
respectively. The distributions overlap, so these measurements alone do not
clearly separate the class codes. The plots also show large values (up to 50
for cap diameter, 25 for stem height, and 70 for stem width); these need review
as possible outliers, not automatic removal. The [numeric summary table](<task 1 eda/plots/1.4_05_numeric_by_class.md>) gives descriptive statistics by class.

The type table and plot data tables are generated by
`task 1 eda/1.4_column_types_distributions.py`.

## Step 1.5 — Numeric range checks and representation

The three numeric columns store intervals as `[minimum, maximum]`. The
`1.5_numeric_ranges.py` script parsed these intervals, treated a single value
as a zero-width range (minimum equals maximum), checked for blanks, reversed
ranges, zeros and extreme endpoints, and calculated midpoint and width. It
saved the derived columns to
[`processed_data/1.5_numeric_range_features.csv`](processed_data/1.5_numeric_range_features.csv)
and wrote the audit tables beside the figures in `task 1 eda/plots/`.

![Numeric range distributions](<task 1 eda/plots/1.5_02_numeric_range_distributions.png>)

**Figure 9. How to read it:** Each panel is one measurement. The horizontal
axis shows which values are being summarized: the minimum endpoint, maximum
endpoint, or midpoint. The vertical axis gives the actual measurement value in
the source units. In each box, the horizontal line is the median; the box
covers the middle half of the mushrooms' values. The whiskers show the typical
range under the boxplot rule, and separate points are possible outliers. For
example, in the cap-diameter panel, compare the three boxes' vertical
positions to see whether minimums, maximums and midpoints tend to be smaller
or larger. These boxplots summarize the distributions; they do not show the
count in each measurement interval or connect the minimum, maximum and
midpoint belonging to an individual mushroom. The distributions are
concentrated at smaller measurements, with a few large observations. The
largest recorded maximum is 50 for Dryad's Saddle cap diameter, 35 for Parasol
Mushroom stem height and 100 for Cep stem width. The audit found no blank or
reversed numeric intervals. There are three rows with zero stem-height and
stem-width values (Soft Slipper Toadstool, Hairy Stereum and Silver Leaf
Fungus); these are flagged for interpretation, not removed as presumed errors.

![Correlation of numeric range endpoints](<task 1 eda/plots/1.5_03_endpoint_correlations.png>)

**Figure 10.** Spearman correlations between each measurement's minimum and
maximum are 0.938 for cap diameter, 0.829 for stem height and 0.960 for stem
width. Spearman correlation compares the rank order of two measurements, so
these high positive values mean mushrooms with larger minimums generally also
have larger maximums. Because the endpoints are strongly correlated, the derived modelling
representation uses midpoint and width for each measurement, preserving both
typical size and range spread without entering both endpoints directly. This
is a representation choice for later modelling, not a claim that the resulting
features are independent.

## Step 1.7 — Association analysis

These plots compare features with one another and with `family` and `class`.
They can show patterns worth checking in later modelling, but they do not show
that one feature causes another. The detailed values are in matching
`1.7_*.md` tables in `task 1 eda/plots/`.

![Grouped categorical feature associations](<task 1 eda/plots/1.7_01_categorical_associations.png>)

**Figure 11.** Cramér's V ranges from 0 (no association) to 1 (perfect
association); darker off-diagonal cells indicate stronger relationships. Each
cell averages the associations across token pairs. The diagonal is set to 0
because it compares a column with itself, so it does not mean “no association.”
Most different-column relationships are weak. The strongest average is
`has-ring` with `ring-type` (0.361), followed by `veil-type` with `has-ring`
(0.340). These pairs may contain overlapping information, but the plot does
not show that one feature causes another.

![Spearman correlations among numeric features](<task 1 eda/plots/1.7_02_numeric_spearman.png>)

**Figure 12.** The plot compares the six numeric midpoint and width columns.
Values closer to 1 mean two columns tend to be high or low together. The
strongest relationships include cap-diameter midpoint with width (0.897), stem-
width midpoint with width (0.886), and cap-diameter midpoint with stem-width
midpoint (0.882). This suggests some numeric columns carry overlapping size
information; the plot does not show that one measurement causes another.

![Categorical token association with family and class](<task 1 eda/plots/1.7_03_categorical_feature_target_mi.png>)

**Figure 13.** Higher values mean a token gives more information about the
label. The strongest shown tokens for `family` are `gill-attachment=p`
(0.424 bits), `has-ring=t` (0.394), and `ring-type=f` (0.392). For `class`,
the highest token score is much smaller: `stem-color=w` at 0.041 bits. In this
dataset, these categorical values appear more informative about family than
class, but the plot alone cannot establish how well they will predict either
label.

![Numeric midpoint association with family and class](<task 1 eda/plots/1.7_04_numeric_feature_target_eta.png>)

**Figure 14.** Higher values mean the numeric measurements differ more across
the groups of a label. For `family`, eta is 0.509 for cap diameter, 0.600 for
stem height and 0.578 for stem width. For `class`, the values are lower at
0.186, 0.127 and 0.201, respectively. The numeric measurements therefore
show clearer group differences by family than by class in this dataset, though
this alone does not guarantee accurate predictions.

## Step 1.8 — Values in columns that contain blanks

The `1.8_missing_value_distributions.py` script counts blanks and the
frequencies of complete nonblank cell values. Multi-valued cells such as
`[g, h]` remain one complete value; they are not split into tokens.

| Column | Blank rows | Blank (%) | Nonblank rows | Most frequent complete cell value(s) | Frequency |
|---|---:|---:|---:|---|---:|
| Cap-surface | 40 | 23.1% | 133 | `[y]` | 14 |
| gill-attachment | 28 | 16.2% | 145 | `[a]` | 32 |
| gill-spacing | 71 | 41.0% | 102 | `[c]` | 70 |
| stem-root | 146 | 84.4% | 27 | `[b]`; `[s]` (tie) | 9 each |
| stem-surface | 108 | 62.4% | 65 | `[s]` | 15 |
| veil-type | 164 | 94.8% | 9 | `[u]` | 9 |
| veil-color | 152 | 87.9% | 21 | `[w]` | 15 |
| ring-type | 7 | 4.0% | 166 | `[f]` | 137 |
| Spore-print-color | 155 | 89.6% | 18 | `[k]` | 5 |

The detailed table of every complete cell value and its count is in
[`1.8_missing_value_distributions.md`](<task 1 eda/plots/1.8_missing_value_distributions.md>).
For `veil-type`, `[u]` is the only observed value and occurs in nine rows;
filling all 164 blanks with it would make the column constant. The other
sparse columns also have modes based on few observed rows, so mode imputation
would repeat those values many times. The three numeric range columns have no
blanks, so median imputation is not needed. Missing values remain unchanged at
this step; the final handling is decided in Step 1.11 (the sparse columns are
dropped) and Task 2.2 (the remaining blanks are filled with training modes).

## Step 1.9 — Feature value frequencies for tier design

The `1.9_feature_value_frequencies.py` script calculates each value's
frequency as `count / total observed rows for that feature`. For a multi-valued
categorical cell, each token is counted separately, at most once per row. Its
denominator is the nonblank rows in that column; thus, percentages for one
column can sum above 100% when rows list multiple tokens. For numeric ranges,
the script uses the previously derived midpoint and width, and counts each
exact value among 173 rows. It excludes `name`, `family`, and `class` so the
table covers only prediction features. For example, a token appearing in 17 of
145 nonblank `gill-attachment` rows has a frequency of 11.72%. A lower
frequency means that observed value is less common within its feature; this
table is input for tier design, not the tier definition itself.

The full table is available as
[`1.9_feature_value_frequencies.md`](<task 1 eda/plots/1.9_feature_value_frequencies.md>)
and [`1.9_feature_value_frequencies.csv`](processed_data/1.9_feature_value_frequencies.csv).

## Step 1.10 — Rarity score and provisional tiers

The `1.10_rarity_tier_scoring.py` script applies the agreed point bands to
feature values, sums the observed feature contributions, and adjusts the sum
to a common 19-feature scale to reduce the effect of different amounts of
missing data. The value-point rule is:

| Value frequency within its feature | Points |
|---|---:|
| Occurs once in the dataset (or falls alone in a numeric bin) | 10 |
| Otherwise, less than 1% | 8 |
| Otherwise, less than 5% | 5 |
| Otherwise, less than 30% | 1 |
| 30% or more | 0 |

For a cell listing multiple categorical tokens, their points are averaged, so
listing more tokens does not automatically increase a species' score. Exact
numeric midpoint and width values produced many singletons, so each is first
placed in one of ten equal-width bins; the midpoint and width points are then
averaged into one contribution per original numeric measurement. `name`,
`family`, and `class` are excluded. `veil-type` is excluded from this
provisional score in line with the planned removal of the only feature above
90% missing; the source data has not been changed. Missing values are not
imputed for scoring; missing feature contributions are omitted and the sum is
scaled by the number of observed scored features.

The species are ranked by this score with a target split of approximately 70%
Common, 25% Rare, and 5% Legendary. Equal scores stay together at the cutoffs.
This produced **122 Common (70.5%), 42 Rare (24.3%), and 9 Legendary (5.2%)**.
The closeness to the target is good; the one-species shift between Common and
Rare comes from keeping tied scores together.

| Tier | Adjusted score range | Median score |
|---|---:|---:|
| Common | 3.353–13.656 | 8.583 |
| Rare | 13.722–24.775 | 16.678 |
| Legendary | 25.446–36.643 | 27.708 |

The nine Legendary species are Parasol Mushroom, Horn of Plenty, Cep, Silver
Leaf Fungus, Shaggy Ink Cap, Fuzzy Polypore, Dryad's Saddle, Purple
Cortinarius, and Wood Blewit. They span seven families and include six `e`
and three `p` class labels, so this result is not simply assigning a whole
family or class to one tier.

As a completeness check, the adjusted score has a Spearman correlation of
−0.200 with the number of missing feature cells: species with more missing
values tend to score somewhat lower, even after normalization. This remaining
relationship should be checked before treating the tiers as final. The
complete per-species scores, family/class tables, numeric bin counts, and
individual Legendary scores are in
[`1.10_rarity_scoring.md`](<task 1 eda/plots/1.10_rarity_scoring.md>) and
[`1.10_rarity_scores.csv`](processed_data/1.10_rarity_scores.csv).

## Step 1.11 — Fixed-rule preprocessing

The `1.11_preprocessing.py` script applies the preprocessing rules that do not
learn anything from the data, so they can be applied to all 173 rows before
the train/test split. It writes
[`processed_data/1.11_clean.csv`](processed_data/1.11_clean.csv) (173 rows ×
19 columns); the full log is in
[`1.11_preprocessing.md`](<task 1 eda/plots/1.11_preprocessing.md>).

| # | Issue found | Where it was found | Decision | Why |
|---|---|---|---|---|
| 1 | Mixed column-name case (`Cap-surface`, `Spore-print-color`) | Step 1.2 | Lowercase all column names | One naming convention avoids lookup mistakes. |
| 2 | The same set of codes is written in different orders or spacings, e.g. `[x, f]` / `[f, x]`, `[n, w]` / `[w, n]` / `[n ,w]` | Checked here | Rewrite every categorical cell as a sorted, de-duplicated set (375 cells rewritten) | A cell lists codes that all apply, so order carries no meaning. Without this, one shape would count as several different values (cap-color: 67 → 58 distinct values, cap-shape: 27 → 25). |
| 3 | Numeric features are stored as `[min, max]` ranges | Step 1.5 | Replace each range by its midpoint; a single value is a zero-width range | Min and max are strongly correlated (Spearman 0.83–0.96, Step 1.5), so one number per measurement keeps the typical size. |
| 4 | `veil-type` (94.8%), `spore-print-color` (89.6%), `veil-color` (87.9%) and `stem-root` (84.4%) are mostly blank | Step 1.2 | Drop the columns more than 80% blank | Filling 84–95% of a column would mostly invent values (Step 1.8). Cost: `veil-type = [u]` almost identifies Amanita (8 of its 9 rows, Step 1.3), so that signal is knowingly given up. |
| 5 | Blanks remain in `cap-surface` (23.1%), `gill-attachment` (16.2%), `gill-spacing` (41.0%), `stem-surface` (62.4%) and `ring-type` (4.0%) | Step 1.2 | Kept blank here; filled with modes in Task 2.2 | A mode is learned from the data, so it must be learned from the training rows only. |
| 6 | Large values (e.g. Dryad's Saddle cap 50, Cep stem width 70) and zeros for stem-less fungi | Steps 1.4–1.5 | Kept here; large values capped at the training 99th percentile in Task 2.2; zeros kept | A cap is learned from the data (training rows only). The zeros are real (no stem), not errors. |
| 7 | `has-ring = [t]` with `ring-type = [f]` (7 rows), `veil-color` without `veil-type` (12 rows) | Step 1.3 | Left as recorded (the veil columns are dropped anyway) | Changing them would mean guessing values. |

The rarity tiers from Step 1.10 were computed on the raw catalogue and are not
recomputed from this cleaned file.


## Task 2.1 — Family-stratified train/test split

The script `task 2 classification/2.1_family_stratified_split.py` splits the
Step 1.11 cleaned file into an approximately 70/30 holdout with random seed 42.
Each family with at least two mushrooms appears in both sets; singleton
families stay in train so the model can see those labels. The resulting split
has **123 training rows (71.1%)** and **50 test rows (28.9%)**. Train contains
all 23 families; test contains 17 because the six singleton-family rows cannot
appear in both sets. Since the rows and their order did not change during
cleaning, the split contains the same mushrooms as the earlier raw-data split.

This means the test set cannot evaluate how well the model generalizes to
those six singleton families. Blanks are still blank in these files. The
family-by-family counts are in
[`2.1_split_summary.md`](<task 2 classification/2.1_split_summary.md>), and
the split files are [`2.1_train.csv`](processed_data/2.1_train.csv) and
[`2.1_test.csv`](processed_data/2.1_test.csv). This is one fixed holdout, not
a repeated cross-validation result.

## Task 2.2 — Training-fitted imputation and outlier capping

The script `task 2 classification/2.2_train_fitted_imputation_capping.py`
learns the fill values and the caps from the **123 training rows only**, then
applies the same values to train and test. Learning them from all 173 rows
would let the test mushrooms influence the training data (data leakage).
Outputs: [`2.2_train_prepared.csv`](processed_data/2.2_train_prepared.csv),
[`2.2_test_prepared.csv`](processed_data/2.2_test_prepared.csv) and
[`2.2_preparation_summary.md`](<task 2 classification/2.2_preparation_summary.md>).

**Missing values.** No numeric column has blanks (Step 1.5), so only
categorical columns are filled. Each blank is replaced by the most frequent
complete cell in the training rows (after the Step 1.11 sorting, so `[f, x]`
and `[x, f]` count as one value).

| Column | Fill value | Training rows behind it | Blanks filled (train / test) | Train rows holding it afterwards |
|---|---|---:|---:|---:|
| cap-surface | `[y]` | 11 | 27 / 13 | 30.9% |
| gill-attachment | `[a]` | 23 | 17 / 11 | 32.5% |
| gill-spacing | `[c]` | 52 | 50 / 21 | 82.9% |
| stem-surface | `[s]` | 14 | 73 / 35 | 70.7% |
| ring-type | `[z]` | 4 | 4 / 3 | 6.5% |

`ring-type` uses a different rule. All its blanks occur with `has-ring = [t]`
(Step 1.3), while its overall mode `[f]` means no ring, so filling with `[f]`
would create new contradictions. The fill value is therefore the most frequent
ring type among training rows with `has-ring = [t]`, ignoring `[f]`.

Limitation: `stem-surface` is 62.4% blank, so mode imputation turns `[s]`,
observed in only 14 training rows, into the value of 70.7% of training rows.
This was accepted to keep the column; models may treat `[s]` as more typical
than the recorded data shows.

**Outliers.** The large values flagged in Steps 1.4–1.5 are real mushrooms, so
they are not removed. Instead, each numeric midpoint is capped at the training
99th percentile, which only lowers the most extreme values. No lower cap is
needed: the minimum values are 0 (stem-less fungi), which are real.

| Midpoint column | Cap (train 99th percentile) | Capped values |
|---|---:|---|
| cap-diameter-midpoint | 19.0 | Dryad's Saddle 50 → 19 |
| stem-height-midpoint | 18.67 | Parasol Mushroom 25 → 18.67, Shaggy Ink Cap 19 → 18.67 |
| stem-width-midpoint | 47.8 | Cep 70 → 47.8, Horn of Plenty 50 → 47.8 |

All five capped values are in the training set; no test value exceeded a cap.

## Task 2.3 — Multi-way decision tree using disorder

The script `task 2 classification/decision tree/2.3_disorder_decision_tree.py`
builds the tree as it was done in class. The **disorder** of a set of
mushrooms is

`D = −Σ pᵢ · log₂(pᵢ)`

where `pᵢ` is the share of family `i` in the set. `D = 0` when the set is
homogeneous (one family). For every possible question, the mushrooms are split
by their answer and the **average disorder** is computed:

`average D = Σ_branches (n_branch / n) · D(branch)`

The question with the least average disorder is asked. Each branch is then
handled the same way using only the mushrooms that reached it, until every
branch is homogeneous.

- **Categorical question:** one branch per complete cell value present at that
  node. Mushrooms listing `[x]`, `[f]` and `[f, x]` go to three different
  branches, so a question is not limited to two answers.
- **Numeric question:** `midpoint <= t?`, where `t` splits the mushrooms at
  that node as evenly as possible into two groups. Because `t` depends on the
  mushrooms at the node, the same column can be asked again lower in the tree.

The 16 inputs are the 13 categorical columns kept in Step 1.11 and the three
numeric midpoints; `family` is the target, and `name` and `class` are not used.

**Root question.** The 123 training mushrooms have disorder **3.7216** (23
families). The average disorder of each first question:

| Question | Branches | Average disorder |
|---|---:|---:|
| What is gill-color? | 41 | **1.5003** |
| What is cap-color? | 44 | 1.8076 |
| What is cap-surface? | 34 | 1.9284 |
| What is cap-shape? | 23 | 2.0521 |
| What is gill-attachment? | 8 | 2.2276 |
| … (11 more, up to) Is stem-height-midpoint <= 6.25? | 2 | 3.4633 |

`gill-color` is asked first. Its largest branch, `[w]`, holds 24 mushrooms from
6 families (disorder 2.1379); many other branches hold a single mushroom and
are already homogeneous. The full candidate list and the per-branch
calculation are in
[`2.3_tree_summary.md`](<task 2 classification/decision tree/2.3_tree_summary.md>).

**Resulting tree.** 25 questions, 114 leaves, maximum depth 3. Every leaf is
homogeneous, so the tree classifies **all 123 training mushrooms correctly
(100%)**. No two training mushrooms have identical features but different
families, so this was always possible. The full tree is in
[`2.3_tree.txt`](<task 2 classification/decision tree/2.3_tree.txt>).

### Results

| Data | Mushrooms | Correctly classified | Accuracy |
|---|---:|---:|---:|
| Training (used to build the tree) | 123 | 123 | **100.0%** |
| Test (never seen by the tree) | 50 | 15 | **30.0%** |

For comparison, always guessing the most common family (Tricholoma) gets
30/123 = **24.4%** on training and 13/50 = **26.0%** on test. The tree is only
4 percentage points better than this guess on unseen mushrooms.

Accuracy counts every mushroom equally, so the many Tricholoma mushrooms
dominate it. Macro F1 gives every family the same weight instead: the tree
scores **0.190** on test and the always-Tricholoma guess scores **0.024**
(1.0 would be perfect).

### Why training is 100% but test is only 30%

The tree keeps asking questions until every branch has a single family, so it
always gets the training mushrooms right. It does this by memorising them
rather than learning general rules. Average disorder prefers questions with
many answers: `gill-color` splits the 123 training mushrooms into 41 branches,
many with one mushroom each, and a one-mushroom branch always has disorder 0.
That is why it was chosen first, and why no numeric question is used anywhere
in the tree.

A test mushroom often has an answer that no training mushroom had, for example
a `gill-color` combination that never appeared in training. There is no branch
for it, so the tree stops and guesses the most common family at that node.

| What happened to the test mushroom | Mushrooms | Correct | Accuracy |
|---|---:|---:|---:|
| Followed a full path down to a leaf | 15 | 4 | 26.7% |
| Reached an answer with no branch, so the node's most common family was used | 35 | 11 | 31.4% |
| **All test mushrooms** | **50** | **15** | **30.0%** |

Per-family scores and individual predictions are in
[`2.3_tree_summary.md`](<task 2 classification/decision tree/2.3_tree_summary.md>)
and [`2.3_test_predictions.csv`](<task 2 classification/decision tree/2.3_test_predictions.csv>).

## Task 2.4 — Encoding and scaling (models like numbers, same scale)

KNN (and later K-Means) compares mushrooms by distance, and a distance can
only be computed between numbers. The disorder tree (Task 2.3) uses the
categories directly, so it does not need this step. The script
`task 2 classification/2.4_encoding_scaling.py` reads the Task 2.2 prepared
files and writes [`2.4_train_encoded.csv`](processed_data/2.4_train_encoded.csv)
and [`2.4_test_encoded.csv`](processed_data/2.4_test_encoded.csv). As in Task
2.2, everything is learned from the 123 training rows and then applied to the
50 test rows. Details are in
[`2.4_encoding_summary.md`](<task 2 classification/2.4_encoding_summary.md>).

### Categorical columns → dummy columns

Each code becomes its own 0/1 column, named `column=code`. A cell that lists
several codes gets a 1 in each of them, so `cap-shape = [f, x]` gives
`cap-shape=f = 1` and `cap-shape=x = 1`. This also keeps the overlap between
`[f, x]` and `[x]`: both have a 1 in `cap-shape=x`.

- The list of codes comes from the training rows. One `stem-color` code that
  appears only in a test mushroom has no column and is ignored.
- `does-bruise-or-bleed` and `has-ring` only take the values `[f]` and `[t]`,
  so only the `=t` column is kept. The `=f` column would always be its exact
  opposite and would count the same information twice in a distance.
- LabelEncoder / OrdinalEncoder were not used: numbering colours 1, 2, 3 would
  make the model think colour 2 lies between colours 1 and 3.

**Why not frequency encoding.** Frequency encoding replaces each value by how
often it occurs. In the training rows, many different values occur equally
often and would get the same number:

| Column | Different values | Different numbers after frequency encoding | Values that would all become 1/123 |
|---|---:|---:|---:|
| cap-color | 44 | 9 | 27 |
| gill-color | 41 | 10 | 23 |
| cap-surface | 34 | 8 | 17 |
| cap-shape | 23 | 9 | 8 |

For example, `cap-color = [e, o]` and `[g, w]` would become the same number,
so the model could not tell them apart. The distance would also measure how
*common* a value is rather than how *similar* two mushrooms are. Frequency
encoding is useful when a column has thousands of categories; here dummy
columns give a manageable number of columns.

### Removing duplicate columns

Following the course step "remove duplicates", the new columns were checked:

| Dropped column | Identical to (kept) | Mushrooms with a 1 |
|---|---|---|
| `gill-spacing=f` | `gill-attachment=f` | 7 train, 3 test |
| `gill-color=f` | `gill-attachment=f` | 7 train, 3 test |
| `stem-color=f` | `stem-surface=f` | 2 train, 1 test |

These are mushrooms without gills (e.g. Horn of Plenty, Common Morel,
Chanterelle) or without a stem (Soft Slipper Toadstool, Silver Leaf Fungus,
Hairy Stereum). They have `[f]` in every gill or stem column, so `f` probably
means "none". Keeping all three gill columns would count "no gills" three
times in every distance. No column was constant.

### Numeric columns → same scale

| Column | Training range (after 2.2 capping) | Scaled training range | Scaled test range |
|---|---|---|---|
| cap-diameter-midpoint | 0.7 – 19.0 | 0 – 1 | 0.000 – 0.883 |
| stem-height-midpoint | 0 – 18.67 | 0 – 1 | 0.000 – 0.848 |
| stem-width-midpoint | 0 – 47.8 | 0 – 1 | 0.000 – 0.883 |

Each midpoint is first transformed with `log1p(x) = log(1 + x)`, which
compresses large sizes so a difference between small mushrooms (2 vs 4) counts
more than the same difference between large ones (40 vs 42). It is then
MinMax-scaled to 0–1 with the training minimum and maximum, the same range as
the dummy columns. Without scaling, stem width (up to 47.8) would outweigh
every 0/1 column in a distance. The dummy columns are not scaled: they are
already 0/1, and standardising them would turn rare codes into large values.

### Result

**94 feature columns**: 91 dummy columns + 3 scaled numeric columns, for 123
training and 50 test mushrooms. Because 91 of the 94 columns are categorical,
the categorical features will have much more influence on KNN distances than
the three size measurements. This follows from the data, not from an error,
and is relevant when interpreting KNN results.

## Task 2.5 — K-Nearest Neighbours on all 94 features

The script `task 2 classification/knn/2.5_knn_all_features.py` uses
scikit-learn's `KNeighborsClassifier` on the 94 encoded columns from Task 2.4.
To classify a mushroom, KNN:

1. computes its **Euclidean distance** to every training mushroom. On the 0/1
   dummy columns, the squared distance is simply the number of codes on which
   the two mushrooms disagree; each scaled size column adds at most 1;
2. takes the **k training mushrooms with the smallest distance**;
3. predicts the family that occurs **most often among those k**. If two or more
   families have the same number of votes, scikit-learn picks the
   alphabetically first one.

All 94 columns are used here on purpose: this result is the reference that
feature selection will be compared against.

### Choosing k

k was chosen **without using the test set**, by leave-one-out on the training
rows: for each k, every one of the 123 training mushrooms is predicted from the
other 122. The k with the highest macro F1 was chosen, because macro F1 counts
every family equally and the families are very unequal in size.

![KNN leave-one-out scores for each k](<task 2 classification/knn/2.5_k_selection.png>)

| k | 1 | **3** | 5 | 7 | 9 | 11 | 13 | 15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Leave-one-out accuracy | 42.3% | **44.7%** | 43.1% | 46.3% | 44.7% | 43.1% | 44.7% | 43.9% |
| Leave-one-out macro F1 | 0.179 | **0.233** | 0.181 | 0.174 | 0.167 | 0.151 | 0.155 | 0.146 |

**k = 3** has the best macro F1. Accuracy barely changes with k (42–46%), but
macro F1 falls as k grows: with more neighbours voting, the big families
(Tricholoma, Russula) win more votes and the small families are predicted
less often. k = 7 has a slightly higher accuracy, but only by getting more of
the big families right. The dashed line is always predicting Tricholoma (24.4%).

### Results

| Data | Mushrooms | Correctly classified | Accuracy |
|---|---:|---:|---:|
| Training, each mushroom predicted from the other 122 (leave-one-out) | 123 | 55 | **44.7%** |
| Training, mushroom itself included among its neighbours | 123 | 80 | 65.0% |
| Test (never seen) | 50 | 27 | **54.0%** |

The second row is shown only to compare with the tree's 100% training score:
when a training mushroom is predicted, it is its own nearest neighbour
(distance 0), so it always gets one vote for its own family. The leave-one-out
row is the honest training estimate. It is lower than the test score partly
because the six single-mushroom families can never be predicted correctly in
leave-one-out (when their only mushroom is left out, no example remains), and
partly because a 50-mushroom test set is small: one mushroom is 2 percentage
points.

### Comparison with the disorder tree

| Model | Test accuracy | Test macro F1 |
|---|---:|---:|
| Always predict Tricholoma | 26.0% (13/50) | 0.024 |
| Disorder tree (Task 2.3) | 30.0% (15/50) | 0.190 |
| **KNN, k = 3, all 94 features** | **54.0% (27/50)** | **0.396** |

KNN classifies 12 more test mushrooms correctly than the tree, and its macro F1
is about twice as high. The tree only matches a test mushroom when its exact
cell value (e.g. a whole `gill-color` combination) was seen in training. KNN
compares codes one by one, so a mushroom with an unseen combination can still
be close to training mushrooms that share most of its codes.

### Clear versus tied votes

| Vote among the 3 neighbours | Test mushrooms | Correct | Accuracy |
|---|---:|---:|---:|
| Clear majority (at least 2 of 3 agree) | 26 | 20 | 76.9% |
| Tied (3 different families, decided alphabetically) | 24 | 7 | 29.2% |

Almost half of the test predictions are ties. For example, the nearest
neighbours of The Blusher (Amanita) are False Panther Cap (Amanita, distance
2.238), Shaggy Parasol (Lepiota, 2.650) and Bare-toothed Russula (Russula,
2.834). Each family has one vote, so the alphabetically first family, Amanita,
is predicted: correct here, but by luck of the alphabet. When the neighbours
agree, KNN is right about three times out of four; when they do not, the
result is close to a guess. A better tie rule (for example, giving closer
neighbours a larger vote) could change those 24 predictions.

The full k table, per-family test scores and individual predictions are in
[`2.5_knn_summary.md`](<task 2 classification/knn/2.5_knn_summary.md>) and
[`2.5_test_predictions.csv`](<task 2 classification/knn/2.5_test_predictions.csv>).
