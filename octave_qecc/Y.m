function x = Y(x, qubit)

  % - x (vector) is a vector representing the state of the qubits
  %   Recall that the magnitude of |x1x2...xn> in x is in the position
  %   x1x2...xn in binary in x (if we start counting from zero)
  % - qubit (int) is the qubit where the X gate is applied

  % If there is some errors we return x unchanged with a warning.

  N = length(x);
  qubit_count = floor(log2(N));

  if qubit > qubit_count || qubit < 1
    warning("'qubit' must be an integer ranging from 1 to the total number of qubits");
    return;
  endif

  if N ~= 2^qubit_count
    warning("The state vector must be a vector whose length is an integer power of two");
    return;
  endif


  % Recall that Y = iXZ (First apply Z, then X and then multiply by 1i)

  x = 1i*X(Z(x, qubit), qubit);

endfunction
