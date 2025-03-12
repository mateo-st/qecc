function p_traced = PartialTrace(x, qubits)

  % qubits to trace. First we supposte that are the last qubits:

  [rows, columns] = size(x)

  if columns == 1
    p = x*x'; % The vector x must be normalized

  elseif columns == rows

    p = x;

  else

    warning("The input state must be either a column state vector or a density matrix");
    return;

  endif



  N = rows;
  qubit_count = floor(log2(N));

  if N ~= 2^qubit_count
    warning("The state vector or denisty matrix must be of size (2^n x 1) or (2^n x 2^n) respectively");
    return;
  endif

  % Define Traced qubit and left qubits
  T_count = length(qubits);
  L_count = qubit_count - T_count;


  Identity_T_count = eye(2^T_count);
  Identity_L_count = eye(2^L_count);


  p_traced = zeros(2^L_count, 2^L_count);
  for k = 1:2^T_count

    m = kron(Identity_L_count, Identity_T_count(:, k));

    p_traced = p_traced + m'*p*m;
  endfor







endfunction
