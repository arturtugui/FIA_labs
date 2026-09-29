"""
questions.py — Task 5: Question generation for the Flag Expert System.

Maps the leaf facts used by FLAG_RULES (see rules.py) to human-readable
questions the interview (Task 6) can ask the user. Three question types
are implemented:
    - YESNO     : simple yes/no question
    - CHOICE    : single choice among mutually-exclusive options
    - CHECKBOX  : multi-select, validated against the combinations that
                  actually occur in the knowledge base

A single question can resolve several leaf facts at once (e.g. "how many
colors?" resolves both 'is bicolor' and 'is tricolor' from one answer).
This keeps the interview short and, more importantly, makes it
impossible for two related questions to produce a self-contradictory
answer (e.g. "centered = no" and "off-center = no" at once) since only
one question governs both facts.

Any answer that cannot correspond to a flag in the knowledge base
(an unmodeled color, an unmodeled cross-attribute combination, "no
cross at all", etc.) resolves to the UNKNOWN sentinel rather than a
fact dict, so the caller can immediately end the interview with a
"no matching flag" result instead of asking further questions.
"""

from production import populate

# ---------------------------------------------------------------------------
# Question type constants
# ---------------------------------------------------------------------------
YESNO = "yes_no"
CHOICE = "single_choice"
NUMBER = "number_input"
CHECKBOX = "multi_select"

UNKNOWN = "UNKNOWN"  # sentinel: this answer rules out every hypothesis


# ---------------------------------------------------------------------------
# Main question bank (the interview path used for the standard demo run)
# ---------------------------------------------------------------------------
# Each question is a dict:
#   id      - unique identifier
#   text    - the question shown to the user
#   qtype   - YESNO / CHOICE / CHECKBOX
#   options - for CHOICE/CHECKBOX: list of (label, value) shown to the user
#   resolve - function(answer) -> dict[fact_template, bool] | UNKNOWN
#             fact_template uses "(?x)" exactly like rules.py, so the
#             result can be populate()-d directly into a concrete fact.

QUESTIONS = [
    {
        "id": "has_cross",
        "text": "Does the flag have a cross on it?",
        "qtype": YESNO,
        "resolve": lambda ans: (
            UNKNOWN if ans == "no" else {}
            # "yes" adds no new fact by itself -- every flag in this KB
            # has a cross. This question exists purely as an early
            # filter, to reject non-cross flags before spending four
            # more questions on cross detail.
        ),
    },
    {
        "id": "color_count",
        "text": "How many colors does the flag have?",
        "qtype": NUMBER,
        "resolve": lambda ans: (
            {"(?x) is bicolor": True, "(?x) is tricolor": False} if ans == 2 else
            {"(?x) is bicolor": False, "(?x) is tricolor": True} if ans == 3 else
            UNKNOWN
        ),
    },
    {
        "id": "stripes",
        "text": "Does the flag have stripes?",
        "qtype": YESNO,
        "resolve": lambda ans: {"(?x) has stripes": ans == "yes"},
    },
    {
        "id": "cross_color",
        "text": "What color is the cross?",
        "qtype": CHOICE,
        "options": [("Red", "red"), ("Blue", "blue"), ("Yellow", "yellow"),
                    ("White", "white"), ("Other", "other")],
        "resolve": lambda ans: (
            {"(?x) is red cross": True, "(?x) is blue cross": False, "(?x) is yellow cross": False} if ans == "red" else
            {"(?x) is red cross": False, "(?x) is blue cross": True, "(?x) is yellow cross": False} if ans == "blue" else
            {"(?x) is red cross": False, "(?x) is blue cross": False, "(?x) is yellow cross": True} if ans == "yellow" else
            UNKNOWN  # white / other: no rule in the KB uses these colors
        ),
    },
    {
        "id": "cross_position",
        "text": "Is the cross centered on the flag?",
        "qtype": YESNO,
        "resolve": lambda ans: (
            {"(?x) is centered cross": True, "(?x) is off-center cross": False}
            if ans == "yes" else
            {"(?x) is centered cross": False, "(?x) is off-center cross": True}
        ),
    },
    {
        "id": "cross_size",
        "text": "Is the cross big?",
        "qtype": YESNO,
        "resolve": lambda ans: (
            {"(?x) is big cross": True, "(?x) is small cross": False}
            if ans == "yes" else
            {"(?x) is big cross": False, "(?x) is small cross": True}
        ),
    },
    {
        "id": "cross_outline",
        "text": "Does the cross have an outline (a border in a different color)?",
        "qtype": YESNO,
        "resolve": lambda ans: (
            {"(?x) is outlined cross": True, "(?x) is not outlined cross": False}
            if ans == "yes" else
            {"(?x) is outlined cross": False, "(?x) is not outlined cross": True}
        ),
    },
]


