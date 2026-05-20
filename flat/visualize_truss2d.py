"""
2D Warren Truss Visualization Functions

This module contains visualization functions for the 2D Warren truss,
including geometry plotting, mode shape visualization, and animation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — prevents Tkinter main-loop errors
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, Circle

# Color scheme (matching visualize.py)
NAVY    = "#1A2151"
BLUE    = "#0D6EFD"
CYAN    = "#00B4D8"
GREEN   = "#0A7C59"
RED     = "#C0392B"
ORANGE  = "#E67E22"
GREY    = "#566573"
LIGHT   = "#EBF5FB"


def plot_truss2d_geometry(nodes, members, node_ids, title="2D Warren Truss Geometry"):
    """
    Plot 2D Warren truss geometry with node labels and member connectivity.

    Parameters
    ----------
    nodes : ndarray (n_nodes, 2)    Node coordinates [x, y]
    members : list of tuple            (i, j, E, A, rho) for each member
    node_ids : dict                    Mapping of node labels to indices
    title : str                        Plot title
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    # Draw members as lines
    for idx, (i, j, E, A, rho) in enumerate(members):
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        ax.plot([xi, xj], [yi, yj], color=GREY, linewidth=3,
               alpha=0.7, zorder=1, label='Members' if idx == 0 else '')

    # Draw nodes
    for label, idx in sorted(node_ids.items(), key=lambda x: x[1]):
        x, y = nodes[idx]
        color = BLUE if label.startswith('B') else CYAN
        ax.scatter(x, y, s=200, c=color, zorder=5,
                   edgecolors=NAVY, linewidths=2,
                   label='Bottom chord' if label.startswith('B') and idx == 0 else
                         ('Top chord' if label.startswith('T') and idx == len(node_ids)//2 else ''))

    # Node labels
    for label, idx in sorted(node_ids.items(), key=lambda x: x[1]):
        x, y = nodes[idx]
        offset = -0.05 if label.startswith('B') else 0.05
        ax.text(x, y + offset, label, ha='center', va='center',
               fontsize=10, fontweight='bold', color=NAVY)

    # Draw pinned support at B0
    B0_idx = node_ids['B0']
    x0, y0 = nodes[B0_idx]
    triangle = Polygon(
        [(x0, y0 - 0.05), (x0 - 0.06, y0 - 0.12), (x0 + 0.06, y0 - 0.12)],
        facecolor='red', edgecolor='black', zorder=10, label='Pinned support'
    )
    ax.add_patch(triangle)

    # Draw roller support at last bottom chord node (Bn-1)
    n_chords = (nodes.shape[0] + 1) // 2
    B_last_label = f'B{n_chords - 1}'
    B_last_idx = node_ids.get(B_last_label, B0_idx)
    x_last, y_last = nodes[B_last_idx]
    triangle = Polygon(
        [(x_last, y_last - 0.05), (x_last - 0.06, y_last - 0.12), (x_last + 0.06, y_last - 0.12)],
        facecolor='red', edgecolor='black', zorder=10, label='Roller support'
    )
    ax.add_patch(triangle)
    # Roller circles
    for dx in [-0.03, 0.03]:
        circle = Circle((x_last + dx, y_last - 0.14), 0.015, color='red', fill=True, zorder=10)
        ax.add_patch(circle)

    ax.set_aspect('equal')
    ax.set_xlabel("x (m)", fontsize=12)
    ax.set_ylabel("y (m)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', color=NAVY)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    # Dynamic y limits based on truss height
    y_min = nodes[:, 1].min() - 0.2
    y_max = nodes[:, 1].max() + 0.3
    ax.set_ylim(y_min, max(y_max, 0.6))

    plt.tight_layout()
    plt.savefig('results/truss2d_geometry.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_truss2d_mode_shapes(nodes, members, node_ids, mode_shapes,
                                free_dofs, n_modes=4, scale=1.0):
    """
    Plot 2D truss mode shapes (deformed overlay on undeformed truss).

    Parameters
    ----------
    nodes : ndarray (n_nodes, 2)        Node coordinates
    members : list of tuple                (i, j, E, A, rho)
    node_ids : dict                            Mapping of node labels to indices
    mode_shapes : ndarray (n_free, n_modes)  Mode shapes (reduced)
    free_dofs : list                           Indices of free DOFs
    n_modes : int                                Number of modes to plot
    scale : float                                 Displacement scaling factor
    """
    n_total_dof = 2 * nodes.shape[0]
    n_plot = min(n_modes, mode_shapes.shape[1])

    fig, axes = plt.subplots(1, n_plot, figsize=(5 * n_plot, 5))
    if n_plot == 1:
        axes = [axes]

    for m_idx in range(n_plot):
        ax = axes[m_idx]

        # Undeformed truss (gray dashed)
        for idx, (i, j, E, A, rho) in enumerate(members):
            ax.plot([nodes[i, 0], nodes[j, 0]],
                   [nodes[i, 1], nodes[j, 1]],
                   'k--', linewidth=1.5, alpha=0.5,
                   label='Undeformed' if idx == 0 else '')

        # Expand mode to full DOF space
        mode_full = np.zeros(n_total_dof)
        mode_full[free_dofs] = mode_shapes[:, m_idx]

        # Normalize and scale
        if np.max(np.abs(mode_full)) > 1e-10:
            mode_norm = mode_full / np.max(np.abs(mode_full))
        else:
            mode_norm = mode_full

        # Deformed coordinates
        x_def = np.zeros(nodes.shape[0])
        y_def = np.zeros(nodes.shape[0])
        for i in range(nodes.shape[0]):
            if 2*i < len(mode_norm):
                x_def[i] = nodes[i, 0] + scale * mode_norm[2*i]
            if 2*i+1 < len(mode_norm):
                y_def[i] = nodes[i, 1] + scale * mode_norm[2*i+1]

        # Draw deformed truss
        for idx, (i, j, E, A, rho) in enumerate(members):
            ax.plot([x_def[i], x_def[j]],
                   [y_def[i], y_def[j]],
                   'o-', color=BLUE, linewidth=2.5, markersize=6,
                   label='Deformed' if idx == 0 else '')

        # Draw deformed nodes
        ax.scatter(x_def, y_def, s=100, c=BLUE, zorder=5,
                   edgecolors=NAVY, linewidths=1.5)

        ax.set_aspect('equal')
        ax.set_title(f"Mode {m_idx+1}", fontsize=12, fontweight='bold')
        ax.set_xlabel("x (m)", fontsize=10)
        ax.set_ylabel("y (m)", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        # Dynamic y limits
        y_min = nodes[:, 1].min() - 0.3
        y_max = nodes[:, 1].max() + 0.5
        ax.set_ylim(y_min, max(y_max, 0.6))

    plt.suptitle("2D Warren Truss Mode Shapes",
                 fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/truss2d_mode_shapes.png', dpi=150, bbox_inches='tight')
    plt.show()


def animate_truss2d_mode(nodes, members, node_ids, mode_shape,
                          free_dofs, mode_num=1, n_frames=60, scale=1.0,
                          interval=50):
    """
    Create animated GIF of oscillating truss for a given mode shape.

    Parameters
    ----------
    nodes, members, node_ids : same as plot_truss2d_mode_shapes()
    mode_shape : ndarray (n_free,)    Mode shape (single mode)
    free_dofs : list                   Indices of free DOFs
    mode_num : int                      Mode number (for filename)
    n_frames : int                     Frames in animation
    scale : float                       Displacement scale
    interval : int                      ms between frames
    """
    n_total_dof = 2 * nodes.shape[0]

    # Expand mode to full DOF space
    mode_full = np.zeros(n_total_dof)
    mode_full[free_dofs] = mode_shape

    # Normalize
    if np.max(np.abs(mode_full)) > 1e-10:
        mode_norm = mode_full / np.max(np.abs(mode_full))
    else:
        mode_norm = mode_full

    # Setup figure
    fig, ax = plt.subplots(figsize=(12, 4))

    # Undeformed members (gray dashed)
    for i, j, E, A, rho in members:
        ax.plot([nodes[i, 0], nodes[j, 0]],
               [nodes[i, 1], nodes[j, 1]],
               'k--', linewidth=1, alpha=0.3, label='Undeformed')

    # Deformed members (will be updated)
    lines = []
    for i, j, E, A, rho in members:
        line, = ax.plot([nodes[i, 0], nodes[j, 0]],
                        [nodes[i, 1], nodes[j, 1]],
                        'o-', color=BLUE, linewidth=2.5, markersize=6)
        lines.append(line)

    ax.set_aspect('equal')
    ax.set_xlabel("x (m)", fontsize=12)
    ax.set_ylabel("y (m)", fontsize=12)
    ax.set_title(f"Mode {mode_num} Oscillation", fontsize=14, fontweight='bold', color=NAVY)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.2, 0.6)
    ax.legend(fontsize=10)

    def animate(frame):
        t = 2 * np.pi * frame / n_frames
        disp = scale * np.sin(t) * mode_norm

        x_def = np.zeros(nodes.shape[0])
        y_def = np.zeros(nodes.shape[0])
        for i in range(nodes.shape[0]):
            if 2*i < len(disp):
                x_def[i] = nodes[i, 0] + disp[2*i]
            if 2*i+1 < len(disp):
                y_def[i] = nodes[i, 1] + disp[2*i+1]

        for idx, line in enumerate(lines):
            i, j = members[idx][0], members[idx][1]
            line.set_data([x_def[i], x_def[j]], [y_def[i], y_def[j]])

        return lines

    anim = animation.FuncAnimation(fig, animate, frames=n_frames,
                                    interval=interval, blit=True)

    anim.save(f'results/truss2d_mode{mode_num}_animation.gif',
              writer='pillow', fps=30, dpi=100)
    plt.close()
    print(f"[OK] Animation saved: results/truss2d_mode{mode_num}_animation.gif")


def plot_truss2d_frequency_comparison(omega_vqe_list, omega_classical,
                                      labels=None, title="2D Truss Natural Frequencies"):
    """
    Bar chart comparing VQE vs Classical natural frequencies for 2D truss.

    Parameters
    ----------
    omega_vqe_list : list of list        VQE frequencies for each run
    omega_classical : ndarray            Classical reference frequencies
    labels : list of str, optional    Labels for VQE runs
    title : str                             Plot title
    """
    if labels is None:
        labels = ['VQE']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    n_modes = min(len(omega_classical), 6)
    x = np.arange(n_modes)
    width = 0.35

    # Frequencies
    for i, (vqe_f, label) in enumerate(zip(omega_vqe_list, labels)):
        offset = width * i
        ax1.bar(x + offset, vqe_f[:n_modes], width, label=label,
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax1.bar(x + width * len(omega_vqe_list), omega_classical[:n_modes], width,
           label='Classical (FEA)', color=RED, alpha=0.8)

    ax1.set_ylabel('Natural Frequency (rad/s)', fontsize=12)
    ax1.set_title('VQE vs Classical: 2D Warren Truss',
                  fontweight='bold', color=NAVY)
    ax1.set_xticks(x + width * (len(omega_vqe_list) + 1) / 2)
    ax1.set_xticklabels([f'Mode {i+1}' for i in range(n_modes)])
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # Relative errors
    for i, (vqe_f, label) in enumerate(zip(omega_vqe_list, labels)):
        offset = width * i
        errors = np.abs(np.array(vqe_f[:n_modes]) - omega_classical[:n_modes]) / omega_classical[:n_modes] * 100
        ax2.bar(x + offset, errors, width, label=label,
               color=BLUE if i == 0 else CYAN, alpha=0.8)

    ax2.set_ylabel('Relative Error (%)', fontsize=12)
    ax2.set_title('VQE Accuracy for 2D Warren Truss',
                  fontweight='bold', color=NAVY)
    ax2.set_xticks(x + width * (len(omega_vqe_list) + 1) / 2)
    ax2.set_xticklabels([f'Mode {i+1}' for i in range(n_modes)])
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(2, color='red', linestyle='--', linewidth=1, alpha=0.5,
               label='Target: <2%')

    plt.suptitle(title, fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/truss2d_frequency_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # Quick test
    from truss import generate_warren_truss_mesh, assemble_truss2d, apply_pinned_roller_bc, classical_modal_analysis

    # Generate mesh
    nodes, members, node_ids = generate_warren_truss_mesh()

    # Assemble and solve
    K, M = assemble_truss2d(nodes, members)
    K_red, M_red, free_dofs, fixed_dofs = apply_pinned_roller_bc(K, M, nodes)
    omega, modes, eigenvalues = classical_modal_analysis(K_red, M_red, n_modes=4)

    # Plot geometry
    plot_truss2d_geometry(nodes, members, node_ids)

    # Plot mode shapes
    plot_truss2d_mode_shapes(nodes, members, node_ids, modes, free_dofs, n_modes=4, scale=0.5)

    print("[OK] 2D truss visualization module ready.")
