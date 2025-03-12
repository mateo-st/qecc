function logic_state = ShorEncoder(x)

  % - x (vector of columns vector)


  % If there is some errors we return x unchanged with a warning.

  logic_state = [1];

  for i = x

    % Append zeros
    for j = 1:8
      i = kron(i, [1; 0]); % Kronecker product with |0> states
    endfor

  i = CNOT(i, 1, 4);
  i = CNOT(i, 1, 7);
  i = H(i, 1);
  i = H(i, 4);
  i = H(i, 7);
  i = CNOT(i, 1, 2);
  i = CNOT(i, 1, 3);
  i = CNOT(i, 4, 5);
  i = CNOT(i, 4, 6);
  i = CNOT(i, 7, 8);
  i = CNOT(i, 7, 9);

  logic_state = kron(logic_state, i);

  endfor




endfunction
