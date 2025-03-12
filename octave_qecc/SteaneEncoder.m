function logic_state = SteaneEncoder(x)

  % - x (vector of columns vector)


  % If there is some errors we return x unchanged with a warning.

  logic_state = [1];

  for i = x

    % Append zeros
    for j = 1:6
      i = kron(i, [1; 0]); % Kronecker product with |0> states
    endfor

  i = H(i, 5);
  i = H(i, 6);
  i = H(i, 7);
  i = CNOT(i, 1, 2);
  i = CNOT(i, 1, 3);
  i = CNOT(i, 5, 4);
  i = CNOT(i, 5, 3);
  i = CNOT(i, 5, 2);
  i = CNOT(i, 6, 4);
  i = CNOT(i, 6, 3);
  i = CNOT(i, 6, 1);
  i = CNOT(i, 7, 4);
  i = CNOT(i, 7, 2);
  i = CNOT(i, 7, 1);

  logic_state = kron(logic_state, i);

  endfor




endfunction
