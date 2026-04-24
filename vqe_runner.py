import numpy as np
import time
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B
from qiskit.primitives import StatevectorEstimator


class VQEStructuralSolver:
    """
    Complete VQE solver for structural eigenvalue problems.
    Handles optimization, result extraction, and logging.
    """

    def __init__(self, hamiltonian, ansatz, optimizer_name='COBYLA', maxiter=500, H_scale=1.0):
        self.hamiltonian = hamiltonian
        self.ansatz = ansatz
        self.optimizer_name = optimizer_name
        self.maxiter = maxiter
        self.H_scale = H_scale  # Spectral norm for back-scaling to physical units

        self.cost_history = []
        self.iteration_count = 0

    def _get_optimizer(self):
        optimizers = {
            'COBYLA': COBYLA(maxiter=self.maxiter),
            'SPSA': SPSA(maxiter=self.maxiter),
            'L_BFGS_B': L_BFGS_B(maxiter=self.maxiter)
        }
        return optimizers[self.optimizer_name]

    def _callback(self, nfev, x, fx, dx):
        """Called at each optimizer iteration. Records convergence."""
        self.cost_history.append(fx)
        self.iteration_count += 1
        if self.iteration_count % 50 == 0:
            print(f"  Iteration {self.iteration_count}: cost = {fx:.6f}")

    def solve(self, initial_point=None):
        """Run VQE optimization. Returns physical eigenvalue and metadata."""

        estimator = StatevectorEstimator()
        optimizer = self._get_optimizer()

        if initial_point is None:
            np.random.seed(42)
            initial_point = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)

        vqe = VQE(
            estimator=estimator,
            ansatz=self.ansatz,
            optimizer=optimizer,
            callback=self._callback,
            initial_point=initial_point
        )

        print(f"Running VQE with {self.optimizer_name}, maxiter={self.maxiter}")
        start_time = time.time()
        result = vqe.compute_minimum_eigenvalue(self.hamiltonian)
        elapsed = time.time() - start_time

        # Eigenvalue from VQE is unitless (normalized Hamiltonian)
        # Back-scale to physical units: lambda_physical = lambda_vqe * H_scale
        lambda_vqe = result.eigenvalue.real
        lambda_physical = lambda_vqe * self.H_scale
        omega_vqe = np.sqrt(abs(lambda_physical))

        print(f"\nVQE Result:")
        print(f"  lambda_vqe (normalized) = {lambda_vqe:.8f}")
        print(f"  lambda_physical = {lambda_physical:.6f}")
        print(f"  omega_fundamental = {omega_vqe:.4f} rad/s")
        print(f"  Iterations: {self.iteration_count}")
        print(f"  Time: {elapsed:.2f} s")

        # Extract mode shape from optimal state vector
        from qiskit.quantum_info import Statevector
        bound_circuit = self.ansatz.assign_parameters(result.optimal_point)
        state = Statevector(bound_circuit)
        mode_shape_state = state.data.real  # Real part of quantum state amplitudes

        return {
            'eigenvalue_physical': lambda_physical,
            'omega': omega_vqe,
            'optimal_point': result.optimal_point,
            'optimal_circuit': result.optimal_circuit,
            'mode_shape': mode_shape_state,
            'cost_history': self.cost_history,
            'iterations': self.iteration_count,
            'time': elapsed
        }

    def solve_excited_states(self, n_modes=3, penalty=None):
        """Find multiple natural frequencies using VQE deflation."""

        results = []
        H_current = self.hamiltonian

        for mode_idx in range(n_modes):
            print(f"\n=== Finding Mode {mode_idx + 1} ===")

            solver = VQEStructuralSolver(
                H_current, self.ansatz,
                self.optimizer_name, self.maxiter,
                H_scale=self.H_scale
            )
            result = solver.solve()
            results.append(result)

            if mode_idx < n_modes - 1:
                # Deflation: add penalty for found eigenstate
                optimal_params = result['optimal_point']
                # Bind optimal parameters to the ansatz circuit
                bound_circuit = self.ansatz.assign_parameters(optimal_params)

                # Build projector |phi><phi| and add to Hamiltonian
                from qiskit.quantum_info import Statevector
                state = Statevector(bound_circuit)
                state_vec = state.data
                projector_np = np.outer(state_vec, state_vec.conj()).real

                from qiskit.quantum_info import SparsePauliOp
                lam = penalty or (result['eigenvalue_physical'] +
                                   abs(self.hamiltonian.coeffs.real).sum() * self.H_scale)
                proj_op = SparsePauliOp.from_operator(lam * projector_np)
                # Normalized deflation: divide projector by H_scale to keep H in [0,1]
                H_current = H_current + proj_op / self.H_scale

        return results


def classical_reference(hamiltonian_np):
    """Classical exact eigenvalue solution for comparison."""
    eigenvalues = np.linalg.eigvalsh(hamiltonian_np)
    return eigenvalues
