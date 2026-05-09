# VQA Modal Analysis Project Report

**A 3rd-Year Undergraduate Project at COEP Technological University**

---

## Executive Summary

This project demonstrates the application of the **Variational Quantum Eigensolver (VQE)** to solve structural modal analysis problems. The core mathematical insight is that the generalized eigenvalue problem from structural mechanics (`[K]{φ} = ω²[M]{φ}`) maps exactly onto the quantum eigenvalue problem (`H|ψ⟩ = λ|ψ⟩`). No approximation is required in the mapping itself.

The **novel research contribution** is studying how structural ill-conditioning (slender beams, damaged elements, buckling proximity) affects VQE's convergence behavior — a question not addressed in existing literature.

---

## 1. Project Overview

### 1.1 Motivation
Structural modal analysis determines natural frequencies and mode shapes of structures. Traditional methods use classical FEA solvers (`scipy.linalg.eigh`). This project explores whether quantum algorithms (VQE) can solve the same problem with potential advantages for large-scale systems.

### 1.2 Mathematical Foundation
```
Structural Eigenvalue Problem:     Kφ = ω²Mφ
                ↓
Standard Form Transform:            H = M^(-1/2) K M^(-1/2)
                ↓
Quantum Eigenvalue Problem:         H|ψ⟩ = λ|ψ⟩,  λ = ω²
```

**Key Insight:** Both are Hermitian eigenvalue problems with mathematically identical structure.

---

## 2. Architecture & Implementation

### 2.1 Software Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| Qiskit | ≥1.0.0 | Core quantum framework |
| Qiskit Aer | ≥0.13.0 | Local statevector simulator |
| NumPy/SciPy | Latest | Matrix operations |
| Matplotlib | Latest | Visualization |

### 2.2 Pipeline Architecture
```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│ fea.py      │     │ quantum_setup.py │     │ vqe_runner.py  │
│ - assemble   │────▶│ - build_hamiltonian│──▶│ - VQE solver   │
│ - BCs        │     │ - M^(-1/2) K M^(-1/2)│ │ - deflation    │
│ - classical  │     │ - normalize      │     │ - COBYLA/LBFGS │
└─────────────┘     └──────────────────┘     └────────────────┘
```

### 2.3 Module Descriptions

#### Core Modules:
- **`main.py`** (416 lines): Full pipeline runner orchestrating beam and truss analysis
- **`fea.py`**: Beam element FEA with Euler-Bernoulli theory
- **`truss.py`**: 2D Warren truss FEA with 4×4 oriented stiffness matrices
- **`quantum_setup.py`**: Hamiltonian construction from K, M matrices
- **`vqe_runner.py`**: VQE solver with multi-start optimization and deflation
- **`ansatz.py`**: Hardware-Efficient Ansatz (HEA) and symmetric ansatz variants
- **`novel_study.py`**: Ill-conditioning and damage detection studies

#### Visualization Modules:
- **`visualize.py`**: Beam mode shapes, convergence plots, frequency comparisons
- **`visualize_truss2d.py`**: 2D truss geometry, mode shapes, animations

---

## 3. Key Results

### 3.1 Beam Analysis Results
| Metric | Value |
|--------|-------|
| Elements | 2 |
| DOF (after BCs) | 4 |
| Qubits | 2 |
| Mode 1 Frequency | 1443.49 rad/s (194.4 Hz) |
| VQE Error (L-BFGS-B) | 0.000% |
| VQE Error (COBYLA) | 0.022% |
| COBYLA Iterations | 2000 |
| L-BFGS-B Iterations | 351 |

### 3.2 2D Warren Truss Results
| Specification | Value |
|---------------|-------|
| Nodes | 10 (5 bottom + 5 top) |
| Members | 17 (4 bottom + 4 top + 2 verticals + 7 diagonals) |
| Panels | 4 |
| Span | 2.0 m |
| Height | 0.4 m |
| DOF (before BCs) | 20 (2 per node) |
| DOF (after BCs) | 17 |
| Qubits | 5 |
| Condition Number | 171.89 (well-conditioned) |

