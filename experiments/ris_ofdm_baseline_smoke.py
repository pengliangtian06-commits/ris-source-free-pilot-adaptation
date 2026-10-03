"""CPU smoke test for a sparse-pilot RIS-assisted wideband MIMO setup.

This is a feasibility check for data generation and metrics, not a paper result.
It deliberately uses NumPy only so it can run before a PyTorch/cloud-GPU setup.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def make_wideband_channel(
    *,
    rng: np.random.Generator,
    n_subcarriers: int,
    n_rx: int,
    n_tx: int,
    n_paths: int,
    max_delay: float = 0.35,
) -> np.ndarray:
    """Generate a small frequency-selective effective RIS channel."""
    delays = rng.uniform(0.0, max_delay, size=n_paths)
    gains = (rng.standard_normal(n_paths) + 1j * rng.standard_normal(n_paths))
    gains /= np.sqrt(2.0 * n_paths)
    spatial_rx = rng.standard_normal((n_paths, n_rx)) + 1j * rng.standard_normal(
        (n_paths, n_rx)
    )
    spatial_tx = rng.standard_normal((n_paths, n_tx)) + 1j * rng.standard_normal(
        (n_paths, n_tx)
    )
    spatial_rx /= np.sqrt(2.0)
    spatial_tx /= np.sqrt(2.0)

    frequencies = np.linspace(-0.5, 0.5, n_subcarriers, endpoint=False)
    channel = np.zeros((n_subcarriers, n_rx, n_tx), dtype=np.complex128)
    for k, frequency in enumerate(frequencies):
        phase = np.exp(-2j * np.pi * frequency * delays)
        for path in range(n_paths):
            channel[k] += (
                gains[path]
                * phase[path]
                * np.outer(spatial_rx[path], np.conj(spatial_tx[path]))
            )
    return channel


def add_awgn(signal: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    power = np.mean(np.abs(signal) ** 2)
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.standard_normal(signal.shape) + 1j * rng.standard_normal(signal.shape)
    return signal + np.sqrt(noise_power / 2.0) * noise


def nmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(np.sum(np.abs(estimate - truth) ** 2) / np.sum(np.abs(truth) ** 2))


def run_once(seed: int, pilot_count: int, snr_db: float) -> float:
    rng = np.random.default_rng(seed)
    n_subcarriers, n_rx, n_tx = 16, 2, 4
    truth = make_wideband_channel(
        rng=rng,
        n_subcarriers=n_subcarriers,
        n_rx=n_rx,
        n_tx=n_tx,
        n_paths=3,
    )

    # Orthogonal pilot rows. pilot_count controls the observation budget.
    pilots = np.eye(pilot_count, n_tx, dtype=np.complex128)
    observations = np.einsum("pt,ktr->kpr", pilots, truth.transpose(0, 2, 1))
    observations = add_awgn(observations, snr_db, rng)

    # Least-squares reconstruction; underdetermined pilot regimes are explicit.
    estimate = np.zeros_like(truth)
    pseudo_inverse = np.linalg.pinv(pilots)
    for k in range(n_subcarriers):
        y = observations[k]
        estimate[k] = (pseudo_inverse @ y).T
    return nmse(estimate, truth)


def main() -> None:
    results = []
    for pilot_count in (2, 3, 4):
        values = [run_once(seed, pilot_count, snr_db=15.0) for seed in range(10)]
        results.append(
            {
                "pilot_count": pilot_count,
                "snr_db": 15.0,
                "nmse_mean": float(np.mean(values)),
                "nmse_std": float(np.std(values)),
            }
        )
    output = {"experiment": "ris_ofdm_sparse_pilot_ls_smoke", "results": results}
    print(json.dumps(output, indent=2))

    artifact = Path("experiments") / "ris_ofdm_baseline_smoke_results.json"
    artifact.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
