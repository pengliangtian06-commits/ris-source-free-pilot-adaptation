"""Held-out target-block evaluation for source-free RIS adaptation.

The adapter is fitted on an unlabeled target support block and evaluated on a
disjoint target block generated with different seeds. This is stricter than
per-batch test-time adaptation and is the CPU gate for the planned scenario-
level/next-time-block protocol.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightning as L
import torch
from torch.utils.data import DataLoader, TensorDataset

import cloud_ris_adapter_lightning as base
from cloud_ris_shift_sweep_cpu import paired_summary


def loader(features, targets) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(features), torch.from_numpy(targets)),
        batch_size=128,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="auto")
    parser.add_argument("--mode", choices=("smoke", "full"), default="full")
    args = parser.parse_args()
    L.seed_everything(args.seed, workers=True)
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")
    source_count, block_count = ((4096, 512) if args.mode == "full" else (512, 128))

    source_x, source_y = base.make_samples(
        source_count, seed=args.seed, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_val_x, source_val_y = base.make_samples(
        block_count, seed=args.seed + 10000, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_loader = loader(source_x, source_y)
    source_val_loader = loader(source_val_x, source_val_y)
    module = base.SourceLightningModule().to(device)
    trainer = L.Trainer(
        accelerator="gpu" if use_cuda else "cpu",
        devices=1,
        max_epochs=12 if args.mode == "full" else 2,
        logger=False,
        enable_checkpointing=False,
        deterministic=True,
        enable_progress_bar=False,
    )
    trainer.fit(module, source_loader, source_val_loader)

    shifts = ((0.08, 1.4), (0.12, 1.6), (0.18, 2.0))
    results = []
    for index, (angle_shift, delay_scale) in enumerate(shifts):
        support_x, support_y = base.make_samples(
            block_count,
            seed=args.seed + 20000 + index * 1000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        eval_x, eval_y = base.make_samples(
            block_count,
            seed=args.seed + 50000 + index * 1000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        support_features = torch.from_numpy(support_x)
        eval_loader = loader(eval_x, eval_y)
        frozen, eval_features, eval_targets = base.collect_predictions(
            module.estimator, eval_loader, device
        )
        adapter = base.fit_adapter_on_unlabeled_features(
            module.estimator,
            support_features,
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.003,
            prior_weight=0.1,
        )
        no_physics_adapter = base.fit_adapter_on_unlabeled_features(
            module.estimator,
            support_features,
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.0,
            prior_weight=0.1,
        )
        with torch.no_grad():
            adapted = adapter(module.estimator(eval_features.to(device))).cpu()
            no_physics = no_physics_adapter(module.estimator(eval_features.to(device))).cpu()
        ls = base.ls_estimate(eval_features)
        frozen_values = base.nmse(frozen, eval_targets)
        adapted_values = base.nmse(adapted, eval_targets)
        no_physics_values = base.nmse(no_physics, eval_targets)
        ls_values = base.nmse(ls, eval_targets)
        results.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "support_count": block_count,
                "evaluation_count": block_count,
                "support_and_evaluation_seed_blocks_are_disjoint": True,
                "target_labels_used_for_adaptation": False,
                "nmse": {
                    "ls": float(ls_values.mean()),
                    "frozen": float(frozen_values.mean()),
                    "adapted": float(adapted_values.mean()),
                    "no_physics": float(no_physics_values.mean()),
                },
                "paired_statistics": {
                    "adapted_minus_frozen": paired_summary(
                        adapted_values - frozen_values, args.seed + index
                    ),
                    "adapted_minus_no_physics": paired_summary(
                        adapted_values - no_physics_values, args.seed + index + 10
                    ),
                    "adapted_minus_ls": paired_summary(
                        adapted_values - ls_values, args.seed + index + 20
                    ),
                },
                "communication": {
                    "ls": base.communication_metrics(ls, eval_targets, seed=args.seed),
                    "frozen": base.communication_metrics(frozen, eval_targets, seed=args.seed),
                    "adapted": base.communication_metrics(adapted, eval_targets, seed=args.seed),
                    "no_physics": base.communication_metrics(
                        no_physics, eval_targets, seed=args.seed
                    ),
                },
            }
        )

    output = {
        "experiment": "cloud_ris_heldout_target_block",
        "mode": args.mode,
        "device": str(device),
        "seed": args.seed,
        "source_validation_nmse": base.evaluate(module.estimator, source_val_loader, device),
        "results": results,
    }
    path = Path(f"experiments/cloud_ris_heldout_geometry_{args.mode}_seed{args.seed}.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
