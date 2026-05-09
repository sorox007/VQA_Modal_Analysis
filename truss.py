import numpy as np
import scipy.linalg as la


def truss_element_stiffness(EA, L):
    """
    2×2 stiffness matrix: (EA/L)*[[1,-1],[-1,1]]
    """
    return (EA / L) * np.array([[1, -1], [-1, 1]])


def truss_element_mass(rhoA, L, lumped=False):
    """
    2×2 mass matrix: consistent=(ρAL/6)*[[2,1],[1,2]], lumped=(ρAL/2)*I
    """
    if lumped:
        return (rhoA * L / 2) * np.eye(2)
    else:
        return (rhoA * L / 6) * np.array([[2, 1], [1, 2]])


def assemble_truss(num_elements, E, A, rho, L_total):
    """
    Assemble global K, M (size: n+1 × n+1, n=num_elements)
    """
    ndof = num_elements + 1
    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))
    
    L_e = L_total / num_elements
    
    for elem in range(num_elements):
        # Element stiffness and mass matrices
        k_e = truss_element_stiffness(E * A, L_e)
        m_e = truss_element_mass(rho * A, L_e, lumped=False)
        
        # Assembly
        dofs = [elem, elem + 1]
        for i_local, i_global in enumerate(dofs):
            for j_local, j_global in enumerate(dofs):
                K_global[i_global, j_global] += k_e[i_local, j_local]
                M_global[i_global, j_global] += m_e[i_local, j_local]
    
    return K_global, M_global


def apply_fixed_fixed_bc(K, M):
    """
    Remove DOF at both ends (indices 0 and n)
    Returns K_red, M_red, free_dofs
    """
    n = K.shape[0] - 1
    free_dofs = list(range(1, n))  # Remove indices 0 and n
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs


def apply_fixed_free_bc(K, M):
    """
    Remove DOF at fixed end (index 0)
    Returns K_red, M_red, free_dofs
    """
    free_dofs = list(range(1, K.shape[0]))  # Remove index 0
    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]
    return K_red, M_red, free_dofs


def classical_modal_analysis(K_red, M_red):
    """
    scipy.linalg.eigh — identical to beam
    """
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    # Return eigenvalues in ascending order (smallest first)
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    # Natural frequencies: omega = sqrt(eigenvalues)
    omega = np.sqrt(eigenvalues)
    return omega, eigenvectors


def analytical_fixed_fixed(E, A, rho, L, n_modes=4):
    """
    ωₙ = (nπ/L)*√(E/ρ)
    """
    n_vals = np.arange(1, n_modes + 1)
    omega = (n_vals * np.pi / L) * np.sqrt(E / rho)
    return omega


def analytical_fixed_free(E, A, rho, L, n_modes=4):
    """
    ωₙ = (2n-1)π/(2L)*√(E/ρ)
    """
    n_vals = np.arange(1, n_modes + 1)
    omega = ((2 * n_vals - 1) * np.pi / (2 * L)) * np.sqrt(E / rho)
    return omega


def validate_truss_matrices(K, M):
    """
    Validate truss matrices
    """
    checks = {}
    
    # Symmetry
    checks['K_symmetric'] = np.allclose(K, K.T, atol=1e-10)
    checks['M_symmetric'] = np.allclose(M, M.T, atol=1e-10)
    
    # Positive definiteness
    try:
        K_eigvals = la.eigvalsh(K)
        M_eigvals = la.eigvalsh(M)
        checks['K_positive_definite'] = np.all(K_eigvals > 0)
        checks['M_positive_definite'] = np.all(M_eigvals > 0)
        checks['K_min_eigenvalue'] = np.min(K_eigvals)
        checks['M_min_eigenvalue'] = np.min(M_eigvals)
    except la.LinAlgError:
        checks['K_positive_definite'] = False
        checks['M_positive_definite'] = False
    
    # Condition number
    checks['K_condition_number'] = np.linalg.cond(K)
    checks['M_condition_number'] = np.linalg.cond(M)
    
    return checks


def print_truss_info(num_elements, E, A, rho, L_total):
    """
    Print truss geometry and material info
    """
    print("="*50)
    print("TRUSS GEOMETRY & MATERIAL")
    print("="*50)
    print(f"Number of elements: {num_elements}")
    print(f"Element length: {L_total/num_elements:.4f} m")
    print(f"Total length: {L_total:.4f} m")
    print(f"Young's modulus: {E:.2e} Pa")
    print(f"Density: {rho:.1f} kg/m³")
    print(f"Cross-sectional area: {A:.6f} m²")
    print(f"Axial stiffness EA: {E*A:.2e} N")
    print(f"Axial mass rho*A: {rho*A:.4f} kg/m")
    print("="*50)


# ============================================================
# 2D WARREN TRUSS FUNCTIONS
# ============================================================

