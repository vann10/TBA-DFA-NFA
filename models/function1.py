# automata.py
# File ini berisi semua fungsi DFA, NFA, REGEX, dan minimization Anda

# ===== PINDAHKAN SEMUA FUNGSI DFA ANDA KE SINI =====
def test_dfa_string(dfa_definition, test_string):
    """
    Fungsi untuk test string dengan DFA
    
    Args:
        dfa_definition: Dictionary berisi definisi DFA
        test_string: String yang akan ditest
    
    Returns:
        Dictionary dengan hasil testing
    """
    # GANTI INI DENGAN KODE DFA ANDA
    # Contoh return:
    return {
        'accepted': True,  # True jika string diterima
        'trace': ['q0', 'q1', 'q2']  # Jejak state yang dilalui
    }

# ===== HELPER FUNCTIONS (jika diperlukan) =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accept_states']
    return all(key in dfa for key in required_keys)

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000