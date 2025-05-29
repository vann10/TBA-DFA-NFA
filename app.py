from flask import Flask, render_template, request, jsonify
from models.function2 import State, regex_to_nfa, visualize_nfa
from models.function3 import minimize_dfa
import re
from models.function4 import compare_dfas
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ===== HOMEPAGE =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create_dfa():
    return render_template('create.html')

@app.route('/test')
def test_dfa():
    return render_template('test.html')

@app.route('/history')
def history():
    return render_template('history.html')

# ===== DFA TESTING =====
@app.route('/dfa-test')
def dfa_test_page():
    return render_template('tes_dfa.html')

def convert_nested_to_flat(dfa):
    """
    Konversi DFA dengan format nested (delta) ke format flat (transitions) yang digunakan oleh fungsi test_dfa_string.
    Jika sudah flat, return apa adanya.
    """
    if "transitions" in dfa:
        return dfa
    if "delta" in dfa:
        flat = {}
        for state, trans in dfa["delta"].items():
            for symbol, target in trans.items():
                flat[f"{state},{symbol}"] = target
        return {
            "states": dfa.get("states", []),
            "alphabet": dfa.get("alphabet", []),
            "transitions": flat,
            "start_state": dfa.get("start", dfa.get("start_state", "")),
            "accept_states": dfa.get("accept", dfa.get("accept_states", []))
        }
    return dfa

