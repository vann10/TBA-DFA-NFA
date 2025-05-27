# ===== PINDAHKAN SEMUA FUNGSI MINIMIZATION ANDA KE SINI =====
def minimize_dfa(dfa_definition):
    """
    Fungsi untuk minimize DFA
    """
    # GANTI INI DENGAN KODE MINIMIZATION ANDA
    return {
        'minimized': dfa_definition,  # DFA yang sudah diminimize
        'original_states': 5,
        'minimized_states': 3
    }

# ===== HELPER FUNCTIONS (jika diperlukan) =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accept_states']
    return all(key in dfa for key in required_keys)

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000