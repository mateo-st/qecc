from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator, Aer
from qiskit import transpile

import numpy as np


def sampler_simulation(circuit, samples):

    from qiskit_aer.primitives import SamplerV2

    exact_sampler = SamplerV2()

    # Transpilamos el circuito
    pass_manager = generate_preset_pass_manager(3, AerSimulator())
    isa_circuit = pass_manager.run(circuit)

    # Corremos el circuito:
    pub = (isa_circuit, None, samples) # Notemos que tambien funciona si le pasamos el circuito qc
    job = exact_sampler.run([pub])

    result = job.result()
    pub_result = result[0]

    return pub_result


def statevector_simulation(circuit, qb_len, epsilon=0.0001):
    simulator = AerSimulator()
    qct = transpile(circuit, simulator)

    state = np.array(Aer.get_backend('statevector_simulator').run(qct, shots=1).result().get_statevector())

    count = {}

    for i in range(len(state)):
        b = format(i, f'0{qb_len}b')
        if abs(state[i]) > epsilon:
            count[b[::-1]] = state[i]

    return count

def extract_simulation_results(pub_result, type=None, reverse_order=True, omit_zeros=False):

    if not isinstance(pub_result, list):
        pub_result = [pub_result]

    measures_results = {}
    
    for experiment in pub_result:
    
        for measure in experiment.data:
    
            if measure not in measures_results:
                measures_results[measure] = []

            counts = experiment.data[measure].get_counts()

            qb_len = len(list(counts.keys())[0])
            states = [bin(i)[2:].zfill(qb_len) for i in range(2**qb_len)]
            shots = sum(counts.values())

            res = {}

            for s in states:

                if reverse_order:
                    if omit_zeros and s[::-1] not in counts:
                        continue
                    res[s] = counts[s[::-1]] if s[::-1] in counts else 0
                else:
                    if omit_zeros and s not in counts:
                        continue
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
