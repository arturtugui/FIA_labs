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

| Family | Mushrooms | Share of 173 |
|---|---:|---:|
| Tricholoma Family | 43 | 24.9% |
| Russula Family | 27 | 15.6% |
| Bolete Family | 14 | 8.1% |
| Ink Cap Family | 13 | 7.5% |
| Cortinarius Family | 11 | 6.4% |
| Amanita Family | 8 | 4.6% |
| Wax Gill Family | 8 | 4.6% |
| Stropharia Family | 8 | 4.6% |
| Entoloma Family | 7 | 4.0% |
| Bracket Fungi | 7 | 4.0% |
| Mushroom Family | 5 | 2.9% |
| Lepiota Family | 3 | 1.7% |
| Bolbitius Family | 3 | 1.7% |
| Paxillus Family | 3 | 1.7% |
| Chanterelle Family | 3 | 1.7% |
| Pluteus Family | 2 | 1.2% |
| Oyster Mushroom Family | 2 | 1.2% |
| Crepidotus Family | 1 | 0.6% |
| Hydnum Family | 1 | 0.6% |
| Ear-Pick Family | 1 | 0.6% |
| Saddle-Cup Family | 1 | 0.6% |
| Morel Family | 1 | 0.6% |
| Jelly Discs Family | 1 | 0.6% |
| **Total (23 families)** | **173** | **100%** |

The two largest families hold 40.5% of all mushrooms, while the 12 smallest
families (3 or fewer mushrooms each) hold 22 mushrooms together (12.7%).

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

#### What macro F1 means

Accuracy counts every mushroom equally, so the 13 Tricholoma mushrooms in the
test set dominate it: a model that only ever says "Tricholoma" already gets
26%. **Macro F1** is used next to accuracy because it gives **every family the
same weight**, however many mushrooms it has. It is built in three steps, for
each family separately:

- **Precision**: of the mushrooms the model *called* this family, how many
  really are? (Are its guesses of this family trustworthy?)
- **Recall**: of the mushrooms that *really are* this family, how many did the
  model find? (Does it miss this family?)
- **F1**: one number combining both, `F1 = 2 × precision × recall /
  (precision + recall)`. It is high only when both are high, and 0 when the
  model never gets this family right.

Example with the tree's test results for Tricholoma: the tree said
"Tricholoma" 23 times and 8 of those were right, so precision = 8 / 23 =
0.348; there are 13 Tricholoma mushrooms in the test set and the tree found 8,
so recall = 8 / 13 = 0.615; F1 = 2 × 0.348 × 0.615 / (0.348 + 0.615) = 0.444.

**Macro F1 is the plain average of the F1 values of all families**, so a small
family with 1 test mushroom counts as much as Tricholoma with 13. The families
included are those that appear in the test set or in the predictions (17 + 2
for the tree); a family the model never gets right has F1 = 0. Macro F1 goes
from 0 (worst) to 1 (every mushroom of every family right).

The tree scores **0.190** on test. Always guessing Tricholoma scores only
**0.024**: Tricholoma gets F1 = 0.413 (precision 13 / 50, recall 13 / 13), every
other family gets 0, and 0.413 averaged over 17 families is 0.024. So a model
can have a reasonable accuracy and still a very low macro F1 when it ignores
the small families; macro F1 is therefore the main score for choosing settings
in the later models.

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

# Task 3 — Ensemble classifiers

An ensemble combines many decision trees into one model. Two ensembles were
trained, one of each kind:

- **Random forest** (a *bagging* method): many independent trees, each trained
  on a random sample of the mushrooms; they vote.
- **Gradient boosting** (a *boosting* method): trees are built one after
  another, each one correcting the mistakes of the trees before it.

Both use exactly the same protocol as KNN (Task 2.5), so all models can be
compared fairly: the same 94 encoded columns from Task 2.4, settings chosen by
leave-one-out macro F1 on the 123 training mushrooms only, and the 50 test
mushrooms used once at the end. Both use scikit-learn with a fixed random seed
(42), so every run gives the same result. Shared code (loading, leave-one-out
tuning, tables, importance plot) is in `task 3 ensembles/ensemble_common.py`.

## Task 3.1 — Random forest

The script `task 3 ensembles/random forest/3.1_random_forest.py` builds a forest
of **300 decision trees**:

1. Each tree is trained on a *bootstrap sample*: 123 mushrooms drawn at random
   **with replacement** from the 123 training mushrooms. Some mushrooms are
   drawn two or three times, and on average about 37% are not drawn at all.
2. At every question (split), a tree may only choose among a **random subset of
   the 94 columns**. This makes the trees different from each other, so their
   mistakes partly cancel out when they vote. Without this step the method
   would be plain bagging of trees, and most trees would ask the same strong
   questions.
3. To classify a mushroom, every tree gives its probability for each family,
   the forest averages them and predicts the family with the highest average.

### Choosing the settings

Four versions were tried, each scored on the training mushrooms by
leave-one-out (each training mushroom is hidden, the forest is trained on the
other 122 and then guesses the hidden one):

| Columns each question may choose from | Mistakes on small families cost more? | Correct (out of 123) | Accuracy | Macro F1 |
|---|---|---:|---:|---:|
| about 9 (√94) | No | 60 | 48.8% | 0.158 |
| about 9 (√94) | Yes | 59 | 48.0% | 0.187 |
| about 28 (30% of 94) | No | 59 | 48.0% | 0.165 |
| **about 28 (30% of 94)** | **Yes** | **61** | **49.6%** | **0.225** |

