# Flag Expert System Goal Tree Documentation

## 1. Hypotheses (Final Outcomes / Flags)
* Switzerland
* Greece
* Finland
* Sweden
* Norway
* Iceland

---

## 2. Facts (Initial Input Features)
* `outlined cross`
* `big cross`
* `not outlined cross`
* `tricolor`
* `small cross`
* `bicolor`
* `stripes`
* `off-center cross`
* `centered cross`
* `red cross`
* `blue cross`
* `yellow cross`

---

## 3. Rule Mapping Breakdown (`R1` to `R15`)

### Switzerland Branch
* **`R1` (AND Gate):** Takes `small cross` AND `bicolor` $\rightarrow$ produces intermediate state `bicolor AND small cross`.
* **`R2` (AND Gate):** Takes `bicolor AND small cross (aka R1)` AND `centered cross` $\rightarrow$ triggers **Switzerland**.
* **`R3` (AND Gate):** Takes `off-center cross` and bicolor AND small cross (aka R1) triggers **Greece**

### Greece Branch
* **`R4` (OR Gate):** Takes `off-center cross` and `small cross` $\rightarrow$ produces intermediate state `small OR off-center cross`.
* **`R5` (AND Gate):** Takes `small OR off-center cross (aka R4)` AND `stripes` $\rightarrow$ triggers **Greece**.

### Finland & Sweden Branch (Non-Outlined Nordic Crosses)
* **`R6` (AND Gate):** Takes `big cross` AND `not outlined cross` $\rightarrow$ produces intermediate state `big AND not outlined cross`.
* **`R7` (OR Gate):** Takes `big AND not outlined cross (aka R6)` (merged with `bicolor` paths) $\rightarrow$ produces intermediate state `R6 OR bicolor`.
* **`R8` (AND Gate):** Takes `R6 OR bicolor (aka R7)` AND `off-center cross` $\rightarrow$ produces intermediate state `R7 AND off-center cross`.
* **`R9` (AND Gate):** Takes `R7 AND off-center cross (aka R8)` AND `yellow cross` $\rightarrow$ triggers **Sweden**.
* **`R10` (AND Gate):** Takes `R7 AND off-center cross (aka R8)` AND `blue cross` $\rightarrow$ triggers **Finland**.

### Iceland & Norway Branch (Outlined / Tricolor Nordic Crosses)
* **`R11` (AND Gate):** Takes `outlined cross` AND `big cross` $\rightarrow$ produces intermediate state `big AND outline cross`.
* **`R12` (OR Gate):** Takes `big AND outline cross (aka R11)` OR `tricolor` $\rightarrow$ produces intermediate state `R11 OR tricolor`.
* **`R13` (AND Gate):** Takes `R11 OR tricolor (aka R12)` AND `off-center cross` $\rightarrow$ produces intermediate state `R12 AND off-center`.
* **`R14` (AND Gate):** Evaluates `R12 AND off-center (aka R13)` with specific color configurations $\rightarrow$ triggers **Norway**.
* **`R15` (AND Gate):** Takes `R12 AND off-center (aka R13)` AND `red cross` $\rightarrow$ triggers **Iceland**.