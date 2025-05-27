# ===== PINDAHKAN SEMUA FUNGSI NFA ANDA KE SINI =====
def test_nfa_string(nfa_definition, test_string):
    """
    Fungsi untuk test string dengan NFA
    """
    # GANTI INI DENGAN KODE NFA ANDA
    return {
        'accepted': False,
        'trace': []
    }

# ===== PINDAHKAN SEMUA FUNGSI REGEX ANDA KE SINI =====
def convert_regex_to_nfa(regex):
    """
    Fungsi untuk convert regex ke NFA
    """
    # GANTI INI DENGAN KODE REGEX -> NFA ANDA
    return {
        'states': ['q0', 'q1'],
        'alphabet': ['a', 'b'],
        'transitions': {},
        'start_state': 'q0',
        'accept_states': ['q1']
    }

def test_regex_string(regex, test_string):
    """
    Fungsi untuk test string dengan regex
    """
    # GANTI INI DENGAN KODE REGEX TESTING ANDA
    import re
    try:
        pattern = re.compile(regex)
        return bool(pattern.fullmatch(test_string))
    except:
        return False

# ===== HELPER FUNCTIONS (jika diperlukan) =====
def validate_dfa_input(dfa):
    """Validasi input DFA"""
    required_keys = ['states', 'alphabet', 'transitions', 'start_state', 'accept_states']
    return all(key in dfa for key in required_keys)

def validate_string_input(string):
    """Validasi input string"""
    return isinstance(string, str) and len(string) <= 1000