# Comprehensive Fix Plan — VQA Modal Analysis Project

**Date:** 2026-05-12
**Status:** Awaiting user confirmation

---

## Issue Summary

Six categories of changes requested:
1. Optimizer comparison graph bug (LBFGS output shown under COBYLA)
2. Include 1D truss study
3. Restore ill-conditioning study
4. Fix beam mode shape visualization
5. Explain why 2D truss was reduced to smaller example
6. Presentation plan after all changes

---

## Issue #1: Optimizer Comparison Bug

### Root Cause Analysis

**File: `main.py` lines 65-89**

The beam section creates THREE solver instances:
- `solver` (L_BFGS_B) → `result_hea`  ← labeled "HEA" but uses L_BFGS_B
- `solver_cobyla` (COBYLA) → `result_cobyla`
- `solver_lbfgs` (L_BFGS_B) → `result_lbfgs`

`result_hea` and `result_lbfgs` are both from L_BFGS_B — redundant. The `plot_dual_convergence` and comparison summary do use `result_cobyla` vs `result_lbfgs` correctly, but the first VQE run (`result_hea`) is wasted and confusing. There's also no clear "HEA vs COBYLA" comparison — it's actually "L_BFGS-B vs COBYLA" both times.

**File: `optimizer_comparison.py`** — This standalone script is actually correct (run separately). The bug is specifically in how `main.py` sets up the comparison.

### Fix (main.py, lines 65-89)

Replace the redundant 3-solver setup with a clean 2-solver comparison:
- Keep one L_BFGS-B run as the primary VQE result (stored in `result_hea`)
- Run COBYLA separately for comparison
- Both fed into `plot_dual_convergence`

Also fix: In the comparison table (lines 200-208), the column headers say "Beam" and "Truss" but the L_BFGS-B beam error is shown under "Beam" and the COBYLA beam error is shown under "Truss" column. This IS the bug — the comparison table mixes up which optimizer result goes where.

**Fix:** Ensure the table correctly shows COBYLA results under "COBYLA" column and L_BFGS-B under "L_BFGS-B" column.

### Fix (optimizer_comparison.py)

The standalone script is correct. No changes needed. But add a header/legend to clarify which optimizer produced which result.

---

## Issue #2: Include 1D Truss Study

### Current State

The 1D truss IS present in `main.py` (lines 111-189) but it uses the simple 1D bar element model (1 DOF/node, axial only). This was the ORIGINAL implementation before the 2D Warren truss was added.

The 1D truss section:
- Uses `assemble_truss()` → 1D bar elements
- Uses `apply_fixed_fixed_bc()` → removes end DOFs
- Runs VQE with COBYLA and L_BFGS_B
- Shows comparison

### Fix

The 1D truss study is already included. To make it more prominent and complete:
1. Add a clear section header "1D Truss Study (Bar Element)" in main.py
2. Add a geometry visualization call: `plot_truss_geometry(n_elem, L)` from visualize.py
3. Add mode shape visualization: `plot_truss_mode_shapes()` from visualize.py
4. Add frequency comparison: `plot_truss_frequency_comparison()` from visualize.py
5. Add convergence comparison for the 1D truss optimizer run

---

## Issue #3: Restore Ill-Conditioning Study

### Current State

`novel_study.py` already has:
- `tapered_beam_study()` — varies beam taper ratio, measures condition number vs VQE performance
- `truss_damage_study()` — simulates damage via stiffness reduction
- `tapered_truss_study()` — varies truss cross-section

`visualize.py` already has:
- `plot_ill_conditioning_study()` — plots condition number vs error/iterations
- `plot_damage_detection()` — plots frequency shift vs damage level

In `main.py`, these are commented out (lines 221-222, 244-245). The `visualize_truss2d.py` has no ill-conditioning plots.

### Fix (main.py lines 216-222)

Uncomment the novel study imports and add calls. But first, fix the `tapered_beam_study` function — it currently has a bug where `classical_modal_analysis` is called from `fea.py` but the import at line 4 only imports it once. Let me verify:

```python
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported
```

This is correct. The function definitions in `novel_study.py` also import what they need. The main issue is that the calls are commented out.

**New main.py section for novel studies:**

1. **Beam ill-conditioning study:** Call `tapered_beam_study()` with a range of taper ratios (1.0 down to 0.2), then plot with `plot_ill_conditioning_study(df_beam)`.

2. **Beam damage detection study:** Call `damage_detection_study()` with damage levels [0.0, 0.1, 0.2, 0.3, 0.5], then plot with `plot_damage_detection(df_damage)`.

3. **Truss ill-conditioning study:** Call `tapered_truss_study()` and `truss_damage_study()` — these exist in novel_study.py but are not called anywhere. Add them.