@app.route('/dfa-test', methods=['POST'])
def dfa_test():
    try:
        data = request.get_json()
        # Validasi input
        if not data or 'dfa' not in data or 'string' not in data:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        dfa_input = data['dfa']
        test_string = data['string']
        # Parse DFA jika dalam bentuk string
        if isinstance(dfa_input, str):
            try:
                dfa_input = json.loads(dfa_input)
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid DFA JSON format'}), 400
        # Konversi DFA ke format flat jika perlu
        dfa_input = convert_nested_to_flat(dfa_input)
        # Validasi struktur DFA
        if not validate_dfa_input(dfa_input):
            return jsonify({'success': False, 'error': 'Invalid DFA structure'}), 400
        # Test DFA dengan string
        result = test_dfa_string(dfa_input, test_string)
        return jsonify({
            'success': True,
            'accepted': result['accepted'],
            'trace': result.get('trace', []),
            'message': f"String '{test_string}' {'diterima' if result['accepted'] else 'ditolak'}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def test_dfa_string(dfa, input_string):
    """
    Test apakah string diterima oleh DFA
    """
    try:
        current_state = dfa['start_state']
        trace = [current_state]

        for symbol in input_string:
            if symbol not in dfa['alphabet']:
                return {'accepted': False, 'trace': trace, 'error': f'Symbol {symbol} not in alphabet'}

            transition_key = f"{current_state},{symbol}"
            if transition_key not in dfa['transitions']:
                return {'accepted': False, 'trace': trace, 'error': f'No transition for {current_state} on {symbol}'}

            current_state = dfa['transitions'][transition_key]
            trace.append(current_state)

        accepted = current_state in dfa['accept_states']
        return {'accepted': accepted, 'trace': trace}

    except Exception as e:
        return {'accepted': False, 'trace': [], 'error': str(e)}

# ===== NFA & REGEX =====
@app.route('/regex-nfa')  
def regex_nfa_page():
    return render_template('regex_nfa.html')

@app.route("/regex-nfa", methods=["GET", "POST"])
def regex_nfa():
    result = ""
    transition_table = ""
    test_result = ""
    input_string = ""
    nfa_image_path = ""
    nfa_image = False

    if request.method == "POST":
        State._id_counter = 0  # Reset ID state
        regex = request.form.get("regex", "")
        input_string = request.form.get("input_string", "")

        try:
            nfa = regex_to_nfa(regex)
            transition_table = nfa.transition_table_str()
            nfa_match = nfa.process_input(input_string)
            regex_match = bool(re.fullmatch(regex, input_string))

            test_result = f"""
            Regex match: {'Diterima' if regex_match else 'Ditolak'}<br>
            NFA match  : {'Diterima' if nfa_match else 'Ditolak'}
            """

            dot = visualize_nfa(nfa)
            image_path = "static/nfa_result"
            dot.render(image_path, format="png", cleanup=True)
            nfa_image_path = f"{image_path}.png"
            visualize_nfa(nfa)  
            nfa_image = True

        except Exception as e:
            result = f"Terjadi error: {e}"

    return render_template("regex_nfa.html", transition_table=transition_table, test_result=test_result, input_string=input_string, nfa_image=nfa_image_path)
    return render_template("regex_nfa.html", transition_table=transition_table, test_result=test_result, input_string=input_string, nfa_image=nfa_image)

@app.route("/regex", methods=["POST"])
def handle_regex():
    data = request.get_json()
    regex = data.get("regex")
    string = data.get("string")

    try:
        nfa = regex_to_nfa(regex)
        result = nfa.process_input(string)
        table = nfa.transition_table_str()
        image_path = visualize_nfa(nfa)  # Simpan ke static/nfa_diagram.png

        return jsonify({
            "result": result,
            "table": table,
            "image_url": "/static/nfa_diagram.png"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===== DFA MINIMIZATION =====
@app.route('/dfa-minimize')
def dfa_minimize_page():
    return render_template('dfa_minimize.html')

@app.route('/dfa-minimize', methods=['POST'])
def dfa_minimize():
    try:
        data = request.get_json()

        # Validasi input data
        if not data or 'dfa' not in data:
            return jsonify({'success': False, 'error': 'Missing DFA data'}), 400

        dfa_input = data['dfa']

        # Parse DFA jika dalam bentuk string JSON
        if isinstance(dfa_input, str):
            try:
                dfa_input = json.loads(dfa_input)
            except json.JSONDecodeError as e:
                return jsonify({'success': False, 'error': f'Invalid JSON format: {str(e)}'}), 400

        # Validasi struktur DFA
        if not validate_dfa_input(dfa_input):
            return jsonify({'success': False, 'error': 'Invalid DFA structure. Required: states, alphabet, transitions, start_state, accept_states'}), 400

        # Panggil fungsi minimize DFA
        result = minimize_dfa(dfa_input)

        return jsonify({
            'success': True,
            'original_dfa': dfa_input,
            'minimized_dfa': result['minimized'],
            'reduction_info': {
                'original_states': result['original_states'],
                'minimized_states': result['minimized_states'],
                'states_removed': result['original_states'] - result['minimized_states'],
                'reduction_percentage': result.get('reduction_percentage', 0)
            },
            'message': f'DFA berhasil diminimalisasi dari {result["original_states"]} state menjadi {result["minimized_states"]} state'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Minimization error: {str(e)}'}), 500

# ===== DFA COMPARISON =====
@app.route('/dfa-compare')  
def dfa_compare_page():
    return render_template('dfa_compare.html')

@app.route('/dfa-compare', methods=['POST'])
def dfa_compare():
    try:
        data = request.get_json()

        # Validasi input
        if not data or 'dfa1' not in data or 'dfa2' not in data:
            return jsonify({'success': False, 'error': 'Missing DFA data'}), 400

        # Parsing DFA
        try:
            if isinstance(data['dfa1'], str):
                dfa1 = json.loads(data['dfa1'])
            else:
                dfa1 = data['dfa1']

            if isinstance(data['dfa2'], str):
                dfa2 = json.loads(data['dfa2'])
            else:
                dfa2 = data['dfa2']
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Invalid JSON: {str(e)}'}), 400

        result = compare_dfas(dfa1, dfa2)

        return jsonify({
            'success': True,
            'equivalent': result['equivalent'],
            'details': result.get('details', {}),
            'message': f"DFA comparison completed: {'Equivalent' if result['equivalent'] else 'Not equivalent'}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Comparison error: {str(e)}'}), 500

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
