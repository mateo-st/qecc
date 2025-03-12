from qiskit import transpile
import json
import sys
import os

sys.path.append(os.path.abspath("../../.."))
from objects.steane_code_circuit import SteaneCodeCircuit
import warnings
from qiskit.circuit import Delay
import json
import math


def get_layout(circuit, qb_len=1):
    layout = circuit._layout.initial_layout.get_virtual_bits()
    keys = [layout[i] for i in layout]
    return keys[:qb_len]


def get_transpile(circuit, backend,
                  scheduling_method="asap", optimization_level=3,
                  iterations=10, initial_layout=None):
    
    transpiles = []
    k = 0
    while k < iterations:

        try:
            isa = transpile(circuit, backend, scheduling_method=scheduling_method, optimization_level=optimization_level)
            if initial_layout:
                while get_layout(isa, qb_len=len(initial_layout)) != initial_layout:
                    # print(get_layout(isa, qb_len=len(initial_layout)))
                    isa = transpile(circuit, backend, scheduling_method=scheduling_method, optimization_level=optimization_level)
            transpiles.append(isa)

            k += 1

        except:
            pass


    return [t for t in transpiles if t.depth() == min([t.depth() for t in transpiles])][0]


def TVD(p, q):
    ''' 
    Given two discrete distributions p and q represented by dictionaries {i: p_i} and {j: q_j} return the Total Variation Distance.

    The domain (keys) of the distribution might not be the same. We take the domain of the distributions as the union of the two domains
    under the assumption that if a key is not in a dictionary that represent a distribution, its probability is zero.
    
    Parameters:
        p (dict): Python dictionary representing the first distribution
        q (dict): Python dictionary representing the second distribution

    Returns: 
        tvd (float): Total Variation Distance between the distribution p and q.
    '''


    tvd = 0
    P = p.copy()
    Q = q.copy()
    # Complete dictionaries: 
    for P_i in P.keys():
        if P_i not in Q.keys():
            Q[P_i] = 0

    for Q_i in Q.keys():
        if Q_i not in P.keys():
            P[Q_i] = 0

    for P_i in P.keys():
        for Q_i in P.keys():
            if P_i == Q_i:
                tvd += abs(P[P_i] - Q[Q_i])

    return 0.5*tvd


def get_result(json_file, experiment_name, service, num_results = 1, first_result = 0, printing = True):
    '''
    Given a json_file, experiment_name and service, return the last job with status = DONE

    Parameters:
        json_file (String): name of the JSON file
        experiment_name (String): name of the experiment of the JSON file
        service (QiskitRuntimeService): User service used to retrieve the job
        num_results (int): num of results to be returned
        first_result (int): first result to be returned. If 0 we start from the last result

    Returns: 
        None if the job does not exists. result, job if the job is found.
    '''

    with open(json_file) as f:
        experiment_results = json.load(f)

    results_list = []
    jobs_list = []


    if (experiment_name in experiment_results.keys()):
        # Check for repeated job_id. If job_id is not repeated we add the job to the json
        results = experiment_results[experiment_name]

        # Get Last ID:
        k = 0
        for result in results[::-1][first_result::]: # Reverse the results list and start from first_result
            
            job = service.job(result['job_id']) # Retrieve the job
            job_status = job.status()

            if printing:
                print(f" > Job ID: {result['job_id']}")
                print(f" > Job Status: {job_status}\n")
                

            if (job_status == 'DONE'):
                k += 1
                if num_results == 1: 
                    return result, job
                
                results_list.append(result)
                jobs_list.append(job)

                if k == num_results:
                    return results_list, jobs_list
                
        return results_list, jobs_list


    else:
        if printing:
            print("There is no experiment with this name")

    return


def epsilon(qubit_count, delta, shots):
    ''' 
    For a given number of qubit_count, a float delta representing the probability or error and the number of shots, return the 
    error epsilon that we can ensure with probability at least 1-delta for the TVD estimation
    '''

    return max( math.sqrt(2**qubit_count / shots) , math.sqrt(2 * math.log(2 / delta) / shots) )


