# Graph Report - .  (2026-04-24)

## Corpus Check
- Corpus is ~41,739 words - fits in a single context window. You may not need a graph.

## Summary
- 136 nodes · 161 edges · 15 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_VQE Runner  Main Pipeline|VQE Runner / Main Pipeline]]
- [[_COMMUNITY_Visualization  Plotting|Visualization / Plotting]]
- [[_COMMUNITY_VQE Core Algorithm|VQE Core Algorithm]]
- [[_COMMUNITY_Structural Mechanics  FEA|Structural Mechanics / FEA]]
- [[_COMMUNITY_FEA Implementation|FEA Implementation]]
- [[_COMMUNITY_Numerical Analysis  Convergence|Numerical Analysis / Convergence]]
- [[_COMMUNITY_Ansatz Design|Ansatz Design]]
- [[_COMMUNITY_Damage Detection Application|Damage Detection Application]]
- [[_COMMUNITY_Quantum Hamiltonian Setup|Quantum Hamiltonian Setup]]
- [[_COMMUNITY_Modal Analysis Output|Modal Analysis Output]]
- [[_COMMUNITY_Validation|Validation]]
- [[_COMMUNITY_Damping|Damping]]
- [[_COMMUNITY_Beam Geometry|Beam Geometry]]
- [[_COMMUNITY_Convergence Plot|Convergence Plot]]
- [[_COMMUNITY_Damage Detection Plot|Damage Detection Plot]]

