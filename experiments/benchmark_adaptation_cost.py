"""Benchmark adapter-only versus full-model target adaptation cost.

The support labels are generated and immediately discarded. This benchmark
measures adaptation cost only; it does not use target CSI for fitting or model
selection. Run the same seed and step count on CPU and CUDA before reporting
hardware-dependent timing in a manuscript.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import lightning as L
import torch

import cloud_ris_adapter_lightning as base
from cloud_ris_full_model_heldout_cpu import fit_full_model, full_model_parameter_count


def timed(callable_, device: torch.device) -> float:
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    start = time.perf_counter()
    callable_()
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="auto")
    parser.add_argument("--support-count", type=int, default=512)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    L.seed_everything(args.seed, workers=True)
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but unavailable; no CPU fallback is permitted")
    device = torch.device("cuda" if use_cuda else "cpu")
    support_x, _support_y = base.make_samples(
        args.support_count,
        seed=args.seed + 20000,
        beam_squint=True,
        angle_shift=0.12,
        delay_scale=1.6,
    )
    support = torch.from_numpy(support_x)
    estimator = base.SourceEstimator().to(device).eval()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    adapter_times: list[float] = []
    full_model_times: list[float] = []
    for _ in range(args.repeats):
        adapter_times.append(
            timed(
                lambda: base.fit_adapter_on_unlabeled_features(
                    estimator,
                    support,
                    device=device,
                    steps=args.steps,
                    learning_rate=1e-3,
                    smooth_weight=0.003,
                    prior_weight=0.1,
                ),
                device,
            )
        )
        full_model_times.append(
            timed(
                lambda: fit_full_model(
                    estimator,
                    support,
                    device=device,
                    steps=args.steps,
                    learning_rate=1e-3,
                ),
                device,
            )
        )
    adapter_params = sum(parameter.numel() for parameter in base.LightweightAdapter().parameters())
    output = {
        "experiment": "adaptation_cost_benchmark",
        "seed": args.seed,
        "device": str(device),
        "support_count": args.support_count,
        "steps": args.steps,
        "repeats": args.repeats,
        "target_labels_used_for_adaptation": False,
        "parameters": {
            "adapter_only": adapter_params,
            "full_model": full_model_parameter_count(estimator),
        },
        "wall_clock_seconds": {
            "adapter_only": adapter_times,
            "full_model": full_model_times,
        },
        "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None,
    }
    path = Path(__file__).resolve().parent / f"adaptation_cost_{device.type}_seed{args.seed}.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
