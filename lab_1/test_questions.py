"""
demo_questions.py — scripted proof that questions.py covers all three
required question types (yes/no, single choice, multi-select) and that
the UNKNOWN sentinel fires correctly. Uses canned answers instead of
real stdin so the transcript is reproducible for the report.
"""

from questions import QUESTIONS, CROSS_DESCRIPTION_QUESTION, ask, get_question, UNKNOWN


def scripted_input(answers):
    """Returns an input_fn that yields answers from `answers` in order."""
    it = iter(answers)
    def _input(_prompt):
        return next(it)
    return _input


def run(question, answers, label):
    print(f"\n=== {label} ===")
    result = ask(question, input_fn=scripted_input(answers), print_fn=print)
    print("-> facts:", result)
    return result


if __name__ == "__main__":
    # 1. YESNO
    run(get_question("stripes"), ["yes"], "Yes/No question")

    # 2. CHOICE
    run(get_question("cross_color"), ["2"], "Single-choice question (blue)")
    # option 2 in the list is "blue"

    # 3. CHECKBOX (valid combo: big + outlined -> Norway/Iceland shape)
    run(CROSS_DESCRIPTION_QUESTION, ["1,2"], "Multi-select question (valid combo)")

    # 4. CHECKBOX (invalid combo -> UNKNOWN)
    result = run(CROSS_DESCRIPTION_QUESTION, ["1,2,3"],
                 "Multi-select question (invalid combo: big+outlined+centered)")
    assert result == UNKNOWN, "Expected UNKNOWN for an impossible combination"

    # 5. CHOICE leading to UNKNOWN (unmodeled color)
    result = run(get_question("cross_color"), ["4"], "Single-choice -> UNKNOWN (white)")
    assert result == UNKNOWN, "Expected UNKNOWN for an unmodeled color"

    # 6. YESNO leading to UNKNOWN (no cross at all)
    result = run(get_question("has_cross"), ["no"], "Yes/No -> UNKNOWN (no cross)")
    assert result == UNKNOWN, "Expected UNKNOWN when the flag has no cross"

    print("\nAll checks passed.")