def generate_warren_truss_mesh(n_chords=5, L=1.0, h=0.3):
    """
    Generate 2D Warren truss mesh with vertical end posts.

    Warren truss pattern: bottom chord nodes (B0-Bn), top chord nodes (T0-Tn)
    where n = n_chords - 1

    Parameters
    ----------
    n_chords : int
        Number of bottom chord nodes (elements in bottom/top chords)
    L : float
        Total horizontal span (m)
    h : float
        Truss height (m)

    Returns
    -------
    nodes : ndarray (n_nodes, 2)
        Node coordinates [x, y]
    members : list of tuple
        Each tuple: (i, j, E, A, rho) for member connecting nodes i and j
    node_ids : dict
        Mapping of node labels ('B0', 'T0', etc.) to node indices
    """
    n_top_nodes = n_chords - 1  # Top chord has one fewer node than bottom
    n_nodes = 2 * n_chords - 1  # Total nodes

    x_spacing = L / (n_chords - 1)

    # Create node coordinates
    nodes = np.zeros((n_nodes, 2))
    node_ids = {}

    # Bottom chord nodes: B0, B1, ..., B(n_chords-1)
    for i in range(n_chords):
        nodes[i, 0] = i * x_spacing
        nodes[i, 1] = 0.0
        node_ids[f'B{i}'] = i

    # Top chord nodes: T0, T1, ..., T(n_top_nodes-1)
    for i in range(n_top_nodes):
        nodes[n_chords + i, 0] = (i + 0.5) * x_spacing
        nodes[n_chords + i, 1] = h
        node_ids[f'T{i}'] = n_chords + i

    # Build members list: (node_i, node_j, E placeholder, A placeholder, rho placeholder)
    members = []

    # Vertical end posts
    members.append((0, n_chords, None, None, None))  # B0 to T0 (left post)
    members.append((n_chords - 1, 2 * n_chords - 2, None, None, None))  # B(n-1) to T(n_top-1) (right post)

    # Bottom chord
    for i in range(n_chords - 1):
        members.append((i, i + 1, None, None, None))

    # Top chord
    for i in range(n_top_nodes - 1):
        members.append((n_chords + i, n_chords + i + 1, None, None, None))

    # Diagonal web members (Warren pattern: alternates direction)
    for i in range(n_top_nodes):
        # Left diagonal: B(i+1) to T(i)
        if i < n_chords - 1:
            members.append((i + 1, n_chords + i, None, None, None))
        # Right diagonal: T(i) to B(i+1) (skip first to avoid duplicate)
        if i < n_top_nodes - 1 and i + 1 < n_chords - 1:
            members.append((n_chords + i, i + 2, None, None, None))

    return nodes, members, node_ids


def truss2d_element_stiffness(E, A, nodes, i, j):
    """
    Compute 2D truss element stiffness matrix.

    Parameters
    ----------
    E : float
        Young's modulus
    A : float
        Cross-sectional area
    nodes : ndarray
        Node coordinates
    i, j : int
        End node indices

    Returns
    -------
    k_e : ndarray (4, 4)
        Element stiffness matrix
    """
    xi, yi = nodes[i]
    xj, yj = nodes[j]

    dx = xj - xi
    dy = yj - yi
    L = np.sqrt(dx**2 + dy**2)

    # Direction cosines
    c = dx / L
    s = dy / L

    # 2D truss element stiffness (axial only)
    k_e = (E * A / L) * np.array([
        [c**2, c*s, -c**2, -c*s],
        [c*s, s**2, -c*s, -s**2],
        [-c**2, -c*s, c**2, c*s],
        [-c*s, -s**2, c*s, s**2]
    ])

    return k_e


def truss2d_element_mass(rho, A, nodes, i, j, lumped=False):
    """
    Compute 2D truss element mass matrix.

    Parameters
    ----------
    rho : float
        Density
    A : float
        Cross-section area
    nodes : ndarray
        Node coordinates
    i, j : int
        End node indices
    lumped : bool
        Use lumped mass matrix

    Returns
    -------
    m_e : ndarray (4, 4)
        Element mass matrix
    """
    xi, yi = nodes[i]
    xj, yj = nodes[j]

    dx = xj - xi
    dy = yj - yi
    L = np.sqrt(dx**2 + dy**2)

    if lumped:
        m_e = (rho * A * L / 2) * np.eye(4)
    else:
        m_e = (rho * A * L / 6) * np.array([
            [2, 0, 1, 0],
            [0, 2, 0, 1],
            [1, 0, 2, 0],
            [0, 1, 0, 2]
        ])

    return m_e


