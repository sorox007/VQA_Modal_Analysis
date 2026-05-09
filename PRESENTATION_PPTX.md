# VQA Modal Analysis Presentation
## For PowerPoint Import

---

### Slide 1: Title Slide
**VQA Modal Analysis: Quantum Computing for Structural Dynamics**

COEP Technological University  
May 2026

*VQE for Finding Natural Frequencies of Structures*

---

### Slide 2: The Problem - Modal Analysis
**Finding Natural Frequencies and Mode Shapes**

```
Kφ = ω²Mφ
```

Applications:
- Design validation
- Resonance avoidance  
- Structural health monitoring

Current approach: Classical FEA solvers with O(N³) complexity

**Visual:** Insert `results/beam_geometry.png`

---

### Slide 3: The Quantum Insight
**Exact Mathematical Mapping**

```
Structural:  Kφ = ω²Mφ
               ↓
Transform:   H = M⁻¹/²KM⁻¹/²
               ↓
Quantum:     H|ψ⟩ = λ|ψ⟩
```

Both are Hermitian eigenvalue problems — mathematically identical!

---

### Slide 4: VQE Pipeline Architecture
**Implementation Flow**

```
fea.py
  ├─ assemble_beam() → K, M
  ├─ apply_simply_supported_bc() → K_red, M_red
  └─ classical_modal_analysis() → ω_classical

quantum_setup.py
  └─ build_structural_hamiltonian() → H_pauli

vqe_runner.py
  └─ VQEStructuralSolver.solve() → ω_vqe
```

---

### Slide 5: Beam Results - Success
**2-Element Simply-Supported Beam**

| Method | Mode 1 (rad/s) | Error |
|--------|----------------|-------|
| Classical FEA | 1443.49 | - |
| VQE (L-BFGS-B) | 1443.49 | **0.000%** |
| VQE (COBYLA) | 1443.81 | 0.022% |

**Optimizer Performance:**
- L-BFGS-B: 351 iterations
- COBYLA: 2000 iterations

**Visual:** Insert `results/convergence.png`

---

### Slide 6: Higher Modes via Deflation
**Excited State Extraction Method**

1. Solve for Mode n-1 via VQE
2. Build projector P = |ψₙ₋₁⟩⟨ψₙ₋₁|
3. Add penalty to Hamiltonian
4. VQE ground state on new H = Mode n

**Results:**
- Mode 1: 1443.81 rad/s (VQE)
- Mode 2: 6384.87 rad/s (VQE)  
- Mode 3: 16045.25 rad/s (VQE)
- All errors < 0.1% vs classical

---

### Slide 7: Novel Research Contribution #1
**Ill-Conditioning Study**

**Hypothesis:** As condition number increases (slender beams, near-buckling), VQE convergence degrades.

**Implementation:** `tapered_beam_study()` varies L/r ratio and measures:
- Condition number of H matrix
- VQE iterations to convergence
- Error vs classical solution

**Significance:** First study of structural ill-conditioning effects on quantum algorithms.

---

### Slide 8: Novel Research Contribution #3
**Damage Detection / SHM**

**Hypothesis:** Systematic frequency shift detection via VQE has a detection threshold related to structural ill-conditioning.

**Implementation:** `damage_detection_study()` simulates:
- 0-50% stiffness reduction
- Frequency shift detection
- VQE capability vs condition number

**Target Application:** VQE-based structural health monitoring

---

### Slide 9: 2D Warren Truss - Geometry
**From 1D to 2D: Proper Triangular Truss**

**1D "Truss" (flawed):**
- 1 DOF per node (axial only)
- Straight line - essentially a beam

**2D Warren Truss (correct):**
- 2 DOF per node (ux, uy)
- 10 nodes, 17 members
- Triangular web diagonals
- Pinned-roller boundary conditions

**Visual:** Insert `results/truss2d_geometry.png`

---

### Slide 10: 2D Truss Results
**17-DOF System (5 qubits after padding)**

| Mode | Frequency (rad/s) | Frequency (Hz) |
|------|-------------------|--------------|
| 1 | 1221.57 | 194.4 |
| 2 | 1861.82 | 296.3 |
| 3 | 3409.80 | 542.7 |
| 4 | 5719.45 | 910.3 |

**Condition Number:** 171.89 (well-conditioned)

**Visual:** Insert `results/truss2d_mode_shapes.png`

---

### Slide 11: Animation & Visualizations
**Generated Outputs**

1. `beam_geometry.png` - Beam node layout
2. `convergence.png` - VQE cost function plot
3. `frequency_comparison.png` - VQE vs Classical bar chart
4. `truss2d_geometry.png` - 2D truss layout
5. `truss2d_mode_shapes.png` - Deformed mode shapes
6. `truss2d_mode1_animation.gif` - Oscillation animation

---

### Slide 12: Conclusion
**Key Achievements**

✅ **Quantum-Classical Mapping** - Exact transformation from structural to quantum eigenvalue problem

✅ **VQE Accuracy** - < 0.03% error for beam modal analysis

✅ **2D Truss Implementation** - 10 nodes, 17 members, classical FEA validated

✅ **Novel Research Framework** - First study of ill-conditioning effects on VQE

---

### Slide 13: Questions?
**Thank You**

Code: Available in VQA_Modal_Analysis repository  
Contact: [your.email@coep.ac.in]