# ===== DFA MINIMIZATION FUNCTIONS =====

def minimize_dfa(dfa_definition):
    """
    Fungsi untuk minimize DFA menggunakan algoritma table-filling
    """
    try:
        # Validasi input DFA
        if not validate_dfa_input(dfa_definition):
            raise ValueError("Invalid DFA structure")
        
        states = dfa_definition['states']
        alphabet = dfa_definition['alphabet']
        transitions = dfa_definition['transitions']
        start_state = dfa_definition['start_state']
        accept_states = set(dfa_definition['accept_states'])
        
        # Jika hanya ada 1 state, tidak perlu diminimize
        if len(states) <= 1:
            return create_minimization_result(dfa_definition, dfa_definition, len(states), len(states))
        
        # Step 1: Hapus unreachable states
        reachable_states = find_reachable_states(states, transitions, start_state, alphabet)
        
        # Step 2: Buat tabel untuk menandai pasangan state yang distinguishable
        distinguishable = create_distinguishable_table(reachable_states, accept_states)
        
        # Step 3: Table-filling algorithm untuk mencari equivalent states
        mark_distinguishable_states(distinguishable, reachable_states, transitions, alphabet)
        
        # Step 4: Grup equivalent states
        equivalent_groups = find_equivalent_groups(distinguishable, reachable_states)
        
        # Step 5: Buat DFA yang sudah diminimize
        minimized_dfa = build_minimized_dfa(
            equivalent_groups, 
            dfa_definition, 
            reachable_states
        )
        
        return create_minimization_result(
            dfa_definition, 
            minimized_dfa, 
            len(states), 
            len(minimized_dfa['states'])
        )
        
    except Exception as e:
        raise Exception(f"Error in DFA minimization: {str(e)}")

def find_reachable_states(states, transitions, start_state, alphabet):
    """Mencari semua state yang reachable dari start state"""
    reachable = set()
    stack = [start_state]
    
    # Pastikan start_state valid
    if start_state not in states:
        raise ValueError(f"Start state '{start_state}' not found in states list")
    
    while stack:
        current = stack.pop()
        if current not in reachable:
            reachable.add(current)
            
            # Cek semua transisi dari current state
            for symbol in alphabet:
                transition_key = f"{current},{symbol}"
                if transition_key in transitions:
                    next_state = transitions[transition_key]
                    # Validasi bahwa next_state ada dalam daftar states
                    if next_state in states and next_state not in reachable:
                        stack.append(next_state)
    
    return list(reachable)

def create_distinguishable_table(states, accept_states):
    """Membuat tabel untuk menandai pasangan state yang distinguishable"""
    distinguishable = {}
    
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            state1, state2 = states[i], states[j]
            # Tandai sebagai distinguishable jika satu accepting dan satu non-accepting
            distinguishable[(state1, state2)] = (
                (state1 in accept_states) != (state2 in accept_states)
            )
    
    return distinguishable

def mark_distinguishable_states(distinguishable, states, transitions, alphabet):
    """Table-filling algorithm untuk menandai semua pasangan distinguishable"""
    changed = True
    
    while changed:
        changed = False
        
        for (state1, state2), is_distinguishable in distinguishable.items():
            if not is_distinguishable:  # Jika belum ditandai sebagai distinguishable
                
                for symbol in alphabet:
                    # Cari next states untuk kedua state
                    next1 = transitions.get(f"{state1},{symbol}")
                    next2 = transitions.get(f"{state2},{symbol}")
                    
                    if next1 is None or next2 is None:
                        # Jika salah satu tidak ada transisi, mereka distinguishable
                        distinguishable[(state1, state2)] = True
                        changed = True
                        break
                    elif next1 != next2:
                        # Cek apakah next states sudah distinguishable
                        pair = (min(next1, next2), max(next1, next2))
                        if pair in distinguishable and distinguishable[pair]:
                            distinguishable[(state1, state2)] = True
                            changed = True
                            break

def find_equivalent_groups(distinguishable, states):
    """Mencari grup-grup state yang equivalent"""
    groups = []
    processed = set()
    
    for state in states:
        if state not in processed:
            group = [state]
            processed.add(state)
            
            for other_state in states:
                if other_state not in processed:
                    pair = (min(state, other_state), max(state, other_state))
                    if pair not in distinguishable or not distinguishable[pair]:
                        group.append(other_state)
                        processed.add(other_state)
            
            groups.append(group)
    
    return groups

