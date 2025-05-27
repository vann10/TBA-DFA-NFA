from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ===== HOMEPAGE =====
@app.route('/')
def index():
    return render_template('index.html')

# ===== DFA TESTING =====
@app.route('/dfa-test')
def dfa_test_page():
    return render_template('dfa_test.html')

@app.route('/dfa-test', methods=['POST'])
def dfa_test():
    try:
        data = request.get_json()
        dfa_input = data['dfa']
        test_string = data['string']
        
        # Panggil fungsi DFA Anda yang sudah ada
        result = test_dfa_string(dfa_input, test_string)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'accepted': result['accepted'],
            'trace': result.get('trace', []),
            'message': f"String '{test_string}' {'diterima' if result['accepted'] else 'ditolak'}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ===== NFA & REGEX =====
@app.route('/nfa-regex')
def nfa_regex_page():
    return render_template('nfa_regex.html')

@app.route('/regex-to-nfa', methods=['POST'])
def regex_to_nfa():
    try:
        data = request.get_json()
        regex = data['regex']
        
        # Panggil fungsi convert regex ke NFA Anda
        nfa = convert_regex_to_nfa(regex)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'nfa': nfa,
            'message': f"Regex '{regex}' berhasil dikonversi ke NFA"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/test-nfa', methods=['POST'])
def test_nfa():
    try:
        data = request.get_json()
        nfa_input = data['nfa']
        test_string = data['string']
        
        # Panggil fungsi test NFA Anda
        result = test_nfa_string(nfa_input, test_string)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'accepted': result['accepted'],
            'trace': result.get('trace', []),
            'message': f"String '{test_string}' {'diterima' if result['accepted'] else 'ditolak'}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/test-regex', methods=['POST'])
def test_regex():
    try:
        data = request.get_json()
        regex = data['regex']
        test_string = data['string']
        
        # Panggil fungsi test regex Anda
        result = test_regex_string(regex, test_string)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'accepted': result,
            'message': f"String '{test_string}' {'cocok' if result else 'tidak cocok'} dengan regex '{regex}'"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ===== DFA MINIMIZATION =====
@app.route('/dfa-minimize')
def dfa_minimize_page():
    return render_template('dfa_minimize.html')

@app.route('/dfa-minimize', methods=['POST'])
def dfa_minimize():
    try:
        data = request.get_json()
        dfa_input = data['dfa']
        
        # Panggil fungsi minimize DFA Anda
        result = minimize_dfa(dfa_input)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'original_dfa': dfa_input,
            'minimized_dfa': result['minimized'],
            'reduction_info': {
                'original_states': result['original_states'],
                'minimized_states': result['minimized_states'],
                'states_removed': result['original_states'] - result['minimized_states']
            },
            'message': 'DFA berhasil diminimalisasi'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ===== DFA COMPARISON =====
@app.route('/dfa-compare')  
def dfa_compare_page():
    return render_template('dfa_compare.html')

@app.route('/dfa-compare', methods=['POST'])
def dfa_compare():
    try:
        data = request.get_json()
        dfa1 = data['dfa1']
        dfa2 = data['dfa2']
        
        # Panggil fungsi compare DFA Anda
        result = compare_dfas(dfa1, dfa2)  # Ganti dengan nama fungsi Anda
        
        return jsonify({
            'success': True,
            'equivalent': result['equivalent'],
            'details': result.get('details', {}),
            'message': f"DFA 1 dan DFA 2 {'equivalent' if result['equivalent'] else 'tidak equivalent'}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)