**Important:** The novel studies take significant time (~2000 iterations each). We should add a flag `RUN_NOVEL_STUDIES = False` that the user can set to True when they want to run them.

---

## Issue #4: Fix Beam Mode Shape Visualization

### Root Cause Analysis

**File: `visualize.py`, `plot_mode_shapes_continuous()` (lines 73-154)**

Bug 1: **VQE mode shapes never plotted.** The code checks:
```python
if len(u_vqe) <= len(x_plot):
```
For 2-element beam: `u_vqe` has 4 components (VQE state vector), `x_plot` has 3 points (node positions). Since 4 > 3, the VQE mode shape is NEVER drawn.

Bug 2: **Incorrect mapping from reduced DOF space to physical space.** The function tries to back-map free DOFs to full DOF positions but doesn't account for the fact that VQE returns a state vector in the REDUCED space (matching free DOFs only), not the full space.

Bug 3: **Only transverse displacement shown, but VQE state vector includes all DOF types.** For beam, free DOFs alternate between transverse (v) and rotational (θ). The code only extracts every-other-element of the VQE state vector, missing the correspondence.

### Fix

Rewrite `plot_mode_shapes_continuous()` to:

1. **For classical mode shapes:** Map from reduced DOF space back to full space using `free_dofs`, then extract only the transverse DOFs (even indices in the full DOF numbering: 0, 2, 4, ...) for plotting. This is already done correctly.

2. **For VQE mode shapes:** The VQE returns a state vector with components corresponding to the computational basis states. For an N-dimensional reduced system padded to 2^n qubits, the first N components of the VQE state correspond to the N free DOFs. So:
   - Extract the first `len(free_dofs)` components from the VQE state
   - Map them back using `free_dofs` to get the full DOF vector
   - Extract transverse DOFs (even indices) for plotting
   - Plot alongside classical

3. **Fix the x-axis positions:** Use the actual node positions: `x_plot = [i * L_total / n_elem for i in range(n_elem + 1)]`

4. **Add analytical mode shapes** for simply-supported beam: sin(nπx/L) curves.

**Corrected mapping code:**
```python
def _map_vqe_to_physical(vqe_state, free_dofs, n_full_dof):
    """Map VQE state vector back to full DOF space."""
    full = np.zeros(n_full_dof)
    n_vqe = min(len(vqe_state), len(free_dofs))
    full[free_dofs[:n_vqe]] = vqe_state[:n_vqe]
    return full
```

Then extract transverse DOFs:
```python
transverse_indices = [i for i in range(n_full_dof) if i % 2 == 0]  # Even DOFs = transverse
u_vqe_physical = _map_vqe_to_physical(u_vqe, free_dofs, 2*n_elem+2)
u_vqe_transverse = u_vqe_physical[transverse_indices]
```

**File: `main.py` (lines 250-260)**

Fix the VQE mode shape list:
```python
vqe_modes = [result_hea['mode_shape']]
vqe_modes.extend([modes_classical[:, i] for i in range(1, 3)])  # These are already in reduced space
```

The classical modes from `modes_classical` are already correctly in reduced space (columns of the eigenvector matrix). The VQE mode shape needs proper mapping as described above.

---

## Issue #5: Explain Why 2D Truss Was Reduced to Smaller Example

### Context

From `PLAN.md`, the ORIGINAL 2D Warren truss design:
- 10 nodes, 17 members
- 17 free DOFs after pinned-roller BCs
- Required 5 qubits (32×32 matrix)
- Would take extremely long VQE simulation time

The current implementation uses n_chords=2:
- 4 nodes, 5 members
- 2 free DOFs → pad to 4×4 (2 qubits)
- Runs in seconds on simulator

### Fix (documentation only — add comment block)

In `main.py` lines 270-272, add a detailed comment:

```python
# WHY n_chords=2 instead of the full 10-node Warren truss?
#
# The full 2D Warren truss (n_chords=5) has 17 free DOFs, requiring
# 5 qubits (32x32 Hamiltonian). VQE on such a system would require:
#   - 12+ HEA parameters (2 reps on 5 qubits)
#   - Hundreds of iterations per optimizer start
#   - Multiple restarts for convergence
#   - ~30+ minutes per optimizer run on Qiskit Aer simulator
#
# For tractable demonstration, we use n_chords=2 (2 qubits) which:
#   - Preserves the 2D Warren truss topology (triangular elements)
#   - Demonstrates quantum advantage concepts at minimal scale
#   - Runs in < 1 minute while maintaining the same methodology
#
# Scaling to 5+ qubits is straightforward — just set n_chords=5
# (requires hardware runtime or significant simulator patience).
```

