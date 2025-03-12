function logic_state = PhaseFlipEncoder(x)

  % - x (vector of columns vector)


  % If there is some errors we return x unchanged with a warning.

  logic_state = [1];

  for i = x

    % Append zeros
    for j = 1:2
      i = kron(i, [1; 0]); % Kronecker product with |0> states
    endfor

  i = CNOT(i, 1, 2);
  i = CNOT(i, 1, 3);
  i = H(i, 1);
  i = H(i, 2);
  i = H(i, 2);

  logic_state = kron(logic_state, i);

  endfor




endfunction
