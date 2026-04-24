import numpy as np
import pandas as pd

from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from fea import beam_element_stiffness, beam_element_mass
from quantum_setup import build_structural_hamiltonian
from vqe_runner import VQEStructuralSolver
from ansatz import hardware_efficient_ansatz


def tapered_beam_assemble_v2(n_elements, E, I0, rho, A0, L_total, taper_ratios):
    """
    Assemble K and M for a tapered beam.

    taper_ratios[i] gives the height ratio h[i]/h0 for element i.
    For rectangular section: A[i] = A0 * taper_ratios[i], I[i] = I0 * taper_ratios[i]^3.
    """
    ndof = 2 * (n_elements + 1)
    L_e = L_total / n_elements

    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))

    for elem in range(n_elements):
        t = taper_ratios[elem]
        A_elem = A0 * t
        I_elem = I0 * t**3

        k_e = beam_element_stiffness(E * I_elem, L_e)
        m_e = beam_element_mass(rho * A_elem, L_e)

        dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]
        for i_l, i_g in enumerate(dofs):
            for j_l, j_g in enumerate(dofs):
                K_global[i_g, j_g] += k_e[i_l, j_l]
                M_global[i_g, j_g] += m_e[i_l, j_l]

    return K_global, M_global


def _linear_taper_elements(n_elements, end_ratio):
    """
    For a linearly tapered beam from h=1.0 to h=end_ratio,
    compute the height ratio at each element center.
    """
    ratios = []
    for i in range(n_elements):
        x = (i + 0.5) / n_elements
        ratio = 1.0 - x * (1.0 - end_ratio)
        ratios.append(ratio)
    return ratios


def tapered_beam_study(E, I, rho, A, L_total, taper_ratios, n_elements=2):
    """
    Study how beam taper (geometric non-uniformity) affects Hamiltonian
    condition number and VQE optimizer convergence.

    Compares three solvers:
    1. COBYLA (derivative-free simplex)
    2. L-BFGS-B (gradient-based quasi-Newton)
    3. NumPyEigensolver (exact classical reference)

    The hypothesis: as condition number increases, gradient-based
    L-BFGS-B should degrade faster than COBYLA (steeper loss landscape
    means worse gradient conditioning).
    """
    from qiskit_algorithms import NumPyMinimumEigensolver

    results = []

    for t2 in taper_ratios:
        taper_per_elem = _linear_taper_elements(n_elements, t2)

        # Assemble tapered beam
        K, M = tapered_beam_assemble_v2(n_elements, E, I, rho, A, L_total, taper_per_elem)
        K_red, M_red, _ = apply_simply_supported_bc(K, M, n_elements)

        # Build quantum Hamiltonian
        H_norm, hamiltonian, _, H_scale = build_structural_hamiltonian(K_red, M_red)
        condition_number = np.linalg.cond(H_norm)

        # Classical reference (scipy generalized eigensolver)
        omega_ref, _ = classical_modal_analysis(K_red, M_red)

        # Exactly same initial point for fair comparison
        np.random.seed(42)
        initial_point = np.random.uniform(-np.pi, np.pi, 12)  # 12 params for HEA 2q-2reps

        ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)

        # --- COBYLA (derivative-free simplex) ---
        print("\n  --- COBYLA (derivative-free) ---")
        cobyla_solver = VQEStructuralSolver(hamiltonian, ansatz, optimizer_name='COBYLA',
                                             maxiter=2000, H_scale=H_scale)
        cobyla_result = cobyla_solver.solve(initial_point=initial_point.copy())

        # --- L-BFGS-B (gradient-based quasi-Newton) ---
        print("\n  --- L-BFGS-B (gradient-based) ---")
        lbfgs_solver = VQEStructuralSolver(hamiltonian, ansatz, optimizer_name='L_BFGS_B',
                                            maxiter=2000, H_scale=H_scale)
        lbfgs_result = lbfgs_solver.solve(initial_point=initial_point.copy())

        # --- Exact quantum (NumPyEigensolver) ---
        np_solver = NumPyMinimumEigensolver()
        np_result = np_solver.compute_minimum_eigenvalue(hamiltonian)
        omega_exact = np.sqrt(abs(np_result.eigenvalue.real * H_scale))
        exact_error = abs(omega_exact - omega_ref[0]) / omega_ref[0] * 100

        # Errors
        cobyla_err = abs(cobyla_result['omega'] - omega_ref[0]) / omega_ref[0] * 100
        lbfgs_err = abs(lbfgs_result['omega'] - omega_ref[0]) / omega_ref[0] * 100

        results.append({
            'taper_ratio': t2,
            'condition_number': condition_number,
            'H_scale': H_scale,
            'omega_classical': omega_ref[0],
            'omega_exact': omega_exact,
            'exact_error_pct': exact_error,
            'omega_cobyla': cobyla_result['omega'],
            'cobyla_error_pct': cobyla_err,
            'cobyla_iterations': cobyla_result['iterations'],
            'omega_lbfgs': lbfgs_result['omega'],
            'lbfgs_error_pct': lbfgs_err,
            'lbfgs_iterations': lbfgs_result['iterations'],
        })

        print(f"\n  taper={t2:.2f} | Cond={condition_number:.1f}")
        print(f"    Classical: {omega_ref[0]:.6f} rad/s")
        print(f"    Exact:     {omega_exact:.6f} (error={exact_error:.2e}%)")
        print(f"    COBYLA:    {cobyla_result['omega']:.6f} (error={cobyla_err:.4f}%, iters={cobyla_result['iterations']})")
        print(f"    L-BFGS-B:  {lbfgs_result['omega']:.6f} (error={lbfgs_err:.4f}%, iters={lbfgs_result['iterations']})")

    return pd.DataFrame(results)


