# VQA Modal Analysis

**Finding Natural Frequencies of Structures Using the Variational Quantum Eigensolver**

A 3rd-year undergraduate project at COEP Technological University exploring how quantum computers can solve structural vibration problems — and how structural complexity affects quantum algorithm convergence.

---

## Project Overview

This project applies the **Variational Quantum Eigensolver (VQE)** to structural modal analysis. The core idea: the generalized eigenvalue problem from structural mechanics (`Kφ = ω²Mφ`) maps *exactly* onto the quantum eigenvalue problem (`H|ψ⟩ = λ|ψ⟩`). No approximation needed.

The **novel research contribution** is studying how structural ill-conditioning (slender beams, damaged elements, buckling proximity) affects VQE's convergence behavior — a question no existing paper addresses.

### What's in This Repo

```
.
├── main.py                  # Full pipeline runner (run this to execute everything)
├── fea.py                   # Finite Element Analysis (assembly, BCs, classical solve)
├── quantum_setup.py         # Hamiltonian construction (K,M → quantum operator)
├── ansatz.py                # Quantum circuit ansatzes (HEA + symmetry-aware)
├── vqe_runner.py            # VQE solver class with deflation for excited states
├── novel_study.py           # Novel ill-conditioning + damage detection studies
├── visualize.py             # All plotting functions
├── optimizer_comparison.py  # COBYLA vs L-BFGS-B vs SPSA comparison
├── validate_fea.py         # FEA validation against analytical solutions
├── results/                 # Output plots and CSV data
│   ├── beam_geometry.png
│   ├── convergence.png
│   ├── damage_detection.png
│   ├── frequency_comparison.png
│   ├── ill_conditioning_study.png
│   ├── mode_shapes_continuous.png
│   └── optimizer_comparison.png
└── graphify-out/            # Knowledge graph outputs (for project navigation)
    ├── graph.html          # Interactive graph viewer
    └── GRAPH_REPORT.md      # Full corpus audit
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install qiskit qiskit-aer qiskit-algorithms numpy scipy matplotlib pandas
```

> **Note:** You need Python 3.9+ and approximately 2-3 GB of free memory for the Qiskit Aer simulator.

### 2. Run the Full Pipeline

```bash
python main.py
```

This executes Steps 1–6 in sequence:
1. **Classical FEA baseline** — assemble beam, apply BCs, compute natural frequencies
2. **Quantum Hamiltonian** — convert `K` and `M` matrices to a quantum operator
3. **VQE on simulator** — minimize energy to find fundamental frequency
4. **Higher modes via deflation** — find 2nd and 3rd natural frequencies
5. **Novel studies** — tapered beam (ill-conditioning) + damage detection
6. **All plots** — generate every visualization

Expected runtime: **2–5 minutes** on a modern laptop (simulator only, no IBM account needed).

### 3. Output Location

All results go to the `results/` directory. You'll see:
- `convergence.png` — VQE cost function decreasing to minimum eigenvalue
- `ill_conditioning_study.png` — condition number vs convergence behavior
- `damage_detection.png` — frequency shift vs stiffness reduction
- `optimizer_comparison.png` — COBYLA vs L-BFGS-B convergence curves
- CSV files: `tapered_beam_study.csv`, `damage_study.csv`

---

## Architecture Walkthrough

### The Pipeline

```
Structural System
      │
      ▼
┌─────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│   fea.py        │     │   quantum_setup.py   │     │   vqe_runner.py│
│                 │     │                      │     │                │
│ assemble_beam() │────▶│ build_structural_    │────▶│ VQEStructural  │
│ apply_bc()      │     │ hamiltonian()        │     │ Solver.solve() │
│ classical_      │     │                      │     │                │
│ modal_analysis()│     │ M^(-1/2) K M^(-1/2)   │     │ Finds ω₁ via   │
│                 │     │ → normalized H        │     │ minimization    │
└─────────────────┘     └──────────────────────┘     └────────────────┘
                                                             │
      ┌────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────────────┐
│                     novel_study.py                            │
│                                                                │
│  tapered_beam_study()      →  ill_conditioning_study.png     │
│  (L/r variations)            Condition # vs VQE iterations  │
│                                                                │
│  damage_detection_study()   →  damage_detection.png          │
│  (stiffness reduction)        VQE frequency shift vs damage % │
└────────────────────────────────────────────────────────────────┘
```

### Module Reference

#### `fea.py` — Finite Element Analysis

