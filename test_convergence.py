import numpy as np
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis, analytical_fixed_fixed

def test_convergence():
    E = 200e9
    A = 0.01
    rho = 7850.0
    L = 1.0
    
    print("Elements | Mode 1 FEM (rad/s) | Mode 1 Analytical (rad/s) | Error (%)")
    print("--------|---------------------|---------------------------|----------")
    
    for n_elem in [2, 4, 8, 16, 32, 64]:
        K, M = assemble_truss(n_elem, E, A, rho, L)
        K_red, M_red, _ = apply_fixed_fixed_bc(K, M)
        omega_fem, _ = classical_modal_analysis(K_red, M_red)
        omega_anal = analytical_fixed_fixed(E, A, rho, L, n_modes=1)
        
        error = abs(omega_fem[0] - omega_anal[0]) / omega_anal[0] * 100
        print(f"{n_elem:8d} | {omega_fem[0]:19.6f} | {omega_anal[0]:25.6f} | {error:9.3f}%")

if __name__ == "__main__":
    test_convergence()