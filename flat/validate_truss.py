import numpy as np
import pandas as pd
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, validate_truss_matrices, analytical_fixed_fixed, analytical_fixed_free


def validate_truss_analysis():
    """
    Validate truss analysis against analytical solutions
    """
    print("="*60)
    print("TRUSS VALIDATION")
    print("="*60)
    
    # Test parameters
    E = 200e9       # Pa
    A = 0.01        # m^2
    rho = 7850.0    # kg/m^3
    L = 1.0         # m
    n_elem = 8      # Increased for validation to get <1% error in mode 1
    
    print(f"Testing truss with:")
    print(f"  E = {E:.2e} Pa")
    print(f"  A = {A:.6f} m^2")
    print(f"  rho = {rho:.1f} kg/m^3")
    print(f"  L = {L:.2f} m")
    print(f"  Elements = {n_elem}")
    print()
    
    # Assemble matrices
    K, M = assemble_truss(n_elem, E, A, rho, L)
    K_red, M_red, free_dofs = apply_fixed_fixed_bc(K, M)
    
    # Validate matrices
    checks = validate_truss_matrices(K, M)
    print("Matrix validation:")
    for key, val in checks.items():
        print(f"  {key}: {val}")
    print()
    
    # Classical solution
    omega_classical, modes = classical_modal_analysis(K_red, M_red)
    omega_analytical = analytical_fixed_fixed(E, A, rho, L, n_modes=len(omega_classical))
    
    print("Frequency validation:")
    print(f"  Mode | Classical (rad/s) | Analytical (rad/s) | Error (%)")
    print(f"  -----|-------------------|--------------------|----------")
    total_error = 0
    for i in range(len(omega_classical)):
        error = abs(omega_classical[i] - omega_analytical[i]) / omega_analytical[i] * 100
        total_error += error
        print(f"  {i+1:4d} | {omega_classical[i]:17.6f} | {omega_analytical[i]:18.6f} | {error:8.3f}%")
    
    avg_error = total_error / len(omega_classical)
    print(f"\nAverage error: {avg_error:.3f}%")
    
    # Check if within tolerance
    if avg_error < 1.0:
        print("PASS: Average error < 1%")
    else:
        print("FAIL: Average error >= 1%")
    
    # Check matrix properties
    if checks['K_symmetric'] and checks['M_symmetric']:
        print("PASS: K and M matrices are symmetric")
    else:
        print("FAIL: K or M matrix not symmetric")
        
    if checks['K_positive_definite'] and checks['M_positive_definite']:
        print("PASS: K and M matrices are positive definite")
    else:
        print("FAIL: K or M matrix not positive definite")
        
    print("="*60)
    return avg_error < 1.0


if __name__ == "__main__":
    success = validate_truss_analysis()
    exit(0 if success else 1)