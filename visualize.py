import numpy as np
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
            color=RED, edgecolor='black', linewidth=0.8
        )
        ax.add_patch(tri)

    ax.annotate('', xy=(0, -h0_vis / 2 - 0.06), xytext=(L_total, -h0_vis / 2 - 0.06),
                arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.2))
    ax.text(L_total / 2, -h0_vis / 2 - 0.09, f'L = {L_total} m',
            ha='center', va='top', fontsize=10, color=NAVY)

    for i, x in enumerate(x_nodes):
        ax.plot(x, 0, 'o', color=NAVY, markersize=5)
        ax.text(x, h0_vis / 2 + 0.015, f'Node {i}', ha='center', fontsize=8, color=GREY)

    ax.set_xlim(-0.05, L_total + 0.05)
    ax.set_ylim(-0.3, h0_vis * 0.7)
    ax.set_axis_off()
    ax.set_title("Simply-Supported Beam Geometry", fontsize=12, fontweight='bold', color=NAVY)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig('results/beam_geometry.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_mode_shapes_continuous(n_elem, L_total, mode_shapes_classical, free_dofs,
                                mode_shapes_vqe=None, analytical_params=None, n_modes=3):
    """
    Plot mode shapes as continuous deflection curves using Hermite
    cubic interpolation (FEA shape functions).
    """
    n_modes = min(n_modes, mode_shapes_classical.shape[1])
    n_nodes = n_elem + 1
    L_e = L_total / n_elem
    x_nodes = np.array([i * L_e for i in range(n_nodes)])
    ndof_full = 2 * n_nodes

    displacement_dofs = [d for d in free_dofs if d % 2 == 0]
    rotation_dofs = [d for d in free_dofs if d % 2 == 1]

    def hermite_interp(node_vals, node_rots, x_nodes_arr, x_eval):
        """C1-continuous Hermite cubic interpolation."""
        n_e = len(node_vals) - 1
        result = np.zeros_like(x_eval)
        for e in range(n_e):
            x1, x2 = x_nodes_arr[e], x_nodes_arr[e + 1]
            Le = x2 - x1
            mask = (x_eval >= x1) & (x_eval <= x2)
            if not np.any(mask):
                continue
            xi = (x_eval[mask] - x1) / Le
            N1 = 1 - 3 * xi ** 2 + 2 * xi ** 3
            N2 = Le * (xi - 2 * xi ** 2 + xi ** 3)
            N3 = 3 * xi ** 2 - 2 * xi ** 3
            N4 = Le * (-xi ** 2 + xi ** 3)
            result[mask] = (N1 * node_vals[e] + N2 * node_rots[e] +
                           N3 * node_vals[e + 1] + N4 * node_rots[e + 1])
        return result

    fig, axes = plt.subplots(1, n_modes, figsize=(16, 4))
    if n_modes == 1:
        axes = [axes]
    fig.suptitle("Mode Shape Deflection Profiles",
                 fontsize=14, fontweight='bold', color=NAVY)

    x_fine = np.linspace(0, L_total, 200)

    for i in range(n_modes):
        ax = axes[i]
        ax.axhline(0, color='black', linewidth=0.5)

        # Classical mode shape
        m_c = mode_shapes_classical[:, i]
        full_disp = np.zeros(ndof_full)
        full_rot = np.zeros(ndof_full)
        for d in displacement_dofs:
            full_disp[d] = m_c[free_dofs.index(d)]
        for d in rotation_dofs:
            full_rot[d] = m_c[free_dofs.index(d)]

        node_disp = full_disp[0::2]
        node_rot = full_rot[1::2]

        y_c = hermite_interp(node_disp, node_rot, x_nodes, x_fine)
        y_c /= (np.max(np.abs(y_c)) + 1e-12)
        ax.plot(x_fine * 1000, y_c, color=RED, linewidth=2.5,
                label='Classical (FEA)', zorder=3)

        # VQE mode shape
        if mode_shapes_vqe is not None and len(mode_shapes_vqe) > i:
            m_v = mode_shapes_vqe[i]
            full_disp_v = np.zeros(ndof_full)
            full_rot_v = np.zeros(ndof_full)
            for d in displacement_dofs:
                full_disp_v[d] = m_v[free_dofs.index(d)]
            for d in rotation_dofs:
                full_rot_v[d] = m_v[free_dofs.index(d)]
            node_disp_v = full_disp_v[0::2]
            node_rot_v = full_rot_v[1::2]
            y_v = hermite_interp(node_disp_v, node_rot_v, x_nodes, x_fine)
            y_v /= (np.max(np.abs(y_v)) + 1e-12)
            if np.dot(y_v, y_c) < 0:
                y_v = -y_v
            ax.plot(x_fine * 1000, y_v, '--', color=BLUE, linewidth=2.5,
                    label='VQE', zorder=4)

        # Analytical simply-supported mode: sin(n*pi*x/L)
        if analytical_params is not None:
            L_a = analytical_params.get('L', L_total)
            n_mode = i + 1
            y_a = np.sin(n_mode * np.pi * x_fine / L_a)
            if np.dot(y_a, y_c) < 0:
                y_a = -y_a
            ax.plot(x_fine * 1000, y_a, ':', color=GREEN, linewidth=2,
                    label='Analytical (exact)', zorder=2, alpha=0.8)

        ax.scatter(x_nodes * 1000, np.zeros_like(x_nodes), color=NAVY,
                   s=50, zorder=5, edgecolors='white', linewidth=1)
        ax.set_xlabel("Position x (mm)", fontsize=11)
        ax.set_ylabel("Normalized Displacement", fontsize=10)
        ax.set_title(f"Mode {i + 1}", fontweight='bold')
        ax.legend(fontsize=9)
        ax.set_facecolor(LIGHT)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/mode_shapes_continuous.png', dpi=150, bbox_inches='tight')
    plt.show()


