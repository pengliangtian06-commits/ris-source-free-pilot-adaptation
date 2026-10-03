"""Explicit-RIS LS and fixed-dictionary OMP baseline.

The cascaded BS--RIS--UE generator produces a BS-side channel that is a
frequency-dependent sparse combination of transmit-array responses.  This
script evaluates a fixed spatial dictionary on the same explicit generator as
the learned estimator.  It is a classical reference and pilot-budget
sensitivity experiment, not an adapted method.  Target CSI is used only to
score the estimates.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ris_cascaded_generator_smoke import make_cascaded_channel, steering


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "ris_explicit_omp_baseline_results.json"
SEEDS = (20261002, 20261003, 20261004)
SHIFTS = ((0.04, 1.2), (0.08, 1.4), (0.12, 1.6), (0.18, 2.0))
N_SUBCARRIERS = 16
N_TX = 4
N_RIS = 16
SNR_DB = 15.0
SAMPLES_PER_SEED = 512
ANGLE_GRID_SIZE = 64
SPARSITY = 3


def complex_omp(dictionary: np.ndarray, observation: np.ndarray, sparsity: int) -> np.ndarray:
    """Recover a sparse complex coefficient vector by greedy OMP."""
    residual = observation.copy()
    support: list[int] = []
    coefficients = np.zeros(dictionary.shape[1], dtype=np.complex128)
    for _ in range(sparsity):
        correlations = np.abs(dictionary.conj().T @ residual)
        if support:
            correlations[support] = -np.inf
        support.append(int(np.argmax(correlations)))
        active = dictionary[:, support]
        active_coefficients, *_ = np.linalg.lstsq(active, observation, rcond=None)
        residual = observation - active @ active_coefficients
    coefficients[support] = active_coefficients
    return coefficients


def nmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    denominator = np.sum(np.abs(truth) ** 2)
    return float(np.sum(np.abs(estimate - truth) ** 2) / max(denominator, 1e-12))


def add_awgn(signal: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    power = np.mean(np.abs(signal) ** 2)
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.standard_normal(signal.shape) + 1j * rng.standard_normal(signal.shape)
    return signal + np.sqrt(noise_power / 2.0) * noise


def make_dictionary(*, beam_squint: bool) -> np.ndarray:
    angles = np.linspace(-0.5, 0.5, ANGLE_GRID_SIZE, endpoint=False)
    frequencies = np.linspace(-0.5, 0.5, N_SUBCARRIERS, endpoint=False)
    # Rows are transmit antennas and columns are candidate BS steering atoms.
    return np.stack(
        [
            np.stack(
                [np.conj(steering(N_TX, angle, frequency, beam_squint)) for angle in angles],
                axis=1,
            )
            for frequency in frequencies
        ],
        axis=0,
    )


def estimate_pair(
    channel: np.ndarray,
    *,
    pilot_count: int,
    dictionary: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, float]:
    pilots = np.eye(pilot_count, N_TX, dtype=np.complex128)
    observations = add_awgn(channel @ pilots.T, SNR_DB, rng)

    ls = np.zeros_like(channel)
    ls[:, :pilot_count] = observations

    omp = np.zeros_like(channel)
    for subcarrier in range(N_SUBCARRIERS):
        sensing = pilots @ dictionary[subcarrier]
        coefficients = complex_omp(sensing, observations[subcarrier], SPARSITY)
        omp[subcarrier] = dictionary[subcarrier] @ coefficients
    return nmse(ls, channel), nmse(omp, channel)


def run() -> dict:
    rows: list[dict] = []
    for angle_shift, delay_scale in SHIFTS:
        for pilot_count in (2, 4):
            seed_rows: list[dict] = []
            for seed in SEEDS:
                rng = np.random.default_rng(seed + int(angle_shift * 1000) + pilot_count)
                dictionary = make_dictionary(beam_squint=True)
                ls_values: list[float] = []
                omp_values: list[float] = []
                for index in range(SAMPLES_PER_SEED):
                    channel_rng = np.random.default_rng(seed * 100000 + index)
                    channel = make_cascaded_channel(
                        channel_rng,
                        n_subcarriers=N_SUBCARRIERS,
                        n_tx=N_TX,
                        n_ris=N_RIS,
                        beam_squint=True,
                        angle_shift=angle_shift,
                        delay_scale=delay_scale,
                    )
                    ls_value, omp_value = estimate_pair(
                        channel,
                        pilot_count=pilot_count,
                        dictionary=dictionary,
                        rng=rng,
                    )
                    ls_values.append(ls_value)
                    omp_values.append(omp_value)
                seed_rows.append(
                    {
                        "seed": seed,
                        "ls_nmse_mean": float(np.mean(ls_values)),
                        "ls_nmse_sd": float(np.std(ls_values, ddof=1)),
                        "omp_nmse_mean": float(np.mean(omp_values)),
                        "omp_nmse_sd": float(np.std(omp_values, ddof=1)),
                    }
                )
            rows.append(
                {
                    "angle_shift": angle_shift,
                    "delay_scale": delay_scale,
                    "pilot_count": pilot_count,
                    "snr_db": SNR_DB,
                    "seed_results": seed_rows,
                    "ls_nmse_mean": float(np.mean([row["ls_nmse_mean"] for row in seed_rows])),
                    "ls_nmse_sd_across_seeds": float(np.std([row["ls_nmse_mean"] for row in seed_rows], ddof=1)),
                    "omp_nmse_mean": float(np.mean([row["omp_nmse_mean"] for row in seed_rows])),
                    "omp_nmse_sd_across_seeds": float(np.std([row["omp_nmse_mean"] for row in seed_rows], ddof=1)),
                }
            )
    return {
        "experiment": "explicit_ris_ls_vs_fixed_dictionary_omp",
        "device": "cpu",
        "seeds": list(SEEDS),
        "target_labels_used_for_adaptation": False,
        "config": {
            "subcarriers": N_SUBCARRIERS,
            "tx_antennas": N_TX,
            "ris_elements": N_RIS,
            "snr_db": SNR_DB,
            "samples_per_seed": SAMPLES_PER_SEED,
            "angle_grid_size": ANGLE_GRID_SIZE,
            "omp_sparsity": SPARSITY,
            "beam_squint": True,
        },
        "results": rows,
    }


if __name__ == "__main__":
    result = run()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
