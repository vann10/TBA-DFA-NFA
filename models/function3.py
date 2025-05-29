# ===== PINDAHKAN SEMUA FUNGSI MINIMIZATION ANDA KE SINI =====

from typing import Dict, List, Set, Tuple, Optional

class DFA:
    """Represents a Deterministic Finite Automaton"""
    
    def __init__(self, states: List[str], alphabet: List[str], 
                 transitions: Dict[str, Dict[str, str]], 
                 start_state: str, final_states: List[str]):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = set(final_states)
        
        # Validate DFA
        self._validate()
    
    def _validate(self):
        """Validate the DFA structure"""
        if self.start_state not in self.states:
            raise ValueError(f"Start state '{self.start_state}' not in states")
        
        for final_state in self.final_states:
            if final_state not in self.states:
                raise ValueError(f"Final state '{final_state}' not in states")

class DFAMinimizer:
    """Class for minimizing DFA using partition refinement algorithm"""
    
    def __init__(self, dfa: DFA):
        self.original_dfa = dfa
        self.state_mapping = {}
    
    def find_reachable_states(self) -> Set[str]:
        """Find all reachable states from start state"""
        reachable = set()
        queue = [self.original_dfa.start_state]
        reachable.add(self.original_dfa.start_state)
        
        while queue:
            current_state = queue.pop(0)
            for symbol in self.original_dfa.alphabet:
                if (current_state in self.original_dfa.transitions and 
                    symbol in self.original_dfa.transitions[current_state]):
                    next_state = self.original_dfa.transitions[current_state][symbol]
                    if next_state not in reachable:
                        reachable.add(next_state)
                        queue.append(next_state)
        
        return reachable
    
    def create_initial_partition(self, reachable_states: Set[str]) -> List[List[str]]:
        """Create initial partition (final vs non-final states)"""
        final_states = reachable_states & self.original_dfa.final_states
        non_final_states = reachable_states - self.original_dfa.final_states
        
        partitions = []
        if non_final_states:
            partitions.append(list(non_final_states))
        if final_states:
            partitions.append(list(final_states))
        
        return partitions
    
    def are_states_equivalent(self, state1: str, state2: str, 
                            partitions: List[List[str]]) -> bool:
        """Check if two states are equivalent based on current partition"""
        for symbol in self.original_dfa.alphabet:
            next1 = self.original_dfa.transitions.get(state1, {}).get(symbol)
            next2 = self.original_dfa.transitions.get(state2, {}).get(symbol)
            
            if next1 is None or next2 is None:
                if next1 != next2:
                    return False
                continue
            
            # Find partition for each next state
            partition1 = self.find_partition_for_state(next1, partitions)
            partition2 = self.find_partition_for_state(next2, partitions)
            
            if partition1 != partition2:
                return False
        
        return True
    
    def find_partition_for_state(self, state: str, partitions: List[List[str]]) -> int:
        """Find which partition contains the given state"""
        for i, partition in enumerate(partitions):
            if state in partition:
                return i
        return -1
    
    def refine_partitions(self, partitions: List[List[str]]) -> List[List[str]]:
        """Refine partitions until no changes occur"""
        changed = True
        
        while changed:
            changed = False
            new_partitions = []
            
            for partition in partitions:
                if len(partition) <= 1:
                    new_partitions.append(partition)
                    continue
                
                # Create sub-partitions based on equivalence
                sub_partitions = []
                processed = set()
                
                for state in partition:
                    if state in processed:
                        continue
                    
                    equivalent_group = [state]
                    processed.add(state)
                    
                    for other_state in partition:
                        if other_state in processed:
                            continue
                        
                        if self.are_states_equivalent(state, other_state, partitions):
                            equivalent_group.append(other_state)
                            processed.add(other_state)
                    
                    sub_partitions.append(equivalent_group)
                
                if len(sub_partitions) > 1:
                    changed = True
                
                new_partitions.extend(sub_partitions)
            
            partitions = new_partitions
        
        return partitions
    
    def create_minimal_dfa(self, final_partitions: List[List[str]]) -> DFA:
        """Create minimal DFA from final partitions"""
        # Create mapping from old states to new states
        for i, partition in enumerate(final_partitions):
            new_state_name = f"q{i}"
            for state in partition:
                self.state_mapping[state] = new_state_name
        
        # New states
        new_states = [f"q{i}" for i in range(len(final_partitions))]
        
        # New transitions
        new_transitions = {}
        for i, partition in enumerate(final_partitions):
            representative = partition[0]  # Take representative from partition
            new_state_name = f"q{i}"
            new_transitions[new_state_name] = {}
            
            for symbol in self.original_dfa.alphabet:
                if (representative in self.original_dfa.transitions and 
                    symbol in self.original_dfa.transitions[representative]):
                    next_state = self.original_dfa.transitions[representative][symbol]
                    new_next_state = self.state_mapping[next_state]
                    new_transitions[new_state_name][symbol] = new_next_state
        
        # New start state
        new_start_state = self.state_mapping[self.original_dfa.start_state]
        
        # New final states
        new_final_states = set()
        for final_state in self.original_dfa.final_states:
            if final_state in self.state_mapping:
                new_final_states.add(self.state_mapping[final_state])
        
        minimal_dfa = DFA(new_states, list(self.original_dfa.alphabet), 
                         new_transitions, new_start_state, list(new_final_states))
        
        return minimal_dfa
    
    def minimize(self) -> DFA:
        """Main minimization process"""
        # Step 1: Find reachable states
        reachable_states = self.find_reachable_states()
        
        # Step 2: Create initial partition
        partitions = self.create_initial_partition(reachable_states)
        
        # Step 3: Refine partitions
        final_partitions = self.refine_partitions(partitions)
        
        # Step 4: Create minimal DFA
        minimal_dfa = self.create_minimal_dfa(final_partitions)
        
        return minimal_dfa

