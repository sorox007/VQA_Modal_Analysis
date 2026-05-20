"""
TCPL Water Bottle Production Line — Process Flow Diagram
Minor Stoppage & Downtime Analysis
Run with: python process_flow_diagram.py
Requires: matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(24, 18))
ax.set_xlim(0, 24)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# ─── Helper functions ──────────────────────────────────────────────

def box(ax, x, y, w, h, text, facecolor, edgecolor='white',
        fontsize=9, textcolor='white', bold=True, alpha=0.93):
    """Draw a rounded rectangle with centered text."""
    rect = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle='round,pad=0.12',
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=1.6, alpha=alpha, zorder=3
    )
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center',
            color=textcolor, fontsize=fontsize,
            fontweight='bold' if bold else 'normal',
            multialignment='center', zorder=4,
            fontfamily='monospace', linespacing=1.4)

def arr(x1, y1, x2, y2, color='#2d6a4f', lw=2.2):
    """Draw a vertical/horizontal arrow."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color,
                               lw=lw, connectionstyle='arc3,rad=0.0'),
                zorder=5)

def label(x, y, text, color='#e9c46a', fontsize=7.5):
    """Small side label."""
    ax.text(x, y, text, ha='center', va='center',
            color=color, fontsize=fontsize, fontweight='bold',
            multialignment='center', fontfamily='monospace', linespacing=1.3)

# ─── Title ─────────────────────────────────────────────────────────

ax.text(12, 17.4, 'TCPL WATER BOTTLE PRODUCTION LINE',
        ha='center', color='#e9c46a', fontsize=16, fontweight='bold', fontfamily='monospace')
ax.text(12, 16.9, 'Process Flow Diagram — Minor Stoppage & Downtime Analysis',
        ha='center', color='#888', fontsize=11, fontfamily='monospace')

# ─── STAGE 0: Storage ──────────────────────────────────────────────

label(0.6, 15.8, 'STG 0\nSTORE', fontsize=7)
box(ax, 8, 15.8, 10, 1.1,
    'STORE ROOM  —  Pellets (PET) + Machine Spares',
    facecolor='#e94560', fontsize=10)

# ─── STAGE 1: Moulding ─────────────────────────────────────────────

arr(8, 15.25, 8, 14.6)
ax.text(8.7, 14.9, 'Pellets fed', color='#aaa', fontsize=7.5)

label(0.6, 13.8, 'STG 1\nMOULD\n(Smart)', fontsize=7)

# Three moulding machines
box(ax, 4,  13.8, 5.2, 1.5, 'MOULDING M/C A\n1L Bottles\n(2 at a time)',
    facecolor='#0f3460', edgecolor='#1a5276', fontsize=8.5)
box(ax, 12, 13.8, 5.2, 1.5, 'MOULDING M/C B\n1L Bottles\n(4 at a time)',
    facecolor='#0f3460', edgecolor='#1a5276', fontsize=8.5)
box(ax, 20, 13.8, 5.2, 1.5, 'MOULDING M/C C\n250ml Bottles\n(4 at a time)',
    facecolor='#0f3460', edgecolor='#1a5276', fontsize=8.5)

# Arrows from storage to each moulding machine
arr(5.5, 15.25, 4,  14.55, lw=1.5)
arr(8,   15.25, 12, 14.55, lw=1.5)
arr(10.5,15.25, 20, 14.55, lw=1.5)

# ─── Conveyor merge ────────────────────────────────────────────────

arr(4,  13.05, 4,  12.5, lw=1.5)
arr(12, 13.05, 12, 12.5, lw=1.5)
arr(20, 13.05, 20, 12.5, lw=1.5)

# Merge arrows → conveyor
for xm in [4, 12, 20]:
    ax.annotate('', xy=(12, 12.2), xytext=(xm, 12.2),
                arrowprops=dict(arrowstyle='->', color='#2d6a4f', lw=2.2,
                               connectionstyle='arc3,rad=0.0'))

ax.text(12, 11.85, '─── Conveyor Belt ───', ha='center', color='#2d6a4f',
        fontsize=8, style='italic')

arr(12, 11.6, 12, 11.1)

# ─── STAGE 2: Hilden Filler ────────────────────────────────────────

label(0.6, 10.3, 'STG 2\nFILL\n(Cam)\n⚠', fontsize=7)

box(ax, 12, 10.3, 11, 1.5,
    'HILDEN 24-24-8  —  RINSER → FILLER → CAPPER\nCam + Rollers  |  Capper has sensors\n'
    'HARDEST TO LOG DATA  —  Manual tracking needed',
    facecolor='#533483', edgecolor='#e94560', fontsize=9)

ax.text(19.5, 10.3, '⚠\nCam-based\n= No PLC\nlogs', ha='center', va='center',
        color='#e94560', fontsize=7.5, fontweight='bold', linespacing=1.3)

# ─── STAGE 3: Laser Engraver ───────────────────────────────────────

arr(12, 9.55, 12, 9.0)

