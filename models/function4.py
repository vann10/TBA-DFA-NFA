# models/function4.py

def parse_dfa(dfa):
    return {
        "states": set(dfa["states"]),
        "alphabet": set(dfa["alphabet"]),
        "start": dfa["start"],
        "accept": set(dfa["accept"]),
        "delta": dfa["delta"]
    }

def compare_dfas(dfa1_json, dfa2_json):
    dfa1 = parse_dfa(dfa1_json)
    dfa2 = parse_dfa(dfa2_json)

    # Method 1: Minimization approach
    min_dfa1 = minimize_dfa(dfa1)
    min_dfa2 = minimize_dfa(dfa2)
    equivalent_by_minimization = are_isomorphic(min_dfa1, min_dfa2)

    # Method 2: Table filling approach
    equivalent_by_table = table_filling_equivalence(dfa1, dfa2)

    # Both methods should give same result
    equivalent = equivalent_by_minimization and equivalent_by_table

    return {
        "equivalent": equivalent,
        "method1_result": equivalent_by_minimization,
        "method2_result": equivalent_by_table,
        "details": {
            # Original DFA details (before minimization)
            "original_transition1": dfa_to_table(dfa1),
            "original_transition2": dfa_to_table(dfa2),
            "original_diagram1": dfa_to_mermaid(dfa1),
            "original_diagram2": dfa_to_mermaid(dfa2),
            # Minimized DFA details
            "minimized_transition1": dfa_to_table(min_dfa1),
            "minimized_transition2": dfa_to_table(min_dfa2),
            "minimized_diagram1": dfa_to_mermaid(min_dfa1),
            "minimized_diagram2": dfa_to_mermaid(min_dfa2),
            # Analysis details
            "dfa1_state_count": len(dfa1["states"]),
            "dfa2_state_count": len(dfa2["states"]),
            "min_dfa1_state_count": len(min_dfa1["states"]),
            "min_dfa2_state_count": len(min_dfa2["states"]),
        }
    }

def show_dfa_analysis(dfa_json, dfa_name="DFA"):
    """Function to display comprehensive DFA analysis including original and minimized versions"""
    dfa = parse_dfa(dfa_json)
    min_dfa = minimize_dfa(dfa)
    
    print(f"\n=== {dfa_name} Analysis ===")
    
    print(f"\n--- Original {dfa_name} ---")
    print("Transition Table:")
    print(dfa_to_table(dfa))
    print(f"\nState Diagram (Mermaid):")
    print(dfa_to_mermaid(dfa))
    print(f"Number of states: {len(dfa['states'])}")
    
    print(f"\n--- Minimized {dfa_name} ---")
    print("Transition Table:")
    print(dfa_to_table(min_dfa))
    print(f"\nState Diagram (Mermaid):")
    print(dfa_to_mermaid(min_dfa))
    print(f"Number of states: {len(min_dfa['states'])}")
    
    reduction = len(dfa['states']) - len(min_dfa['states'])
    if reduction > 0:
        print(f"\nState reduction: {reduction} states removed")
    else:
        print(f"\nNo state reduction needed (DFA was already minimal)")
    
    return {
        "original": {
            "dfa": dfa,
            "table": dfa_to_table(dfa),
            "diagram": dfa_to_mermaid(dfa),
            "state_count": len(dfa['states'])
        },
        "minimized": {
            "dfa": min_dfa,
            "table": dfa_to_table(min_dfa),
            "diagram": dfa_to_mermaid(min_dfa),
            "state_count": len(min_dfa['states'])
        },
        "reduction": reduction
    }

