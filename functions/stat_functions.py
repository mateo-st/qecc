import numpy as np

def generate_uniform_distribution(qb_len, valid_states, snr=None):

    states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]

    alpha = {}

    if not snr:
        for s in states:
            alpha[s] = 1/len(valid_states) if s in valid_states else 0

    else:
        if snr > 1:
            non_valid_prob = 1 / (len(valid_states)*(snr-1) + 2**qb_len)
            for s in states:
                alpha[s] = non_valid_prob if s not in valid_states else snr*non_valid_prob
        else:
            raise ValueError('The SNR should be greater than 1')

    return alpha


def calculate_tvd(results, expected_distribution, percentage=True):

    states = list(results.keys())

    if percentage:
        return sum([abs(results[s]/100 - expected_distribution[s]) for s in states])/2
    else:
        return sum([abs(results[s] - expected_distribution[s]) for s in states])/2


def calculate_kl(results, expected_distribution, percentage=True):

    states = list(results.keys())

    per = 100 if percentage else 1

    kl = 0

    for s in states:
            
        if expected_distribution[s] != 0:

            if results[s] == 0:
                raise ValueError('The state {} has a probability of 0 in the results distribution'.format(s))
            
            else:
                kl += expected_distribution[s] * np.log(expected_distribution[s] / (results[s]/per))

        # if expected_distribution[s] == 0 -> kl += 0

    return kl

def distribution_function(x, distribution, percentage=True):
    per = 100 if percentage else 1
    return sum([prob/per for state, prob in distribution.items() if int(state, 2) <= x])

def calculate_test_ks(results, expected_distribution, percentage=True):

    sup = 0

    for state in results.keys():
        dif = abs(
            distribution_function(int(state,2), results, percentage=percentage)
            - distribution_function(int(state,2), expected_distribution, percentage=False)
        )
        sup = dif if dif > sup else sup

    return sup



# valid_states = ['000', '001', '010', '011']
# alpha = generate_uniform_distribution(3, valid_states)
# # noise_alpha = generate_uniform_distribution(3, valid_states, snr=10)
# # print('kl', calculate_kl(noise_alpha, alpha))
# # print('tvd', calculate_tvd(noise_alpha, alpha))

# import matplotlib.pyplot as plt
# snrs = range(2, 200)
# plt.plot(snrs, [calculate_kl(generate_uniform_distribution(3, valid_states, snr=snr), alpha) for snr in snrs], label='kl')
# plt.plot(snrs, [2*calculate_tvd(generate_uniform_distribution(3, valid_states, snr=snr), alpha)**2 for snr in snrs], label='tvd')
# plt.legend()
# plt.show()



def get_possible_states(qb_len):
    return [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]

def generate_gray_code(n):
    if n == 0:
        return ["0"]
    if n == 1:
        return ["0", "1"]

    previous_gray_code = generate_gray_code(n - 1)
    gray_code = []

    for code in previous_gray_code:
        gray_code.append("0" + code)
    for code in reversed(previous_gray_code):
        gray_code.append("1" + code)

    return gray_code


def estimate_T1_parameter(t_array, log_y_array):

    x = t_array
    y = log_y_array

    T1 = - np.sum([x_i**2 for x_i in x]) / np.sum([x[i]*y[i] for i in range(len(x))])
    T1_std = np.sqrt(1/len(x) * np.sum([(np.exp(-x[i]/T1)/2 - y[i])**2 for i in range(len(x))]))

    return T1, T1_std

def calculate_snr(results, valid_states):
    s = np.mean([
            value for key, value in results.items() if key in valid_states
        ])
    n = np.mean([
            value for key, value in results.items() if key not in valid_states
        ])
    return s/n
