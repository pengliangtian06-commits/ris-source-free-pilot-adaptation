# Nature workflow audit R032

> Historical snapshot. R033 supersedes this audit; current public release
> identifiers are recorded in `nature_workflow_audit_R033.md`.

## Scope and detected axes

- **Task:** manuscript restructuring and compression with submission planning.
- **Paper type:** algorithmic/research benchmark. The algorithmic playbook is used for task definition, design rationale, evaluation, ablations, failure modes and cost; the research playbook is used for the field-scale question and bounded implication.
- **Sections:** abstract, introduction, related work, method, experiments/results, discussion and conclusion.
- **Language:** English manuscript, with Chinese author planning notes.
- **Journal axis:** generic Nature-style workflow. DCN is the target journal, not a Nature Portfolio journal; Nature guidance is used for evidence-chain discipline and reviewer audit, while DCN instructions control exact submission requirements.
- **Current source:** `paper-draft-r025.tex`.

## One-sentence argument

In an explicit wideband BS–RIS–UE simulator, source-free pilot adaptation can recover part of the degradation of a frozen learned channel estimator under controlled distribution shifts, as shown by canonical and strict held-out evaluations with communication metrics, classical references, cost controls and retained failure cells, but the recovery is conditional on geometry, SNR, pilot budget and adaptation capacity.

## Terminology ledger

| Concept | Canonical form | Avoid drift |
|---|---|---|
| deployment update | source-free pilot adaptation | source-free adaptation, test-time adaptation when the target protocol is meant |
| broad sweep | canonical shift sweep | canonical batch-level sweep |
| strict split | held-out support/evaluation protocol | held-out proof, test-time proof |
| small update | lightweight adapter / adapter-only adaptation | lightweight method when parameter count is not stated |
| large update | full-model adaptation | full fine-tuning unless the whole estimator is explicitly updated |
| channel metric | NMSE | reconstruction loss when NMSE is the reported endpoint |
| communication metrics | BER and spectral efficiency | downstream performance without naming the metric |
| frequency effect | beam squint | beam-squint effect and beam squint are allowed only as noun/modifier forms |
| independent unit | training/data seed | sample, realization or channel when referring to replication |
| uncertainty | seed SD; paired bootstrap 95% CI | confidence interval for a future observation |

## Claim–evidence map

| ID | Claim | Evidence pointer | Boundary | Status |
|---|---|---|---|---|
| C1 | Pilot-only adaptation recovers part of frozen-estimator loss over four canonical shifts. | Fig. 2; Table `table_r014_shift_sweep.tex`; canonical Results paragraph. | Target batch adaptation and tested simulator only. | Supported |
| C2 | Recovery direction survives strict support/evaluation separation. | Fig. 1 protocol; Table `table_r017_capacity.tex`; SI Table S2; held-out Results paragraph. | Three held-out shifts, three seeds, same generator. | Supported within design |
| C3 | Communication-facing gains are conditional and LS remains competitive. | Fig. 2; Fig. 5; LS columns in Tables R014/R032; robustness failure cell. | LS BER trace is not plotted in the canonical communication panel; do not claim global ranking. | Supported with qualified wording |
| C4 | Full-model adaptation is more accurate at a larger trainable parameter count. | Table `table_r017_capacity.tex`; Fig. 4; Table `table_r024_cost.tex`. | Runtime is hardware-specific; no universal speed ordering. | Supported |
| C5 | The preregistered delay-tail objective fails the independent-contribution gate. | Table `table_r021_physics_control.tex`; paired analysis with 3,072 evaluation observations. | Negative control in this configuration; no claim that every physical penalty fails. | Supported |
| C6 | Fixed-dictionary OMP is not automatically better in the two-pilot regime, while four pilots change conditioning. | Fig. 3; Table `table_r032_omp.tex`. | OMP dictionary and sparsity are fixed; not an exhaustive SBL comparison. | Supported |
| C7 | The release protocol is reproducible and label-isolated. | JSON artifacts, exporters, verifier manifest and figure QA records. | Public repository/DOI not yet assigned; final software versions still needed. | Partially supported / release pending |

## Main-text discipline audit

