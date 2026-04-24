"""
VQA Modal Analysis - Complete Pipeline
Run this file to execute the full project.
"""

import numpy as np
import os
os.makedirs('results', exist_ok=True)

from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported
from quantum_setup import build_structural_hamiltonian, inspect_pauli_decomposition
from ansatz import hardware_efficient_ansatz, symmetric_ansatz
from vqe_runner import VQEStructuralSolver, classical_reference
from visualize import (plot_convergence, plot_mode_shapes,
                        plot_frequency_comparison, plot_ill_conditioning_study,
                        plot_damage_detection, plot_beam_geometry,
                        plot_mode_shapes_continuous, plot_optimizer_comparison)

# --- MATERIAL & GEOMETRY ---
E = 200e9       # Young's modulus (Pa) - steel
I = 8.33e-6     # Second moment of area (m^4)
rho = 7850.0    # Density (kg/m^3)
A = 0.01        # Cross-section area (m^2)
L = 1.0         # Beam length (m)
n_elem = 2      # Number of FEA elements

# --- STEP 1: Classical FEA ---
print("="*60)
print("STEP 1: CLASSICAL FEA BASELINE")
print("="*60)

K, M = assemble_beam(n_elem, E, I, rho, A, L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, n_elem)
omega_classical, modes_classical = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

print(f"Classical natural frequencies (rad/s): {omega_classical}")
print(f"Analytical:                            {omega_analytical[:len(omega_classical)]}")

# --- STEP 2: Quantum Hamiltonian ---
print("\n" + "="*60)
print("STEP 2: QUANTUM HAMILTONIAN CONSTRUCTION")
print("="*60)

H_norm, hamiltonian, M_half_inv, H_scale = build_structural_hamiltonian(K_red, M_red)
inspect_pauli_decomposition(hamiltonian)

# --- STEP 3: VQE on Simulator ---
print("\n" + "="*60)
print("STEP 3: VQE ON QISKIT AER SIMULATOR")
print("="*60)

ansatz_hea = hardware_efficient_ansatz(num_qubits=2, reps=2)

# Run both optimizers from same starting point for comparison comparison
np.random.seed(42)
init_pt = np.random.uniform(-np.pi, np.pi, 12)

solver_cobyla = VQEStructuralSolver(hamiltonian, ansatz_hea,
                                     optimizer_name='COBYLA', maxiter=200,
                                     H_scale=H_scale)
result_cobyla = solver_cobyla.solve(initial_point=init_pt.copy())

# L-BFGS-B
solver_lbfgs = VQEStructuralSolver(hamiltonian, ansatz_hea,
                                    optimizer_name='L_BFGS_B', maxiter=200,
                                    H_scale=H_scale)
result_lbfgs = solver_lbfgs.solve(initial_point=init_pt.copy())

# Use COBYLA result for downstream (higher modes)
result_hea = result_cobyla
solver = solver_cobyla

print(f"\n--- Optimizer Comparison (same initial point) ---")
print(f"  COBYLA:  freq = {result_cobyla['omega']:.4f} rad/s  "
      f"(error = {abs(result_cobyla['omega']-omega_classical[0])/omega_classical[0]*100:.3f}%, "
      f"iters = {result_cobyla['iterations']})")
print(f"  L-BFGS-B:  freq = {result_lbfgs['omega']:.4f} rad/s  "
      f"(error = {abs(result_lbfgs['omega']-omega_classical[0])/omega_classical[0]*100:.3f}%, "
      f"iters = {result_lbfgs['iterations']})")

# --- STEP 4: Multiple Modes ---
print("\n" + "="*60)
print("STEP 4: FINDING HIGHER MODES (DEFLATION)")
print("="*60)

multi_result = solver.solve_excited_states(n_modes=3)
omega_vqe_all = [r['omega'] for r in multi_result]
print(f"\nAll VQE frequencies: {omega_vqe_all}")
print(f"All Classical:       {list(omega_classical[:3])}")

# --- STEP 5: Novel Study ---
print("\n" + "="*60)
print("STEP 5: NOVEL STUDY - ILL-CONDITIONING")
print("="*60)

from novel_study import tapered_beam_study, damage_detection_study

taper_ratios = [1.0, 0.8, 0.6, 0.4, 0.25, 0.15]
df_tapered = tapered_beam_study(E, I, rho, A, L, taper_ratios)
print(df_tapered.to_string())
df_tapered.to_csv('results/tapered_beam_study.csv', index=False)

damage_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
df_damage = damage_detection_study(E, I, rho, A, L, damage_levels)
print(df_damage.to_string())
df_damage.to_csv('results/damage_study.csv', index=False)

# --- STEP 6: All Visualizations ---
print("\n" + "="*60)
print("STEP 6: GENERATING ALL PLOTS")
print("="*60)

plot_convergence(result_hea['cost_history'], result_hea['omega'], omega_classical[0],
                  H_scale=H_scale)

# Dual optimizer convergence plot
from visualize import plot_dual_convergence
plot_dual_convergence(result_cobyla['cost_history'], result_lbfgs['cost_history'],
                       omega_classical[0], H_scale)
plot_frequency_comparison([np.array(omega_vqe_all)], omega_classical[:3],
                           labels=['VQE (HEA, 2 reps)'])
plot_ill_conditioning_study(df_tapered)
plot_damage_detection(df_damage)

# Geometry visualizations
plot_beam_geometry(n_elem, L)
plot_mode_shapes_continuous(
    n_elem, L, modes_classical, free_dofs,
    mode_shapes_vqe=[r['mode_shape'] for r in multi_result],
    analytical_params={'L': L},
    n_modes=3
)

print("\n[SUCCESS] Full pipeline complete. Results saved to results/")