# ---------------------------------------------------------------------------
# Alternate question: checkbox / multi-select (third-type demo)
# ---------------------------------------------------------------------------
# Bundles size + outline + position into a single multi-select. Kept
# separate from the main interview path (see roadmap/report discussion):
# it shortens the interview, which is fine, but is demonstrated on its
# own rather than substituted into the main run, so the main run stays
# the depth-4 example. Only combinations that actually occur among
# FLAG_RULES are valid; every other subset is UNKNOWN.

_VALID_CHECKBOX_COMBOS = {
    frozenset({"big", "outlined"}): True,  # Norway, Iceland
    frozenset({"big"}): True,              # Sweden, Finland
    frozenset({"centered"}): True,         # Switzerland
    frozenset(): True,                     # Greece
}


def _resolve_checkbox(selected):
    selected = frozenset(selected)
    if selected not in _VALID_CHECKBOX_COMBOS:
        return UNKNOWN
    return {
        "(?x) is big cross": "big" in selected,
        "(?x) is small cross": "big" not in selected,
        "(?x) is outlined cross": "outlined" in selected,
        "(?x) is not outlined cross": "outlined" not in selected,
        "(?x) is centered cross": "centered" in selected,
        "(?x) is off-center cross": "centered" not in selected,
    }


CROSS_DESCRIPTION_QUESTION = {
    "id": "cross_description",
    "text": "Check all boxes that describe the cross:",
    "qtype": CHECKBOX,
    "options": [("Big", "big"), ("Outlined", "outlined"), ("Centered", "centered")],
    "resolve": _resolve_checkbox,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_question(question_id):
    """Look up a question spec by its id."""
    for q in QUESTIONS + [CROSS_DESCRIPTION_QUESTION]:
        if q["id"] == question_id:
            return q
    raise KeyError(f"No such question: {question_id!r}")


def ask(question, subject="flag", input_fn=input, print_fn=print):
    """
    Present `question` to the user via input_fn/print_fn and return the
    resulting facts as {concrete_fact_string: bool}, or UNKNOWN if the
    answer rules out every hypothesis in the knowledge base.

    `subject` fills in "(?x)" in the returned fact strings -- this KB
    always reasons about a single flag at a time, so it defaults to
    the literal word "flag" (matching the fact style already used in
    rules.py, e.g. "flag is red cross").
    """
    print_fn(question["text"])

    if question["qtype"] == YESNO:
        raw = input_fn("(y/n): ").strip().lower()
        while raw not in ("yes", "y", "no", "n"):
            raw = input_fn("Please answer y or n: ").strip().lower()
        ans = "yes" if raw in ("yes", "y") else "no"
        facts = question["resolve"](ans)

    elif question["qtype"] == NUMBER:
        raw = input_fn("Enter a natural number greater than 0: ").strip()
        while not raw.isdigit() or int(raw) == 0:
            raw = input_fn("Please enter a natural number greater than 0: ").strip()
        facts = question["resolve"](int(raw))

    elif question["qtype"] == CHOICE:
        for i, (label, _value) in enumerate(question["options"], 1):
            print_fn(f"  {i}. {label}")
        raw = input_fn(f"Choose 1-{len(question['options'])}: ").strip()
        while not raw.isdigit() or not (1 <= int(raw) <= len(question["options"])):
            raw = input_fn("Please enter a valid option number: ").strip()
        _label, value = question["options"][int(raw) - 1]
        facts = question["resolve"](value)

    elif question["qtype"] == CHECKBOX:
        for i, (label, _value) in enumerate(question["options"], 1):
            print_fn(f"  {i}. {label}")
        raw = input_fn("Enter option numbers separated by commas (blank for none): ").strip()
        chosen_idxs = [int(x) for x in raw.split(",") if x.strip().isdigit()]
        chosen = {question["options"][i - 1][1] for i in chosen_idxs
                  if 1 <= i <= len(question["options"])}
        facts = question["resolve"](chosen)

    else:
        raise ValueError(f"Unknown question type: {question['qtype']}")

    if facts is UNKNOWN:
        return UNKNOWN

    return {populate(fact, {"x": subject}): value for fact, value in facts.items()}