# ============================================================
# DUAL OPTIMIZER CONVERGENCE
# ============================================================

def plot_dual_convergence(cobyla_costs, lbfgs_costs, omega_ref, H_scale=1.0):
    """Side-by-side convergence of COBYLA and L-BFGS-B."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Optimizer Comparison: COBYLA vs L-BFGS-B",
                 fontsize=14, fontweight='bold', color=NAVY)

    freqs_c = [np.sqrt(max(c * H_scale, 0)) for c in cobyla_costs]
    freqs_l = [np.sqrt(max(c * H_scale, 0)) for c in lbfgs_costs]

    # Top-left: COBYLA
    ax1 = axes[0, 0]
    ax1.plot(freqs_c, color=ORANGE, linewidth=1.5)
    ax1.axhline(y=omega_ref, color=RED, linestyle='--', linewidth=2, label='Classical')
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Frequency (rad/s)")
    ax1.set_title("COBYLA (derivative-free simplex)", fontweight='bold', color=ORANGE)
    ax1.legend()
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.4)

    # Top-right: L-BFGS-B
    ax2 = axes[0, 1]
    ax2.plot(freqs_l, color=GREEN, linewidth=1.5)
    ax2.axhline(y=omega_ref, color=RED, linestyle='--', linewidth=2, label='Classical')
    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Frequency (rad/s)")
    ax2.set_title("L-BFGS-B (gradient-based quasi-Newton)", fontweight='bold', color=GREEN)
    ax2.legend()
    ax2.set_facecolor(LIGHT)
    ax2.grid(True, alpha=0.4)

    # Bottom-left: Error decay
    err_c = [(abs(f - omega_ref) / omega_ref * 100) for f in freqs_c if f > 0]
    err_l = [(abs(f - omega_ref) / omega_ref * 100) for f in freqs_l if f > 0]
    ax3 = axes[1, 0]
    ax3.semilogy(err_c, color=ORANGE, linewidth=1.5, label='COBYLA')
    ax3.semilogy(err_l, color=GREEN, linewidth=1.5, label='L-BFGS-B')
    ax3.set_xlabel("Iteration")
    ax3.set_ylabel("Relative Error (%)")
    ax3.set_title("Error Decay (log scale)", fontweight='bold')
    ax3.legend()
    ax3.set_facecolor(LIGHT)
    ax3.grid(True, alpha=0.4, which='both')

    # Bottom-right: Normalized error
    ax4 = axes[1, 1]
    if err_c:
        ax4.semilogy([e / err_c[0] for e in err_c], color=ORANGE, linewidth=1.5,
                    label='COBYLA (derivative-free)')
    if err_l:
        ax4.semilogy([e / err_l[0] for e in err_l], color=GREEN, linewidth=1.5,
                    label='L-BFGS-B (gradient-based)')
    ax4.set_xlabel("Iteration")
    ax4.set_ylabel("Error Fraction (E / E\u2080)")
    ax4.set_title("Convergence Rate", fontweight='bold')
    ax4.legend()
    ax4.set_facecolor(LIGHT)
    ax4.grid(True, alpha=0.4, which='both')
    ax4.text(0.98, 0.02,
             f"COBYLA:   {len(cobyla_costs)} iters  final error = {err_c[-1]:.4f}%\n"
             f"L-BFGS-B: {len(lbfgs_costs)} iters  final error = {err_l[-1]:.6f}%",
             transform=ax4.transAxes, fontsize=9, va='bottom', ha='right',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor=NAVY, alpha=0.9))

    plt.tight_layout()
    plt.savefig('results/optimizer_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_optimizer_comparison(cobyla_results, lbfgs_results, classical_ref,
                               taper_ratios, condition_numbers):
    """Side-by-side comparison across geometries (taper ratios)."""
    n_geos = len(taper_ratios)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Optimizer Comparison: COBYLA vs L-BFGS-B",
                 fontsize=14, fontweight='bold', color=NAVY)

    ax1 = axes[0, 0]
    colors_geo = plt.cm.viridis(np.linspace(0.1, 0.9, n_geos))
    for j, t in enumerate(taper_ratios):
        hist = cobyla_results[j]['cost_history']
        ax1.plot(hist, color=colors_geo[j], linewidth=1.2,
                 label=f't={t:.2f}', alpha=0.7)
    ax1.set_title("COBYLA Convergence (all geometries)", fontweight='bold')
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Cost")
    ax1.legend(fontsize=8, ncol=2)
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.3)

    ax2 = axes[0, 1]
    for j, t in enumerate(taper_ratios):
        hist = lbfgs_results[j]['cost_history']
        ax2.plot(hist, color=colors_geo[j], linewidth=1.2,
                 label=f't={t:.2f}', alpha=0.7)
    ax2.set_title("L-BFGS-B Convergence (all geometries)", fontweight='bold')
    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Cost")
    ax2.legend(fontsize=8, ncol=2)
    ax2.set_facecolor(LIGHT)
    ax2.grid(True, alpha=0.3)

    ax3 = axes[1, 0]
    x = np.arange(n_geos)
    w = 0.25
    ax3.bar(x - w, classical_ref, w, label='Classical', color=NAVY, alpha=0.85)
    ax3.bar(x, [r['omega'] for r in cobyla_results], w, label='COBYLA',
            color=ORANGE, alpha=0.85)
    ax3.bar(x + w, [r['omega'] for r in lbfgs_results], w, label='L-BFGS-B',
            color=GREEN, alpha=0.85)
    ax3.set_xticks(x)
    ax3.set_xticklabels([f'{t:.2f}' for t in taper_ratios])
    ax3.set_xlabel("Taper Ratio")
    ax3.set_ylabel("Frequency (rad/s)")
    ax3.set_title("Frequency Accuracy", fontweight='bold')
    ax3.legend()
    ax3.set_facecolor(LIGHT)
    ax3.grid(True, alpha=0.3, axis='y')

    ax4 = axes[1, 1]
    cobyla_errs = [abs(r['omega'] - classical_ref[i]) / classical_ref[i] * 100
                   for i, r in enumerate(cobyla_results)]
    lbfgs_errs = [abs(r['omega'] - classical_ref[i]) / classical_ref[i] * 100
                  for i, r in enumerate(lbfgs_results)]
    ax4.scatter(condition_numbers, cobyla_errs, color=ORANGE, s=120,
                zorder=5, edgecolors=NAVY, linewidths=1.5, label='COBYLA')
    ax4.scatter(condition_numbers, lbfgs_errs, color=GREEN, s=120,
                zorder=5, edgecolors=NAVY, linewidths=1.5, label='L-BFGS-B')
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.set_xlabel("Condition Number of H")
    ax4.set_ylabel("Frequency Error (%)")
    ax4.set_title("Error vs Ill-Conditioning", fontweight='bold')
    ax4.legend()
    ax4.set_facecolor(LIGHT)
    ax4.grid(True, alpha=0.3, which='both')

    plt.tight_layout()
    plt.savefig('results/optimizer_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


# ============================================================
# ORIGINAL PLOTS (unchanged)
# ============================================================

def plot_convergence(cost_history, omega_vqe, omega_ref, H_scale=1.0, title="VQE Convergence"):
    """Plot VQE cost function convergence."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold', color=NAVY)

    physical_costs = [c * H_scale for c in cost_history]
    ax1.plot(physical_costs, color=BLUE, linewidth=1.5, alpha=0.8)
    ax1.axhline(y=omega_ref**2, color=RED, linestyle='--',
                label=f'Classical lambda = {omega_ref**2:.4f}', linewidth=2)
    ax1.set_xlabel("Iteration", fontsize=12)
    ax1.set_ylabel("Cost <psi(theta)|H|psi(theta)>", fontsize=12)
    ax1.set_title("Cost Function vs Iteration", fontweight='bold')
    ax1.legend()
    ax1.set_facecolor(LIGHT)
    ax1.grid(True, alpha=0.4)

    if omega_ref > 0:
        errors = [abs(np.sqrt(max(c, 0) * H_scale) - omega_ref) / omega_ref * 100
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

    for i, ax in enumerate(axes):
        m_classical = mode_shapes_classical[:, i]
        if len(mode_shapes_vqe) > i:
            m_vqe = mode_shapes_vqe[i]
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

    ax.bar(x - width/2, omega_classical, width,
           label='Classical (scipy)', color=NAVY, alpha=0.85, edgecolor='white')

    colors = [BLUE, CYAN, GREEN, ORANGE]
    for i, (omega_vqe, label) in enumerate(zip(omega_vqe_list,
                                                 labels or [f'VQE Run {i+1}']*len(omega_vqe_list))):
        offset = (i - len(omega_vqe_list)//2) * (width/len(omega_vqe_list))
        ax.bar(x + width/2 + offset, omega_vqe[:n], width/len(omega_vqe_list),
               label=label, color=colors[i % len(colors)], alpha=0.85,
               edgecolor='white')

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
    """COBYLA vs L-BFGS-B vs Exact across taper ratios."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Optimizer Convergence: COBYLA vs L-BFGS-B vs Exact",
                 fontsize=14, fontweight='bold', color=NAVY)

    axes[0, 0].plot(df['taper_ratio'], df['condition_number'],
                    'o-', color=BLUE, linewidth=2.5, markersize=10,
                    markeredgecolor=NAVY, markeredgewidth=1.5)
    axes[0, 0].set_xlabel("Taper Ratio (h_end / h_start)", fontsize=11)
    axes[0, 0].set_ylabel("Condition Number of H", fontsize=11)
    axes[0, 0].set_title("Taper Controls Ill-Conditioning", fontweight='bold')
    axes[0, 0].set_facecolor(LIGHT)
    axes[0, 0].grid(True, alpha=0.4)

    axes[0, 1].scatter(df['condition_number'], df['cobyla_error_pct'],
                       color=ORANGE, s=120, zorder=5, edgecolors=NAVY, linewidths=1.5)
    axes[0, 1].set_xlabel("Condition Number kappa(H)", fontsize=11)
    axes[0, 1].set_ylabel("COBYLA Frequency Error (%)", fontsize=11)
    axes[0, 1].set_title("COBYLA Error vs Ill-Conditioning", fontweight='bold')
    axes[0, 1].set_xscale('log')
    axes[0, 1].set_facecolor(LIGHT)
    axes[0, 1].grid(True, alpha=0.4)

    axes[0, 2].scatter(df['condition_number'], df['lbfgs_error_pct'],
                       color=GREEN, s=120, zorder=5, edgecolors=NAVY, linewidths=1.5)
    axes[0, 2].set_xlabel("Condition Number kappa(H)", fontsize=11)
    axes[0, 2].set_ylabel("L-BFGS-B Frequency Error (%)", fontsize=11)
    axes[0, 2].set_title("L-BFGS-B Error vs Ill-Conditioning", fontweight='bold')
    axes[0, 2].set_xscale('log')
    axes[0, 2].set_facecolor(LIGHT)
    axes[0, 2].grid(True, alpha=0.4)

    x = np.arange(len(df))
    w = 0.35
    axes[1, 0].bar(x - w/2, df['cobyla_iterations'], w,
                   label='COBYLA', color=ORANGE, alpha=0.85, edgecolor='white')
    axes[1, 0].bar(x + w/2, df['lbfgs_iterations'], w,
                   label='L-BFGS-B', color=GREEN, alpha=0.85, edgecolor='white')
    axes[1, 0].set_xticks(x)
    taper_labels = [f"t={t:.2f}" for t in df['taper_ratio']]
    axes[1, 0].set_xticklabels(taper_labels)
    axes[1, 0].set_ylabel("Iterations", fontsize=11)
    axes[1, 0].set_title("Iterations to Convergence", fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].set_facecolor(LIGHT)
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    axes[1, 1].bar(x - w, df['omega_classical'], w,
                   label='Classical (exact)', color=NAVY, alpha=0.85, edgecolor='white')
    axes[1, 1].bar(x, df['omega_cobyla'], w,
                   label='VQE (COBYLA)', color=ORANGE, alpha=0.85, edgecolor='white')
    axes[1, 1].bar(x + w, df['omega_lbfgs'], w,
                   label='VQE (L-BFGS-B)', color=GREEN, alpha=0.85, edgecolor='white')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(taper_labels)
    axes[1, 1].set_ylabel("Frequency (rad/s)", fontsize=11)
    axes[1, 1].set_title("Frequency: Classical vs Optimizers", fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].set_facecolor(LIGHT)
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    axes[1, 2].bar(x - w/2, df['cobyla_error_pct'], w,
                   label='COBYLA', color=ORANGE, alpha=0.85, edgecolor='white')
    axes[1, 2].bar(x + w/2, df['lbfgs_error_pct'], w,
                   label='L-BFGS-B', color=GREEN, alpha=0.85, edgecolor='white')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(taper_labels)
    axes[1, 2].set_ylabel("Error (%)", fontsize=11)
    axes[1, 2].set_title("Optimizer Error Comparison", fontweight='bold')
    axes[1, 2].legend()
    axes[1, 2].set_facecolor(LIGHT)
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    axes[1, 2].set_yscale('log')

    plt.tight_layout()
    plt.savefig('results/ill_conditioning_study.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_damage_detection(df):
    """Frequency shift vs damage severity."""
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
