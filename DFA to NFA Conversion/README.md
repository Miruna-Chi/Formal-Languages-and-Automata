# NFA-> DFA conversion (Subset Construction)

### state_matrix ~

Because DFA states can correspond to multiple NFA states
(NFA: on the same symbol we can go on several paths +
transitions on epsilon), I decided to create a matrix of
states for the DFA:

  - the matrix is a list composed of sorted lists (as not to
be repeated) of NFA states
  - each list represents a state of the DFA composed of one or
several NFA states. The index of each list will be the name
of the states of the DFA
Eg: [[0], [0, 1, 2], [0, 2], [1, 2] ...] -> [0, 1, 2, 3 ...]


### find_next_state

Starting with state 0 (we will create more and more states according
to the paths we take), for each symbol in the alphabet, we look for all
the following valid states (so for a compound state, we go to all the
states that form it, including all transitions on epsilon). We do a conditioned BFS
for all possible states starting from the current state. So we will have a
queue and a set of visited states. An element in the queue will be a tuple that
looks like this:
(Current_partial_state, symbol, is_it_necessary_to_look_for_the_symbol?)
Ex: (1, 'b', True)

The third component of the tuple tells me if I still need to search
for the symbol further (if I found it once on the current path,
I am only allowed to look for transitions on epsilon further). If I haven't found
the symbol on the current path, I can go both on transitions on epsilon,
as well as on the symbol.

The tuples that have the same first two elements and the third is different
(if in the same state, we are seeking the symbol in one tuple and not seeking it
in another tuple, it means that there are at least two paths that have lead to
that state, so it will be useful to search further for both tuples.

States are considered valid (and we add them to the following set of states for the
current symbol) if they are part of the tuples for which we have already found
the symbol on the current path (the third component is False).

As I explained earlier, a set will be formed with the following
valid partial states for each compound state, forming another compound
state (which we add to the state matrix if it does not already exist).

Ex: We are in state 012 and we have the symbol 'b'
We call the find_next_state function for 0, 1, 2 separately. Every call will
return a set (empty or not) of the following valid states. The final set
will be formed from the 3 sets and will be part of the state matrix.
In the absence of relevant transitions in the NFA delta, the final set could be empty.
Then the transition will lead to a sink_state.

### sink_state

After going through all the states, if we know that there is at least one transition
that leads to a sink_state, we add this state to the current states (it will be the last
line of the matrix, so the state with the largest number) and we make the necessary changes
in delta.

### final_states

The final states will be states from the matrix of states that contain
at least one final state of the NFA.
ex:
State matrix: [[0], [1, 2], [0, 1], ...]
NFA finals: 0, 2
DFA final states: [0], [1, 2], so states 0, 1 list indices
in the state matrix correspond to the names of the DFA states)