## God Nodes (most connected - your core abstractions)
1. `Variational Quantum Eigensolver (VQE)` - 16 edges
2. `VQE Convergence` - 14 edges
3. `VQEStructuralSolver` - 13 edges
4. `Condition Number` - 6 edges
5. `Stiffness Matrix K` - 5 edges
6. `Mass Matrix M` - 5 edges
7. `Generalized Eigenvalue Problem Kφ=ω²Mφ` - 5 edges
8. `Structural Ill-Conditioning` - 5 edges
9. `assemble_beam()` - 4 edges
10. `tapered_beam_study()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `VQE Convergence` --semantically_similar_to--> `Damage Detection via Frequency Shift`  [INFERRED] [semantically similar]
  VQA_Modal_Analysis.md → results/damage_detection.png
- `VQE Convergence` --measures--> `Cost Function <psi(theta)|H|psi(theta)>`  [EXTRACTED]
  VQA_Modal_Analysis.md → results/convergence.png
- `VQE Convergence` --produces--> `Frequency Error (%)`  [EXTRACTED]
  VQA_Modal_Analysis.md → results/convergence.png
- `VQE Convergence` --compares_against--> `Classical lambda Reference`  [EXTRACTED]
  VQA_Modal_Analysis.md → results/convergence.png
- `VQA Modal Analysis - Complete Pipeline Run this file to execute the full project` --uses--> `VQEStructuralSolver`  [INFERRED]
  main.py → vqe_runner.py

## Hyperedges (group relationships)
- **VQE Pipeline for Modal Analysis** — vqe_algorithm, pauli_decomposition, hardware_efficient_ansatz_hea, symmetry_aware_ansatz, cobyla_optimizer, spsa_optimizer, vqe_deflation [EXTRACTED 0.85]
- **Structural Systems Studied** — euler_bernoulli_beam, portal_frame, composite_laminated_beam, buckling_analysis, damage_detection [EXTRACTED 0.80]
- **Novel Contribution Research Gaps** — structural_ill_conditioning, slenderness_ratio, symmetry_aware_ansatz, damage_detection, vqe_convergence, barren_plateaus [EXTRACTED 0.85]
- **Damage Detection via VQE Frequency Shift** — stiffness_reduction_damage, natural_frequency_omega, vqe_frequency, classical_frequency, frequency_shift [EXTRACTED 1.00]
- **VQE Convergence Analysis Components** — cost_function, frequency_error, classical_lambda_reference, vqe_convergence [EXTRACTED 1.00]
- **VQE Optimizer Selection Landscape** — vqe_algorithm, cobyla_optimizer, spsa_optimizer, lbfgsb_optimizer [EXTRACTED 1.00]
- **Modal Analysis Output Entities** — natural_frequencies, mode_shapes, omega_rad_s, eigenvector [EXTRACTED 1.00]

## Communities

### Community 0 - "VQE Runner / Main Pipeline"
Cohesion: 0.1
Nodes (17): VQA Modal Analysis - Complete Pipeline Run this file to execute the full project, damage_detection_study(), _linear_taper_elements(), Assemble K and M for a tapered beam.      taper_ratios[i] gives the height ratio, Study how stiffness reduction (simulated crack) affects VQE-computed frequencies, For a linearly tapered beam from h=1.0 to h=end_ratio,     compute the height ra, Study how beam taper (geometric non-uniformity) affects Hamiltonian     conditio, tapered_beam_assemble_v2() (+9 more)

### Community 1 - "Visualization / Plotting"
Cohesion: 0.11
Nodes (18): plot_beam_geometry(), plot_convergence(), plot_damage_detection(), plot_dual_convergence(), plot_frequency_comparison(), plot_ill_conditioning_study(), plot_mode_shapes(), plot_mode_shapes_continuous() (+10 more)

### Community 2 - "VQE Core Algorithm"
Cohesion: 0.14
Nodes (18): COBYLA Optimizer, Quantum Structural Health Monitoring via Damage Detection, Hardware-Efficient Ansatz (HEA), Hybrid Classical-Quantum Algorithm, IBM Quantum Hardware, L-BFGS-B Optimizer, Principle of Minimum Potential Energy, Natural Frequencies (+10 more)

### Community 3 - "Structural Mechanics / FEA"
Cohesion: 0.14
Nodes (18): Boundary Conditions, Composite Laminated Beam, Euler-Bernoulli Beam Element, Finite Element Analysis (FEA), VQE vs Classical Frequency Comparison Bar Chart, Generalized Eigenvalue Problem Kφ=ω²Mφ, Mass Matrix M, Modal Analysis (+10 more)

### Community 4 - "FEA Implementation"
Cohesion: 0.15
Nodes (14): analytical_simply_supported(), apply_cantilever_bc(), apply_simply_supported_bc(), assemble_beam(), beam_element_mass(), beam_element_stiffness(), classical_modal_analysis(), Analytical natural frequencies for simply-supported Euler-Bernoulli beam. (+6 more)

### Community 5 - "Numerical Analysis / Convergence"
Cohesion: 0.29
Nodes (12): Barren Plateau Phenomenon, Barren Plateaus, Critical Buckling Load Analysis, Classical lambda Reference, Condition Number, Cost Function <psi(theta)|H|psi(theta)>, Frequency Error (%), Structural Ill-Conditioning vs VQE Convergence Research Gap (+4 more)

### Community 6 - "Ansatz Design"
Cohesion: 0.29
Nodes (6): hardware_efficient_ansatz(), minimal_ansatz(), Symmetry-aware ansatz for simply-supported beam.     Constrains parameters to e, Minimal 2-parameter ansatz for quick testing., Standard Hardware-Efficient Ansatz (HEA)., symmetric_ansatz()

### Community 7 - "Damage Detection Application"
Cohesion: 0.48
Nodes (7): Classical Frequency, Damage Detection via Frequency Shift, Frequency Shift from Intact (%), Fundamental Frequency (rad/s), Quantum Structural Health Monitoring, Stiffness Reduction (% damage), VQE-Detected Frequency

### Community 8 - "Quantum Hamiltonian Setup"
Cohesion: 0.4
Nodes (4): build_structural_hamiltonian(), inspect_pauli_decomposition(), Print all Pauli terms and their coefficients., Convert structural generalized eigenvalue problem to quantum Hamiltonian.      T

### Community 9 - "Modal Analysis Output"
Cohesion: 0.67
Nodes (4): Eigenvector, Mode Shape (Eigenvector), Continuous Mode Shapes Visualization, Symmetric Fundamental Mode Shape Property

### Community 10 - "Validation"
Cohesion: 1.0
Nodes (0): 

### Community 11 - "Damping"
Cohesion: 1.0
Nodes (1): Natural Damping in Structures

### Community 12 - "Beam Geometry"
Cohesion: 1.0
Nodes (1): Beam Geometry Diagram

### Community 13 - "Convergence Plot"
Cohesion: 1.0
Nodes (1): VQE Convergence Plot

### Community 14 - "Damage Detection Plot"
Cohesion: 1.0
Nodes (1): Quantum Structural Health Monitoring via Frequency Shift

## Knowledge Gaps
- **49 isolated node(s):** `Standard Hardware-Efficient Ansatz (HEA).`, `Symmetry-aware ansatz for simply-supported beam.     Constrains parameters to e`, `Minimal 2-parameter ansatz for quick testing.`, `Returns 4x4 Euler-Bernoulli beam element stiffness matrix.     DOF order: [v_i,`, `Returns 4x4 consistent mass matrix for Euler-Bernoulli beam element.     rhoA:` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Validation`** (1 nodes): `validate_fea.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Damping`** (1 nodes): `Natural Damping in Structures`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Beam Geometry`** (1 nodes): `Beam Geometry Diagram`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Convergence Plot`** (1 nodes): `VQE Convergence Plot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Damage Detection Plot`** (1 nodes): `Quantum Structural Health Monitoring via Frequency Shift`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Variational Quantum Eigensolver (VQE)` connect `VQE Core Algorithm` to `Structural Mechanics / FEA`, `Numerical Analysis / Convergence`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `VQE Convergence` connect `Numerical Analysis / Convergence` to `VQE Core Algorithm`, `Damage Detection Application`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `Damage Detection via Frequency Shift` connect `Damage Detection Application` to `Numerical Analysis / Convergence`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `VQE Convergence` (e.g. with `Slenderness Ratio` and `Quantum Structural Health Monitoring via Damage Detection`) actually correct?**
  _`VQE Convergence` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `VQEStructuralSolver` (e.g. with `VQA Modal Analysis - Complete Pipeline Run this file to execute the full project` and `Assemble K and M for a tapered beam.      taper_ratios[i] gives the height ratio`) actually correct?**
  _`VQEStructuralSolver` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Condition Number` (e.g. with `VQE Convergence` and `Barren Plateau Phenomenon`) actually correct?**
  _`Condition Number` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Standard Hardware-Efficient Ansatz (HEA).`, `Symmetry-aware ansatz for simply-supported beam.     Constrains parameters to e`, `Minimal 2-parameter ansatz for quick testing.` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._