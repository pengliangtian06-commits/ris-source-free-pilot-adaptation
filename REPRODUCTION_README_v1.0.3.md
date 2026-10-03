# Reproduction README for v1.0.3

This release contains the source manuscript, synthetic wideband BS--RIS--UE
generator, CPU result artifacts, figures, tables, verification scripts and
CPU-loadable source/adapter weights.

## Environment

The paper-grade artifacts were regenerated in a local CPU environment. Use
Python 3.11 or a compatible environment described in `requirements-cloud.txt`.
The package does not require a GPU to reload the published weights.

## Rebuild the paper-grade artifacts

From the project root:

```text
python experiments/ris_cascaded_generator_consistency_test.py
python experiments/aggregate_cpu_artifacts.py
python experiments/export_latex_tables.py
python experiments/plot_paper_figures.py
```

The fixed paper seeds are `20261002`, `20261003` and `20261004`. Re-running the
full experiment suites is optional because the paper-grade JSON summaries are
included in the release.

## Reload the model weights

```text
python experiments/verify_model_weights.py --weights-dir weights/v1.0.3 --device cpu
```

The verifier checks SHA-256 entries, loads each file with
`torch.load(..., weights_only=True)`, reconstructs the declared architecture,
checks parameter counts and performs a finite-output forward pass. The source
estimator has 115,328 parameters. Each lightweight adapter has 16,576
parameters.

The adapters represent the final state after four ordered 128-sample canonical
batches and ten pilot-only updates per batch. Target labels are scoring-only and
are not passed to the adaptation optimizer.

## Scope and license

The generator uses normalized synthetic channels with explicit RIS reflection,
beam squint, angular displacement and delay scaling. It has no measured-channel
or calibrated hardware claim. Code is MIT licensed. Manuscript text, figures,
tables, generated artifacts and model weights are CC BY 4.0.

Repository: <https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>

Release tag: `v1.0.3`  
Zenodo version DOI: `10.5281/zenodo.23121462`  
Concept DOI: <https://doi.org/10.5281/zenodo.23118757>
