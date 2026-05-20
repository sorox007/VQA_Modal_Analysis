import numpy as np
import time
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B, SLSQP
from qiskit_aer.primitives import EstimatorV2
from qiskit.quantum_info import Statevector, SparsePauliOp


class VQEStructuralSolver:
    """
    Complete VQE solver for structural eigenvalue problems.
    Handles optimization, result extraction, and logging.
    """

    def __init__(self, hamiltonian, ansatz, optimizer_name='SPSA', maxiter=500, H_scale=1.0,
                 num_restarts=5, use_two_stage=True):
        self.hamiltonian = hamiltonian
        self.ansatz = ansatz
        self.optimizer_name = optimizer_name
        self.maxiter = maxiter
        self.H_scale = H_scale
        self.num_restarts = num_restarts
        self.use_two_stage = use_two_stage

        self.cost_history = []
        self.iteration_count = 0
        self._best_result = None

    def _get_optimizer(self, name=None):
        opt_name = name or self.optimizer_name
        if opt_name == 'SPSA':
            return SPSA(
                maxiter=self.maxiter,
                learning_rate=0.01,
                perturbation=0.05,
                last_avg=1,
                resamplings=1
            )
        elif opt_name == 'COBYLA':
            return COBYLA(maxiter=self.maxiter, rhobeg=0.5, tol=1e-6)
        elif opt_name == 'L_BFGS_B':
            return L_BFGS_B(maxiter=self.maxiter, maxfun=15000)
        elif opt_name == 'SLSQP':
            return SLSQP(maxiter=self.maxiter)
        else:
            return COBYLA(maxiter=self.maxiter)

    def _callback(self, nfev, x, fx, dx):
        self.cost_history.append(fx)
        self.iteration_count += 1
        if self.iteration_count % 100 == 0:
            print(f"  Iteration {self.iteration_count}: cost = {fx:.8f}")

    def _generate_initial_points(self, num_points=None, classical_hint=None):
        """Generate multiple initial points for multi-start optimization."""
        n_points = num_points or self.num_restarts
        n_params = self.ansatz.num_parameters
        points = []
        
        # 1. If classical hint provided, use it as initial point
        if classical_hint is not None:
            # Convert classical eigenvector to parameters (using amplitude encoding)
            hint_normalized = classical_hint[:2**n_params] / np.linalg.norm(classical_hint[:2**n_params])
            # Use angles that approximate the target state (simple approach)
            hint_params = np.angle(hint_normalized[:n_params]) + np.pi/2
            points.append(hint_params)
            n_points -= 1
        
        # 2. Random points
        for i in range(n_points):
            np.random.seed(42 + i * 100)
            points.append(np.random.uniform(-np.pi/2, np.pi/2, n_params))
        
        # 3. Add points near identity state (all zeros - corresponds to |0>^n)
        points.append(np.zeros(n_params))
        
        # 4. Add points near uniform superposition
        points.append(np.full(n_params, np.pi/4))
        
        return points

    def _run_single_vqe(self, initial_point, optimizer_name=None):
        """Run VQE from a single initial point."""
        self.cost_history = []
        self.iteration_count = 0
        
        estimator = EstimatorV2()
        opt_name = optimizer_name or self.optimizer_name
        optimizer = self._get_optimizer(opt_name)

        vqe = VQE(
            estimator=estimator,
            ansatz=self.ansatz,
            optimizer=optimizer,
            callback=self._callback,
            initial_point=initial_point
        )

        result = vqe.compute_minimum_eigenvalue(self.hamiltonian)
        
        lambda_vqe = result.eigenvalue.real
        lambda_physical = lambda_vqe * self.H_scale
        omega_vqe = np.sqrt(abs(lambda_physical))

        bound_circuit = self.ansatz.assign_parameters(result.optimal_point)
        state = Statevector(bound_circuit)
        mode_shape_state = state.data.real

        return {
            'eigenvalue_physical': lambda_physical,
            'eigenvalue_vqe': lambda_vqe,
            'omega': omega_vqe,
            'optimal_point': result.optimal_point,
            'optimal_circuit': result.optimal_circuit,
            'mode_shape': mode_shape_state,
            'cost_history': self.cost_history.copy(),
            'iterations': self.iteration_count,
            'optimal_value': result.eigenvalue.real
        }

    def solve(self, initial_point=None):
        """Run VQE with multi-start and two-stage optimization."""

        if initial_point is not None:
            return self._run_single_vqe(initial_point)

        initial_points = self._generate_initial_points()
        best_result = None
        best_eigenvalue = float('inf')

        print(f"Running VQE with multi-start ({len(initial_points)} initial points)...")
        
        for i, init_pt in enumerate(initial_points):
            opt_name = self.optimizer_name
            
            result = self._run_single_vqe(init_pt, optimizer_name=opt_name)
            
            print(f"  Start {i+1}/{len(initial_points)}: "
                  f"lambda={result['eigenvalue_vqe']:.6f}, "
                  f"omega={result['omega']:.4f} rad/s, "
                  f"iters={result['iterations']}")
            
            if result['eigenvalue_vqe'] < best_eigenvalue:
                best_eigenvalue = result['eigenvalue_vqe']
                best_result = result

        if self.use_two_stage and best_result is not None:
            print("\nRunning two-stage refinement (SPSA -> L_BFGS_B)...")
            
            # Stage 2: Local refinement with L-BFGS-B
            refined_result = self._run_single_vqe(
                best_result['optimal_point'],
                optimizer_name='L_BFGS_B'
            )
            
            if refined_result['eigenvalue_vqe'] < best_eigenvalue:
                best_result = refined_result
                print(f"  Refinement improved: {best_eigenvalue:.6f} -> {refined_result['eigenvalue_vqe']:.6f}")

        print(f"\nBest VQE Result:")
        print(f"  lambda_vqe (normalized) = {best_result['eigenvalue_vqe']:.8f}")
        print(f"  lambda_physical = {best_result['eigenvalue_physical']:.6f}")
        print(f"  omega_fundamental = {best_result['omega']:.4f} rad/s")
        print(f"  Iterations: {best_result['iterations']}")

        self._best_result = best_result
        return best_result

    def solve_excited_states(self, n_modes=3, penalty_factor=10.0):
        """Find multiple natural frequencies using improved VQE with reinitialization."""
        from qiskit.quantum_info import Operator

        results = []
        H_current = self.hamiltonian
        
        # Get classical eigenvalues for penalty scaling
        H_np = self.hamiltonian.to_matrix()
        classical_eigs = np.sort(np.linalg.eigvalsh(H_np))
        
        for mode_idx in range(n_modes):
            print(f"\n=== Finding Mode {mode_idx + 1} ===")

            # Calculate appropriate penalty strength - scale with eigenvalue
            penalty = penalty_factor * abs(classical_eigs[mode_idx + 1] - classical_eigs[mode_idx]) if mode_idx < len(classical_eigs) - 1 else penalty_factor * abs(classical_eigs[-1])
            penalty = max(penalty, 5.0)  # Minimum penalty

            # Solve with current Hamiltonian using L_BFGS_B (faster)
            solver = VQEStructuralSolver(
                H_current, self.ansatz,
                optimizer_name='L_BFGS_B',
                maxiter=self.maxiter,
                H_scale=self.H_scale,
                num_restarts=2,
                use_two_stage=False
            )
            result = solver.solve()
            results.append(result)

            if mode_idx < n_modes - 1:
                # Build deflation projector using proper operator construction
                optimal_params = result['optimal_point']
                bound_circuit = self.ansatz.assign_parameters(optimal_params)
                state = Statevector(bound_circuit)
                
                # Projector in computational basis
                state_vec = state.data
                projector_matrix = np.outer(state_vec, state_vec.conj()).real
                
                # Convert to operator and add to Hamiltonian
                proj_op = SparsePauliOp.from_operator(projector_matrix * penalty)
                
                # Add to current Hamiltonian (penalty in original scale, then normalize)
                H_current = H_current + proj_op
                
                print(f"  Added deflation penalty: {penalty:.4f}")

        return results


def classical_reference(hamiltonian_np):
    """Classical exact eigenvalue solution for comparison."""
    eigenvalues = np.linalg.eigvalsh(hamiltonian_np)
    return eigenvalues
