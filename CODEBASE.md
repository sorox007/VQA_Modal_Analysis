# VQA Modal Analysis — Complete Code Repository

**Quantum Computing for Structural Dynamics**
COEP Technological University, May 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [File Inventory](#2-file-inventory)
3. [main.py — Pipeline Orchestrator](#3-mainpy)
4. [fea.py — Beam Finite Element Analysis](#4-feapy)
5. [truss.py — 1D and 2D Truss Analysis](#5-trusspy)
6. [quantum_setup.py — Hamiltonian Construction](#6-quantum_setuppy)
7. [ansatz.py — Quantum Circuit Ansätze](#7-ansatzpy)
8. [vqe_runner.py — VQE Solver](#8-vqe_runnerpy)
9. [visualize.py — Beam and Truss Visualizations](#9-visualizepy)
10. [visualize_truss2d.py — 2D Warren Truss Visualizations](#10-visualize_truss2dpy)
11. [novel_study.py — Ill-Conditioning and Damage Detection](#11-novel_studypy)
12. [optimizer_comparison.py — COBYLA vs L-BFGS-B](#12-optimizer_comparisonpy)
13. [validate_fea.py — Beam FEA Validation](#13-validate_feapy)
14. [validate_truss.py — Truss FEA Validation](#14-validate_trusspy)
15. [test_convergence.py — Mesh Convergence Study](#15-test_convergencepy)
16. [test_n_elem.py — Qubit Count Analysis](#16-test_n_elempy)
17. [generate_presentation.py — Slide Generator](#17-generate_presentationpy)
18. [generate_pdf.py — LaTeX PDF Builder](#18-generate_pdfpy)
19. [setup_pdf.py — File Flattening Utility](#19-setup_pdfpy)
20. [requirements.txt — Dependencies](#20-requirementstxt)

---

## 1. Project Overview

This codebase implements a **Variational Quantum Eigensolver (VQE)** pipeline for structural modal analysis. It computes natural frequencies and mode shapes of beam and truss structures by mapping the generalized eigenvalue problem **Kφ = ω²Mφ** onto a quantum Hamiltonian **H = M⁻¹/²KM⁻¹/²**, then solving with VQE on Qiskit Aer simulator.

The pipeline covers:
- **Beam FEA** — Euler-Bernoulli elements, simply-supported BCs, analytical validation
- **1D Truss FEA** — Axial bar elements, fixed-fixed BCs, analytical validation
- **2D Warren Truss FEA** — Triangular mesh, pinned-roller BCs, proper geometry
- **Quantum Hamiltonian** — Pauli decomposition, normalization to O(1)
- **VQE Solver** — Multi-start optimization, two-stage refinement, excited-state deflation
- **Visualization** — Convergence curves, mode shapes, frequency comparisons, animations
- **Novel Studies** — Ill-conditioning (tapered structures), damage detection (stiffness reduction)
- **Optimizer Comparison** — COBYLA vs L-BFGS-B benchmarking

---

## 2. File Inventory

| File | Description |
|------|-------------|
| `main.py` | Pipeline Orchestrator — runs full beam + truss + 2D truss analysis |
| `fea.py` | Beam FEA — Euler-Bernoulli element stiffness/mass, assembly, BCs |
| `truss.py` | 1D truss + 2D Warren truss FEA — mesh generation, assembly, BCs |
| `quantum_setup.py` | Hamiltonian construction — K,M → H, Pauli decomposition |
| `ansatz.py` | Quantum circuit ansätze — HEA, symmetric, minimal |
| `vqe_runner.py` | VQE solver — multi-start, two-stage, deflation for excited states |
| `visualize.py` | Beam and 1D truss plots — geometry, mode shapes, convergence |
| `visualize_truss2d.py` | 2D Warren truss plots — geometry, mode shapes, animation |
| `novel_study.py` | Ill-conditioning and damage detection studies |
| `optimizer_comparison.py` | COBYLA vs L-BFGS-B benchmarking |
| `validate_fea.py` | Beam FEA validation against analytical solution |
| `validate_truss.py` | Truss FEA validation against analytical solution |
| `test_convergence.py` | Mesh convergence study |
| `test_n_elem.py` | Qubit count analysis for different mesh sizes |
| `generate_presentation.py` | Matplotlib-based slide deck generator |
| `generate_pdf.py` | LaTeX PDF builder with embedded source code |
| `setup_pdf.py` | Utility to flatten project files into `flat/` directory |
| `requirements.txt` | Python dependencies |

---

## 3. main.py

```python
"""
VQA Modal Analysis - Complete Pipeline
Run this file to execute the full project (Beam + 1D Truss).
"""

import numpy as np
import os
os.makedirs('results', exist_ok=True)

from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported
from truss import (assemble_truss, apply_fixed_fixed_bc, apply_fixed_free_bc,
                   classical_modal_analysis as truss_classical_modal,
                   analytical_fixed_fixed, analytical_fixed_free,
                   validate_truss_matrices, print_truss_info,
                   generate_warren_truss_mesh, assemble_truss2d, apply_pinned_roller_bc,
                   classical_modal_analysis_2d)
from quantum_setup import build_structural_hamiltonian, inspect_pauli_decomposition
from ansatz import hardware_efficient_ansatz, symmetric_ansatz
from vqe_runner import VQEStructuralSolver, classical_reference
from visualize import (plot_convergence, plot_mode_shapes,
                       plot_frequency_comparison, plot_ill_conditioning_study,
                       plot_damage_detection, plot_beam_geometry,
                       plot_mode_shapes_continuous, plot_dual_convergence,
                       plot_truss_geometry, plot_truss_mode_shapes,
                       plot_truss_frequency_comparison)
from visualize_truss2d import (plot_truss2d_geometry, plot_truss2d_mode_shapes,
                                animate_truss2d_mode, plot_truss2d_frequency_comparison)

# ===========================================================
# BEAM ANALYSIS PIPELINE
# ===========================================================

# --- Material & Geometry ---
E = 200e9       # Young's modulus (Pa) - steel
I = 8.33e-6     # Second moment of area (m^4)
rho = 7850.0    # Density (kg/m^3)
A = 0.01        # Cross-section area (m^2)
L = 1.0         # Beam length (m)
n_elem_beam = 2      # Number of FEA elements

# --- STEP 1: Classical FEA ---
print("="*60)
print("STEP 1: CLASSICAL FEA BASELINE (BEAM)")
print("="*60)

K, M = assemble_beam(n_elem_beam, E, I, rho, A, L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, n_elem_beam)
omega_classical, modes_classical = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

print(f"Classical natural frequencies (rad/s): {omega_classical}")
print(f"Analytical:                            {omega_analytical[:len(omega_classical)]}")

# --- STEP 2: Quantum Hamiltonian ---
print("\n" + "="*60)
print("STEP 2: QUANTUM HAMILTONIAN CONSTRUCTION (BEAM)")
print("="*60)

H_norm, hamiltonian, M_half_inv, H_scale = build_structural_hamiltonian(K_red, M_red)
inspect_pauli_decomposition(hamiltonian)

# --- STEP 3: VQE on Simulator ---
print("\n" + "="*60)
print("STEP 3: VQE ON QISKIT AER SIMULATOR (BEAM)")
print("="*60)

ansatz_hea = hardware_efficient_ansatz(num_qubits=2, reps=2)

# Run with COBYLA (derivative-free)
solver_cobyla = VQEStructuralSolver(
    hamiltonian, ansatz_hea,
    optimizer_name='COBYLA', maxiter=500, H_scale=H_scale
)
result_cobyla = solver_cobyla.solve()

# Run with L_BFGS-B (gradient-based)
solver_lbfgs = VQEStructuralSolver(
    hamiltonian, ansatz_hea,
    optimizer_name='L_BFGS_B', maxiter=500, H_scale=H_scale
)
result_lbfgs = solver_lbfgs.solve()

# Primary result for downstream use: L_BFGS-B (fastest convergence)
result_hea = result_lbfgs

print(f"\n--- Beam VQE Result ---")
print(f"  COBYLA:   omega = {result_cobyla['omega']:.4f} rad/s  "
      f"(error = {abs(result_cobyla['omega']-omega_classical[0])/omega_classical[0]*100:.3f}%, "
      f"iters = {result_cobyla['iterations']})")
print(f"  L_BFGS-B: omega = {result_lbfgs['omega']:.4f} rad/s  "
      f"(error = {abs(result_lbfgs['omega']-omega_classical[0])/omega_classical[0]*100:.3f}%, "
      f"iters = {result_lbfgs['iterations']})")

# --- STEP 4: Multiple Modes ---
print("\n" + "="*60)
print("STEP 4: FINDING HIGHER MODES (DEFLATION) - BEAM")
print("="*60)

print("Note: Using classical frequencies for higher modes (deflation skipped for speed)")
omega_vqe_all = [result_hea['omega']]
omega_vqe_all.extend(omega_classical[1:3].tolist())
print(f"VQE frequencies (Mode 1 VQE, Modes 2-3 classical): {omega_vqe_all}")
print(f"All Classical:       {list(omega_classical[:3])}")

# ===========================================================
# TRUSS ANALYSIS PIPELINE
# ===========================================================

print("\n" + "="*60)
print("TRUSS ANALYSIS PIPELINE")
print("="*60)

# --- Material & Geometry (1D Truss) ---
E = 200e9; A = 0.01; rho = 7850.0; L = 1.0; n_elem = 4

# --- STEP T1: Generate Mesh & Classical FEA ---
print("\n--- 1D Truss: Mesh Generation & Classical FEA ---")

K_t, M_t = assemble_truss(n_elem, E, A, rho, L)
K_t_red, M_t_red, free_dofs_t = apply_fixed_fixed_bc(K_t, M_t)
omega_t_classical, modes_t = classical_modal_analysis(K_t_red, M_t_red)

# --- STEP T2: Quantum Hamiltonian (2 qubits) ---
H_norm_t, ham_t, _, H_scale_t = build_structural_hamiltonian(K_t_red, M_t_red)
inspect_pauli_decomposition(ham_t)

# --- STEP T3: VQE on Simulator (2 qubits) ---
ansatz_t = hardware_efficient_ansatz(num_qubits=2, reps=2)
np.random.seed(42)
init_pt_t = np.random.uniform(-np.pi, np.pi, ansatz_t.num_parameters)

solver_t_cobyla = VQEStructuralSolver(ham_t, ansatz_t, optimizer_name='COBYLA', maxiter=500, H_scale=H_scale_t)
result_t_cobyla = solver_t_cobyla.solve(initial_point=init_pt_t.copy())

solver_t_lbfgs = VQEStructuralSolver(ham_t, ansatz_t, optimizer_name='L_BFGS_B', maxiter=500, H_scale=H_scale_t)
result_t_lbfgs = solver_t_lbfgs.solve(initial_point=init_pt_t.copy())

result_t_hea = result_t_lbfgs

plot_dual_convergence(result_t_cobyla['cost_history'], result_t_lbfgs['cost_history'], omega_t_classical[0], H_scale_t)
plot_truss_frequency_comparison([[result_t_lbfgs['omega']] + omega_t_classical[1:].tolist()], omega_t_classical, labels=['VQE (L-BFGS-B)'])

# --- T4: Higher Modes (Deflation) ---
solver_t_deflate = VQEStructuralSolver(ham_t, ansatz_t, optimizer_name='COBYLA', maxiter=500, H_scale=H_scale_t)
multi_t = solver_t_deflate.solve_excited_states(n_modes=3)
omega_t_all = [r['omega'] for r in multi_t]

# ===========================================================
# COMPARISON SUMMARY
# ===========================================================
print("\n" + "="*60)
print("COMPARISON: BEAM vs TRUSS")
print("="*60)
# ... (comparison table printed)

# ===========================================================
# NOVEL STUDIES
# ===========================================================
RUN_NOVEL_STUDIES = True
if RUN_NOVEL_STUDIES:
    from novel_study import (tapered_beam_study, damage_detection_study, tapered_truss_study, truss_damage_study)
    # ... (ill-conditioning and damage detection studies)

# ===========================================================
# VISUALIZATIONS
# ===========================================================
# ... (all plot calls for beam, truss, mode shapes, convergence)

# ===========================================================
# 2D WARREN TRUSS ANALYSIS
# ===========================================================
nodes, members, node_ids = generate_warren_truss_mesh(n_chords=2, L=1.0, h=0.3)
K_2d, M_2d = assemble_truss2d(nodes, members, E_truss, A_truss, rho_truss)
K_2d_red, M_2d_red, free_dofs_2d, fixed_dofs_2d = apply_pinned_roller_bc(K_2d, M_2d, nodes)
omega_2d_classical, modes_2d, _ = classical_modal_analysis_2d(K_2d_red, M_2d_red, n_modes=2)

H_norm_2d, ham_2d, _, H_scale_2d = build_structural_hamiltonian(K_2d_red, M_2d_red)
ansatz_2d = hardware_efficient_ansatz(num_qubits=2, reps=2)
solver_2d = VQEStructuralSolver(ham_2d, ansatz_2d, optimizer_name='COBYLA', maxiter=500, H_scale=H_scale_2d)
result_2d = solver_2d.solve()

# 2D visualizations
plot_truss2d_geometry(nodes, members, node_ids)
plot_truss2d_mode_shapes(nodes, members, node_ids, modes_2d, free_dofs_2d, n_modes=2, scale=0.5)
animate_truss2d_mode(nodes, members, node_ids, modes_2d[:, 0], free_dofs_2d, mode_num=1, n_frames=60, scale=0.5)
plot_truss2d_frequency_comparison(...)

print("\n[SUCCESS] Full pipeline complete. Results saved to results/")
```

---

## 4. fea.py

```python
import numpy as np
import scipy.linalg as la

def beam_element_stiffness(EI, L):
    """Returns 4x4 Euler-Bernoulli beam element stiffness matrix.
    DOF order: [v_i, theta_i, v_j, theta_j]"""
    k = EI / L**3 * np.array([
        [ 12,   6*L,  -12,   6*L],
        [  6*L,  4*L**2, -6*L,  2*L**2],
        [-12,  -6*L,   12,  -6*L],
        [  6*L,  2*L**2, -6*L,  4*L**2]
    ])
    return k

def beam_element_mass(rhoA, L):
    """Returns 4x4 consistent mass matrix for Euler-Bernoulli beam element."""
    m = rhoA * L / 420 * np.array([
        [ 156,   22*L,   54,  -13*L],
        [  22*L,  4*L**2,  13*L,  -3*L**2],
        [  54,   13*L,  156,  -22*L],
        [ -13*L,  -3*L**2, -22*L,   4*L**2]
    ])
    return m

def assemble_beam(num_elements, E, I, rho, A, L_total):
    """Assemble global K and M matrices for a uniform beam."""
    n = num_elements
    ndof = 2 * (n + 1)
    L_e = L_total / n
    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))
    EI = E * I
    rhoA = rho * A
    for elem in range(n):
        k_e = beam_element_stiffness(EI, L_e)
        m_e = beam_element_mass(rhoA, L_e)
        dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]
        for i_local, i_global in enumerate(dofs):
            for j_local, j_global in enumerate(dofs):
                K_global[i_global, j_global] += k_e[i_local, j_local]
                M_global[i_global, j_global] += m_e[i_local, j_local]
    return K_global, M_global

def apply_simply_supported_bc(K, M, num_elements):
    """Apply simply-supported BCs: remove transverse displacement DOF at both ends."""
    n = num_elements
    ndof = 2 * (n + 1)
    fixed_dofs = [0, 2*n]
    free_dofs = [i for i in range(ndof) if i not in fixed_dofs]
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs

def apply_cantilever_bc(K, M):
    """Apply cantilever BCs: remove all DOFs at node 0 (fixed end)."""
    fixed_dofs = [0, 1]
    ndof = K.shape[0]
    free_dofs = list(range(2, ndof))
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs

def classical_modal_analysis(K_red, M_red):
    """Solve generalized eigenvalue problem. Returns natural frequencies (rad/s) and mode shapes."""
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    omega = np.sqrt(np.abs(eigenvalues))
    return omega, eigenvectors

def analytical_simply_supported(E, I, rho, A, L, n_modes=4):
    """Analytical natural frequencies for simply-supported Euler-Bernoulli beam."""
    frequencies = []
    for n in range(1, n_modes + 1):
        omega_n = (n * np.pi / L)**2 * np.sqrt(E * I / (rho * A))
        frequencies.append(omega_n)
    return np.array(frequencies)
```

---

## 5. truss.py

```python
import numpy as np
import scipy.linalg as la


def truss_element_stiffness(EA, L):
    """2x2 stiffness matrix: (EA/L)*[[1,-1],[-1,1]]"""
    return (EA / L) * np.array([[1, -1], [-1, 1]])


def truss_element_mass(rhoA, L, lumped=False):
    """2x2 mass matrix: consistent=(rhoAL/6)*[[2,1],[1,2]], lumped=(rhoAL/2)*I"""
    if lumped:
        return (rhoA * L / 2) * np.eye(2)
    else:
        return (rhoA * L / 6) * np.array([[2, 1], [1, 2]])


def assemble_truss(num_elements, E, A, rho, L_total):
    """Assemble global K, M (size: n+1 x n+1, n=num_elements)"""
    ndof = num_elements + 1
    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))
    L_e = L_total / num_elements
    for elem in range(num_elements):
        k_e = truss_element_stiffness(E * A, L_e)
        m_e = truss_element_mass(rho * A, L_e, lumped=False)
        dofs = [elem, elem + 1]
        for i_local, i_global in enumerate(dofs):
            for j_local, j_global in enumerate(dofs):
                K_global[i_global, j_global] += k_e[i_local, j_local]
                M_global[i_global, j_global] += m_e[i_local, j_local]
    return K_global, M_global


def apply_fixed_fixed_bc(K, M):
    """Remove DOF at both ends (indices 0 and n)"""
    n = K.shape[0] - 1
    free_dofs = list(range(1, n))
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs


def apply_fixed_free_bc(K, M):
    """Remove DOF at fixed end (index 0)"""
    free_dofs = list(range(1, K.shape[0]))
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs


def classical_modal_analysis(K_red, M_red):
    """scipy.linalg.eigh — identical to beam"""
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    omega = np.sqrt(eigenvalues)
    return omega, eigenvectors


def analytical_fixed_fixed(E, A, rho, L, n_modes=4):
    """omega_n = (n*pi/L)*sqrt(E/rho)"""
    n_vals = np.arange(1, n_modes + 1)
    omega = (n_vals * np.pi / L) * np.sqrt(E / rho)
    return omega


def analytical_fixed_free(E, A, rho, L, n_modes=4):
    """omega_n = (2n-1)*pi/(2L)*sqrt(E/rho)"""
    n_vals = np.arange(1, n_modes + 1)
    omega = ((2 * n_vals - 1) * np.pi / (2 * L)) * np.sqrt(E / rho)
    return omega


def validate_truss_matrices(K, M):
    """Validate truss matrices: symmetry, positive definiteness, condition number"""
    checks = {}
    checks['K_symmetric'] = np.allclose(K, K.T, atol=1e-10)
    checks['M_symmetric'] = np.allclose(M, M.T, atol=1e-10)
    try:
        K_eigvals = la.eigvalsh(K)
        M_eigvals = la.eigvalsh(M)
        checks['K_positive_definite'] = np.all(K_eigvals > 0)
        checks['M_positive_definite'] = np.all(M_eigvals > 0)
        checks['K_min_eigenvalue'] = np.min(K_eigvals)
        checks['M_min_eigenvalue'] = np.min(M_eigvals)
    except la.LinAlgError:
        checks['K_positive_definite'] = False
        checks['M_positive_definite'] = False
    checks['K_condition_number'] = np.linalg.cond(K)
    checks['M_condition_number'] = np.linalg.cond(M)
    return checks


def print_truss_info(num_elements, E, A, rho, L_total):
    """Print truss geometry and material info"""
    print("="*50)
    print("TRUSS GEOMETRY & MATERIAL")
    print("="*50)
    print(f"Number of elements: {num_elements}")
    print(f"Element length: {L_total/num_elements:.4f} m")
    print(f"Total length: {L_total:.4f} m")
    print(f"Young's modulus: {E:.2e} Pa")
    print(f"Density: {rho:.1f} kg/m³")
    print(f"Cross-sectional area: {A:.6f} m²")
    print(f"Axial stiffness EA: {E*A:.2e} N")
    print(f"Axial mass rho*A: {rho*A:.4f} kg/m")
    print("="*50)


# ============================================================
# 2D WARREN TRUSS FUNCTIONS
# ============================================================

def generate_warren_truss_mesh(n_chords=5, L=1.0, h=0.3):
    """
    Generate 2D Warren truss mesh with vertical end posts.
    Warren truss pattern: bottom chord nodes (B0-Bn), top chord nodes (T0-Tn)
    where n = n_chords - 1
    """
    n_top_nodes = n_chords - 1
    n_nodes = 2 * n_chords - 1
    x_spacing = L / (n_chords - 1)
    nodes = np.zeros((n_nodes, 2))
    node_ids = {}

    # Bottom chord nodes: B0, B1, ..., B(n_chords-1)
    for i in range(n_chords):
        nodes[i, 0] = i * x_spacing
        nodes[i, 1] = 0.0
        node_ids[f'B{i}'] = i

    # Top chord nodes: T0, T1, ..., T(n_top_nodes-1)
    for i in range(n_top_nodes):
        nodes[n_chords + i, 0] = (i + 0.5) * x_spacing
        nodes[n_chords + i, 1] = h
        node_ids[f'T{i}'] = n_chords + i

    members = []
    # Vertical end posts
    members.append((0, n_chords, None, None, None))
    members.append((n_chords - 1, 2 * n_chords - 2, None, None, None))
    # Bottom chord
    for i in range(n_chords - 1):
        members.append((i, i + 1, None, None, None))
    # Top chord
    for i in range(n_top_nodes - 1):
        members.append((n_chords + i, n_chords + i + 1, None, None, None))
    # Diagonal web members (Warren pattern)
    for i in range(n_top_nodes):
        if i < n_chords - 1:
            members.append((i + 1, n_chords + i, None, None, None))
        if i < n_top_nodes - 1 and i + 1 < n_chords - 1:
            members.append((n_chords + i, i + 2, None, None, None))

    return nodes, members, node_ids


def truss2d_element_stiffness(E, A, nodes, i, j):
    """Compute 2D truss element stiffness matrix (axial only)."""
    xi, yi = nodes[i]; xj, yj = nodes[j]
    dx = xj - xi; dy = yj - yi
    L = np.sqrt(dx**2 + dy**2)
    c = dx / L; s = dy / L
    k_e = (E * A / L) * np.array([
        [c**2, c*s, -c**2, -c*s],
        [c*s, s**2, -c*s, -s**2],
        [-c**2, -c*s, c**2, c*s],
        [-c*s, -s**2, c*s, s**2]
    ])
    return k_e


def truss2d_element_mass(rho, A, nodes, i, j, lumped=False):
    """Compute 2D truss element mass matrix."""
    xi, yi = nodes[i]; xj, yj = nodes[j]
    dx = xj - xi; dy = yj - yi
    L = np.sqrt(dx**2 + dy**2)
    if lumped:
        m_e = (rho * A * L / 2) * np.eye(4)
    else:
        m_e = (rho * A * L / 6) * np.array([
            [2, 0, 1, 0], [0, 2, 0, 1], [1, 0, 2, 0], [0, 1, 0, 2]
        ])
    return m_e


def assemble_truss2d(nodes, members, E, A, rho):
    """Assemble global K, M for 2D truss."""
    n_nodes = nodes.shape[0]; ndof = 2 * n_nodes
    K_global = np.zeros((ndof, ndof)); M_global = np.zeros((ndof, ndof))
    for member in members:
        i, j, E_m, A_m, rho_m = member
        E_use = E if E_m is None else E_m
        A_use = A if A_m is None else A_m
        rho_use = rho if rho_m is None else rho_m
        k_e = truss2d_element_stiffness(E_use, A_use, nodes, i, j)
        m_e = truss2d_element_mass(rho_use, A_use, nodes, i, j)
        dofs = [2*i, 2*i+1, 2*j, 2*j+1]
        for ii, di in enumerate(dofs):
            for jj, dj in enumerate(dofs):
                K_global[di, dj] += k_e[ii, jj]
                M_global[di, dj] += m_e[ii, jj]
    return K_global, M_global


def apply_pinned_roller_bc(K, M, nodes):
    """Pinned support at B0 (both x,y), roller at B(n-1) (y only)."""
    n_nodes = nodes.shape[0]; ndof = 2 * n_nodes
    n_chords = (n_nodes + 1) // 2
    fixed_dofs = [0, 1]  # B0: both x and y
    roller_node = n_chords - 1
    fixed_dofs.append(2 * roller_node + 1)  # y-DOF only
    free_dofs = list(sorted([i for i in range(ndof) if i not in fixed_dofs]))
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs, fixed_dofs


def classical_modal_analysis_2d(K_red, M_red, n_modes=None):
    """Classical modal analysis for 2D truss."""
    from scipy import linalg as la
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]; eigenvectors = eigenvectors[:, idx]
    if n_modes is not None:
        eigenvalues = eigenvalues[:n_modes]; eigenvectors = eigenvectors[:, :n_modes]
    omega = np.sqrt(eigenvalues)
    return omega, eigenvectors, eigenvalues
```

---

## 6. quantum_setup.py

```python
import numpy as np
import scipy.linalg as la
from qiskit.quantum_info import SparsePauliOp


def build_structural_hamiltonian(K_red, M_red):
    """
    Convert structural generalized eigenvalue problem to quantum Hamiltonian.
    Transforms: K phi = omega^2 M phi
    Into: H |psi> = lambda |psi>  where H = M^(-1/2) K M^(-1/2), lambda = omega^2
    """
    M_half_inv = la.fractional_matrix_power(M_red, -0.5)
    H_np = M_half_inv @ K_red @ M_half_inv
    H_np = 0.5 * (H_np + H_np.T)
    assert np.allclose(H_np, H_np.T, atol=1e-10), "H is not Hermitian!"

    raw_eigenvalues = np.linalg.eigvalsh(H_np)
    H_scale = np.max(np.abs(raw_eigenvalues))
    H_norm = H_np / H_scale

    # Pad to power-of-2 size for Qiskit
    n = H_norm.shape[0]
    n_qubits = int(np.ceil(np.log2(n)))
    padded_size = 2 ** n_qubits
    if padded_size != n:
        pad_value = 2.0
        H_padded = np.eye(padded_size) * pad_value
        H_padded[:n, :n] = H_norm
        H_norm = H_padded

    hamiltonian = SparsePauliOp.from_operator(H_norm)

    H_reconstructed = hamiltonian.to_matrix()
    eigvals_pauli = np.linalg.eigvalsh(H_reconstructed)
    print(f"Pauli op eigenvalues (reconstructed): {eigvals_pauli}")
    print(f"Matrix size: {H_norm.shape} (padded from {H_np.shape})")
    print(f"Number of Pauli terms: {len(hamiltonian)}")
    print(f"Condition number of H: {np.linalg.cond(H_np):.2f}")
    print(f"H_scale (spectral norm): {H_scale:.4e}")

    return H_norm, hamiltonian, M_half_inv, H_scale


def inspect_pauli_decomposition(hamiltonian):
    """Print all Pauli terms and their coefficients."""
    print("\n=== PAULI DECOMPOSITION ===")
    print(f"{'Pauli String':<15} {'Coefficient':<15}")
    print("-" * 30)
    for pauli, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
        if abs(coeff) > 1e-10:
            print(f"{str(pauli):<15} {coeff.real:<15.6f}")
```

---

## 7. ansatz.py

```python
from qiskit.circuit.library import EfficientSU2, RealAmplitudes
from qiskit.circuit import QuantumCircuit, ParameterVector
import numpy as np

def hardware_efficient_ansatz(num_qubits, reps=2):
    """Standard Hardware-Efficient Ansatz (HEA)."""
    ansatz = EfficientSU2(num_qubits=num_qubits, reps=reps, entanglement='linear')
    ansatz = ansatz.decompose()
    print(f"HEA: {num_qubits} qubits, {reps} reps, {ansatz.num_parameters} parameters")
    return ansatz

def symmetric_ansatz(num_qubits, reps=2):
    """Symmetry-aware ansatz for simply-supported beam.
    Constrains parameters to enforce mirror symmetry of mode shapes."""
    n_params = 2 * reps + 2
    theta = ParameterVector('θ', n_params)
    qc = QuantumCircuit(num_qubits)
    param_idx = 0
    for rep in range(reps):
        for q in range(num_qubits // 2):
            qc.ry(theta[param_idx], q)
            qc.ry(theta[param_idx], num_qubits - 1 - q)
        param_idx += 1
        for q in range(num_qubits - 1):
            qc.cx(q, q + 1)
    for q in range(num_qubits):
        qc.ry(theta[param_idx], q)
        param_idx += 1
    print(f"Symmetric ansatz: {num_qubits} qubits, {reps} reps, {qc.num_parameters} parameters")
    return qc

def minimal_ansatz(num_qubits):
    """Minimal 2-parameter ansatz for quick testing."""
    theta = ParameterVector('θ', 2 * num_qubits)
    qc = QuantumCircuit(num_qubits)
    for q in range(num_qubits):
        qc.ry(theta[q], q)
    qc.cx(0, 1)
    for q in range(num_qubits):
        qc.ry(theta[num_qubits + q], q)
    return qc
```

---

## 8. vqe_runner.py

```python
import numpy as np
import time
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B, SLSQP
from qiskit_aer.primitives import EstimatorV2
from qiskit.quantum_info import Statevector, SparsePauliOp


class VQEStructuralSolver:
    """Complete VQE solver for structural eigenvalue problems."""

    def __init__(self, hamiltonian, ansatz, optimizer_name='SPSA', maxiter=500,
                 H_scale=1.0, num_restarts=5, use_two_stage=True):
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
            return SPSA(maxiter=self.maxiter, learning_rate=0.01, perturbation=0.05, last_avg=1, resamplings=1)
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
        if classical_hint is not None:
            hint_normalized = classical_hint[:2**n_params] / np.linalg.norm(classical_hint[:2**n_params])
            hint_params = np.angle(hint_normalized[:n_params]) + np.pi/2
            points.append(hint_params)
            n_points -= 1
        for i in range(n_points):
            np.random.seed(42 + i * 100)
            points.append(np.random.uniform(-np.pi/2, np.pi/2, n_params))
        points.append(np.zeros(n_params))
        points.append(np.full(n_params, np.pi/4))
        return points

    def _run_single_vqe(self, initial_point, optimizer_name=None):
        """Run VQE from a single initial point."""
        self.cost_history = []
        self.iteration_count = 0
        estimator = EstimatorV2()
        opt_name = optimizer_name or self.optimizer_name
        optimizer = self._get_optimizer(opt_name)
        vqe = VQE(estimator=estimator, ansatz=self.ansatz, optimizer=optimizer,
                  callback=self._callback, initial_point=initial_point)
        result = vqe.compute_minimum_eigenvalue(self.hamiltonian)
        lambda_vqe = result.eigenvalue.real
        lambda_physical = lambda_vqe * self.H_scale
        omega_vqe = np.sqrt(abs(lambda_physical))
        bound_circuit = self.ansatz.assign_parameters(result.optimal_point)
        state = Statevector(bound_circuit)
        mode_shape_state = state.data.real
        return {
            'eigenvalue_physical': lambda_physical, 'eigenvalue_vqe': lambda_vqe,
            'omega': omega_vqe, 'optimal_point': result.optimal_point,
            'optimal_circuit': result.optimal_circuit, 'mode_shape': mode_shape_state,
            'cost_history': self.cost_history.copy(), 'iterations': self.iteration_count,
            'optimal_value': result.eigenvalue.real
        }

    def solve(self, initial_point=None):
        """Run VQE with multi-start and two-stage optimization."""
        if initial_point is not None:
            return self._run_single_vqe(initial_point)
        initial_points = self._generate_initial_points()
        best_result = None; best_eigenvalue = float('inf')
        for i, init_pt in enumerate(initial_points):
            result = self._run_single_vqe(init_pt)
            if result['eigenvalue_vqe'] < best_eigenvalue:
                best_eigenvalue = result['eigenvalue_vqe']
                best_result = result
        if self.use_two_stage and best_result is not None:
            refined_result = self._run_single_vqe(best_result['optimal_point'], optimizer_name='L_BFGS_B')
            if refined_result['eigenvalue_vqe'] < best_eigenvalue:
                best_result = refined_result
        self._best_result = best_result
        return best_result

    def solve_excited_states(self, n_modes=3, penalty_factor=10.0):
        """Find multiple natural frequencies using deflation."""
        results = []; H_current = self.hamiltonian
        H_np = self.hamiltonian.to_matrix()
        classical_eigs = np.sort(np.linalg.eigvalsh(H_np))
        for mode_idx in range(n_modes):
            penalty = penalty_factor * abs(classical_eigs[mode_idx + 1] - classical_eigs[mode_idx])
            penalty = max(penalty, 5.0)
            solver = VQEStructuralSolver(H_current, self.ansatz, optimizer_name='L_BFGS_B',
                                          maxiter=self.maxiter, H_scale=self.H_scale,
                                          num_restarts=2, use_two_stage=False)
            result = solver.solve(); results.append(result)
            if mode_idx < n_modes - 1:
                optimal_params = result['optimal_point']
                bound_circuit = self.ansatz.assign_parameters(optimal_params)
                state = Statevector(bound_circuit)
                state_vec = state.data
                projector_matrix = np.outer(state_vec, state_vec.conj()).real
                proj_op = SparsePauliOp.from_operator(projector_matrix * penalty)
                H_current = H_current + proj_op
        return results


def classical_reference(hamiltonian_np):
    """Classical exact eigenvalue solution for comparison."""
    eigenvalues = np.linalg.eigvalsh(hamiltonian_np)
    return eigenvalues
```

---

## 9. visualize.py

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch

# Color Scheme
NAVY="#1A2151"; BLUE="#0D6EFD"; CYAN="#00B4D8"; GREEN="#0A7C59"
RED="#C0392B"; ORANGE="#E67E22"; GREY="#566573"; LIGHT="#EBF5FB"

# --- Beam geometry, mode shapes, convergence, frequency comparison ---
# --- Ill-conditioning study, damage detection ---
# --- Truss geometry, truss mode shapes, truss frequency comparison ---
# (Full implementation with all plotting functions)
```

**Key functions in visualize.py:**
- `plot_beam_geometry()` — 2D side-view of beam with supports
- `plot_mode_shapes_continuous()` — Classical vs VQE mode shapes with analytical overlay
- `plot_dual_convergence()` — COBYLA vs L-BFGS-B convergence comparison
- `plot_convergence()` — VQE cost function convergence
- `plot_frequency_comparison()` — Bar chart of natural frequencies
- `plot_ill_conditioning_study()` — Condition number vs VQE performance
- `plot_damage_detection()` — Frequency shift vs damage severity
- `plot_truss_geometry()` — 1D truss representation
- `plot_truss_mode_shapes()` — Axial displacement profiles
- `plot_truss_frequency_comparison()` — Truss VQE vs classical

---

## 10. visualize_truss2d.py

```python
"""2D Warren Truss Visualization Functions"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, Circle

# (Full implementation with color scheme matching visualize.py)
```

**Key functions in visualize_truss2d.py:**
- `plot_truss2d_geometry()` — 2D truss with node labels, pinned/roller supports
- `plot_truss2d_mode_shapes()` — Deformed overlay on undeformed truss
- `animate_truss2d_mode()` — Animated GIF of oscillating mode shape
- `plot_truss2d_frequency_comparison()` — VQE vs Classical bar chart

---

## 11. novel_study.py

```python
import numpy as np
import pandas as pd
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from fea import beam_element_stiffness, beam_element_mass
from truss import assemble_truss, apply_fixed_fixed_bc, analytical_fixed_fixed
from quantum_setup import build_structural_hamiltonian
from vqe_runner import VQEStructuralSolver
from ansatz import hardware_efficient_ansatz

# Key functions:
# - tapered_beam_study(): VQE performance vs beam taper ratio
# - damage_detection_study(): Frequency shift vs stiffness reduction (beam)
# - tapered_truss_study(): VQE performance vs truss area ratio
# - truss_damage_study(): Frequency shift vs stiffness reduction (truss)
# - _tapered_truss_assemble(): Assembly for tapered truss
# - _linear_taper_elements(): Height ratios for linear taper
# - tapered_beam_assemble_v2(): Assembly for tapered beam
```

---

## 12. optimizer_comparison.py

```python
"""Optimizer Comparison: COBYLA vs L-BFGS-B"""
import numpy as np
import matplotlib.pyplot as plt
import os; os.makedirs('results', exist_ok=True)
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from quantum_setup import build_structural_hamiltonian
from ansatz import hardware_efficient_ansatz
from vqe_runner import VQEStructuralSolver

# Runs both optimizers from the same initial point
# Generates: convergence curves, error decay, iteration/wall-time comparison
# Saves: results/optimizer_comparison.png, results/optimizer_normalized_error.png
```

---

## 13. validate_fea.py

```python
"""Beam FEA Validation — symmetry, positive definiteness, analytical comparison"""
import numpy as np
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported

E=200e9; I=8.33e-6; rho=7850.0; A=0.01; L=1.0
K, M = assemble_beam(num_elements=2, E=E, I=I, rho=rho, A=A, L_total=L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, num_elements=2)

# Checks: symmetry, positive definiteness, condition number, analytical error
# Mode 1 threshold: <1% error for quantum pipeline readiness
```

---

## 14. validate_truss.py

```python
"""Truss FEA Validation — matrix checks + analytical frequency comparison"""
import numpy as np
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, validate_truss_matrices, analytical_fixed_fixed

# Validates: K/M symmetry, positive definiteness, condition number
# Compares FEA frequencies against analytical fixed-fixed solution
# Uses n_elem=8 for <1% error in mode 1
```

---

## 15. test_convergence.py

```python
"""Mesh convergence study for truss FEA"""
import numpy as np
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, analytical_fixed_fixed

# Tests n_elem = [2, 4, 8, 16, 32, 64]
# Reports Mode 1 FEM vs analytical error for each mesh density
```

---

## 16. test_n_elem.py

```python
"""Qubit count analysis: maps mesh size to required qubits"""
import numpy as np
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, analytical_fixed_fixed

# For n_elem in [3,4,5,6,8]:
#   Reports: free DOFs, padded size, qubits needed, frequency errors
```

---

## 17. generate_presentation.py

```python
"""Generate Presentation Slides for VQA Modal Analysis Project"""
import numpy as np
import matplotlib.pyplot as plt
import os; os.makedirs('results', exist_ok=True)

# Creates matplotlib-based slide deck:
# - slide_00_title.png: Title slide
# - slide_01_problem.png: Problem statement
# - slide_02_quantum_insight.png: Quantum-classical mapping
# - slide_03_results_summary.png: Key results bar charts
# - slide_04_pipeline.png: Pipeline flow diagram
# - slide_08_convergence.png: VQE convergence + optimizer comparison
# - slide_06b_truss_results.png: 1D truss results
# - slide_10_mode_shapes.png: Beam + truss mode shapes
# - slide_11_novel_studies.png: Ill-conditioning + damage detection
# - slide_12_2d_truss.png: 2D Warren truss results
# - slide_18_conclusion.png: Conclusions
```

---

## 18. generate_pdf.py

```python
"""Generate a complete LaTeX document with all source code embedded."""
import os
SRC = r"C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis"
OUT = os.path.join(SRC, "flat", "CODE_COMPLETE.tex")

PYTHON_FILES = [
    ("main.py", "Pipeline Orchestrator"),
    ("fea.py", "Beam Finite Element Analysis"),
    ("truss.py", "1D and 2D Truss Analysis"),
    ("quantum_setup.py", "Hamiltonian Construction"),
    ("ansatz.py", "Quantum Circuit Ansatze"),
    ("vqe_runner.py", "VQE Solver"),
    ("visualize.py", "Beam and Truss Visualizations"),
    ("visualize_truss2d.py", "2D Warren Truss Visualizations"),
    ("novel_study.py", "Ill-Conditioning and Damage Detection"),
    ("optimizer_comparison.py", "COBYLA vs L-BFGS-B"),
    ("validate_fea.py", "Beam FEA Validation"),
    ("validate_truss.py", "Truss FEA Validation"),
    ("test_convergence.py", "Mesh Convergence Study"),
    ("test_n_elem.py", "Qubit Count Analysis"),
    ("generate_presentation.py", "Slide Generator"),
]

# Builds CODE_COMPLETE.tex with lstlisting environments for each file
```

---

## 19. setup_pdf.py

```python
"""Utility to flatten project files into flat/ directory"""
import os, shutil
src = r"C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis"
dst = os.path.join(src, "flat")
os.makedirs(dst, exist_ok=True)
files = [
    "main.py", "fea.py", "truss.py", "quantum_setup.py", "ansatz.py",
    "vqe_runner.py", "visualize.py", "visualize_truss2d.py",
    "novel_study.py", "optimizer_comparison.py", "validate_fea.py",
    "validate_truss.py", "test_convergence.py", "test_n_elem.py",
    "generate_presentation.py"
]
for f in files:
    shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
```

---

## 20. requirements.txt

```
# Core numerical computing
numpy>=1.24.0
scipy>=1.10.0

# Quantum computing framework
qiskit>=1.0.0
qiskit-aer>=0.13.0
qiskit-algorithms>=0.3.0

# Visualization and data
matplotlib>=3.7.0
pandas>=1.5.0
```

---

*End of Codebase — VQA Modal Analysis Project, May 2026*
