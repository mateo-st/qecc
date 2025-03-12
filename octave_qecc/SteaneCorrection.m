function x = SteaneCorrection(x)


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

  logical_qubit_count = floor(qubit_count/7);

  if logical_qubit_count ~= qubit_count/7
    warning("Using the steane code the number of physical qubits must be a multiple of 7");
    return;
  endif

  % Now we add six qubits in state |0> for each logical qubit
  for i = 1:6*logical_qubit_count
    x = kron(x, [1; 0]);
  endfor


  % Error correction:
  for i = 1:logical_qubit_count

    q = (i-1)*7;
    a = qubit_count + (i-1)*3;
    b = a + 3;

    x = CNOT(x, q + 1, a + 1); % Control, target
    x = CNOT(x, q + 3, a + 1);
    x = CNOT(x, q + 5, a + 1);
    x = CNOT(x, q + 7, a + 1);

    x = CNOT(x, q + 2, a + 2);
    x = CNOT(x, q + 3, a + 2);
    x = CNOT(x, q + 6, a + 2);
    x = CNOT(x, q + 7, a + 2);

    x = CNOT(x, q + 4, a + 3);
    x = CNOT(x, q + 5, a + 3);
    x = CNOT(x, q + 6, a + 3);
    x = CNOT(x, q + 7, a + 3);

    x = MCG(x, XGate, q + 1, a+1:a+3, [1, 0, 0]);
    x = MCG(x, XGate, q + 2, a+1:a+3, [0, 1, 0]);
    x = MCG(x, XGate, q + 3, a+1:a+3, [1, 1, 0]);
    x = MCG(x, XGate, q + 4, a+1:a+3, [0, 0, 1]);
    x = MCG(x, XGate, q + 5, a+1:a+3, [1, 0, 1]);
    x = MCG(x, XGate, q + 6, a+1:a+3, [0, 1, 1]);
    x = MCG(x, XGate, q + 7, a+1:a+3, [1, 1, 1]);


    % Correct phase flip errors:
    for j = 1:7
      x = H(x, q + j);
    endfor

    x = CNOT(x, q + 1, b + 1);
    x = CNOT(x, q + 3, b + 1);
    x = CNOT(x, q + 5, b + 1);
    x = CNOT(x, q + 7, b + 1);

    x = CNOT(x, q + 2, b + 2);
    x = CNOT(x, q + 3, b + 2);
    x = CNOT(x, q + 6, b + 2);
    x = CNOT(x, q + 7, b + 2);

    x = CNOT(x, q + 4, b + 3);
    x = CNOT(x, q + 5, b + 3);
    x = CNOT(x, q + 6, b + 3);
    x = CNOT(x, q + 7, b + 3);

    x = MCG(x, XGate, q + 1, b+1:b+3, [1, 0, 0]);
    x = MCG(x, XGate, q + 2, b+1:b+3, [0, 1, 0]);
    x = MCG(x, XGate, q + 3, b+1:b+3, [1, 1, 0]);
    x = MCG(x, XGate, q + 4, b+1:b+3, [0, 0, 1]);
    x = MCG(x, XGate, q + 5, b+1:b+3, [1, 0, 1]);
    x = MCG(x, XGate, q + 6, b+1:b+3, [0, 1, 1]);
    x = MCG(x, XGate, q + 7, b+1:b+3, [1, 1, 1]);

    for j = 1:7
      x = H(x, q + j);
    endfor

  endfor



endfunction
