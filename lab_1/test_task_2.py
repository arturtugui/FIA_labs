from production import forward_chain
from rules_example_zookeeper import ZOOKEEPER_RULES, ZOO_DATA
from rules import FLAG_RULES, FLAG_DATA

if __name__ == '__main__':
    # Run forward chaining with verbose=True to see the step-by-step trace
    results = forward_chain(FLAG_RULES, FLAG_DATA, verbose=True)
    
    print("\n--- Final Inferred Facts ---")
    for fact in results:
        print(fact)