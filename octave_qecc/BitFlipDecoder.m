function x = BitFlipDecoder(x)


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

  logical_qubit_count = floor(qubit_count/3);

  if logical_qubit_count ~= qubit_count/3
    warning("Using the steane code the number of physical qubits must be a multiple of 3");
    return;
  endif


  % Error correction:
  for i = 1:logical_qubit_count

    q = (i-1)*3;

    x = CNOT(x, q + 1, q + 3);
    x = CNOT(x, q + 1, q + 2);



  endfor



endfunction
