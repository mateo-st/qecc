# Test of steane code:
x = SteaneEncoder([1; 0]);
p1 = x*x';
ComputationalBasis(x, 1); % The second argument is line_break True or False


XGate = [0, 1; 1, 0];
ZGate = [1, 0; 0, -1];
HGate = 1/sqrt(2) * [1, 1; 1, -1];


x = Gate(x, rand(2, 2), 4);
x = x/norm(x);
% x = Y(x, 4);

x = SteaneCorrection(x);


ComputationalBasis(x, 1);


p = PartialTrace(x, 8:13);
x = DensityMatrix_to_StateVector(p);


ComputationalBasis(x, 1);


% Create logical state:
x0 = SteaneEncoder([1; 0]);
p0 = StateVector_to_DensityMatrix(x0);

for i = 1:100
  fprintf("Iteration %d\n", i);
  G = rand(2, 2) %
  qubit = randi([1, 7], 1); % Random qubit to introduce the error
  xe = Gate(x, G, qubit);
  pe = StateVector_to_DensityMatrix(xe);

  xc = SteaneCorrection(xe);
  pc = StateVector_to_DensityMatrix(pe);

  error_no_correction = norm(p0 - pe);
  error_error_correction = norm(p0 - pc);


endfor


plot(1:100, error_error_correction);
hold on;
plot(1:100, error_no_correction);












