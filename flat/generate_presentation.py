"""
Generate Presentation Slides for VQA Modal Analysis Project
Creates a matplotlib-based slide deck covering all project results.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import os

os.makedirs('results', exist_ok=True)

# Color scheme
NAVY    = "#1A2151"
BLUE    = "#0D6EFD"
CYAN    = "#00B4D8"
GREEN   = "#0A7C59"
RED     = "#C0392B"
ORANGE  = "#E67E22"
GREY    = "#566573"
LIGHT   = "#EBF5FB"
PURPLE  = "#6C3483"
TEAL    = "#1ABC9C"

def create_title_slide():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    ax.text(0.5, 0.65, "VQA Modal Analysis",
            transform=ax.transAxes, fontsize=48, fontweight='bold',
            color='white', ha='center', va='center')
    ax.text(0.5, 0.50, "Quantum Computing for Structural Dynamics",
            transform=ax.transAxes, fontsize=28, color=CYAN,
            ha='center', va='center', style='italic')
    ax.text(0.5, 0.40, "COEP Technological University",
            transform=ax.transAxes, fontsize=18, color='white',
            ha='center', va='center', alpha=0.7)
    ax.text(0.5, 0.34, "May 2026",
            transform=ax.transAxes, fontsize=16, color='white',
            ha='center', va='center', alpha=0.5)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('results/slide_00_title.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()

def create_problem_slide():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    ax.text(0.05, 0.90, "The Problem: Structural Modal Analysis",
            fontsize=28, fontweight='bold', color=NAVY,
            transform=ax.transAxes)

    # Problem description
    problem_text = (
        "Determine natural frequencies (ω) and mode shapes (φ) of structures\n"
        "Governing equation: Kφ = ω²Mφ\n\n"
        "Applications:\n"
        "  • Design validation & resonance avoidance\n"
        "  • Structural health monitoring\n"
        "  • Vibration analysis\n\n"
        "Classical approach: O(N³) eigenvalue decomposition\n"
        "For large structures → computationally expensive"
    )
    ax.text(0.05, 0.70, problem_text, fontsize=14, color=GREY,
            transform=ax.transAxes, verticalalignment='top',
            fontfamily='monospace')

    # Equation box
    eq_text = "Kφ = ω²Mφ"
    ax.text(0.55, 0.35, eq_text, fontsize=40, fontweight='bold',
            color=RED, transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT,
                     edgecolor=RED, linewidth=2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('results/slide_01_problem.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()

def create_quantum_insight_slide():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor('white')

    ax.text(0.05, 0.88, "The Quantum Insight", fontsize=28,
            fontweight='bold', color=NAVY, transform=ax.transAxes)
    ax.text(0.05, 0.82, "Both are Hermitian eigenvalue problems!",
            fontsize=18, color=RED, fontweight='bold',
            transform=ax.transAxes)

    # Mapping arrows
    mappings = [
        ("Structural", "Kφ = ω²Mφ", 0.55),
        ("↓ Transform", "H = M⁻¹/²KM⁻¹/²", 0.40),
        ("Quantum", "H|ψ⟩ = λ|ψ⟩", 0.25),
    ]

    for i, (label, eq, y) in enumerate(mappings):
        color = [RED, ORANGE, GREEN][i]
        ax.text(0.05, y, label, fontsize=16, fontweight='bold',
                color=color, transform=ax.transAxes)
        ax.text(0.35, y, eq, fontsize=20, color=NAVY,
                transform=ax.transAxes, fontfamily='monospace')
        if i < 2:
            ax.annotate('', xy=(0.3, y-0.08), xytext=(0.3, y-0.02),
                       arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))

    # Key point
    ax.text(0.05, 0.10, "Key Point: Same math, different physics",
            fontsize=16, color=PURPLE, fontweight='bold',
            transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('results/slide_02_quantum_insight.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_results_summary():
    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    fig.patch.set_facecolor('white')
    for ax in axes.flat:
        ax.set_facecolor('white')

    axes[0, 0].set_title("BEAM Results", fontsize=14, fontweight='bold',
                         color=NAVY)
    beam_data = [1443.4879, 1443.4879, 1443.4879]
    labels = ['COBYLA', 'L-BFGS-B', 'Classical']
    colors = [BLUE, ORANGE, RED]
    bars = axes[0, 0].bar(labels, beam_data, color=colors, alpha=0.8, width=0.5)
    axes[0, 0].set_ylabel('ω (rad/s)', fontsize=12)
    axes[0, 0].set_ylim(1400, 1500)
    for bar, val in zip(bars, beam_data):
        axes[0, 0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
                       f'{val:.2f}', ha='center', fontsize=10)
    axes[0, 0].grid(axis='y', alpha=0.3)

    axes[0, 1].set_title("1D TRUSS Results", fontsize=14, fontweight='bold',
                         color=NAVY)
    truss_data = [16267.3852, 16267.3852, 16267.3852]
    bars = axes[0, 1].bar(labels, truss_data, color=colors, alpha=0.8, width=0.5)
    axes[0, 1].set_ylabel('ω (rad/s)', fontsize=12)
    axes[0, 1].set_ylim(15500, 17000)
    for bar, val in zip(bars, truss_data):
        axes[0, 1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+20,
                       f'{val:.2f}', ha='center', fontsize=10)
    axes[0, 1].grid(axis='y', alpha=0.3)

    axes[1, 0].set_title("2D Warren TRUSS", fontsize=14, fontweight='bold',
                         color=NAVY)
    twod_labels = ['VQE', 'Classical 1', 'Classical 2']
    twod_data = [3970.4796, 3970.4795, 7635.7410]
    colors2 = [BLUE, RED, GREEN]
    bars = axes[1, 0].bar(twod_labels, twod_data, color=colors2, alpha=0.8,
                          width=0.5)
    axes[1, 0].set_ylabel('ω (rad/s)', fontsize=12)
    for bar, val in zip(bars, twod_data):
        axes[1, 0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+20,
                       f'{val:.2f}', ha='center', fontsize=10)
    axes[1, 0].grid(axis='y', alpha=0.3)

    axes[1, 1].set_title("Optimizer Convergence", fontsize=14,
                         fontweight='bold', color=NAVY)
    axes[1, 1].text(0.5, 0.5, "See optimizer_comparison.png\n"
                    "COBYLA: 2000 iters\n"
                    "L-BFGS-B: 351 iters",
                    ha='center', va='center', fontsize=14,
                    transform=axes[1, 1].transAxes)
    axes[1, 1].axis('off')

    plt.suptitle("VQA Modal Analysis — Key Results", fontsize=20,
                 fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig('results/slide_03_results_summary.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_pipeline_slide():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    ax.text(0.5, 0.90, "Project Pipeline", fontsize=32,
            fontweight='bold', color='white', ha='center',
            transform=ax.transAxes)

    steps = [
        ("1", "Classical\nFEA", "K, M matrices"),
        ("2", "Quantum\nHamiltonian", "H = M⁻¹/²KM⁻¹/²"),
        ("3", "VQE\nOptimization", "COBYLA / L-BFGS-B"),
        ("4", "Deflation", "Higher modes"),
        ("5", "Novel\nStudies", "Ill-conditioning"),
        ("6", "Visualization", "Plots & Analysis"),
    ]

    x_start = 0.05
    x_end = 0.95
    y_pos = 0.55
    n = len(steps)

    for i, (num, title, desc) in enumerate(steps):
        x = x_start + (x_end - x_start) * i / (n - 1)
        circ = plt.Circle((x, y_pos), 0.08, color=CYAN, ec='white', lw=2)
        ax.add_patch(circ)
        ax.text(x, y_pos, num, fontsize=20, fontweight='bold',
                color=NAVY, ha='center', va='center',
                transform=ax.transAxes)
        ax.text(x, y_pos-0.15, title, fontsize=12, color='white',
                ha='center', va='center', fontweight='bold',
                transform=ax.transAxes)
        ax.text(x, y_pos-0.25, desc, fontsize=10, color=CYAN,
                ha='center', va='center', transform=ax.transAxes)
        if i < n - 1:
            next_x = x_start + (x_end - x_start) * (i+1) / (n - 1)
            ax.annotate('', xy=(next_x-0.03, y_pos),
                       xytext=(x+0.03, y_pos),
                       arrowprops=dict(arrowstyle='->', color='white', lw=2))

    plt.tight_layout()
    plt.savefig('results/slide_04_pipeline.png', dpi=150,
                bbox_inches='tight', facecolor=NAVY)
    plt.close()

def create_mode_shape_slide():
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('white')

    axes[0].set_title("BEAM Mode Shapes (VQE vs Classical)", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/mode_shapes_continuous.png')
        axes[0].imshow(img)
        axes[0].axis('off')
    except:
        axes[0].text(0.5, 0.5, "See mode_shapes_continuous.png",
                     ha='center', va='center', transform=axes[0].transAxes)

    axes[1].set_title("TRUSS Mode Shapes (Axial Displacement)", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss_mode_shapes.png')
        axes[1].imshow(img)
        axes[1].axis('off')
    except:
        axes[1].text(0.5, 0.5, "See truss_mode_shapes.png",
                     ha='center', va='center', transform=axes[1].transAxes)

    plt.tight_layout()
    plt.savefig('results/slide_10_mode_shapes.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_novel_studies_slide():
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('white')

    axes[0].set_title("Ill-Conditioning Study", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/ill_conditioning_study.png')
        axes[0].imshow(img)
        axes[0].axis('off')
    except:
        axes[0].text(0.5, 0.5, "See ill_conditioning_study.png",
                     ha='center', va='center', transform=axes[0].transAxes)

    axes[1].set_title("Damage Detection Study", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/damage_detection.png')
        axes[1].imshow(img)
        axes[1].axis('off')
    except:
        axes[1].text(0.5, 0.5, "See damage_detection.png",
                     ha='center', va='center', transform=axes[1].transAxes)

    plt.tight_layout()
    plt.savefig('results/slide_11_novel_studies.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_2d_truss_slide():
    fig, axes = plt.subplots(1, 3, figsize=(16, 9))
    fig.patch.set_facecolor('white')

    axes[0].set_title("2D Warren Truss Geometry", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss2d_geometry.png')
        axes[0].imshow(img)
        axes[0].axis('off')
    except:
        axes[0].axis('off')

    axes[1].set_title("2D Mode Shapes", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss2d_mode_shapes.png')
        axes[1].imshow(img)
        axes[1].axis('off')
    except:
        axes[1].axis('off')

    axes[2].set_title("2D Frequency Comparison", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss2d_frequency_comparison.png')
        axes[2].imshow(img)
        axes[2].axis('off')
    except:
        axes[2].axis('off')

    plt.tight_layout()
    plt.savefig('results/slide_12_2d_truss.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_convergence_slide():
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('white')

    axes[0].set_title("VQE Convergence (Beam)", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/convergence.png')
        axes[0].imshow(img)
        axes[0].axis('off')
    except:
        axes[0].axis('off')

    axes[1].set_title("Optimizer Comparison", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/optimizer_comparison.png')
        axes[1].imshow(img)
        axes[1].axis('off')
    except:
        axes[1].axis('off')

    plt.tight_layout()
    plt.savefig('results/slide_08_convergence.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_truss_results_slide():
    fig, axes = plt.subplots(1, 3, figsize=(16, 9))
    fig.patch.set_facecolor('white')

    axes[0].set_title("1D Truss Geometry", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss_geometry.png')
        axes[0].imshow(img)
        axes[0].axis('off')
    except:
        axes[0].axis('off')

    axes[1].set_title("Truss Mode Shapes", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss_mode_shapes.png')
        axes[1].imshow(img)
        axes[1].axis('off')
    except:
        axes[1].axis('off')

    axes[2].set_title("Truss Frequency Comparison", fontsize=14,
                      fontweight='bold', color=NAVY)
    try:
        img = plt.imread('results/truss_frequency_comparison.png')
        axes[2].imshow(img)
        axes[2].axis('off')
    except:
        axes[2].axis('off')

    plt.tight_layout()
    plt.savefig('results/slide_06b_truss_results.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_conclusion_slide():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    ax.text(0.5, 0.85, "Conclusions", fontsize=36,
            fontweight='bold', color='white', ha='center',
            transform=ax.transAxes)

    conclusions = [
        "✅ VQE achieves <0.03% error for beam modal analysis",
        "✅ Quantum pipeline validated for both beam and truss",
        "✅ All 3 modes found via deflation (truss)",
        "✅ Novel studies: ill-conditioning & damage detection",
        "✅ First demonstration of VQE for structural modal analysis",
        "✅ Open-source framework for quantum structural analysis",
    ]

    y_start = 0.72
    for i, text in enumerate(conclusions):
        y = y_start - i * 0.08
        ax.text(0.08, y, text, fontsize=16, color=CYAN,
                transform=ax.transAxes, va='center')

    ax.text(0.5, 0.10, "Thank You!", fontsize=32,
            fontweight='bold', color='white', ha='center',
            transform=ax.transAxes)

    ax.text(0.5, 0.05, "Questions?", fontsize=18,
            color=ORANGE, ha='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig('results/slide_18_conclusion.png', dpi=150,
                bbox_inches='tight', facecolor=NAVY)
    plt.close()


if __name__ == "__main__":
    print("Generating presentation slides...")
    create_title_slide()
    print("  [OK] slide_00_title.png")
    create_problem_slide()
    print("  [OK] slide_01_problem.png")
    create_quantum_insight_slide()
    print("  [OK] slide_02_quantum_insight.png")
    create_results_summary()
    print("  [OK] slide_03_results_summary.png")
    create_pipeline_slide()
    print("  [OK] slide_04_pipeline.png")
    create_convergence_slide()
    print("  [OK] slide_08_convergence.png")
    create_truss_results_slide()
    print("  [OK] slide_06b_truss_results.png")
    create_mode_shape_slide()
    print("  [OK] slide_10_mode_shapes.png")
    create_novel_studies_slide()
    print("  [OK] slide_11_novel_studies.png")
    create_2d_truss_slide()
    print("  [OK] slide_12_2d_truss.png")
    create_conclusion_slide()
    print("  [OK] slide_18_conclusion.png")
    print("\n[SUCCESS] All presentation slides generated in results/")