In scikit-learn these settings are called `max_features` (`"sqrt"` or `0.3`)
and `class_weight` (`None` or `"balanced_subsample"`). The number of trees is
fixed at 300: more trees only make the vote more stable, never worse.

Accuracy hardly changes (48–50%), but macro F1 rises clearly when mistakes on
small families cost more (0.158 → 0.187 and 0.165 → 0.225). That setting makes
the trees try harder on the small families instead of mostly learning
Tricholoma and Russula. The last version has the best macro F1 and was chosen.

### Results

| Data | Mushrooms | Correctly classified | Accuracy |
|---|---:|---:|---:|
| Training, each mushroom predicted from the other 122 (leave-one-out) | 123 | 61 | **49.6%** |
| Training, forest asked about the mushrooms it was trained on | 123 | 123 | 100.0% |
| Test (never seen) | 50 | 33 | **66.0%** |

Test macro F1: **0.494**.

The 100% row is not real skill: the forest has seen those exact mushrooms. As
with KNN, leave-one-out is lower than test partly because the six
single-mushroom families can never be guessed in leave-one-out, and partly
because a 50-mushroom test set is small (one mushroom = 2 percentage points).

**Out-of-bag check.** Each tree never saw about 37% of the training mushrooms,
so each mushroom can be guessed using only the trees that did not see it. This
gives a second training-only estimate for free: **49.6% accuracy, macro F1
0.225**, the same as leave-one-out.

### Which columns the forest used most

![Random forest feature importance](<task 3 ensembles/random forest/3.1_feature_importance.png>)

Importance measures how much a column helped the trees separate the families,
averaged over all 300 trees (all importances add up to 1). Summed over the
dummy columns of each original feature, the top features are
`gill-attachment` (0.143), `gill-color` (0.103), `cap-color` (0.097) and
`cap-shape` (0.094). The three size columns are the top single columns, but
this measure is known to favour numeric columns, because they offer many
possible split points while a 0/1 column offers only one. `gill-attachment`
also had the strongest association with family in Step 1.7.

Full tables are in
[`3.1_random_forest_summary.md`](<task 3 ensembles/random forest/3.1_random_forest_summary.md>)
and [`3.1_test_predictions.csv`](<task 3 ensembles/random forest/3.1_test_predictions.csv>).

## Task 3.2 — Gradient boosting

The script `task 3 ensembles/gradient boosting/3.2_gradient_boosting.py` uses
scikit-learn's `GradientBoostingClassifier`:

1. Start from a simple guess: each family's share of the training mushrooms.
2. Build a small tree that predicts how wrong the current probabilities are
   for each training mushroom. With 23 families, each round builds one small
   tree per family (23 trees per round).
3. Add the trees' corrections, scaled down by the **learning rate** (0.1, so
   each round fixes only a tenth of the error), and repeat for the chosen
   number of rounds.
4. Predict the family with the highest probability after the last round.

Unlike the random forest, the trees are not independent: each one is built to
fix what the previous ones still get wrong. Each round also uses a random 80%
of the training mushrooms (`subsample = 0.8`), which adds some randomness and
makes overfitting slower.

### Choosing the settings

| Rounds | Questions per small tree (depth) | Correct (out of 123) | Accuracy | Macro F1 |
|---:|---:|---:|---:|---:|
| 100 | 2 | 58 | 47.2% | 0.213 |
| **100** | **3** | **58** | **47.2%** | **0.214** |
| 200 | 2 | 59 | 48.0% | 0.212 |
| 200 | 3 | 57 | 46.3% | 0.191 |

In scikit-learn these settings are `n_estimators` and `max_depth`; the
learning rate is fixed at 0.1. The trees are kept shallow (2–3 questions)
because boosting overfits quickly on small data. 100 rounds with depth 3 has
the highest macro F1 and was chosen, but the first three versions differ by
only 0.002, which is far less than a single mushroom changes; in practice they
are equally good. Only the largest version (200 rounds, depth 3) is clearly
worse, which is a sign of overfitting.

### Results

| Data | Mushrooms | Correctly classified | Accuracy |
|---|---:|---:|---:|
| Training, each mushroom predicted from the other 122 (leave-one-out) | 123 | 58 | **47.2%** |
| Training, model asked about the mushrooms it was trained on | 123 | 122 | 99.2% |
| Test (never seen) | 50 | 26 | **52.0%** |

Test macro F1: **0.277**.

### Which columns gradient boosting used most

![Gradient boosting feature importance](<task 3 ensembles/gradient boosting/3.2_feature_importance.png>)

Summed per original feature, the top features are `ring-type` (0.210),
`gill-color` (0.114), `cap-shape` (0.106) and `gill-attachment` (0.097).
`gill-color`, `cap-shape` and `gill-attachment` are near the top for both
ensembles. `ring-type` is ranked much higher than in the random forest
(0.064): boosting concentrates on the few columns that fix the remaining
mistakes, while the random forest's random column subsets spread the
importance over more columns.

Full tables are in
[`3.2_gradient_boosting_summary.md`](<task 3 ensembles/gradient boosting/3.2_gradient_boosting_summary.md>)
and [`3.2_test_predictions.csv`](<task 3 ensembles/gradient boosting/3.2_test_predictions.csv>).

## Task 3 — Comparison with the Task 2 models

All models were evaluated on the same 50 test mushrooms:

