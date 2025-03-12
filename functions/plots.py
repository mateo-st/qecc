import matplotlib.pyplot as plt
from functions.stat_functions import distribution_function

plotting_colors = [
        'green', 'blue', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white',
        'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'lightblue', 'darkgreen'
]

def hamming_distance(s, valid_states):
    return min([sum([1 for i in range(len(s)) if s[i] != vs[i]]) for vs in valid_states])

def error_positions(s, valid_states):
    possible_errors = []
    for v in valid_states:
        errors = [i for i in range(len(s)) if s[i] != v[i]]
        possible_errors.append(errors)

    return [p for p in possible_errors if len(p) == min([len(p) for p in possible_errors])]

def print_order_results(results, valid_states=None, type='percentage', limit=None):

    if not limit:
        limit = len(results)

    if not valid_states:

        print("state: result")
        print(*[
            f"{state}: {round(results[state], 3)}%"
            for state in sorted(results, key = lambda x: results[x], reverse=True)[:limit]
        ], sep='\n')
        
    else: # show hamming distance and error positions

        print("state: result, HD, error positions")
        print(*[
            f"{state}: {round(results[state], 3)}%, {hamming_distance(state, valid_states)}, {error_positions(state, valid_states)}"
            for state in sorted(results, key = lambda x: results[x], reverse=True)[:limit]
        ], sep='\n')


def plot_results_hamming_distance(results, qb_len, valid_states, omit_zeros=False, title=None, integer_representation=False):

    states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]

    for hd in range(qb_len+1):
        states_hd = [s for s in states if hamming_distance(s, valid_states) == hd]
        
        if omit_zeros:
            states_hd = [s for s in states_hd if results[s] > 0]
        
        if len(states_hd) > 0:

            if integer_representation:
                x = [int(s, 2) for s in states_hd]
            else:
                x = states_hd
            
            plt.plot(x, [results[i] for i in states_hd], '.', color=plotting_colors[hd%len(plotting_colors)], label=f'HD={hd}')

    if not title:
        title = 'Results by Hamming Distance'
        if omit_zeros:
            title += ' (excluding zeros)'

    if integer_representation:
        plt.xlabel('states (integer representation)')
    else:
        plt.xlabel('states')
        
    plt.ylabel('counts (%)')
    plt.title(title)
    plt.legend()
    plt.show()


def plot_distribution_functions(results, expected_distribution, percentage=True, title=None, style=''):

    x = range(2**len(list(results.keys())[0]))
    y_results = [distribution_function(i, results, percentage=percentage) for i in x]
    y_expected = [distribution_function(i, expected_distribution, percentage=False) for i in x]

    if style == 'step':
        plt.step(x, y_results, where='post', label='Results')
        plt.step(x, y_expected, where='post', label='Expected')
    else:    
        plt.plot(x, y_results, style, label='Results')
        plt.plot(x, y_expected, style, label='Expected')
    plt.legend()

    if not title:
        title = 'Distribution Functions'

    # plt.ylim(0, 1)
    plt.xlabel('states (integer representation)')
    plt.ylabel('probability [0;1]')
    plt.title(title)
    plt.show()


def simple_plot(x, y, title='', labels=['']):

    if not (isinstance(y[0], list) or isinstance(y[0], dict)):
        y = [y]
    
    if isinstance(y[0], dict):
        for i in range(len(y)):
            y[i] = [y_i for y_i in y[i].values()]

    for i in range(len(y)):
        plt.plot(x, y[i], label=labels[i%len(labels)])

    plt.title(title)
    if labels != ['']:
        plt.legend()
    plt.show()