| Function | Description |
|---|---|
| `beam_element_stiffness(EI, L)` | Returns 4×4 Euler-Bernoulli stiffness matrix |
| `beam_element_mass(rhoA, L)` | Returns 4×4 consistent mass matrix |
| `assemble_beam(n, E, I, rho, A, L)` | Assembles global K and M for n-element beam |
| `apply_simply_supported_bc(K, M, n)` | Removes pinned DOFs, returns reduced matrices |
| `apply_cantilever_bc(K, M)` | Removes fixed-end DOFs |
| `classical_modal_analysis(K_red, M_red)` | Solves eigenvalue problem via `scipy.linalg.eigh` |
| `analytical_simply_supported(...)` | Closed-form frequencies for validation |

**DOF ordering** in beam elements: `[v_i, θ_i, v_j, θ_j]`
- `v` = transverse displacement, `θ` = rotation

**Boundary conditions**:
- Simply-supported: remove `v` at both ends (indices 0 and `2n`)
- Cantilever: remove `v` and `θ` at node 0 (indices 0 and 1)

#### `quantum_setup.py` — Hamiltonian Construction

| Function | Description |
|---|---|
| `build_structural_hamiltonian(K_red, M_red)` | Converts structural eigenvalue problem to quantum Hamiltonian |
| `inspect_pauli_decomposition(hamiltonian)` | Prints all Pauli terms and coefficients |

**The transformation:**
```
Kφ = ω²Mφ
→ H = M^(-1/2) K M^(-1/2)      (standard form)
→ H_norm = H / ||H||          (normalize to O(1) for VQE)
→ H |ψ⟩ = λ |ψ⟩              (quantum eigenvalue problem)
```

VQE returns λ_min (unitless). Multiply by `H_scale` and take `sqrt` to recover ω in rad/s.

#### `ansatz.py` — Quantum Circuit Ansatzes

| Function | Description |
|---|---|
| `hardware_efficient_ansatz(n_qubits, reps=2)` | Standard HEA from Qiskit library |
| `symmetric_ansatz(n_qubits, reps=2)` | Symmetry-constrained ansatz (encodes simply-supported beam symmetry) |
| `minimal_ansatz(n_qubits)` | 2-parameter minimal ansatz for quick testing |

**HEA (Hardware-Efficient Ansatz):** alternating rotation layers + CNOT entanglers. For 2 qubits, 2 reps → 12 parameters. Good default choice.

**Symmetric Ansatz:** enforces mirror symmetry of fundamental mode shape. Fewer parameters → potentially faster convergence. **This is part of the novel contribution** — testing whether physics-informed ansatz design helps.

#### `vqe_runner.py` — VQE Solver

| Class | Description |
|---|---|
| `VQEStructuralSolver` | Full VQE solver for structural problems |

**Key methods:**
- `solve(initial_point=None)` — Runs VQE, returns `{'omega', 'cost_history', 'iterations', 'mode_shape', ...}`
- `solve_excited_states(n_modes=3)` — Uses **deflation** to find higher eigenvalues

**Supported optimizers:** `'COBYLA'` (derivative-free), `'SPSA'` (noisy hardware), `'L_BFGS_B'` (gradient-based)

**Deflation method:** after finding mode i, add a projector penalty `λ|φ_i⟩⟨φ_i|` to the Hamiltonian and re-run VQE. This pushes the ground state above the found mode, forcing the optimizer to find the next excited state.

#### `truss.py` — Truss (Bar Element) Analysis

| Function | Description |
|---|---|
| `truss_element_stiffness(EA, L)` | Returns 2×2 axial stiffness matrix |
| `truss_element_mass(rhoA, L, lumped=False)` | Returns 2×2 mass matrix (consistent or lumped) |
| `assemble_truss(num_elements, E, A, rho, L)` | Assembles global K, M matrices |
| `apply_fixed_fixed_bc(K, M)` | Removes DOFs at both ends |
| `apply_fixed_free_bc(K, M)` | Removes DOFs at fixed end (cantilever) |
| `classical_modal_analysis(K_red, M_red)` | Solves eigenvalue problem via `scipy.linalg.eigh` |
| `analytical_fixed_fixed(E, A, rho, L, n_modes)` | ωₙ = (nπ/L)√(E/ρ) |
| `analytical_fixed_free(E, A, rho, L, n_modes)` | ωₙ = (2n-1)π/(2L)√(E/ρ) |

**DOF ordering:** `[u₀, u₁, ..., uₙ]` — 1 DOF (axial displacement) per node. For n elements: n+1 nodes, n+1 DOF before BCs.

**Key difference from beams:** Truss elements have only axial stiffness (no bending). Stiffness matrix is 2×2 (vs 4×4 for beams). Simpler physics, faster convergence.

