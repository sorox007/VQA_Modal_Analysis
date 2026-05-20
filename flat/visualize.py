import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — prevents Tkinter main-loop errors
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch

# --- Color Scheme ---
NAVY    = "#1A2151"
BLUE    = "#0D6EFD"
CYAN    = "#00B4D8"
GREEN   = "#0A7C59"
RED     = "#C0392B"
ORANGE  = "#E67E22"
GREY    = "#566573"
LIGHT   = "#EBF5FB"

# ============================================================
# BEAM GEOMETRY
# ============================================================

def plot_beam_geometry(n_elem, L_total, taper_ratios=None):
    """2D side-view of the beam with supports and optional taper."""
    fig, ax = plt.subplots(figsize=(10, 2.5))
    L_e = L_total / n_elem
    h0_vis = 0.12
    x_nodes = [i * L_e for i in range(n_elem + 1)]

    if taper_ratios is not None:
        xs = np.linspace(0, L_total, 200)
        heights = []
        for x in xs:
            elem_idx = min(int(x / L_e), n_elem - 1)
            heights.append(h0_vis * taper_ratios[elem_idx])
        heights = np.array(heights)
        ax.fill_between(xs, -heights / 2, heights / 2,
                        color=GREY, alpha=0.5, edgecolor=NAVY, linewidth=2,
                        label="Tapered beam")
        for x in x_nodes[1:-1]:
            ax.axvline(x, color=GREY, linewidth=0.5, alpha=0.4)
    else:
        rect = plt.Rectangle((0, -h0_vis / 2), L_total, h0_vis,
                             facecolor=GREY, alpha=0.5, edgecolor=NAVY, linewidth=2)
        ax.add_patch(rect)
        for x in x_nodes[1:-1]:
            ax.axvline(x, color=GREY, linewidth=0.5, alpha=0.4)

    # Pinned support triangles
    for x_s in [0, L_total]:
        tri = plt.Polygon(
            [(x_s, -h0_vis / 2 - 0.005), (x_s - 0.02, -h0_vis / 2 - 0.035),
             (x_s + 0.02, -h0_vis / 2 - 0.035)],
            facecolor=NAVY, edgecolor='black'
        )
        ax.add_patch(tri)

    ax.set_xlim(-0.05, L_total + 0.05)
    ax.set_ylim(-0.08, 0.08)
    ax.set_aspect('equal')
    ax.set_xlabel("Length (m)", fontsize=12)
    ax.set_ylabel("Cross-section", fontsize=12)
    ax.set_title(f"Beam Geometry ({n_elem} elements, L={L_total}m)",
                 fontsize=13, fontweight='bold', color=NAVY)
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/beam_geometry.png', dpi=150, bbox_inches='tight')
    plt.show()


# ============================================================
# MODE SHAPE VISUALIZATION (Continuous interpolation)
# ============================================================

def _map_vqe_to_transverse(vqe_state, free_dofs, n_full_dof, n_elem, L_total):
    """
    Map VQE state vector (in reduced DOF space) back to transverse displacements.

    For a beam, DOFs are interleaved: [v0, θ0, v1, θ1, ...].
    Transverse displacements are at even indices (0, 2, 4, ...).
    The VQE state vector has one component per free DOF, in the order of free_dofs.
    """
    # Map to full DOF space
    u_full = np.zeros(n_full_dof)
    n_use = min(len(vqe_state), len(free_dofs))
    for i in range(n_use):
        u_full[free_dofs[i]] = vqe_state[i]

    # Extract transverse DOFs only (even indices: 0, 2, 4, ...)
    node_positions = np.array([i * L_total / n_elem for i in range(n_elem + 1)])
    transverse_vals = np.array([u_full[2*j] for j in range(n_elem + 1)])

    return node_positions, transverse_vals


