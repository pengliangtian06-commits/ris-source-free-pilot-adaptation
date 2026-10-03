"""Full-model versus adapter-only adaptation on held-out explicit-RIS blocks."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import lightning as L
import torch
from torch.utils.data import DataLoader, TensorDataset

import cloud_ris_adapter_lightning as base


def loader(features, targets) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(features), torch.from_numpy(targets)),
        batch_size=128,
    )


def full_model_parameter_count(model: base.SourceEstimator) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def fit_full_model(
    source_estimator: base.SourceEstimator,
    support_features: torch.Tensor,
    *,
    device: torch.device,
    steps: int,
    learning_rate: float,
) -> base.SourceEstimator:
    model = copy.deepcopy(source_estimator).to(device)
    model.train()
    support_features = support_features.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = base.physics_loss(
            model(support_features),
            support_features,
            smooth_weight=0.003,
            prior_weight=0.1,
        )
        loss.backward()
        optimizer.step()
    return model.eval()


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
    source_loader = loader(source_x, source_y)
    source_val_loader = loader(source_val_x, source_val_y)
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
    for index, (angle_shift, delay_scale) in enumerate(((0.08, 1.4), (0.12, 1.6), (0.18, 2.0))):
        support_x, _ = base.make_samples(
            512,
            seed=args.seed + 20000 + index * 1000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        eval_x, eval_y = base.make_samples(
            512,
            seed=args.seed + 50000 + index * 1000,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        eval_loader = loader(eval_x, eval_y)
        frozen, eval_features, targets = base.collect_predictions(module.estimator, eval_loader, device)
        adapter = base.fit_adapter_on_unlabeled_features(
            module.estimator,
            torch.from_numpy(support_x),
            device=device,
            steps=10,
            learning_rate=1e-3,
            smooth_weight=0.003,
            prior_weight=0.1,
        )
        full_model = fit_full_model(
            module.estimator,
            torch.from_numpy(support_x),
            device=device,
            steps=10,
            learning_rate=1e-3,
        )
        with torch.no_grad():
            adapted = adapter(module.estimator(eval_features.to(device))).cpu()
            full_prediction = full_model(eval_features.to(device)).cpu()
        rows.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "target_labels_used_for_adaptation": False,
                "nmse": {
                    "frozen": float(base.nmse(frozen, targets).mean()),
                    "adapter_only": float(base.nmse(adapted, targets).mean()),
                    "full_model": float(base.nmse(full_prediction, targets).mean()),
                },
                "communication": {
                    "adapter_only": base.communication_metrics(adapted, targets, seed=args.seed),
                    "full_model": base.communication_metrics(full_prediction, targets, seed=args.seed),
                },
            }
        )

    output = {
        "experiment": "cloud_ris_full_model_vs_adapter_heldout",
        "device": str(device),
        "seed": args.seed,
        "source_validation_nmse": base.evaluate(module.estimator, source_val_loader, device),
        "parameters": {
            "source_estimator_and_full_model": full_model_parameter_count(module.estimator),
            "adapter_only": sum(parameter.numel() for parameter in adapter.parameters()),
        },
        "results": rows,
    }
    path = Path(f"experiments/cloud_ris_full_model_heldout_seed{args.seed}.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