#### `novel_study.py` — Novel Research Studies

| Function | Description |
|---|---|
| `tapered_beam_study(E, I, rho, A, L, taper_ratios)` | Tests VQE across a range of condition numbers via geometric taper |
| `damage_detection_study(E, I, rho, A, L, damage_levels)` | Tests frequency shift detection via simulated stiffness reduction |
| `tapered_truss_study(E, A, rho, L, area_ratios, n_elements)` | Truss version: area taper study (condition number vs VQE) |
| `truss_damage_study(E, A, rho, L, damage_levels, n_elements)` | Truss version: damage detection via frequency shifts |

**The key hypothesis being tested:**
- As condition number increases (slender beams, damaged elements), VQE convergence degrades
- This has practical implications: **VQE-based structural health monitoring has a detection threshold**

#### `visualize.py` — Plotting Functions

| Function | Output |
|---|---|
| `plot_convergence(...)` | `results/convergence.png` — cost curve + frequency error |
| `plot_dual_convergence(...)` | COBYLA vs L-BFGS-B side-by-side convergence |
| `plot_ill_conditioning_study(df)` | `results/ill_conditioning_study.png` — condition # vs iterations |
| `plot_damage_detection(df)` | `results/damage_detection.png` — frequency shift vs damage % |
| `plot_frequency_comparison(...)` | `results/frequency_comparison.png` — VQE vs classical bar chart |
| `plot_mode_shapes_continuous(...)` | `results/mode_shapes_continuous.png` — animated mode shapes |
| `plot_optimizer_comparison(...)` | `results/optimizer_comparison.png` — optimizer comparison |
| `plot_beam_geometry(n_elem, L)` | `results/beam_geometry.png` — beam diagram with node labels |

---

## Running Individual Components

### Run Only the Classical FEA Baseline

```python
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported

E, I, rho, A, L = 200e9, 8.33e-6, 7850, 0.01, 1.0
n_elem = 2

K, M = assemble_beam(n_elem, E, I, rho, A, L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, n_elem)
omega_classical, modes = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

print(f"FEA:   {omega_classical}")
print(f"Exact: {omega_analytical[:len(omega_classical)]}")
```

### Run VQE on Simulator Only

```python
from quantum_setup import build_structural_hamiltonian, inspect_pauli_decomposition
from ansatz import hardware_efficient_ansatz
from vqe_runner import VQEStructuralSolver
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis

# Setup
K, M = assemble_beam(2, 200e9, 8.33e-6, 7850, 0.01, 1.0)
K_red, M_red, _ = apply_simply_supported_bc(K, M, 2)
omega_classical, _ = classical_modal_analysis(K_red, M_red)

# Quantum
H_norm, hamiltonian, _, H_scale = build_structural_hamiltonian(K_red, M_red)
inspect_pauli_decomposition(hamiltonian)

# VQE
ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)
solver = VQEStructuralSolver(hamiltonian, ansatz, optimizer_name='COBYLA', maxiter=500, H_scale=H_scale)
result = solver.solve()

print(f"VQE: {result['omega']:.4f} rad/s | Classical: {omega_classical[0]:.4f} rad/s")
print(f"Error: {abs(result['omega'] - omega_classical[0]) / omega_classical[0] * 100:.3f}%")
```

### Run Only the Novel Studies

```python
from novel_study import tapered_beam_study, damage_detection_study
import matplotlib.pyplot as plt

# Ill-conditioning study
taper_ratios = [1.0, 0.8, 0.6, 0.4, 0.25, 0.15]
df_tapered = tapered_beam_study(200e9, 8.33e-6, 7850, 0.01, 1.0, taper_ratios)

from visualize import plot_ill_conditioning_study
plot_ill_conditioning_study(df_tapered)
print(df_tapered)

# Damage detection study
damage_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
df_damage = damage_detection_study(200e9, 8.33e-6, 7850, 0.01, 1.0, damage_levels)

from visualize import plot_damage_detection
plot_damage_detection(df_damage)
print(df_damage)
```

### Run Truss Analysis

