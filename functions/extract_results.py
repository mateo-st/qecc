import json


# IBM ------------------------------

def extract_results_IBM(pub_result, type=None, reverse_order=True):
    """
    Extracts and processes measurement results from a list of experiments.
    Args:
        pub_result (list): A list of experiment results, where each experiment is a dictionary containing measurement data.
        type (str, optional): The type of result to return. Can be 'percentage' for percentage results or 'probability' for probability results. Defaults to None.
        reverse_order (bool, optional): If True, reverses the order of the qubit states in the results. Defaults to True.
    Returns:
        dict: A dictionary where keys are measurement names and values are lists of dictionaries. Each dictionary contains the processed results for each state.

    Printing example:
        for key, value in extract_results_IBM(pub_result, type='probability', reverse_order=True).items():
            print(key, *value, sep='\n\t')
    """

    measures_results = {}
    
    for experiment in pub_result:
    
        for measure in experiment['__value__']['data']:
    
            if measure not in measures_results:
                measures_results[measure] = []

            counts = experiment['__value__']['data'][measure].get_counts()

            qb_len = len(list(counts.keys())[0])
            states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]
            shots = sum(counts.values())

            res = {}

            for s in states:

                if reverse_order:
                    res[s] = counts[s[::-1]] if s[::-1] in counts else 0
                else:
                    res[s] = counts[s] if s in counts else 0

                match type:
                    case 'percentage':
                        res[s] = res[s] / shots * 100 # %
                    case 'probability':
                        res[s] = res[s] / shots
                    case 'counts':
                        pass
                
            measures_results[measure].append(res)
    
    return measures_results


def extract_raw_results(pub_result):
    measures_results = {}
    for shot in pub_result:
        for measure in shot['__value__']['data']:
            if measure not in measures_results:
                measures_results[measure] = []
            measures_results[measure].append(shot['__value__']['data'][measure].get_counts())

    return measures_results


# IONQ ------------------------------

def extract_results_json_IONQ(json_file, type=None, reverse_order=True):

    return_results = []

    with open(json_file, 'r') as file:
        data = json.load(file)

    for experiment in data["Results"]:
        histogram = experiment["Histogram"]

        counts = {}

        for outcome in histogram:
            state = ''.join(c for c in outcome["Display"] if c in ['0', '1'])
            counts[state] = outcome["Count"]

        qb_len = len(list(counts.keys())[0])
        states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]
        shots = sum(counts.values())

        res = {}

        for s in states:

            if reverse_order:
                res[s] = counts[s[::-1]] if s[::-1] in counts else 0
            else:
                res[s] = counts[s] if s in counts else 0

            match type:
                case 'percentage':
                    res[s] = res[s] / shots * 100 # %
                case 'probability':
                    res[s] = res[s] / shots
                case 'counts':
                    pass

        return_results.append(res)

    return return_results


def extract_results_IONQ(pub_result, type=None, reverse_order=True):

    counts = pub_result.data()['counts']

    # if type == 'probability':
    #     counts = pub_result.data()['probabilities']

    qb_len = len(list(counts.keys())[0])
    states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]
    shots = sum(counts.values())

    res = {}

    for s in states:

        if reverse_order:
            res[s] = counts[s[::-1]] if s[::-1] in counts else 0
        else:
            res[s] = counts[s] if s in counts else 0

        match type:
            case 'percentage':
                res[s] = res[s] / shots * 100 # %
            case 'probability':
                res[s] = res[s] / shots
            case 'counts':
                pass

    return res