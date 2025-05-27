class DFA:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()
    
    def add_state(self, state):
        self.states.add(state)
    
    def set_start_state(self, state):
        self.start_state = state
        self.add_state(state)
    
    def add_accept_state(self, state):
        self.accept_states.add(state)
        self.add_state(state)
    
    def add_transition(self, from_state, symbol, to_state):
        self.add_state(from_state)
        self.add_state(to_state)
        self.alphabet.add(symbol)
        
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        
        self.transitions[from_state][symbol] = to_state
    
    def process_input(self, input_string):
        if not self.start_state:
            return False, "DFA tidak memiliki state awal"
        
        current_state = self.start_state
        path = [current_state]
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False, f"Simbol '{symbol}' tidak ada dalam alfabet DFA"
            
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False, f"Tidak ada transisi dari state '{current_state}' dengan simbol '{symbol}'"
            
            current_state = self.transitions[current_state][symbol]
            path.append(current_state)
        
        is_accepted = current_state in self.accept_states
        result_message = "diterima" if is_accepted else "ditolak"
        
        return is_accepted, f"Input string {result_message}. Path: {' -> '.join(path)}"

def create_dfa():
    print("==== PEMBUATAN DFA ====")
    dfa = DFA()
    
    # Input states
    states_input = input("Masukkan semua state (pisahkan dengan spasi): ").split()
    for state in states_input:
        dfa.add_state(state)
    
    # Input alphabet
    alphabet_input = input("Masukkan alfabet (pisahkan dengan spasi): ").split()
    for symbol in alphabet_input:
        dfa.alphabet.add(symbol)
    
    # Input start state
    start_state = input("Masukkan state awal: ")
    dfa.set_start_state(start_state)
    
    # Input accept states
    accept_states = input("Masukkan state penerima (pisahkan dengan spasi): ").split()
    for state in accept_states:
        dfa.add_accept_state(state)
    
    # Input transitions
    print("\nMasukkan transisi dalam format: <state_awal> <simbol> <state_tujuan>")
    print("Masukkan 'selesai' untuk mengakhiri input transisi")
    
    while True:
        transition = input("Transisi: ")
        if transition.lower() == 'selesai':
            break
        
        parts = transition.split()
        if len(parts) != 3:
            print("Format tidak valid! Gunakan: <state_awal> <simbol> <state_tujuan>")
            continue
        
        from_state, symbol, to_state = parts
        
        if from_state not in dfa.states:
            print(f"Warning: State '{from_state}' belum didefinisikan sebelumnya.")
        if to_state not in dfa.states:
            print(f"Warning: State '{to_state}' belum didefinisikan sebelumnya.")
        if symbol not in dfa.alphabet:
            print(f"Warning: Simbol '{symbol}' belum ada dalam alfabet.")
        
        dfa.add_transition(from_state, symbol, to_state)
    
    return dfa

def display_dfa_info(dfa):
    print("\n==== INFORMASI DFA ====")
    print(f"States: {', '.join(sorted(dfa.states))}")
    print(f"Alfabet: {', '.join(sorted(dfa.alphabet))}")
    print(f"State awal: {dfa.start_state}")
    print(f"State penerima: {', '.join(sorted(dfa.accept_states))}")
    
    print("\nTransisi:")
    for from_state in sorted(dfa.transitions.keys()):
        for symbol in sorted(dfa.transitions[from_state].keys()):
            to_state = dfa.transitions[from_state][symbol]
            print(f"  δ({from_state}, {symbol}) = {to_state}")

def main():
    print("=== PROGRAM TESTER DFA ===")
    print("Buat DFA baru:")
    
    dfa = create_dfa()
    display_dfa_info(dfa)
    
    print("\n==== MODE TESTING ====")
    print("Masukkan string untuk diuji (ketik 'keluar' untuk mengakhiri program)")
    
    while True:
        input_string = input("\nInput string: ")
        if input_string.lower() == 'keluar':
            break
        
        is_accepted, message = dfa.process_input(input_string)
        print(message)

if __name__ == "__main__":
    main()