def minimize_dfa(dfa):
    """Minimize DFA using partition refinement algorithm"""
    states = dfa["states"]
    alphabet = dfa["alphabet"]
    delta = dfa["delta"]
    accept = dfa["accept"]
    
    # Initial partition: accepting vs non-accepting states
    accepting = accept
    non_accepting = states - accept
    
    partitions = []
    if accepting:
        partitions.append(accepting)
    if non_accepting:
        partitions.append(non_accepting)
    
    changed = True
    while changed:
        changed = False
        new_partitions = []
        
        for partition in partitions:
            # Try to split this partition
            split_groups = {}
            
            for state in partition:
                # Create signature for this state
                signature = []
                for symbol in sorted(alphabet):
                    next_state = delta.get(state, {}).get(symbol)
                    if next_state:
                        # Find which partition the next state belongs to
                        partition_index = -1
                        for i, p in enumerate(partitions):
                            if next_state in p:
                                partition_index = i
                                break
                        signature.append(partition_index)
                    else:
                        signature.append(-1)  # No transition
                
                signature = tuple(signature)
                if signature not in split_groups:
                    split_groups[signature] = set()
                split_groups[signature].add(state)
            
            # Add split groups to new partitions
            if len(split_groups) > 1:
                changed = True
            
            for group in split_groups.values():
                new_partitions.append(group)
        
        partitions = new_partitions
    
    # Create minimized DFA
    # Map each state to its partition representative
    state_to_partition = {}
    partition_reps = {}
    
    for i, partition in enumerate(partitions):
        rep = f"q{i}"
        partition_reps[rep] = partition
        for state in partition:
            state_to_partition[state] = rep
    
    # Build minimized DFA
    min_states = set(partition_reps.keys())
    min_start = state_to_partition[dfa["start"]]
    min_accept = set()
    min_delta = {}
    
    # Determine accepting states in minimized DFA
    for rep, partition in partition_reps.items():
        if any(state in accept for state in partition):
            min_accept.add(rep)
    
    # Build transition function
    for rep, partition in partition_reps.items():
        min_delta[rep] = {}
        # Take any state from partition as representative
        representative_state = next(iter(partition))
        for symbol in alphabet:
            if representative_state in delta and symbol in delta[representative_state]:
                target = delta[representative_state][symbol]
                min_target = state_to_partition[target]
                min_delta[rep][symbol] = min_target
    
    return {
        "states": min_states,
        "alphabet": alphabet,
        "start": min_start,
        "accept": min_accept,
        "delta": min_delta
    }

def are_isomorphic(dfa1, dfa2):
    """Check if two minimized DFAs are isomorphic"""
    if len(dfa1["states"]) != len(dfa2["states"]):
        return False
    
    if dfa1["alphabet"] != dfa2["alphabet"]:
        return False
    
    if len(dfa1["accept"]) != len(dfa2["accept"]):
        return False
    
    # Try to find a mapping between states
    def find_mapping(mapping, states1, states2):
        if not states1:
            return True
        
        state1 = states1[0]
        remaining1 = states1[1:]
        
        for state2 in states2:
            if state2 in mapping.values():
                continue
            
            # Check if this mapping is consistent
            valid = True
            
            # Check if both are accepting or both are non-accepting
            if (state1 in dfa1["accept"]) != (state2 in dfa2["accept"]):
                valid = False
            
            if valid:
                # Check transitions
                for symbol in dfa1["alphabet"]:
                    next1 = dfa1["delta"].get(state1, {}).get(symbol)
                    next2 = dfa2["delta"].get(state2, {}).get(symbol)
                    
                    if next1 is None and next2 is None:
                        continue
                    if next1 is None or next2 is None:
                        valid = False
                        break
                    
                    if next1 in mapping:
                        if mapping[next1] != next2:
                            valid = False
                            break
                    elif next2 in mapping.values():
                        valid = False
                        break
            
            if valid:
                new_mapping = mapping.copy()
                new_mapping[state1] = state2
                
                remaining2 = [s for s in states2 if s != state2]
                if find_mapping(new_mapping, remaining1, remaining2):
                    return True
        
        return False
    
    # Start mapping from start states
    return find_mapping({dfa1["start"]: dfa2["start"]}, 
                       [s for s in dfa1["states"] if s != dfa1["start"]], 
                       [s for s in dfa2["states"] if s != dfa2["start"]])

