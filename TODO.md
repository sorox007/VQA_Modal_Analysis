# TODO - 2D Warren Truss VQA Modal Analysis

**Project:** VQA Modal Analysis  
**Location:** `C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis`  
**Date:** 2026-05-07  
**Status:** IN PROGRESS

---

## Implementation Plan (Updated 2026-05-07)

Replacing 1D axial truss model with proper 2D Warren Truss (triangular members, 2 DOF per node).

### Truss Specifications
| Parameter | Value |
|---|---|
| Type | 2D Warren Truss |
| Panels | 4 (0.5m each) |
| Span | 2.0 m |
| Height | 0.4 m |
| Nodes | 10 (5 bottom + 5 top) |
| Members | 17 (4 bottom + 4 top + 2 verticals + 7 diagonals) |
| Material | Steel (E=200 GPa, rho=7850 kg/m³, A=10 cm²) |
| BCs | Pinned-Roller (pinned at B0, roller at B4) |
| Free DOFs | 17 (after BCs) → 5 qubits (32×32 matrix) |

---

## Tasks

### Phase 1: Core FEA Module ✅
- [x] `truss.py` - Full rewrite with 2D truss formulation
  - [x] 4×4 element stiffness matrix (orientation-dependent)
  - [x] 4×4 element mass matrix (consistent/lumped)
  - [x] Warren truss mesh generation (10 nodes, 17 members)
  - [x] Global matrix assembly (20×20 → 17×17 after BCs)
  - [x] Pinned-roller boundary conditions
  - [x] Classical modal analysis via scipy.linalg.eigh
  - [x] Validation: K symmetric, M symmetric, K_red positive definite
  - [x] Test: Natural frequencies valid (Mode 1: 1221.57 rad/s)

### Phase 2: Visualization Module ✅
- [x] `visualize_truss2d.py` - Created new module with 2D truss plots
  - [x] `plot_truss2d_geometry()` - Node and member layout
  - [x] `plot_truss2d_mode_shapes()` - Deformed shape overlay
  - [x] `animate_truss2d_mode()` - GIF animation of oscillating truss
  - [x] `plot_truss2d_frequency_comparison()` - Frequency bar chart
  - [x] Test: Geometry plot, mode shape plots generated successfully

### Phase 3: Main Pipeline Update 🔄
- [ ] `main.py` - Overhaul for 2D Warren Truss
  - [ ] Generate truss mesh (call `generate_warren_truss_mesh()`)
  - [ ] Assemble K, M (call `assemble_truss2d()`)
  - [ ] Apply pinned-roller BCs
  - [ ] Classical modal analysis (reference)
  - [ ] Build Hamiltonian (5 qubits, 32×32 matrix)
  - [ ] Run VQE on Aer simulator
  - [ ] Extract multiple modes via deflation
  - [ ] Generate all visualizations

### Phase 4: Validation Script 🔄
- [ ] `validate_truss_2d.py` - Comprehensive validation
  - [ ] K, M symmetry checks
  - [ ] Positive definiteness verification
  - [ ] Condition number reporting
  - [ ] Physical scale checks (K[0,0] ~ EA/L, etc.)
  - [ ] Comparison with reference FEA software (target: <2% error)

### Phase 5: End-to-End Test & VQE Verification 🔄
- [ ] Run full pipeline
  - [ ] Verify classical FEA results
  - [ ] Check VQE convergence (5 qubits, COBYLA/L-BFGS-B)
  - [ ] Compare VQE vs Classical frequencies (<2% error target)
  - [ ] Test higher mode extraction (deflation)
  - [ ] Generate all output files (CSVs, PNGs, GIFs)

---

## Reused Modules (No Changes Needed)
- ✅ `quantum_setup.py` - `build_structural_hamiltonian()` works with any K, M
- ✅ `vqe_runner.py` - `VQEStructuralSolver` is problem-agnostic (Qiskit 1.0+)
- ✅ `ansatz.py` - All ansatzes independent of problem type (Qiskit 1.0+)

---

## Notes
- **Qiskit Version:** 1.0+ (qiskit>=1.0.0, qiskit-aer>=0.13.0, qiskit-algorithms>=0.3.0)
- **Hamiltonian Size:** 17 DOF → pad to 32×32 for 5 qubits
- **Pauli Terms:** ~32² = 1024 max (far fewer for sparse structural matrices)
- **Optimizer:** COBYLA (maxiter=500) for clean simulation
- **Hardware:** IBM Quantum (per VQA_Modal_Analysis.md Section 11, 20 min/month budget)

---

## File Summary

### Created/Overhauled
1. `truss.py` - 2D Warren Truss FEA (~300 lines) ✅
2. `visualize_truss2d.py` - 2D truss visualization (~300 lines) ✅

### To Modify
3. `main.py` - Overhaul for truss pipeline (~150 lines) 🔄

### To Create
4. `validate_truss_2d.py` - Validation script (~80 lines) 🔄

### Reused (Unchanged)
5. `quantum_setup.py` ✓
6. `vqe_runner.py` ✓
7. `ansatz.py` ✓

---

## Expected Results

| Metric | Target |
|---|---|
| Classical FEA vs Reference | < 2% error |
| VQE vs Classical (Mode 1) | < 2% error |
| VQE Convergence (5 qubits) | < 300 iterations |
| Condition Number (K_red) | ~100-200 (well-conditioned) |
| Modes Extracted | 6+ via deflation |
