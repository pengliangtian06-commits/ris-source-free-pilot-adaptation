"""One-source-checkpoint sweep over explicit-RIS target shifts.

The source estimator is trained once per seed.  Each target shift then gets a
fresh lightweight adapter, so target environments cannot influence one another
through optimizer state.  Target CSI is retained only for evaluation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightning as L
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from scipy import stats

import cloud_ris_adapter_lightning as base


def loader(features, targets, batch_size: int = 128) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(features), torch.from_numpy(targets)),
        batch_size=batch_size,
    )


def paired_summary(values: torch.Tensor, seed: int) -> dict[str, float | list[float]]:
    differences = values.detach().cpu().numpy().astype(np.float64)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, differences.size, size=(2000, differences.size))
    bootstrap_means = differences[indices].mean(axis=1)
    signed_rank = stats.wilcoxon(differences, alternative="two-sided", method="auto")
    return {
        "mean_difference": float(differences.mean()),
        "median_difference": float(np.median(differences)),
        "bootstrap_ci95": [
            float(np.percentile(bootstrap_means, 2.5)),
            float(np.percentile(bootstrap_means, 97.5)),
        ],
        "wilcoxon_p_value": float(signed_rank.pvalue),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="auto")
    parser.add_argument("--mode", choices=("smoke", "full"), default="full")
    args = parser.parse_args()
    L.seed_everything(args.seed, workers=True)
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")
    source_count, target_count = ((4096, 512) if args.mode == "full" else (512, 128))
    source_x, source_y = base.make_samples(
        source_count,
        seed=args.seed,
        beam_squint=True,
        angle_shift=0.0,
        delay_scale=base.SOURCE_DELAY_SCALE,
    )
    source_val_x, source_val_y = base.make_samples(
        target_count,
        seed=args.seed + 10000,
        beam_squint=True,
        angle_shift=0.0,
        delay_scale=base.SOURCE_DELAY_SCALE,
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

    shifts = ((0.04, 1.2), (0.08, 1.4), (0.12, 1.6), (0.18, 2.0))
    results = []
    for angle_shift, delay_scale in shifts:
        target_x, target_y = base.make_samples(
            target_count,
            seed=args.seed + 20000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        target_loader = loader(target_x, target_y)
        frozen_predictions, target_features, target_targets = base.collect_predictions(
            module.estimator, target_loader, device
        )
        adapter, adapted_predictions = base.adapt_target_unlabeled(
            module.estimator,
            target_features,
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.003,
            prior_weight=0.1,
            batch_size=128,
        )
        ls_predictions = base.ls_estimate(target_features)
        ls_values = base.nmse(ls_predictions, target_targets)
        frozen_values = base.nmse(frozen_predictions, target_targets)
        adapted_values = base.nmse(adapted_predictions, target_targets)
        results.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "target_labels_used_for_adaptation": False,
                "nmse": {
                    "ls": float(ls_values.mean()),
                    "frozen": float(frozen_values.mean()),
                    "adapted": float(adapted_values.mean()),
                },
                "paired_statistics": {
                    "adapted_minus_frozen": paired_summary(adapted_values - frozen_values, args.seed),
                    "adapted_minus_ls": paired_summary(adapted_values - ls_values, args.seed + 1),
                },
                "communication": {
                    "ls": base.communication_metrics(ls_predictions, target_targets, seed=args.seed),
                    "frozen": base.communication_metrics(frozen_predictions, target_targets, seed=args.seed),
                    "adapted": base.communication_metrics(adapted_predictions, target_targets, seed=args.seed),
                },
                "adapter_parameters": sum(parameter.numel() for parameter in adapter.parameters()),
            }
        )

    output = {
        "experiment": "cloud_ris_explicit_target_shift_sweep",
        "mode": args.mode,
        "device": str(device),
        "seed": args.seed,
        "source_validation_nmse": base.evaluate(module.estimator, source_val_loader, device),
        "results": results,
    }
    output_path = Path(f"experiments/cloud_ris_shift_sweep_{args.mode}_seed{args.seed}.json")
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
