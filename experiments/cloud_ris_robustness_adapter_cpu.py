"""Fixed-input neural robustness study for explicit RIS target scenarios.

The source estimator is trained once at 16 RIS elements, beam squint enabled,
and 15 dB SNR with two pilots.  Target adaptation uses only an unlabeled
support block; a disjoint evaluation block is used for all reported metrics.
RIS size, beam-squint state, and SNR are varied while the model input/output
dimensions remain fixed.  Pilot-count robustness is intentionally excluded and
is reported by the LS-only factorial baseline.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from cloud_ris_adapter_lightning import (
    N_SUBCARRIERS,
    N_TX,
    PILOT_COUNT,
    LightweightAdapter,
    SourceEstimator,
    communication_metrics,
    complex_features,
    ls_estimate,
    nmse,
    physics_loss,
    unpack_complex,
)
from ris_cascaded_generator_smoke import make_cascaded_channel


SOURCE_RIS = 16
SOURCE_BEAM_SQUINT = True
SOURCE_SNR_DB = 15.0
RIS_SIZES = (8, 16, 32)
BEAM_SQUINTS = (False, True)
SNR_LEVELS = (5.0, 15.0, 25.0)
SOURCE_COUNT = 4096
SOURCE_VAL_COUNT = 512
SUPPORT_COUNT = 256
EVAL_COUNT = 512
EPOCHS = 12
BATCH_SIZE = 128
ADAPT_STEPS = 10
ADAPTER_LR = 1e-3
SMOOTH_WEIGHT = 0.003
PRIOR_WEIGHT = 0.1


def make_samples(
    count: int,
    *,
    seed: int,
    n_ris: int,
    beam_squint: bool,
    snr_db: float,
) -> tuple[np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    pilots = np.eye(PILOT_COUNT, N_TX, dtype=np.complex128)
    for index in range(count):
        rng = np.random.default_rng(seed + index)
        channel = make_cascaded_channel(
            rng,
            n_subcarriers=N_SUBCARRIERS,
            n_tx=N_TX,
            n_ris=n_ris,
            beam_squint=beam_squint,
        )
        noise_power = np.mean(np.abs(channel) ** 2) / (10.0 ** (snr_db / 10.0))
        noise = rng.standard_normal((N_SUBCARRIERS, PILOT_COUNT)) + 1j * rng.standard_normal(
            (N_SUBCARRIERS, PILOT_COUNT)
        )
        observations = channel @ pilots.T + np.sqrt(noise_power / 2.0) * noise
        features.append(complex_features(observations))
        targets.append(complex_features(channel))
    return np.stack(features), np.stack(targets)


def train_source(seed: int, device: torch.device) -> SourceEstimator:
    torch.manual_seed(seed)
    np.random.seed(seed)
    source_x, source_y = make_samples(
        SOURCE_COUNT, seed=seed, n_ris=SOURCE_RIS, beam_squint=SOURCE_BEAM_SQUINT, snr_db=SOURCE_SNR_DB
    )
    val_x, val_y = make_samples(
        SOURCE_VAL_COUNT,
        seed=seed + 10000,
        n_ris=SOURCE_RIS,
        beam_squint=SOURCE_BEAM_SQUINT,
        snr_db=SOURCE_SNR_DB,
    )
    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(source_x), torch.from_numpy(source_y)),
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    val_loader = DataLoader(TensorDataset(torch.from_numpy(val_x), torch.from_numpy(val_y)), batch_size=BATCH_SIZE)
    estimator = SourceEstimator().to(device)
    optimizer = torch.optim.AdamW(estimator.parameters(), lr=2e-3, weight_decay=1e-5)
    estimator.train()
    for _ in range(EPOCHS):
        for features, target in train_loader:
            features, target = features.to(device), target.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.mse_loss(estimator(features), target)
            loss.backward()
            optimizer.step()
    estimator.eval()
    with torch.no_grad():
        validation_values = []
        for features, target in val_loader:
            validation_values.append(nmse(estimator(features.to(device)).cpu(), target))
    estimator.source_validation_nmse = float(torch.cat(validation_values).mean())  # type: ignore[attr-defined]
    return estimator


def fit_adapter(
    estimator: SourceEstimator, support_features: torch.Tensor, device: torch.device
) -> LightweightAdapter:
    estimator.eval()
    adapter = LightweightAdapter().to(device)
    support_features = support_features.to(device)
    with torch.no_grad():
        frozen = estimator(support_features)
    optimizer = torch.optim.Adam(adapter.parameters(), lr=ADAPTER_LR)
    adapter.train()
    for _ in range(ADAPT_STEPS):
        optimizer.zero_grad(set_to_none=True)
        loss = physics_loss(
            adapter(frozen),
            support_features,
            smooth_weight=SMOOTH_WEIGHT,
            prior_weight=PRIOR_WEIGHT,
        )
        loss.backward()
        optimizer.step()
    return adapter.eval()


def bootstrap_ci(values: np.ndarray, seed: int, draws: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = np.empty(draws, dtype=np.float64)
    for index in range(draws):
        means[index] = np.mean(values[rng.integers(0, len(values), len(values))])
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def evaluate_cell(
    estimator: SourceEstimator,
    *,
    ris_size: int,
    beam_squint: bool,
    snr_db: float,
    seed: int,
    device: torch.device,
) -> dict[str, object]:
    support_x, _ = make_samples(
        SUPPORT_COUNT,
        seed=seed,
        n_ris=ris_size,
        beam_squint=beam_squint,
        snr_db=snr_db,
    )
    eval_x, eval_y = make_samples(
        EVAL_COUNT,
        seed=seed + 50000,
        n_ris=ris_size,
        beam_squint=beam_squint,
        snr_db=snr_db,
    )
    support_features = torch.from_numpy(support_x)
    eval_features = torch.from_numpy(eval_x)
    eval_targets = torch.from_numpy(eval_y)
    adapter = fit_adapter(estimator, support_features, device)
    with torch.no_grad():
        frozen_predictions = estimator(eval_features.to(device)).cpu()
        adapted_predictions = adapter(estimator(eval_features.to(device))).cpu()
        ls_predictions = ls_estimate(eval_features.to(device)).cpu()
    frozen_values = nmse(frozen_predictions, eval_targets).numpy()
    adapted_values = nmse(adapted_predictions, eval_targets).numpy()
    ls_values = nmse(ls_predictions, eval_targets).numpy()
    paired_diff = adapted_values - frozen_values
    ci_low, ci_high = bootstrap_ci(paired_diff, seed + 90000)
    try:
        from scipy.stats import wilcoxon

        p_value = float(wilcoxon(paired_diff, alternative="two-sided").pvalue)
    except Exception:
        p_value = None
    return {
        "ris_elements": ris_size,
        "beam_squint": beam_squint,
        "snr_db": snr_db,
        "support_samples": SUPPORT_COUNT,
        "evaluation_samples": EVAL_COUNT,
        "target_labels_used_for_adaptation": False,
        "nmse": {
            "ls_mean": float(np.mean(ls_values)),
            "frozen_mean": float(np.mean(frozen_values)),
            "adapted_mean": float(np.mean(adapted_values)),
            "adapted_minus_frozen_mean": float(np.mean(paired_diff)),
            "adapted_minus_frozen_bootstrap_ci95": [ci_low, ci_high],
            "adapted_vs_frozen_wilcoxon_p": p_value,
        },
        "communication": {
            "ls": communication_metrics(ls_predictions, eval_targets, snr_db=snr_db, seed=seed + 100000),
            "frozen": communication_metrics(frozen_predictions, eval_targets, snr_db=snr_db, seed=seed + 100000),
            "adapted": communication_metrics(adapted_predictions, eval_targets, snr_db=snr_db, seed=seed + 100000),
        },
        "adapter_parameters": sum(parameter.numel() for parameter in adapter.parameters()),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")
    started = time.perf_counter()
    estimator = train_source(args.seed, device)
    cells = list(itertools.product(RIS_SIZES, BEAM_SQUINTS, SNR_LEVELS))
    order_rng = np.random.default_rng(args.seed + 1)
    order_rng.shuffle(cells)
    results = [
        evaluate_cell(
            estimator,
            ris_size=ris_size,
            beam_squint=beam_squint,
            snr_db=snr_db,
            seed=args.seed + index * 1000,
            device=device,
        )
        for index, (ris_size, beam_squint, snr_db) in enumerate(cells)
    ]
    output = {
        "experiment": "cloud_ris_robustness_adapter_cpu",
        "device": str(device),
        "seed": args.seed,
        "design": "3x2x3 target full factorial; randomized cell order; fixed two-pilot input",
        "source_validation_nmse": estimator.source_validation_nmse,
        "source_config": {"ris_elements": SOURCE_RIS, "beam_squint": SOURCE_BEAM_SQUINT, "snr_db": SOURCE_SNR_DB},
        "target_config": {
            "ris_sizes": RIS_SIZES,
            "beam_squint": BEAM_SQUINTS,
            "snr_db": SNR_LEVELS,
            "pilot_count": PILOT_COUNT,
            "support_samples": SUPPORT_COUNT,
            "evaluation_samples": EVAL_COUNT,
        },
        "results": results,
        "adapter_parameters": sum(parameter.numel() for parameter in LightweightAdapter().parameters()),
        "elapsed_seconds": time.perf_counter() - started,
    }
    path = Path(__file__).resolve().parent / f"cloud_ris_robustness_adapter_cpu_seed{args.seed}.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