```python
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, analytical_fixed_fixed
from quantum_setup import build_structural_hamiltonian, inspect_pauli_decomposition
from ansatz import hardware_efficient_ansatz
from vqe_runner import VQEStructuralSolver
import matplotlib.pyplot as plt

# Truss parameters
E = 200e9       # Young's modulus (Pa) - steel
A = 0.01        # Cross-section area (m^2)
rho = 7850.0    # Density (kg/m^3)
L = 1.0         # Truss length (m)
n_elem = 4      # Number of elements (gives 2 qubits after BCs)

# Assemble truss
K_t, M_t = assemble_truss(n_elem, E, A, rho, L)
K_t_red, M_t_red, free_dofs_t = apply_fixed_fixed_bc(K_t, M_t)
omega_t_classical, modes_t = classical_modal_analysis(K_t_red, M_t_red)
omega_t_analytical = analytical_fixed_fixed(E, A, rho, L, n_modes=len(omega_t_classical))

print(f"Truss natural frequencies (rad/s): {omega_t_classical}")
print(f"Analytical:                         {omega_t_analytical}")

# Quantum Hamiltonian
H_norm_t, ham_t, _, H_scale_t = build_structural_hamiltonian(K_t_red, M_t_red)
inspect_pauli_decomposition(ham_t)

# VQE
ansatz_t = hardware_efficient_ansatz(num_qubits=2, reps=2)
np.random.seed(42)
init_pt_t = np.random.uniform(-np.pi, np.pi, 12)

solver_t = VQEStructuralSolver(ham_t, ansatz_t, optimizer_name='COBYLA',
                                maxiter=500, H_scale=H_scale_t)
result_t = solver_t.solve(initial_point=init_pt_t)

print(f"VQE: {result_t['omega']:.4f} rad/s | Classical: {omega_t_classical[0]:.4f} rad/s")
print(f"Error: {abs(result_t['omega'] - omega_t_classical[0])/omega_t_classical[0]*100:.3f}%")
```

### Run Optimizer Comparison

```python
python optimizer_comparison.py
# Outputs: results/optimizer_comparison.png
```

---

## Physics Background

### The Problem

For a vibrating beam, the equation of motion gives the **generalized eigenvalue problem**:

```
[K]{φ} = ω²[M]{φ}
```

| Symbol | Meaning |
|---|---|
| `K` | Global stiffness matrix (assembled from element matrices) |
| `M` | Global mass matrix (consistent mass formulation) |
| `ω²` | Eigenvalue → squared natural frequency |
| `{φ}` | Eigenvector → mode shape |

Solving this gives `N` natural frequencies and `N` mode shapes for an `N`-DOF system.

### Why Quantum?

The structural eigenvalue problem is **mathematically identical** to the Schrödinger equation in quantum mechanics. Both are eigenvalue problems of Hermitian matrices. This means:

1. The same quantum algorithm (VQE) that finds ground states of molecular Hamiltonians also finds the fundamental frequency of structural systems
2. The mapping is **direct and exact** — no approximation or reformulation
3. As quantum hardware improves, VQE for structural problems will scale polynomially with DOF (vs classical O(N³))

### The Standard Form Transform

For VQE to work, the generalized eigenvalue problem must be converted to standard form:

```python
H = M^(-1/2) @ K @ M^(-1/2)   # Symmetric Hamiltonian
H_norm = H / ||H||             # Normalized (spectral norm = 1)
```

`H_norm` is then decomposed into Pauli strings and loaded into the VQE ansatz circuit.

---

## Novel Research Contribution

### The Three Research Gaps

**Gap 1: Structural Ill-Conditioning vs VQE Convergence**
No paper studies how matrix condition number (slender beams, near-buckling) affects the VQE energy landscape flatness and convergence rate.

**Gap 2: Physically-Motivated Ansatz Design**
Mode shapes have known symmetry properties (simply-supported → symmetric fundamental). Can encoding this into the circuit reduce iterations by 30-50%? No paper has tested this.

**Gap 3: VQE-Based Structural Health Monitoring**
Systematic frequency shift detection as a damage indicator using VQE — what damage level causes VQE's estimate to diverge from classical?

### Key Results to Look For

1. **Condition number vs iterations** — if the plot shows increasing iterations with condition number, the hypothesis is confirmed
2. **Frequency vs damage level** — if VQE-detected shifts match classical within 2%, damage detection via quantum is feasible
3. **HEA vs Symmetric ansatz** — if symmetric converges faster, physics-informed ansatz design helps

---

## Team Task Allocation

### Mechanical Engineering Students

- [ ] Validate FEA output against analytical formulas
- [ ] Define all structural test cases (geometry, materials, BCs)
- [ ] Interpret frequency shifts mechanically ("what does a 5% drop in ω₁ mean for the beam?")
- [ ] Design the ill-conditioning parameter study (which L/r values to test)
- [ ] Physical interpretation of mode shapes

### Computer Science / Quantum Students

