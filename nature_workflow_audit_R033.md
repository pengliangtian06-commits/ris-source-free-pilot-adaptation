# Nature workflow audit R033

## Scope and routing

- **Task:** whole-manuscript restructuring, evidence-bound polishing and initial submission planning.
- **Paper type:** algorithmic research benchmark.
- **Sections:** abstract, introduction, related work, methods, results, discussion, limitations and data/code statement.
- **Language:** English manuscript with Chinese planning notes.
- **Journal axis:** generic Nature-style workflow. DCN is an Elsevier communications target, so Nature-style evidence-chain guidance is used for argument discipline while DCN's current author guide controls exact submission requirements.
- **Primary source:** `paper-draft-r025.tex`.

## Nature-style argument audit

The manuscript now follows the shortest sufficient evidence chain:

`explicit shift -> prequential pilot-only recovery -> classical/pilot-budget comparator -> strict held-out transfer -> robustness failure cell -> negative physical control -> capacity and cost trade-off -> simulator boundary`.

Each Results subsection answers one question and ends with a bounded inference. The Discussion synthesizes the result, positions it against adjacent work, states the cost and deployment implications, and limits the inference to the explicit simulator. The abstract and conclusion use “recovers part of” and “conditional” wording; no universal, causal or measured-channel claim is made.

## Evidence and implementation changes completed in R033

1. `adapt_target_unlabeled` accepts pilot features only. The canonical sweep is four ordered 128-sample batches, ten updates per batch, with adapter state carried forward and post-update scoring.
2. The channel equation and generator agree on `h_UE.T @ diag(reflection) @ h_BS`; the deterministic generator consistency test passes.
3. Adapter-only and full-model held-out updates use the same `smooth_weight=0.003` objective. The local capacity artifacts were regenerated on CPU.
4. LS BER and spectral efficiency are included in the canonical table and Figure 2, so the communication claim is not based on a hidden baseline omission.
5. Figure 4 reports only the locally regenerated CPU cost, and its caption no longer refers to an absent held-out-NMSE panel. Figure 5 labels use five decimal places.
6. The methods state the normalized simulator frequency coordinate, delay distributions, path-gain normalization, missing physical carrier/bandwidth mapping and the element-count interpretation of RIS size.

## Statistical reporting audit

- **Independent repeated unit:** training/data seed, three fixed seeds.
- **Paired unit:** matched channel realization within a target evaluation block.
- **Uncertainty:** seed mean and SD for repeated runs; 2,000-resample percentile bootstrap for paired block-level differences.
- **Test:** two-sided Wilcoxon signed-rank test where recorded.
- **Inference boundary:** channel-level intervals and tests are block-conditional. The 3,072 pairs in the physical control are not 3,072 independent experiments.
- **Multiplicity:** four shifts, three communication outcomes, 18 robustness cells and several controls are presented as effect-size/descriptive evidence. Only the preregistered delay-tail contrast keeps confirmatory gate wording.
- **No significance stars:** effect sizes, intervals and unit definitions carry the main claims.

## Figure, citation and data audit

- Five figures were regenerated from JSON artifacts using the Nature-figure Python backend. Alignment and collision checks pass for the current PDFs, SVGs and TIFFs.
- `table_r014_shift_sweep.tex` reports LS, frozen and adapted NMSE, BER and spectral efficiency from the same three-seed artifacts.
- DOI-verified neighboring records remain a bounded search matrix in Supplementary Table S1. The paper does not issue a global novelty certificate.
- The Data and Code Availability statement now points to the public GitHub `v1.0.2` release, the dual-license files, Zenodo version DOI `10.5281/zenodo.23119393` and concept DOI `10.5281/zenodo.23118757`; the v1.0.1 version DOI is also preserved.

## Reproducibility status

The R033 release contains the current TeX, table exporters, CPU aggregation script, generator and consistency gate, canonical/held-out/robustness/physics/cost JSON artifacts, source scripts, five final figures, supplementary tables and a credential-scanned manifest. The local environment is CPU-only (Python 3.14.7, PyTorch 2.14.1+cpu, Lightning 2.6.6, NumPy 2.5.2, SciPy 1.18.1, Matplotlib 3.11.1). Remote CUDA logs and stale CUDA artifacts are excluded from the current paper-grade package.

## Final validation and remaining submission gates

1. **Completed:** local `latexmk` compilation succeeded for the main manuscript and supplementary tables; the current author-complete main PDF has 12 pages and the supplementary PDF has 3 pages. The built-in editor compiler could not run because it returned `Unable to find standard directories for platform`; this is an environment limitation, not a source error.
2. **Completed:** `texcount` reports 6,381 words in text, 132 words in headings and 320 words in captions/floats. Undefined-reference, citation and multiply-defined-label checks are clean.
3. **Completed:** the final page-10 visual check contains the revised local CPU limitation and no stale Tesla/P100 wording. The regenerated v1.0.2 package contains 108 allowlisted files, credential scanning passes, every paper-grade per-seed JSON reports `device=cpu`, and the manifest hash for `paper-draft-r025.tex` matches the source.
4. **Completed for the automatic portion of Phase 4:** `DCN投稿门槛核验_R034.md` records the official Elsevier serial metadata response and the attempted Guide for Authors retrieval. The dynamic ScienceDirect page returned HTTP 403, so its article-specific fields remain explicitly unconfirmed.
5. **Partially completed author input:** supplied names, affiliations, first-author ORCID and provisional CRediT are recorded; corresponding-author designation, final contact choice, funding and acknowledgements remain open.
6. **Pending author/institution verification:** open the DCN guide and submission system in a normal browser, confirm article type and upload fields, and record institutional Clarivate JCR/MJL and CAS evidence before describing its quartile as confirmed.
