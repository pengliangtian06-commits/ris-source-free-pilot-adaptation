# R032 reproducibility release

This release contains the working manuscript, machine-readable experiment
artifacts, table exporters, figure source and validation scripts for the
source-free pilot-adaptation benchmark. Digital Communications and Networks
(DCN) is the provisional target venue. The public repository is
<https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>,
the current tag is `v1.0.2`, and the release family has the Zenodo concept DOI
<https://doi.org/10.5281/zenodo.23118757>. The archived `v1.0.1` record is
<https://doi.org/10.5281/zenodo.23118758>.

## Environment used for the current CPU artifacts

- Windows 11 x86-64, Python 3.14.7
- PyTorch 2.14.1+cpu, Lightning 2.6.6
- NumPy 2.5.2, SciPy 1.18.1, Matplotlib 3.11.1
- CUDA was unavailable for this local rerun. Device fields in the regenerated
  canonical, capacity, cost and smoke artifacts therefore read `cpu`.

## Simulator boundary and parameters

The generator is an explicit but normalized BS--RIS--UE cascade. It uses 16
subcarriers, four BS transmit antennas, three BS-side paths and two UE-side
paths. Robustness varies the RIS element count over 8, 16 and 32. The
subcarrier coordinate is `[-0.5, 0.5)` and is not mapped to a physical carrier
frequency, bandwidth or subcarrier spacing. BS and UE path delays are sampled
from `[0, 0.25]` and `[0, 0.20]` and multiplied by the delay-scale factor.
Complex gains are normalized by path count. Array responses use normalized
element indices and a frequency-dependent spacing factor when beam squint is
enabled. Reflection phases are sampled per realization and held fixed during
the pilot observation. There is no calibrated path-loss, mutual-coupling or
physical-aperture model, so the RIS count is an element-count factor.

The implemented cascade is `h_UE.T @ diag(reflection) @ h_BS`, where the
transpose is without complex conjugation. The consistency gate is
`experiments/ris_cascaded_generator_consistency_test.py`.

## Rebuild commands

From the project root:

```text
python experiments/ris_cascaded_generator_consistency_test.py
python experiments/cloud_ris_adapter_lightning.py --mode smoke --device cpu --seed 20261002
python experiments/cloud_ris_shift_sweep_cpu.py --mode full --device cpu --seed 20261002
python experiments/cloud_ris_shift_sweep_cpu.py --mode full --device cpu --seed 20261003
python experiments/cloud_ris_shift_sweep_cpu.py --mode full --device cpu --seed 20261004
python experiments/aggregate_shift_sweep.py
python experiments/cloud_ris_heldout_geometry_cpu.py --mode full --device cpu --seed 20261002
python experiments/cloud_ris_full_model_heldout_cpu.py --device cpu --seed 20261002
python experiments/cloud_ris_physics_preregistered_cpu.py --device cpu
python experiments/cloud_ris_robustness_adapter_cpu.py --device cpu --seed 20261002
python experiments/benchmark_adaptation_cost.py --device cpu --seed 20261002 --repeats 3
python experiments/export_latex_tables.py
python experiments/plot_paper_figures.py
```

The three-seed robustness and preregistered summary files in this package are
the locked artifacts used by the manuscript. Re-running those suites requires
the three fixed seeds `20261002`, `20261003` and `20261004`; their scripts
write per-seed JSON files before a summary is assembled.

## Evidence and interpretation boundaries

The canonical shift sweep is prequential batch-level adaptation. Each 512
sample target block is processed as four ordered batches of 128, with ten
pilot-only optimizer steps per batch and adapter state carried forward. The
strict held-out protocol fits on a 512-sample unlabeled support block and
scores a disjoint 512-sample evaluation block. Channel-level bootstrap and
Wilcoxon summaries are block-conditional; the independent repeated unit is the
training/data seed. The negative delay-tail control is retained as a negative
control and does not establish a physical mechanism.

The current Data and Code Availability statement can cite the repository URL,
tag, concept DOI and the dual-license files. Before submission, complete the
corresponding-author designation, final contact choice, funding statement and
institution-specific venue classification. Do not add private credentials,
phone numbers or host details to the release.