def load_experiment(state, basis, error_correction, backend, transpile_iterations = None, logical_operations = None, t_array = None, t_array_unit = 'dt', initial_layout = None, printing = True):
    '''
    Returns a list of transpiled circuits corresponding to one experiment. An experiment is determined by an initial state, 
    a basis (or measurement method), if we apply or not error correction, the backend in which we ran the experimint, 
    which logical operations do we apply, an initial layout and a t_array (if the measurement involves a time delay).

    Parameters:
        - state (String): Initial encoded state. it can be '+' | '-' | '1' | '0'
        - basis (String): Observable of the measurement: 'all' | 'z' | 'x'
        - backend (qiskit backend): Bakend of qiskit used for transpile the circuit
        - logical_operations (list[String]): List of logical operations to apply to the circuit. It elements are 'x' | 'z' | 'y' | 'h' and 
                                             the order of appearence in the list is the order of the applications of the operations. 
                                             i.e logical_operations = ['x', 'h'] indicates first an X_L and then an H_L
                                                Default: None
        - t_array (list[float]): list of times delays in dt to append to the circuit. If None then we do not apply any delay
                                    Default: None
        - initial_layout (list[int]): Initial layout for transpilation. If None we transpile a circuit first to get an initial layout
                                        Default: None
        - printing (boolean): If True we print to console in the function.
                                Default: True  

    Returns:
        - circuits (list[QuantumCircuits]): list of transpiled circuits
        - qc_circuits (list[QuantumCircuits]): list of origina circuits
        - initial_layout (list[int]): To retrieve the initial layout.
        - estimated_durations (list[float]): List of estimated times un us for each circuit - important to note that is in us
    '''

    # Get the dt of the selected backend in nano seconds and print it.
    dt = backend.configuration().dt * 10**9
    if printing:
        print(f" > dt in seconds: {backend.configuration().dt} s")
        print(f" > dt in ns: {round(dt, 3)} ns")


    # Define initial layout if None is given:
    if initial_layout == None:
        qubit_count = 7
        if error_correction:
            qubit_count += 6

        if basis != 'all':
            qubit_count += 1

        # Create a circuit with no delay to get the layout
        qc_steane = SteaneCodeCircuit(logical_qubit_count=1)
        if state == '+':
            qc_steane.h(0)
            qc_steane.encode(append=True)

        elif state == '-':
            qc_steane.x(0)
            qc_steane.h(0)
            qc_steane.encode(append=True)

        else:
            qc_steane.encode(append=True, initial_state=state)

        qc_steane.barrier()
        if logical_operations:
            for op in logical_operations:
                if op == 'x':
                    qc_steane.x(0)

                elif op == 'z':
                    qc_steane.z(0)

                elif op == 'y':
                    qc_steane.y(0)

                elif op == 'h':
                    qc_steane.h(0)

            qc_steane.barrier()

        if t_array:
            qc_steane.delay(0)
            qc_steane.barrier()

        if error_correction:
            qc_steane.correct(append=True)

        qc_steane.measure_all(basis = basis)

        # Get physical circuit and transpile it
        qc = qc_steane.physical_quantum_circuit
        isa_circuit = get_transpile(qc, backend, iterations=100, scheduling_method="asap", optimization_level=3)
        initial_layout = get_layout(isa_circuit, qb_len=qubit_count)

    if printing:
        print(f" > Initial layout: {initial_layout}")


    if not transpile_iterations:
        transpile_iterations = 10
    circuits = []
    qc_circuits = []
    estimated_durations = []
    if t_array:

        if printing:
            if t_array_unit == 'dt':
                print(f" > Delays in dt: {t_array}")
                print(f" > Delays un us: {[round(t*dt * 10**(-3) , 3) for t in t_array]}")

            else:
                print(f" > Delays in {t_array_unit}: {t_array}")
        

        for t in t_array:
            # Generate circuit without error correction
            qc_steane = SteaneCodeCircuit(logical_qubit_count=1)

            if state == '+':
                qc_steane.h(0)
                qc_steane.encode(append=True)

            elif state == '-':
                qc_steane.x(0)
                qc_steane.h(0)
                qc_steane.encode(append=True)

            else:
                qc_steane.encode(append=True, initial_state=state)

            qc_steane.barrier()
            if logical_operations:
                for op in logical_operations:
                    if op == 'x':
                        qc_steane.x(0)

                    elif op == 'z':
                        qc_steane.z(0)

                    elif op == 'y':
                        qc_steane.y(0)

                    elif op == 'h':
                        qc_steane.h(0)

                qc_steane.barrier()

            qc_steane.delay(t, unit=t_array_unit)

            qc_steane.barrier()

            if error_correction:
                qc_steane.correct(append=True)
                qc_steane.barrier()

            qc_steane.measure_all(basis=basis)

            # Get and transpile physical_quantum_circuit
            qc = qc_steane.physical_quantum_circuit

            isa_circuit = get_transpile(qc, backend, iterations=transpile_iterations, scheduling_method="asap", optimization_level=3, initial_layout=initial_layout)
            circuits.append(isa_circuit)
            qc_circuits.append(qc)

            # QuantumCircuit.duration is deprecated. Ignore the warning
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                total_duration = isa_circuit.duration * dt * 10**(-3)

            estimated_durations.append(total_duration)

            if printing:
                print(f"Circuit Depth: {isa_circuit.depth()}")
                print(f"Delay Duration: {round(t*dt * 10**(-3), 3)} us")
                print(f"Estimated Total Duration: {round(total_duration, 3)} us\n")


    else:
        if printing:
            print(f" > Experiment without delay (Generating only one circuit)")

        # Generate circuit without error correction
        qc_steane = SteaneCodeCircuit(logical_qubit_count=1)

        if state == '+':
            qc_steane.h(0)
            qc_steane.encode(append=True)

        elif state == '-':
            qc_steane.x(0)
            qc_steane.h(0)
            qc_steane.encode(append=True)

        else:
            qc_steane.encode(append=True, initial_state=state)

        qc_steane.barrier()
        if logical_operations:
            for op in logical_operations:
                if op == 'x':
                    qc_steane.x(0)

                elif op == 'z':
                    qc_steane.z(0)

                elif op == 'y':
                    qc_steane.y(0)

                elif op == 'h':
                    qc_steane.h(0)
            qc_steane.barrier()

        if error_correction:
            qc_steane.correct(append=True)
            qc_steane.barrier()

        qc_steane.measure_all(basis=basis)

        # Get and transpile physical_quantum_circuit
        qc = qc_steane.physical_quantum_circuit

        isa_circuit = get_transpile(qc, backend, iterations=transpile_iterations, scheduling_method="asap", optimization_level=3, initial_layout=initial_layout)
        circuits.append(isa_circuit)
        qc_circuits.append(qc)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            total_duration = isa_circuit.duration * dt * 10**(-3)

        estimated_durations.append(total_duration)

        if printing:
            print(f"Circuit Depth: {isa_circuit.depth()}")
            print(f"Estimated Total Duration: {round(total_duration, 3)} us\n")


    return circuits, qc_circuits, initial_layout, estimated_durations


