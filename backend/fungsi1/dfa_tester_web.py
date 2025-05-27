from flask import Flask, render_template, request, jsonify, session
import json
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

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
            return False, "DFA tidak memiliki state awal", []
        
        current_state = self.start_state
        path = [current_state]
        trace = []
        
        # Record initial state
        trace.append({
            'step': 0,
            'symbol': '',
            'state': current_state,
            'description': f"Mulai dari state awal {current_state}"
        })
        
        for i, symbol in enumerate(input_string):
            if symbol not in self.alphabet:
                return False, f"Simbol '{symbol}' tidak ada dalam alfabet DFA", trace
            
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False, f"Tidak ada transisi dari state '{current_state}' dengan simbol '{symbol}'", trace
            
            prev_state = current_state
            current_state = self.transitions[current_state][symbol]
            path.append(current_state)
            
            # Record each transition
            trace.append({
                'step': i + 1,
                'symbol': symbol,
                'state': current_state,
                'description': f"Membaca '{symbol}', pindah dari {prev_state} ke {current_state}"
            })
        
        is_accepted = current_state in self.accept_states
        result_message = "diterima" if is_accepted else "ditolak"
        
        # Add final result to trace
        trace.append({
            'step': len(input_string) + 1,
            'symbol': '',
            'state': current_state,
            'description': f"Selesai di state {current_state} ({result_message})"
        })
        
        return is_accepted, f"Input string {result_message}. Path: {' -> '.join(path)}", trace
    
    def to_dict(self):
        return {
            'states': list(self.states),
            'alphabet': list(self.alphabet),
            'transitions': self.transitions,
            'start_state': self.start_state,
            'accept_states': list(self.accept_states)
        }
    
    @classmethod
    def from_dict(cls, data):
        dfa = cls()
        for state in data['states']:
            dfa.add_state(state)
        
        for symbol in data['alphabet']:
            dfa.alphabet.add(symbol)
        
        dfa.set_start_state(data['start_state'])
        
        for state in data['accept_states']:
            dfa.add_accept_state(state)
        
        for from_state, transitions in data['transitions'].items():
            for symbol, to_state in transitions.items():
                dfa.add_transition(from_state, symbol, to_state)
        
        return dfa

# Dictionary to store DFAs
dfas = {}

# Dictionary to store test history
test_history = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/test')
def test():
    return render_template('test.html', dfas=dfas)

@app.route('/visualize/<dfa_id>')
def visualize(dfa_id):
    if dfa_id not in dfas:
        return "DFA not found", 404
    return render_template('visualize.html', dfa_id=dfa_id)

@app.route('/history')
def history():
    return render_template('history.html', history=test_history)

