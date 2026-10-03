# Source-Free Pilot Adaptation for RIS-Assisted Wideband MIMO

Reproducibility release for the manuscript **Source-Free Pilot Adaptation for RIS-Assisted Wideband MIMO Channel Estimation under Explicit Distribution Shifts**.

This repository contains the source manuscript, synthetic BS--RIS--UE generator, CPU-regenerated result artifacts, table and figure exporters, verification records, and the bounded DOI search record used to prepare the manuscript for a potential submission to *Digital Communications and Networks*. The venue remains provisional; no journal quartile is asserted here.

## Scope and evidence boundary

- The study uses controlled synthetic wideband channels, not measured or ray-traced channels.
- Paper-grade result JSON files in this release record `device=cpu`.
- Target CSI labels are used for scoring and held-out evaluation, not by the pilot-only adaptation optimizer.
- The preregistered physical-term control is retained as a negative result because it did not pass the independent-contribution gate.
- The release is a reproducibility package and does not claim universal estimator superiority.

## Contents

- `paper-draft-r025.tex`: manuscript source.
- `supplementary_tables_r032.tex`: supplementary table source.
- `experiments/`: generators, baselines, CPU experiment runners, aggregators and exporters.
- `paper-tables/`: generated LaTeX tables.
- `figures/`: final figure sources, exports and layout/collision audit records.
- `refine-logs/FINAL_NOVELTY_PASS_20261002.json`: DOI resolution record for the bounded neighboring-work search.
- `REPRODUCTION_README_R032.md`: environment and rerun details.
- `submission_package_manifest_r032.json`: SHA-256 manifest for the release selection.

## Reproduction

Use Python 3.11 or a compatible environment described in `requirements-cloud.txt`. The paper-grade artifacts are already included. To regenerate the CPU summaries and LaTeX tables, run:

```powershell
python experiments/aggregate_cpu_artifacts.py
python experiments/export_latex_tables.py
```

Figure regeneration additionally requires the Nature figure alignment auditor. Set `NATURE_FIGURE_SCRIPTS` to the directory containing `audit_panel_alignment.py`, then run:

```powershell
python experiments/plot_paper_figures.py
```

The local manuscript build uses `latexmk -pdf paper-draft-r025.tex`. The release does not include temporary LaTeX build products.

## Licensing

- Source code is released under the MIT License in `LICENSE`.
- Manuscript text, figures, tables and generated result artifacts are released under the Creative Commons Attribution 4.0 International license in `LICENSE-CC-BY-4.0.txt`.
- Third-party packages and external records retain their own licenses and terms.

## Citation and archival status

The public repository URL, release tag and DOI are assigned at publication time through the repository host and its DOI archive integration. Until those fields are filled in, this README intentionally does not invent a DOI or author identity.
