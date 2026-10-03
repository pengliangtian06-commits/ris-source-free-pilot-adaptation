# Source-free pilot adaptation for RIS-assisted wideband MIMO

Reproducibility release for the manuscript **Source-free pilot adaptation for
RIS-assisted wideband MIMO channel estimation under explicit distribution
shifts**.

The v1.0.3 release contains the source manuscript, synthetic BS--RIS--UE
generator, CPU result artifacts, table and figure exporters, verification
records, submission materials and CPU-loadable source/adapter model weights.

## Scope and evidence boundary

- The study uses controlled synthetic wideband channels, not measured or ray-traced channels.
- Paper-grade result JSON files record the local CPU environment.
- Target CSI labels are used for scoring and held-out evaluation, not by the pilot-only adaptation optimizer.
- The preregistered physical-term control is retained as a negative result because it did not pass the independent-contribution gate.
- The release does not claim universal estimator superiority.

## Contents

- `submission_package_v1.0.3.zip`: credential-scanned reproducibility and submission bundle.
- `submission_package_manifest_v1.0.3.json`: SHA-256 manifest for the release selection.
- `weights/v1.0.3/`: three source-estimator state dictionaries and twelve canonical-adapter state dictionaries.
- `experiments/export_model_weights.py`: deterministic weight export from the locked training/adaptation implementation.
- `experiments/verify_model_weights.py`: CPU reload, hash, parameter-count and finite-forward verifier.
- `REPRODUCTION_README_v1.0.3.md`: environment, rerun and weight-reload instructions.
- `PUBLIC_RELEASE_NOTES_v1.0.3.md`: release-level change record.
- `CITATION.cff`: machine-readable citation metadata.

## Reproduction

Use Python 3.11 or a compatible environment described in `requirements-cloud.txt`.
The paper-grade artifacts are already included. To regenerate CPU summaries and
LaTeX tables, run:

```powershell
python experiments/aggregate_cpu_artifacts.py
python experiments/export_latex_tables.py
```

To verify the published model weights:

```powershell
python experiments/verify_model_weights.py --weights-dir weights/v1.0.3 --device cpu
```

The verifier loads every file with `weights_only=True`; no executable objects,
target CSI labels or private host details are stored in the weights.

## Licensing

- Source code is released under the MIT License in `LICENSE`.
- Manuscript text, figures, tables, generated result artifacts and model weights are released under CC BY 4.0 in `LICENSE-CC-BY-4.0.txt`.
- Third-party packages and external records retain their own licenses and terms.

## Citation and archival status

The public repository is
<https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>.
The current release tag is `v1.0.3`. Its version DOI is
<https://doi.org/10.5281/zenodo.23121462>. The release-family concept DOI is
<https://doi.org/10.5281/zenodo.23118757>. Cite the version DOI when referring
to this exact release and the concept DOI when referring to the release family.

The corresponding author for the manuscript is Changjiang Zhang
(`zhangchangjiang@ccbupt.cn`).
