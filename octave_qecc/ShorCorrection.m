function x = ShorCorrection(x)


  % First we see how many qubits do we have and then append qubits to perform error correction:

  % - x (vector) is a vector representing the state of the qubits
  %   Recall that the magnitude of |x1x2...xn> in x is in the position
  %   x1x2...xn in binary in x (if we start counting from zero)
  % - qubit (int) is the qubit where the X gate is applied

  % If there is some errors we return x unchanged with a warning.

  XGate = [0, 1; 1, 0];
  N = length(x);
  qubit_count = floor(log2(N));

  if N ~= 2^qubit_count
    warning("The state vector must be a vector whose length is an integer power of two");
    return;
  endif

  logical_qubit_count = floor(qubit_count/9);

  if logical_qubit_count ~= qubit_count/9
    warning("Using the steane code the number of physical qubits must be a multiple of 9");
    return;
  endif


  % Error correction:
  for i = 1:logical_qubit_count

    q = (i-1)*9;

    x = CNOT(x, q + 1, q + 3);
    x = CNOT(x, q + 1, q + 2);
    x = MCG(x, XGate, q + 1, q + 2:q + 3, [1, 1]);

    x = CNOT(x, q + 4, q + 6);
    x = CNOT(x, q + 4, q + 5);
    x = MCG(x, XGate, q + 4, q + 5:q + 6, [1, 1]);

    x = CNOT(x, q + 7, q + 9);
    x = CNOT(x, q + 7, q + 8);
    x = MCG(x, XGate, q + 7, q + 8:q + 9, [1, 1]);

    x = H(x, q + 1);
    x = H(x, q + 4);
    x = H(x, q + 7);

    x = CNOT(x, q + 1, q + 7);
    x = CNOT(x, q + 1, q + 4);
    x = MCG(x, XGate, q + 1, [q + 7, q + 4], [1, 1]);


  endfor



endfunction