Also update `TODO.md` to note this decision.

---

## Issue #6: Presentation Plan

### After all code changes are complete, create presentation materials:

1. **Update `PRESENTATION_OUTLINE.md`** with:
   - New slide for "1D Truss Results" (between beam and 2D truss)
   - Updated slide for "Mode Shape Validation" (before/after fix)
   - Slides for "Ill-Conditioning Study Results" with actual plots
   - Slide explaining the 2D truss size reduction rationale
   - Updated performance summary table

2. **Generate all plot outputs:**
   - Run optimizer_comparison.py (standalone)
   - Run main.py with all fixes
   - Run novel_study.py (tapered beam + truss studies)
   - Verify all plots in results/

3. **Create presentation script:**
   - A `generate_presentation.py` that creates a matplotlib-based slide deck OR
   - Update the existing PRESENTATION_PPTX.md with actual data tables

---

## Detailed Task Breakdown

### Phase 1: Fix Optimizer Comparison (main.py)

**Files:** `main.py`

Changes:
1. Clean up the 3-solver setup to 2 solvers (L_BFGS-B as primary, COBYLA for comparison)
2. Fix the comparison table to correctly attribute results to the right optimizer
3. Add convergence plot for truss as well

**Estimated lines changed:** ~15 in main.py

### Phase 2: Fix Beam Mode Shapes (visualize.py + main.py)

**Files:** `visualize.py`, `main.py`

Changes:
1. Fix `plot_mode_shapes_continuous()`:
   - Proper VQE-to-physical DOF mapping
   - Fix the length comparison bug
   - Add analytical mode shape overlay
2. Update `main.py` mode shape call to pass correct data

**Estimated lines changed:** ~30 in visualize.py, ~10 in main.py

### Phase 3: Restore Ill-Conditioning Study (novel_study.py + main.py)

**Files:** `novel_study.py`, `main.py`

Changes:
1. Add `if __name__ == "__main__"` guard to novel_study.py for standalone testing
2. Uncomment imports in main.py
3. Add controlled study execution with `RUN_NOVEL_STUDIES` flag
4. Add plotting of results
5. Generate study CSV files

**Estimated lines changed:** ~20 in novel_study.py, ~30 in main.py

### Phase 4: Add 1D Truss Visualization (main.py + visualize.py)

**Files:** `main.py`, `visualize.py`

Changes:
1. In main.py: Add calls to `plot_truss_geometry()`, `plot_truss_mode_shapes()`, `plot_truss_frequency_comparison()` for 1D truss
2. Add 1D truss optimizer comparison
3. Add 1D truss convergence plot

**Estimated lines changed:** ~20 in main.py

### Phase 5: Add Documentation Comments

**Files:** `main.py`, `TODO.md`

Changes:
1. Add "why reduced truss" comment in main.py
2. Update TODO.md to reflect all changes
3. Update docstrings where needed

### Phase 6: Generate Presentation Materials

**Files:** `PRESENTATION_OUTLINE.md`, `results/` (new plots)

Changes:
1. Update presentation outline with new slides
2. Run full pipeline and verify all outputs
3. Generate final figures for presentation

---

## Verification Checklist

- [ ] `main.py` runs without errors
- [ ] Optimizer comparison correctly shows COBYLA vs L_BFGS-B (not mixed up)
- [ ] Beam mode shapes show both classical and VQE results
- [ ] Beam mode shapes match analytical sin(nπx/L) shapes
- [ ] 1D truss section generates geometry + mode shape + frequency plots
- [ ] Ill-conditioning study generates `tapered_beam_study.csv` and plots
- [ ] Damage detection study generates `damage_detection.csv` and plots
- [ ] 2D truss section still works correctly
- [ ] All plots saved to results/
- [ ] `TODO.md` updated to reflect completed changes
- [ ] Presentation outline updated
- [ ] Documentation comments added explaining truss size reduction

## Files to Modify (Summary)

| File | Change Type | Priority |
|------|------------|----------|
| `main.py` | Modify | HIGH |
| `visualize.py` | Modify | HIGH |
| `novel_study.py` | Minor add | MEDIUM |
| `TODO.md` | Update | LOW |
| `PRESENTATION_OUTLINE.md` | Update | LOW |

## Files NOT Modified (Verified Compatible)
- `truss.py` ✓ (no changes needed)
- `visualize_truss2d.py` ✓ (no changes needed)
- `quantum_setup.py` ✓ (no changes needed)
- `vqe_runner.py` ✓ (no changes needed)
- `ansatz.py` ✓ (no changes needed)
- `fea.py` ✓ (no changes needed)
- `validate_truss.py` ✓ (no changes needed)