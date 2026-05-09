# ============================================================
# TRUSS VISUALIZATIONS
# ============================================================

plot_truss_geometry(n_elem_truss, L)

# Classical truss mode shapes
modes_t_list = [modes_t[:, i] for i in range(min(3, modes_t.shape[1]))]
plot_truss_mode_shapes(
    n_elem_truss, L,
    modes=modes_t_list,
    labels=['Classical'],
    analytical_omega=omega_t_classical[:3]
)

# VQE truss mode shapes
mode_shapes_vqe_t = [r['mode_shape'] for r in multi_t]
plot_truss_mode_shapes(
    n_elem_truss, L,
    modes=mode_shapes_vqe_t,
    labels=['VQE'],
    analytical_omega=omega_t_classical[:3]
)

# Truss frequency comparison
plot_truss_frequency_comparison(
    [omega_t_all],
    omega_t_classical[:3],
    labels=['VQE (HEA, 3 reps)']
)
EOF'
tail -5 main.py >> main_new.py && mv main_new.py main.py
