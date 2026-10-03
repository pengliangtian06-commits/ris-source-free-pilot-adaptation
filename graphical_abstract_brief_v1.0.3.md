# Graphical abstract brief v1.0.3

## Status

Internal deterministic design draft. Submission eligibility, dimensions and
graphical-abstract policy must be confirmed on the current *Physical
Communication* submission page before upload.

## One-sentence message

Pilot-only residual adaptation can recover part of a source estimator's loss
under explicit wideband RIS shifts, but the recovery depends on held-out target
evaluation, geometry and adaptation capacity.

## Reading order and audience

Read left to right. The intended audience is wireless-communications researchers
who know pilots and channel estimation but may not know the implementation
details of this benchmark.

## Required elements

1. Source CSI training produces a frozen estimator.
2. Target pilots enter a residual adapter; target labels stay in a locked scoring box.
3. Four explicit shifts are represented by angle and delay labels.
4. Outputs are NMSE, BER and spectral efficiency.
5. A red boundary callout marks the 8-element beam-squint, 5-dB failure cell.
6. A small cost callout distinguishes 16,576 adapter parameters from 115,328
   full-model parameters.

## Forbidden implications

Do not draw measured hardware, a calibrated physical aperture, universal gains,
or a causal physical mechanism. Do not add invented percentages, logos or
unreported measurements.

## Provenance and QA

The current graphical abstract is generated deterministically from the protocol
and locked result values. Its source, PDF, SVG and PNG are included for review.
Text, arrows and labels remain editable. The final asset must be checked against
the manuscript, the journal's image policy and the final v1.0.3 DOI metadata.
