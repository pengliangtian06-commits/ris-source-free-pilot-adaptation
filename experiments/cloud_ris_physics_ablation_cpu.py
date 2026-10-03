"""Explicit-RIS no-physics ablation with paired target samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightning as L
import torch
from torch.utils.data import DataLoader, TensorDataset

import cloud_ris_adapter_lightning as base
from cloud_ris_shift_sweep_cpu import paired_summary


def make_loader(features, targets) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(features), torch.from_numpy(targets)),
        batch_size=128,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="auto")
    args = parser.parse_args()
    L.seed_everything(args.seed, workers=True)
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")

    source_x, source_y = base.make_samples(
        4096, seed=args.seed, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_val_x, source_val_y = base.make_samples(
        512, seed=args.seed + 10000, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_loader = make_loader(source_x, source_y)
    source_val_loader = make_loader(source_val_x, source_val_y)
    module = base.SourceLightningModule().to(device)
    trainer = L.Trainer(
        accelerator="gpu" if use_cuda else "cpu",
        devices=1,
        max_epochs=12,
        logger=False,
        enable_checkpointing=False,
        deterministic=True,
        enable_progress_bar=False,
    )
    trainer.fit(module, source_loader, source_val_loader)

    rows = []
    for angle_shift, delay_scale in ((0.08, 1.4), (0.18, 2.0)):
        target_x, target_y = base.make_samples(
            512,
            seed=args.seed + 20000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        target_loader = make_loader(target_x, target_y)
        frozen, features, targets = base.collect_predictions(module.estimator, target_loader, device)
        full_adapter, full_predictions = base.adapt_target_unlabeled(
            module.estimator,
            features,
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.003,
            prior_weight=0.1,
            batch_size=128,
        )
        no_physics_adapter, no_physics_predictions = base.adapt_target_unlabeled(
            module.estimator,
            features,
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.0,
            prior_weight=0.1,
            batch_size=128,
        )
        frozen_values = base.nmse(frozen, targets)
        full_values = base.nmse(full_predictions, targets)
        no_physics_values = base.nmse(no_physics_predictions, targets)
        rows.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "nmse": {
                    "frozen": float(frozen_values.mean()),
                    "full_physics": float(full_values.mean()),
                    "no_physics": float(no_physics_values.mean()),
                },
                "paired_statistics": {
                    "full_minus_no_physics": paired_summary(
                        full_values - no_physics_values, args.seed
                    ),
                    "full_minus_frozen": paired_summary(full_values - frozen_values, args.seed + 1),
                },
                "communication": {
                    "full_physics": base.communication_metrics(full_predictions, targets, seed=args.seed),
                    "no_physics": base.communication_metrics(no_physics_predictions, targets, seed=args.seed),
                },
                "adapter_parameters": {
                    "full_physics": sum(parameter.numel() for parameter in full_adapter.parameters()),
                    "no_physics": sum(parameter.numel() for parameter in no_physics_adapter.parameters()),
                },
            }
        )

    output = {
        "experiment": "cloud_ris_physics_ablation",
        "device": str(device),
        "seed": args.seed,
        "target_labels_used_for_adaptation": False,
        "source_validation_nmse": base.evaluate(module.estimator, source_val_loader, device),
        "results": rows,
    }
    path = Path(f"experiments/cloud_ris_physics_ablation_seed{args.seed}.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
