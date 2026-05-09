# Setup & Installation

## Quick Start

### Option 1: Using Conda (Recommended)

Conda is recommended for this project because it handles optimized scientific libraries (like NumPy and SciPy with MKL support) which are important for matrix operations in FEA and quantum simulation.

```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate vqa-modal-analysis

# Verify installation
python -c "import qiskit; print('Qiskit version:', qiskit.__version__)"

# Run the full pipeline
python main.py
```

### Option 2: Using pip (Alternative)

If you prefer pip or already have Python 3.9+ installed:

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import qiskit; print('Qiskit version:', qiskit.__version__)"

# Run the full pipeline
python main.py
```

---

## Project Structure

```
VQA_Modal_Analysis/
├── main.py                    # Full pipeline runner
├── fea.py                     # Beam FEA (existing)
├── truss.py                   # Truss FEA (NEW)
├── quantum_setup.py           # K,M → quantum Hamiltonian
├── vqe_runner.py              # VQE solver
├── ansatz.py                  # Quantum circuits
├── novel_study.py             # Research studies
├── visualize.py               # All plotting
├── validate_fea.py           # Beam validation
├── validate_truss.py          # Truss validation (NEW)
├── requirements.txt           # pip dependencies
├── environment.yml            # conda environment
├── .gitignore                 # Git exclusions
└── results/                   # Generated plots & data
```

---

## What Gets Installed

### Core Dependencies
- **numpy** - Array operations, linear algebra
- **scipy** - Scientific computing (eigenvalue solvers, matrix operations)
- **matplotlib** - Visualization
- **pandas** - Data analysis

### Quantum Computing
- **qiskit** (v1.0.0) - Core quantum framework
- **qiskit-aer** (v0.13.0) - Quantum simulator
- **qiskit-algorithms** (v0.3.0) - VQE, optimizers

### Optional (for development)
- **jupyter** - Interactive notebooks
- **qiskit-ibm-runtime** - Run on real IBM quantum hardware

---

## Verification

After installation, run:

```python
# Test imports
import numpy as np
import scipy as sp
import matplotlib
import qiskit
import pandas as pd

print("All imports successful!")
print(f"NumPy version: {np.__version__}")
print(f"Qiskit version: {qiskit.__version__}")

# Quick VQE test
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import SparsePauliOp

# Create a simple Hamiltonian
hamiltonian = SparsePauliOp.from_list([("II", 1), ("IZ", 0.5), ("ZI", -0.5), ("ZZ", 0.3)])

# Create ansatz
ansatz = TwoLocal(2, 'ry', 'cz', reps=1)

print("\nVQE test passed! Ready to run.")
```

---

## Running the Project

### Full Pipeline
```bash
python main.py
```

This runs:
1. Beam FEA baseline
2. Quantum Hamiltonian construction
3. VQE optimization (COBYLA and L-BFGS-B)
4. Higher modes via deflation
5. Truss analysis (NEW)
6. Novel studies (ill-conditioning, damage detection)
7. All visualizations

**Output:** Results saved to `results/` directory

### Individual Components

**Run only beam FEA validation:**
```bash
python validate_fea.py
```

**Run only truss FEA validation:**
```bash
python validate_truss.py
```

**Run only beam VQE:**
```python
from fea import assemble_beam, apply_simply_supported_bc, classical_modal_analysis
from quantum_setup import build_structural_hamiltonian
from vqe_runner import VQEStructuralSolver
from ansatz import hardware_efficient_ansatz

# Your parameters here
K, M = assemble_beam(2, 200e9, 8.33e-6, 7850, 0.01, 1.0)
K_red, M_red, _ = apply_simply_supported_bc(K, M, 2)
```

**Run only truss VQE:**
```python
from truss import assemble_truss, apply_fixed_fixed_bc, classical_modal_analysis

K, M = assemble_truss(4, 200e9, 0.01, 7850, 1.0)
K_red, M_red, _ = apply_fixed_fixed_bc(K, M)
```

**Run novel studies:**
```bash
python -c "from novel_study import tapered_beam_study; import matplotlib.pyplot as plt; df = tapered_beam_study(200e9, 8.33e-6, 7850, 0.01, 1.0, [1.0, 0.8, 0.6]); print(df)"
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'qiskit'`

**Solution:**
```bash
# If using conda
conda activate vqa-modal-analysis
pip install -r requirements.txt

# If using pip
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: `Qiskit version mismatch`

**Solution:** The project is tested with specific versions:
```bash
pip install qiskit==1.0.0 qiskit-aer==0.13.0 qiskit-algorithms==0.3.0
```

### Issue: `numpy.linalg.LinAlgError`

**Cause:** Matrices not positive definite (usually BC issue)

**Solution:** Check boundary conditions are applied correctly:
```python
from validate_fea import *  # or validate_truss
```

### Issue: VQE not converging

**Try:**
```python
# Increase iterations
solver = VQEStructuralSolver(hamiltonian, ansatz, 
                              optimizer_name='COBYLA',
                              maxiter=2000,  # was 500
                              H_scale=H_scale)

# Or try different optimizer
solver = VQEStructuralSolver(hamiltonian, ansatz,
                              optimizer_name='L_BFGS_B',  # or 'SPSA'
                              maxiter=2000,
                              H_scale=H_scale)
```

### Issue: Out of memory

**Cause:** Qiskit Aer statevector simulator uses ~16 GB for large systems

**Solution:**
```python
# Reduce problem size
n_elem = 2  # Instead of 4 or more

# Or use shot-based simulation (if running on hardware)
# from qiskit.primitives import Sampler
```

---

## Updating Dependencies

### To update Qiskit:
```bash
pip install --upgrade qiskit qiskit-aer qiskit-algorithms
```

### To regenerate environment.yml:
```bash
conda env export > environment.yml
```

### To generate requirements.txt:
```bash
pip freeze > requirements.txt
```

*Note: Be careful with `pip freeze` - it pins ALL packages including transitive dependencies*

---

## Development Setup

For contributing to the project:

```bash
# Install development tools
pip install pytest pytest-cov black flake8

# Run tests (if any)
pytest

# Format code
black *.py

# Lint code
flake8 *.py
```

---

## System Requirements

### Minimum
- Python 3.9+
- 8 GB RAM (16 GB recommended)
- 10 GB disk space

### Recommended
- Python 3.9-3.11
- 16 GB RAM (for larger FEA problems)
- Multi-core CPU (Qiskit can parallelize)

### Optional
- NVIDIA GPU (for Qiskit Aer GPU acceleration)
- IBM Quantum account (for real hardware runs)

---

## Getting Help

- **Qiskit Documentation:** https://docs.quantum.ibm.com/
- **Project README.md:** Detailed usage guide
- **VQA_Modal_Analysis.md:** Technical deep-dive

---

## License

This project is for educational and research purposes.

---

## Quick Reference

| Task | Command |
|---|---|
| Create env | `conda env create -f environment.yml` |
| Activate | `conda activate vqa-modal-analysis` |
| Install deps | `pip install -r requirements.txt` |
| Run full | `python main.py` |
| Test imports | `python -c "import qiskit"` |
| Validate beam | `python validate_fea.py` |
| Validate truss | `python validate_truss.py` |
| Clean results | `rm results/*.png results/*.csv` |