| Result | Class | Main-text decision | SI or source-data pointer |
|---|---|---|---|
| Explicit generator and target shift | Necessary support | Keep short before adaptation result. | JSON generator artifacts |
| Four-shift canonical recovery | Core discovery | Keep Fig. 2 and Table R014. | CPU seed JSON |
| OMP and four-pilot sensitivity | Necessary comparator/qualification | Keep concise Fig. 3 and Table R032. | OMP JSON |
| Held-out support/evaluation | Core validation | Keep Fig. 1, Table R017 and paired effect summary. | SI Table S2 |
| 18-cell robustness | Qualification and edge case | Keep Fig. 5 and the 8-element beam-squint 5-dB failure cell. | SI Table S3 |
| Delay-tail negative control | Alternative inference that changes interpretation | Keep compact Table R021 and conclusion. | Physical-control JSON |
| Capacity and timing | Core design trade-off | Keep Fig. 4 and Table R024. | Cost JSON and CUDA manifest |
| Five-record related-work matrix | Provenance/search detail | Removed from main text. | SI Table S1 and `venue_external_evidence_r030.md` |
| Full paired rows | Secondary inferential detail | Removed from main text after retaining primary interval and unit. | SI Table S2 |

## Statistical audit

- Independent replication unit: training/data seed, n = 3 for the repeated summaries.
- Paired evaluation unit: matched channel realization within a held-out evaluation block; block size is 512, with the physical-control analysis reporting 3,072 paired observations across its recorded comparison.
- Summary: means and seed SDs for repeated runs; 2,000-resample percentile bootstrap intervals for paired effects.
- Test: two-sided Wilcoxon signed-rank test for the recorded paired comparisons.
- Claim discipline: p values and intervals support within-protocol differences; they do not establish a simulator-independent population effect or a mechanism.
- No significance stars are used. The main text reports effect sizes and a primary interval; full rows remain in SI.
- **AUTHOR_INPUT_NEEDED:** final Python/PyTorch/NumPy versions, exact CUDA/driver version, and whether the submission system requires an explicit multiple-comparison statement for the prespecified paired rows.
- **AUTHOR_INPUT_NEEDED:** confirm whether all three seeds correspond to independent source training runs or whether any weights were reused.

## Citation audit

- `references.bib` contains 12 entries and 12 DOI fields.
- The RIS foundations, self-supervised adaptation, zero-shot estimation, wideband beam-squint, digital-twin, sparse and XL-RIS records are cited next to the claims they support.
- The five-record comparison is search-bounded and now stored in SI Table S1 rather than presented as a comprehensive novelty matrix.
- Crossref/publisher checks are the source hierarchy used in R032. The related-work wording avoids `first`, `unprecedented`, `complete` and universal absence claims.
- Remaining action: run the final DOI resolver check after any bibliography edit, then inspect the generated `.bbl` for author/title corruption.

## Data and code audit

- Synthetic channel realizations, JSON summaries, table exporters, figure source and verifier manifests are identified in the manuscript.
- Current statement correctly says that a public repository and DOI have not yet been assigned; it does not imply public availability.
- Required before submission: persistent repository record, release tag, license, README with exact commands, environment lock file, source-data mapping for each figure/table and a citation for the deposited record.
- Do not include SSH credentials, private host paths or other machine secrets in the archive.

## Figure audit

- Five figures were generated with the Python backend.
- Prior R032 QA records show strict source validation pass, panel alignment JSON, PDF font-floor pass and collision audit pass for each final figure.
- No figure geometry or figure source was modified in this manuscript compression; rerun PDF-level figure QA if the figure files are regenerated.
- Captions state the main summary convention and the direction of favorable deltas. Final submission should add explicit n/replicate wording if the DCN production form requests it.

## Consistency and layout audit

- Before revision: `texcount` total 5,845, text 5,209; PDF 13 pages.
- After revision source target: text must remain 6,000–10,000; PDF must be 10–12 pages.
- Related-work matrix, paired seed table and full robustness table are now SI-only, reducing float pressure while preserving the evidence record.
- The manuscript keeps one authoritative display for each main result; repeated numerical detail is removed from captions or routed to SI.
- Final checks: `texcount`, `pdfinfo`, `pdftotext`, LaTeX log, undefined references/citations grep, bibliography pass and visual page inspection.

## Open author inputs

1. Author identities, affiliations, correspondence, ORCID, funding, CRediT roles and competing interests.
2. Institution-authenticated JCR/CAS record for DCN, including year, category and quartiles.
3. Public repository, DOI, license and software versions.
4. Whether the work has a preprint, conference extension or overlapping submission.
5. Final decision on APC and any DCN graphical-abstract/highlights fields.
