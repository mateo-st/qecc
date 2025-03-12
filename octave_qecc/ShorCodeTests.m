% Create logical zero state and its density matrix:
x0 = [1; 0];
p0 = x0*x0';

x = ShorEncoder(x0);
p = StateVector_to_DensityMatrix(x);

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
  qubit = randi([1, 9], 1);

  % Introduce error, normalize the state and compute the Density Matrix
  xe = Gate(x, G, qubit);
  xe = xe/norm(xe);
  pe = StateVector_to_DensityMatrix(xe);

  xe_decode = ShorDecoder(xe);
  pe_decode = PartialTrace(xe_decode, 2:9);

  % Apply error correction and take partial trace:
  xc = ShorCorrection(xe);

  % Take partial trace to eliminate the ancilla qubits
  pc = PartialTrace(xc, 2:9);


  fidelity_error_correction = [fidelity_error_correction, trace(p0*pc*p0)];
  fidelity_no_error_correction = [fidelity_no_error_correction, trace(p0*pe_decode*p0)];


endfor


figure(1);
plot(1:N, fidelity_error_correction, '*');
hold on;
grid on;
plot(1:N, fidelity_no_error_correction, '*');
ylabel("Fidelity");
xlabel("Experiment number");
title("Fidelity after error correction with Shor Code");
% label("Error Correction", "No error correction");



