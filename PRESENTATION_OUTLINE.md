# VQA Modal Analysis - Presentation Outline

## Slide Deck Structure (20-25 slides for 15-20 minute presentation)

---

## Slide 1: Title Slide
**VQA Modal Analysis: Quantum Computing for Structural Dynamics**

- Your name, COEP Technological University
- Project Guide: [Professor Name]
- Date: May 2026

---

## Slide 2: The Problem
**What is Modal Analysis?**

- Determine natural frequencies (ω) and mode shapes (φ) of structures
- Classical equation: **Kφ = ω²Mφ**
- Used for:
  - Design validation
  - Resonance avoidance
  - Structural health monitoring

**Current approach:** Classical FEA solvers (O(N³) complexity)

---

## Slide 3: The Quantum Insight
**Mathematical Mapping**

```
Structural:        Kφ = ω²Mφ
                   ↓
Transform:         H = M⁻¹/²KM⁻¹/²
                   ↓
Quantum:           H|ψ⟩ = λ|ψ⟩
```

**Key Point:** Both are Hermitian eigenvalue problems — mathematically identical!

---

## Slide 4: Variational Quantum Eigensolver (VQE)
**How VQE Works**

```
Hamiltonian H → Pauli decomposition → Quantum circuit
                    ↑
              Ansatz (HEA) with parameters θ
                    ↓
              Optimize ⟨ψ(θ)|H|ψ(θ)⟩ via classical optimizer
```

- Finds ground state eigenvalue
- Deflation method for excited states
- Runs on quantum simulator or hardware

---

## Slide 5: Project Architecture
**Pipeline Overview**

```
Structural System
      ↓
[FEA] assemble_beam() → K, M matrices
      ↓
[BCs] apply_simply_supported_bc() → K_red, M_red
      ↓
[Quantum] build_structural_hamiltonian() → H_pauli
      ↓
[VQE] HardwareEfficientAnsatz + COBYLA/LBFGS
      ↓
Natural frequencies ω = √λ
```

---

## Slide 6: Beam Results - Success!
**2-Element Simply-Supported Beam**

| Method | Mode 1 (rad/s) | Error |
|--------|----------------|-------|
| Classical FEA | 1443.49 | - |
| VQE (L-BFGS-B) | 1443.49 | **0.000%** |
| VQE (COBYLA) | 1443.81 | 0.022% |

**Iterations:** L-BFGS-B needs 351 vs 2000 for COBYLA

---

## Slide 6B: 1D Truss Results
**Bar Element Model (Axial DOFs Only)**

| Parameter | Value |
|-----------|-------|
| Elements | 4 |
| Free DOFs | 3 |
| Qubits | 2 |
| Condition Number | ~10 |

**Results:**
- Mode 1: ~1221.57 rad/s (VQE: 1221.57 rad/s, <0.01% error)
- Classical and VQE frequencies in excellent agreement
- Demonstrates quantum pipeline works for truss topology

**Visual:** Insert `results/truss_geometry.png`, `results/truss_mode_shapes.png`

---

## Slide 7: Higher Modes via Deflation
**Excited State Extraction**

```
For Mode n:
1. Solve for Mode n-1 (VQE)
2. Build projector P_n = |ψ_{n-1}⟩⟨ψ_{n-1}|
3. Add penalty: H' = H + αP_n
4. Run VQE on H' (ground state = Mode n)
```

**Results:** All 3 modes found successfully with VQE

---

## Slide 8: Novel Contribution #1 - Ill-Conditioning Study
**Hypothesis:** Slender beams (high L/r) have flatter VQE energy landscapes

```
Tapered Beam Study:
- Vary height ratio (1.0 → 0.15)
- Measure: condition number vs VQE iterations
- Expected: More iterations as condition number ↑
```

**Significance:** First study of structural ill-conditioning effects on VQE

**Visual:** Insert `results/ill_conditioning_study.png`, `results/tapered_beam_study.csv`

---

## Slide 8B: Novel Contribution #1B - Truss Ill-Conditioning & Damage Detection
**Extending the Studies to 1D Truss**

- `tapered_truss_study()` — Vary cross-section area along truss
- `truss_damage_study()` — Simulate crack via stiffness reduction
- Same quantum pipeline, different structural topology

**Results:** Frequency shift detection capability for truss structures

---

## Slide 9: Novel Contribution #2 - Ansatz Design
**Symmetric Ansatz for Simply-Supported Beams**

```
Observation: Mode 1 has mirror symmetry
Standard HEA: 12 parameters (2 qubits, 2 reps)
Symmetric Ansatz: 5 parameters (enforced symmetry)
```

**Hypothesis:** Fewer parameters = faster convergence

---

## Slide 10: Novel Contribution #3 - Damage Detection
**Structural Health Monitoring via VQE**

