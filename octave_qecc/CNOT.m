function x = CNOT(x, control, target)

  % - x (vector) is a vector representing the state of the qubits
  %   Recall that the magnitude of |x1x2...xn> in x is in the position
  %   x1x2...xn in binary in x (if we start counting from zero)
  % - control (int) is the control qubit
  % - target (int) is the qubit in where the control gate is applied

  % If there is some errors we return x unchanged with a warning

  N = length(x);
  qubit_count = floor(log2(N));

  if control > qubit_count || control < 1
    warning("'control' must be an integer ranging from 1 to the total number of qubits");
    return;
  endif

  if target > qubit_count || control < 1
    warning("'target' must be an integer ranging from 1 to the total number of qubits");
    return;
  endif

  if control == target
    warning("'target' and 'control' qubits can not be the same");
  endif

  if N ~= 2^qubit_count
    warning("The state vector must be a vector whose length is an integer power of two");
    return;
  endif


  pos_control = qubit_count - control;
  pos_target = qubit_count - target;

  for i = 1:N

    % Check if the position i has a zero in position pos_target of its binary decomposition:
    % We chack i - 1 instead of i since octave starts counting at 1
    shifted_i = bitshift(i - 1, -pos_target);

    % Check if the least significant bit is 1
    is_zero = bitand(shifted_i, 1) == 0;


    % Now we see if the control is on
    shifted_i = bitshift(i - 1, -pos_control);
    is_on = bitand(shifted_i, 1) == 1;


    if is_zero && is_on

      x_i = x(i);
      x(i) = x(i + 2^pos_target);
      x(i + 2^pos_target) = x_i;

    endif


  endfor


endfunction