def plot_mode_shapes_continuous(n_elem, L_total, mode_shapes_classical,
                                 free_dofs, mode_shapes_vqe=None,
                                 analytical_params=None, n_modes=3):
    """
    Plot mode shapes as continuous curves with markers at nodes.
    Handles both classical FEA and VQE results.

    Parameters
    ----------
    n_elem : int
        Number of beam elements
    L_total : float
        Total beam length
    mode_shapes_classical : ndarray (n_free, n_modes)
        Classical mode shapes in reduced DOF space
    free_dofs : list
        Indices of free DOFs after BCs
    mode_shapes_vqe : list of ndarray, optional
        VQE mode shapes (each is a state vector in reduced space)
    analytical_params : dict, optional
        Parameters for analytical solution (e.g., {'L': L})
    n_modes : int
        Number of modes to plot
    """
    fig, axes = plt.subplots(min(n_modes, 3), 1, figsize=(10, 3 * min(n_modes, 3)))
    if n_modes == 1:
        axes = [axes]

    # Node positions for plotting (one point per element end)
    x_nodes = np.array([i * L_total / n_elem for i in range(n_elem + 1)])

    for mode_idx in range(min(n_modes, len(axes))):
        ax = axes[mode_idx]

        # --- Classical mode shape ---
        # Map from reduced DOF space to full DOF space
        n_full_dof = 2 * (n_elem + 1)
        u_full_classical = np.zeros(n_full_dof)
        for i, dof in enumerate(free_dofs):
            if i < mode_shapes_classical.shape[0]:
                u_full_classical[dof] = mode_shapes_classical[i, mode_idx]

        # Extract transverse displacements (even DOF indices: 0, 2, 4, ...)
        u_classical_transverse = np.array([u_full_classical[2*j] for j in range(n_elem + 1)])

        # Normalize for plotting
        u_classical_plot = u_classical_transverse.copy()
        max_abs = np.max(np.abs(u_classical_plot))
        if max_abs > 1e-12:
            u_classical_plot /= max_abs

        ax.plot(x_nodes, u_classical_plot, 'o-', color=RED,
                linewidth=2, markersize=8, label='Classical FEA')

        # --- VQE mode shape ---
        if mode_shapes_vqe and mode_idx < len(mode_shapes_vqe):
            u_vqe = mode_shapes_vqe[mode_idx]
            x_vqe, u_vqe_transverse = _map_vqe_to_transverse(
                u_vqe, free_dofs, n_full_dof, n_elem, L_total
            )
            # Normalize
            max_abs_vqe = np.max(np.abs(u_vqe_transverse))
            if max_abs_vqe > 1e-12:
                u_vqe_transverse = u_vqe_transverse / max_abs_vqe

            ax.plot(x_vqe, u_vqe_transverse, 's--', color=BLUE,
                    linewidth=2, markersize=8, label='VQE')

        # --- Analytical mode shape ---
        if analytical_params is not None:
            L_ana = analytical_params.get('L', L_total)
            x_ana = np.linspace(0, L_ana, 200)
            # Simply supported beam mode shape: sin(n*pi*x/L)
            n_mode = mode_idx + 1
            u_ana = np.sin(n_mode * np.pi * x_ana / L_ana)
            ax.plot(x_ana, u_ana, '--', color=GREEN, linewidth=2,
                   alpha=0.7, label='Analytical')

        ax.set_xlim(-0.02 * L_total, 1.02 * L_total)
        ax.set_ylim(-1.3, 1.3)
        ax.set_ylabel(f"Mode {mode_idx+1}\nAmplitude", fontsize=11)
        ax.set_title(f"Mode {mode_idx+1} Shape", fontsize=12, fontweight='bold')
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color='black', linewidth=0.5)

    axes[-1].set_xlabel("Length (m)", fontsize=12)
    plt.suptitle("Mode Shapes - Classical vs VQE vs Analytical",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/mode_shapes_continuous.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_dual_convergence(cobyla_costs, lbfgs_costs, omega_ref, H_scale=1.0):
    """Side-by-side convergence comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # COBYLA
    ax1.semilogy(cobyla_costs, color=BLUE, linewidth=2, label='COBYLA')
    ax1.axhline(omega_ref**2 / H_scale, color=RED, linestyle='--',
                linewidth=2, label='Classical Reference')
    ax1.set_xlabel("Iteration", fontsize=12)
    ax1.set_ylabel("Cost Function (VQE Energy)", fontsize=12)
    ax1.set_title("COBYLA Convergence", fontweight='bold', color=BLUE)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.4)

    # L-BFGS-B
    ax2.semilogy(lbfgs_costs, color=ORANGE, linewidth=2, label='L-BFGS-B')
    ax2.axhline(omega_ref**2 / H_scale, color=RED, linestyle='--',
                linewidth=2, label='Classical Reference')
    ax2.set_xlabel("Iteration", fontsize=12)
    ax2.set_ylabel("Cost Function (VQE Energy)", fontsize=12)
    ax2.set_title("L-BFGS-B Convergence", fontweight='bold', color=ORANGE)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.4)

    plt.suptitle("Optimizer Comparison: Convergence Behavior",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/optimizer_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_optimizer_comparison(cobyla_results, lbfgs_results, classical_ref,
                               labels=None):
    """Bar chart comparing final VQE results to classical."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    x = np.arange(len(classical_ref))
    width = 0.35

    # Plot 1: Frequencies
    if labels is None:
        labels = ['VQE']

    for i, (vqe_freqs, label) in enumerate(zip(cobyla_results, labels)):
        offset = width * i
        ax1.bar(x + offset, vqe_freqs, width, label=f'{label} (VQE)',
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax1.bar(x + width * len(cobyla_results), classical_ref, width,
           label='Classical (FEA/scipy)', color=RED, alpha=0.8)
    ax1.set_ylabel('Frequency (rad/s)', fontsize=12)
    ax1.set_title('Natural Frequencies: VQE vs Classical',
                  fontweight='bold', color=NAVY)
    ax1.set_xticks(x + width * (len(cobyla_results) + 1) / 2)
    ax1.set_xticklabels([f'Mode {i+1}' for i in range(len(classical_ref))])
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Relative error
    for i, (vqe_freqs, label) in enumerate(zip(cobyla_results, labels)):
        offset = width * i
        errors = np.abs(np.array(vqe_freqs) - np.array(classical_ref)) / np.array(classical_ref) * 100
        ax2.bar(x + offset, errors, width, label=f'{label} (VQE)',
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax2.set_ylabel('Absolute Error (%)', fontsize=12)
    ax2.set_title('VQE Accuracy vs Classical Reference',
                  fontweight='bold', color=NAVY)
    ax2.set_xticks(x + width * (len(cobyla_results) + 1) / 2)
    ax2.set_xticklabels([f'Mode {i+1}' for i in range(len(classical_ref))])
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(2, color='red', linestyle='--', linewidth=1, alpha=0.5,
               label='Target: <2%')

    plt.suptitle("Frequency Comparison Across Modes",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_convergence(cost_history, omega_vqe, omega_ref, H_scale=1.0, title="VQE Convergence", filename='convergence.png'):
    """Plot VQE cost function convergence and final frequency error."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Convergence curve
    ax1.semilogy(cost_history, color=BLUE, linewidth=2)
    ax1.axhline(omega_ref**2 / H_scale, color=RED, linestyle='--',
                linewidth=2, label='Classical eigenvalue')
    ax1.set_xlabel("Iteration", fontsize=12)
    ax1.set_ylabel("VQE Energy (E/||H||)", fontsize=12)
    ax1.set_title("VQE Cost Function Convergence", fontweight='bold', color=NAVY)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.4)

    # Frequency comparison
    freq_error = abs(omega_vqe - omega_ref) / omega_ref * 100
    bars = ax2.bar(['Classical (FEA/scipy)', 'VQE (Quantum)'],
                    [omega_ref, omega_vqe],
                    color=[RED, BLUE], alpha=0.8, width=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, [omega_ref, omega_vqe]):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}', ha='center', va='bottom', fontsize=11)

    ax2.set_ylabel('Frequency (rad/s)', fontsize=12)
    ax2.set_title(f'Fundamental Frequency\n(Error: {freq_error:.3f}%)',
                  fontweight='bold', color=NAVY)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.suptitle(title, fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig(f'results/{filename}', dpi=150, bbox_inches='tight')
    plt.show()


def plot_mode_shapes(mode_shapes_vqe, mode_shapes_classical, n_modes=3):
    """Simple bar/stem plot comparing mode shapes."""
    fig, axes = plt.subplots(min(n_modes, 3), 1, figsize=(10, 3*min(n_modes, 3)))
    if n_modes == 1:
        axes = [axes]

    for mode_idx in range(min(n_modes, len(axes))):
        ax = axes[mode_idx]
        n = len(mode_shapes_classical[mode_idx])
        x = np.arange(n)

        ax.stem(x, mode_shapes_classical[mode_idx],
                linefmt=RED, markerfmt='ro', basefmt=' ',
                label='Classical', use_line_collection=True)
        if mode_idx < len(mode_shapes_vqe):
            # Normalize VQE mode shape for comparison
            vqe_mode = mode_shapes_vqe[mode_idx][:n]
            if np.max(np.abs(vqe_mode)) > 0:
                vqe_mode = vqe_mode / np.max(np.abs(vqe_mode))
            ax.stem(x, vqe_mode,
                    linefmt=BLUE, markerfmt='bs', basefmt=' ',
                    label='VQE', use_line_collection=True)

        ax.set_ylabel(f"Mode {mode_idx+1}", fontsize=11)
        ax.set_title(f"Mode Shape - Mode {mode_idx+1}",
                     fontweight='bold', color=NAVY)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

    axes[-1].set_xlabel("Node index", fontsize=12)
    plt.suptitle("Mode Shapes: Classical vs VQE",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/mode_shapes.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_frequency_comparison(omega_vqe_list, omega_classical, labels=None):
    """Compare frequencies across different VQE runs."""
    if labels is None:
        labels = [f'Run {i+1}' for i in range(len(omega_vqe_list))]

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(omega_classical))
    width = 0.35

    for i, (vqe_freqs, label) in enumerate(zip(omega_vqe_list, labels)):
        offset = width * i
        ax.bar(x + offset, vqe_freqs, width, label=label,
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax.bar(x + width * len(omega_vqe_list), omega_classical, width,
           label='Classical', color=RED, alpha=0.8)

    ax.set_ylabel('Frequency (rad/s)', fontsize=12)
    ax.set_title('Natural Frequencies Comparison',
                 fontweight='bold', color=NAVY)
    ax.set_xticks(x + width * (len(omega_vqe_list) + 1) / 2)
    ax.set_xticklabels([f'Mode {i+1}' for i in range(len(omega_classical))])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_ill_conditioning_study(df):
    """Plot condition number vs VQE performance for beam and truss."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))

    # Determine if this is beam or truss data
    is_beam = 'taper_ratio' in df.columns and len(df) > 0

    # Subplot 1: Condition number vs taper
    ax1.plot(df['taper_ratio'], df['condition_number'],
             'o-', color=BLUE, linewidth=2, markersize=8)
    ax1.set_xlabel('Taper Ratio (h_min/h_max)', fontsize=12)
    ax1.set_ylabel('Condition Number of H', fontsize=12)
    ax1.set_title('Condition Number vs Geometric Non-uniformity',
                  fontweight='bold', color=NAVY)
    ax1.grid(True, alpha=0.4)

    # Subplot 2: Iterations vs condition number
    ax2.loglog(df['condition_number'], df['cobyla_iterations'],
               's-', color=ORANGE, linewidth=2, markersize=8, label='COBYLA')
    ax2.loglog(df['condition_number'], df['lbfgs_iterations'],
               'o-', color=CYAN, linewidth=2, markersize=8, label='L-BFGS-B')
    ax2.set_xlabel('Condition Number of H', fontsize=12)
    ax2.set_ylabel('VQE Iterations to Convergence', fontsize=12)
    ax2.set_title('Iteration Count vs Conditioning',
                  fontweight='bold', color=NAVY)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.4, which='both')

    # Subplot 3: Error vs condition number
    ax3.semilogx(df['condition_number'], df['cobyla_error_pct'],
                 's-', color=ORANGE, linewidth=2, markersize=8, label='COBYLA')
    ax3.semilogx(df['condition_number'], df['lbfgs_error_pct'],
                 'o-', color=CYAN, linewidth=2, markersize=8, label='L-BFGS-B')
    ax3.set_xlabel('Condition Number of H', fontsize=12)
    ax3.set_ylabel('Frequency Error (%)', fontsize=12)
    ax3.set_title('Solution Accuracy vs Conditioning',
                  fontweight='bold', color=NAVY)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.4, which='both')

    system_type = "Beam" if is_beam else ("Truss" if 'taper_ratio' in df.columns else "System")
    plt.suptitle(f"Ill-Conditioning Study: {system_type} (VQE Performance)",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/ill_conditioning_study.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_damage_detection(df):
    """Frequency shift vs damage severity (beam and truss)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Quantum Structural Health Monitoring via Frequency Shift",
                 fontsize=14, fontweight='bold', color=NAVY)

    ax1.plot(df['damage_pct'], df['omega_ref'],
              's--', color=RED, linewidth=2, markersize=8, label='Classical')
    ax1.plot(df['damage_pct'], df['omega_vqe'],
              'o-', color=BLUE, linewidth=2, markersize=8, label='VQE')
    ax1.set_xlabel("Stiffness Reduction (% damage)", fontsize=12)
    ax1.set_ylabel("Fundamental Frequency (rad/s)", fontsize=12)
    ax1.set_title("Natural Frequency Drops with Damage", fontweight='bold')
    ax1.legend()
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.4)

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


# ============================================================
# TRUSS-SPECIFIC VISUALIZATIONS
# ============================================================

def plot_truss_geometry(n_elem, L_total):
    """
    1D horizontal bar representation of truss with node labels.

    Parameters
    ----------
    n_elem : int
        Number of truss elements
    L_total : float
        Total truss length (m)
    """
    fig, ax = plt.subplots(figsize=(10, 3))

    L_e = L_total / n_elem
    x_nodes = np.linspace(0, L_total, n_elem + 1)

    # Draw truss as thick horizontal line
    ax.plot([0, L_total], [0, 0], color=GREY, linewidth=10,
            solid_capstyle='round', alpha=0.6, label='Truss member')

    # Draw nodes as circles
    ax.scatter(x_nodes, np.zeros_like(x_nodes), s=200, c=BLUE,
              zorder=5, edgecolors=NAVY, linewidths=2, label='Nodes')

    # Node labels and DOF indicators
    for i, x in enumerate(x_nodes):
        ax.text(x, 0.08, f'N{i}\n(u{i})', ha='center', va='bottom',
               fontsize=10, fontweight='bold', color=NAVY)

    # Fixed ends (first and last nodes)
    ax.plot([0, 0], [-0.1, 0.1], color=RED, linewidth=4, marker='^',
           markersize=12, markeredgecolor='black', label='Fixed support')
    ax.plot([L_total, L_total], [-0.1, 0.1], color=RED, linewidth=4,
           marker='^', markersize=12, markeredgecolor='black')

    # Element labels
    for i in range(n_elem):
        x_mid = (x_nodes[i] + x_nodes[i+1]) / 2
        ax.text(x_mid, -0.08, f'Elem {i+1}', ha='center', va='top',
               fontsize=9, style='italic', color=GREY)

    ax.set_xlim(-0.05 * L_total, 1.05 * L_total)
    ax.set_ylim(-0.15, 0.15)
    ax.set_aspect('equal')
    ax.set_xlabel("Length (m)", fontsize=12)
    ax.set_yticks([])
    ax.set_title(f"Truss Geometry ({n_elem} elements, L={L_total}m)",
                fontsize=13, fontweight='bold', color=NAVY)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/truss_geometry.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_truss_mode_shapes(n_elem, L_total, modes, labels=None,
                            analytical_omega=None, show_displacements=True):
    """
    Plot truss mode shapes (axial displacement profiles).

    Parameters
    ----------
    n_elem : int
        Number of elements
    L_total : float
        Total length
    modes : list of ndarray
        List of mode shape arrays (one per mode)
    labels : list of str, optional
        Label for each mode set (e.g., ['Classical', 'VQE'])
    analytical_omega : ndarray, optional
        Analytical natural frequencies for comparison
    show_displacements : bool
        If True, show deformed shape with exaggerated displacement
    """
    if labels is None:
        labels = [f'Mode Set {i+1}' for i in range(len(modes))]

    n_modes = min(len(modes), 3)
    fig, axes = plt.subplots(n_modes, 1, figsize=(10, 3.5 * n_modes))
    if n_modes == 1:
        axes = [axes]

    x_nodes = np.linspace(0, L_total, n_elem + 1)

    for mode_idx in range(n_modes):
        ax = axes[mode_idx]
        mode = modes[mode_idx]

        # Truss undeformed position (horizontal line)
        ax.plot([0, L_total], [0, 0], 'k--', linewidth=1, alpha=0.5,
               label='Undeformed')

        if show_displacements and mode is not None:
            # Use mode shape as displacement (scale for visibility)
            u = mode[:len(x_nodes)] if len(mode) >= len(x_nodes) else mode
            if len(u) < len(x_nodes):
                # Pad if needed
                u_padded = np.zeros(len(x_nodes))
                u_padded[:len(u)] = u
                u = u_padded

            # Normalize for plotting
            if np.max(np.abs(u)) > 1e-10:
                u_plot = u / np.max(np.abs(u)) * 0.1  # 10% max displacement
            else:
                u_plot = u

            # Plot deformed shape
            ax.plot(x_nodes, u_plot, 'o-', linewidth=2.5,
                   markersize=8, label=f'{labels[0]} mode shape')

            # Draw arrows for displacement direction
            for i, x in enumerate(x_nodes):
                if abs(u_plot[i]) > 1e-6:
                    color = GREEN if u_plot[i] > 0 else RED
                    ax.annotate('', xy=(x, u_plot[i]), xytext=(x, 0),
                               arrowprops=dict(arrowstyle='->', lw=1.5,
                                             color=color, alpha=0.7))

            # Node markers
            ax.scatter(x_nodes, u_plot, s=100, c=BLUE, zorder=5,
                      edgecolors=NAVY, linewidths=1.5)

        # Analytical frequency if provided
        freq_str = ""
        if analytical_omega is not None and mode_idx < len(analytical_omega):
            freq_str = f" (ω={analytical_omega[mode_idx]:.1f} rad/s)"

        ax.set_xlim(-0.05 * L_total, 1.05 * L_total)
        max_disp = max(0.15, np.max(np.abs(ax.get_ylim())) * 1.1)
        ax.set_ylim(-max_disp, max_disp)
        ax.set_ylabel(f"Axial Disp.", fontsize=11)
        ax.set_title(f"Mode {mode_idx+1}{freq_str}",
                    fontweight='bold', color=NAVY)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3, axis='both')
        ax.axhline(0, color='black', linewidth=0.5)

        # Draw supports
        ax.plot([0, 0], [-max_disp*0.9, max_disp*0.9], 'r-', linewidth=3,
               alpha=0.7, label='Fixed' if mode_idx == 0 else '')
        ax.plot([L_total, L_total], [-max_disp*0.9, max_disp*0.9], 'r-',
               linewidth=3, alpha=0.7)

    axes[-1].set_xlabel("Length (m)", fontsize=12)
    plt.suptitle("Truss Mode Shapes - Axial Displacement",
                fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/truss_mode_shapes.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_truss_frequency_comparison(vqe_freqs, classical_freqs, labels=None):
    """
    Compare truss natural frequencies from VQE and classical analysis.

    Parameters
    ----------
    vqe_freqs : list of list
        VQE frequencies for each run/config
    classical_freqs : ndarray
        Classical frequencies
    labels : list of str, optional
        Labels for VQE runs
    """
    if labels is None:
        labels = ['VQE']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    n_modes = len(classical_freqs)
    x = np.arange(n_modes)
    width = 0.35

    # Frequencies
    for i, (vqe_f, label) in enumerate(zip(vqe_freqs, labels)):
        offset = width * i
        ax1.bar(x + offset, vqe_f[:n_modes], width, label=label,
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax1.bar(x + width * len(vqe_freqs), classical_freqs, width,
           label='Classical (Analytical)', color=RED, alpha=0.8)

    ax1.set_ylabel('Natural Frequency (rad/s)', fontsize=12)
    ax1.set_title('Truss Natural Frequencies: VQE vs Classical',
                  fontweight='bold', color=NAVY)
    ax1.set_xticks(x + width * (len(vqe_freqs) + 1) / 2)
    ax1.set_xticklabels([f'Mode {i+1}' for i in range(n_modes)])
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # Relative errors
    for i, (vqe_f, label) in enumerate(zip(vqe_freqs, labels)):
        offset = width * i
        errors = np.abs(np.array(vqe_f[:n_modes]) - classical_freqs) / classical_freqs * 100
        ax2.bar(x + offset, errors, width, label=label,
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax2.set_ylabel('Absolute Error (%)', fontsize=12)
    ax2.set_title('VQE Accuracy for Truss Modes',
                  fontweight='bold', color=NAVY)
    ax2.set_xticks(x + width * (len(vqe_freqs) + 1) / 2)
    ax2.set_xticklabels([f'Mode {i+1}' for i in range(n_modes)])
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(2, color='red', linestyle='--', linewidth=1, alpha=0.5,
               label='Target: <2%')

    plt.suptitle("Truss Frequency Comparison Across Modes",
                fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/truss_frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