label(0.6, 8.3, 'STG 3\nENGRAV\n(Smart)', fontsize=7)

box(ax, 9.5, 8.3, 6, 1.3,
    'LASER ENGRAVER\nCamera detection + Auto reject\n⚠ Not 100% accurate yet',
    facecolor='#0f3460', edgecolor='#e9c46a', fontsize=8.5)

arr(12.5, 8.3, 14.2, 8.3, color='#e9c46a', lw=1.5)

box(ax, 16, 8.3, 4, 1.3,
    'MANUAL CHECK #1\nBacklit inspection\nby operator',
    facecolor='#16213e', edgecolor='#e9c46a', fontsize=8)

# ─── STAGE 4: Sleeve Wrapper ───────────────────────────────────────

arr(9.5, 7.65, 9.5, 7.1)

label(0.6, 6.4, 'STG 4\nSLEEVE\n(Smart)', fontsize=7)

box(ax, 9.5, 6.4, 6, 1.3,
    'SLEEVE WRAPPER\nSleeve applied without\nproper compression  ⚠',
    facecolor='#0f3460', edgecolor='#e9c46a', fontsize=8.5)

arr(12.5, 6.4, 14.2, 6.4, color='#e9c46a', lw=1.5)

box(ax, 16, 6.4, 4, 1.3,
    'MANUAL CHECK #2\nSleeve quality\ncheck',
    facecolor='#16213e', edgecolor='#e9c46a', fontsize=8)

# ─── STAGE 5: Steam ────────────────────────────────────────────────

arr(9.5, 5.75, 9.5, 5.2)

label(0.6, 4.55, 'STG 5\nSTEAM\n(Smart)', fontsize=7)

box(ax, 9.5, 4.55, 6, 1.2,
    'STEAM MACHINE\nCompresses & wraps sleeve properly',
    facecolor='#0f3460', edgecolor='#1a5276', fontsize=8.5)

# ─── STAGE 6: Final Packaging ──────────────────────────────────────

arr(9.5, 3.95, 3, 3.35, lw=2)

label(0.6, 2.7, 'STG 6\nPACK\n(Mixed)', fontsize=7)

boxes = [
    (3,   2.7, 3.2, 1.2, 'FINAL\nCHECK #3\nBottle quality',  '#16213e', '#e9c46a'),
    (7.5, 2.7, 3.2, 1.2, 'CASE PACKER\n12 bottles\nper carton',  '#0f3460', '#1a5276'),
    (12,  2.7, 3.2, 1.2, 'BOXING /\nTAPING M/C\nSeal cartons',  '#0f3460', '#1a5276'),
    (16.5,2.7, 3.2, 1.2, 'WEIGHING\nVerify all\nbottles present','#264653', '#e9c46a'),
    (21,  2.7, 3.2, 1.2, 'FINAL\nPACKING\nBy workers',        '#2d6a4f', '#2d6a4f'),
]

for (bx, by, bw, bh, bt, bc, be) in boxes:
    box(ax, bx, by, bw, bh, bt, facecolor=bc, edgecolor=be, fontsize=8)

# Arrows between packaging boxes
for i in range(len(boxes)-1):
    x1 = boxes[i][0]   + boxes[i][2]/2 + 0.15
    x2 = boxes[i+1][0] - boxes[i+1][2]/2 - 0.15
    arr(x1, 2.7, x2, 2.7, lw=2)

# ─── Legend ────────────────────────────────────────────────────────

legend_items = [
    ('#e94560', 'white', 'Storage'),
    ('#0f3460', '#1a5276', 'Smart Machine'),
    ('#533483', '#e94560', 'Cam-Based'),
    ('#16213e', '#e9c46a', 'Manual Check'),
    ('#264653', '#e9c46a', 'Quality/Weigh'),
    ('#2d6a4f', 'white', 'Final Packing'),
]

ax.text(1, 1.3, 'LEGEND', color='white', fontsize=8, fontweight='bold', fontfamily='monospace')

for i, (fc, ec, name) in enumerate(legend_items):
    lx = 2.5 + i * 3.6
    patch = FancyBboxPatch((lx-0.5, 0.85), 1.0, 0.5,
                            boxstyle='round,pad=0.06',
                            facecolor=fc, edgecolor=ec, linewidth=1.2)
    ax.add_patch(patch)
    ax.text(lx+0.7, 1.1, name, color='#ccc', fontsize=7.5, va='center', fontfamily='monospace')

# ─── Key callout ───────────────────────────────────────────────────

ax.text(12, 0.45,
        '⏱  Priority stoppage logging: Hilden Filler → Laser Engraver → Sleeve Wrapper → Case Packer',
        ha='center', color='#e94560', fontsize=9, fontweight='bold', fontfamily='monospace')

# ─── Save ──────────────────────────────────────────────────────────

out = r'C:\Users\somro\Documents\Internship_TCPL_2026\01_Project_Overview\process_flow_diagram.png'
plt.tight_layout(pad=0.5)
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
print(f'Diagram saved to: {out}')