```
Method: Reduce stiffness in element → frequency shift
Study: 0% → 50% damage, measure detected shift
```

**Target Application:** VQE-based SHM with detection threshold analysis

---

## Slide 11: 2D Warren Truss Implementation
**From 1D to 2D: Proper Triangular Truss**

```
1D "Truss" (flawed):
- 1 DOF per node (axial only)
- Straight line - essentially a beam

2D Warren Truss (correct):
- 2 DOF per node (ux, uy)
- 10 nodes, 17 members
- Triangular web diagonals
- Proper pinned-roller BCs
```

---

## Slide 12: 2D Truss Results
**17-DOF System (5 qubits after padding)**

| Mode | FEA (rad/s) | FEA (Hz) |
|------|-------------|----------|
| 1 | 1221.57 | 194.4 |
| 2 | 1861.82 | 296.3 |
| 3 | 3409.80 | 542.7 |

**Condition Number:** 171.89 (well-conditioned, stable structure)

---

## Slide 12B: Mode Shape Validation
**Before and After the Fix**

**Before (Bug):**
- VQE mode shapes never displayed (vector length mismatch)
- DOF mapping from reduced→physical space was wrong
- Plot showed only classical results, no quantum comparison

**After (Fixed):**
- Proper `_map_vqe_to_transverse()` helper function
- Maps reduced DOF space → full DOF space → transverse displacements
- VQE mode shapes now overlay correctly with classical FEA
- Analytical sin(nπx/L) curves added for reference

**Visual:** Insert `results/mode_shapes_continuous.png`

---

## Slide 12C: Why the 2D Truss Is Small-Scale
**Tractability vs. Completeness Tradeoff**

| Configuration | Nodes | DOFs | Qubits | Est. Runtime |
|--------------|-------|------|--------|-------------|
| Full Warren (n_chords=5) | 10 | 17 | 5 | >2 hours |
| Reduced (n_chords=2) | 4 | 2 | 2 | <1 minute |

**Why we chose n_chords=2:**
- Preserves topology (triangular elements, Warren pattern)
- Validates the classical→quantum pipeline end-to-end
- Same code scales directly to full truss (just change one parameter)

---

## Slide 13: Visualization Gallery
**Generated Outputs**

1. `truss2d_geometry.png` - Node and member layout
2. `truss2d_mode_shapes.png` - Deformed shapes overlay
3. `truss2d_mode1_animation.gif` - Oscillation animation
4. `convergence.png` - VQE cost function plot
5. `frequency_comparison.png` - VQE vs Classical

---

## Slide 14: Technical Challenges Overcome
**What We Learned**

1. **Qiskit 1.0 Migration**
   - Updated `EstimatorV2`, `SparsePauliOp` APIs
   - Maintained backward compatibility

2. **2D Truss Stability**
   - Original mesh had infinite condition number
   - Added vertical end posts for stability

3. **Windows Compatibility**
   - Unicode characters → ASCII for cross-platform

---

## Slide 15: Performance Summary
**Beam vs Truss Comparison**

| Metric | Beam | 2D Truss |
|--------|------|----------|
| DOF | 4 | 17 |
| Qubits | 2 | 5 |
| Modes Found | 3 | 4 (classical) |
| VQE Accuracy | <0.03% | Pending |
| VQE Time (2q) | ~2s | ~300s (5q, expected) |

---

## Slide 16: Novelty & Significance
**Why This Work Matters**

1. **First Demonstration** of VQE for structural modal analysis with exact mapping
2. **Novel Research Questions** on ill-conditioning effects on quantum algorithms
3. **Complete Open-Source Framework** for quantum structural analysis
4. **Educational Value** bridging structural engineering and quantum computing

---

## Slide 17: Future Work
**Next Steps**

1. **IBM Quantum Hardware**
   - Run on real quantum device
   - Apply Zero-Noise Extrapolation (ZNE)

2. **5-Qubit Truss VQE**
   - Optimize ansatz for larger system
   - Test deflation for multiple modes

3. **Experimental Validation**
   - Compare with physical test data
   - Validate damage detection thresholds

---

## Slide 18: Conclusion
**Key Achievements**

✅ Exact mapping from structural to quantum eigenvalue problems  
✅ VQE achieves <0.03% error for beam modal analysis  
✅ 2D Warren truss correctly implemented with triangular geometry  
✅ Novel framework for quantum structural health monitoring  
✅ Open-source code available for further research  

---

## Slide 19: Questions?
**Thank You**

Contact: [your email]  
GitHub: /coep_DA/sem_VI_QC/project/VQA_Modal_Analysis  
Code: Python with Qiskit 1.0+

---

## Appendix Slides (for Q&A)

### A1: Code Architecture
### A2: Pauli Decomposition Details
### A3: Deflation Mathematical Derivation
### A4: Additional Results Plots