- [ ] Maintain `quantum_setup.py` and `ansatz.py`
- [ ] Run VQE on IBM hardware (after simulator validation)
- [ ] Implement and test ZNE error mitigation
- [ ] Performance profiling: circuit depth, gate count, shot budget
- [ ] All visualization and data analysis

---

## Expected Results

### Minimum (Pass)

| Metric | Target |
|---|---|
| FEA vs Analytical error | < 1% |
| VQE vs Classical error | < 2% |
| Simulator runtime | < 2 minutes |

### Good (Merit)

| Metric | Target |
|---|---|
| Modes found (deflation) | 3 natural frequencies |
| Tapered beam cases | 6 different taper ratios |
| Damage detection cases | 6 damage levels with clear trend |

### Excellent (Distinction)

| Metric | Target |
|---|---|
| Ansatz comparison | HEA vs symmetric with convergence speed metrics |
| IBM hardware run | Raw vs ZNE-mitigated comparison |
| Detection threshold | Identified damage level where VQE error exceeds 5% |

---

## Technology Stack

| Package | Version | Purpose |
|---|---|---|
| `qiskit` | ≥1.0 | Core quantum framework |
| `qiskit-aer` | ≥0.14 | Local statevector simulator |
| `qiskit-algorithms` | ≥0.3 | VQE + optimizers |
| `numpy` | ≥1.24 | Matrix operations |
| `scipy` | ≥1.10 | `eigh`, `fractional_matrix_power` |
| `matplotlib` | ≥3.7 | All plots |

Install all at once:
```bash
pip install qiskit qiskit-aer qiskit-algorithms numpy scipy matplotlib pandas
```

---

## Project Structure

```
vqa_modal_analysis/
├── main.py                 ← Start here (full pipeline)
├── fea.py                  ← Classical FEA
├── quantum_setup.py         ← K,M → quantum Hamiltonian
├── ansatz.py               ← Quantum circuit designs
├── vqe_runner.py            ← VQE solver
├── novel_study.py          ← Novel research studies
├── visualize.py            ← All plots
├── optimizer_comparison.py  ← Optimizer benchmark
├── validate_fea.py         ← FEA validation
├── VQA_Modal_Analysis.md   ← Full technical documentation
├── results/                ← Generated plots and data
│   ├── convergence.png
│   ├── damage_detection.png
│   ├── ill_conditioning_study.png
│   ├── frequency_comparison.png
│   ├── optimizer_comparison.png
│   ├── mode_shapes_continuous.png
│   ├── beam_geometry.png
│   ├── tapered_beam_study.csv
│   └── damage_study.csv
└── graphify-out/           ← Knowledge graph
    ├── graph.html
    └── GRAPH_REPORT.md
```

---

## Understanding the Codebase

The `graphify-out/graph.html` file is an interactive knowledge graph of the entire project. Open it in any browser to explore:

- Which functions call which others
- How structural concepts (condition number, slenderness) connect to quantum concepts (ansatz, Pauli decomposition)
- The community structure of the project

The `graphify-out/GRAPH_REPORT.md` contains the full audit including:
- God nodes (most connected concepts)
- Surprising cross-domain connections
- Knowledge gaps (49 weakly-connected nodes that need documentation)

---

## Troubleshooting

### "Qiskit nightly install issues"
If you get import errors with `qiskit-algorithms`, make sure you're using compatible versions:
```bash
pip install qiskit==1.0.0 qiskit-aer==0.13.0 qiskit-algorithms==0.3.0
```

### "VQE doesn't converge"
- Try increasing `maxiter` from 500 to 2000
- Change `initial_point` (current uses `np.random.seed(42)`)
- Try a different optimizer (COBYLA is generally most stable for VQE)

### "FEA frequency doesn't match analytical"
- Check that you applied boundary conditions correctly
- Verify material properties (E, I, rho, A, L)
- For simply-supported: analytical formula is `ωₙ = (nπ/L)² × √(EI/ρA)`

### "IBM Quantum runtime error"
- Make sure you have a valid IBM Quantum API token
- For the simulator only (no IBM account needed), remove all `qiskit-ibm-runtime` calls

---

## References

- **VQE Original:** Peruzzo et al. (2014), "A variational eigenvalue solver on a photonic quantum processor", *Nature Communications*
- **IBM Error Mitigation:** Kandala et al. (2019), "Error mitigation extends the computational reach of a noisy quantum processor", *Nature*
- **Structural Dynamics:** Chopra, "Dynamics of Structures" — Chapters 3-4 (modal analysis)
- **FEA:** Cook et al., "Concepts and Applications of Finite Element Analysis"
- **Qiskit Docs:** https://docs.quantum.ibm.com/