def build_minimized_dfa(equivalent_groups, original_dfa, reachable_states):
    """Membangun DFA yang sudah diminimize dari equivalent groups"""
    # Buat mapping dari state asli ke representative state
    state_mapping = {}
    new_states = []
    
    for i, group in enumerate(equivalent_groups):
        representative = f"q{i}"
        new_states.append(representative)
        for state in group:
            state_mapping[state] = representative
    
    # Buat transisi baru
    new_transitions = {}
    for symbol in original_dfa['alphabet']:
        for group in equivalent_groups:
            representative = state_mapping[group[0]]
            
            # Ambil transisi dari representative state asli
            old_state = group[0]
            transition_key = f"{old_state},{symbol}"
            if transition_key in original_dfa['transitions']:
                old_next_state = original_dfa['transitions'][transition_key]
                new_next_state = state_mapping.get(old_next_state)
                if new_next_state:
                    new_transitions[f"{representative},{symbol}"] = new_next_state
    
    # Tentukan start state dan accept states baru
    new_start_state = state_mapping.get(original_dfa['start_state'])
    new_accept_states = []
    
    for accept_state in original_dfa['accept_states']:
        if accept_state in state_mapping:
            new_state = state_mapping[accept_state]
            if new_state not in new_accept_states:
                new_accept_states.append(new_state)
    
    return {
        'states': new_states,
        'alphabet': original_dfa['alphabet'],
        'transitions': new_transitions,
        'start_state': new_start_state,
        'accept_states': new_accept_states
    }

def create_minimization_result(original_dfa, minimized_dfa, original_count, minimized_count):
    """Membuat result object untuk minimization"""
    return {
        'minimized': minimized_dfa,
        'original_states': original_count,
        'minimized_states': minimized_count,
        'reduction_percentage': round((1 - minimized_count/original_count) * 100, 2) if original_count > 0 else 0
    }

# ===== HELPER FUNCTIONS =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    if not isinstance(dfa, dict):
        return False
    
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accept_states']
    
    # Cek apakah semua key yang diperlukan ada
    if not all(key in dfa for key in required_keys):
        print(f"Missing required keys. Found: {list(dfa.keys())}")
        return False
    
    # Validasi lebih detail
    try:
        # States harus berupa list dan tidak kosong
        if not isinstance(dfa['states'], list) or len(dfa['states']) == 0:
            print(f"States validation failed: {dfa['states']}")
            return False
        
        # Alphabet harus berupa list dan tidak kosong
        if not isinstance(dfa['alphabet'], list) or len(dfa['alphabet']) == 0:
            print(f"Alphabet validation failed: {dfa['alphabet']}")
            return False
        
        # Transitions harus berupa dict
        if not isinstance(dfa['transitions'], dict):
            print(f"Transitions validation failed: {type(dfa['transitions'])}")
            return False
        
        # Start state harus ada dalam states
        if dfa['start_state'] not in dfa['states']:
            print(f"Start state '{dfa['start_state']}' not in states: {dfa['states']}")
            return False
        
        # Accept states harus berupa list dan semua element ada dalam states
        if not isinstance(dfa['accept_states'], list):
            print(f"Accept states validation failed: {type(dfa['accept_states'])}")
            return False
        
        for accept_state in dfa['accept_states']:
            if accept_state not in dfa['states']:
                print(f"Accept state '{accept_state}' not in states: {dfa['states']}")
                return False
        
        # Validasi transitions - pastikan semua state dan symbol yang direferensikan valid
        for transition_key, next_state in dfa['transitions'].items():
            if ',' not in transition_key:
                print(f"Invalid transition key format: '{transition_key}' (expected 'state,symbol')")
                return False
                
            state, symbol = transition_key.split(',', 1)
            
            if state not in dfa['states']:
                print(f"Transition references invalid state: '{state}'")
                return False
                
            if symbol not in dfa['alphabet']:
                print(f"Transition references invalid symbol: '{symbol}'")
                return False
                
            if next_state not in dfa['states']:
                print(f"Transition leads to invalid state: '{next_state}'")
                return False
        
        return True
        
    except Exception as e:
        print(f"Validation exception: {e}")
    
    # Validasi lebih detail
    try:
        # States harus berupa list dan tidak kosong
        if not isinstance(dfa['states'], list) or len(dfa['states']) == 0:
            return False
        
        # Alphabet harus berupa list dan tidak kosong
        if not isinstance(dfa['alphabet'], list) or len(dfa['alphabet']) == 0:
            return False
        
        # Transitions harus berupa dict
        if not isinstance(dfa['transitions'], dict):
            return False
        
        # Start state harus ada dalam states
        if dfa['start_state'] not in dfa['states']:
            return False
        
        # Accept states harus berupa list dan semua element ada dalam states
        if not isinstance(dfa['accept_states'], list):
            return False
        
        for accept_state in dfa['accept_states']:
            if accept_state not in dfa['states']:
                return False
        
        return True
        
    except Exception:
        return False

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000

def print_dfa_info(dfa, title="DFA"):
    """Helper function untuk debugging - print info DFA"""
    print(f"\n=== {title} ===")
    print(f"States: {dfa.get('states', [])}")
    print(f"Alphabet: {dfa.get('alphabet', [])}")
    print(f"Start State: {dfa.get('start_state', 'None')}")
    print(f"Accept States: {dfa.get('accept_states', [])}")
    print("Transitions:")
    for key, value in dfa.get('transitions', {}).items():
        print(f"  {key} -> {value}")