| Model | Test accuracy | Test macro F1 |
|---|---:|---:|
| Always predict Tricholoma | 26.0% (13/50) | 0.024 |
| Disorder tree (Task 2.3) | 30.0% (15/50) | 0.190 |
| KNN, k = 3 (Task 2.5) | 54.0% (27/50) | 0.396 |
| **Random forest (Task 3.1)** | **66.0% (33/50)** | **0.494** |
| Gradient boosting (Task 3.2) | 52.0% (26/50) | 0.277 |

- **The random forest is the best model so far** on both measures: 6 more
  correct test mushrooms than KNN and 18 more than the disorder tree.
- **Gradient boosting did not beat KNN.** Its accuracy is close (52% vs 54%),
  but its macro F1 is much lower (0.277 vs 0.396): it gets the big families
  right but misses more of the small ones.
- **Why the forest did better than boosting here.** Both start from trees that
  can memorise the training data (100% and 99.2% on the training mushrooms).
  The forest averages 300 independent trees, so the memorised details of
  individual mushrooms mostly cancel out. Boosting builds every tree to fix the
  remaining mistakes, and with 23 families and only 1–3 training mushrooms for
  many of them, the remaining mistakes are often single unusual mushrooms, so
  it learns details that do not repeat in the test set.
- **These differences need care.** With 50 test mushrooms, one mushroom is 2
  percentage points, so a gap of 1–2 mushrooms (e.g. KNN vs gradient boosting)
  is within chance. The gap between the random forest and the rest (6 or more
  mushrooms) is larger. Task 4 will compare all models with more metrics.

# Task 4 — Performance of all models

The script `task 4 evaluation/4.1_model_comparison.py` compares every model from
Tasks 2 and 3 on the **same 50 test mushrooms**. It reads each model's saved
test predictions, so no model is retrained and every model is judged on
exactly the same mushrooms. "Always Tricholoma" (always predicting the most
common training family) is included as the reference every model must beat.
All tables are also in
[`4.1_model_comparison_summary.md`](<task 4 evaluation/4.1_model_comparison_summary.md>).

## 4.1 Which metrics, and why

The data is very unbalanced: the 50 test mushrooms include 13 Tricholoma and
8 Russula, while 6 families have a single test mushroom. A good metric must
therefore show whether a model recognises the small families too, not only the
big ones. Five metrics were used, each answering a different question:

| Metric | What it measures | Why it is used here | Always Tricholoma scores |
|---|---|---|---:|
| **Accuracy** | Share of mushrooms classified correctly | Easy to understand, but the big families dominate it. Kept as a reference only. | 0.26 |
| **Balanced accuracy** | Average recall per family: for each family, the share of its mushrooms that were found, then averaged | Every family counts equally, so ignoring the small families is punished | 0.06 |
| **Macro F1** | Average F1 per family (precision and recall combined; see Task 2.3) | Like balanced accuracy, every family counts equally, but it also punishes *wrong* guesses of a family (low precision). Used to choose the settings of every model. | 0.02 |
| **Weighted F1** | F1 per family, averaged with each family weighted by its number of test mushrooms | Comparing it with macro F1 shows how much a model relies on the big families: a large gap means the small families are mostly missed | 0.11 |
| **MCC** (Matthews correlation coefficient) | One number from the whole table of real versus predicted families: −1 = always wrong, 0 = no better than chance, 1 = perfect | Corrects for chance: guessing only the biggest family gets exactly 0, however unbalanced the data is | 0.00 |

Always predicting Tricholoma looks acceptable by accuracy (26%) but scores close
to zero on every other metric. This is why accuracy alone would be misleading
here. ROC-AUC was not used: it needs a probability for every family, and with
1–2 test mushrooms for most families its per-family values would be
meaningless.

## 4.2 Results

| Model | Correct | Accuracy | Balanced accuracy | Macro F1 | Weighted F1 | MCC |
|---|---:|---:|---:|---:|---:|---:|
| Always Tricholoma | 13/50 | 0.260 | 0.059 | 0.024 | 0.107 | 0.000 |
| Disorder tree (2.3) | 15/50 | 0.300 | 0.242 | 0.190 | 0.256 | 0.179 |
| KNN, k = 3 (2.5) | 27/50 | 0.540 | 0.476 | 0.396 | 0.502 | 0.509 |
| **Random forest (3.1)** | **33/50** | **0.660** | **0.525** | **0.494** | **0.590** | **0.613** |
| Gradient boosting (3.2) | 26/50 | 0.520 | 0.310 | 0.277 | 0.477 | 0.446 |

![All metrics for all models](<task 4 evaluation/4.1_metrics.png>)

- **The random forest is best on all five metrics.**
- **The ranking depends on the metric for KNN and gradient boosting.** Their
  accuracy is almost the same (54% vs 52%) and gradient boosting's weighted F1
  is close to KNN's (0.48 vs 0.50), but its balanced accuracy (0.31 vs 0.48)
  and macro F1 (0.28 vs 0.40) are much lower. Gradient boosting does well on
  the big families and misses the small ones; KNN spreads its correct answers
  over more families. Accuracy alone would have hidden this.
- **Weighted F1 versus macro F1** shows the same thing for every model: the gap
  is 0.20 for gradient boosting, 0.11 for KNN and 0.10 for the random forest.

### Training versus unseen mushrooms (overfitting)

From the results tables of Tasks 2.3–3.2:

