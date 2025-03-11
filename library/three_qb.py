from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UnitaryGate
from qiskit.circuit.library.standard_gates import XGate, ZGate, YGate
from qiskit.quantum_info import random_unitary
from qiskit.circuit import Delay
import random

class ThreeQbCodeCircuit():
    """
    A class to represent a three-qubit code quantum circuit.
    Attributes
    ----------
    qubits : list
        A list of Qubit objects representing the logical qubits.
    show_ancillas : bool
        A flag to indicate whether to show ancilla qubits in the circuit.
    physical_circuit : QuantumCircuit
        The physical quantum circuit.
    logical_circuit : QuantumCircuit
        The logical quantum circuit.
    type : str
        The type of error correction ('bit_flip' or 'phase_flip').
    Methods
    -------
    __init__(self, k, type):
        Initializes the ThreeQbCodeCircuit with k logical qubits and a specified type.
    initial_state(self, qubit_index=0, state="0"):
        Sets the initial state of the specified qubit.
    reset(self, qubits_index=None):
        Resets the specified qubits.
    encode(self, qubits_index=None):
        Encodes the specified qubits based on the error correction type.
    decode(self, qubits_index=None):
        Decodes the specified qubits based on the error correction type.
    random_error(self, qubits_index=None, physical_qubit=None):
        Applies a random error to the specified qubits.
    measure(self, qubits_index=None, basis='Z'):
        Post-decoding measurement the specified qubits in the given basis.
    measure_all(self, qubits_index=None, basis='Z'):
        Measures all physical qubits of the specified logical qubits in the given basis.
    delay(self, dt, qubits_index=None):
        Applies a delay to the specified qubits.
    x(self, qubits_index=None):
        Applies an X gate to the specified qubits.
    z(self, qubits_index=None):
        Applies a Z gate to the specified qubits.
    spot_syndrome(self, qubits_index=None):
        Spots the syndrome for the specified qubits.
    measure_syndrome(self, qubits_index=None):
        Measures the syndrome for the specified qubits.
    correct(self, qubits_index=None):
        Corrects the errors for the specified qubits.
    barrier(self):
        Adds a barrier to the circuit.
    draw(self, options=None):
        Draws the physical circuit.
    """


    def __init__(self, k, type):
        # k: cantidad de qubits logicos

        self.qubits = []
        for i in range(k):
            self.qubits.append(Qubit('q' + str(i)))
        
        self.show_ancillas = False

        self.physical_circuit = QuantumCircuit(*[q.physical_qubits for q in self.qubits],
                                            #    *[q.qb_measures for q in self.qubits],
                                            #    *[q.ancillas for q in self.qubits],
                                            #    *[q.anc_measures for q in self.qubits],
                                            #    *[q.all_measures for q in self.qubits],
                                               )
        
        self.logical_circuit = QuantumCircuit(*[q.logical_qubit for q in self.qubits])

        if type in ['bit_flip', 'phase_flip']:
            self.type = type
        else:
            raise ValueError("Invalid type ('bit_flip' or 'phase_flip')")
        



    def initial_state(self, qubit_index=0, state="0"):

        if len(state) > 1:
            if len(state) == len(self.qubits):
                for i in range(len(state)):
                    self.initial_state(i, state[i])
            else:
                raise ValueError("Invalid state")
            return
        
        qubit = self.qubits[qubit_index]

        circuit = self.physical_circuit
        qreg = qubit.physical_qubits[0]

        match state:
            case "0":
                pass
            case "1":
                circuit.x(qreg)
                self.logical_circuit.x(qubit.logical_qubit)
            case "+":
                circuit.h(qreg)
                self.logical_circuit.h(qubit.logical_qubit)
            case "-":
                circuit.x(qreg)
                self.logical_circuit.x(qubit.logical_qubit)
                circuit.h(qreg)
                self.logical_circuit.h(qubit.logical_qubit)

    def reset(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)

        for q in qubits_index:
            qubit = self.qubits[q]
            self.physical_circuit.reset(qubit.physical_qubits)
            self.logical_circuit.reset(qubit.logical_qubit)

    def encode(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            match self.type:
                case 'bit_flip':
                    encode_qubit_bit(self.physical_circuit, self.qubits[q])
                case 'phase_flip':
                    encode_qubit_phase(self.physical_circuit, self.qubits[q])

    def decode(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            match self.type:
                case 'bit_flip':
                    decode_qubit_bit(self.physical_circuit, self.qubits[q])
                case 'phase_flip':
                    decode_qubit_phase(self.physical_circuit, self.qubits[q])

    def random_error(self, qubits_index=None, physical_qubit=None):

        self.physical_circuit.barrier()

        qubits_index = self.parse_index(qubits_index)

        u = UnitaryGate(random_unitary(2), label='E')

        for qi in qubits_index:
            q = self.qubits[qi]
            error_qubit_index = random.randint(0, len(q.physical_qubits)-1) if physical_qubit is None else physical_qubit
            self.physical_circuit.append(u, [q.physical_qubits[error_qubit_index]])

    def measure(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        circuit.barrier()

        for q in qubits_index:
            # basis: base logica
            creg = self.qubits[q].qb_measures[0]
            qreg = self.qubits[q].physical_qubits[0]

            circuit.add_register(creg)
            
            if basis == 'Z':    # medir 0 o 1 logico
                pass

            if basis == 'X':    # medir + o - logico
                circuit.h(qreg)

            circuit.measure(qreg, creg)

    def measure_all(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        circuit.barrier()

        for q in qubits_index:
            # basis: base logica

            if self.show_ancillas and not self.qubits[q].syndrome_measured:
                qreg = [*self.qubits[q].physical_qubits, *self.qubits[q].ancillas]
                creg = self.qubits[q].all_measures
            else:
                qreg = self.qubits[q].physical_qubits
                creg = self.qubits[q].qb_measures

            circuit.add_register(creg)
            
            if basis == 'Z':    # medir 0 o 1 logico
                pass

            if basis == 'X':    # medir + o - logico
                circuit.h(qreg)
                
            circuit.measure(qreg, creg)

    def delay(self, dt, qubits_index=None):
        
        self.physical_circuit.barrier()

        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            delay_on_qubit(self.physical_circuit, self.qubits[q], dt)
            self.logical_circuit.append(Delay(dt), self.qubits[q].logical_qubit)
        
        self.physical_circuit.barrier()

    def x(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            if self.type == 'bit_flip':
                x_on_qubit(self.physical_circuit, self.qubits[q])
            if self.type == 'phase_flip':
                z_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.x(self.qubits[q].logical_qubit)

    def z(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            if self.type == 'bit_flip':
                z_on_qubit(self.physical_circuit, self.qubits[q])
            if self.type == 'phase_flip':
                x_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.z(self.qubits[q].logical_qubit)

    def spot_syndrome(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        self.show_ancillas = True
        for q in qubits_index:
            self.physical_circuit.add_register(self.qubits[q].ancillas)
            spot_syndrome_qubit(self.physical_circuit, self.qubits[q], self.type)

    def measure_syndrome(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            self.physical_circuit.add_register(self.qubits[q].anc_measures)
            self.physical_circuit.measure(self.qubits[q].ancillas, self.qubits[q].anc_measures[::-1])
            self.qubits[q].syndrome_measured = True

    def correct(self, qubits_index=None, partial_measurements=False):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            correct_qubit(self.physical_circuit, self.qubits[q], self.type, partial_measurements=partial_measurements)
            

    def barrier(self):
        self.physical_circuit.barrier()
        self.logical_circuit.barrier()

    def draw(self, options = None):
        return self.physical_circuit.draw(options)
    
    def parse_index(self, qubits_index):
        if qubits_index is None:
            qubits_index = range(len(self.qubits))
        elif not isinstance(qubits_index, list):
            qubits_index = [qubits_index]
        return qubits_index 



class Qubit:

    def __init__(self, name) -> None:
        # 3 qubits fisicos por qubit logico
        self.logical_qubit = QuantumRegister(1, name) # representacion del qubit logico

        self.physical_qubits = QuantumRegister(3, name)
        self.ancillas = QuantumRegister(2, name + '_anc')

        self.qb_measures = ClassicalRegister(3, name + '_meas')
        self.anc_measures = ClassicalRegister(2, name + '_anc_meas')
        self.all_measures = ClassicalRegister(3+2, name + '_all_meas')

        self.name = name

        self.syndrome_measured = False

    


def encode_qubit_bit(circuit, qubit):

    qreg = qubit.physical_qubits

    circuit.barrier()

    circuit.cx(qreg[0], qreg[1])
    circuit.cx(qreg[0], qreg[2])

def encode_qubit_phase(circuit, qubit):

    qreg = qubit.physical_qubits

    circuit.barrier()

    circuit.cx(qreg[0], qreg[1])
    circuit.cx(qreg[0], qreg[2])
    circuit.h(qreg)

def decode_qubit_bit(circuit, qubit):

    qreg = qubit.physical_qubits

    circuit.barrier()

    circuit.cx(qreg[0], qreg[2])
    circuit.cx(qreg[0], qreg[1])

def decode_qubit_phase(circuit, qubit):

    qreg = qubit.physical_qubits

    circuit.barrier()

    circuit.h(qreg)
    circuit.cx(qreg[0], qreg[2])
    circuit.cx(qreg[0], qreg[1])

def delay_on_qubit(circuit, qubit, dt):
    for q in qubit.physical_qubits:
        circuit.append(Delay(dt), [q])

def x_on_qubit(circuit, qubit):
    circuit.x(qubit.physical_qubits)

def z_on_qubit(circuit, qubit):
    circuit.z(qubit.physical_qubits)

def spot_syndrome_qubit(circuit, qubit, type):
    
    qreg = qubit.physical_qubits
    anc = qubit.ancillas

    if type == 'bit_flip':
        circuit.cx(qreg[0], anc[0])
        circuit.cx(qreg[1], anc[0])
        circuit.cx(qreg[1], anc[1])
        circuit.cx(qreg[2], anc[1])

    if type == 'phase_flip':
        circuit.h(anc)
        circuit.cx(anc[0], qreg[0])
        circuit.cx(anc[0], qreg[1])
        circuit.cx(anc[1], qreg[1])
        circuit.cx(anc[1], qreg[2])
        circuit.h(anc)
    
    circuit.barrier()
    
def correct_qubit(circuit, qubit, type, partial_measurements=False):
    
    qreg = qubit.physical_qubits
    anc = qubit.ancillas
    syn = qubit.anc_measures

    if partial_measurements:
        match type:
            case 'bit_flip':
                circuit.append(XGate(), [qreg[2]]).c_if(syn, 1)
                circuit.append(XGate(), [qreg[0]]).c_if(syn, 2)
                circuit.append(XGate(), [qreg[1]]).c_if(syn, 3)

            case 'phase_flip':
                circuit.append(ZGate(), [qreg[2]]).c_if(syn, 1)
                circuit.append(ZGate(), [qreg[0]]).c_if(syn, 2)
                circuit.append(ZGate(), [qreg[1]]).c_if(syn, 3)
    else:
        match type:
            case 'bit_flip':
                circuit.append(XGate().control(2, ctrl_state='10'), [anc[0], anc[1], qreg[2]])
                circuit.append(XGate().control(2, ctrl_state='01'), [anc[0], anc[1], qreg[0]])
                circuit.append(XGate().control(2, ctrl_state='11'), [anc[0], anc[1], qreg[1]])

            case 'phase_flip':
                circuit.append(ZGate().control(2, ctrl_state='10'), [anc[0], anc[1], qreg[2]])
                circuit.append(ZGate().control(2, ctrl_state='01'), [anc[0], anc[1], qreg[0]])
                circuit.append(ZGate().control(2, ctrl_state='11'), [anc[0], anc[1], qreg[1]])
        

    circuit.barrier()
        