def damage_detection_study(E, I, rho, A, L, damage_levels, n_elements=2):
    """
    Study how stiffness reduction (simulated crack) affects VQE-computed frequencies.

    damage_levels: list of damage fractions, e.g., [0.0, 0.1, 0.2, 0.3, 0.5]
    """

    results = []

    for d in damage_levels:
        # Damaged beam: element 1 has reduced stiffness
        K_damaged = np.zeros((2*(n_elements+1), 2*(n_elements+1)))
        M_full = np.zeros((2*(n_elements+1), 2*(n_elements+1)))

        L_e = L / n_elements
        rhoA = rho * A

        # Assemble with damage
        EI_values = [E * I * (1 - d), E * I]  # First element damaged
        for elem in range(n_elements):
            k_e = beam_element_stiffness(EI_values[elem], L_e)
            m_e = beam_element_mass(rhoA, L_e)
            dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]
            for i_l, i_g in enumerate(dofs):
                for j_l, j_g in enumerate(dofs):
                    K_damaged[i_g, j_g] += k_e[i_l, j_l]
                    M_full[i_g, j_g] += m_e[i_l, j_l]

        # Apply BCs
        fixed_dofs = [0, 2*n_elements]
        free_dofs = [i for i in range(2*(n_elements+1)) if i not in fixed_dofs]
        K_red = K_damaged[np.ix_(free_dofs, free_dofs)]
        M_red = M_full[np.ix_(free_dofs, free_dofs)]

        # Classical solve
        omega_ref, _ = classical_modal_analysis(K_red, M_red)

        # VQE solve
        H_norm, hamiltonian, _, H_scale = build_structural_hamiltonian(K_red, M_red)
        ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)
        solver = VQEStructuralSolver(hamiltonian, ansatz, maxiter=2000, H_scale=H_scale)
        vqe_result = solver.solve()

        # Reference omega for first entry (undamaged)
        if not results:
            omega_0_ref = omega_ref[0]
        else:
            omega_0_ref = results[0]['omega_ref']

        results.append({
            'damage': d,
            'damage_pct': d * 100,
            'omega_ref': omega_ref[0],
            'omega_vqe': vqe_result['omega'],
            'freq_shift_pct': (omega_0_ref - omega_ref[0]) / omega_0_ref * 100,
            'vqe_detected_shift_pct': (omega_0_ref - vqe_result['omega']) / omega_0_ref * 100,
            'vqe_error_pct': abs(vqe_result['omega'] - omega_ref[0]) / omega_ref[0] * 100,
        })

    return pd.DataFrame(results)
