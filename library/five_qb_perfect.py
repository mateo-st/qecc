from math import pi
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.circuit.library.standard_gates import XGate, ZGate, YGate, RZGate
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import random_unitary
from qiskit.circuit import Delay
import random

class FiveQbPerfectCodeCircuit:
    """
    A class to represent a Five Qubit Perfect Code Circuit.
    Attributes
    ----------
    qubits : list
        A list to store the qubits.
    physical_circuit : QuantumCircuit
        The physical quantum circuit.
    logical_circuit : QuantumCircuit
        The logical quantum circuit.
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
    decode(qubits_index=None):
        Decodes the specified qubits.
    measure_syndrome(qubits_index=None):
        Post-decoding measurement of the syndrome of the specified qubits.
    measure(qubits_index=None, basis='Z'):
        Post-decoding measurement of the specified qubits in the given basis.
    logical_measure(qubits_index=None, basis='Z'):
        Measures the logical state of the specified qubits in the given basis.
    measure_all(qubits_index=None, basis='Z'):
        Measures all the physical qubits for the specified logical qubits in the given basis.
    correct(qubits_index=None):
        Corrects the errors in the specified qubits.
    delay(dt, qubits_index=None):
        Applies a delay to the specified qubits.
    x(qubits_index=None):
        Applies an X gate to the specified qubits.
    z(qubits_index=None):
        Applies a Z gate to the specified qubits.
    cx(control_index, target_index):
        Applies a controlled-X (CX) gate between the control and target qubits.
    draw(options=None):
        Draws the physical circuit.
    """



    def __init__(self, k):
        # k: cantidad de qubits logicos

        

        self.qubits = []
        for i in range(k):
            self.qubits.append(Qubit('q' + str(i)))
        
        self.physical_circuit = QuantumCircuit(*[q.physical_qubits for q in self.qubits],
                                            #    *[q.syn_qb_measures for q in self.qubits],
                                            #    *[q.qb_measure for q in self.qubits],
                                            #    *[q.qb_state for q in self.qubits],
                                            #    *[q.all_measures for q in self.qubits],
                                               )
        
        self.logical_circuit = QuantumCircuit(*[q.logical_qubit for q in self.qubits])


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
        qreg = qubit.physical_qubits

        match state:
            case "0":
                pass
            case "1":
                circuit.x(qreg[2])
                self.logical_circuit.x(qubit.logical_qubit)
            case "+":
                circuit.h(qreg[2])
                self.logical_circuit.h(qubit.logical_qubit)
            case "-":
                circuit.x(qreg[2])
                circuit.h(qreg[2])
                self.logical_circuit.x(qubit.logical_qubit)
                self.logical_circuit.h(qubit.logical_qubit)

    def reset(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)

        for q in qubits_index:
            qubit = self.qubits[q]
            self.physical_circuit.reset(qubit.physical_qubits)
            self.logical_circuit.reset(qubit.logical_qubit)

    def barrier(self):
        self.physical_circuit.barrier()
        self.logical_circuit.barrier()

    def encode(self, qubits_index=None, type='universal'):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            match type:
                case 'universal':
                    encode_qubit(self.physical_circuit, self.qubits[q])
                case '0':
                    encode_qubit_zero(self.physical_circuit, self.qubits[q])
                case '1':
                    encode_qubit_one(self.physical_circuit, self.qubits[q])

    def random_error(self, qubits_index=None, physical_qubit=None):

        self.physical_circuit.barrier()

        qubits_index = self.parse_index(qubits_index)

        u = UnitaryGate(random_unitary(2), label='E')

        for qi in qubits_index:
            q = self.qubits[qi]
            error_qubit_index = random.randint(0, len(q.physical_qubits)-1) if physical_qubit is None else physical_qubit
            self.physical_circuit.append(u,[q.physical_qubits[error_qubit_index]])

    def decode(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            decode_qubit(self.physical_circuit, self.qubits[q])

    def measure_syndrome(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            self.physical_circuit.add_register(self.qubits[q].syn_qb_measures)
            self.physical_circuit.measure([self.qubits[q].physical_qubits[i] for i in [0,1,3,4]], self.qubits[q].syn_qb_measures[::-1])

    def measure(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        circuit.barrier()

        for q in qubits_index:
            # basis: base logica
            circuit.add_register(self.qubits[q].qb_measure)
            creg = self.qubits[q].qb_measure
            qreg = self.qubits[q].physical_qubits[2]
            

            if basis == 'Z':    # medir 0 o 1 logico
                pass

            if basis == 'X':    # medir + o - logico
                circuit.h(qreg)

            circuit.measure(qreg, creg)

    def logical_measure(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        

        for q in qubits_index:
            
            creg = self.qubits[q].qb_measure
            qreg = self.qubits[q].qb_state
            qregs = self.qubits[q].physical_qubits

            circuit.add_register(qreg)
            circuit.add_register(creg)
        
            circuit.barrier()

            if basis == 'Z':    # medir 0 o 1 logico
                circuit.h(qreg)
                circuit.cx(qreg, qregs[0])
                circuit.cx(qreg, qregs[1])
                circuit.cx(qreg, qregs[2])
                circuit.h(qreg)

            if basis == 'X':    # medir + o - logico
                circuit.h(qreg)
                circuit.cz(qreg, qregs[0])
                circuit.cx(qreg, qregs[1])
                circuit.cx(qreg, qregs[2])
                circuit.cz(qreg, qregs[3])
                circuit.cz(qreg, qregs[4])
                circuit.h(qreg)

            circuit.measure(qreg, creg)

    def measure_all(self, qubits_index=None, basis='Z'):
        qubits_index = self.parse_index(qubits_index)

        circuit = self.physical_circuit

        circuit.barrier()

        for q in qubits_index:

            circuit.add_register(self.qubits[q].all_measures)

            # basis: base logica
            
            if basis == 'Z':    # medir 0 o 1 logico
                pass

            if basis == 'X':    # medir + o - logico
                circuit.h(self.qubits[q].physical_qubits)

            circuit.measure(self.qubits[q].physical_qubits,
                         self.qubits[q].all_measures)
        
    def measure_operator(self, qubits_index=None, operator=None):
        
        if operator in ['Z', 'X']:
            self.logical_measure(qubits_index, basis=operator)
            return

        if len(operator) != 5:
            raise ValueError("Invalid operator")
        
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            measure_operator_qubit(self.physical_circuit, self.qubits[q], operator)

    def correct(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            correct_qubit(self.physical_circuit, self.qubits[q]) # , self.syndromes) ?

    def delay(self, dt, qubits_index=None, unit='dt'):

        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            delay_on_qubit(self.physical_circuit, self.qubits[q], dt, unit)
            self.logical_circuit.append(Delay(dt, unit=unit), self.qubits[q].logical_qubit)
        
        self.physical_circuit.barrier()


    def x(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            x_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.x(self.qubits[q].logical_qubit)

    def z(self, qubits_index=None):
        qubits_index = self.parse_index(qubits_index)
        for q in qubits_index:
            z_on_qubit(self.physical_circuit, self.qubits[q])
            self.logical_circuit.x(self.qubits[q].logical_qubit)

    def cx(self, control_index, target_index):

        control_qubit = self.qubits[control_index]
        target_qubit = self.qubits[target_index]
        
        cx_on_qubits(self.physical_circuit, control_qubit, target_qubit)
        self.logical_circuit.cx(control_qubit.logical_qubit, target_qubit.logical_qubit)
    

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
        # n: qubits fisicos por qubit logico
        self.logical_qubit = QuantumRegister(1, name) # representacion del qubit logico

        self.physical_qubits = QuantumRegister(5, name)
        self.qb_state = QuantumRegister(1, name + '_state')
        self.extra_ancillas = []

        self.syn_qb_measures = ClassicalRegister(4, name + '_syn')
        self.qb_measure = ClassicalRegister(1, name + '_meas')
        self.all_measures = ClassicalRegister(5, name + '_all_meas')
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

    qreg_q = qubit.physical_qubits
    
    circuit.barrier()

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[3])

    circuit.append(ZGate().control(2, ctrl_state="11"), [qreg_q[1], qreg_q[3], qreg_q[2]])

    circuit.append(ZGate().control(2, ctrl_state="00"), [qreg_q[1], qreg_q[3], qreg_q[2]])

    circuit.cx(qreg_q[2], qreg_q[4])
    circuit.cx(qreg_q[0], qreg_q[2])
    circuit.cx(qreg_q[0], qreg_q[4])
    circuit.cx(qreg_q[3], qreg_q[2])
    circuit.cx(qreg_q[1], qreg_q[4])

    circuit.cz(qreg_q[3], qreg_q[4])


def encode_qubit_zero(circuit, qubit):

    qreg_q = qubit.physical_qubits
    
    circuit.barrier()

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[3])

    circuit.cx(qreg_q[0], qreg_q[2])
    circuit.cx(qreg_q[0], qreg_q[4])
    circuit.cx(qreg_q[3], qreg_q[2])
    circuit.cx(qreg_q[1], qreg_q[4])

    circuit.cz(qreg_q[3], qreg_q[4])

def encode_qubit_one(circuit, qubit):

    qreg_q = qubit.physical_qubits
    
    circuit.barrier()

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[3])

    circuit.cx(qreg_q[0], qreg_q[2])
    circuit.cx(qreg_q[0], qreg_q[4])
    circuit.cx(qreg_q[3], qreg_q[2])
    circuit.cx(qreg_q[1], qreg_q[4])

    circuit.cz(qreg_q[3], qreg_q[4])

    circuit.z(qreg_q[0])
    circuit.x(qreg_q[1])
    circuit.x(qreg_q[2])
    circuit.z(qreg_q[3])
    circuit.z(qreg_q[4])


def decode_qubit(circuit, qubit):
    
    qreg_q = qubit.physical_qubits

    circuit.barrier()

    circuit.cz(qreg_q[3], qreg_q[4])

    circuit.cx(qreg_q[1], qreg_q[4])
    circuit.cx(qreg_q[3], qreg_q[2])
    circuit.cx(qreg_q[0], qreg_q[4])
    circuit.cx(qreg_q[0], qreg_q[2])
    circuit.cx(qreg_q[2], qreg_q[4])

    circuit.append(ZGate().control(2, ctrl_state="00"), [qreg_q[1], qreg_q[3], qreg_q[2]])    

    circuit.append(ZGate().control(2, ctrl_state="11"), [qreg_q[1], qreg_q[3], qreg_q[2]])

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[3])


def correct_qubit(circuit, qubit):

    qreg_q = qubit.physical_qubits

    circuit.append(ZGate().control(4, ctrl_state="0001"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(ZGate().control(4, ctrl_state="0101"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(ZGate().control(4, ctrl_state="1010"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(ZGate().control(4, ctrl_state="1100"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])


    circuit.barrier()

    # ctrl = "0010"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    # ctrl = "0011"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    # ctrl = "0100"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    # ctrl = "1000"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    # circuit.barrier(qreg_q)

    ctrl="0110"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    ctrl="0111"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    ctrl="1001"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    ctrl="1011"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    ctrl="1110"
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(XGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(ZGate().control(4, ctrl_state=ctrl), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    circuit.barrier()

    # circuit.append(ZGate().control(4, ctrl_state="1101"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state="1101"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(YGate().control(4, ctrl_state="1101"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    circuit.barrier()

    # circuit.append(XGate().control(4, ctrl_state="1111"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    circuit.append(ZGate().control(4, ctrl_state="1111"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])
    # circuit.append(XGate().control(4, ctrl_state="1111"), [qreg_q[4], qreg_q[3], qreg_q[1], qreg_q[0], qreg_q[2]])

    circuit.barrier()

def x_on_qubit(circuit, qubit):
    qreg_q = qubit.physical_qubits
    circuit.z(qreg_q[0])
    circuit.x(qreg_q[1])
    circuit.x(qreg_q[2])
    circuit.z(qreg_q[3])
    circuit.z(qreg_q[4])

def z_on_qubit(circuit, qubit):
    qreg_q = qubit.physical_qubits
    circuit.x(qreg_q[0])
    circuit.x(qreg_q[1])
    circuit.x(qreg_q[2])

def cx_on_qubits(circuit, control, target):
    control_reg = control.physical_qubits
    target_reg = target.physical_qubits

    for i in range(5):
        circuit.cx(control_reg[i], target_reg[i])

def delay_on_qubit(circuit, qubit, dt, unit):
    for q in qubit.physical_qubits:
        circuit.append(Delay(dt, unit=unit), [q])

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

            