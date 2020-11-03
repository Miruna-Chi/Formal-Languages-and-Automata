import sys  # provides access to command line arguments


def suffix_prefix(pattern, c):
    # Find the longest prefix of the pattern that is a suffix of what we found so far in the text

    pattern_c = pattern + chr(c)   # concatenate the pattern with the current character
    subpattern_len = len(pattern)  # start from the longest possible length, then decrement it in a loop

    while subpattern_len != 0:
        # compare the current pattern prefix with the suffix of the same length (up to the current text position)
        if pattern[:subpattern_len] == pattern_c[len(pattern_c) - subpattern_len:]:
            # return the length of the matched prefix (the next state after character c is found)
            return subpattern_len
        subpattern_len -= 1

    return subpattern_len


def compute_delta(pattern):
    rows = len(pattern) + 1  # epsilon + all pattern prefixes
    columns = 26             # corresponding to A-Z

    delta = []

    # Initialize matrix
    for i in range(rows):
        a = [0] * columns
        delta.append(a)

    # only one entry will be != 0 on the first row:
    delta[0][ord(pattern[0]) - 65] = 1;

    for i in range(1, rows):
        for j in range(columns):
            # if current character(column) matches the next character in the pattern, next state = current_state + 1
            if i < len(pattern) and ord(pattern[i]) == j + 65:
                delta[i][j] = i + 1;
            else:
                delta[i][j] = suffix_prefix(pattern[0:i], j + 65)

    return delta


def string_matcher(p, t):
    q = 0;  # current_state
    delta = compute_delta(p)
    for i in range(0, len(t)):
        # decide next state after each character in the text (find in delta)
        # ord(char) - 65 = ascii(char) - 65 => column number [0-25]
        q = delta[q][ord(t[i]) - 65]
        if q == len(p):
            # if the pattern was found, print the position where it was found
            output_file.write(str(i - (len(p) - 1)) + ' ')

    output_file.write('\n')


if __name__ == '__main__':
    input_file = open(sys.argv[1], 'r')
    output_file = open(sys.argv[2], 'w')

    # read the whole file
    string12 = input_file.read()

    # split it by new line so the first element of the newly created list will be string1, the second = string2
    string12 = list(string12.split('\n'))
    string1 = string12[0]
    string2 = string12[1]

    string_matcher(string1, string2)

    input_file.close()
    output_file.close()
