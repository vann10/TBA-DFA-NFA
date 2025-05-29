from graphviz import Digraph

class State:
    _id_counter = 0

    def __init__(self):
        self.transitions = {}
        self.epsilon = set()
        self.id = f"q{State._id_counter}"
        State._id_counter += 1

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

    def add_transition(self, from_state, symbol, to_state):
        if symbol == "":
            from_state.epsilon.add(to_state)
        else:
            from_state.transitions.setdefault(symbol, set()).add(to_state)

    def epsilon_closure(self, states):
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            for next_state in state.epsilon:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def process_input(self, string):
        current_states = self.epsilon_closure({self.start})
        for char in string:
            next_states = set()
            for state in current_states:
                if char in state.transitions:
                    for next_state in state.transitions[char]:
                        next_states |= self.epsilon_closure({next_state})
            current_states = next_states
        return self.accept in current_states

    def get_all_states(self):
        visited = set()
        stack = [self.start]
        while stack:
            state = stack.pop()
            if state not in visited:
                visited.add(state)
                for symbol, to_states in state.transitions.items():
                    stack.extend(to_states)
                stack.extend(state.epsilon)
        return visited

    def transition_table_str(self):
        output = []
        states = sorted(self.get_all_states(), key=lambda s: int(s.id[1:]))
        for state in states:
            for symbol, to_states in state.transitions.items():
                for to_state in to_states:
                    output.append(f"{state.id} -- {symbol} --> {to_state.id}")
            for to_state in state.epsilon:
                output.append(f"{state.id} -- ε --> {to_state.id}")
        output.append(f"\nState awal   : {self.start.id}")
        output.append(f"State akhir  : {self.accept.id}")
        return "\n".join(output)

def regex_to_nfa(regex):
    def parse_expr(tokens):
        terms = [parse_term(tokens)]
        while tokens and tokens[0] == '|':
            tokens.pop(0)
            terms.append(parse_term(tokens))
        if len(terms) == 1:
            return terms[0]
        return build_alternate(terms)

    def parse_term(tokens):
        factors = []
        while tokens and tokens[0] not in ')|':
            factors.append(parse_factor(tokens))
        if not factors:
            return build_epsilon()
        return build_concatenate(factors)

    def parse_factor(tokens):
        base = parse_base(tokens)
        while tokens and tokens[0] == '*':
            tokens.pop(0)
            base = build_kleene_star(base)
        return base

    def parse_base(tokens):
        token = tokens.pop(0)
        if token == '(':
            inner = parse_expr(tokens)
            if not tokens or tokens.pop(0) != ')':
                raise ValueError("Kurung tidak seimbang")
            return inner
        return build_symbol(token)

    def build_symbol(symbol):
        s1 = State()
        s2 = State()
        nfa = NFA(s1, s2)
        nfa.add_transition(s1, symbol, s2)
        return nfa

    def build_concatenate(nfas):
        nfa = nfas[0]
        for next_nfa in nfas[1:]:
            nfa.add_transition(nfa.accept, "", next_nfa.start)
            nfa.accept = next_nfa.accept
        return nfa

    def build_alternate(nfas):
        start = State()
        accept = State()
        nfa = NFA(start, accept)
        for sub_nfa in nfas:
            nfa.add_transition(start, "", sub_nfa.start)
            nfa.add_transition(sub_nfa.accept, "", accept)
        return nfa

    def build_kleene_star(sub_nfa):
        start = State()
        accept = State()
        nfa = NFA(start, accept)
        nfa.add_transition(start, "", sub_nfa.start)
        nfa.add_transition(start, "", accept)
        nfa.add_transition(sub_nfa.accept, "", sub_nfa.start)
        nfa.add_transition(sub_nfa.accept, "", accept)
        return nfa

    def build_epsilon():
        s1 = State()
        s2 = State()
        nfa = NFA(s1, s2)
        nfa.add_transition(s1, "", s2)
        return nfa

    tokens = list(regex)
    return parse_expr(tokens)

def visualize_nfa(nfa):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')

    states = nfa.get_all_states()

    for state in states:
        if state == nfa.accept:
            dot.node(state.id, shape='doublecircle')
        else:
            dot.node(state.id, shape='circle')

    dot.node("", shape="none")
    dot.edge("", nfa.start.id)

    for state in states:
        for symbol, to_states in state.transitions.items():
            for to_state in to_states:
                dot.edge(state.id, to_state.id, label=symbol)
        for to_state in state.epsilon:
            dot.edge(state.id, to_state.id, label="ε")

    return dot
# function2.py
def generate_nfa_image(dot):
    filepath = 'static/nfa_result'
    dot.render(filepath, cleanup=True) 
    return filepath + '.png'