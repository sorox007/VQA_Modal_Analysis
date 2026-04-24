# VQA-Based Modal Analysis
## Finding Natural Frequencies of Structures Using Variational Quantum Eigensolver

**Quantum Computing Minor | COEP Technological University | 3rd Year Project**  
*Written for Mechanical + Computer Engineering students — no prior QC knowledge assumed*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Background — What is Modal Analysis?](#2-background--what-is-modal-analysis)
3. [The Mechanics Foundation](#3-the-mechanics-foundation)
4. [Quantum Computing Basics (For Mech Students)](#4-quantum-computing-basics-for-mech-students)
5. [Why Structural Mechanics Maps Perfectly to QC](#5-why-structural-mechanics-maps-perfectly-to-qc)
6. [The VQE Algorithm — Full Breakdown](#6-the-vqe-algorithm--full-breakdown)
7. [Structural Systems to Model](#7-structural-systems-to-model)
8. [Full Implementation Plan — Step by Step](#8-full-implementation-plan--step-by-step)
9. [Novel Contribution — The Research Gap](#9-novel-contribution--the-research-gap)
10. [Visualizations](#10-visualizations)
11. [IBM Hardware Strategy](#11-ibm-hardware-strategy)
12. [Complete Code Reference](#12-complete-code-reference)
13. [Technology Stack](#13-technology-stack)
14. [Team Task Split](#14-team-task-split)
15. [Expected Results & Deliverables](#15-expected-results--deliverables)
16. [Ratings & Comparison](#16-ratings--comparison)
17. [References & Further Reading](#17-references--further-reading)

---

## 1. Project Overview

### The One-Line Summary
> Use a Variational Quantum Algorithm to compute the natural frequencies and mode shapes of structural systems — and study how structural complexity (slenderness, damage, material layup) affects quantum convergence.

### What Are We Building?
A complete pipeline that:
1. Takes a structural system (beam, column, frame) as input
2. Assembles the stiffness `K` and mass `M` matrices using classical FEA
3. Converts the eigenvalue problem into a quantum Hamiltonian
4. Solves it on IBM Quantum hardware (real quantum computer)
5. Extracts natural frequencies and mode shapes
6. Compares results against classical solvers
7. Studies how structural ill-conditioning affects the quantum solver

### Why This Is Novel
The mapping of structural eigenvalue problems to VQE is known. What is **not** studied anywhere:
- How structural **ill-conditioning** (slenderness, buckling proximity, damage) distorts the VQE energy landscape
- Whether physically-motivated ansatz circuits (exploiting mode shape symmetry) converge faster than generic ones
- Systematic frequency shift detection as a quantum structural health monitoring tool

No existing paper has studied these specific questions. This is the research gap.

### Quick Stats

| Property | Value |
|---|---|
| Algorithm | VQE (Variational Quantum Eigensolver) |
| Hardware | IBM Quantum (2-3 qubits for clean results) |
| Simulator | Qiskit Aer (statevector) |
| Primary Language | Python |
| Key Libraries | Qiskit, NumPy, SciPy, Matplotlib |
| Expected Timeline | 5 weeks |
| Team Size | 2–4 students |
| Difficulty | ⭐⭐⭐⭐ out of 5 |

---

## 2. Background — What is Modal Analysis?

### Real-World Motivation
Every structure vibrates. When the frequency of an external force matches a structure's **natural frequency**, resonance occurs. Energy builds up, amplitudes grow, and the structure can fail.

Famous examples:
- **Tacoma Narrows Bridge (1940)** — collapsed because wind-induced oscillation matched the bridge's natural frequency
- **Soldiers break step crossing bridges** — to avoid resonance with footstep frequency
- **Aircraft engine mounts** — designed so engine vibration frequencies do not match airframe modes
- **Artillery barrels** — must avoid resonance with recoil impulse frequencies (directly relevant to KSSL-type work)

### What Modal Analysis Gives You
Running modal analysis gives you two things per mode:

1. **Natural frequency** `ω_n` (rad/s) or `f_n = ω_n / 2π` (Hz) — the frequency at which this mode vibrates
2. **Mode shape** `φ_n` — the deformation pattern at that frequency (which parts move how much)

A structure with `N` DOF (degrees of freedom) has exactly `N` natural frequencies and `N` mode shapes.

### Classical vs Quantum Approach

| Aspect | Classical (ANSYS/scipy) | Quantum (VQE) |
|---|---|---|
| Method | Dense eigensolvers (LAPACK) | Variational minimization on QPU |
| Scaling | O(N³) for dense, O(N²) for sparse | Polynomial with number of qubits |
| Current limit | Millions of DOF (but slow) | ~50 DOF (NISQ era hardware) |
| Advantage | Mature, fast for current sizes | Future exponential speedup |
| Noise | None (deterministic) | Hardware noise present |

> **Key Point:** We are not claiming VQE beats classical solvers today. We are studying the quantum approach, characterizing its behaviour, and establishing the groundwork for when fault-tolerant hardware arrives.

---

## 3. The Mechanics Foundation

> **For CS Students:** This section covers the structural mechanics math. Think of `K` and `M` as NumPy matrices that encode the physics. You don't need to derive them — the Mech team does that. You just need to know what they represent.

### 3.1 Degrees of Freedom (DOF)

When we discretize a continuous structure into finite elements, each node has a set of **degrees of freedom** — independent displacement components.

- 1D bar: 1 DOF per node (axial displacement `u`)
- 2D beam: 2 DOF per node (transverse displacement `v`, rotation `θ`)
- 2D frame: 3 DOF per node (`u`, `v`, `θ`)

A beam modeled with 2 elements has 3 nodes × 2 DOF = 6 DOF total (4 after applying boundary conditions at supports).

### 3.2 The Global Stiffness Matrix K

`K` is assembled by looping over all elements, computing each element's stiffness matrix `k_e`, and adding contributions to the global matrix at the appropriate DOF indices.

For an **Euler-Bernoulli beam element** of length `L`, Young's modulus `E`, and second moment of area `I`, the element stiffness matrix in local coordinates is:

```
         12    6L   -12    6L
k_e = EI/L³ *  6L   4L²   -6L    2L²
        -12   -6L    12   -6L
         6L   2L²   -6L    4L²
```

Properties of K:
- **Symmetric**: `K = Kᵀ` always
- **Positive semi-definite**: all eigenvalues ≥ 0
- **Sparse**: most entries are zero (only adjacent elements contribute)
- **Hermitian**: same as symmetric for real matrices — this is the critical property for quantum computing

### 3.3 The Global Mass Matrix M

The consistent mass matrix for an Euler-Bernoulli beam element (using the same shape functions as the stiffness matrix):

```
          156    22L    54   -13L
m_e = ρAL/420 *  22L    4L²   13L   -3L²
           54    13L   156   -22L
          -13L   -3L²  -22L    4L²
```

Where `ρ` = density, `A` = cross-section area, `L` = element length.

Properties of M:
- Symmetric, positive definite (all eigenvalues > 0)
- Hermitian — also quantum-compatible

### 3.4 The Generalized Eigenvalue Problem

The governing equation for free vibration (Newton's second law applied to all DOF simultaneously) is:

```
[ K ] { φ } = ω² [ M ] { φ }
```

This is a **generalized eigenvalue problem**. The solutions are:
- `ω₁² ≤ ω₂² ≤ ... ≤ ωₙ²` — eigenvalues → natural frequencies
- `{φ₁}, {φ₂}, ..., {φₙ}` — eigenvectors → mode shapes

The fundamental (lowest) natural frequency `ω₁` is the most critical for resonance avoidance.

### 3.5 Boundary Conditions

Before solving, apply boundary conditions by removing the DOF rows and columns corresponding to fixed supports (zero displacement). This reduces the `6×6` system (for 2-element beam) to a `4×4` reduced system `K_red` and `M_red`.

For a simply-supported beam (both ends pinned):
- Remove transverse displacement DOF at both ends
- Keep rotation DOF at both ends
- Result: 4×4 reduced system → 4 natural frequencies

For a cantilever beam (fixed at one end, free at other):
- Remove all DOF at fixed end (both displacement and rotation)
- Result: 4×4 reduced system for 2-element model

### 3.6 Analytical Validation Formula

For a simply-supported Euler-Bernoulli beam, the analytical natural frequencies are:

```
ωₙ = (nπ/L)² × √(EI / ρA)    for n = 1, 2, 3, ...
```

Your FEA result must match this within 1% for 2 elements. This is your first validation checkpoint.

---

## 4. Quantum Computing Basics (For Mech Students)

> **For Mech Students:** This section covers the QC fundamentals you need to understand what happens after the FEA matrices are assembled. CS students already know this.

### 4.1 What is a Qubit?

A classical bit is either 0 or 1. A **qubit** can be in a **superposition** — a quantum state that is simultaneously 0 and 1 until measured:

```
|ψ⟩ = α|0⟩ + β|1⟩    where |α|² + |β|² = 1
```

`α` and `β` are complex amplitudes. When measured, the qubit collapses to `|0⟩` with probability `|α|²` or `|1⟩` with probability `|β|²`.

For `n` qubits, the system exists in a superposition of all `2ⁿ` possible states simultaneously. A 10-qubit system is in superposition of 1024 states. A 50-qubit system: 1 quadrillion states simultaneously.

### 4.2 Quantum Gates

Quantum gates are operations on qubits — analogous to logic gates (AND, OR, NOT) in classical computing. Key gates:

| Gate | Symbol | What It Does |
|---|---|---|
| Hadamard | H | Puts qubit into superposition: `|0⟩ → (|0⟩+|1⟩)/√2` |
| Rotation-Y | Ry(θ) | Rotates qubit state by angle θ around Y-axis |
| Rotation-Z | Rz(θ) | Rotates qubit state by angle θ around Z-axis |
| CNOT | ⊕ | Flips target qubit if control qubit is `|1⟩` — creates entanglement |
| Pauli-X | X | Quantum NOT gate: flips `|0⟩↔|1⟩` |
| Pauli-Z | Z | Phase flip: `|1⟩ → -|1⟩` |

### 4.3 Pauli Matrices

The Pauli matrices are the fundamental building blocks of quantum operators:

```
I = [[1, 0],    X = [[0, 1],    Y = [[0, -i],    Z = [[1,  0],
     [0, 1]]         [1, 0]]         [i,  0]]         [0, -1]]
```

**Critical fact:** Any Hermitian matrix (including your structural `K` and `M`) can be written as a weighted sum of tensor products of Pauli matrices:

```
H = Σᵢ cᵢ Pᵢ    where Pᵢ ∈ {I, X, Y, Z}^⊗n
```

This is called **Pauli decomposition** and is what makes structural matrices quantum-computable. Qiskit does this automatically.

### 4.4 Quantum Measurement

Measuring a qubit destroys its superposition — the qubit collapses to a definite state. To estimate an expectation value `⟨ψ|H|ψ⟩`, you run the circuit many times (shots) and average the outcomes.

For 1024 shots, you get a statistical estimate. More shots = lower statistical noise, but more time on quantum hardware.

### 4.5 The Variational Principle

This is the core mathematical idea behind VQE:

> For any quantum state `|ψ(θ)⟩` (parametrized by angles θ), the expectation value of a Hermitian operator H is ALWAYS ≥ the minimum eigenvalue:

```
⟨ψ(θ)|H|ψ(θ)⟩  ≥  λ_min    for ALL choices of θ
```

Equality holds only when `|ψ(θ)⟩` is exactly the ground state (eigenvector of minimum eigenvalue). Therefore: **minimize the expectation value → find the minimum eigenvalue**.

This is the variational principle from quantum mechanics, and it is mathematically identical to the principle of minimum potential energy in structural mechanics.

---

## 5. Why Structural Mechanics Maps Perfectly to QC

### 5.1 The Key Insight

The Schrödinger equation from quantum physics:
```
H_quantum |ψ⟩ = E |ψ⟩
```

The structural vibration equation from mechanics:
```
H_structural |φ⟩ = λ |φ⟩    where H = M^(-1/2) K M^(-1/2), λ = ω²
```

**These are mathematically identical.** Both are eigenvalue problems of Hermitian operators. Quantum computers were built to solve the first equation. They solve the second for free.

This is not a forced analogy. Structural matrices ARE quantum Hamiltonians in the mathematical sense. There is no approximation or reformulation — just recognition that the same math governs both.

### 5.2 The Standard Form Transformation

The generalized eigenvalue problem `Kφ = ω²Mφ` must be converted to standard form for VQE:

```python
# Step 1: Compute M^(-1/2) using scipy
import scipy.linalg as la
M_half_inv = la.fractional_matrix_power(M_red, -0.5)

# Step 2: Form the symmetric Hamiltonian
H = M_half_inv @ K_red @ M_half_inv

# Step 3: Verify H is Hermitian (should be True)
print(np.allclose(H, H.T))  # True

# Step 4: Classical check - eigenvalues should match original problem
eigenvalues_H = np.linalg.eigvalsh(H)
omega_classical = np.sqrt(eigenvalues_H)  # Natural frequencies
```

### 5.3 Why This Is The Cleanest QC-Mech Mapping

Compared to other quantum structural mechanics approaches:

| Approach | Mapping Quality | Notes |
|---|---|---|
| **VQE for Modal Analysis** | ✅ Natural | Structure IS an eigenvalue problem. Zero reformulation needed. |
| VQLS for Ku=f | ✅ Good | Linear system → natural VQLS problem. One step removed. |
| HHL for Ku=f | ⚠️ Forced | HHL has readout paradox and condition sensitivity. |
| QAOA for Topology Opt | ⚠️ Reformulated | Continuous problem forced into binary QUBO. |
| QNN for Fatigue | ⚠️ ML proxy | Quantum ML, not a direct physics mapping. |

VQE Modal Analysis wins because it is the most honest, direct mapping — no reformulation, no approximation layers, no force-fitting.

---

## 6. The VQE Algorithm — Full Breakdown

### 6.1 Overview

VQE is a **hybrid classical-quantum algorithm**:
- **Quantum part:** Prepare a parametrized quantum state, measure energy expectation value
- **Classical part:** Optimize the parameters to minimize the energy

The quantum computer does what it's good at (quantum state preparation and interference). The classical computer does what it's good at (numerical optimization).

### 6.2 Algorithm Flowchart

```
START
  │
  ├─ Initialize theta randomly in [-π, π]
  │
  ▼
┌─────────────────────────────────┐
│  QUANTUM STEP                   │
│  1. Build ansatz circuit        │
│     |ψ(θ)⟩ = U(θ)|0⟩           │
│  2. Run circuit on QPU/simulator│
│  3. Measure ⟨ψ(θ)|H|ψ(θ)⟩      │
│     (cost function value)       │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  CLASSICAL STEP                 │
│  4. Pass cost to optimizer      │
│     (COBYLA / SPSA)             │
│  5. Optimizer updates theta     │
└─────────────┬───────────────────┘
              │
              ▼
         Converged?
         /        \
       YES         NO
        │           │
        ▼           └──► back to QUANTUM STEP
  Extract λ_min
  ω = √λ_min
  DONE
```

### 6.3 Pauli Decomposition — In Detail

Any `2ⁿ × 2ⁿ` Hermitian matrix can be decomposed into Pauli strings. For a `4×4` matrix (2 qubits), there are at most `4² = 16` Pauli terms:

```
H = c₁(I⊗I) + c₂(I⊗X) + c₃(I⊗Y) + c₄(I⊗Z) + c₅(X⊗I) + ... + c₁₆(Z⊗Z)
```

Each Pauli string `Pᵢ` corresponds to a simple quantum circuit. The expectation value is computed by running each Pauli term separately and summing:

```
⟨H⟩ = Σᵢ cᵢ ⟨ψ(θ)|Pᵢ|ψ(θ)⟩
```

For a 4×4 stiffness matrix typical of a 2-element beam, expect 8-12 non-zero Pauli terms. Sparse structural matrices have fewer non-zero Pauli terms than dense molecular Hamiltonians — this is an advantage.

```python
from qiskit.quantum_info import SparsePauliOp

hamiltonian = SparsePauliOp.from_operator(H)
print(f"Number of Pauli terms: {len(hamiltonian)}")
print(hamiltonian)  # Shows each term and coefficient
```

### 6.4 The Ansatz Circuit

The **ansatz** is the parametrized quantum circuit `U(θ)`. It defines the family of quantum states we search over. A good ansatz:
- Can represent the true ground state (sufficient expressibility)
- Has few parameters (fast optimization)
- Has shallow circuit depth (low noise on hardware)

#### Hardware-Efficient Ansatz (HEA)

The default choice. Alternating layers of single-qubit rotations and CNOT entangling gates:

```
Layer 1:  Ry(θ₁)──●──Ry(θ₃)
          Ry(θ₂)──⊕──Ry(θ₄)

Layer 2:  Ry(θ₅)──●──Ry(θ₇)
          Ry(θ₆)──⊕──Ry(θ₈)
```

For 2 qubits, 2 layers: 8 parameters. This is manageable for COBYLA.

```python
from qiskit.circuit.library import EfficientSU2
ansatz = EfficientSU2(num_qubits=2, reps=2, entanglement='linear')
print(f"Parameters: {ansatz.num_parameters}")  # 8 for 2 qubits, 2 layers
ansatz.decompose().draw('mpl')
```

#### Symmetry-Aware Ansatz (Novel Contribution)

For a simply-supported beam, the fundamental mode shape is symmetric (both halves of the beam deflect equally). We can encode this into the ansatz by constraining certain rotation angles to be equal:

```python
from qiskit.circuit import QuantumCircuit, ParameterVector

theta = ParameterVector('θ', 4)  # Fewer params due to symmetry constraint
qc = QuantumCircuit(2)
qc.ry(theta[0], 0)
qc.ry(theta[0], 1)  # SAME parameter — symmetry enforced
qc.cx(0, 1)
qc.ry(theta[1], 0)
qc.ry(theta[1], 1)  # SAME parameter
qc.cx(0, 1)
qc.ry(theta[2], 0)
qc.ry(theta[3], 1)  # Different for asymmetric modes
```

Does this symmetry-constrained ansatz converge faster? That is one of the research questions.

### 6.5 Optimizers

| Optimizer | Type | Best For | Qiskit Import |
|---|---|---|---|
| **COBYLA** | Gradient-free | Clean simulator runs, stable convergence | `from qiskit_algorithms.optimizers import COBYLA` |
| **SPSA** | Gradient-free | Noisy hardware, shot-based estimation | `from qiskit_algorithms.optimizers import SPSA` |
| **L-BFGS-B** | Gradient-based | Smooth landscapes, statevector simulator | `from qiskit_algorithms.optimizers import L_BFGS_B` |
| **SLSQP** | Gradient-based | Constrained optimization | `from qiskit_algorithms.optimizers import SLSQP` |

**Recommendation:** Start with COBYLA (maxiter=500) for simulator runs. Switch to SPSA for IBM hardware runs.

### 6.6 Finding Higher Modes — Deflation

VQE naturally finds the **minimum** eigenvalue (fundamental frequency). To find the 2nd, 3rd modes, use **VQE Deflation**:

After finding the ground state `|φ₁⟩`, modify the Hamiltonian:
```
H' = H + λ|φ₁⟩⟨φ₁|    (add a penalty for the ground state, pushing VQE to find the next)
```

Where `λ` is a large positive number (larger than the gap between eigenvalues). Run VQE again on `H'` → finds the 1st excited state (2nd mode).

```python
from qiskit.quantum_info import SparsePauliOp, Statevector

# After finding ground state φ1:
phi1 = result.eigenstate  # Ground state from VQE
penalty = 10.0  # Large enough to shift ground state above 1st excited state

# Build projector |φ1⟩⟨φ1| as SparsePauliOp
phi1_op = SparsePauliOp.from_operator(np.outer(phi1, phi1.conj()))
H_modified = hamiltonian + penalty * phi1_op

# Run VQE again on H_modified → finds 2nd mode
result2 = vqe.compute_minimum_eigenvalue(H_modified)
omega_2 = np.sqrt(result2.eigenvalue.real)
```

---

## 7. Structural Systems to Model

### 7.1 Recommended Progression

Start with the simplest system, validate fully, then move to more complex ones. Never skip validation.

```
Week 1: 2-DOF Spring-Mass ──► Euler-Bernoulli Beam (2 elements)
Week 2: Slender Column (Buckling) ──► Beam with Damage
Week 3: Portal Frame (3 members) ──► Composite Beam (optional)
```

### 7.2 System Specifications

#### System 1: 2-DOF Spring-Mass (Warm-Up Only)
```
k₁        k₂        k₃
──/\/\/──[m₁]──/\/\/──[m₂]──/\/\/──
```
- **DOF:** 2 (displacements of m₁ and m₂)
- **Qubits:** 1
- **K matrix:** `[[k₁+k₂, -k₂], [-k₂, k₂+k₃]]`
- **M matrix:** `[[m₁, 0], [0, m₂]]`
- **Analytical frequencies:** Solve 2×2 eigenvalue problem directly
- **Purpose:** Validate pipeline. Should take < 1 hour. Not the main result.

#### System 2: Euler-Bernoulli Beam — 2 Elements (MAIN SYSTEM)
```
Pin ●────────────────────────────────● Pin
    0        Node 1        Node 2        L
    ←────── L/2 ──────►←────── L/2 ──────►
```
- **DOF:** 6 total, 4 after BCs (remove pin supports → zero transverse displacement at ends)
- **Free DOF:** `[v₁, θ₁, v₂, θ₂]` — midpoint displacement, end rotations, midpoint rotation
- **Qubits:** 2
- **Pauli terms:** max 16, typically 8-12 non-zero
- **Parameters (HEA, 2 layers):** 8
- **IBM gate count:** ~16 gates at circuit depth ~12
- **Properties:** E = 200 GPa (steel), I = 8.33×10⁻⁶ m⁴, L = 1 m, ρ = 7850 kg/m³, A = 0.01 m²
- **Analytical ω₁:** `π² × √(EI/ρAL⁴)` ≈ 987 rad/s for these properties

#### System 3: Slender Column — Buckling Analysis
Same FEA setup as System 2, but:
- Replace ω² with **critical buckling load** P_cr
- Modified eigenvalue problem: `(K - P × K_G) φ = 0` where K_G is the geometric stiffness matrix
- Near P_cr, the effective stiffness matrix becomes nearly singular → very high condition number
- **Novel angle:** Does VQE convergence degrade as P → P_cr? How steep is the degradation?

```python
# Geometric stiffness matrix for beam element
def geometric_stiffness(P, L):
    return (P/30/L) * np.array([
        [ 36,   3*L,  -36,   3*L],
        [  3*L,  4*L²,  -3*L, -L²],
        [-36,  -3*L,   36,  -3*L],
        [  3*L,  -L²,  -3*L,  4*L²]
    ])

# K_eff = K - P * K_G
# Find P_cr where smallest eigenvalue of K_eff → 0
```

#### System 4: Beam with Simulated Crack (Damage Detection)
- Take System 2 (simply supported beam)
- Reduce local stiffness of element 1 by factor `(1 - d)` where `d` is damage severity
- `d = 0`: intact beam, `d = 0.1`: 10% stiffness loss, ..., `d = 0.5`: 50% loss
- Track how natural frequency shifts with damage severity

```python
# Damage model: stiffness reduction at element level
def damaged_beam_K(E, I, L, damage_factor=0.0):
    K_global = np.zeros((4, 4))
    
    # Element 1: damaged
    EI_1 = E * I * (1 - damage_factor)
    k1 = beam_element_stiffness(EI_1, L/2)
    # assemble...
    
    # Element 2: intact
    EI_2 = E * I
    k2 = beam_element_stiffness(EI_2, L/2)
    # assemble...
    
    return K_global
```

VQE should detect the frequency shift. This is **quantum structural health monitoring**.

#### System 5: Portal Frame — 3 Members (Stretch Goal)
```
    ────────────── (beam)
    │                    │
    │ (column)           │ (column)
    │                    │
    ●                    ●
  Fixed               Fixed
```
- **DOF:** 6 (two free nodes, 3 DOF each)
- **Qubits:** 3
- **Pauli terms:** up to 64
- **IBM gate count:** ~40 gates — feasible but noisy
- **Physics:** Combines axial + bending DOFs. Sway mode (horizontal frame vibration) is the critical mode for earthquake design.

#### System 6: Composite Laminated Beam (Advanced)
- Off-diagonal bending-extension coupling terms in K (from classical lamination theory)
- Denser Pauli decomposition → more non-zero terms → harder optimization landscape
- **Novel angle:** Does quantum circuit expressibility advantage appear for coupled-DOF systems vs isotropic?

### 7.3 Qubit Count vs Matrix Size

| Matrix Size | DOF | Qubits (n) | States (2ⁿ) | Pauli Terms (max 4ⁿ) |
|---|---|---|---|---|
| 2×2 | 2 | 1 | 2 | 4 |
| 4×4 | 4 | 2 | 4 | 16 |
| 8×8 | 8 | 3 | 8 | 64 |
| 16×16 | 16 | 4 | 16 | 256 |
| 32×32 | 32 | 5 | 32 | 1024 |

The qubit count grows **logarithmically** with matrix size. A 1024×1024 FEA system needs only 10 qubits. This is the quantum advantage — if the circuit depth stays manageable.

---

## 8. Full Implementation Plan — Step by Step

### Week 1: Classical FEA Baseline

#### Step 1.1 — Project Setup
```bash
# Create project structure
mkdir vqa_modal_analysis
cd vqa_modal_analysis
mkdir -p src tests data results plots

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install qiskit qiskit-aer qiskit-algorithms qiskit-ibm-runtime
pip install numpy scipy matplotlib plotly
pip install jupyter notebook
```

#### Step 1.2 — FEA Assembly Functions

Create `src/fea.py`:

```python
import numpy as np
import scipy.linalg as la

def beam_element_stiffness(EI, L):
    """
    Returns 4x4 Euler-Bernoulli beam element stiffness matrix.
    DOF order: [v_i, theta_i, v_j, theta_j]
    EI: flexural rigidity (E*I)
    L: element length
    """
    k = EI / L**3 * np.array([
        [ 12,   6*L,  -12,   6*L],
        [  6*L,  4*L**2, -6*L,  2*L**2],
        [-12,  -6*L,   12,  -6*L],
        [  6*L,  2*L**2, -6*L,  4*L**2]
    ])
    return k

def beam_element_mass(rhoA, L):
    """
    Returns 4x4 consistent mass matrix for Euler-Bernoulli beam element.
    rhoA: mass per unit length (rho * A)
    L: element length
    """
    m = rhoA * L / 420 * np.array([
        [ 156,   22*L,   54,  -13*L],
        [  22*L,  4*L**2,  13*L,  -3*L**2],
        [  54,   13*L,  156,  -22*L],
        [ -13*L,  -3*L**2, -22*L,   4*L**2]
    ])
    return m

def assemble_beam(num_elements, E, I, rho, A, L_total):
    """
    Assemble global K and M matrices for a uniform beam.
    Returns K_global (2n+2 x 2n+2) and M_global (2n+2 x 2n+2)
    where n = num_elements.
    """
    n = num_elements
    ndof = 2 * (n + 1)  # 2 DOF per node
    L_e = L_total / n   # Element length
    
    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))
    
    EI = E * I
    rhoA = rho * A
    
    for elem in range(n):
        k_e = beam_element_stiffness(EI, L_e)
        m_e = beam_element_mass(rhoA, L_e)
        
        # Global DOF indices for this element [v_i, theta_i, v_j, theta_j]
        dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]
        
        for i_local, i_global in enumerate(dofs):
            for j_local, j_global in enumerate(dofs):
                K_global[i_global, j_global] += k_e[i_local, j_local]
                M_global[i_global, j_global] += m_e[i_local, j_local]
    
    return K_global, M_global

def apply_simply_supported_bc(K, M, num_elements):
    """
    Apply simply-supported BCs: remove transverse displacement DOF at both ends.
    Returns reduced K_red and M_red.
    """
    n = num_elements
    ndof = 2 * (n + 1)
    
    # Fixed DOFs: v at node 0 (index 0) and v at node n (index 2n)
    fixed_dofs = [0, 2*n]
    free_dofs = [i for i in range(ndof) if i not in fixed_dofs]
    
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    
    return K_red, M_red, free_dofs

def apply_cantilever_bc(K, M):
    """
    Apply cantilever BCs: remove all DOFs at node 0 (fixed end).
    """
    fixed_dofs = [0, 1]
    ndof = K.shape[0]
    free_dofs = list(range(2, ndof))
    
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    
    return K_red, M_red, free_dofs

def classical_modal_analysis(K_red, M_red):
    """
    Solve generalized eigenvalue problem using scipy.
    Returns natural frequencies (rad/s) and mode shapes.
    """
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    omega = np.sqrt(np.abs(eigenvalues))  # Natural frequencies in rad/s
    return omega, eigenvectors

def analytical_simply_supported(E, I, rho, A, L, n_modes=4):
    """Analytical natural frequencies for simply-supported Euler-Bernoulli beam."""
    frequencies = []
    for n in range(1, n_modes + 1):
        omega_n = (n * np.pi / L)**2 * np.sqrt(E * I / (rho * A))
        frequencies.append(omega_n)
    return np.array(frequencies)
```

#### Step 1.3 — Validation Script

Create `src/validate_fea.py`:

```python
import numpy as np
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported

# Material and geometry: Steel beam
E = 200e9       # Young's modulus (Pa)
I = 8.33e-6     # Second moment of area (m^4)
rho = 7850.0    # Density (kg/m^3)
A = 0.01        # Cross-section area (m^2)
L = 1.0         # Beam length (m)

# Assemble
K, M = assemble_beam(num_elements=2, E=E, I=I, rho=rho, A=A, L_total=L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, num_elements=2)

# Classical solution
omega_fea, modes = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

# Validation
print("=== FEA VALIDATION ===")
print(f"{'Mode':<6} {'FEA (rad/s)':<15} {'Analytical (rad/s)':<20} {'Error %':<10}")
print("-" * 55)
for i in range(min(4, len(omega_fea))):
    err = abs(omega_fea[i] - omega_analytical[i]) / omega_analytical[i] * 100
    print(f"{i+1:<6} {omega_fea[i]:<15.2f} {omega_analytical[i]:<20.2f} {err:<10.3f}%")

print("\n✅ FEA VALIDATED" if all(
    abs(omega_fea[i] - omega_analytical[i]) / omega_analytical[i] < 0.02
    for i in range(min(4, len(omega_fea)))
) else "❌ FEA VALIDATION FAILED — Check assembly")
```

### Week 2: Quantum Pipeline Setup

#### Step 2.1 — Hamiltonian Construction

Create `src/quantum_setup.py`:

```python
import numpy as np
import scipy.linalg as la
from qiskit.quantum_info import SparsePauliOp

def build_structural_hamiltonian(K_red, M_red):
    """
    Convert structural generalized eigenvalue problem to quantum Hamiltonian.
    
    Transforms: K φ = ω² M φ
    Into: H |ψ⟩ = λ |ψ⟩  where H = M^(-1/2) K M^(-1/2), λ = ω²
    
    Returns: 
        H_np: numpy array of Hamiltonian
        hamiltonian: Qiskit SparsePauliOp
        M_half_inv: M^(-1/2) for back-transformation
    """
    # Compute M^(-1/2)
    M_half_inv = la.fractional_matrix_power(M_red, -0.5)
    
    # Form symmetric Hamiltonian
    H_np = M_half_inv @ K_red @ M_half_inv
    
    # Symmetrize (remove numerical noise)
    H_np = 0.5 * (H_np + H_np.T)
    
    # Verify Hermitian
    assert np.allclose(H_np, H_np.T, atol=1e-10), "H is not Hermitian!"
    
    # Convert to Qiskit SparsePauliOp
    hamiltonian = SparsePauliOp.from_operator(H_np)
    
    print(f"Matrix size: {H_np.shape}")
    print(f"Number of Pauli terms: {len(hamiltonian)}")
    print(f"Condition number of H: {np.linalg.cond(H_np):.2f}")
    print(f"Eigenvalue range: [{H_np.min():.4f}, {np.linalg.eigvalsh(H_np).max():.4f}]")
    
    return H_np, hamiltonian, M_half_inv

def inspect_pauli_decomposition(hamiltonian):
    """Print all Pauli terms and their coefficients."""
    print("\n=== PAULI DECOMPOSITION ===")
    print(f"{'Pauli String':<15} {'Coefficient':<15}")
    print("-" * 30)
    for pauli, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
        if abs(coeff) > 1e-10:
            print(f"{str(pauli):<15} {coeff.real:<15.6f}")
```

#### Step 2.2 — Ansatz Design

Create `src/ansatz.py`:

```python
from qiskit.circuit.library import EfficientSU2, RealAmplitudes
from qiskit.circuit import QuantumCircuit, ParameterVector
import numpy as np

def hardware_efficient_ansatz(num_qubits, reps=2):
    """Standard Hardware-Efficient Ansatz (HEA)."""
    ansatz = EfficientSU2(
        num_qubits=num_qubits,
        reps=reps,
        entanglement='linear',
        su2_gates=['ry', 'rz']
    )
    print(f"HEA: {num_qubits} qubits, {reps} reps, {ansatz.num_parameters} parameters")
    return ansatz

def symmetric_ansatz(num_qubits, reps=2):
    """
    Symmetry-aware ansatz for simply-supported beam.
    Constrains parameters to enforce mirror symmetry of mode shapes.
    Fewer parameters → faster convergence (hypothesis to test).
    """
    n_params = 2 * reps + 2
    theta = ParameterVector('θ', n_params)
    qc = QuantumCircuit(num_qubits)
    
    param_idx = 0
    for rep in range(reps):
        # Symmetric rotation layer
        for q in range(num_qubits // 2):
            qc.ry(theta[param_idx], q)
            qc.ry(theta[param_idx], num_qubits - 1 - q)  # Mirror
        param_idx += 1
        
        # Entanglement layer
        for q in range(num_qubits - 1):
            qc.cx(q, q + 1)
    
    # Final rotation layer (asymmetric for higher modes)
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

#### Step 2.3 — VQE Runner

Create `src/vqe_runner.py`:

```python
import numpy as np
import time
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B
from qiskit.primitives import Estimator

class VQEStructuralSolver:
    """
    Complete VQE solver for structural eigenvalue problems.
    Handles optimization, result extraction, and logging.
    """
    
    def __init__(self, hamiltonian, ansatz, optimizer_name='COBYLA', maxiter=500):
        self.hamiltonian = hamiltonian
        self.ansatz = ansatz
        self.optimizer_name = optimizer_name
        self.maxiter = maxiter
        
        self.cost_history = []
        self.iteration_count = 0
        
    def _get_optimizer(self):
        optimizers = {
            'COBYLA': COBYLA(maxiter=self.maxiter),
            'SPSA': SPSA(maxiter=self.maxiter),
            'L_BFGS_B': L_BFGS_B(maxiter=self.maxiter)
        }
        return optimizers[self.optimizer_name]
    
    def _callback(self, nfev, x, fx, dx):
        """Called at each optimizer iteration. Records convergence."""
        self.cost_history.append(fx)
        self.iteration_count += 1
        if self.iteration_count % 50 == 0:
            print(f"  Iteration {self.iteration_count}: cost = {fx:.6f}")
    
    def solve(self, initial_point=None):
        """Run VQE optimization. Returns eigenvalue and metadata."""
        
        estimator = Estimator()
        optimizer = self._get_optimizer()
        
        if initial_point is None:
            np.random.seed(42)
            initial_point = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)
        
        vqe = VQE(
            estimator=estimator,
            ansatz=self.ansatz,
            optimizer=optimizer,
            callback=self._callback,
            initial_point=initial_point
        )
        
        print(f"Running VQE with {self.optimizer_name}, maxiter={self.maxiter}")
        start_time = time.time()
        result = vqe.compute_minimum_eigenvalue(self.hamiltonian)
        elapsed = time.time() - start_time
        
        lambda_min = result.eigenvalue.real
        omega_vqe = np.sqrt(abs(lambda_min))
        
        print(f"\nVQE Result:")
        print(f"  λ_min = {lambda_min:.6f}")
        print(f"  ω_fundamental = {omega_vqe:.4f} rad/s")
        print(f"  Iterations: {self.iteration_count}")
        print(f"  Time: {elapsed:.2f} s")
        
        return {
            'eigenvalue': lambda_min,
            'omega': omega_vqe,
            'optimal_point': result.optimal_point,
            'optimal_circuit': result.optimal_circuit,
            'cost_history': self.cost_history,
            'iterations': self.iteration_count,
            'time': elapsed
        }
    
    def solve_excited_states(self, n_modes=3, penalty=None):
        """Find multiple natural frequencies using VQE deflation."""
        
        results = []
        H_current = self.hamiltonian
        
        for mode_idx in range(n_modes):
            print(f"\n=== Finding Mode {mode_idx + 1} ===")
            
            solver = VQEStructuralSolver(
                H_current, self.ansatz,
                self.optimizer_name, self.maxiter
            )
            result = solver.solve()
            results.append(result)
            
            if mode_idx < n_modes - 1:
                # Deflation: add penalty for found eigenstate
                phi = result['optimal_circuit']
                # Build projector |φ⟩⟨φ| and add to Hamiltonian
                # (simplified — use scipy for the projector construction)
                from qiskit.quantum_info import Statevector
                state = Statevector(phi)
                state_vec = state.data
                projector_np = np.outer(state_vec, state_vec.conj()).real
                
                from qiskit.quantum_info import SparsePauliOp
                lam = penalty or (result['eigenvalue'] + 
                                   abs(self.hamiltonian.coeffs.real).sum())
                proj_op = SparsePauliOp.from_operator(lam * projector_np)
                H_current = H_current + proj_op
        
        return results

def classical_reference(hamiltonian_np):
    """Classical exact eigenvalue solution for comparison."""
    eigenvalues = np.linalg.eigvalsh(hamiltonian_np)
    return eigenvalues
```

### Week 3: Novel Study — Ill-Conditioning Analysis

#### Step 3.1 — Systematic Parameter Study

Create `src/novel_study.py`:

```python
import numpy as np
import pandas as pd
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from quantum_setup import build_structural_hamiltonian
from vqe_runner import VQEStructuralSolver
from ansatz import hardware_efficient_ansatz

def slenderness_study(E, I_ref, rho, A, L_range, n_elements=2):
    """
    Study how beam slenderness (L/r) affects VQE convergence.
    
    As L increases → K becomes ill-conditioned → does VQE struggle more?
    """
    
    results = []
    
    for L in L_range:
        # Slenderness ratio: L/r where r = sqrt(I/A)
        r = np.sqrt(I_ref / A)
        slenderness = L / r
        
        # Assemble FEA
        K, M = assemble_beam(n_elements, E, I_ref, rho, A, L)
        K_red, M_red, _ = apply_simply_supported_bc(K, M, n_elements)
        
        # Build quantum Hamiltonian
        H_np, hamiltonian, _ = build_structural_hamiltonian(K_red, M_red)
        condition_number = np.linalg.cond(H_np)
        
        # Classical reference
        omega_ref, _ = classical_modal_analysis(K_red, M_red)
        
        # VQE solve
        ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)
        solver = VQEStructuralSolver(hamiltonian, ansatz, maxiter=500)
        vqe_result = solver.solve()
        
        # Compute error
        omega_vqe = vqe_result['omega']
        error = abs(omega_vqe - omega_ref[0]) / omega_ref[0] * 100
        
        results.append({
            'L': L,
            'slenderness': slenderness,
            'condition_number': condition_number,
            'omega_ref': omega_ref[0],
            'omega_vqe': omega_vqe,
            'error_pct': error,
            'iterations': vqe_result['iterations'],
            'final_cost': vqe_result['cost_history'][-1] if vqe_result['cost_history'] else None
        })
        
        print(f"L={L:.2f}m | Slenderness={slenderness:.0f} | "
              f"Condition={condition_number:.1f} | "
              f"Error={error:.2f}% | Iters={vqe_result['iterations']}")
    
    return pd.DataFrame(results)

def damage_detection_study(E, I, rho, A, L, damage_levels, n_elements=2):
    """
    Study how stiffness reduction (simulated crack) affects VQE-computed frequencies.
    
    damage_levels: list of damage fractions, e.g., [0.0, 0.1, 0.2, 0.3, 0.5]
    """
    
    results = []
    
    for d in damage_levels:
        # Damaged beam: element 1 has reduced stiffness
        K_damaged = np.zeros((2*(n_elements+1), 2*(n_elements+1)))
        M_full = np.zeros((2*(n_elements+1), 2*(n_elements+1)))
        
        from fea import beam_element_stiffness, beam_element_mass
        L_e = L / n_elements
        rhoA = rho * A
        
        # Assemble with damage
        EI_values = [E * I * (1 - d), E * I]  # First element damaged
        for elem in range(n_elements):
            k_e = beam_element_stiffness(EI_values[elem], L_e)
            m_e = beam_element_mass(rhoA, L_e)
            dofs = [2*elem, 2*elem+1, 2*elem+2, 2*elem+3]
            for i_l, i_g in enumerate(dofs):
                for j_l, j_g in enumerate(dofs):
                    K_damaged[i_g, j_g] += k_e[i_l, j_l]
                    M_full[i_g, j_g] += m_e[i_l, j_l]
        
        # Apply BCs
        fixed_dofs = [0, 2*n_elements]
        free_dofs = [i for i in range(2*(n_elements+1)) if i not in fixed_dofs]
        K_red = K_damaged[np.ix_(free_dofs, free_dofs)]
        M_red = M_full[np.ix_(free_dofs, free_dofs)]
        
        # Classical solve
        omega_ref, _ = classical_modal_analysis(K_red, M_red)
        
        # VQE solve
        H_np, hamiltonian, _ = build_structural_hamiltonian(K_red, M_red)
        ansatz = hardware_efficient_ansatz(num_qubits=2, reps=2)
        solver = VQEStructuralSolver(hamiltonian, ansatz, maxiter=500)
        vqe_result = solver.solve()
        
        results.append({
            'damage': d,
            'damage_pct': d * 100,
            'omega_ref': omega_ref[0],
            'omega_vqe': vqe_result['omega'],
            'freq_shift_pct': (omega_ref[0] - results[0]['omega_ref']) / results[0]['omega_ref'] * 100 if results else 0,
            'vqe_error_pct': abs(vqe_result['omega'] - omega_ref[0]) / omega_ref[0] * 100,
        })
    
    return pd.DataFrame(results)
```

### Week 4: Visualizations

#### Step 4.1 — All Plots

Create `src/visualize.py`:

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch

# ─── Color Scheme ─────────────────────────────────────────────────────────────
NAVY    = "#1A2151"
BLUE    = "#0D6EFD"
CYAN    = "#00B4D8"
GREEN   = "#0A7C59"
RED     = "#C0392B"
ORANGE  = "#E67E22"
GREY    = "#566573"
LIGHT   = "#EBF5FB"

def plot_convergence(cost_history, omega_vqe, omega_ref, title="VQE Convergence"):
    """Plot VQE cost function convergence."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold', color=NAVY)
    
    # Cost convergence
    ax1.plot(cost_history, color=BLUE, linewidth=1.5, alpha=0.8)
    ax1.axhline(y=omega_ref**2, color=RED, linestyle='--', 
                label=f'Classical λ₁ = {omega_ref**2:.4f}', linewidth=2)
    ax1.set_xlabel("Iteration", fontsize=12)
    ax1.set_ylabel("Cost ⟨ψ(θ)|H|ψ(θ)⟩", fontsize=12)
    ax1.set_title("Cost Function vs Iteration", fontweight='bold')
    ax1.legend()
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.4)
    
    # Error convergence
    if omega_ref > 0:
        errors = [abs(np.sqrt(max(c, 0)) - omega_ref) / omega_ref * 100 
                  for c in cost_history if c > 0]
        ax2.semilogy(errors, color=ORANGE, linewidth=1.5)
        ax2.set_xlabel("Iteration", fontsize=12)
        ax2.set_ylabel("Frequency Error (%)", fontsize=12)
        ax2.set_title("Frequency Error vs Iteration", fontweight='bold')
        ax2.set_facecolor(LIGHT)
        ax2.grid(True, alpha=0.4, which='both')
    
    plt.tight_layout()
    plt.savefig('results/convergence.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_mode_shapes(mode_shapes_vqe, mode_shapes_classical, n_modes=3):
    """Compare VQE and classical mode shapes."""
    fig, axes = plt.subplots(1, n_modes, figsize=(15, 5))
    fig.suptitle("Mode Shape Comparison: VQE vs Classical", 
                 fontsize=14, fontweight='bold', color=NAVY)
    
    x = np.linspace(0, 1, len(mode_shapes_classical[:, 0]) + 2)
    
    for i, ax in enumerate(axes):
        # Normalize mode shapes for comparison
        m_classical = mode_shapes_classical[:, i]
        if len(mode_shapes_vqe) > i:
            m_vqe = mode_shapes_vqe[i]
            # Align sign
            if np.dot(m_classical, m_vqe) < 0:
                m_vqe = -m_vqe
            m_vqe_norm = m_vqe / np.max(np.abs(m_vqe)) if np.max(np.abs(m_vqe)) > 0 else m_vqe
            ax.bar(range(len(m_vqe_norm)), m_vqe_norm, 
                   alpha=0.6, color=CYAN, label='VQE', width=0.4)
        
        m_classical_norm = m_classical / np.max(np.abs(m_classical))
        ax.bar(np.arange(len(m_classical_norm)) + 0.4, m_classical_norm, 
               alpha=0.6, color=RED, label='Classical', width=0.4)
        
        ax.set_title(f"Mode {i+1}", fontweight='bold')
        ax.set_xlabel("DOF Index")
        ax.set_ylabel("Normalized Amplitude")
        ax.legend()
        ax.set_facecolor(LIGHT)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/mode_shapes.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_frequency_comparison(omega_vqe_list, omega_classical, labels=None):
    """Bar chart comparing VQE vs classical natural frequencies."""
    n = len(omega_classical)
    x = np.arange(n)
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor(LIGHT)
    
    bars1 = ax.bar(x - width/2, omega_classical, width, 
                    label='Classical (scipy)', color=NAVY, alpha=0.85, edgecolor='white')
    
    colors = [BLUE, CYAN, GREEN, ORANGE]
    for i, (omega_vqe, label) in enumerate(zip(omega_vqe_list, 
                                                 labels or [f'VQE Run {i+1}']*len(omega_vqe_list))):
        ax.bar(x + width/2, omega_vqe[:n], width/len(omega_vqe_list),
               label=label, color=colors[i % len(colors)], alpha=0.85, 
               edgecolor='white', 
               align='center',
               left=width/2 + (i - len(omega_vqe_list)//2) * width/len(omega_vqe_list))
    
    ax.set_xlabel("Mode Number", fontsize=12)
    ax.set_ylabel("Natural Frequency (rad/s)", fontsize=12)
    ax.set_title("Natural Frequencies: VQE vs Classical", 
                  fontsize=14, fontweight='bold', color=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Mode {i+1}" for i in range(n)])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('results/frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_ill_conditioning_study(df):
    """
    Plot condition number vs VQE iterations — the main novel result.
    df: DataFrame from slenderness_study() with columns:
        slenderness, condition_number, iterations, error_pct
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Novel Result: Structural Ill-Conditioning vs VQE Convergence", 
                 fontsize=14, fontweight='bold', color=NAVY)
    
    # Plot 1: Condition number vs iterations
    axes[0].scatter(df['condition_number'], df['iterations'], 
                     color=BLUE, s=100, zorder=5, edgecolors=NAVY, linewidths=1.5)
    axes[0].set_xlabel("Condition Number κ(H)", fontsize=11)
    axes[0].set_ylabel("VQE Iterations to Convergence", fontsize=11)
    axes[0].set_title("Does ill-conditioning slow down VQE?", fontweight='bold')
    axes[0].set_xscale('log')
    axes[0].set_facecolor(LIGHT)
    axes[0].grid(True, alpha=0.4)
    
    # Annotate points with slenderness
    for _, row in df.iterrows():
        axes[0].annotate(f"λ={row['slenderness']:.0f}", 
                          (row['condition_number'], row['iterations']),
                          textcoords="offset points", xytext=(5, 5), fontsize=8)
    
    # Plot 2: Slenderness vs frequency error
    axes[1].plot(df['slenderness'], df['error_pct'], 
                  'o-', color=ORANGE, linewidth=2, markersize=8, markeredgecolor=NAVY)
    axes[1].set_xlabel("Slenderness Ratio L/r", fontsize=11)
    axes[1].set_ylabel("VQE Frequency Error (%)", fontsize=11)
    axes[1].set_title("Slenderness vs Solution Accuracy", fontweight='bold')
    axes[1].set_facecolor(LIGHT)
    axes[1].grid(True, alpha=0.4)
    axes[1].axhline(y=2, color=RED, linestyle='--', alpha=0.7, label='2% threshold')
    axes[1].legend()
    
    # Plot 3: Frequency vs slenderness (classical + VQE)
    axes[2].plot(df['slenderness'], df['omega_ref'], 
                  's--', color=RED, linewidth=2, markersize=8, label='Classical')
    axes[2].plot(df['slenderness'], df['omega_vqe'], 
                  'o-', color=GREEN, linewidth=2, markersize=8, label='VQE')
    axes[2].set_xlabel("Slenderness Ratio L/r", fontsize=11)
    axes[2].set_ylabel("Fundamental Frequency ω₁ (rad/s)", fontsize=11)
    axes[2].set_title("Frequency vs Slenderness", fontweight='bold')
    axes[2].legend()
    axes[2].set_facecolor(LIGHT)
    axes[2].grid(True, alpha=0.4)
    
    plt.tight_layout()
    plt.savefig('results/ill_conditioning_study.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_damage_detection(df):
    """Frequency shift vs damage severity — quantum structural health monitoring."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Quantum Structural Health Monitoring via Frequency Shift", 
                 fontsize=14, fontweight='bold', color=NAVY)
    
    # Frequency vs damage level
    ax1.plot(df['damage_pct'], df['omega_ref'], 
              's--', color=RED, linewidth=2, markersize=8, label='Classical')
    ax1.plot(df['damage_pct'], df['omega_vqe'], 
              'o-', color=BLUE, linewidth=2, markersize=8, label='VQE')
    ax1.set_xlabel("Stiffness Reduction (% damage)", fontsize=12)
    ax1.set_ylabel("Fundamental Frequency ω₁ (rad/s)", fontsize=12)
    ax1.set_title("Natural Frequency Drops with Damage", fontweight='bold')
    ax1.legend()
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.4)
    
    # Frequency shift (% change from undamaged)
    omega_0 = df['omega_ref'].iloc[0]
    freq_shift_classical = (df['omega_ref'] - omega_0) / omega_0 * 100
    freq_shift_vqe = (df['omega_vqe'] - omega_0) / omega_0 * 100
    
    ax2.plot(df['damage_pct'], freq_shift_classical, 
              's--', color=RED, linewidth=2, markersize=8, label='Classical shift')
    ax2.plot(df['damage_pct'], freq_shift_vqe, 
              'o-', color=BLUE, linewidth=2, markersize=8, label='VQE-detected shift')
    ax2.set_xlabel("Stiffness Reduction (% damage)", fontsize=12)
    ax2.set_ylabel("Frequency Shift from Intact (%)", fontsize=12)
    ax2.set_title("VQE Detects Damage via Frequency Shift", fontweight='bold')
    ax2.legend()
    ax2.set_facecolor(LIGHT)
    ax2.grid(True, alpha=0.4)
    ax2.axhline(0, color='black', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig('results/damage_detection.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Week 5: IBM Hardware Validation

#### Step 5.1 — IBM Submission Script

Create `src/ibm_validation.py`:

```python
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Estimator, Options
from qiskit_ibm_runtime.options import ResilienceOptions
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import numpy as np

def run_on_ibm_hardware(hamiltonian, optimal_circuit, token=None):
    """
    Run optimized VQE circuit on real IBM quantum hardware.
    Use ONLY the final circuit (theta*) — NOT the training loop.
    
    Steps:
    1. Connect to IBM
    2. Select least-busy backend
    3. Transpile circuit for hardware topology
    4. Run with ZNE error mitigation
    5. Return mitigated expectation value
    """
    
    # Connect to IBM Quantum
    if token:
        QiskitRuntimeService.save_account(channel="ibm_quantum", token=token)
    service = QiskitRuntimeService()
    
    # Get least busy real backend with enough qubits
    backend = service.least_busy(
        operational=True, 
        simulator=False,
        min_num_qubits=optimal_circuit.num_qubits
    )
    print(f"Using backend: {backend.name}")
    print(f"Qubits: {backend.num_qubits}, Gates: ~{backend.num_qubits * 100}/min budget")
    
    # Transpile circuit for hardware topology
    pm = generate_preset_pass_manager(
        optimization_level=3, 
        backend=backend
    )
    transpiled_circuit = pm.run(optimal_circuit)
    print(f"Transpiled circuit depth: {transpiled_circuit.depth()}")
    print(f"Gate count: {transpiled_circuit.count_ops()}")
    
    with Session(service=service, backend=backend) as session:
        
        # Run 1: No mitigation (baseline)
        options_raw = Options()
        options_raw.execution.shots = 2048
        options_raw.resilience_level = 0
        
        estimator_raw = Estimator(session=session, options=options_raw)
        job_raw = estimator_raw.run(transpiled_circuit, hamiltonian)
        result_raw = job_raw.result()
        ev_raw = result_raw.values[0]
        print(f"IBM Raw (no mitigation): ⟨H⟩ = {ev_raw:.6f}")
        
        # Run 2: ZNE mitigation (Level 1)
        options_zne = Options()
        options_zne.execution.shots = 2048
        options_zne.resilience_level = 1  # ZNE
        
        estimator_zne = Estimator(session=session, options=options_zne)
        job_zne = estimator_zne.run(transpiled_circuit, hamiltonian)
        result_zne = job_zne.result()
        ev_zne = result_zne.values[0]
        print(f"IBM ZNE (mitigated): ⟨H⟩ = {ev_zne:.6f}")
    
    return {
        'backend': backend.name,
        'raw_expectation': ev_raw,
        'zne_expectation': ev_zne,
        'omega_raw': np.sqrt(max(ev_raw, 0)),
        'omega_zne': np.sqrt(max(ev_zne, 0)),
        'circuit_depth': transpiled_circuit.depth()
    }

def compare_simulator_vs_hardware(ev_simulator, ev_ibm_raw, ev_ibm_zne, omega_classical):
    """Print three-way comparison table."""
    print("\n" + "="*65)
    print(f"{'Source':<25} {'⟨H⟩':<15} {'ω (rad/s)':<15} {'Error %':<10}")
    print("="*65)
    
    for name, ev in [("Classical (exact)", omega_classical**2),
                      ("Simulator (VQE)", ev_simulator),
                      ("IBM Raw", ev_ibm_raw),
                      ("IBM ZNE Mitigated", ev_ibm_zne)]:
        omega = np.sqrt(max(ev, 0))
        err = abs(omega - omega_classical) / omega_classical * 100
        marker = "  ✅" if err < 2 else "  ⚠️" if err < 10 else "  ❌"
        print(f"{name:<25} {ev:<15.6f} {omega:<15.4f} {err:<10.2f}%{marker}")
    
    print("="*65)
    noise_error = abs(ev_ibm_raw - ev_simulator)
    mitigation_improvement = abs(ev_ibm_raw - ev_simulator) - abs(ev_ibm_zne - ev_simulator)
    print(f"\nHardware noise error: {noise_error:.6f}")
    print(f"ZNE improvement: {mitigation_improvement:.6f} ({mitigation_improvement/noise_error*100:.1f}% correction)")
```

---

## 9. Novel Contribution — The Research Gap

### 9.1 What Exists in Literature

Papers that exist:
- VQE for molecular Hamiltonian (thousands of papers — quantum chemistry)
- General VQE benchmark studies on toy Hamiltonians
- A few papers applying VQE to structural matrices (very recent, 2022-2024)

### 9.2 What Does NOT Exist

No existing paper has studied:

#### Gap 1: Structural Ill-Conditioning vs VQE Convergence Landscape
In quantum chemistry, VQE is applied to well-conditioned molecular Hamiltonians with bounded eigenvalue spectra. Structural matrices near instability (slender columns near buckling, damaged beams) have **condition numbers that blow up**. How does this affect the VQE energy landscape flatness (barren plateaus)? Does convergence degrade exponentially with condition number? This is practically significant for structural health monitoring applications.

#### Gap 2: Physically-Motivated Ansatz for Structural Problems
In quantum chemistry, problem-inspired ansatz (UCCSD) outperform hardware-efficient ansatz for molecular systems because they encode physical prior knowledge. For structural mechanics, mode shapes have known symmetry properties (simply-supported → symmetric fundamental mode, antisymmetric second mode). Can encoding this into the ansatz circuit architecture reduce convergence iterations by 30-50%? No paper has tested this.

#### Gap 3: Systematic Damage Detection via VQE Frequency Shift
Using VQE as a structural health monitoring tool — tracking frequency shifts as stiffness is progressively reduced — has not been studied systematically. The key question: at what damage level does VQE's frequency estimate diverge from the classical reference due to ill-conditioning? This sets the practical detection threshold.

### 9.3 Your Novel Contribution in One Paragraph

> This study systematically characterizes how structural ill-conditioning — specifically slenderness ratio in beams, proximity to critical buckling loads in columns, and local stiffness reduction from simulated damage — affects the VQE energy landscape, convergence rate, and solution fidelity for structural eigenvalue problems. Furthermore, it introduces and evaluates physically-motivated ansatz circuits that exploit known mode shape symmetry properties of structural systems, comparing convergence behaviour against hardware-efficient ansatz of identical parameter count. Results provide the first quantitative characterization of VQE applicability boundaries for structural health monitoring applications on NISQ hardware.

---

## 10. Visualizations

### Complete Visualization List

| Plot | What It Shows | File | Novel? |
|---|---|---|---|
| Cost convergence curve | C(θ) vs iteration | `convergence.png` | No |
| Mode shape comparison | VQE vs classical eigenvectors | `mode_shapes.png` | No |
| Frequency comparison bar chart | All modes, VQE vs classical | `frequency_comparison.png` | No |
| Quantum circuit diagram | `circuit.draw('mpl')` — actual gates | `circuit.png` | No |
| **Condition number vs iterations** | Main novel result | `ill_conditioning_study.png` | **YES** |
| **Frequency vs damage level** | Damage detection curve | `damage_detection.png` | **YES** |
| **Ansatz comparison convergence** | HEA vs symmetric ansatz | `ansatz_comparison.png` | **YES** |
| IBM noise characterization | Raw vs ZNE vs simulator | `ibm_comparison.png` | No |
| Pauli decomposition bar chart | Which Pauli terms dominate | `pauli_terms.png` | No |

### Showstopper Visualization: Animated Convergence

```python
def animate_vqe_convergence(cost_history, title="VQE Finding the Ground State Energy"):
    """
    Animated plot showing cost function collapsing to minimum eigenvalue.
    Save as GIF for presentation.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor('#0A0E2A')
    ax.set_xlim(0, len(cost_history))
    ax.set_ylim(min(cost_history) * 0.9, max(cost_history) * 1.1)
    ax.set_xlabel("Iteration", fontsize=12, color='white')
    ax.set_ylabel("⟨ψ(θ)|H|ψ(θ)⟩", fontsize=12, color='white')
    ax.set_title(title, fontsize=13, color='#00D4FF', fontweight='bold')
    ax.tick_params(colors='white')
    
    line, = ax.plot([], [], color='#00D4FF', linewidth=2)
    point, = ax.plot([], [], 'o', color='#FF6B6B', markersize=8)
    
    def init():
        line.set_data([], [])
        point.set_data([], [])
        return line, point
    
    def update(frame):
        x = list(range(frame + 1))
        y = cost_history[:frame + 1]
        line.set_data(x, y)
        point.set_data([frame], [cost_history[frame]])
        return line, point
    
    anim = animation.FuncAnimation(
        fig, update, frames=len(cost_history),
        init_func=init, interval=20, blit=True
    )
    
    anim.save('results/vqe_convergence.gif', 
              writer='pillow', fps=30, dpi=100)
    plt.close()
    print("Animation saved: results/vqe_convergence.gif")
```

---

## 11. IBM Hardware Strategy

### Budget: 20 Minutes / Month

This is tight. Use it strategically:

| Activity | Shots | Time Estimate | When |
|---|---|---|---|
| 2-qubit validation run | 2048 | ~2 min | After simulator confirms convergence |
| ZNE mitigation run | 2048 × 3 noise levels | ~6 min | Same circuit, 3 scaled versions |
| Excited state validation | 2048 | ~2 min | If time permits |
| Damage detection (1 point) | 2048 | ~2 min | For showstopper demo |
| **Total** | | **~12 min** | Leaves 8 min buffer |

**Never run the training loop on IBM hardware.** The optimizer needs 300-500 circuit evaluations — at 2 min each, that's 10+ hours. Train on simulator, validate on IBM.

### What You Report from IBM Results

A full IBM results section includes:
1. Backend used (e.g., ibm_sherbrooke, 127 qubits)
2. Transpiled circuit depth and gate count
3. Raw expectation value vs simulator expectation value
4. ZNE-mitigated value
5. Three-way comparison table (simulator / IBM raw / IBM ZNE)
6. How noise affects the computed natural frequency (in physical units: rad/s)

---

## 12. Complete Code Reference

### `main.py` — Full Pipeline Runner

```python
"""
VQA Modal Analysis — Complete Pipeline
Run this file to execute the full project.
"""

import numpy as np
import os
os.makedirs('results', exist_ok=True)

from src.fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis, analytical_simply_supported
from src.quantum_setup import build_structural_hamiltonian, inspect_pauli_decomposition
from src.ansatz import hardware_efficient_ansatz, symmetric_ansatz
from src.vqe_runner import VQEStructuralSolver, classical_reference
from src.visualize import (plot_convergence, plot_mode_shapes, 
                            plot_frequency_comparison, plot_ill_conditioning_study,
                            plot_damage_detection)
from src.novel_study import slenderness_study, damage_detection_study

# ─── MATERIAL & GEOMETRY ────────────────────────────────────────────────────
E = 200e9       # Young's modulus (Pa) — steel
I = 8.33e-6     # Second moment of area (m^4)
rho = 7850.0    # Density (kg/m^3)
A = 0.01        # Cross-section area (m^2)
L = 1.0         # Beam length (m)
n_elem = 2      # Number of FEA elements

# ─── STEP 1: Classical FEA ──────────────────────────────────────────────────
print("="*60)
print("STEP 1: CLASSICAL FEA BASELINE")
print("="*60)

K, M = assemble_beam(n_elem, E, I, rho, A, L)
K_red, M_red, free_dofs = apply_simply_supported_bc(K, M, n_elem)
omega_classical, modes_classical = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

print(f"Classical natural frequencies (rad/s): {omega_classical}")
print(f"Analytical:                            {omega_analytical[:len(omega_classical)]}")

# ─── STEP 2: Quantum Hamiltonian ────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: QUANTUM HAMILTONIAN CONSTRUCTION")
print("="*60)

H_np, hamiltonian, M_half_inv = build_structural_hamiltonian(K_red, M_red)
inspect_pauli_decomposition(hamiltonian)

# ─── STEP 3: VQE on Simulator ───────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3: VQE ON QISKIT AER SIMULATOR")
print("="*60)

ansatz_hea = hardware_efficient_ansatz(num_qubits=2, reps=2)
solver = VQEStructuralSolver(hamiltonian, ansatz_hea, 
                              optimizer_name='COBYLA', maxiter=500)
result_hea = solver.solve()

print(f"\nFundamental frequency (VQE):       {result_hea['omega']:.4f} rad/s")
print(f"Fundamental frequency (Classical): {omega_classical[0]:.4f} rad/s")
print(f"Error: {abs(result_hea['omega'] - omega_classical[0])/omega_classical[0]*100:.3f}%")

# ─── STEP 4: Multiple Modes ─────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 4: FINDING HIGHER MODES (DEFLATION)")
print("="*60)

multi_result = solver.solve_excited_states(n_modes=3)
omega_vqe_all = [r['omega'] for r in multi_result]
print(f"\nAll VQE frequencies: {omega_vqe_all}")
print(f"All Classical:       {list(omega_classical[:3])}")

# ─── STEP 5: Novel Study ────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5: NOVEL STUDY — ILL-CONDITIONING")
print("="*60)

L_range = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
df_slenderness = slenderness_study(E, I, rho, A, L_range)
print(df_slenderness.to_string())
df_slenderness.to_csv('results/slenderness_study.csv', index=False)

damage_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
df_damage = damage_detection_study(E, I, rho, A, L, damage_levels)
print(df_damage.to_string())
df_damage.to_csv('results/damage_study.csv', index=False)

# ─── STEP 6: All Visualizations ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 6: GENERATING ALL PLOTS")
print("="*60)

plot_convergence(result_hea['cost_history'], result_hea['omega'], omega_classical[0])
plot_frequency_comparison([np.array(omega_vqe_all)], omega_classical[:3], 
                           labels=['VQE (HEA, 2 reps)'])
plot_ill_conditioning_study(df_slenderness)
plot_damage_detection(df_damage)

print("\n✅ Full pipeline complete. Results saved to results/")
```

---

## 13. Technology Stack

| Tool | Version | Purpose | Install |
|---|---|---|---|
| `qiskit` | ≥1.0 | Core quantum computing framework | `pip install qiskit` |
| `qiskit-aer` | ≥0.14 | Local quantum simulator | `pip install qiskit-aer` |
| `qiskit-algorithms` | ≥0.3 | VQE, VQLS, optimizers | `pip install qiskit-algorithms` |
| `qiskit-ibm-runtime` | ≥0.20 | IBM hardware access + ZNE | `pip install qiskit-ibm-runtime` |
| `numpy` | ≥1.24 | Matrix operations, FEA assembly | `pip install numpy` |
| `scipy` | ≥1.10 | `eigh`, `fractional_matrix_power` | `pip install scipy` |
| `matplotlib` | ≥3.7 | All plots, animations | `pip install matplotlib` |
| `pandas` | ≥2.0 | Results dataframes, CSV export | `pip install pandas` |
| `jupyter` | — | Interactive development | `pip install jupyter` |

### Full install command:
```bash
pip install qiskit qiskit-aer qiskit-algorithms qiskit-ibm-runtime numpy scipy matplotlib pandas jupyter
```

---

## 14. Team Task Split

### Mech Students Own

- [ ] Write `beam_element_stiffness()` and `beam_element_mass()` functions
- [ ] Write `assemble_beam()` global assembly
- [ ] Implement all boundary condition functions
- [ ] Validate FEA against analytical solutions (< 1% error required)
- [ ] Define all structural systems (geometry, material properties, BCs)
- [ ] Write `damaged_beam_K()` for damage study
- [ ] Physical interpretation: "what does the frequency shift mean mechanically?"
- [ ] Design the ill-conditioning study: which L/r values to test?
- [ ] Validate IBM results against classical reference (physical units check)

### CS Students Own

- [ ] `build_structural_hamiltonian()` — Pauli decomposition pipeline
- [ ] `hardware_efficient_ansatz()` and `symmetric_ansatz()` circuits
- [ ] `VQEStructuralSolver` class — complete VQE loop with callback
- [ ] `solve_excited_states()` — deflation for higher modes
- [ ] IBM hardware submission and ZNE setup
- [ ] All visualization functions
- [ ] Animated convergence GIF
- [ ] `slenderness_study()` and `damage_detection_study()` runners
- [ ] Performance profiling (circuit depth, gate count, shot count)

### Both Teams

- [ ] Interpreting ill-conditioning study results
- [ ] Writing the final report / presentation
- [ ] Comparing HEA vs symmetric ansatz (joint discussion)
- [ ] Deciding which structural systems to include as main results

---

## 15. Expected Results & Deliverables

### Minimum Results (Pass)
- [ ] FEA validated against analytical formula (< 1% error)
- [ ] VQE converges on 2-qubit Hamiltonian (simulator)
- [ ] Fundamental frequency within 2% of classical
- [ ] At least 1 IBM hardware run with ZNE comparison

### Good Results (Merit)
- [ ] 3 natural frequencies found via deflation
- [ ] Ill-conditioning study: 4+ slenderness ratios tested
- [ ] Damage detection: 5+ damage levels, clear frequency shift trend
- [ ] Convergence curves for all cases

### Excellent Results (Distinction)
- [ ] HEA vs symmetric ansatz comparison (convergence speed and accuracy)
- [ ] IBM noise characterization: noise error vs circuit depth
- [ ] Animated convergence visualization
- [ ] Portal frame (3 qubits) results
- [ ] Clear identification of "VQE breakdown" condition number threshold

### Final Deliverables

| Item | Format | Content |
|---|---|---|
| Jupyter Notebook | `.ipynb` | Full reproducible pipeline |
| Results CSV | `.csv` | Slenderness + damage study data |
| Plots | `.png` + `.gif` | All 9 visualizations |
| Report | `.pdf` | 8-12 pages with all results and novel contribution |
| Presentation | `.pptx` | 12-15 slides for final presentation |

---

## 16. Ratings & Comparison

### Project Ratings

| Dimension | Score | Notes |
|---|---|---|
| Hardware Feasibility | 8/10 | 2-3 qubits runs cleanly on IBM; 20 min/month is sufficient |
| Theoretical Novelty | 8/10 | Ill-conditioning + VQE: no paper covers this for structural systems |
| Mech Relevance | 10/10 | Modal analysis is core structural dynamics. Zero forced mapping. |
| CS Engagement | 8/10 | Algorithm, circuit design, optimization, data analysis all present |
| Scope Fit (3rd Year) | 8/10 | Clear pipeline, expandable to buckling/damage/composites |
| Publishable Potential | 7/10 | Damage detection + ill-conditioning study = mid-tier journal |
| **Overall** | **8/10** | **Top recommended standalone project** |

### Comparison vs Other Topics

| Topic | Novelty | Feasibility | Mech | Overall |
|---|---|---|---|---|
| **VQA Modal Analysis (this)** | **8** | **8** | **10** | **8** |
| VQLS Truss FEA | 7 | 7 | 9 | 7 |
| Hybrid Quantum PINN | 8 | 6 | 7 | 7 |
| HHL for FEA | 5 | 4 | 8 | 4.5 |
| Quantum CUDA speedup | 4 | 8 | 2 | 4.6 |
| Quantum Image Processing | 2 | 9 | 1 | 4.0 |

---

## 17. References & Further Reading

### Core Papers

1. **VQE Original Paper:** Peruzzo et al. (2014), "A variational eigenvalue solver on a photonic quantum processor", *Nature Communications*. — The paper that introduced VQE.

2. **Structural Quantum Computing (recent):** Search arXiv for "variational quantum eigensolver structural mechanics" — there are 2-3 recent papers (2022-2024) that do basic VQE for FEA. Your ill-conditioning study goes beyond all of them.

3. **Barren Plateaus:** McClean et al. (2018), "Barren plateaus in quantum neural network training landscapes", *Nature Communications*. — Relevant to your novel angle on convergence landscape.

4. **IBM Quantum Error Mitigation:** Kandala et al. (2019), "Error mitigation extends the computational reach of a noisy quantum processor", *Nature*. — Basis for ZNE approach.

### Textbooks

5. **Structural Dynamics (Mech):** Chopra, "Dynamics of Structures" — Chapters on modal analysis and eigenvalue problems.

6. **FEA (Mech):** Cook et al., "Concepts and Applications of Finite Element Analysis" — Stiffness and mass matrix assembly.

7. **Quantum Computing (CS):** Nielsen & Chuang, "Quantum Computation and Quantum Information" — The standard QC textbook. Chapter 5 for quantum phase estimation, which VQE builds on.

### Online Resources

8. **Qiskit Documentation:** https://docs.quantum.ibm.com — Complete API reference, tutorials on VQE.

9. **Qiskit Textbook (free):** https://learning.quantum.ibm.com — Excellent interactive tutorials on VQE from scratch.

10. **IBM Quantum Lab:** https://quantum.ibm.com — Free IBM hardware access (20 min/month on free tier).

---

*Document prepared for VQA Modal Analysis Project | COEP Technological University | Quantum Computing Minor | 3rd Year Undergraduate*

*For Mechanical + Computer Engineering students — no prior QC knowledge assumed*
