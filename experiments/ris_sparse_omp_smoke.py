"""CPU smoke test for sparse dictionary channel estimation.

The goal is to validate an OMP baseline before any neural model is trained.
It uses a small complex overcomplete spatial dictionary and keeps all random
seeds/configuration values in the output artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def complex_omp(dictionary: np.ndarray, observation: np.ndarray, sparsity: int) -> np.ndarray:
    """Recover a sparse complex coefficient vector by greedy OMP."""
    residual = observation.copy()
    support: list[int] = []
    coefficients = np.zeros(dictionary.shape[1], dtype=np.complex128)
    for _ in range(sparsity):
        correlations = np.abs(dictionary.conj().T @ residual)
        correlations[support] = -np.inf
        support.append(int(np.argmax(correlations)))
        active = dictionary[:, support]
        active_coefficients, *_ = np.linalg.lstsq(active, observation, rcond=None)
        residual = observation - active @ active_coefficients
    coefficients[support] = active_coefficients
    return coefficients


def make_sparse_channel(
    rng: np.random.Generator,
    n_subcarriers: int,
    n_tx: int,
    n_atoms: int,
    n_paths: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a frequency-selective sparse channel and its dictionary."""
    angles = np.linspace(-0.5, 0.5, n_atoms, endpoint=False)
    antenna_index = np.arange(n_tx)
    dictionary = np.exp(2j * np.pi * np.outer(antenna_index, angles)) / np.sqrt(n_tx)
    support = rng.choice(n_atoms, size=n_paths, replace=False)
    base_coefficients = (
        rng.standard_normal(n_paths) + 1j * rng.standard_normal(n_paths)
    ) / np.sqrt(2.0 * n_paths)
    delays = rng.uniform(0.0, 0.4, size=n_paths)
    frequencies = np.linspace(-0.5, 0.5, n_subcarriers, endpoint=False)
    channel = np.zeros((n_subcarriers, n_tx), dtype=np.complex128)
    for k, frequency in enumerate(frequencies):
        coefficients = base_coefficients * np.exp(-2j * np.pi * frequency * delays)
        channel[k] = dictionary[:, support] @ coefficients
    return channel, dictionary


def add_awgn(signal: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    power = np.mean(np.abs(signal) ** 2)
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.standard_normal(signal.shape) + 1j * rng.standard_normal(signal.shape)
    return signal + np.sqrt(noise_power / 2.0) * noise


def nmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(np.sum(np.abs(estimate - truth) ** 2) / np.sum(np.abs(truth) ** 2))


def run_once(seed: int, pilot_count: int, snr_db: float) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n_subcarriers, n_tx, n_atoms, n_paths = 16, 8, 16, 3
    truth, dictionary = make_sparse_channel(
        rng, n_subcarriers, n_tx, n_atoms, n_paths
    )
    pilots = np.eye(pilot_count, n_tx, dtype=np.complex128)
    observations = truth @ pilots.T
    observations = add_awgn(observations, snr_db, rng)
    ls_estimate = observations @ np.linalg.pinv(pilots).T
    omp_estimate = np.zeros_like(truth)
    sensing_dictionary = pilots @ dictionary
    for k in range(n_subcarriers):
        sparse_coefficients = complex_omp(
            sensing_dictionary, observations[k], sparsity=n_paths
        )
        omp_estimate[k] = dictionary @ sparse_coefficients
    return nmse(ls_estimate, truth), nmse(omp_estimate, truth)


def main() -> None:
    results = []
    for pilot_count in (2, 3, 4, 5, 6):
        ls_values, omp_values = zip(
            *(run_once(seed, pilot_count, snr_db=15.0) for seed in range(20))
        )
        results.append(
            {
                "pilot_count": pilot_count,
                "snr_db": 15.0,
                "ls_nmse_mean": float(np.mean(ls_values)),
                "ls_nmse_std": float(np.std(ls_values)),
                "omp_nmse_mean": float(np.mean(omp_values)),
                "omp_nmse_std": float(np.std(omp_values)),
            }
        )
    output = {
        "experiment": "ris_sparse_dictionary_ls_vs_omp_smoke",
        "config": {"subcarriers": 16, "tx_antennas": 8, "dictionary_atoms": 16, "paths": 3},
        "results": results,
    }
    print(json.dumps(output, indent=2))
    artifact = Path("experiments") / "ris_sparse_omp_smoke_results.json"
    artifact.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
