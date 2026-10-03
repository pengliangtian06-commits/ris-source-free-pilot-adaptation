"""Sanity check for an explicit wideband BS-RIS-UE channel generator.

This is the validity gate for the earlier generic wideband-MIMO proxy.  It
contains a frequency-selective BS-to-RIS hop, a RIS-to-UE hop, fixed RIS
reflection phases, and an optional beam-squint term in the array responses.
It intentionally reports only LS NMSE; learning experiments come later.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def steering(count: int, angle: float, frequency: float, beam_squint: bool) -> np.ndarray:
    spacing_scale = 1.0 + frequency if beam_squint else 1.0
    indices = np.arange(count)
    return np.exp(2j * np.pi * spacing_scale * indices * np.sin(angle)) / np.sqrt(count)


def cascaded_hop(
    ue_hop: np.ndarray, reflection: np.ndarray, bs_hop: np.ndarray
) -> np.ndarray:
    """Apply the explicit row-vector RIS cascade used by the simulator.

    ``ue_hop`` is represented as a length-``N_r`` column-vector quantity in
    the model description, so the implemented contraction is its transpose
    (without conjugation) followed by the diagonal reflection matrix and the
    BS-to-RIS matrix.
    """
    return ue_hop.T @ np.diag(reflection) @ bs_hop


def make_cascaded_channel(
    rng: np.random.Generator,
    *,
    n_subcarriers: int = 16,
    n_tx: int = 4,
    n_ris: int = 16,
    n_bs_paths: int = 3,
    n_ue_paths: int = 2,
    beam_squint: bool = True,
    angle_shift: float = 0.0,
    delay_scale: float = 1.0,
) -> np.ndarray:
    frequencies = np.linspace(-0.5, 0.5, n_subcarriers, endpoint=False)
    bs_delays = delay_scale * rng.uniform(0.0, 0.25, size=n_bs_paths)
    ue_delays = delay_scale * rng.uniform(0.0, 0.20, size=n_ue_paths)
    bs_gains = (rng.standard_normal(n_bs_paths) + 1j * rng.standard_normal(n_bs_paths))
    ue_gains = (rng.standard_normal(n_ue_paths) + 1j * rng.standard_normal(n_ue_paths))
    bs_gains /= np.sqrt(2.0 * n_bs_paths)
    ue_gains /= np.sqrt(2.0 * n_ue_paths)
    bs_angles = rng.uniform(-0.45, 0.45, size=(n_bs_paths, 2)) + angle_shift
    ue_angles = rng.uniform(-0.45, 0.45, size=n_ue_paths) + angle_shift
    reflection = np.exp(1j * rng.uniform(-np.pi, np.pi, size=n_ris))

    channel = np.zeros((n_subcarriers, n_tx), dtype=np.complex128)
    for k, frequency in enumerate(frequencies):
        bs_hop = np.zeros((n_ris, n_tx), dtype=np.complex128)
        for path in range(n_bs_paths):
            ris_response = steering(n_ris, bs_angles[path, 0], frequency, beam_squint)
            bs_response = steering(n_tx, bs_angles[path, 1], frequency, beam_squint)
            bs_hop += (
                bs_gains[path]
                * np.exp(-2j * np.pi * frequency * bs_delays[path])
                * np.outer(ris_response, np.conj(bs_response))
            )

        ue_hop = np.zeros(n_ris, dtype=np.complex128)
        for path in range(n_ue_paths):
            ris_response = steering(n_ris, ue_angles[path], frequency, beam_squint)
            ue_hop += (
                ue_gains[path]
                * np.exp(-2j * np.pi * frequency * ue_delays[path])
                * ris_response
            )
        channel[k] = cascaded_hop(ue_hop, reflection, bs_hop)

    return channel


def add_noise(signal: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    power = np.mean(np.abs(signal) ** 2)
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.standard_normal(signal.shape) + 1j * rng.standard_normal(signal.shape)
    return signal + np.sqrt(noise_power / 2.0) * noise


def nmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(np.sum(np.abs(estimate - truth) ** 2) / np.sum(np.abs(truth) ** 2))


def run_once(seed: int, pilot_count: int, beam_squint: bool) -> float:
    rng = np.random.default_rng(seed)
    truth = make_cascaded_channel(rng, beam_squint=beam_squint)
    pilots = np.eye(pilot_count, truth.shape[1], dtype=np.complex128)
    observations = add_noise(truth @ pilots.T, 15.0, rng)
    estimate = observations @ np.linalg.pinv(pilots).T
    return nmse(estimate, truth)


def main() -> None:
    results = []
    for beam_squint in (False, True):
        for pilot_count in (2, 3, 4):
            values = [run_once(seed, pilot_count, beam_squint) for seed in range(20)]
            results.append(
                {
                    "beam_squint": beam_squint,
                    "pilot_count": pilot_count,
                    "snr_db": 15.0,
                    "nmse_mean": float(np.mean(values)),
                    "nmse_std": float(np.std(values, ddof=1)),
                }
            )
    output = {
        "experiment": "ris_explicit_bs_ris_ue_generator_smoke",
        "config": {
            "subcarriers": 16,
            "tx_antennas": 4,
            "ris_elements": 16,
            "bs_paths": 3,
            "ue_paths": 2,
            "seeds": 20,
        },
        "results": results,
    }
    print(json.dumps(output, indent=2))
    Path(__file__).resolve().parent.joinpath("ris_cascaded_generator_smoke_results.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
