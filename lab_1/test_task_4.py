from production import IF, AND, THEN, OR, NOT, match, populate, simplify
from rules import FLAG_RULES  # or wherever your rules are defined
from production import backward_chain 

def pretty_goal_tree(node, indent=0):
    """
    Recursively render an AND/OR/leaf goal tree (as returned by
    backward_chain) as an indented, human-readable string.
    """
    pad = "  " * indent

    if isinstance(node, AND):
        lines = [f"{pad}AND:"]
        for child in node:
            lines.append(pretty_goal_tree(child, indent + 1))
        return "\n".join(lines)

    elif isinstance(node, OR):
        lines = [f"{pad}OR:"]
        for child in node:
            lines.append(pretty_goal_tree(child, indent + 1))
        return "\n".join(lines)

    else:
        # leaf: a plain fact string (or an unmatched hypothesis)
        return f"{pad}- {node}"
    
if __name__ == '__main__':
    goal = 'flag is Norway'
    results = backward_chain(FLAG_RULES, goal, verbose=True)
    
    print(f"\n--- Resulting Goal Tree for {goal} ---")
    print(pretty_goal_tree(results))