@app.route('/api/create_dfa', methods=['POST'])
def create_dfa():
    data = request.json
    try:
        # Create DFA from input data
        dfa = DFA()
        
        # Add states
        for state in data['states'].split():
            dfa.add_state(state)
        
        # Add alphabet
        for symbol in data['alphabet'].split():
            if len(symbol) != 1:
                return jsonify({'success': False, 'error': f"Symbol '{symbol}' must be a single character"})
            dfa.alphabet.add(symbol)
        
        # Set start state
        start_state = data['start_state']
        if start_state not in dfa.states:
            return jsonify({'success': False, 'error': f"Start state '{start_state}' not in states list"})
        dfa.set_start_state(start_state)
        
        # Add accept states
        for state in data['accept_states'].split():
            if state not in dfa.states:
                return jsonify({'success': False, 'error': f"Accept state '{state}' not in states list"})
            dfa.add_accept_state(state)
        
        # Add transitions
        for transition in data['transitions']:
            from_state = transition['from']
            symbol = transition['symbol']
            to_state = transition['to']
            
            if from_state not in dfa.states:
                return jsonify({'success': False, 'error': f"State '{from_state}' not in states list"})
            
            if to_state not in dfa.states:
                return jsonify({'success': False, 'error': f"State '{to_state}' not in states list"})
            
            if symbol not in dfa.alphabet:
                return jsonify({'success': False, 'error': f"Symbol '{symbol}' not in alphabet"})
            
            dfa.add_transition(from_state, symbol, to_state)
        
        # Generate ID and save DFA
        dfa_id = str(uuid.uuid4())
        dfas[dfa_id] = {
            'dfa': dfa,
            'name': data['name'],
            'description': data['description'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify({
            'success': True, 
            'dfa_id': dfa_id,
            'dfa_info': {
                'states': list(dfa.states),
                'alphabet': list(dfa.alphabet),
                'start_state': dfa.start_state,
                'accept_states': list(dfa.accept_states),
                'transitions': dfa.transitions
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test_string', methods=['POST'])
def test_string():
    data = request.json
    dfa_id = data['dfa_id']
    input_string = data['input_string']
    
    if dfa_id not in dfas:
        return jsonify({'success': False, 'error': 'DFA not found'})
    
    dfa = dfas[dfa_id]['dfa']
    is_accepted, message, trace = dfa.process_input(input_string)
    
    # Save test result to history
    test_id = str(uuid.uuid4())
    test_history[test_id] = {
        'dfa_id': dfa_id,
        'dfa_name': dfas[dfa_id]['name'],
        'input_string': input_string,
        'is_accepted': is_accepted,
        'message': message,
        'trace': trace,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return jsonify({
        'success': True,
        'is_accepted': is_accepted,
        'message': message,
        'trace': trace,
        'test_id': test_id
    })

@app.route('/api/get_dfa/<dfa_id>')
def get_dfa(dfa_id):
    if dfa_id not in dfas:
        return jsonify({'success': False, 'error': 'DFA not found'})
    
    dfa_info = dfas[dfa_id]
    dfa = dfa_info['dfa']
    
    return jsonify({
        'success': True,
        'name': dfa_info['name'],
        'description': dfa_info['description'],
        'created_at': dfa_info['created_at'],
        'dfa_data': dfa.to_dict()
    })

@app.route('/api/get_all_dfas')
def get_all_dfas():
    result = {}
    for dfa_id, dfa_info in dfas.items():
        result[dfa_id] = {
            'name': dfa_info['name'],
            'description': dfa_info['description'],
            'created_at': dfa_info['created_at']
        }
    
    return jsonify({'success': True, 'dfas': result})

@app.route('/api/get_test_history')
def get_test_history():
    return jsonify({'success': True, 'history': test_history})

@app.route('/api/delete_dfa/<dfa_id>', methods=['DELETE'])
def delete_dfa(dfa_id):
    if dfa_id not in dfas:
        return jsonify({'success': False, 'error': 'DFA not found'})
    
    del dfas[dfa_id]
    
    # Also delete related test history
    to_delete = []
    for test_id, test_data in test_history.items():
        if test_data['dfa_id'] == dfa_id:
            to_delete.append(test_id)
    
    for test_id in to_delete:
        del test_history[test_id]
    
    return jsonify({'success': True})

# Sample DFA for testing
def create_sample_dfa():
    dfa = DFA()
    dfa.add_state('q0')
    dfa.add_state('q1')
    dfa.add_state('q2')
    dfa.set_start_state('q0')
    dfa.add_accept_state('q2')
    dfa.alphabet.add('0')
    dfa.alphabet.add('1')
    dfa.add_transition('q0', '0', 'q1')
    dfa.add_transition('q0', '1', 'q0')
    dfa.add_transition('q1', '0', 'q1')
    dfa.add_transition('q1', '1', 'q2')
    dfa.add_transition('q2', '0', 'q2')
    dfa.add_transition('q2', '1', 'q2')
    
    dfa_id = "sample"
    dfas[dfa_id] = {
        'dfa': dfa,
        'name': 'Sample DFA (Accepts strings containing "01")',
        'description': 'This is a sample DFA that accepts strings containing the substring "01".',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == '__main__':
    create_sample_dfa()
    app.run(debug=True) 