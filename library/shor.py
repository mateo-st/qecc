from .encoded_circuit import EncodedCircuit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library.standard_gates import XGate, ZGate, YGate
import warnings

class ShorCodeCircuit(EncodedCircuit):
    '''
        A class representing a Shor code quantum error-correcting circuit.

        This class implements the [[9,1,3]] Shor code, which encodes a single logical qubit 
        into nine physical qubits. It provides methods to encode, apply quantum gates, correct 
        errors, and manage interactions between the logical and physical layers. The class inherits 
        from the `EncodedCircuit` class, adding further functionality such as error injection and 
        circuit measurement.

        Attributes:
            logical_qubit_count (int): The number of logical qubits in the circuit.
            physical_qubit_count (int): The number of physical qubits (excluding ancillas for error correction and measurement).
            encode_applied (bool): Indicates whether the encoding step has been applied.
            logical_qubit_register (QuantumRegister): Register of logical qubits.
            logical_bit_register (ClassicalRegister): Classical register to store logical measurement results.
            logical_quantum_circuit (QuantumCircuit): Logical layer of the quantum circuit.
            physical_qubit_register (QuantumRegister): Register of physical qubits.
            physical_ancilla_qubit_register (QuantumRegister): Register of ancilla qubits used for error correction.
            physical_measurement_qubit_register (QuantumRegister): Register of qubits used for measurements.
            physical_bit_register (ClassicalRegister): Classical register to store physical measurement results.
            physical_quantum_circuit (QuantumCircuit): Physical layer of the quantum circuit.

        Methods:
            get_physical_qubits_from_logical(logical_qubits: list | int) -> list[int]:
                Maps logical qubits to their corresponding physical qubits.

            encode(re_encode: bool = False) -> None:
                Encodes each logical qubit using the Shor code. If encoding is already applied, a 
                warning is issued unless `re_encode` is set to True.

            correct() -> None:
                Applies quantum error correction to the physical circuit.

            x(logical_qubits: list | int) -> None:
                Applies the Pauli-X gate to the specified logical and corresponding physical qubits.

            y(logical_qubits: list | int) -> None:
                Applies the Pauli-Y gate to the specified logical and corresponding physical qubits.

            z(logical_qubits: list | int) -> None:
                Applies the Pauli-Z gate to the specified logical and corresponding physical qubits.

            h(logical_qubits: list | int) -> None:
                Applies the Hadamard gate to the specified logical and corresponding physical qubits.

            cx(control: list | int, target: list | int) -> None:
                Applies a CNOT gate between the specified control and target logical qubits in both the 
                logical and physical quantum circuits.

            measure_all() -> None:
                Measures all logical and physical qubits, storing the results in their respective classical registers.

            append(U, logical_qubits: list | int) -> None:
                Appends a quantum gate to the logical and physical circuits unless encoding has been applied.
                If encoding is applied, a warning is issued.

            append_unitary_error(E, physical_qubits: list | int) -> None:
                Appends an error gate to the specified physical qubits in the physical circuit.

            barrier(num_qubits: int = None, label: str = None) -> None:
                Appends a barrier to the logical and physical circuits for visualization and grouping.

            draw_logical_circuit(output: str = 'mpl') -> None:
                Draws the logical quantum circuit using the specified output format.

            draw_physical_circuit(output: str = 'mpl') -> None:
                Draws the physical quantum circuit using the specified output format.
        '''

    def __init__(self, logical_qubit_count):
        # For Shor's code, 9 physical qubits are needed for each logical qubit
        super().__init__(logical_qubit_count, physical_qubits_per_logical=9)
        self.physical_ancilla_qubit_register = QuantumRegister(8*self.logical_qubit_count, name = 'ancilla_qubits')
        self.physical_measurement_qubit_register = QuantumRegister(self.logical_qubit_count, name = 'measure_register')
        self.physical_quantum_circuit = QuantumCircuit(self.physical_qubit_register, name = 'physical_circuit') # OVERWRITE
        # self.logical_quantum_circuit = QuantumCircuit(logical_qubit_count, name = 'logical_circuit')  # Initialize logical quantum circuit
        # self.physical_quantum_circuit = QuantumCircuit(logical_qubit_count * 9, name = 'physical_circuit')  # Initialize physical quantum circuit


    def get_physical_qubits_from_logical(self, logical_qubits: list | int):
        '''
        Maps logical qubits to their corresponding physical qubits in the Steane code.

        Parameters:
            logical_qubits (list[int] | int): A logical qubit or list of logical qubits to map.

        Returns:
            list[int]: The list of physical qubit indices representing the given logical qubits.
        '''
        physical_qubits = []  # Initialize
        
        if isinstance(logical_qubits, int):
            if logical_qubits < 0 or logical_qubits >= self.logical_qubit_count:
                raise ValueError("Invalid logical qubit index.")

            # For Shor's code, each logical qubit maps to 9 physical qubits
            start_index = logical_qubits * self.physical_qubits_per_logical
            physical_qubits = list(range(start_index, start_index + 9))  # E.g.: Logical Qubit is 0, Physical Qubits are 0-8

        elif isinstance(logical_qubits, list):
            for logical_qubit in logical_qubits:
                if logical_qubit < 0 or logical_qubit >= self.logical_qubit_count:
                    raise ValueError(f"Invalid logical qubit index: {logical_qubit}")
                start_index = logical_qubit * self.physical_qubits_per_logical
                physical_qubits.extend(list(range(start_index, start_index + 9)))

        return physical_qubits


    def encode(self, re_encode = False, initial_state = None):
        '''
        Encodes each logical qubit using the Steane code.

        Parameters:
            re_encode (bool): If `True`, forces re-encoding even if it was previously applied. Default is `False`.

        Returns:
            None

        Side Effects:
            - Sets `self.encode_applied` to True if encoding is performed.
            - Issues a UserWarning if encoding is skipped due to being already applied and `re_encode` is `False`.
        '''
        if not self.encode_applied:
            for logical_qubit in range(self.logical_qubit_count):
                current_physical_qubits = self.get_physical_qubits_from_logical(logical_qubit)
                # Initial encoding block for phase-flips
                if initial_state == '0':
                    pass
                elif initial_state == '1':
                    self.physical_quantum_circuit.h(current_physical_qubits[0])
                    self.physical_quantum_circuit.h(current_physical_qubits[3])
                    self.physical_quantum_circuit.h(current_physical_qubits[6])

                else:
                    self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[3])
                    self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[6])

                self.physical_quantum_circuit.h(current_physical_qubits[0])
                self.physical_quantum_circuit.h(current_physical_qubits[3])
                self.physical_quantum_circuit.h(current_physical_qubits[6])
                # Next encoding block for bit-flips
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[2])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[4])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[5])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[7])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[8])
                self.encode_applied = True
        else:
            warning_text = "\r\nWARNING! Encoder has already been applied."
            warnings.warn(warning_text, category=UserWarning)


    def x(self, logical_qubits: list | int):
        '''
        Applies the Pauli-X gate to specified logical qubits in both the logical and physical circuits.

        Parameters:
            logical_qubits (list[int] | int): Logical qubit(s) where the X-gate will be applied.

        Returns:
            None
        '''
        # Logical circuit
        self.logical_quantum_circuit.x(logical_qubits)

        if self.encode_applied:
            # Physical circuit: Logical X is equivalent to transversal Z on all physical qubits belonging to the logical qubit
            physical_qubits_to_use = self.get_physical_qubits_from_logical(logical_qubits)
            self.physical_quantum_circuit.z(physical_qubits_to_use)

        else:
            if isinstance(logical_qubits, int):
                logical_qubits = [logical_qubits]
            self.physical_quantum_circuit.x([self.physical_qubits_per_logical * i for i in logical_qubits])


    def y(self, logical_qubits: list | int):
        '''
        Applies the Pauli-Y gate to specified logical qubits in both the logical and physical circuits.

        Parameters:
            logical_qubits (list[int] | int): Logical qubit(s) where the Y-gate will be applied.

        Returns:
            None
        '''
        pass


    def z(self, logical_qubits: list | int):
        '''
        Applies the Pauli-Z gate to specified logical qubits in both the logical and physical circuits.

        Parameters:
            logical_qubits (list[int] | int): Logical qubit(s) where the Z-gate will be applied.

        Returns:
            None
        '''
        
        # Logical circuit
        self.logical_quantum_circuit.z(logical_qubits)

        if self.encode_applied:
            # Physical circuit: Logical X is equivalent to transversal Z on all physical qubits belonging to the logical qubit
            physical_qubits_to_use = self.get_physical_qubits_from_logical(logical_qubits)
            self.physical_quantum_circuit.x(physical_qubits_to_use)
            
        else:
            if isinstance(logical_qubits, int):
                logical_qubits = [logical_qubits]
            self.physical_quantum_circuit.z([self.physical_qubits_per_logical * i for i in logical_qubits])


    def h(self, logical_qubits: list | int):
        '''
        Applies the Hadamard gate H to specified logical qubits in both the logical and physical circuits.

        Parameters:
            logical_qubits (list[int] | int): Logical qubit(s) where the H-gate will be applied.

        Returns:
            None
        '''
        pass


    def cx(self, control: list | int, target: list | int):
        '''
        Applies a CNOT (CX) gate between control and target logical qubits in both the logical and physical circuits.

        Parameters:
            control (list[int] | int): Logical qubit(s) acting as the control qubit(s).
            target (list[int] | int): Logical qubit(s) acting as the target qubit(s).

        Returns:
            None
        '''
        # Logical circuit
        self.logical_quantum_circuit.cx(control, target)

        if self.encode_applied:
            # Physical circuit: Logical CX is transversal
            control_physical_qubits = self.get_physical_qubits_from_logical(control)
            target_physical_qubits = self.get_physical_qubits_from_logical(target)
            for control_physical_qubit, target_physical_qubit in zip(control_physical_qubits, target_physical_qubits):
                self.physical_quantum_circuit.cx(control_physical_qubit, target_physical_qubit)

        else:
            if isinstance(control, int):
                control = [control]
            if isinstance(target, int):
                target = [target]
            for control_qubit, target_qubit in zip(control, target):
                control_physical_qubits = self.get_physical_qubits_from_logical(control_qubit)
                target_physical_qubits = self.get_physical_qubits_from_logical(target_qubit)
                for control_physical_qubit, target_physical_qubit in zip(control_physical_qubits, target_physical_qubits):
                    self.physical_quantum_circuit.cx(control_physical_qubit, target_physical_qubit)


    def correct(self, correction_method = 'stabilizers'):
        """Apply quantum error correction to a certain operation (placeholder)."""

        if correction_method == 'decoding': 
            
            for logical_qubit in range(self.logical_qubit_count):
                
                current_physical_qubits = self.get_physical_qubits_from_logical(logical_qubit)
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[2])
                self.physical_quantum_circuit.ccx(current_physical_qubits[1], current_physical_qubits[2], current_physical_qubits[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[4])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[5])
                self.physical_quantum_circuit.ccx(current_physical_qubits[4], current_physical_qubits[5], current_physical_qubits[3])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[7])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[8])
                self.physical_quantum_circuit.ccx(current_physical_qubits[7], current_physical_qubits[8], current_physical_qubits[6])
                self.physical_quantum_circuit.h(current_physical_qubits[0])
                self.physical_quantum_circuit.h(current_physical_qubits[3])
                self.physical_quantum_circuit.h(current_physical_qubits[6])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[3])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[6])
                self.physical_quantum_circuit.ccx(current_physical_qubits[3], current_physical_qubits[6], current_physical_qubits[0])


        elif correction_method == 'stabilizers':

            self.physical_quantum_circuit.add_register(self.physical_ancilla_qubit_register)
            
            for i in range(self.logical_qubit_count):
                
                current_physical_qubits = self.physical_qubit_register[9*i :9*i + 9]
            
                # Apply stabilizer measurements, X side of check-matrix
                self.physical_quantum_circuit.h(current_physical_qubits)
                self.physical_quantum_circuit.cx(current_physical_qubits[0], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[1], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[2], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[4], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[5], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[7], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[7], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[8], self.physical_ancilla_qubit_register[0])
                self.physical_quantum_circuit.cx(current_physical_qubits[8], self.physical_ancilla_qubit_register[1])
                self.physical_quantum_circuit.h(current_physical_qubits)
                
                # Apply stabilizer measurements, Z side of check-matrix
                self.physical_quantum_circuit.cx(current_physical_qubits[0], self.physical_ancilla_qubit_register[2])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], self.physical_ancilla_qubit_register[5])
                self.physical_quantum_circuit.cx(current_physical_qubits[1], self.physical_ancilla_qubit_register[3])
                self.physical_quantum_circuit.cx(current_physical_qubits[1], self.physical_ancilla_qubit_register[4])
                self.physical_quantum_circuit.cx(current_physical_qubits[2], self.physical_ancilla_qubit_register[2])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], self.physical_ancilla_qubit_register[3])
                self.physical_quantum_circuit.cx(current_physical_qubits[4], self.physical_ancilla_qubit_register[4])
                self.physical_quantum_circuit.cx(current_physical_qubits[5], self.physical_ancilla_qubit_register[5])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], self.physical_ancilla_qubit_register[6])
                self.physical_quantum_circuit.cx(current_physical_qubits[7], self.physical_ancilla_qubit_register[7])
                self.physical_quantum_circuit.cx(current_physical_qubits[8], self.physical_ancilla_qubit_register[6])
                self.physical_quantum_circuit.cx(current_physical_qubits[8], self.physical_ancilla_qubit_register[7])
                
                # CNOTs according to syndrome in ancilla qubits, Z errors
                print([self.physical_ancilla_qubit_register, current_physical_qubits[1]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00100100"),
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[0]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00010000"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[1]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00100000"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[2]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00010000"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[3]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00001000"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[4]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00000100"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[5]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00000010"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[6]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00000001"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[7]])
                self.physical_quantum_circuit.append(ZGate().control(8, ctrl_state="00000011"), 
                                                    [*self.physical_ancilla_qubit_register, current_physical_qubits[8]])
                
                # CNOTs according to syndrome in ancilla qubits, Y errors
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="10100100"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[0]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="01011000"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[1]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="10100000"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[2]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="01010000"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[3]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="01001000"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[4]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="10000100"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[5]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="11000010"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[6]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="11000001"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[7]])
                self.physical_quantum_circuit.append(YGate().control(8, ctrl_state="11000011"), 
                                                     [*self.physical_ancilla_qubit_register, current_physical_qubits[8]])
                
        
        elif correction_method == 'mid_circuit_measurements':
            pass
        
        else:
            raise ValueError("Invalid correction method.")


    def measure_all(self, correction_method = 'stabilizers', basis = 'Z'):
        '''
        Measures all qubits in both the logical and physical circuits.

        Parameters:
            None

        Returns:
            None
        '''
        self.logical_quantum_circuit.measure(self.logical_qubit_register, self.logical_bit_register)

        match basis:
            case 'all':
                # Redefine physical_bit_register
                self.physical_bit_register = ClassicalRegister(9*self.logical_qubit_count, name = 'all_physical_bits')
                self.physical_quantum_circuit.add_register(self.physical_bit_register)
                
                self.physical_quantum_circuit.measure(self.physical_qubit_register, self.physical_bit_register)

            case 'Z':
                self.physical_bit_register = ClassicalRegister(self.logical_qubit_count, name = 'physical_bits')
                self.physical_quantum_circuit.add_register(self.physical_bit_register)
                match correction_method:
                    case 'decoding_1':
                        for i in range(self.logical_qubit_count):
                            current_physical_qubits = self.get_physical_qubits_from_logical(i)
                            self.physical_quantum_circuit.measure(current_physical_qubits[0], self.physical_bit_register[i])
            
                    case 'stabilizers':
                        self.physical_quantum_circuit.add_register(self.physical_measurement_qubit_register)
                        for i in range(self.logical_qubit_count):
                            current_physical_qubits = self.get_physical_qubits_from_logical(i)
                            self.physical_quantum_circuit.h(self.physical_measurement_qubit_register[i])
                            for j in range(len(current_physical_qubits)):   
                                self.physical_quantum_circuit.cx(self.physical_measurement_qubit_register[i], self.physical_qubit_register[j])
                            self.physical_quantum_circuit.h(self.physical_measurement_qubit_register[i])
                        self.physical_quantum_circuit.measure(self.physical_measurement_qubit_register, self.physical_bit_register)  
                    
                    case _:
                        raise ValueError("Invalid correction method.")
            
            case 'X':
                self.physical_bit_register = ClassicalRegister(self.logical_qubit_count, name = 'physical_bits')
                self.physical_quantum_circuit.add_register(self.physical_bit_register)
                match correction_method:
                    case 'decoding_1':
                        for i in range(self.logical_qubit_count):
                            current_physical_qubits = self.get_physical_qubits_from_logical(i)
                            self.physical_quantum_circuit.h(current_physical_qubits[0])
                            self.physical_quantum_circuit.measure(current_physical_qubits[0], self.physical_bit_register[i])
            
                    case 'stabilizers':
                        self.physical_quantum_circuit.add_register(self.physical_measurement_qubit_register)
                        for i in range(self.logical_qubit_count):
                            current_physical_qubits = self.get_physical_qubits_from_logical(i)
                            for j in range(len(current_physical_qubits)):
                                self.physical_quantum_circuit.cx(self.physical_qubit_register[j], self.physical_measurement_qubit_register[i])
                        self.physical_quantum_circuit.measure(self.physical_measurement_qubit_register, self.physical_bit_register)  
                    
                    case _:
                        raise ValueError("Invalid correction method.")
                    
            case _:
                raise ValueError("Invalid basis.")
            
    def decode(self, re_encode = False):
        
        if self.encode_applied:
            for logical_qubit in range(self.logical_qubit_count):
                current_physical_qubits = self.get_physical_qubits_from_logical(logical_qubit)
                # Next encoding block for bit-flips
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[1])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[2])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[4])
                self.physical_quantum_circuit.cx(current_physical_qubits[3], current_physical_qubits[5])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[7])
                self.physical_quantum_circuit.cx(current_physical_qubits[6], current_physical_qubits[8])

                # correcting toffoli gates
                self.physical_quantum_circuit.ccx(current_physical_qubits[1], current_physical_qubits[2], current_physical_qubits[0])
                self.physical_quantum_circuit.ccx(current_physical_qubits[4], current_physical_qubits[5], current_physical_qubits[3])
                self.physical_quantum_circuit.ccx(current_physical_qubits[7], current_physical_qubits[8], current_physical_qubits[6])

                self.physical_quantum_circuit.h(current_physical_qubits[0])
                self.physical_quantum_circuit.h(current_physical_qubits[3])
                self.physical_quantum_circuit.h(current_physical_qubits[6])

                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[3])
                self.physical_quantum_circuit.cx(current_physical_qubits[0], current_physical_qubits[6])

                self.physical_quantum_circuit.ccx(current_physical_qubits[3], current_physical_qubits[6], current_physical_qubits[0])

                self.encode_applied = False # Reset the flag
             
        else:
            warning_text = "\r\nWARNING! Encoder was not applied."
            warnings.warn(warning_text, category=UserWarning)
        
    
    def measure_operator(self, operator):

        if len(operator) != 9:
            raise ValueError('The operator must have one element for each physical qubit.')
        
        circuit = self.physical_quantum_circuit

        for i in range(self.logical_qubit_count):
                
            qregs = self.physical_qubit_register[9*i :9*i + 9]           
            creg = ClassicalRegister(1)
            qreg = QuantumRegister(1)

            circuit.add_register(qreg)
            circuit.add_register(creg)

            # circuit.barrier()

            circuit.h(qreg) # 'anc' = |+>

            for i in range(9):
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

    def delay(self, dt, unit='dt'):

        circuit = self.physical_quantum_circuit

        for i in range(self.logical_qubit_count):
                
            qregs = self.physical_qubit_register[9*i :9*i + 9]

            for q in qregs:
                circuit.delay(dt, q, unit=unit)


