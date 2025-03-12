# QECC-TFC
This Python library provides tools for encoding, decoding, correcting, measuring, and analyzing quantum error correction codes (QECCs) using Qiskit. It offers a unified interface to work with different quantum codes, including Shor, Steane, and the Five-Qubit code, while preserving user interaction with Qiskit's quantum circuit structure.

## Features
- *Encapsulation of QECCs* — Define logical and physical qubit relationships.
- *Modular and Extensible* — Users can define and implement new quantum error correction codes.
- *Parallel Circuit Management* — Manage logical and physical quantum circuits simultaneously operating with logical gates.
- *Flexible Correction Methods* — Supports different error correction approaches (e.g., decoding, syndrome-based correction, mid-circuit measurements).
- *Visualization Tools* — Draw logical and physical quantum circuits for easy debugging and analysis.
- *Error Simulation* — Apply arbitrary unitary errors for benchmarking code performance.

## Repo Structure
```
qecc/
│── library/        # Core implementation of QECC classes and tools
│    ├── encoded_circuit.py  # Abstract base class
│    ├── shor_code.py        # Shor Code implementation
│    ├── steane_code.py      # Steane Code implementation
│    ├── five_qubit_code.py  # Five-Qubit Code implementation
│    ├── __init__.py         # Library module initialization
│
│── experiments/    # Scripts and notebooks for testing QECCs on current hardware
│── octave_qecc/    # Numerical implementation of QECCs, logical gates and noise modelling
│── functions/    # Utilities for simulating, plotting and presenting results
│── README.md       # Project documentation
│── requirements.txt # Required dependencies
```

## Installation

To install the library, clone the repository and install dependencies:
```
git clone https://github.com/mateo-st/qecc.git
cd qecc
pip install -r requirements.txt
```

## Usage
### Importing the Library
`from qecc.library import ShorCode, SteaneCode, FiveQubitCode`

### Encoding, Operating and Measuring
```
qcc = ShorCode(n=1)  # Initialize a Shor code with 1 logical qubit
qcc.append_init('H')  # Prepare the initial state to |+>
qcc.encode()  # Encode logical |+>
qcc.append_unitary_error('X', 3)  # Apply an X error on fourth physical qubit.
qcc.x()  # Apply a logical X gate
qcc.correct(correction_method='syndrome')  # Correct the error
qcc.measure_all()  # Measure all qubits
qcc.draw_both()  # Visualize the logical and physical circuits
```

## Class Structure

### EncodedCircuit (Abstract Base Class)

- Defines common attributes and methods for all QECCs.
- Provides visualization and error modeling tools.
- Not instantiated directly; serves as a blueprint for specific codes.

### Implemented Quantum Codes

#### ShorCode
9-qubit code for bit-flip and phase-flip error correction.

#### SteaneCode
7-qubit CSS code providing single-qubit error correction.

#### FiveQubitCode
5-qubit code offering full single-qubit error correction with minimal qubits.

## License

This project is licensed under the MIT License. See LICENSE for details.

## Contributing

Contributions are welcome! Please submit issues or pull requests to improve the library.

## Contact

For questions or suggestions, open an issue or reach out to the repository maintainer.
