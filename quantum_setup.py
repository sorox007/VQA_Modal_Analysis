import numpy as np
import scipy.linalg as la
from qiskit.quantum_info import SparsePauliOp


def build_structural_hamiltonian(K_red, M_red):
    """
    Convert structural generalized eigenvalue problem to quantum Hamiltonian.

    Transforms: K phi = omega^2 M phi
    Into: H |psi> = lambda |psi>  where H = M^(-1/2) K M^(-1/2), lambda = omega^2

    The Hamiltonian is normalized to O(1) for VQE convergence: H_norm = H / ||H||,
    where ||H|| = max(|eigenvalue|). VQE returns eigenvalues in unitless form;
    multiply by H_scale to recover physical eigenvalues.

    Returns:
        H_norm: normalized numpy array (H / H_scale)
        hamiltonian: Qiskit SparsePauliOp (from H_norm)
        M_half_inv: M^(-1/2) for back-transformation
        H_scale: spectral norm of H (multiply VQE eigenvalues by this to get physical values)
    """
    # Compute M^(-1/2)
    M_half_inv = la.fractional_matrix_power(M_red, -0.5)

    # Form symmetric Hamiltonian
    H_np = M_half_inv @ K_red @ M_half_inv

    # Symmetrize (remove numerical noise)
    H_np = 0.5 * (H_np + H_np.T)

    # Verify Hermitian
    assert np.allclose(H_np, H_np.T, atol=1e-10), "H is not Hermitian!"

    # Compute eigenvalue spectrum for normalization
    raw_eigenvalues = np.linalg.eigvalsh(H_np)
    H_scale = np.max(np.abs(raw_eigenvalues))

    # Normalize to O(1) - VQE needs this for stable gradient steps
    H_norm = H_np / H_scale

    # Convert to Qiskit SparsePauliOp
    hamiltonian = SparsePauliOp.from_operator(H_norm)

    print(f"Matrix size: {H_np.shape}")
    print(f"Number of Pauli terms: {len(hamiltonian)}")
    print(f"Condition number of H: {np.linalg.cond(H_np):.2f}")
    print(f"H_scale (spectral norm): {H_scale:.4e}")
    print(f"Unnormalized eigenvalue range: [{raw_eigenvalues.min():.4e}, {raw_eigenvalues.max():.4e}]")
    print(f"Normalized eigenvalue range: [{(raw_eigenvalues / H_scale).min():.6f}, {(raw_eigenvalues / H_scale).max():.6f}]")

    return H_norm, hamiltonian, M_half_inv, H_scale


def inspect_pauli_decomposition(hamiltonian):
    """Print all Pauli terms and their coefficients."""
    print("\n=== PAULI DECOMPOSITION ===")
    print(f"{'Pauli String':<15} {'Coefficient':<15}")
    print("-" * 30)
    for pauli, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
        if abs(coeff) > 1e-10:
            print(f"{str(pauli):<15} {coeff.real:<15.6f}")
