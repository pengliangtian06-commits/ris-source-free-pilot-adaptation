"""Preregistered held-out physics-control experiment for explicit RIS.

The primary comparison is a fixed delay-domain tail penalty versus the
measurement-only adapter. All objective settings are fixed in
``refine-logs/PHYSICS_PREREGISTRATION_R021.md`` before execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

import cloud_ris_adapter_lightning as base
from cloud_ris_robustness_adapter_cpu import (
    EVAL_COUNT,
    SUPPORT_COUNT,
    fit_adapter,
    train_source,
)


SHIFTS = ((0.08, 1.4), (0.18, 2.0))
SEEDS = (20261002, 20261003, 20261004)
DELAY_MODES = 5
DELAY_WEIGHT = 0.003
PRIOR_WEIGHT = 0.1
ADAPT_STEPS = 10
ADAPTER_LR = 1e-3


def delay_tail_loss(
    adapted: torch.Tensor,
    observations: torch.Tensor,
    *,
    delay_modes: int = DELAY_MODES,
    delay_weight: float = DELAY_WEIGHT,
) -> torch.Tensor:
    estimate = base.unpack_complex(adapted, base.N_TX)
    observed = base.unpack_complex(observations, base.PILOT_COUNT)
    measurement = (estimate[..., : base.PILOT_COUNT] - observed).abs().square().mean()
    spectrum = torch.fft.fft(estimate, dim=1)
    mask = torch.zeros(base.N_SUBCARRIERS, dtype=torch.bool, device=estimate.device)
    positive = (delay_modes + 1) // 2
    negative = delay_modes // 2
    mask[:positive] = True
    if negative:
        mask[-negative:] = True
    tail = spectrum[:, ~mask, :].abs().square().mean()
    return measurement + delay_weight * tail + PRIOR_WEIGHT * adapted.square().mean()


def fit_objective(
    estimator: base.SourceEstimator,
    support_features: torch.Tensor,
    *,
    condition: str,
    device: torch.device,
) -> base.LightweightAdapter:
    estimator.eval()
    adapter = base.LightweightAdapter().to(device)
    support_features = support_features.to(device)
    with torch.no_grad():
        frozen = estimator(support_features)
    optimizer = torch.optim.Adam(adapter.parameters(), lr=ADAPTER_LR)
    adapter.train()
    for _ in range(ADAPT_STEPS):
        optimizer.zero_grad(set_to_none=True)
        adapted = adapter(frozen)
        if condition == "no_physics":
            loss = base.physics_loss(
                adapted,
                support_features,
                smooth_weight=0.0,
                prior_weight=PRIOR_WEIGHT,
            )
        elif condition == "first_difference":
            loss = base.physics_loss(
                adapted,
                support_features,
                smooth_weight=0.003,
                prior_weight=PRIOR_WEIGHT,
            )
        elif condition == "delay_tail":
            loss = delay_tail_loss(adapted, support_features)
        else:
            raise ValueError(f"unknown condition: {condition}")
        loss.backward()
        optimizer.step()
    return adapter.eval()


def bootstrap_ci(values: np.ndarray, seed: int, draws: int = 2000) -> list[float]:
    rng = np.random.default_rng(seed)
    means = np.empty(draws, dtype=np.float64)
    for index in range(draws):
        sample = values[rng.integers(0, values.size, values.size)]
        means[index] = np.mean(sample)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def run_seed(seed: int, device: torch.device) -> dict[str, object]:
    estimator = train_source(seed, device)
    rows: list[dict[str, object]] = []
    for shift_index, (angle_shift, delay_scale) in enumerate(SHIFTS):
        support_x, _ = make_shifted_samples(
            SUPPORT_COUNT, seed + 20000 + shift_index * 1000, angle_shift, delay_scale
        )
        eval_x, eval_y = make_shifted_samples(
            EVAL_COUNT, seed + 50000 + shift_index * 1000, angle_shift, delay_scale
        )
        support_features = torch.from_numpy(support_x)
        eval_features = torch.from_numpy(eval_x)
        eval_targets = torch.from_numpy(eval_y)
        with torch.no_grad():
            frozen = estimator(eval_features.to(device)).cpu()
        predictions: dict[str, torch.Tensor] = {}
        for condition in ("no_physics", "first_difference", "delay_tail"):
            adapter = fit_objective(estimator, support_features, condition=condition, device=device)
            with torch.no_grad():
                predictions[condition] = adapter(estimator(eval_features.to(device))).cpu()
        values = {name: base.nmse(prediction, eval_targets).numpy() for name, prediction in predictions.items()}
        differences = values["delay_tail"] - values["no_physics"]
        rows.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "evaluation_samples": EVAL_COUNT,
                "target_labels_used_for_adaptation": False,
                "nmse": {name: float(np.mean(value)) for name, value in values.items()},
                "delay_tail_minus_no_physics": {
                    "mean": float(np.mean(differences)),
                    "bootstrap_ci95": bootstrap_ci(differences, seed + 90000 + shift_index),
                    "per_sample": differences.tolist(),
                },
                "communication": {
                    name: base.communication_metrics(prediction, eval_targets, snr_db=15.0, seed=seed + 100000)
                    for name, prediction in predictions.items()
                },
            }
        )
    return {
        "seed": seed,
        "source_validation_nmse": estimator.source_validation_nmse,
        "results": rows,
    }


def make_shifted_samples(count: int, seed: int, angle_shift: float, delay_scale: float):
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    pilots = np.eye(base.PILOT_COUNT, base.N_TX, dtype=np.complex128)
    for index in range(count):
        rng = np.random.default_rng(seed + index)
        channel = base.make_cascaded_channel(
            rng,
            n_subcarriers=base.N_SUBCARRIERS,
            n_tx=base.N_TX,
            n_ris=16,
            beam_squint=True,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        noise_power = np.mean(np.abs(channel) ** 2) / (10.0 ** (15.0 / 10.0))
        noise = rng.standard_normal((base.N_SUBCARRIERS, base.PILOT_COUNT)) + 1j * rng.standard_normal(
            (base.N_SUBCARRIERS, base.PILOT_COUNT)
        )
        observations = channel @ pilots.T + np.sqrt(noise_power / 2.0) * noise
        features.append(base.complex_features(observations))
        targets.append(base.complex_features(channel))
    return np.stack(features), np.stack(targets)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")
    seeds = (args.seed,) if args.seed is not None else SEEDS
    output = {
        "experiment": "cloud_ris_physics_preregistered_cpu",
        "device": str(device),
        "protocol": {
            "shifts": SHIFTS,
            "seeds": seeds,
            "support_samples": SUPPORT_COUNT,
            "evaluation_samples": EVAL_COUNT,
            "delay_modes": DELAY_MODES,
            "delay_weight": DELAY_WEIGHT,
            "prior_weight": PRIOR_WEIGHT,
            "adapt_steps": ADAPT_STEPS,
            "adapter_lr": ADAPTER_LR,
            "target_labels_used_for_adaptation": False,
        },
        "results": [run_seed(seed, device) for seed in seeds],
    }
    if args.seed is None:
        path = Path("experiments/cloud_ris_physics_preregistered_cpu_3seed_summary.json")
    else:
        path = Path(f"experiments/cloud_ris_physics_preregistered_cpu_seed{args.seed}.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