def run_experiment(json_file, experiment_name, circuits, shots, sampler, expected_distribution, initial_layout, estimated_durations, estimated_durations_unit, encoder_type, t_array = None, t_array_unit = None, printing = True):
    '''
    Run the circuit and save metadata and job_id in json_file

    Parameters:
        - json_file (String): abspath of JSON file with the result
        - experiment_name (String): name of the experiment. Used as a key in the json_file
        - circuits (list[QuantumCircuits]): List of transpiled quantum circuits
        - shots (int): shots to run each circuit
        - expected_distribution (dict): Expected distribution if there is no errors. Used to compute the TVD
        - initial_layout (list[int]): Initial layout for transpilation.
        - estimated_durations (list[float]): List of estimated durations in us
        - encoder_type (String): Indicates if a particula encoder is used. Can be 'universal', '0' or '1'
        - t_array (list[float]): list of dt. Can be none 
        - printing (boolean): If True we print to console in the function.
                                Default: True  

    Returns:
        - experiments_results (dict): Changed JSON of json_file
    '''

    # Run circuit and take job_id
    job = sampler.run(circuits, shots = shots)
    job_id = job.job_id()

    if printing:
        print(f" > job_id: {job_id}")
        print(f" > job_status: {job.status()}")

    # Save data in a json_file
    if t_array:
        metadata = {'expected_distribution': expected_distribution, 
                    't_array': t_array, 
                    'initial_layout':initial_layout, 
                    'estimated_duration':estimated_durations, 
                    'encoder_type':encoder_type,
                    't_arrya_units':t_array_unit,
                    'estimated_duration_units':estimated_durations_unit}

    else: 
        metadata = {'expected_distribution': expected_distribution, 
                    'initial_layout':initial_layout, 
                    'estimated_duration': estimated_durations, 
                    'encoder_type':encoder_type,
                    'estimated_duration_units':estimated_durations_unit}


    with open(json_file) as f:
        experiment_results = json.load(f)


    if (experiment_name in experiment_results.keys()):
        # Check for repeated job_id. If job_id is not repeated we add the job to the json
        results = experiment_results[experiment_name]
        if job_id not in [results[i]['job_id'] for i in range(len(results))]:
            experiment_results[experiment_name].append({"job_id":job_id, "metadata":metadata})

    else:
        experiment_results[experiment_name] = [{"job_id":job_id, "metadata":metadata}]


    # Writing back to JSON
    with open(json_file, "w") as f:
        f.write(json.dumps(experiment_results, indent=2))

    if printing:
        print(json.dumps(experiment_results[experiment_name], indent=2))

    return