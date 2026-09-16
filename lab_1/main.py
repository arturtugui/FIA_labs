"""
main.py — Task 6: Interactive Flag Expert System.

Combines:
  * Backward chaining (production.backward_chain) to build, for every
    candidate hypothesis, the AND/OR/leaf goal tree that would prove it.
  * Question generation (questions.py) to turn an unresolved leaf fact
    into something we can actually ask the user.
  * Forward chaining (production.forward_chain) to check, after every
    new answer, whether enough facts are now known to conclusively
    derive one of the hypotheses.

The backward-chained trees are also used, independently of forward
chaining, to *prune* hypotheses that a "no" (or otherwise
contradicting) answer has made logically impossible. That pruning is
what keeps the interview from wasting questions on flags an earlier
answer already ruled out.
"""

from production import AND, OR, backward_chain, forward_chain
from rules import FLAG_RULES
from questions import QUESTIONS, get_question, ask, UNKNOWN

SUBJECT = "flag"
HYPOTHESES = {
    "Switzerland": f"{SUBJECT} is Switzerland",
    "Greece": f"{SUBJECT} is Greece",
    "Finland": f"{SUBJECT} is Finland",
    "Sweden": f"{SUBJECT} is Sweden",
    "Norway": f"{SUBJECT} is Norway",
    "Iceland": f"{SUBJECT} is Iceland",
}


# ---------------------------------------------------------------------------
# Build a fact -> question-id lookup once, by asking every question's
# resolve() function what facts it can produce, for every legal answer
# it accepts. This keeps questions.py the single source of truth: the
# fact-to-question relationship is never hardcoded a second time here.
# ---------------------------------------------------------------------------
def _build_fact_to_question():
    mapping = {}
    for q in QUESTIONS:
        if q["qtype"] == "yes_no":
            candidate_answers = ["yes", "no"]
        elif q["qtype"] == "number_input":
            candidate_answers = [2]
        elif q["qtype"] == "single_choice":
            candidate_answers = [value for _label, value in q["options"]]
        else:
            continue  # checkbox question is demoed separately, not in the main interview

        for ans in candidate_answers:
            result = q["resolve"](ans)
            if result is UNKNOWN:
                continue
            for template_fact in result:
                mapping[template_fact] = q["id"]
    return mapping


FACT_TO_QUESTION = _build_fact_to_question()


def _templatize(concrete_fact):
    """'flag is small cross' -> '(?x) is small cross' (reverses populate())."""
    return concrete_fact.replace(SUBJECT, "(?x)", 1)


def question_for_fact(concrete_fact):
    """Return the question dict responsible for resolving `concrete_fact`, or None."""
    qid = FACT_TO_QUESTION.get(_templatize(concrete_fact))
    return get_question(qid) if qid else None


# ---------------------------------------------------------------------------
# Three-valued evaluation of a backward-chained goal tree against the
# facts known so far. True/False are certain; None means "still needs
# more answers before this hypothesis can be decided".
# ---------------------------------------------------------------------------
def evaluate(node, facts):
    """Evaluate an AND/OR/leaf goal tree given a dict of known facts.

    Returns True, False, or None (undetermined) using short-circuit,
    three-valued logic: an AND is False as soon as any child is False
    even if others are still unknown; an OR is True as soon as any
    child is True even if others are still unknown.
    """
    if isinstance(node, AND):
        values = [evaluate(child, facts) for child in node]
        if any(v is False for v in values):
            return False
        if any(v is None for v in values):
            return None
        return True

    if isinstance(node, OR):
        values = [evaluate(child, facts) for child in node]
        if any(v is True for v in values):
            return True
        if any(v is None for v in values):
            return None
        return False

    # leaf fact: unknown until we've asked about it
    return facts.get(node)


def collect_unknown_leaves(node, facts, out):
    """Recursively gather leaf facts in `node` that aren't in `facts` yet."""
    if isinstance(node, (AND, OR)):
        for child in node:
            collect_unknown_leaves(child, facts, out)
    elif node not in facts:
        out.append(node)


# ---------------------------------------------------------------------------
# The interview
# ---------------------------------------------------------------------------
def run_interview(input_fn=input, print_fn=print):
    """Run one interactive session and return the matched flag name, or None."""
    print_fn("Welcome to the Flag Expert System!\n")

    # Pre-filter: not part of any goal tree (every flag here has a cross),
    # so it can't be discovered by walking the trees -- ask it explicitly.
    has_cross_q = get_question("has_cross")
    if ask(has_cross_q, subject=SUBJECT, input_fn=input_fn, print_fn=print_fn) is UNKNOWN:
        print_fn("\nThis doesn't match any flag in my knowledge base.")
        return None

    trees = {name: backward_chain(FLAG_RULES, goal) for name, goal in HYPOTHESES.items()}
    facts = {}       # concrete_fact -> True/False, used for pruning
    known_true = []  # concrete facts known True, fed to forward_chain

    while True:
        alive = {name: tree for name, tree in trees.items()
                 if evaluate(tree, facts) is not False}

        if not alive:
            print_fn("\nNo matching flag found in the knowledge base.")
            return None

        # Forward chaining answers "are we done yet?" -- data-driven,
        # independent of which tree we happened to be walking.
        derived = forward_chain(FLAG_RULES, tuple(known_true))
        matched = [name for name, goal in HYPOTHESES.items() if goal in derived]
        if matched:
            print_fn(f"\nBased on your answers, this flag is {matched[0]}.")
            return matched[0]

        # Backup: if only one hypothesis survives pruning and its own
        # tree is already fully satisfied, don't wait on forward_chain.
        if len(alive) == 1:
            (name, tree), = alive.items()
            if evaluate(tree, facts) is True:
                print_fn(f"\nBased on your answers, this flag is {name}.")
                return name

        # Pick the next fact to ask about: among leaves still unknown in
        # at least one *surviving* candidate, prefer whichever fact is
        # shared by the most surviving candidates -- it prunes the most
        # per question asked.
        counts = {}
        for tree in alive.values():
            leaves = []
            collect_unknown_leaves(tree, facts, leaves)
            for leaf in set(leaves):
                counts[leaf] = counts.get(leaf, 0) + 1

        if not counts:
            print_fn("\nNo matching flag found in the knowledge base.")
            return None

        next_fact = max(counts, key=counts.get)
        question = question_for_fact(next_fact)
        if question is None:
            # No question covers this leaf (shouldn't happen if
            # questions.py covers every fact in fc_as_text.md) -- drop
            # it rather than crash or loop forever on it.
            facts[next_fact] = False
            continue

        answer = ask(question, subject=SUBJECT, input_fn=input_fn, print_fn=print_fn)
        if answer is UNKNOWN:
            print_fn("\nNo matching flag found in the knowledge base.")
            return None

        for fact, value in answer.items():
            facts[fact] = value
            if value:
                known_true.append(fact)


if __name__ == "__main__":
    run_interview()