| Model | Training mushrooms it was trained on | Training, leave-one-out (unseen) | Test (unseen) |
|---|---:|---:|---:|
| Disorder tree | 100.0% | – | 30.0% |
| KNN, k = 3 | 65.0% | 44.7% | 54.0% |
| Random forest | 100.0% | 49.6% | 66.0% |
| Gradient boosting | 99.2% | 47.2% | 52.0% |

All tree-based models reach (almost) 100% on mushrooms they were trained on
and about 30–66% on unseen ones. The random forest overfits as much as the
others on its own training mushrooms, but averaging 300 different trees still
gives the best result on unseen mushrooms.

## 4.3 How certain are these differences?

With 50 test mushrooms, one mushroom changes accuracy by 2 percentage points,
so some differences could be luck. To measure this, the 50 test mushrooms were
resampled with replacement 2000 times (*bootstrap*): each resample is a new
"test set" of 50 drawn from the real one, and every model is scored on it. The
middle 95% of those scores gives a range for each result.

![Accuracy and macro F1 with 95% ranges](<task 4 evaluation/4.1_uncertainty.png>)

| Model | Accuracy (95% range) | Macro F1 (95% range) |
|---|---|---|
| Disorder tree | 0.30 (0.18 to 0.44) | 0.19 (0.10 to 0.29) |
| KNN, k = 3 | 0.54 (0.40 to 0.68) | 0.40 (0.30 to 0.56) |
| Random forest | 0.66 (0.52 to 0.78) | 0.49 (0.35 to 0.65) |
| Gradient boosting | 0.52 (0.38 to 0.66) | 0.28 (0.20 to 0.42) |

The ranges are wide (about ±0.13) and overlap. A fairer test of "is the random
forest better than model X?" compares both models on the *same* resampled
mushrooms and looks at the difference:

| Random forest minus … | Accuracy difference (95% range) | Macro F1 difference (95% range) | Clearly better? |
|---|---|---|---|
| Always Tricholoma | +0.40 (+0.24 to +0.56) | +0.47 (+0.32 to +0.62) | Yes |
| Disorder tree | +0.36 (+0.18 to +0.52) | +0.30 (+0.15 to +0.46) | Yes |
| Gradient boosting | +0.14 (0.00 to +0.28) | +0.20 (+0.07 to +0.33) | Yes for macro F1; borderline for accuracy |
| KNN, k = 3 | +0.12 (−0.04 to +0.28) | +0.08 (−0.07 to +0.22) | **No**: the range includes 0 |

So the random forest is clearly better than the tree, the baseline and (for
macro F1) gradient boosting. Against KNN it is better on this test set, but
the difference is not large enough to rule out luck with only 50 test
mushrooms.

## 4.4 Which families are recognised?

Test mushrooms found per family (found / test mushrooms of that family):

| Family | In dataset | Always Tricholoma | Disorder tree | KNN | Random forest | Gradient boosting |
|---|---:|---:|---:|---:|---:|---:|
| Tricholoma | 43 | 13/13 | 8/13 | 5/13 | **12/13** | 9/13 |
| Russula | 27 | 0/8 | 0/8 | 5/8 | **6/8** | **6/8** |
| Bolete | 14 | 0/4 | 0/4 | **4/4** | **4/4** | **4/4** |
| Ink Cap | 13 | 0/4 | 2/4 | **3/4** | 1/4 | 2/4 |
| Cortinarius | 11 | 0/3 | 0/3 | **1/3** | 0/3 | **1/3** |
| Amanita | 8 | 0/2 | 1/2 | **2/2** | 1/2 | 0/2 |
| Stropharia | 8 | 0/2 | 0/2 | 0/2 | **2/2** | **2/2** |
| Wax Gill | 8 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| Bracket Fungi | 7 | 0/2 | **2/2** | **2/2** | **2/2** | 0/2 |
| Entoloma | 7 | 0/2 | 1/2 | **2/2** | **2/2** | 1/2 |
| Mushroom | 5 | 0/2 | 0/2 | **2/2** | 1/2 | 1/2 |
| Bolbitius | 3 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| Chanterelle | 3 | 0/1 | 0/1 | **1/1** | **1/1** | 0/1 |
| Lepiota | 3 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| Paxillus | 3 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| Oyster Mushroom | 2 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| Pluteus | 2 | 0/1 | **1/1** | 0/1 | **1/1** | 0/1 |

Grouped by family size (number of mushrooms in the whole dataset):

| Family size | Families | Test mushrooms | Disorder tree | KNN | Random forest | Gradient boosting |
|---|---:|---:|---:|---:|---:|---:|
| Large (13–43) | 4 | 29 | 10 (34%) | 17 (59%) | **23 (79%)** | 21 (72%) |
| Medium (5–11) | 7 | 15 | 4 (27%) | **9 (60%)** | 8 (53%) | 5 (33%) |
| Small (2–3) | 6 | 6 | 1 (17%) | 1 (17%) | **2 (33%)** | 0 (0%) |

- **The random forest wins mainly on the large families** (79%), especially
  Tricholoma (12 of 13).
- **KNN is the best model for the medium-sized families** (60% versus 53% for
  the forest). Because it compares a mushroom with its closest neighbours, it
  can recognise a family from just a few similar training mushrooms.
- **Gradient boosting** is almost as good as the forest on large families
  (72%) but weak on medium and small ones, which explains its low macro F1.