def table_filling_equivalence(dfa1, dfa2):
    """Use table filling algorithm to check equivalence"""
    # Create combined state space
    states1 = list(dfa1["states"])
    states2 = list(dfa2["states"])
    alphabet = dfa1["alphabet"] | dfa2["alphabet"]
    
    # Create distinguishability table
    table = {}
    
    # Initialize table - mark pairs where one is accepting and other is not
    for s1 in states1:
        for s2 in states2:
            pair = (s1, s2)
            is_s1_accepting = s1 in dfa1["accept"]
            is_s2_accepting = s2 in dfa2["accept"]
            
            if is_s1_accepting != is_s2_accepting:
                table[pair] = True  # Distinguishable
            else:
                table[pair] = False  # Not yet marked
    
    # Iteratively mark distinguishable pairs
    changed = True
    while changed:
        changed = False
        for s1 in states1:
            for s2 in states2:
                pair = (s1, s2)
                if not table.get(pair, False):  # If not already marked
                    # Check if any transition leads to distinguishable states
                    for symbol in alphabet:
                        next1 = dfa1["delta"].get(s1, {}).get(symbol)
                        next2 = dfa2["delta"].get(s2, {}).get(symbol)
                        
                        # If one has transition but other doesn't
                        if (next1 is None) != (next2 is None):
                            table[pair] = True
                            changed = True
                            break
                        
                        # If both have transitions, check if they lead to distinguishable states
                        if next1 and next2:
                            next_pair = (next1, next2)
                            if table.get(next_pair, False):
                                table[pair] = True
                                changed = True
                                break
    
    # Check if start states are distinguishable
    start_pair = (dfa1["start"], dfa2["start"])
    return not table.get(start_pair, False)

def dfa_to_table(dfa):
    """Convert DFA to transition table string"""
    if not dfa["states"]:
        return "Empty DFA"
    
    header = ["State"] + sorted(dfa["alphabet"])
    lines = ["\t".join(header)]
    
    for state in sorted(dfa["states"]):
        row = [state]
        if state in dfa["accept"]:
            row[0] += "*"  # Mark accepting states
        if state == dfa["start"]:
            row[0] = "→" + row[0]  # Mark start state
            
        for symbol in sorted(dfa["alphabet"]):
            target = dfa["delta"].get(state, {}).get(symbol, "-")
            row.append(target)
        lines.append("\t".join(row))
    
    return "\n".join(lines)

def dfa_to_mermaid(dfa):
    """Convert DFA to Mermaid diagram format"""
    lines = ["stateDiagram-v2"]
    
    # Mark start state
    if dfa["start"]:
        lines.append(f"[*] --> {dfa['start']}")
    
    # Add accepting states
    for state in dfa["accept"]:
        lines.append(f"{state} --> [*]")
    
    # Add transitions
    for state in sorted(dfa["states"]):
        for symbol, target in dfa["delta"].get(state, {}).items():
            lines.append(f"{state} --> {target}: {symbol}")
    
    return "\n".join(lines)

# Example usage function
def example_usage():
    """Example of how to use the modified functions"""
    
    # Sample DFA 1
    dfa1 = {
        "states": ["q0", "q1", "q2", "q3"],
        "alphabet": ["a", "b"],
        "start": "q0",
        "accept": ["q3"],
        "delta": {
            "q0": {"a": "q1", "b": "q2"},
            "q1": {"a": "q3", "b": "q2"},
            "q2": {"a": "q1", "b": "q3"},
            "q3": {"a": "q3", "b": "q3"}
        }
    }
    
    # Sample DFA 2
    dfa2 = {
        "states": ["p0", "p1", "p2"],
        "alphabet": ["a", "b"],
        "start": "p0",
        "accept": ["p2"],
        "delta": {
            "p0": {"a": "p1", "b": "p1"},
            "p1": {"a": "p2", "b": "p2"},
            "p2": {"a": "p2", "b": "p2"}
        }
    }
    
    # Show individual DFA analysis
    print("=== Individual DFA Analysis ===")
    analysis1 = show_dfa_analysis(dfa1, "DFA1")
    analysis2 = show_dfa_analysis(dfa2, "DFA2")
    
    # Compare DFAs
    print("\n=== DFA Comparison ===")
    comparison = compare_dfas(dfa1, dfa2)
    print(f"DFAs are equivalent: {comparison['equivalent']}")
    print(f"Method 1 (Minimization): {comparison['method1_result']}")
    print(f"Method 2 (Table Filling): {comparison['method2_result']}")
    
    return comparison

if __name__ == "__main__":
    example_usage()