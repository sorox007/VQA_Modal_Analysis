# Truss Analysis Implementation Plan
## VQA Modal Analysis Project

**Current Directory:** `C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis`  
**Date:** 2026-05-06

---

## 1. Overview

Current project implements VQE-based modal analysis for **Euler-Bernoulli beams**. Need to add **truss (bar element)** analysis with identical pipeline integration.

### Existing Architecture Pattern
```
fea.py (beam):   element_fn() → assemble() → apply_bc() → classical_solve()
quantum_setup.py:          K, M → H = M^(-1/2)KM^(-1/2) → normalize → Pauli
vqe_runner.py:          H_pauli → VQE solver (COBYLA/SPSA/LBFGS) → eigenvalues
ansatz.py:          HEA / Symmetric / Minimal circuits
novel_study.py:      Condition number & damage detection studies
visualize.py:        All plotting functions
main.py:             Full pipeline runner
```

**Key Insight:** Quantum pipeline is 100% reusable — only need new truss FEA code.

---

## 2. Implementation Components

### File 1: `truss.py` (NEW)
Follows `fea.py` pattern exactly.

**Functions:**
```python
def truss_element_stiffness(EA, L):
    """2×2 stiffness matrix: (EA/L)*[[1,-1],[-1,1]]"""

def truss_element_mass(rhoA, L, lumped=False):
    """2×2 mass matrix: consistent=(ρAL/6)*[[2,1],[1,2]], lumped=(ρAL/2)*I"""

def assemble_truss(num_elements, E, A, rho, L_total):
    """Assemble global K, M (size: n+1 × n+1, n=num_elements)"""

def apply_fixed_fixed_bc(K, M):
    """Remove DOF at both ends (indices 0 and n)"""
    Returns K_red, M_red, free_dofs

def apply_fixed_free_bc(K, M):
    """Remove DOF at fixed end (index 0)"""
    Returns K_red, M_red, free_dofs

def classical_modal_analysis(K_red, M_red):
    """scipy.linalg.eigh — identical to beam"""

def analytical_fixed_fixed(E, A, rho, L, n_modes=4):
    """ωₙ = (nπ/L)*√(E/ρ)"""

def analytical_fixed_free(E, A, rho, L, n_modes=4):
    """ωₙ = (2n-1)π/(2L)*√(E/ρ)"""
```

### File 2: `validate_truss.py` (NEW)
Adapted from `validate_fea.py`.

**Checks:**
- [ ] K, M symmetry
- [ ] Positive definiteness (K, M eigenvalues > 0)
- [ ] Condition numbers
- [ ] Physical scale: K[0,0] ~ EA/L, M[0,0] ~ ρAL/3
- [ ] Mode 1 analytical comparison (< 1% error)

### File 3: `main.py` (MODIFY)
Add truss pipeline section.

```python
# TRUSS ANALYSIS PIPELINE
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis

E, A, rho, L = 200e9, 0.01, 7850, 1.0
n_elem = 4  # Need ≥4 for 2 qubits after BCs

K_t, M_t = assemble_truss(n_elem, E, A, rho, L)
K_t_red, M_t_red, _ = apply_fixed_fixed_bc(K_t, M_t)
omega_t_classical, _ = classical_modal_analysis(K_t_red, M_t_red)

# Quantum pipeline (reuses existing code!)
H_norm_t, ham_t, _, H_scale_t = build_structural_hamiltonian(K_t_red, M_t_red)
ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)
solver = VQEStructuralSolver(ham_t, ansatz, optimizer_name='COBYLA',
                              maxiter=500, H_scale=H_scale_t)
result_t = solver.solve()
```

### File 4: `novel_study.py` (MODIFY)
Add truss-specific studies.

```python
def tapered_truss_study(E, A, rho, L, area_ratios, n_elements=4):
    """Vary cross-section linearly, track condition # vs VQE convergence"""

def truss_damage_study(E, A, rho, L, damage_levels, n_elements=4):
    """Reduce A in elements, detect frequency shifts via VQE"""
```

### File 5: `visualize.py` (MODIFY)
Add truss plotting functions.

```python
def plot_truss_geometry(n_elem, L):
    """Horizontal bar with node labels → results/truss_geometry.png"""

def plot_truss_mode_shapes(n_elem, L, modes, ...):
    """Axial displacement profiles"""

def plot_truss_frequency_comparison(vqe_freqs, classical_freqs, labels):
    """VQE vs classical bar chart"""
```

### File 6: `README.md` (MODIFY)
Add truss section:
- Quick start example
- Module reference (`truss.py` functions)
- Results/metrics

---

## 3. Technical Details

### Truss Element Theory (1D Bar)
| Quantity | Formula |
|---|---|
| **DOFs/node** | 1 (axial displacement u) |
| **Stiffness** | k_e = (EA/L)[[1,-1],[-1,1]] |
| **Mass (consistent)** | m_e = (ρAL/6)[[2,1],[1,2]] |
| **Mass (lumped)** | m_e = (ρAL/2)[[1,0],[0,1]] |
| **Natural freq (fixed-fixed)** | ωₙ = (nπ/L)√(E/ρ) |
| **Natural freq (fixed-free)** | ωₙ = (2n-1)π/(2L)√(E/ρ) |

