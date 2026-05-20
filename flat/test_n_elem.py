import numpy as np
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, analytical_fixed_fixed

E = 200e9
A = 0.01
rho = 7850.0
L = 1.0

for n_elem in [3,4,5,6,8]:
    K, M = assemble_truss(n_elem, E, A, rho, L)
    K_red, M_red, free_dofs = apply_fixed_fixed_bc(K, M)
    n_orig = K_red.shape[0]
    # Pad to next power of two
    n_pad = 1
    while n_pad < n_orig:
        n_pad <<= 1
    print(f"n_elem={n_elem}: free DOFs={n_orig}, padded to={n_pad}, qubits needed={int(np.log2(n_pad))}")
    omega_classical, _ = classical_modal_analysis(K_red, M_red)
    omega_analytical = analytical_fixed_fixed(E, A, rho, L, n_modes=min(3, len(omega_classical)))
    print(f"  Frequencies (rad/s):")
    for i in range(min(3, len(omega_classical))):
        error = abs(omega_classical[i] - omega_analytical[i]) / omega_analytical[i] * 100
        print(f"    Mode {i+1}: FEA={omega_classical[i]:.2f}, Analytical={omega_analytical[i]:.2f}, error={error:.2f}%")
    print()