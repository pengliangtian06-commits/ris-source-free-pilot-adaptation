# Claim–evidence map R033

| Claim ID | Main-text location | Evidence | Boundary and wording gate |
|---|---|---|---|
| C1 | Abstract; Results canonical sweep; Discussion anchor | `figures/fig2_shift_sweep.pdf`, `paper-tables/table_r014_shift_sweep.tex`, canonical three-seed JSON | Say “recovers part of” across the tested shifts; canonical result is prequential batch-level adaptation. |
| C2 | Results held-out protocol; Discussion | Fig. 1, `table_r017_capacity.tex`, `table_r017_paired.tex`, held-out JSON | Say the direction survives the support/evaluation protocol; do not generalize beyond the simulator and three held-out shifts. |
| C3 | Results canonical and robustness sections | LS columns in Table R014, Fig. 2 and Fig. 5 | Communication gains are conditional; LS remains a competitive reference. |
| C4 | Results capacity/cost; Discussion | `table_r017_capacity.tex`, `fig4_capacity_cost.pdf`, `table_r024_cost.tex` | Parameter count is portable within the implementation; CPU timing is hardware-specific. |
| C5 | Results physical control; Discussion | `table_r021_physics_control.tex`, preregistered paired JSON | The delay-tail term fails this preregistered independent-contribution gate; do not infer that every physical penalty fails. |
| C6 | Results classical baseline | `fig3_classical_sensitivity.pdf`, `table_r032_omp.tex`, OMP JSON | Fixed dictionary and sparsity define the tested OMP reference; this is not an exhaustive model-based comparison. |
| C7 | Methods and Data/Code statement | R033 README, generator test, exporters, v1.0.2 manifest and final figures; GitHub tag and Zenodo version DOI | Reproducibility is publicly auditable at the tagged release; version DOI `10.5281/zenodo.23119393` and concept DOI `10.5281/zenodo.23118757` are recorded. |

Every claim has a visible evidence pointer and an explicit scope boundary. The
R033 package excludes private host details, credentials and stale CUDA artifacts.
