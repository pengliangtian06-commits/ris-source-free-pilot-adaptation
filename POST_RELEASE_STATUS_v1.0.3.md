# v1.0.3 post-release status

Verification date: 2026-10-04 (Asia/Taipei)

This file records facts verified after the immutable `v1.0.3` ZIP and tag were
created. It is intentionally separate from the archived ZIP, whose manifest
and release notes are retained unchanged.

## Public release identity

- GitHub repository: <https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>
- GitHub release: <https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation/releases/tag/v1.0.3>
- Git tag `v1.0.3` dereferences to commit `763755aebd288a2e4fd9a523d0c446d0cf0dd624`.
- GitHub `main` contains post-release verification records; the tagged release
  tree remains immutable.
- The post-release submission-material updates are recorded on `main` at
  `ce01a9464ad3d62ef9133c58711142829c5d1fc6`, `25f7e0716fd6dae22f0be8ff79c3d68a01c2491d`,
  and the later verification commits. None rewrites the tag or Zenodo archive.
- GitHub asset: `submission_package_v1.0.3.zip`, 4,132,213 bytes,
  SHA-256 `4c15cd3907b1bed0988021ffc6ead620be4c1276a423b917df3f6e089c764fa9`.

## Zenodo record

- Version record: <https://zenodo.org/records/23121462>
- Version DOI: <https://doi.org/10.5281/zenodo.23121462>
- Concept DOI: <https://doi.org/10.5281/zenodo.23118757>
- Version: `1.0.3`, published 2026-10-03, public access.
- Zenodo file: `submission_package_v1.0.3.zip`, 4,132,213 bytes,
  MD5 `666dd58e35d4f45264dac1d6aeca4894`.
- The record displays both MIT License and Creative Commons Attribution 4.0
  International. The package keeps code under MIT and manuscript, figures,
  tables, generated artifacts and weights under CC BY 4.0.
- Zenodo's related software URL points to the GitHub `v1.0.3` tree.

## Verification result

- GitHub asset and Zenodo file have the same byte size and MD5.
- The GitHub asset SHA-256 equals the local package SHA-256.
- GitHub release is published, non-draft, non-prerelease and marked Latest.
- The local manifest contains 134 allowlisted files, five intentional
  exclusions, and a passed credential scan.

## Security-scan hygiene

- The current `main` branch uses generic password, private-network and SSH
  pattern checks in `experiments/create_submission_package.py`; no literal
  password or host value is needed by the scanner.
- The immutable v1.0.3 archive retains the historical scanner source used to
  create that release. Its defined ZIP scan passed and no credential value is
  present in the package data or weights. A future hotfix release should keep
  the generic scanner source when the package is republished.

## Remaining submission gates

1. Record institution-authenticated Clarivate JCR/MJL and CAS evidence for
   *Physical Communication* (ISSN `1874-4907`).
2. Verify the live Elsevier guide and submission-system fields, including
   article type, abstract/highlights limits, graphical abstract, declarations,
   AI-use statement, ORCID/CRediT and APC.
3. Confirm the corresponding-author postal address. The institution's official
   website lists Beijing University of Posts and Telecommunications Century
   College, Kangzhuang Avenue, Kangzhuang Town, Yanqing District, Beijing
   102101, China. The evidence and candidate rendering are recorded in
   `author_address_evidence_20261004.md`; this remains an author confirmation
   item.
4. Keep the shell compilation and Nature-style preflight records with the
   submission audit. The built-in editor compiler remains unavailable in this
   environment, so the journal remains a candidate until the institutional and
   live-system records above are supplied.

## Latest local verification

- Current `main` commit: `4da613ee3e15770dc82bde07426dfcefd1222bfe`.
- Elsevier serial metadata endpoint returned HTTP 200.
- Version DOI resolved with HTTP 200.
- Weight verifier returned `verified_entries: 15` and `status: pass`.
- Submission manifest returned 18 files with zero hash mismatches.
- Release ZIP returned `testzip() = None`.

The current submission package cites the published version DOI
`10.5281/zenodo.23121462` as its sole Zenodo identifier. The older release note
inside the immutable archive is retained for historical provenance.

