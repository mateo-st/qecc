function x = DensityMatrix_to_StateVector(p)

  % We calculate the eigenvalues and eigenvectors:
  [V, D] = eig(p);

  % Get the first eigenvector with eigenvalue 1 (or close to 1)
  tol = 1e-5;

  k = 1;
  for i = diag(D)'



    if abs(i - 1) < tol


      x = V(:, k);

      return;
    endif

    k = k + 1;
  endfor


endfunction