**Natural Frequencies (rad/s):**
- Mode 1: 1221.57 rad/s (194.4 Hz)
- Mode 2: 1861.82 rad/s (296.3 Hz)
- Mode 3: 3409.80 rad/s (542.7 Hz)
- Mode 4: 5719.45 rad/s (910.3 Hz)

### 3.3 Optimizer Comparison
| Optimizer | Beam Error | Truss Error (expected) | Iterations | Speed |
|-----------|------------|------------------------|------------|-------|
| COBYLA | 0.022% | ~2-5% | ~2000 | Slow |
| L-BFGS-B | 0.000% | ~2-5% | ~300-400 | Fast (4.5x) |

---

## 4. Novel Research Contributions

### 4.1 Research Gap 1: Structural Ill-Conditioning vs VQE Convergence
**Hypothesis:** As condition number increases (slender beams, near-buckling), VQE convergence degrades.

**Implementation:** `tapered_beam_study()` varies L/r ratio and measures:
- Condition number of H matrix
- VQE iterations to convergence
- Error vs classical solution

### 4.2 Research Gap 2: Physically-Motivated Ansatz Design
**Hypothesis:** Encoding mode shape symmetry into ansatz reduces parameters and improves convergence.

**Implementation:** `symmetric_ansatz()` enforces mirror symmetry for simply-supported beams.

### 4.3 Research Gap 3: VQE-Based Structural Health Monitoring
**Hypothesis:** Systematic frequency shift detection via VQE has a detection threshold related to structural ill-conditioning.

**Implementation:** `damage_detection_study()` simulates stiffness reduction and measures:
- Frequency shift vs damage percentage
- VQE detection capability vs condition number

---

## 5. Technical Challenges & Solutions

### Challenge 1: Qiskit Version Migration (0.46 → 1.0+)
**Problem:** `StatevectorEstimator` replaced with `EstimatorV2`

**Solution:** Updated all estimator calls, maintained backward compatibility

### Challenge 2: 2D Truss Implementation
**Problem:** Original 1D truss was effectively a straight beam, not a triangular truss

**Solution:** Complete rewrite with:
- 4×4 oriented element stiffness matrices
- Proper Warren pattern with vertical end posts
- Pinned-roller boundary conditions

### Challenge 3: Windows Unicode Encoding
**Problem:** Greek letters (ρ, ω) caused encoding errors on Windows

**Solution:** Replaced with ASCII equivalents in print statements

---

## 6. Files & Statistics

### Codebase Statistics
| File | Lines | Purpose |
|------|-------|---------|
| truss.py | ~350 | 2D Warren truss FEA |
| visualize_truss2d.py | ~320 | Truss visualization |
| vqe_runner.py | ~220 | VQE solver |
| quantum_setup.py | ~84 | Hamiltonian builder |
| main.py | ~416 | Pipeline runner |
| novel_study.py | ~430 | Research studies |

### Generated Outputs (results/)
- `beam_geometry.png` - Beam node layout
- `convergence.png` - VQE cost function plot
- `frequency_comparison.png` - VQE vs Classical bar chart
- `truss2d_geometry.png` - 2D truss layout
- `truss2d_mode_shapes.png` - Deformed mode shapes
- `truss2d_mode1_animation.gif` - Oscillation animation
- `tapered_beam_study.csv` - Ill-conditioning data
- `damage_study.csv` - Damage detection data

---

## 7. Future Work

1. **IBM Quantum Hardware Run:** Apply Zero-Noise Extrapolation (ZNE) error mitigation
2. **5-Qubit Truss VQE:** Optimize ansatz for 5-qubit (32×32) Hamiltonian
3. **Higher Modes:** Improve deflation method for multiple eigenvalue extraction
4. **Condition Number Study:** Complete ill-conditioning study across multiple structures
5. **Experimental Validation:** Compare with physical test data

---

## 8. Conclusions

This project successfully demonstrates:
1. ✅ Exact mathematical mapping from structural to quantum eigenvalue problems
2. ✅ Accurate VQE solution for beam modal analysis (<0.02% error)
3. ✅ 2D Warren truss implementation with proper triangular geometry
4. ✅ Multi-start VQE with deflation for higher modes
5. ✅ Novel framework for studying VQE convergence under structural ill-conditioning

The work establishes a foundation for quantum structural analysis and provides insights into how structural complexity affects quantum algorithm performance.