- **Five families are never recognised by any model**: Wax Gill, Bolbitius,
  Lepiota, Paxillus and Oyster Mushroom. Apart from Wax Gill, each has only
  1–2 training mushrooms, which is too few to learn from.

**Confusion matrix of the random forest** (rows = real family, columns =
predicted family; outlined cells are the correct predictions):

![Random forest confusion matrix](<task 4 evaluation/4.1_confusion_matrix_best_model.png>)

10 of the forest's 17 mistakes are predictions of **Tricholoma**: Ink Cap (3),
Russula (2), Wax Gill (2), Amanita, Bolbitius and Cortinarius (1 each). When
the forest is unsure, it falls back to the biggest family, which has the most
training examples and therefore wins many tree votes. Two small families
(Oyster Mushroom, Paxillus) are predicted as Russula, the second-biggest family.

## 4.5 Errors by rarity tier

The story asks whether valuable (Legendary) mushrooms are classified as well
as common ones. Using the tiers from Step 1.10:

| Tier | Test mushrooms | Disorder tree | KNN | Random forest | Gradient boosting |
|---|---:|---:|---:|---:|---:|
| Common | 40 | 10 | 20 | **27** | 22 |
| Rare | 9 | 4 | **6** | 5 | 4 |
| Legendary | 1 | 1 | 1 | 1 | 0 |

Only one Legendary mushroom ended up in the test set, so nothing can be
concluded about Legendary mushrooms from this split. On the 9 Rare mushrooms,
KNN (6) does slightly better than the forest (5), consistent with KNN being
better on less typical mushrooms, but 9 mushrooms is too few for a firm
conclusion. The models predict the family, not the tier, so a mistake here
means "wrong family", not "Legendary sold as Common".

## 4.6 Conclusions

**Per model**

- **Always Tricholoma (baseline):** 26% accuracy but 0 MCC and a macro F1 of
  0.02. It shows why accuracy alone is not enough on this data.
- **Disorder tree:** only slightly better than the baseline on accuracy (30%),
  though clearly better on the family-balanced metrics. It classifies every
  training mushroom correctly but cannot handle test mushrooms whose exact cell
  values it never saw (35 of 50 test mushrooms hit such an answer).
- **KNN (k = 3):** a large step up (54%, macro F1 0.40) from a very simple
  method, and the best model for medium-sized families and Rare mushrooms. Its
  weakness is tied votes: almost half of its test predictions were three
  different families, decided alphabetically.
- **Random forest:** the best model on every metric (66%, macro F1 0.49, MCC
  0.61), and the most reliable on the large families. Averaging 300 different
  trees removes much of the single tree's memorising. Its typical mistake is
  falling back to Tricholoma when unsure.
- **Gradient boosting:** good accuracy and weighted F1, but low balanced
  accuracy and macro F1: it learns the big families and overfits the small
  ones (99.2% on its training mushrooms).

**Overall**

1. **Ensembles were not automatically better.** The random forest beat every
   other model, but gradient boosting did worse than the much simpler KNN on
   the family-balanced metrics. With 123 training mushrooms, averaging
   (random forest) worked better than step-by-step correction (boosting).
2. **The data limits the results more than the choice of model.** Six families
   have a single mushroom and cannot be tested at all; five more are never
   recognised by any model. More mushrooms per family would help more than a
   different algorithm.
3. **The test set is small.** The 95% ranges are about ±0.13, so the random
   forest's lead over KNN (6 mushrooms) is suggestive but not certain.

**Improvements not tried here:** repeated stratified cross-validation instead
of one fixed 70/30 split (more reliable scores from the same data), merging the
families with fewer than 5 mushrooms into one "Other" class, feature selection
to remove columns that only add noise, and distance-weighted voting in KNN to
avoid alphabetical tie-breaks.

# Task 5 — Clustering with K-Means

**Held-out column: `family`.** K-Means is run without the family label, and
the clusters are compared with the families afterwards, to see whether the
mushrooms' features alone group them into their families. `class` and `name`
are also left out of the input. K-Means only sees the 94 encoded feature
columns from Task 2.4 (91 dummy 0/1 columns and 3 scaled size columns), the
same columns KNN used. No train/test split is needed: K-Means uses no labels,
so there is nothing to test on unseen mushrooms.

The script is `task 5 clustering/5.1_kmeans_by_family_size.py`. K-Means works
as follows:

1. Place k cluster centres.
2. Assign every mushroom to its nearest centre (Euclidean distance, as in KNN).
3. Move every centre to the average of the mushrooms assigned to it.
4. Repeat steps 2–3 until no mushroom changes cluster.

The result depends on the starting centres, so it is run 10 times from
different starts and the best run is kept (fixed random seed 42).

## 5.1 Number of clusters = number of families

Many families have only one or a few mushrooms (see the family table in Step
1.4), and a cluster cannot meaningfully represent a family of one. So K-Means
was run four times, each time only on the mushrooms of families above a size
threshold, with **k equal to the number of those families**. If the features
grouped mushrooms by family, each cluster would then contain a single family.

| Run | Families included | Families = k | Mushrooms clustered |
|---|---|---:|---:|
| 1 | more than 10 mushrooms (Tricholoma, Russula, Bolete, Ink Cap, Cortinarius) | 5 | 108 |
| 2 | more than 6 mushrooms (+ Amanita, Wax Gill, Stropharia, Entoloma, Bracket Fungi) | 10 | 146 |
| 3 | more than 2 mushrooms (+ Mushroom, Lepiota, Bolbitius, Paxillus, Chanterelle) | 15 | 163 |
| 4 | all families | 23 | 173 |

