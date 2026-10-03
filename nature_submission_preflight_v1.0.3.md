# Nature-style submission preflight for v1.0.3

Verification date: 2026-10-03 (Asia/Taipei)

This is a Nature-style evidence-chain and submission-package audit applied to
an Elsevier *Physical Communication* target. Nature guidance supplies claim,
main-text, statistics and availability discipline; the target journal's live
instructions remain authoritative for exact fields.

## Routing and argument

- Task: initial submission package and whole-manuscript preflight.
- Paper type: algorithmic research benchmark.
- Core claim: within the tested synthetic wideband BS--RIS--UE generator,
  pilot-only residual adaptation recovers part of a frozen estimator's loss
  under explicit shifts, with held-out transfer, capacity trade-offs and
  failure cells defining the operating boundary.
- Evidence chain: explicit shift → pilot-only recovery → LS/OMP and pilot-budget
  comparison → disjoint support/evaluation transfer → robustness failure cell →
  negative physical control → capacity/cost trade-off → simulator boundary.
- Boundary: no measured-channel validity, universal superiority or independently
  established physical mechanism is claimed.

## Main-text allocation

| Result | Function | Destination |
|---|---|---|
| Four-shift recovery | core discovery | Main Results, Fig. 2/Table 1 |
| LS/OMP and pilot budget | necessary support | Main Results, Fig. 3/Table 2 |
| Held-out support/evaluation | decisive transport qualification | Main Results, Table 3 |
| 8-element beam-squint/5 dB cell | conclusion-changing edge case | Main Results, Fig. 4 |
| Delay-tail negative control | mechanism boundary | Main Results, Table 4 |
| Full-model parameter/cost comparison | capacity implication | Main Results, Fig. 5/Table 5 |
| Seed-level intervals and full robustness matrix | provenance and secondary detail | Supplementary tables/source artifacts |

## Statistics and consistency

- Independent repeated unit: three fixed training/data seeds
  (`20261002`, `20261003`, `20261004`).
- Paired unit: matched channel realization within an evaluation block.
- Uncertainty: seed mean/SD; 2,000-resample paired bootstrap intervals; the
  recorded two-sided Wilcoxon test is retained for the preregistered control.
- The manuscript explicitly says that channel-level pairs are not independent
  simulator experiments and that descriptive multi-cell results are not a
  universal significance claim.
- Shell compilation produced no undefined references, undefined citations or
  multiply-defined labels. The deterministic audit found no internal arithmetic
  or ordering contradiction in the supplied headline values.

## Data, code and model availability

- Synthetic generator, fixed seeds, result artifacts, source code and CPU
  state-dict weights are mapped to the GitHub `v1.0.3` tree and Zenodo version
  DOI `10.5281/zenodo.23121462`.
- Concept DOI: `10.5281/zenodo.23118757`.
- Code is MIT; manuscript, figures, tables, generated artifacts and weights
  are CC BY 4.0. Zenodo displays both licenses.
- Target CSI labels are scoring-only and are excluded from adaptation.
- No measured or ray-traced channel dataset is implied.

## Build and package checks

- Main PDF: 11 pages; 6,072 words in text, 132 in headings and 320 in
  captions/floats.
- Supplementary tables PDF: 3 pages.
- `latexmk` shell compilation: passed for both sources.
- Built-in editor compiler: unavailable in this environment because it reports
  `Unable to find standard directories for platform`; this is recorded as an
  environment limitation.
- Weight verifier: 15/15 entries passed on CPU with `weights_only=True`.
- ZIP: 4,132,213 bytes; `testzip()` passed; all 134 manifest entries match the
  archived ZIP bytes and hashes; ZIP credential scan passed.
- GitHub asset SHA-256:
  `4c15cd3907b1bed0988021ffc6ead620be4c1276a423b917df3f6e089c764fa9`.

## Submission gate

The scientific and reproducibility package is `ready_with_author_checks`.
Institution-authenticated JCR/CAS classification and live Elsevier submission
fields remain unresolved. Until those records are supplied or verified in a
logged-in institutional route, *Physical Communication* remains a candidate
route rather than a confirmed submission route.

