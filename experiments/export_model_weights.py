"""Export paper-grade source and canonical-adapter state dictionaries.

The exporter reuses the locked training and adaptation implementation from
``cloud_ris_adapter_lightning.py``.  It writes weights as plain state_dict
files and keeps architecture/protocol metadata in JSON so that loading never
requires executing a serialized Python object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import lightning as L
import torch
from torch.utils.data import DataLoader, TensorDataset

import cloud_ris_adapter_lightning as base


SEEDS = (20261002, 20261003, 20261004)
SHIFTS = ((0.04, 1.2), (0.08, 1.4), (0.12, 1.6), (0.18, 2.0))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def train_source(seed: int, device: torch.device) -> base.SourceEstimator:
    L.seed_everything(seed, workers=True)
    source_x, source_y = base.make_samples(
        4096, seed=seed, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_val_x, source_val_y = base.make_samples(
        512, seed=seed + 10000, beam_squint=True, angle_shift=0.0, delay_scale=1.0
    )
    source_loader = DataLoader(
        TensorDataset(torch.from_numpy(source_x), torch.from_numpy(source_y)),
        batch_size=128,
        shuffle=True,
    )
    source_val_loader = DataLoader(
        TensorDataset(torch.from_numpy(source_val_x), torch.from_numpy(source_val_y)),
        batch_size=128,
    )
    module = base.SourceLightningModule().to(device)
    trainer = L.Trainer(
        accelerator="gpu" if device.type == "cuda" else "cpu",
        devices=1,
        max_epochs=12,
        logger=False,
        enable_checkpointing=False,
        deterministic=True,
        enable_progress_bar=False,
    )
    trainer.fit(module, source_loader, source_val_loader)
    return base.prepare_estimator(module.estimator, device)


def export_state(module: torch.nn.Module, path: Path) -> None:
    state = {name: tensor.detach().cpu() for name, tensor in module.state_dict().items()}
    torch.save(state, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--output-dir", type=Path, default=Path("weights/v1.0.3"))
    args = parser.parse_args()

    unknown = sorted(set(args.seeds) - set(SEEDS))
    if unknown:
        raise SystemExit(f"seeds must be drawn from {SEEDS}; received {unknown}")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but unavailable")

    device = torch.device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for seed in args.seeds:
        estimator = train_source(seed, device)
        source_name = f"source_estimator_seed{seed}.pt"
        source_path = args.output_dir / source_name
        export_state(estimator, source_path)
        manifest.append(
            {
                "file": source_name,
                "sha256": digest(source_path),
                "model_type": "source_estimator",
                "seed": seed,
                "device_export": "cpu",
                "parameter_count": sum(p.numel() for p in estimator.parameters()),
                "architecture": "SourceEstimator(input=64, hidden=[256,256], output=128, GELU)",
                "source_training": {
                    "samples": 4096,
                    "epochs": 12,
                    "batch_size": 128,
                    "optimizer": "AdamW",
                    "learning_rate": 0.002,
                    "weight_decay": 1e-5,
                },
            }
        )
        for angle_shift, delay_scale in SHIFTS:
            target_x, _ = base.make_samples(
                512,
                seed=seed + 20000,
                beam_squint=True,
                angle_shift=angle_shift,
                delay_scale=delay_scale,
            )
            adapter, _ = base.adapt_target_unlabeled(
                estimator,
                torch.from_numpy(target_x),
                device=device,
                steps=10,
                learning_rate=1e-3,
                smooth_weight=0.003,
                prior_weight=0.1,
                batch_size=128,
            )
            shift_tag = f"angle{angle_shift:g}_delay{delay_scale:g}".replace(".", "p")
            adapter_name = f"adapter_seed{seed}_{shift_tag}.pt"
            adapter_path = args.output_dir / adapter_name
            export_state(adapter, adapter_path)
            manifest.append(
                {
                    "file": adapter_name,
                    "sha256": digest(adapter_path),
                    "model_type": "canonical_adapter_final_state",
                    "seed": seed,
                    "angle_shift": angle_shift,
                    "delay_scale": delay_scale,
                    "device_export": "cpu",
                    "parameter_count": sum(p.numel() for p in adapter.parameters()),
                    "architecture": "LightweightAdapter(width=64, residual, GELU)",
                    "target_adaptation": {
                        "support_samples": 512,
                        "prequential_batches": 4,
                        "batch_size": 128,
                        "steps_per_batch": 10,
                        "learning_rate": 1e-3,
                        "smooth_weight": 0.003,
                        "prior_weight": 0.1,
                        "target_labels_used_for_adaptation": False,
                        "state_semantics": "final adapter state after the four canonical batches",
                    },
                }
            )

    metadata = {
        "schema": "ris-adaptation-weights/1.0",
        "release": "v1.0.3",
        "license": "CC-BY-4.0",
        "code_license": "MIT",
        "source": "experiments/cloud_ris_adapter_lightning.py",
        "device": "cpu",
        "seeds": list(args.seeds),
        "canonical_shifts": [{"angle_shift": a, "delay_scale": d} for a, d in SHIFTS],
        "target_labels_used_for_adaptation": False,
        "entries": manifest,
    }
    (args.output_dir / "weights_manifest.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output_dir": str(args.output_dir), "entries": len(manifest)}, indent=2))


if __name__ == "__main__":
    main()
