function x = MCG(x, G, target, controls, state)

  % - x (vector) is a vector representing the state of the qubits
  %   Recall that the magnitude of |x1x2...xn> in x is in the position
  %   x1x2...xn in binary in x (if we start counting from zero)
  % - G (matrix) is a 2x2 matrix representing the control gate
  % - target (int) is the qubit in where the control gate is applied
  % - controls (vector) is a vector of integers indicating the controls
  % - state (vector) is a vector of the same length as controls indicating
  %   if the control is by the state 0 or 1.

  % If there is some errors (the target or controls qubits are bigger than
  % the maximum qubit count, the length of state is not the same as the
  % length of controls, or G is not a 2x2 matrix then we return x unchanged)

  N = length(x);
  qubit_count = log2(N);

  % Check that the target qubit exists
  if target > qubit_count || target < 1
    warning("'target' must be an integer ranging from 1 to the total number of qubits");
    return;
  endif

  % Check that the length of the controls and the control state are the same
  if length(controls) ~= length(state)
    warning("'controls' and 'state' must be of the same length");
    return;
  endif

  % Check that G is a 2x2 matrix
  if ~all(size(G) == [2, 2])
    warning("The gate 'G' must be a 2x2 matrix");
    return;
  endif

  % Check that the controls qubits exists
  if max(controls) > qubit_count || min(controls) < 1
    warning("'control' must be an vector with elements ranging from 1 to the total number of qubits");
    return;
  endif

  if N ~= 2^qubit_count
    warning("The state vector must be a vector whose length is an integer power of two");
    return;
  endif

  if any(target == controls)
    warning("'target' qubit can not be one of the control qubits");
    return;
  endif


  pos_controls = qubit_count - controls; % This gives a vector
  pos_target = qubit_count - target;


  for i = 1:length(x)


    shifted_i = bitshift(i - 1, -pos_target);
    is_zero = bitand(shifted_i, 1) == 0;


    % Now we check if all the controls are on:
    controls_on = 1;
    for j = 1:length(controls)

      shifted_i = bitshift(i - 1, -pos_controls(j));
      is_on = bitand(shifted_i, 1) == state(j);
      controls_on = controls_on & is_on;

    endfor


    if is_zero && controls_on

      x_i = x(i);
      x(i) = G(1, 1)*x_i + G(2, 1)*x(i + 2^pos_target);
      x(i + 2^pos_target) = G(1, 2)*x_i + G(2, 2)*x(i + 2^pos_target);

    endif


  endfor


endfunction
