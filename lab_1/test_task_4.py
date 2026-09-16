from production import backward_chain, forward_chain
from rules_example_zookeeper import ZOOKEEPER_RULES, ZOO_DATA
from rules import FLAG_RULES, FLAG_DATA

if __name__ == '__main__':
    results = backward_chain(FLAG_RULES, 'flag is Finland', verbose=True)
    
    print("\n--- Resulting Goal Tree ---")
    for fact in results:
        print(fact)