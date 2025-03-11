from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library.standard_gates import XGate, ZGate, YGate
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import random_unitary
from qiskit.circuit import Delay
import random

class FiveQbStabilizerCodeCircuit:
    """
    A class to represent a Five Qubit Stabilizer Code Circuit.
    Attributes
    ----------
    qubits : list
        A list of Qubit objects representing the qubits in the circuit.
    show_ancillas : bool
        A flag to indicate whether to show ancilla qubits.
    physical_circuit : QuantumCircuit
        The physical quantum circuit.
    logical_circuit : QuantumCircuit
        The logical quantum circuit.
    syndromes : dict
        A dictionary mapping syndrome strings to error corrections.
    Methods
    -------
    __init__(k):
        Initializes the circuit with k logical qubits.
    initial_state(qubit_index=0, state="0"):
        Sets the initial state of the specified qubit.
    reset(qubits_index=None):
        Resets the specified qubits.
    encode(qubits_index=None, type='universal'):
        Encodes the specified qubits.
    random_error(qubits_index=None, physical_qubit=None):
        Applies a random error to the specified qubits.
    spot_syndrome(qubits_index=None):
        Spots the syndrome for the specified qubits.
    measure_syndrome(qubits_index=None):
        Measures the syndrome for the specified qubits.
    measure(qubits_index=None, basis='Z'):
        Measures the specified qubits in the given basis.
    measure_all(qubits_index=None, basis='Z'):
        Measures all physical qubits (ancillas included if used) of specified logical qubits in the given basis.
    delay(dt, qubits_index=None):
        Applies a delay to the specified qubits.
    correct(qubits_index=None):
        Corrects errors on the specified qubits.
    x(qubits_index=None):
        Applies an X gate to the specified qubits.
    z(qubits_index=None):
        Applies a Z gate to the specified qubits.
    h(qubits_index=None, swap=True):
        Applies an H gate to the specified qubits.
    cx(control_index, target_index, options=None):
        Applies a controlled-X gate between the control and target qubits.
    cz(control_index, target_index, options=None):
        Applies a controlled-Z gate between the control and target qubits.
    barrier():
        Adds a barrier to the circuit.
    draw(options=None):
        Draws the physical circuit.
    """

    

    def __init__(self, k):
        # k: cantidad de qubits logicos

        self.qubits = []
        for i in range(k):
            self.qubits.append(Qubit('q' + str(i)))

        self.show_ancillas = False

        self.physical_circuit = QuantumCircuit(*[q.physical_qubits for q in self.qubits],
                                            #    *[q.ancillas for q in self.qubits],
                                            #    *[q.anc_measures for q in self.qubits],
                                            #    *[q.qb_measure for q in self.qubits],
                                            #    *[q.qb_measures for q in self.qubits],
                                            #    *[q.qb_state for q in self.qubits],
                                            #    *[q.all_measures for q in self.qubits]
                                               )
        
        self.logical_circuit = QuantumCircuit(*[q.logical_qubit for q in self.qubits])

        self.syndromes = {
            '0000': "None",
            '0001': "X1",
            '1000': "X2",
            '1100': "X3",
            '0110': "X4",
            '0011': "X5",
            '1010': "Z1",
            '0101': "Z2",
            '0010': "Z3",
            '1001': "Z4",
            '0100': "Z5",
            '1011': "Y1",
            '1101': "Y2",
            '1110': "Y3",
            '1111': "Y4",
            '0111': "Y5"
            }

        

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
        qreg_psi = qubit.physical_qubits

        match state:
            case "0":
                pass
            case "1":
                circuit.x(qreg_psi[0])
                self.logical_circuit.x(qubit.logical_qubit)
            case "+":
                circuit.h(qreg_psi[0])
                self.logical_circuit.h(qubit.logical_qubit)
            case "-":
                circuit.x(qreg_psi[0])
                self.logical_circuit.x(qubit.logical_qubit)
                circuit.h(qreg_psi[0])
                self.logical_circuit.h(qubit.logical_qubit)

    def reset(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)

        for q in qubits_index:
            qubit = self.qubits[q]
            self.physical_circuit.reset(qubit.physical_qubits)
            self.logical_circuit.reset(qubit.logical_qubit)

    def encode(self, qubits_index=None, type='universal'):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            match type:
                case 'universal':
                    encode_qubit(self.physical_circuit, self.qubits[q])
                case '-':
                    encode_qubit_minus(self.physical_circuit, self.qubits[q])
                case '0':
                    encode_qubit_zero(self.physical_circuit, self.qubits[q])
        
        self.physical_circuit.barrier()

    def random_error(self, qubits_index=None, physical_qubit=None):

        qubits_index = self.parse_index(qubits_index)

        u = UnitaryGate(random_unitary(2), label='E')

        for qi in qubits_index:
            q = self.qubits[qi]
            error_qubit_index = random.randint(0, len(q.physical_qubits)-1) if physical_qubit is None else physical_qubit
            self.physical_circuit.append(u,[q.physical_qubits[error_qubit_index]])

        self.physical_circuit.barrier()

    def spot_syndrome(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        self.show_ancillas = True
        for q in qubits_index:
            self.physical_circuit.add_register(self.qubits[q].ancillas)
            spot_syndrome_qubit(self.physical_circuit, self.qubits[q])

    def measure_syndrome(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        
        for q in qubits_index:
            self.physical_circuit.add_register(self.qubits[q].anc_measures)
            self.physical_circuit.measure(self.qubits[q].ancillas, self.qubits[q].anc_measures[::-1])
    
    def measure(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            measure_qubit(self.physical_circuit, self.qubits[q], basis)

    def measure_all(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        for q in qubits_index:
            # basis: base logica
            
            if self.show_ancillas:
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

    def measure_operator(self, qubits_index=None, operator=None):
        
        if operator in ['Z', 'X']:
            self.measure(qubits_index, basis=operator)
            return

        if len(operator) != 5:
            raise ValueError("Invalid operator")
        
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            measure_operator_qubit(self.physical_circuit, self.qubits[q], operator)
        

    def delay(self, dt, qubits_index=None, unit='dt'):

        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            delay_on_qubit(self.physical_circuit, self.qubits[q], dt, unit)
            self.logical_circuit.append(Delay(dt, unit=unit), self.qubits[q].logical_qubit)
        
        self.physical_circuit.barrier()

    def correct(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            correct_qubit(self.physical_circuit, self.qubits[q], self.syndromes)

    def x(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            x_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.x(self.qubits[q].logical_qubit)

    def z(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            z_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.z(self.qubits[q].logical_qubit)
    
    def h(self, qubits_index=None, swap=True):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            h_on_qubit(self.physical_circuit, self.qubits[q], swap=swap)
            self.logical_circuit.h(self.qubits[q].logical_qubit)

        self.physical_circuit.barrier()

    def cx(self, control_index, target_index, options=None):

        control_qubit = self.qubits[control_index]
        target_qubit = self.qubits[target_index]

        cx1_on_qubits(self.physical_circuit, control_qubit, target_qubit)

        if options == "FT":

            check_matrix = [
                [1, 0, 1, 0, 0, 0, 0, 1, 0, 1,  1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0,  1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 1, 1, 0, 0, 0, 1,  1, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1, 1, 0,  0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 0,  1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0,  1, 0, 1, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 1, 1, 1, 1,  0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            ]
            
            alt_spot_syndrome(self.physical_circuit, check_matrix, [control_qubit, target_qubit])
            alt_correct(self.physical_circuit, check_matrix, [control_qubit, target_qubit])

        cx2_on_qubits(self.physical_circuit, control_qubit, target_qubit)
    
        self.logical_circuit.cx(control_qubit.logical_qubit, target_qubit.logical_qubit)
    
    def cz(self, control_index, target_index, options=None):

        control_qubit = self.qubits[control_index]
        target_qubit = self.qubits[target_index]
        
        cz1_on_qubits(self.physical_circuit, control_qubit, target_qubit)

        if options == "FT":

            check_matrix = [
                [1, 0, 1, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 0, 1, 0, 0, 1, 0, 1],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0,  1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 0, 0, 0,  1, 0, 0, 1, 1, 1, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 1, 0, 1,  1, 0, 1, 0, 0, 1, 0, 0, 1, 1],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 0,  0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 1, 0, 0,  1, 0, 0, 0, 1, 1, 1, 0, 0, 1]
            ]

            alt_spot_syndrome(self.physical_circuit, check_matrix, [control_qubit, target_qubit])
            alt_correct(self.physical_circuit, check_matrix, [control_qubit, target_qubit])

        cz2_on_qubits(self.physical_circuit, control_qubit, target_qubit)
    
        self.logical_circuit.cz(control_qubit.logical_qubit, target_qubit.logical_qubit)
    

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
        # 5 qubits fisicos por qubit logico
        self.logical_qubit = QuantumRegister(1, name) # representacion del qubit logico

        self.physical_qubits = QuantumRegister(5, name)
        self.ancillas = QuantumRegister(4, name + '_anc')
        self.qb_state = QuantumRegister(1, name + '_state')
        self.extra_ancillas = []

        self.qb_measures = ClassicalRegister(5, name + '_meas')
        self.anc_measures = ClassicalRegister(4, name + '_anc_meas')
        self.qb_measure = ClassicalRegister(1, name + '_state_meas')        
        self.all_measures = ClassicalRegister(5+4, name + '_all_meas')
        self.extra_measures = []

        self.name = name

    def add_extra_ancilla(self):
        q = QuantumRegister(1, self.name + '_extra' + str(len(self.extra_ancillas)))
        self.extra_ancillas.append(q)
        return q
        
    def add_extra_measure(self):
        c = ClassicalRegister(1, self.name + '_extra_meas' + str(len(self.extra_ancillas)))
        self.extra_measures.append(c)
        return c
    

def encode_qubit(circuit, qubit):

    qreg_psi = qubit.physical_qubits

    circuit.z(qreg_psi[0])
    circuit.h(qreg_psi[2])
    circuit.h(qreg_psi[3])

    circuit.sdg(qreg_psi[0])
    circuit.cx(qreg_psi[2], qreg_psi[4])

    circuit.cx(qreg_psi[3], qreg_psi[1])

    circuit.h(qreg_psi[1])
    circuit.cx(qreg_psi[3], qreg_psi[4])

    circuit.cx(qreg_psi[1], qreg_psi[0])
    circuit.sdg(qreg_psi[2])
    circuit.s(qreg_psi[3])
    circuit.sdg(qreg_psi[4])

    circuit.s(qreg_psi[0])
    circuit.s(qreg_psi[1])
    circuit.z(qreg_psi[2])

    circuit.cx(qreg_psi[4], qreg_psi[0])

    circuit.h(qreg_psi[4])

    circuit.cx(qreg_psi[4], qreg_psi[1])

def encode_qubit_minus(circuit, qubit):
    qreg_psi = qubit.physical_qubits

    circuit.h(qreg_psi)
    circuit.cz(qreg_psi[0], qreg_psi[1])
    circuit.cz(qreg_psi[2], qreg_psi[3])
    circuit.cz(qreg_psi[1], qreg_psi[2])
    circuit.cz(qreg_psi[3], qreg_psi[4])
    circuit.cz(qreg_psi[4], qreg_psi[0])

def encode_qubit_zero(circuit, qubit):

    qreg_psi = qubit.physical_qubits
    
    circuit.h(qreg_psi[1])
    circuit.h(qreg_psi[4])

    circuit.cx(qreg_psi[4], qreg_psi[0])
    circuit.cx(qreg_psi[1], qreg_psi[3])
    circuit.cx(qreg_psi[0], qreg_psi[2])

    circuit.h(qreg_psi[2])
    circuit.h(qreg_psi[3])

    circuit.cx(qreg_psi[3], qreg_psi[4])
    circuit.cx(qreg_psi[1], qreg_psi[3])
    circuit.cx(qreg_psi[2], qreg_psi[3])

    circuit.z(qreg_psi[2])
    circuit.z(qreg_psi[4])

    # ---------------------------

    # circuit.h(qreg_psi[0])
    # circuit.h(qreg_psi[3])

    # circuit.cx(qreg_psi[3], qreg_psi[4])
    # circuit.cx(qreg_psi[3], qreg_psi[1])
    # circuit.cx(qreg_psi[0], qreg_psi[4])
    # circuit.cx(qreg_psi[0], qreg_psi[2])

    # circuit.h(qreg_psi[2])
    # circuit.h(qreg_psi[3])

    # circuit.cx(qreg_psi[3], qreg_psi[4])
    # circuit.cx(qreg_psi[2], qreg_psi[3])

    # circuit.z(qreg_psi[0])
    # circuit.z(qreg_psi[3])

def spot_syndrome_qubit(circuit, qubit):
    
    qreg_psi = qubit.physical_qubits
    qreg_q = qubit.ancillas

    # implementacion estandar para estabilizadores
        
    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[2])
    circuit.h(qreg_q[3])

    circuit.barrier()

    # XZZXI
    circuit.cx(qreg_q[0], qreg_psi[0])
    circuit.cz(qreg_q[0], qreg_psi[1])
    circuit.cz(qreg_q[0], qreg_psi[2])
    circuit.cx(qreg_q[0], qreg_psi[3])

    circuit.barrier()

    # IXZZX
    circuit.cx(qreg_q[1], qreg_psi[1])
    circuit.cz(qreg_q[1], qreg_psi[2])
    circuit.cz(qreg_q[1], qreg_psi[3])
    circuit.cx(qreg_q[1], qreg_psi[4])

    circuit.barrier()

    # XIXZZ
    circuit.cx(qreg_q[2], qreg_psi[0])
    circuit.cx(qreg_q[2], qreg_psi[2])
    circuit.cz(qreg_q[2], qreg_psi[3])
    circuit.cz(qreg_q[2], qreg_psi[4])

    circuit.barrier()

    # ZXIXZ
    circuit.cz(qreg_q[3], qreg_psi[0])
    circuit.cx(qreg_q[3], qreg_psi[1])
    circuit.cx(qreg_q[3], qreg_psi[3])
    circuit.cz(qreg_q[3], qreg_psi[4])

    circuit.barrier()

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[2])
    circuit.h(qreg_q[3])

    circuit.barrier()    

def cnx(circuit, qreg_q, psi, ctrl):
    qs = []
    for q in qreg_q:
        qs.append(q)
    qs.append(psi)
    circuit.append(XGate().control(len(qreg_q), ctrl_state=ctrl), qs)

def cny(circuit, qreg_q, psi, ctrl):
    qs = []
    for q in qreg_q:
        qs.append(q)
    qs.append(psi)
    circuit.append(YGate().control(len(qreg_q), ctrl_state=ctrl), qs)

def cnz(circuit, qreg_q, psi, ctrl):
    qs = []
    for q in qreg_q:
        qs.append(q)
    qs.append(psi)
    circuit.append(ZGate().control(len(qreg_q), ctrl_state=ctrl), qs)

def correct_qubit(circuit, qubit, syndromes):
    
    qreg_psi = qubit.physical_qubits
    qreg_q = qubit.ancillas

    i = 0
    for s in syndromes:
        
        if syndromes[s] == "None":
            continue

        if i < 5:       # errores X
            cnx(circuit, qreg_q[::-1], qreg_psi[i%5], s)
        elif i < 10:    # errores Z
            cnz(circuit, qreg_q[::-1], qreg_psi[i%5], s)
        else:           # errores Y
            cny(circuit, qreg_q[::-1], qreg_psi[i%5], s)
        i += 1

    circuit.barrier()

def measure_qubit(circuit, qubit, basis):
    # basis: base logica

    creg = qubit.qb_measure
    qreg = qubit.qb_state
    qregs = qubit.physical_qubits

    circuit.add_register(qreg)
    circuit.add_register(creg)

    circuit.barrier()

    if basis == 'Z':    # medir 0 o 1 logico
        for i in range(5):
            circuit.cx(qregs[i], qreg)
        # 'anc' cambia a |1> si hay cantidad impar de 1s (1 logico)

    if basis == 'X':    # medir + o - logico
        circuit.h(qreg) # 'anc' = |+>
        for i in range(5):
            circuit.cx(qreg, qregs[i])
        circuit.h(qreg) # volver a base Z

    circuit.measure(qreg, creg) # medir 'anc'

def measure_operator_qubit(circuit, qubit, operator):

    qreg = qubit.add_extra_ancilla()
    creg = qubit.add_extra_measure()
    qregs = qubit.physical_qubits

    circuit.add_register(qreg)
    circuit.add_register(creg)

    circuit.barrier()

    circuit.h(qreg) # 'anc' = |+>

    for i in range(5):
        match operator[i]:
            case 'X':
                circuit.cx(qreg, qregs[i])
            case 'Z':
                circuit.cz(qreg, qregs[i])
            case 'Y':
                circuit.cy(qreg, qregs[i])
            case 'I':
                pass

    circuit.h(qreg) # volver a base Z

    circuit.measure(qreg, creg) # medir extra_ancilla


def delay_on_qubit(circuit, qubit, dt, unit):
    for q in qubit.physical_qubits:
        circuit.append(Delay(dt, unit=unit), [q])

def x_on_qubit(circuit, qubit):
    circuit.x(qubit.physical_qubits)

def z_on_qubit(circuit, qubit):
    circuit.z(qubit.physical_qubits)

def h_on_qubit(circuit, qubit, swap=True):
    qbs = qubit.physical_qubits
    circuit.h(qbs)
    if swap:
        circuit.swap(qbs[0], qbs[3])
        circuit.swap(qbs[0], qbs[4])
        circuit.swap(qbs[0], qbs[1])

def cx_on_qubits(circuit, control, target, correction_step = None):

    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.h(qreg[0])
        circuit.s(qreg[0])
        circuit.y(qreg[2])
        circuit.h(qreg[4])
        circuit.s(qreg[4])

    circuit.barrier()

    # first part
    circuit.cx(control_reg[0], target_reg[0])
    circuit.cx(control_reg[2], target_reg[2])
    circuit.cx(control_reg[4], target_reg[4])


    circuit.barrier()

    # second first part
    circuit.cx(control_reg[0], target_reg[4])
    circuit.cx(control_reg[2], target_reg[0])
    circuit.cx(control_reg[4], target_reg[2])

    circuit.barrier()

    # no correction step

    # second part
    circuit.cx(control_reg[0], target_reg[2])
    circuit.cx(control_reg[2], target_reg[4])
    circuit.cx(control_reg[4], target_reg[0])

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.sdg(qreg[0])
        circuit.h(qreg[0])
        circuit.y(qreg[2])
        circuit.sdg(qreg[4])
        circuit.h(qreg[4])
    
    circuit.barrier()

def cx1_on_qubits(circuit, control, target):

    # only first part of the circuit

    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.h(qreg[0])
        circuit.s(qreg[0])
        circuit.y(qreg[2])
        circuit.h(qreg[4])
        circuit.s(qreg[4])

    circuit.barrier()

    # first part
    circuit.cx(control_reg[0], target_reg[0])
    circuit.cx(control_reg[2], target_reg[2])
    circuit.cx(control_reg[4], target_reg[4])


    circuit.barrier()

    # second first part
    circuit.cx(control_reg[0], target_reg[4])
    circuit.cx(control_reg[2], target_reg[0])
    circuit.cx(control_reg[4], target_reg[2])

    circuit.barrier()

def cx2_on_qubits(circuit, control, target):

    # only second part of the circuit

    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    circuit.barrier()

    circuit.cx(control_reg[0], target_reg[2])
    circuit.cx(control_reg[2], target_reg[4])
    circuit.cx(control_reg[4], target_reg[0])

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.sdg(qreg[0])
        circuit.h(qreg[0])
        circuit.y(qreg[2])
        circuit.sdg(qreg[4])
        circuit.h(qreg[4])
    
    circuit.barrier()

def cz1_on_qubits(circuit, control, target):

    # only first part of the circuit

    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.h(qreg[0])
        circuit.s(qreg[0])
        circuit.y(qreg[2])
        circuit.h(qreg[4])
        circuit.s(qreg[4])

    circuit.barrier()

    # first part
    circuit.cz(control_reg[0], target_reg[0])
    circuit.cz(control_reg[2], target_reg[2])
    circuit.cz(control_reg[4], target_reg[4])


    circuit.barrier()

    # second first part
    circuit.cz(control_reg[0], target_reg[4])
    circuit.cz(control_reg[2], target_reg[0])
    circuit.cz(control_reg[4], target_reg[2])

    circuit.barrier()

def cz2_on_qubits(circuit, control, target):

    # only second part of the circuit

    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    circuit.barrier()

    circuit.cz(control_reg[0], target_reg[2])
    circuit.cz(control_reg[2], target_reg[4])
    circuit.cz(control_reg[4], target_reg[0])

    circuit.barrier()

    for qreg in [control_reg, target_reg]:
        circuit.sdg(qreg[0])
        circuit.h(qreg[0])
        circuit.y(qreg[2])
        circuit.sdg(qreg[4])
        circuit.h(qreg[4])
    
    circuit.barrier()


def alt_spot_syndrome(circuit, check_matrix, qubits):

    qreg_psi = []
    qreg_q = []

    for q in qubits:
        for i in q.physical_qubits:
            qreg_psi.append(i)
        for i in q.ancillas:
            qreg_q.append(i)
    
    # implementacion estandar para estabilizadores

    circuit.barrier()
    circuit.h(qreg_q)
    circuit.barrier()

    for f in range(8):
        for c in range(10):
            if check_matrix[f][c] == 1 and check_matrix[f][c+10] == 1:
                circuit.cy(qreg_q[f], qreg_psi[c])
            if check_matrix[f][c] == 1 and check_matrix[f][c+10] == 0:
                circuit.cx(qreg_q[f], qreg_psi[c])
            if check_matrix[f][c] == 0 and check_matrix[f][c+10] == 1:
                circuit.cz(qreg_q[f], qreg_psi[c])
        circuit.barrier()

    circuit.h(qreg_q)
    circuit.barrier()
                    
def alt_correct(circuit, check_matrix, qubits):

    qreg_psi = []
    qreg_q = []

    for q in qubits:
        for i in q.physical_qubits:
            qreg_psi.append(i)
        for i in q.ancillas:
            qreg_q.append(i)

    syndromes = {}

    syndromes['11111111'] = "None"

    for c in range(10):

        syn = ''.join([str((check_matrix[r][c])%2) for r in range(8)])
        # syndromes[syn] = "Z" + str(c+1)
        syndromes[syn] = ['Z', c+1]

        syn = ''.join([str((check_matrix[r][c+10])%2) for r in range(8)])
        # syndromes[syn] = "X" + str(c+1)
        syndromes[syn] = ['X', c+1]

        syn = ''.join([str((check_matrix[r][c] + check_matrix[r][c+10])%2) for r in range(8)])
        # syndromes[syn] = "Y" + str(c+1)
        syndromes[syn] = ['Y', c+1]

    for s in syndromes:
        
        if syndromes[s] == "None":
            continue

        match syndromes[s][0]:       # errores X
            case 'X':
                cnx(circuit, qreg_q[::-1], qreg_psi[syndromes[s][1]-1], s)
            case 'Z':
                cnz(circuit, qreg_q[::-1], qreg_psi[syndromes[s][1]-1], s)
            case 'Y':
                cny(circuit, qreg_q[::-1], qreg_psi[syndromes[s][1]-1], s)
    
    circuit.barrier()


            
