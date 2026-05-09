"""
Optimizer Comparison: COBYLA vs L-BFGS-B
=========================================
Runs both optimizers from the same initial point and generates
convergence comparison plots showing error decay, iteration counts,
and wall-clock time.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
os.makedirs('results', exist_ok=True)

from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from quantum_setup import build_structural_hamiltonian
from ansatz import hardware_efficient_ansatz
from vqe_runner import VQEStructuralSolver

# --- Color Scheme ---
NAVY    = "#1A2151"
BLUE    = "#0D6EFD"
CYAN    = "#00B4D8"
GREEN   = "#0A7C59"
ORANGE  = "#E67E22"
RED     = "#C0392B"
LIGHT   = "#EBF5FB"

# --- Beam geometry ---
E = 200e9
I = 8.33e-6
rho = 7850.0
A = 0.01
L = 1.0
n_elem = 2

K, M = assemble_beam(n_elem, E, I, rho, A, L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, n_elem)
omega_classical, _ = classical_modal_analysis(K_red, M_red)
omega_ref = omega_classical[0]

H_norm, hamiltonian, _, H_scale = build_structural_hamiltonian(K_red, M_red)

# Same initial point for fair comparison
np.random.seed(42)
initial_point = np.random.uniform(-np.pi, np.pi, 12)

ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)

maxiter = 3000

print(f"\n{'='*60}")
print(f"OPTIMIZER COMPARISON (maxiter={maxiter})")
print(f"{'='*60}")
print(f"Reference: {omega_ref:.6f} rad/s\n")

# --- COBYLA ---
print("--- COBYLA (derivative-free simplex) ---")
cobyla = VQEStructuralSolver(hamiltonian, ansatz, 'COBYLA', maxiter=maxiter, H_scale=H_scale)
cobyla_res = cobyla.solve(initial_point=initial_point.copy())

# --- L-BFGS-B ---
print("\n--- L-BFGS-B (gradient-based quasi-Newton) ---")
lbfgs = VQEStructuralSolver(hamiltonian, ansatz, 'L_BFGS_B', maxiter=maxiter, H_scale=H_scale)
lbfgs_res = lbfgs.solve(initial_point=initial_point.copy())

omega_cobyla = cobyla_res['omega']
omega_lbfgs = lbfgs_res['omega']
err_cobyla = abs(omega_cobyla - omega_ref) / omega_ref * 100
err_lbfgs = abs(omega_lbfgs - omega_ref) / omega_ref * 100

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"  COBYLA:     ω = {omega_cobyla:.6f}  error = {err_cobyla:.6f}%  iters = {cobyla_res['iterations']}  time = {cobyla_res['time']:.2f}s")
print(f"  L-BFGS-B:   ω = {omega_lbfgs:.6f}  error = {err_lbfgs:.6f}%  iters = {lbfgs_res['iterations']}  time = {lbfgs_res['time']:.2f}s")
print(f"  Reference:  ω = {omega_ref:.6f}")

# ================================
# PLOTS
# ================================

# --- Plot 1: Convergence curves side by side ---
cost_cobyla = cobyla_res['cost_history']
cost_lbfgs = lbfgs_res['cost_history']
freqs_cobyla = [np.sqrt(max(c * H_scale, 0)) for c in cost_cobyla]
freqs_lbfgs = [np.sqrt(max(c * H_scale, 0)) for c in cost_lbfgs]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Optimizer Comparison: COBYLA vs L-BFGS-B",
             fontsize=14, fontweight='bold', color=NAVY)

# Top-left: COBYLA convergence
ax1 = axes[0, 0]
ax1.plot(freqs_cobyla, color=ORANGE, linewidth=1.5)
ax1.axhline(y=omega_ref, color=RED, linestyle='--', linewidth=2, label='Classical')
ax1.set_xlabel("Iteration")
ax1.set_ylabel("Frequency (rad/s)")
ax1.set_title("COBYLA Convergence", fontweight='bold', color=ORANGE)
ax1.legend()
ax1.set_facecolor(LIGHT)
ax1.grid(True, alpha=0.4)

# Top-right: L-BFGS-B convergence
ax2 = axes[0, 1]
ax2.plot(freqs_lbfgs, color=GREEN, linewidth=1.5)
ax2.axhline(y=omega_ref, color=RED, linestyle='--', linewidth=2, label='Classical')
ax2.set_xlabel("Iteration")
ax2.set_ylabel("Frequency (rad/s)")
ax2.set_title("L-BFGS-B Convergence", fontweight='bold', color=GREEN)
ax2.legend()
ax2.set_facecolor(LIGHT)
ax2.grid(True, alpha=0.4)

# Bottom-left: Error decay (semilogy)
ax3 = axes[1, 0]
err_c = [(abs(f - omega_ref) / omega_ref * 100) for f in freqs_cobyla if f > 0]
err_l = [(abs(f - omega_ref) / omega_ref * 100) for f in freqs_lbfgs if f > 0]
ax3.semilogy(err_c, color=ORANGE, linewidth=1.5, label='COBYLA')
ax3.semilogy(err_l, color=GREEN, linewidth=1.5, label='L-BFGS-B')
ax3.set_xlabel("Iteration")
ax3.set_ylabel("Relative Error (%)")
ax3.set_title("Error Decay (log scale)", fontweight='bold')
ax3.legend()
ax3.set_facecolor(LIGHT)
ax3.grid(True, alpha=0.4, which='both')

# Bottom-right: Iteration count + wall time
ax4 = axes[1, 1]
x_pos = np.arange(2)
w = 0.35
bars1 = ax4.bar(x_pos - w/2, [cobyla_res['iterations'], lbfgs_res['iterations']],
                w, color=[ORANGE, GREEN], alpha=0.85, edgecolor='white')
bars2 = ax4.bar(x_pos + w/2, [cobyla_res['time'], lbfgs_res['time']],
                w, color=[BLUE, CYAN], alpha=0.85, edgecolor='white')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(['COBYLA', 'L-BFGS-B'])
ax4.set_ylabel("Iterations / Time (s)")
ax4.set_title("Iterations and Wall Time", fontweight='bold')
ax4.legend(['Iterations', 'Time (s)'])
ax4.set_facecolor(LIGHT)
ax4.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{height:.0f}', ha='center', fontsize=9, fontweight='bold')
for bar in bars2:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{height:.2f}s', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('results/optimizer_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# --- Plot 2: Progress ratio ---
fig2, ax5 = plt.subplots(figsize=(10, 5))
# Normalize errors to iteration index 0 error
err0_c = err_c[0] if err_c[1] != 0 else 1
err0_l = err_l[0] if len(err_l) > 0 else 1
ax5.semilogy([e/err0_c for e in err_c], color=ORANGE, linewidth=1.5,
            label='COBYLA (derivative-free)', alpha=0.9)
ax5.semilogy([e/err0_l for e in err_l], color=GREEN, linewidth=1.5,
            label='L-BFGS-B (gradient-based)', alpha=0.9)
ax5.set_xlabel("Iteration", fontsize=12)
ax5.set_ylabel("Error Fraction (E / E₀)", fontsize=12)
ax5.set_title("Convergence Rate: Normalized Error vs Iterations",
              fontsize=13, fontweight='bold', color=NAVY)
ax5.legend(fontsize=11)
ax5.set_facecolor(LIGHT)
ax5.grid(True, alpha=0.4, which='both')
ax5.text(0.98, 0.02,
         f"COBYLA:     {cobyla_res['iterations']} iters, {err_cobyla:.4f}% final\n"
         f"L-BFGS-B:   {lbfgs_res['iterations']} iters, {err_lbfgs:.6f}% final\n"
         f"L-BFGS-B is {cobyla_res['iterations']/max(lbfgs_res['iterations'],1):.1f}x faster to converge",
         transform=ax5.transAxes, fontsize=9, va='bottom', ha='right',
         bbox=dict(boxstyle='round', facecolor='white', edgecolor=NAVY, alpha=0.9))
plt.tight_layout()
plt.savefig('results/optimizer_normalized_error.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n[SUCCESS] Optimizer comparison plots saved to results/")
