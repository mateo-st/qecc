function [] = ComputationalBasis(x, line_break)

  % - x (vector) is a vector representing the state of the qubits

  % If there is some errors we return x unchanged with a warning.


  N = length(x);
  qubit_count = floor(log2(N));


  if N ~= 2^qubit_count
    warning("The state vector must be a vector whose length is an integer power of two");
    return;
  endif

  % First we get the position of the last non zero element:
  index = 1:N;
  max_non_zero = max(index(x ~= 0));

  tol = 1e-10;
  disp('State in computational basis:');
  for i = 1:N

    if abs(x(i)) > tol

      if i == max_non_zero

        bin_string = dec2bin([i-1, 2^(qubit_count - 1)]);
        fprintf('(%.4f+%.4fi) |%s>\n', real(x(i)), imag(x(i)), bin_string(1:2:2*(qubit_count)));

      else
        bin_string = dec2bin([i-1, 2^(qubit_count - 1)]);

        if line_break
          fprintf('(%.4f+%.4fi) |%s> + \n', real(x(i)), imag(x(i)), bin_string(1:2:2*(qubit_count)));
        else
          fprintf('(%.4f%.4fi) |%s> + ', real(x(i)), imag(x(i)), bin_string(1:2:2*(qubit_count)));
        endif

      endif

    endif

  endfor


endfunction
