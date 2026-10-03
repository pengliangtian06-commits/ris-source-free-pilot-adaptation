# Cover letter for *Physical Communication*

Dear Editors,

Please consider our manuscript, “Source-free pilot adaptation for RIS-assisted
wideband MIMO channel estimation under explicit distribution shifts”, for
publication as an Original Research Article in *Physical Communication*.

The manuscript addresses a deployment problem in learned wireless channel
estimation: a source estimator can degrade after a propagation shift while
target CSI labels are unavailable. We evaluate a lightweight residual adapter
that uses received pilots only in an explicit wideband BS--RIS--UE simulator.
The protocol separates an unlabeled target support block from a disjoint
evaluation block and reports NMSE, QPSK BER, spectral efficiency, adaptation
capacity and failure cells alongside LS and fixed-dictionary OMP references.

The principal result is deliberately bounded. Pilot-only adaptation recovers
part of the frozen estimator's loss across four tested shifts, and the recovery
direction persists on disjoint held-out target blocks. The benefit is conditional:
least squares remains competitive in BER, an eight-element beam-squint cell at
5 dB worsens all three communication-facing outcomes, and full-model adaptation
is more accurate at approximately 6.96 times the trainable parameter count. A
preregistered delay-tail objective fails its independent-contribution gate and
is retained as a negative control. The paper therefore presents a reproducible
benchmark and failure analysis rather than a claim of universal superiority.

The release includes the synthetic generator, fixed seeds, CPU result artifacts,
verification scripts and CPU-loadable source/adapter weights. We state explicitly
that the work does not establish measured-channel validity. The authors declare
no competing interests, no specific grant funding and no additional
acknowledgements. AI-assisted tools supported workflow organization and language
editing; the authors designed the study, controlled the experiments and verified
the final claims.

This manuscript is not under consideration elsewhere. All authors have approved
the manuscript and agree with its submission to *Physical Communication*.

Sincerely,

Changjiang Zhang  
Corresponding author  
Beijing University of Posts and Telecommunications Century College  
zhangchangjiang@ccbupt.cn