def assemble_truss2d(nodes, members, E, A, rho):
    """
    Assemble global K, M for 2D truss.

    Parameters
    ----------
    nodes : ndarray (n_nodes, 2)
        Node coordinates
    members : list of tuple
        (i, j, E, A, rho) for each member (E, A, rho can be None if using defaults)
    E : float
        Young's modulus (used if member E is None)
    A : float
        Cross-sectional area
    rho : float
        Density

    Returns
    -------
    K_global : ndarray
        Global stiffness matrix
    M_global : ndarray
        Global mass matrix
    """
    n_nodes = nodes.shape[0]
    ndof = 2 * n_nodes
    K_global = np.zeros((ndof, ndof))
    M_global = np.zeros((ndof, ndof))

    for member in members:
        i, j, E_m, A_m, rho_m = member
        E_use = E if E_m is None else E_m
        A_use = A if A_m is None else A_m
        rho_use = rho if rho_m is None else rho_m

        k_e = truss2d_element_stiffness(E_use, A_use, nodes, i, j)
        m_e = truss2d_element_mass(rho_use, A_use, nodes, i, j)

        # DOF mapping: node i -> [2*i, 2*i+1], node j -> [2*j, 2*j+1]
        dofs = [2*i, 2*i+1, 2*j, 2*j+1]

        for ii, di in enumerate(dofs):
            for jj, dj in enumerate(dofs):
                K_global[di, dj] += k_e[ii, jj]
                M_global[di, dj] += m_e[ii, jj]

    return K_global, M_global


def apply_pinned_roller_bc(K, M, nodes):
    """
    Apply pinned-roller boundary conditions.

    Pinned support at B0 (both x and y restrained)
    Roller support at B(n-1) (y restrained only)

    Parameters
    ----------
    K : ndarray
        Global stiffness matrix
    M : ndarray
        Global mass matrix
    nodes : ndarray
        Node coordinates (to determine n_chords)

    Returns
    -------
    K_red : ndarray
        Reduced stiffness matrix
    M_red : ndarray
        Reduced mass matrix
    free_dofs : list
        Indices of free DOFs
    fixed_dofs : list
        Indices of fixed DOFs
    """
    n_nodes = nodes.shape[0]
    ndof = 2 * n_nodes

    # Determine number of bottom chord nodes
    n_chords = (n_nodes + 1) // 2

    # Fixed DOFs: B0 = node 0 (both x and y), B(n-1) = node n_chords-1 (y only)
    fixed_dofs = [0, 1]  # B0: both x and y

    # Add roller support constraint: B(n_chords-1) y-DOF
    roller_node = n_chords - 1
    fixed_dofs.append(2 * roller_node + 1)  # y-DOF only

    free_dofs = [i for i in range(ndof) if i not in fixed_dofs]
    free_dofs = list(sorted(free_dofs))

    K_red = K[np.ix_(free_dofs, free_dofs)]
    M_red = M[np.ix_(free_dofs, free_dofs)]

    return K_red, M_red, free_dofs, fixed_dofs


def classical_modal_analysis_2d(K_red, M_red, n_modes=None):
    """
    Classical modal analysis for 2D truss (wrapper for existing function).

    Parameters
    ----------
    K_red : ndarray
        Reduced stiffness matrix
    M_red : ndarray
        Reduced mass matrix
    n_modes : int, optional
        Number of modes to return

    Returns
    -------
    omega : ndarray
        Natural frequencies (rad/s)
    modes : ndarray
        Mode shapes (reduced DOF space)
    eigenvalues : ndarray
        Eigenvalues
    """
    from scipy import linalg as la
    eigenvalues, eigenvectors = la.eigh(K_red, M_red)
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    if n_modes is not None:
        eigenvalues = eigenvalues[:n_modes]
        eigenvectors = eigenvectors[:, :n_modes]

    omega = np.sqrt(eigenvalues)
    return omega, eigenvectors, eigenvalues


if __name__ == "__main__":
    # Simple test
    E, A, rho, L = 200e9, 0.01, 7850, 1.0
    n_elem = 4
    
    print_truss_info(n_elem, E, A, rho, L)
    
    K, M = assemble_truss(n_elem, E, A, rho, L)
    print(f"Global K shape: {K.shape}, M shape: {M.shape}")
    
    K_red, M_red, free_dofs = apply_fixed_fixed_bc(K, M)
    print(f"After fixed-fixed BCs:")
    print(f"  Free DOFs: {free_dofs}")
    print(f"  K_red shape: {K_red.shape}")
    print(f"  K_red condition: {np.linalg.cond(K_red):.2f}")
    
    omega, modes = classical_modal_analysis(K_red, M_red)
    print(f"\nNatural frequencies (rad/s): {omega}")
    print(f"Natural frequencies (Hz): {omega/(2*np.pi)}")
    
    # Validation
    checks = validate_truss_matrices(K, M)
    print(f"\nValidation checks:")
    for key, val in checks.items():
        print(f"  {key}: {val}")