### DOF Comparison
| System | Elements | Total DOF | After BCs | Qubits Needed |
|---|---|---|---|---|
| **Beam** | 2 | 6 → 4 | 4 | 2 |
| **Truss** | 2 | 3 → 1 | 1 | 1 (too small) |
| **Truss** | 4 | 5 → 3 | 3 | 2 ✓ |
| **Truss** | 5 | 6 → 4 | 4 | 2 ✓ |

**Decision:** Use `n_elem = 4` or `5` for fair comparison (2 qubits after BCs).

### Assembly Pattern (Identical to Beam)
```python
ndof = n_elements + 1  # Truss (1 DOF/node)
# vs
ndof = 2*(n_elements + 1)  # Beam (2 DOF/node)

for elem in range(n_elements):
    dofs = [elem, elem+1]  # Truss
    # vs
    dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]  # Beam
    
    for i_local, i_global in enumerate(dofs):
        for j_local, j_global in enumerate(dofs):
            K_global[i_global, j_global] += k_e[i_local, j_local]
```

### Boundary Conditions
| Type | Removed DOFs | Use Case |
|---|---|---|
| **Fixed-Fixed** | indices 0, n | Simply-supported beam analogue |
| **Fixed-Free** | index 0 | Cantilever beam analogue |

---

## 4. Integration Points

### Zero Changes Required
- ✅ `quantum_setup.py` — `build_structural_hamiltonian(K_red, M_red)` works with ANY K, M
- ✅ `vqe_runner.py` — `VQEStructuralSolver` takes any Hamiltonian
- ✅ `ansatz.py` — All ansatzes independent of problem type
- ✅ Classical solver — `scipy.linalg.eigh` is universal

### Reuse Pattern
```python
# Beam pipeline
K_red, M_red = apply_simply_supported_bc(*assemble_beam(...))
result = VQEStructuralSolver(build_structural_hamiltonian(...), ...).solve()

# Truss pipeline (IDENTICAL below quantum_setup)
K_red, M_red = apply_fixed_fixed_bc(*assemble_truss(...))
result = VQEStructuralSolver(build_structural_hamiltonian(...), ...).solve()
```

---

## 5. Verification Checklist

### Unit Tests
- [ ] Truss element stiffness: hand-calculated 2×2 matrix
- [ ] Truss element mass: hand-calculated 2×2 matrix
- [ ] Assembly: symmetry, correct DOF mapping
- [ ] BCs: correct rows/columns removed

### Validation
- [ ] K, M symmetric
- [ ] K, M positive definite
- [ ] Condition number reasonable
- [ ] Physical scale checks
- [ ] Mode 1 matches analytical (< 1%)

### Quantum Pipeline
- [ ] Hamiltonian builds (Hermitian, normalized)
- [ ] VQE converges (< 5% error)
- [ ] Excited states via deflation work

### Integration
- [ ] `main.py` runs without errors
- [ ] Both beam and truss results printed
- [ ] Visualizations generate

---

## 6. Expected Results

### Performance (n_elem=4, 2 qubits)
| Metric | Beam | Truss |
|---|---|---|
| **FEA Error (Mode 1)** | < 1% | < 1% |
| **VQE Error (Mode 1)** | < 2% | < 5% |
| **Condition Number** | ~10² (slender) | ~10¹ (better) |
| **VQE Iterations** | ~100-200 | ~50-100 (faster) |

### Why Truss Should Converge Faster
1. **Simpler physics**: Axial only (no bending moments)
2. **Better conditioning**: Less slenderness effect
3. **Smaller matrices**: Fewer operations per VQE evaluation
4. **Smoother landscape**: Flatter energy surface?

---

## 7. Tasks Breakdown

### Phase 1: Core FEA (1 day)
- [ ] `truss.py` implementation
- [ ] `validate_truss.py` implementation
- [ ] Unit test verification

### Phase 2: Integration (0.5 day)
- [ ] Update `main.py`
- [ ] Test VQE convergence
- [ ] Verify excited states

### Phase 3: Studies & Viz (1 day)
- [ ] Add tapered truss study
- [ ] Add damage detection study  
- [ ] Add visualization functions

### Phase 4: Documentation (0.5 day)
- [ ] Update README
- [ ] Test full pipeline
- [ ] Generate results

**Total:** ~3 days

---

## 8. Risk & Mitigation

| Risk | Mitigation |
|---|---|
| Too few DOFs | Use n_elem = 4-5 |
| Rigid body modes | Use fixed-fixed/fixed-free BCs |
| Mass matrix issues | Verify positive definiteness |
| Integration bugs | Keep truss module independent |
| Validation fails | Analytical formulas verified |

---

## 9. Files Summary

### To Create
1. `truss.py` — ~100 lines
2. `validate_truss.py` — ~50 lines

### To Modify
3. `main.py` — +40 lines (truss section)
4. `novel_study.py` — +60 lines (2 studies)
5. `visualize.py` — +80 lines (3 plots)
6. `README.md` — +100 lines (truss section)

### No Changes Needed
7. `quantum_setup.py` ✓
8. `vqe_runner.py` ✓
9. `ansatz.py` ✓
10. `fea.py` ✓

**Total new code:** ~200 lines  
**Total modified:** ~280 lines  
**Reused:** ~700+ lines

---

## 10. References

- Beam pattern: `fea.py`
- Quantum conversion: `quantum_setup.py`
- VQE solver: `vqe_runner.py`
- Validation pattern: `validate_fea.py`
- Study pattern: `novel_study.py`
