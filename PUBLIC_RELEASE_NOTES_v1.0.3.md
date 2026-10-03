# Public release notes v1.0.3

## What changed

This release adds CPU-loadable model weights to the reproducibility package for
the source-free pilot-adaptation benchmark. It preserves the locked v1.0.2
result artifacts and adds:

- three source-estimator `state_dict` files for seeds `20261002`, `20261003`
  and `20261004`;
- twelve final canonical-adapter `state_dict` files for the four shifts
  `(0.04, 1.2)`, `(0.08, 1.4)`, `(0.12, 1.6)` and `(0.18, 2.0)`;
- JSON metadata with architecture, seed, shift, support protocol, update count,
  learning rate and label-isolation fields;
- a SHA-256 manifest and a clean-environment reload verifier.

The weights are plain PyTorch `state_dict` files and are loaded with
`weights_only=True`. They do not contain executable Python objects, target CSI
labels or private host information. Source code remains MIT licensed; model
weights, manuscript text, figures, tables and generated result artifacts are
released under CC BY 4.0.

## Verification

The v1.0.3 package passed the following checks before release:

```text
python experiments/verify_model_weights.py --weights-dir weights/v1.0.3 --device cpu
verified_entries: 15
status: pass
```

The release package also runs a credential scan, verifies every manifest hash,
and checks ZIP completeness. The manuscript continues to use synthetic
BS--RIS--UE channels and does not claim measured-channel validation.

## Identifiers

- Repository: <https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>
- Release tag: `v1.0.3`
- Zenodo version DOI: `10.5281/zenodo.23121462`
- Release-family concept DOI: <https://doi.org/10.5281/zenodo.23118757>

The DOI was reserved in the Zenodo v1.0.3 draft and will be registered when the
upload is published. No DOI is inferred from the GitHub tag.