Two simple scores measure how well the clusters match the families:

- **Purity**: the share of mushrooms that belong to the largest family of
  their cluster. 1.0 means every cluster contains a single family. For
  comparison, putting all mushrooms into one cluster would give a purity
  equal to the share of the largest family (Tricholoma).
- **Family togetherness**: for each family, the share of its mushrooms that
  are in the same cluster (its most common one), averaged over the families.
  1.0 means no family is split over several clusters.

## 5.2 Results

| Families included | k | Mushrooms | Purity | Purity if all in one cluster | Family togetherness | Families that are the largest family of some cluster |
|---|---:|---:|---:|---:|---:|---|
| more than 10 mushrooms | 5 | 108 | 0.528 | 0.398 | 0.516 | 3 of 5 |
| more than 6 mushrooms | 10 | 146 | 0.493 | 0.295 | 0.413 | 6 of 10 |
| more than 2 mushrooms | 15 | 163 | 0.497 | 0.264 | 0.563 | 7 of 15 |
| all families | 23 | 173 | 0.549 | 0.249 | 0.654 | 12 of 23 |

In each figure below, the left map shows the K-Means clusters and the right
map shows the real families of the same mushrooms. Each cluster is labelled
with its largest family and how many of its mushrooms belong to it (e.g.
"Russula 12/14" = 12 of the cluster's 14 mushrooms are Russula). The maps are
a 2D PCA projection of the 94 columns, which keeps only 13.8% of the
variation, so clusters that overlap on the map can still be separated in the
full 94 columns. Each family keeps the same colour and marker shape in every
figure. Under each figure, a table gives the number of mushrooms of each
family in each cluster; **bold** marks the largest family of each cluster
(both are bold when two families tie), and the last row is the cluster size.

**k = 5, families with more than 10 mushrooms:**

![K-Means k = 5](<task 5 clustering/5.1_k5_map.png>)

| Family (mushrooms) | C1 | C2 | C3 | C4 | C5 |
| --- | --- | --- | --- | --- | --- |
| Tricholoma (43) | 2 | **9** | **17** | 3 | **12** |
| Russula (27) | **12** | 3 | 12 | 0 | 0 |
| Bolete (14) | 0 | 6 | 0 | **7** | 1 |
| Ink Cap (13) | 0 | 1 | 3 | 0 | 9 |
| Cortinarius (11) | 0 | 6 | 2 | 1 | 2 |
| **Cluster size** | 14 | 25 | 34 | 11 | 24 |

Even with only the five largest families, no cluster is one family.
Tricholoma is spread over all five clusters, Russula is split in two halves
(12 and 12), and Ink Cap and Cortinarius are never the largest family of any
cluster. The closest match is cluster C1 (12 of its 14 mushrooms are
Russula).

**k = 10, families with more than 6 mushrooms:**

![K-Means k = 10](<task 5 clustering/5.1_k10_map.png>)

| Family (mushrooms) | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tricholoma (43) | **11** | 1 | 4 | 1 | 1 | 1 | 0 | **13** | **9** | **2** |
| Russula (27) | 1 | 0 | 2 | 0 | 0 | 0 | **11** | 4 | **9** | 0 |
| Bolete (14) | 1 | **7** | **5** | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| Ink Cap (13) | 0 | 0 | 0 | **3** | 1 | **4** | 0 | 1 | 3 | 1 |
| Cortinarius (11) | 1 | 2 | 2 | 1 | 0 | 0 | 0 | 1 | 3 | 1 |
| Amanita (8) | 0 | 0 | 0 | 0 | **7** | 0 | 0 | 1 | 0 | 0 |
| Stropharia (8) | 0 | 2 | 1 | **3** | 0 | 0 | 0 | 0 | 0 | **2** |
| Wax Gill (8) | 0 | 1 | 2 | 1 | 0 | 0 | 0 | 3 | 1 | 0 |
| Bracket Fungi (7) | 2 | 2 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Entoloma (7) | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | 0 |
| **Cluster size** | 19 | 15 | 18 | 9 | 9 | 7 | 11 | 24 | 28 | 6 |

Adding five medium families gives one new clear group: 7 of the 8 Amanita
mushrooms end up in the same cluster. The large families stay split.

**k = 15, families with more than 2 mushrooms:**

![K-Means k = 15](<task 5 clustering/5.1_k15_map.png>)

| Family (mushrooms) | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 | C15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tricholoma (43) | 0 | 0 | 1 | **7** | 0 | **7** | 1 | 3 | **4** | **3** | 1 | **3** | 3 | 7 | **3** |
| Russula (27) | 0 | **10** | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **6** | **8** | 1 |
| Bolete (14) | 0 | 0 | 0 | 0 | **9** | 0 | 0 | 0 | 1 | 0 | **3** | 0 | 0 | 1 | 0 |
| Ink Cap (13) | 1 | 0 | **5** | 0 | 0 | 0 | **2** | 1 | 0 | 1 | 0 | 0 | 0 | 3 | 0 |
| Cortinarius (11) | 0 | 0 | 3 | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 1 |
| Amanita (8) | **7** | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Stropharia (8) | 0 | 0 | 1 | 0 | 0 | 1 | **2** | **4** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Wax Gill (8) | 0 | 0 | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| Bracket Fungi (7) | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | **3** | 0 | 0 | 0 |
| Entoloma (7) | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| Mushroom (5) | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bolbitius (3) | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Chanterelle (3) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** | 0 | 0 | 0 |
| Lepiota (3) | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Paxillus (3) | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Cluster size** | 15 | 13 | 14 | 7 | 15 | 11 | 8 | 9 | 8 | 6 | 5 | 9 | 14 | 21 | 8 |

One cluster now collects the ringed families: 7 Amanita, 4 of the 5 Mushroom
Family and all 3 Lepiota. All 3 Chanterelle mushrooms also share a cluster,
and 9 of the 14 Bolete mushrooms are together.

**k = 23, all families:**

![K-Means k = 23](<task 5 clustering/5.1_k23_map.png>)

| Family (mushrooms) | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 | C19 | C20 | C21 | C22 | C23 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tricholoma (43) | 0 | 1 | 1 | **7** | 0 | 3 | 3 | **4** | **4** | **2** | 0 | 0 | 0 | **7** | 1 | 2 | 2 | 3 | 1 | 1 | 0 | **1** | 0 |
| Russula (27) | 0 | 2 | 0 | 1 | 0 | **4** | 0 | 0 | 0 | 0 | **2** | **2** | 0 | 0 | 3 | **6** | 0 | 0 | **7** | 0 | 0 | 0 | 0 |
| Bolete (14) | 0 | 0 | 0 | 0 | **5** | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** | 0 | 0 | 0 |
| Ink Cap (13) | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | **9** | 0 | 0 | 0 | 0 | 0 |
| Cortinarius (11) | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 4 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| Amanita (8) | 0 | **5** | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Stropharia (8) | **2** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **4** | 0 | 0 | 0 | **2** | 0 | 0 |
| Wax Gill (8) | 0 | 0 | **4** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| Bracket Fungi (7) | 0 | 0 | 0 | 0 | 0 | 0 | **4** | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| Entoloma (7) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | **4** | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| Mushroom (5) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | **3** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bolbitius (3) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** | 0 | 0 |
| Chanterelle (3) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | **2** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Lepiota (3) | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Paxillus (3) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Oyster Mushroom (2) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Pluteus (2) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Crepidotus (1) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ear-Pick (1) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Hydnum (1) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Jelly Discs (1) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Morel (1) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Saddle-Cup (1) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Cluster size** | 6 | 8 | 6 | 10 | 5 | 12 | 13 | 6 | 12 | 2 | 4 | 5 | 4 | 12 | 8 | 13 | 8 | 14 | 10 | 6 | 4 | 3 | 2 |

With 23 clusters, some clusters are small groups of very similar mushrooms
(e.g. 9 of the 13 Ink Cap mushrooms in one cluster), but Tricholoma is spread
over 16 clusters and Russula over 8. The full family-by-cluster tables of all
four runs are in
[`5.1_kmeans_by_family_size_summary.md`](<task 5 clustering/5.1_kmeans_by_family_size_summary.md>).

## 5.3 What the clusters show

- **Clusters match families only partly.** Purity stays around 0.5 in every
  run: about half of the mushrooms are in a cluster dominated by another
  family. This is clearly better than putting everything in one cluster
  (0.40 down to 0.25), so the features do carry some family information, but
  K-Means does not recover the families.
- **Removing the small families does not help.** With only the five largest
  families (run 1), purity is 0.53, about the same as with all 23 families.
  The problem is not the small families: the large families themselves are
  split, because their mushrooms look different from each other (for example
  in colour), and K-Means groups mushrooms by how they look.
- **Families with a distinctive look are found.** Amanita (7 of 8 together
  for k = 10 and 15), and at k = 15 the other ringed families (Mushroom,
  Lepiota) join the same cluster. These families share a ring, which few
  other mushrooms have.
- **Family togetherness rises for k = 15 and 23 for a simple reason.** The
  small families added in these runs have 1–3 mushrooms, which can hardly be
  split (a family of one mushroom is always "together"), so they raise the
  average. The large families are not more together than in run 1.

# Task 6 — Clustering versus classification

The script `task 6 conclusions/6.1_clustering_vs_classification.py` puts the
Task 4 and Task 5 results side by side. It uses the k = 23 clustering run (all
173 mushrooms, one cluster per family) and the test predictions of the best
classifier (random forest) and of KNN; nothing is retrained. Each cluster's
**cluster family** is its largest family. Full tables are in
[`6.1_comparison_summary.md`](<task 6 conclusions/6.1_comparison_summary.md>).

## 6.1 Per family

For each family with test mushrooms: how many test mushrooms the classifiers
found, and how well the family stays together in the clusters.

| Family | Mushrooms | Random forest found (test) | KNN found (test) | Clusters it is spread over (k = 23) | Share in its main cluster | Largest family of that cluster? |
|---|---:|---:|---:|---:|---:|---|
| Tricholoma | 43 | 12/13 | 5/13 | 16 | 16% | yes |
| Russula | 27 | 6/8 | 5/8 | 8 | 26% | yes |
| Bolete | 14 | 4/4 | 4/4 | 4 | 36% | yes |
| Ink Cap | 13 | 1/4 | 3/4 | 5 | 69% | yes |
| Cortinarius | 11 | 0/3 | 1/3 | 8 | 36% | no (Russula) |
| Amanita | 8 | 1/2 | 2/2 | 2 | 62% | yes |
| Stropharia | 8 | 2/2 | 0/2 | 3 | 50% | yes |
| Wax Gill | 8 | 0/2 | 0/2 | 4 | 50% | yes |
| Bracket Fungi | 7 | 2/2 | 2/2 | 3 | 57% | yes |
| Entoloma | 7 | 2/2 | 2/2 | 4 | 57% | yes |
| Mushroom | 5 | 1/2 | 2/2 | 3 | 60% | yes |
| Bolbitius | 3 | 0/1 | 0/1 | 2 | 67% | yes |
| Chanterelle | 3 | 1/1 | 1/1 | 2 | 67% | yes |
| Lepiota | 3 | 0/1 | 0/1 | 3 | 33% | no (Stropharia) |
| Paxillus | 3 | 0/1 | 0/1 | 2 | 67% | no (Russula) |
| Oyster Mushroom | 2 | 0/1 | 0/1 | 2 | 50% | no (Tricholoma) |
| Pluteus | 2 | 1/1 | 0/1 | 1 | 100% | no (Tricholoma) |

## 6.2 Per test mushroom

For each of the 50 test mushrooms, the random forest's prediction is compared
with the cluster family of the cluster the mushroom fell into:

| Random forest prediction | Test mushrooms | Cluster family = real family | Cluster family = predicted family |
|---|---:|---:|---:|
| Correct | 33 | 25 | 25 |
| Wrong | 17 | 7 | 2 |

- When the forest is **right**, the cluster usually agrees (25 of 33).
- When the forest is **wrong**, the cluster rarely shares its mistake (2 of
  17), and in **7 of the 17 mistakes the cluster points to the correct
  family**. The clearest case is Ink Cap: Fairies' Bonnets, Fairy Parasol and
  Hay Cap all sit in cluster C18, whose largest family is Ink Cap (9 of the 13
  Ink Cap mushrooms are in it), yet the forest predicted Tricholoma for all
  three. The same happens for Field Mushroom (cluster of Mushroom Family),
  Egg Yolk Fungus (cluster of Bolbitius), Field Blewit (cluster of
  Tricholoma) and Birch Russula (cluster of Russula).

## 6.3 Where they agree and disagree

| Pattern | Families | Reading |
|---|---|---|
| **Both good**: classifiers find the family and it stays together in one cluster | Bracket Fungi, Entoloma, Chanterelle | These families look distinct; both approaches see it. |
| **Classification good, clustering split** | Tricholoma (12/13 found, spread over 16 clusters), Russula, Bolete | Large families whose mushrooms differ in appearance (especially colour). The classifier learned the few features that still identify the family; K-Means, which weighs all 94 columns equally, splits them by look. |
| **Clustering together, random forest poor, KNN good** | Ink Cap (69% in one cluster; forest 1/4, KNN 3/4), Amanita, Mushroom | The mushrooms are similar to each other, so distance-based methods (K-Means and KNN) group them, but the forest falls back to Tricholoma, the family with the most training examples. |
| **Both poor** | Cortinarius, Lepiota, Paxillus, Oyster Mushroom | Cortinarius is spread over 8 clusters and is not the largest family of any; the others have only 2–3 mushrooms and fall into clusters of other families. These families have no feature pattern of their own in this data. |

**KNN and K-Means agree with each other more than with the random forest.**
Both use the same Euclidean distance over all 94 columns, so they share the
same view of which mushrooms are similar. The random forest instead learns,
from the labels, which columns separate the families.

## 6.4 What each approach reveals that the other misses

**Classification reveals:**

- which features separate the families: `gill-attachment`, `gill-color`,
  `cap-shape` and `ring-type` carry the most importance (Task 3);
- that a large, varied family such as Tricholoma can still be recognised
  (12 of 13) although its members look different from each other, because a
  few features are shared within the family;
- how far the family can be predicted at all: about 66% of test mushrooms
  with the best model.

**Clustering reveals:**

- that the mushrooms group mainly by **appearance**, not by family: purity
  stays around 0.5 even when only the five largest families are clustered
  (Task 5);
- that large families consist of several **look-alike subgroups**
  (Tricholoma spread over 16 clusters, Russula over 8), which a classifier's
  single label hides;
- that some families **look like each other**: the ringed families Amanita,
  Mushroom and Lepiota share a cluster at k = 15, which explains why the
  classifiers confuse them (the Lepiota test mushroom was predicted as
  Amanita);
- a **bias of the random forest**: several of its mistakes are mushrooms that
  clearly belong to a tight group of their own family (Ink Cap), which the
  forest overrides with the most common family.

## 6.5 Overall conclusions

1. **Family can be predicted only partly from these features.** The best
   model (random forest) classifies 66% of test mushrooms correctly, against
   26% for always guessing Tricholoma, and K-Means recovers families only for
   the few with a distinctive look.
2. **The features describe appearance, and family is only partly a matter of
   appearance.** Families with a clear feature (a ring, unusual shape) are
   found by both approaches; families whose members vary (Tricholoma, Russula)
   are found only by a classifier that knows the labels; families with no
   pattern of their own are found by neither.
3. **The data limits both approaches.** 173 mushrooms in 23 families, six of
   them with a single mushroom, many blanks filled with modes, and a small
   test set (50 mushrooms) all limit what any model can learn or prove.
4. **The two views complement each other.** The classifier is the better tool
   for naming the family; the clusters show where its mistakes come from
   (look-alike families, varied large families) and suggest an improvement:
   combining a distance-based view (KNN, which finds tight small families)
   with the random forest (which handles large varied families).
