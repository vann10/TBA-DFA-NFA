# ===== PINDAHKAN SEMUA FUNGSI COMPARISON ANDA KE SINI =====
def compare_dfas(dfa1, dfa2):
    """
    Fungsi untuk compare 2 DFA
    """
    # GANTI INI DENGAN KODE COMPARISON ANDA
    return {
        'equivalent': True,  # True jika equivalent
        'details': {
            'reason': 'Both DFAs accept the same language'
        }
    }

# ===== HELPER FUNCTIONS (jika diperlukan) =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accept_states']
    return all(key in dfa for key in required_keys)

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000