def minimize_dfa(dfa_definition):
    """
    Fungsi untuk minimize DFA
    Input format expected:
    {
        'states': ['q0', 'q1', 'q2', ...],
        'alphabet': ['a', 'b', ...],  
        'transitions': {
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q3', 'b': 'q4'},
            ...
        },
        'start_state': 'q0',
        'accept_states': ['q3', 'q4', ...]  # Note: might be 'final_states' in some formats
    }
    """
    try:
        # Handle different naming conventions for final states
        final_states = dfa_definition.get('accept_states', 
                                        dfa_definition.get('final_states', []))
        
        # Create DFA object
        dfa = DFA(
            states=dfa_definition['states'],
            alphabet=dfa_definition['alphabet'],
            transitions=dfa_definition['transitions'],
            start_state=dfa_definition['start_state'],
            final_states=final_states
        )
        
        # Create minimizer and minimize
        minimizer = DFAMinimizer(dfa)
        minimized_dfa = minimizer.minimize()
        
        # Convert back to dictionary format - THIS IS THE KEY FIX
        return {
            'states': list(minimized_dfa.states),
            'alphabet': list(minimized_dfa.alphabet),
            'transitions': minimized_dfa.transitions,
            'start_state': minimized_dfa.start_state,
            'accept_states': list(minimized_dfa.final_states)
        }
        
    except Exception as e:
        # Return original DFA if minimization fails
        print(f"Error during minimization: {e}")
        raise e  # Re-raise the exception so Flask can handle it

# ===== HELPER FUNCTIONS (jika diperlukan) =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    required_keys = ['states', 'alphabet', 'transitions', 'start_state']
    
    # Check for accept_states or final_states
    has_accept_states = 'accept_states' in dfa or 'final_states' in dfa
    
    basic_validation = all(key in dfa for key in required_keys) and has_accept_states
    
    if not basic_validation:
        return False
    
    # Additional validations
    try:
        states = set(dfa['states'])
        alphabet = set(dfa['alphabet'])
        transitions = dfa['transitions']
        start_state = dfa['start_state']
        final_states = dfa.get('accept_states', dfa.get('final_states', []))
        
        # Check if start state is in states
        if start_state not in states:
            return False
        
        # Check if final states are in states
        for fs in final_states:
            if fs not in states:
                return False
        
        # Check transitions format
        for state, trans in transitions.items():
            if state not in states:
                return False
            if not isinstance(trans, dict):
                return False
            for symbol, next_state in trans.items():
                if symbol not in alphabet or next_state not in states:
                    return False
        
        return True
        
    except (KeyError, TypeError):
        return False

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000

# ===== EXAMPLE USAGE =====
def test_minimization():
    """Test function with example DFA"""
    example_dfa = {
        'states': ['q0', 'q1', 'q2', 'q3', 'q4'],
        'alphabet': ['a', 'b'],
        'transitions': {
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q3', 'b': 'q4'},
            'q2': {'a': 'q4', 'b': 'q3'},
            'q3': {'a': 'q3', 'b': 'q3'},
            'q4': {'a': 'q4', 'b': 'q4'}
        },
        'start_state': 'q0',
        'accept_states': ['q3', 'q4']
    }
    
    result = minimize_dfa(example_dfa)
    print("Original DFA:", example_dfa)
    print("\nMinimization Result:", result)
    
    return result

# Uncomment to test:
# test_minimization()
