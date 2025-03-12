% Create logical zero state and its density matrix:
x0 = SteaneEncoder([1; 0]);
p0 = StateVector_to_DensityMatrix(x0);

error_no_error_correction = [];
error_error_correction = [];

fidelity_error_correction = [];
fidelity_no_error_correction = [];

N = 10;
for i = 1:N
  fprintf("Iteration %d\n", i);

  % Select random error and random qubit in where to apply the error
  % The error might not be unitary. The error correction process still work
  G = rand(2, 2);
  qubit = randi([1, 7], 1);

  % Introduce error, normalize the state and compute the Density Matrix
  xe = Gate(x0, G, qubit);
  xe = xe/norm(xe);
  pe = StateVector_to_DensityMatrix(xe);

  % Apply error correction and ctake
  xc = SteaneCorrection(xe);

  % Take partial trace to eliminate the ancilla qubits
  pc = PartialTrace(xc, 8:13);

  % Save errors (measured by frobenious matrix norm) between the p0 state
  % (the state with no error) and pe and pc respectively
  error_no_error_correction = [error_no_error_correction, norm(p0 - pe)];
  error_error_correction = [error_error_correction, norm(p0 - pc)];

  fidelity_no_error_correction = [fidelity_no_error_correction, trace(p0*pe*p0)];
  fidelity_error_correction = [fidelity_error_correction, trace(p0*pc*p0)];


endfor


figure(1);
plot(1:N, fidelity_error_correction, '*');
hold on;
grid on;
plot(1:N, fidelity_no_error_correction, '*');
ylabel("Fidelity");
xlabel("Experiment number");
title("Fidelity after Error Correction with Steane Code");
legend("Error Correction", "Whitout error correction");


figure(2);
plot(1:N, 1 - fidelity_error_correction, '*');
hold on;
grid on;
plot(1:N, 1 - fidelity_no_error_correction, '*');
ylabel("Error rate");
xlabel("Experiment number");
title("Error rate (1 - Fidelity) after Error Correction with Steane Code");
legend("Error Correction", "Whitout error correction");


figure(3);
plot(1:N, error_no_error_correction, '*');
hold on;
grid on;
plot(1:N, error_error_correction, '*');
ylabel("Error");
xlabel("Experiment");
title("Frobenius matrix norm between the expected state and the resulted state");
legend("Error Correction", "Whitout error correction");



