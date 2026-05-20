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

# Sanity checks — run these before the frequency comparison
print("=== MATRIX SANITY CHECKS ===")

# Symmetry
print(f"K_red symmetric: {np.allclose(K_red, K_red.T)}")
print(f"M_red symmetric: {np.allclose(M_red, M_red.T)}")

# Positive definiteness
k_eigs = np.linalg.eigvalsh(K_red)
m_eigs = np.linalg.eigvalsh(M_red)
print(f"K_red min eigenvalue: {k_eigs.min():.4f}  (must be > 0)")
print(f"M_red min eigenvalue: {m_eigs.min():.4f}  (must be > 0)")

# Condition number
print(f"Condition number of K_red: {np.linalg.cond(K_red):.2f}")
print(f"Condition number of M_red: {np.linalg.cond(M_red):.2f}")

# Physical scale check
print(f"\nK_red[0,0] = {K_red[0,0]:.4e}  (expected ~EI/L = {E*I/L:.4e})")
print(f"M_red[1,1] = {M_red[1,1]:.4e}  (expected ~rho*A*L = {rho*A*L:.4e})")

# Classical solution
omega_fea, modes = classical_modal_analysis(K_red, M_red)
omega_analytical = analytical_simply_supported(E, I, rho, A, L)

# Validation
print("=== FEA VALIDATION ===")
print(f"{'Mode':<6} {'FEA (rad/s)':<15} {'Analytical (rad/s)':<20} {'Error %':<12} {'Status'}")
print("-" * 70)

thresholds = {0: 1.0, 1: 15.0, 2: None, 3: None}  # Mode 1: strict, Mode 2: loose, 3-4: not checked

for i in range(len(omega_fea)):
    err = abs(omega_fea[i] - omega_analytical[i]) / omega_analytical[i] * 100
    
    if thresholds[i] is None:
        status = "(mesh artifact, not validated)"
    elif err < thresholds[i]:
        status = "PASS"
    else:
        status = "FAIL"
    
    print(f"{i+1:<6} {omega_fea[i]:<15.2f} {omega_analytical[i]:<20.2f} {err:<12.3f}% {status}")

# The only check that actually matters for the quantum pipeline
mode1_error = abs(omega_fea[0] - omega_analytical[0]) / omega_analytical[0] * 100
print("\n" + "="*60)
if mode1_error < 1.0:
    print(f"MODE 1 VALIDATED - {mode1_error:.3f}% error (threshold: 1%)")
    print("   K_red and M_red are ready to hand off to the quantum pipeline.")
else:
    print(f"MODE 1 FAILED - {mode1_error:.3f}% error")
    print("   Check assembly and boundary condition implementation.")