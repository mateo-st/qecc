from qiskit import transpile
from qiskit_ionq import IonQProvider


def get_layout(circuit, qb_len=1):
    layout = circuit._layout.initial_layout.get_virtual_bits()
    keys = [layout[i] for i in layout]
    return keys[:qb_len]

def get_transpile(circuit, backend,
                  scheduling_method="asap", optimization_level=3,
                  iterations=10, initial_layout=None,
                  min_depth=None
                  ):
    
    transpiles = []
    for i in range(iterations):
        isa = transpile(circuit, backend, scheduling_method=scheduling_method, optimization_level=optimization_level)
        if initial_layout:
            while get_layout(isa, qb_len=len(initial_layout)) != initial_layout:
                # print(get_layout(isa, qb_len=len(initial_layout)))
                isa = transpile(circuit, backend, scheduling_method=scheduling_method, optimization_level=optimization_level)
            if min_depth and isa.depth() <= min_depth:
                return isa
        transpiles.append(isa)


    return [t for t in transpiles if t.depth() == min([t.depth() for t in transpiles])][0]


def ionq_transpile(qc_abstract):
    '''
    Given a Qiskit Quantum circuit transpile the circuit with the native gates of Aria-1
    '''

    provider = IonQProvider()
    backend_native = provider.get_backend("simulator", gateset="native")

    qc_native = transpile(qc_abstract, backend=backend_native)
    qc_native.draw("mpl")

    return qc_native