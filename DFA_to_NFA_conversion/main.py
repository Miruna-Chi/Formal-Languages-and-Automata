import sys  # provides access to command line arguments


class NFA:
    def __init__(self):
        self.q0 = 0
        self.alphabet = set()
        self.states = set()
        self.final_states = set()
        self.delta = {}
        self.state_matrix = []  # explained in README
        self.sink_state = False

    def __str__(self):
        print('\tNFA:')
        print('Alphabet: ', self.alphabet)
        print('States: ', self.states)
        print('Final states: ', self.final_states)
        print('Delta: ', self.delta)
        print('State matrix: ', self.state_matrix, '\n')
        return '\n'

    # turn the input text into an NFA
    def encode(self, nfa):
        str_lines = nfa.split('\n')
        if str_lines[0].isdigit():
            self.states = set(range(int(str_lines[0])))
        self.final_states = set(str_lines[1].split(' '))
        self.final_states = set([int(i) for i in self.final_states])

        if str_lines[len(str_lines) - 1] == '':
            str_lines.remove(str_lines[len(str_lines) - 1])
        for i in range(2, len(str_lines)):
            delta = str_lines[i]
            delta = delta.split(' ')
            s0 = int(delta[0])
            s1 = list(int(x) for x in (delta[2:]))
            c = delta[1]
            self.alphabet.add(c)
            self.delta[s0, c] = s1

        return True

    # adds s0 to state matrix
    def add_first_state(self):

        self.state_matrix.append([0])
        state = len(self.state_matrix) - 1
        self.states.add(state)

    # starts from a partial state of the DFA (ex: 2 from state 012), finds all next states for a symbol
    # including epsilon paths
    def find_next_states(self, partial_state, symbol):
        # make a queue for all the next possible partial states (actual states in the NFA)
        queue = [(partial_state, symbol, True)]
        # keep a set for visited states so we don't go in circles
        visited = set()

        # add all valid next states, including paths with epsilon, here: 
        valid_paths = set()
        while queue:

            current_tuple = queue.pop(0)
            visited.add(current_tuple)
            
            # Ex: (2, 'b', True/False)
            # partial state: 2(NFA) from 0123(DFA)
            # look_for_symbol: Have I found the symbol on the path once?
            #                  - Yes: only look for epsilon next
            #                  - No: look for both type of paths (start with the symbol/epsilon)  
            (partial_state, symbol, look_for_symbol) = current_tuple

            next_states_epsilon = []
            next_states_symbol = []

            # is there a path on epsilon from this partial DFA state (NFA state)?
            if (partial_state, 'eps') in self.delta:
                # add it to next possible states
                next_states_epsilon = self.delta[(partial_state, 'eps')]

            # is there a path on the symbol from this partial DFA state (NFA state)?
            # (I'm still looking for the symbol)
            if look_for_symbol:
                if (partial_state, symbol) in self.delta:
                    next_states_symbol = self.delta[(partial_state, symbol)]

                # add tuples to queue

                # looking for symbol + eps => still looking for symbol in the next_tuple
                for next_state in next_states_epsilon:
                    next_tuple = (next_state, symbol, True)
                    if next_tuple in visited:
                        continue
                    queue.append(next_tuple)

                # looking for symbol + symbol => not looking for symbol in the next_tuple =>
                # => this is a valid next partial state, add it
                for next_state in next_states_symbol:
                    next_tuple = (next_state, symbol, False)
                    if next_tuple in visited:
                        continue
                    queue.append(next_tuple)
                    valid_paths.add(next_state)

            else:

                # add tuples to queue

                # not looking for symbol + epsilon => valid next partial state, add it
                for next_state in next_states_epsilon:
                    next_tuple = (next_state, symbol, False)
                    if next_tuple in visited:
                        continue
                    queue.append(next_tuple)
                    valid_paths.add(next_state)

        return list(valid_paths)

    def complete_states(self, dfa):
        dfa_states = list(dfa.states)
        # at this point, we only have s0, so we start there and build the other states and add them
        # to the state matrix and the list of states

        '''
        the DFA state matrix works like this:
        - it's a list of ordered lists (so we don't repeat them) of different length
        - each list represents a state in the DFA that's composed of more NFA states:
            ex: [[0], [0, 1, 2], [0, 2], [1, 2]...] -> [0, 1, 2, 3...]
        - the index of the compound state in the matrix is actually the name of the state in the DFA
        '''
        for state in dfa_states:
            for symbol in dfa.alphabet:
                next_states = []
                # partial_state = NFA state (ex: 2), part of a DFA state (ex: 012)
                for partial_state in dfa.state_matrix[state]:
                    next_states += self.find_next_states(partial_state, symbol)

                next_states = list(set(next_states))
                next_states.sort()

                # if there are next states: add the corresponding transitions to the DFA's delta
                if next_states:
                    # firstly, add DFA state in matrix if it's not there (turning it into a properly named state)
                    if next_states not in dfa.state_matrix:
                        dfa.state_matrix.append(next_states)
                        dfa.states.add(len(dfa.state_matrix) - 1)
                        dfa_states.append(len(dfa.state_matrix) - 1)

                    dfa.delta[(state, symbol)] = [dfa.state_matrix.index(next_state) for next_state in
                                                  dfa.state_matrix if next_state == next_states]
                # if there are no next states, the transition on this symbol should go to a sink_state
                else:
                    dfa.delta[(state, symbol)] = 'sink_state'
                    if not dfa.sink_state:
                        dfa.sink_state = True

    def add_final_states(self, dfa):
        # find the final states of the DFA (the compound states that contain at least one NFA final state)
        # ex: [0, 1, 2] contains 0, 1, 2 => if at least one of them is a final state in the NFA, then
        # this is a final state in the DFA
        for state in self.final_states:
            dfa_final_state = [dfa.state_matrix.index(compound_state) for compound_state in dfa.state_matrix if
                               state in compound_state]
            dfa.final_states.update(dfa_final_state)

    def resolve_sink_state(self):
        """
        - if we have a sink_state, we won't call it a sink_state. we'll add it to the state_matrix
        and thus generate a number for it (will always be the greatest state number, since we add it last)
        - we then change each transition in delta that contains the sink_state to that number
        """
        if self.sink_state:
            sink_state = len(self.states)
            self.states.add(sink_state)

            for (current_state, symbol) in self.delta:
                if self.delta[(current_state, symbol)][0] == 's':
                    self.delta[(current_state, symbol)] = [sink_state]

            for symbol in self.alphabet:
                self.delta[(sink_state, symbol)] = [sink_state]

    def nfa_to_dfa(self, dfa):
        # NFA to DFA conversion calling all the necessary functions:
        dfa.add_first_state()
        dfa.alphabet = self.alphabet
        dfa.alphabet.discard('eps')
        self.complete_states(dfa)
        self.add_final_states(dfa)
        dfa.resolve_sink_state()

    def print_to_file(self):

        output_file.write(str(len(self.states)) + '\n')

        s = ''
        for final_state in self.final_states:
            s += str(final_state) + ' '

        s = s[:len(s) - 1]
        output_file.write(s + '\n')

        for (current_state, symbol) in self.delta:
            if self.delta[(current_state, symbol)][0] == 's':
                self.delta[(current_state, symbol)] = [len(self.states) - 1];
            s = str(current_state) + ' ' + symbol + ' ' + str(self.delta[(current_state, symbol)][0]) + '\n'
            output_file.write(s)


if __name__ == '__main__':
    input_file = open(sys.argv[1], 'r')
    output_file = open(sys.argv[2], 'w')

    read_nfa = input_file.read()
    nfa = NFA()
    dfa = NFA()

    NFA.encode(nfa, read_nfa)
    NFA.nfa_to_dfa(nfa, dfa)

    NFA.print_to_file(dfa)
