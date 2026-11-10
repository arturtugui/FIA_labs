# FCIM.FIA Autumn 2026
## Lab: Learning
**Handed out:** Monday, November 2, 2026

---

### Ma-ma-ma-Mushroom

It's late autumn in Luna-City, and with it comes the most anticipated time of the year: mushroom season. But these are not your ordinary Earth mushrooms. Lunarian mushrooms grow in the pressurised bio-domes scattered across the lunar surface, fed by recycled atmosphere and synthetic soil. They come in every shape, colour, and smell imaginable, and the citizens of Luna-City have been cultivating them for generations.

Every Lunarian mushroom is edible (the poisonous ones were, allegedly, dealt with a long time ago; no questions how). But not all mushrooms are created equal. The Luna-City Mycological Authority maintains a strict ranking system:

* **Common:** decent, fills the stomach, goes well in a soup.
* **Rare:** aromatic, sought after by local chefs.
* **Legendary:** so extraordinary that even Mario himself would abandon a princess rescue mission to get his hands on one.

The annual Mushroom Fair is Luna-City's biggest export event. Merchants from across the solar system arrive to bid on the finest specimens. But here's the problem: the mushrooms grow wild in the bio-domes, often in hard-to-reach corners, and by the time they're harvested, many are bruised, dirty, partially decomposed, or otherwise distorted beyond easy identification. The old survey catalogues are a mess. The mess consists of, but is not limited to: missing entries, inconsistent naming conventions, and measurements recorded in formats that haven't been standardised since the original colony ship landed.

The Mycological Authority needs an automated system that can take a mushroom (any mushroom, even a mangled, half-identified one) and determine what it is and how it ranks. The stakes are commercial: misclassifying a Legendary as a Common means selling it for pocket change. Misclassifying a Common as a Legendary means angry customers and a diplomatic incident with the Martian Trade Commission (they are very peculiar about their mushrooms, and not only).

You've been contracted to build this system and save the Luna City's authorities again. You'll work with the Authority's primary species catalogue. Missing values, multi-valued fields, inconsistent encodings, and enough data quality issues to make a database administrator weep, and you have real fun! The princess can wait; mushrooms... not really.

---

### General Guidelines

* Submit your solution as a zip archive, containing `.ipynb` and/or `.py` code files, and a PDF report describing what you have implemented, on ELSE.
* It is mandatory to use the Python programming language for this laboratory work.
* Do **NOT** host your solution in public repositories (e.g. GitHub etc). You can use private repositories if you need to.
* Plagiarism is **NOT** tolerated! Abusive usage of LLMs and vibe-coding are treated the same as plagiarism!

---

### Grading Policy

#### **Task 1** (2p.)
Load the provided mushroom catalogue and explore it thoroughly. Make a detailed dataset analysis and present some statistics in the form of Matplotlib or Seaborn visualisations. Pre-process the data if necessary.

Define your own Common/Rare/Legendary tier based on species frequency, feature rarity, or a combination.

Your EDA should cover at minimum: class distributions, missing value patterns, feature type identification, and correlation or association analysis between features. For each data quality issue you find, document what you found, what decision you made, and why. Every preprocessing step must be documented and explained.

#### **Task 2** (1p.)
Based on the analysis from Task 1, perform Feature Selection. State which features you will use for classification and show why you are choosing them. Train at least two simple classifiers (e.g. K-Nearest Neighbours, Decision Tree, etc.) to predict a target variable (family).

#### **Task 3** (1.5p.)
Train at least two ensemble classifiers. You can use: Random Forest, Gradient Boosting, XGBoost, Ada Boost, Extra Trees, or another ensemble method you consider suitable.

#### **Task 4** (1.5p.)
Show the performance of all models from Tasks 2 and 3. Use multiple metrics appropriate for imbalanced classification and explain why you chose them specifically. Draw conclusions based on the obtained results and the performance of each model.

#### **Task 5** (2p.)
Cluster your data using a clustering algorithm (e.g. K-Means or another clustering algorithm you consider suitable). Determine the optimal number of clusters and show a visual representation using dimensionality reduction. Analyse what the clusters capture. Do they correspond to edibility, morphology, species groups, or something else?

> **Hint:** Choose a categorical feature you believe groups mushrooms into meaningful categories. Apply the clustering algorithm using the remaining features, excluding the one you selected. This allows you to discover whether the algorithm can identify those same natural groupings based solely on mushroom characteristics. Compare the clustering results with your classification results from Task 4.

#### **Task 6** (1p.)
Draw conclusions on the obtained clusters and classification results. Analyse where clustering and classification agree and disagree. Discuss what each approach reveals about the dataset that the other misses.

#### **Report & Presentation** (1p.)
Clear explanations, report formatting, code quality, comments in the code, docstrings, visualisations if relevant etc.

---

*Good Luck, and may your mushrooms be Legendary!*