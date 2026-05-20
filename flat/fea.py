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