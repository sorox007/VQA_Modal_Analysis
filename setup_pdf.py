import os, shutil

src = r"C:\Users\somro\Documents\coep_DA\sem_VI_QC\project\VQA_Modal_Analysis"
dst = os.path.join(src, "flat")
os.makedirs(dst, exist_ok=True)

files = [
    "main.py", "fea.py", "truss.py", "quantum_setup.py", "ansatz.py",
    "vqe_runner.py", "visualize.py", "visualize_truss2d.py",
    "novel_study.py", "optimizer_comparison.py", "validate_fea.py",
    "validate_truss.py", "test_convergence.py", "test_n_elem.py",
    "generate_presentation.py"
]

for f in files:
    shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    print(f"Copied {f}")

print("Done copying files.")