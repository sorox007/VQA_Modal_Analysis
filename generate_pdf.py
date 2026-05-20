#!/usr/bin/env python3
"""Generate a complete LaTeX document with all source code embedded."""

import os

SRC = r"C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis"
OUT = os.path.join(SRC, "flat", "CODE_COMPLETE.tex")

PYTHON_FILES = [
    ("main.py", "Pipeline Orchestrator"),
    ("fea.py", "Beam Finite Element Analysis"),
    ("truss.py", "1D and 2D Truss Analysis"),
    ("quantum_setup.py", "Hamiltonian Construction"),
    ("ansatz.py", "Quantum Circuit Ansatze"),
    ("vqe_runner.py", "VQE Solver"),
    ("visualize.py", "Beam and Truss Visualizations"),
    ("visualize_truss2d.py", "2D Warren Truss Visualizations"),
    ("novel_study.py", "Ill-Conditioning and Damage Detection"),
    ("optimizer_comparison.py", "COBYLA vs L-BFGS-B"),
    ("validate_fea.py", "Beam FEA Validation"),
    ("validate_truss.py", "Truss FEA Validation"),
    ("test_convergence.py", "Mesh Convergence Study"),
    ("test_n_elem.py", "Qubit Count Analysis"),
    ("generate_presentation.py", "Slide Generator"),
]

def escape_latex(s):
    # Escape special LaTeX characters (outside lstlisting)
    s = s.replace("\\", "\\textbackslash{}")
    s = s.replace("_", "\\_")
    s = s.replace("#", "\\#")
    s = s.replace("$", "\\$")
    s = s.replace("%", "\\%")
    s = s.replace("&", "\\&")
    s = s.replace("~", "\\textasciitilde{}")
    s = s.replace("^", "\\textasciicircum{}")
    s = s.replace("{", "\\{")
    s = s.replace("}", "\\}")
    s = s.replace("|", "\\textbar{}")
    s = s.replace("<", "\\textless{}")
    s = s.replace(">", "\\textgreater{}")
    s = s.replace("\t", "    ")
    return s

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def build():
    lines = []

    # Preamble
    preamble = r"""\documentclass[12pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}
\usepackage{fancyvrb}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{float}
\usepackage[colorlinks=true,linkcolor=blue,filecolor=magenta,urlcolor=cyan]{hyperref}

\onehalfspacing

\lstdefinestyle{codestyle}{
    basicstyle=\ttfamily\footnotesize,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!9},
    keywordstyle=\color{blue!80!black},
    commentstyle=\color{green!50!black},
    stringstyle=\color{red!80!black},
    numbers=left,
    numberstyle=\tiny\color{gray},
    numbersep=5pt,
    showstringspaces=false,
    tabsize=2,
    captionpos=b,
    xleftmargin=0.5em,
    framexleftmargin=0.5em,
    literate={_}{{\_}}1,
}

\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{1em}{}

\title{\textbf{VQA Modal Analysis --- Complete Code Repository} \\
\large Quantum Computing for Structural Dynamics}
\author{Somro, COEP Technological University}
\date{May 2026}

\begin{document}

\maketitle
\tableofcontents
\newpage
"""
    lines.append(preamble)

    # Overview section
    lines.append(r"\section{Project Overview}")
    lines.append("")
    lines.append(r"This document contains the complete source code for the ")
    lines.append(r"\textbf{Variational Quantum Eigensolver (VQE) Modal Analysis} project. ")
    lines.append("The codebase implements a quantum-classical hybrid pipeline for computing")
    lines.append("natural frequencies and mode shapes of structural systems.")
    lines.append("")

    lines.append(r"\subsection{File Inventory}")
    lines.append("")
    lines.append(r"\begin{table}[H]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{ll}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{File} & \textbf{Description} \\")
    lines.append(r"\midrule")
    for fname, desc in PYTHON_FILES:
        fname_esc = fname.replace("_", r"\_")
        lines.append(r"\texttt{" + fname_esc + r"} & " + desc + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{Complete file inventory of the project}")
    lines.append(r"\end{table}")

    # Each file as a section with lstlisting
    for i, (fname, desc) in enumerate(PYTHON_FILES):
        fpath = os.path.join(SRC, fname)
        code = read_file(fpath)

        lines.append("")
        lines.append(f"% {'='*60}")
        lines.append("")
        lines.append(r"\section{" + fname + " --- " + desc + "}")
        lines.append("")
        lines.append(r"\begin{lstlisting}[style=codestyle, caption={"
                      + fname + " --- " + desc + r"}]")
        # Inside lstlisting, only escape double backslash for path issues
        # lstlisting handles most special chars, but need to handle double backslash
        lines.append(code)
        lines.append(r"\end{lstlisting}")

    # Formal Report section
    lines.append("")
    lines.append(r"\section{Project Report (Official LaTeX)}")
    lines.append("")
    report_path = os.path.join(SRC, "VQA_Modal_Analysis_Report.tex")
    report = read_file(report_path)
    lines.append(r"\begin{lstlisting}[style=codestyle, "
                  r"caption={VQA\_Modal\_Analysis\_Report.tex}]")
    lines.append(report)
    lines.append(r"\end{lstlisting}")

    # Conclusion
    lines.append("")
    lines.append(r"\section{Summary}")
    lines.append("")
    lines.append("This document contains every source file in the repository. "
                  "The pipeline covers:")
    lines.append("")
    lines.append(r"\begin{enumerate}")
    lines.append(r"\item \textbf{Beam FEA} --- Euler-Bernoulli elements, "
                  r"simply-supported BCs, analytical validation")
    lines.append(r"\item \textbf{1D Truss FEA} --- Axial bar elements, "
                  r"fixed-fixed BCs, analytical validation")
    lines.append(r"\item \textbf{2D Warren Truss FEA} --- Triangular mesh, "
                  r"pinned-roller BCs, proper geometry")
    lines.append(r"\item \textbf{Quantum Hamiltonian} --- "
                  r"$H = M^{-1/2} K M^{-1/2}$, Pauli decomposition, normalization")
    lines.append(r"\item \textbf{VQE Solver} --- Multi-start optimization, "
                  r"two-stage refinement, excited-state deflation")
    lines.append(r"\item \textbf{Visualization} --- Convergence curves, "
                  r"mode shapes, frequency comparisons, animations")
    lines.append(r"\item \textbf{Novel Studies} --- Ill-conditioning "
                  r"(tapered structures), damage detection (stiffness reduction)")
    lines.append(r"\item \textbf{Optimizer Comparison} --- "
                  r"COBYLA vs L-BFGS-B benchmarking")
    lines.append(r"\end{enumerate}")

    lines.append("")
    lines.append(r"\end{document}")

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print("Wrote %s (%d lines)" % (OUT, len(lines)))

if __name__ == "__main__":
    build()