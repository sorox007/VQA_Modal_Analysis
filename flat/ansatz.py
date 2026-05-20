from qiskit.circuit.library import EfficientSU2, RealAmplitudes
from qiskit.circuit import QuantumCircuit, ParameterVector
import numpy as np

def hardware_efficient_ansatz(num_qubits, reps=2):
    """Standard Hardware-Efficient Ansatz (HEA)."""
    ansatz = EfficientSU2(
        num_qubits=num_qubits,
        reps=reps,
        entanglement='linear'
    )
    ansatz = ansatz.decompose()
    print(f"HEA: {num_qubits} qubits, {reps} reps, {ansatz.num_parameters} parameters")
    return ansatz

def symmetric_ansatz(num_qubits, reps=2):
    """
    Symmetry-aware ansatz for simply-supported beam.
    Constrains parameters to enforce mirror symmetry of mode shapes.
    Fewer parameters → faster convergence (hypothesis to test).
    """
    n_params = 2 * reps + 2
    theta = ParameterVector('θ', n_params)
    qc = QuantumCircuit(num_qubits)
    
    param_idx = 0
    for rep in range(reps):
        # Symmetric rotation layer
        for q in range(num_qubits // 2):
            qc.ry(theta[param_idx], q)
            qc.ry(theta[param_idx], num_qubits - 1 - q)  # Mirror
        param_idx += 1
        
        # Entanglement layer
        for q in range(num_qubits - 1):
            qc.cx(q, q + 1)
    
    # Final rotation layer (asymmetric for higher modes)
    for q in range(num_qubits):
        qc.ry(theta[param_idx], q)
        param_idx += 1
    
    print(f"Symmetric ansatz: {num_qubits} qubits, {reps} reps, {qc.num_parameters} parameters")
    return qc

def minimal_ansatz(num_qubits):
    """Minimal 2-parameter ansatz for quick testing."""
    theta = ParameterVector('θ', 2 * num_qubits)
    qc = QuantumCircuit(num_qubits)
    for q in range(num_qubits):
        qc.ry(theta[q], q)
    qc.cx(0, 1)
    for q in range(num_qubits):
        qc.ry(theta[num_qubits + q], q)
    return qc