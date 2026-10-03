"""CPU prototype of a physics-consistent, label-free online adapter.

The source model is trained only on source-domain CSI labels.  At target time,
the adapter sees noisy pilots and a known pilot operator, then selects a
low-dimensional correction from candidates that combine:

* measurement consistency on the observed pilot antennas; and
* wideband frequency consistency implemented as a low-delay Fourier filter.

The target CSI is used only for evaluation.  This is a deliberately small
NumPy/scikit-learn gate for the later PyTorch experiment, not a paper result.
Its current generator is a generic frequency-selective MIMO proxy; a true
BS-RIS-UE cascade must replace it before making RIS-specific claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats
from sklearn.compose import TransformedTargetRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ris_data_consistency_adapter_smoke import project_prediction
from ris_mlp_supervised_smoke import nmse_from_flat, sample


N_SUBCARRIERS = 8
N_TX = 4
PILOT_COUNT = 2
TARGET_SIZE = 100


def make_model(x_train: np.ndarray, y_train: np.ndarray) -> TransformedTargetRegressor:
    """Train the same frozen source model used by the earlier smoke tests."""
    model = TransformedTargetRegressor(
        regressor=Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "mlp",
                    MLPRegressor(
                        hidden_layer_sizes=(128, 64),
                        activation="relu",
                        max_iter=350,
                        early_stopping=True,
                        validation_fraction=0.15,
                        random_state=7,
                    ),
                ),
            ]
        ),
        transformer=StandardScaler(),
    )
    model.fit(x_train, y_train)
    return model


def unpack_channel(flat: np.ndarray) -> np.ndarray:
    half = flat.size // 2
    return (flat[:half] + 1j * flat[half:]).reshape(N_SUBCARRIERS, N_TX)


def unpack_observation(flat: np.ndarray) -> np.ndarray:
    half = flat.size // 2
    return (flat[:half] + 1j * flat[half:]).reshape(N_SUBCARRIERS, PILOT_COUNT)


def pack_channel(channel: np.ndarray) -> np.ndarray:
    return np.concatenate([channel.real.ravel(), channel.imag.ravel()])


def low_delay_filter(channel: np.ndarray, keep_modes: int) -> np.ndarray:
    """Keep low-delay Fourier modes across subcarriers.

    The generator is frequency selective but smooth in frequency.  Truncating
    the delay-domain representation is therefore a compact physics prior.
    """
    spectrum = np.fft.fft(channel, axis=0)
    # ``keep_modes`` is the *total* number of retained modes.  Keeping a
    # half-width here would accidentally retain 2*keep_modes-1 modes and make
    # the filter an identity when keep_modes is near N_SUBCARRIERS.
    mask = np.zeros(N_SUBCARRIERS, dtype=bool)
    positive_count = (keep_modes + 1) // 2
    negative_count = keep_modes // 2
    mask[:positive_count] = True
    if negative_count:
        mask[-negative_count:] = True
    spectrum[~mask] = 0.0
    return np.fft.ifft(spectrum, axis=0)


def fixed_projection(prediction: np.ndarray, feature: np.ndarray) -> np.ndarray:
    return project_prediction(
        prediction,
        feature,
        PILOT_COUNT,
        N_SUBCARRIERS,
        N_TX,
        regularization=0.1,
    )


def adapt_without_wideband_prior(
    prediction: np.ndarray,
    feature: np.ndarray,
    *,
    blend_grid: tuple[float, ...] = tuple(np.linspace(0.0, 1.0, 11)),
    regularization: float = 0.1,
) -> np.ndarray:
    """Measurement-consistency-only control with the same blend budget."""
    frozen = unpack_channel(prediction)
    projected = unpack_channel(fixed_projection(prediction, feature))
    observation = unpack_observation(feature)
    best: tuple[float, np.ndarray] | None = None
    for blend in blend_grid:
        candidate = (1.0 - blend) * frozen + blend * projected
        objective = np.mean(np.abs(candidate[:, :PILOT_COUNT] - observation) ** 2)
        objective += 1.0 * blend * blend * np.mean(np.abs(projected - frozen) ** 2)
        if best is None or objective < best[0]:
            best = (float(objective), candidate)
    assert best is not None
    return pack_channel(best[1])


def adapt_online(
    prediction: np.ndarray,
    feature: np.ndarray,
    *,
    keep_modes_grid: tuple[int, ...] = (1, 3, 5),
    blend_grid: tuple[float, ...] = tuple(np.linspace(0.0, 1.0, 11)),
    regularization: float = 0.1,
) -> tuple[np.ndarray, dict[str, float]]:
    """Select a correction using pilots only.

    The objective is the observed-pilot residual plus a small penalty on the
    correction magnitude.  No target CSI enters either selection or output.
    """
    frozen = unpack_channel(prediction)
    projected = unpack_channel(
        project_prediction(
            prediction,
            feature,
            PILOT_COUNT,
            N_SUBCARRIERS,
            N_TX,
            regularization,
        )
    )
    observation = unpack_observation(feature)

    best: tuple[float, np.ndarray, float, int] | None = None
    for keep_modes in keep_modes_grid:
        smoothed = low_delay_filter(projected, keep_modes)
        for blend in blend_grid:
            candidate = (1.0 - blend) * frozen + blend * smoothed
            pilot_residual = np.mean(np.abs(candidate[:, :PILOT_COUNT] - observation) ** 2)
            # Scale the prior at the same order as the pilot residual.  A much
            # weaker penalty collapses to the fixed projection control.
            correction_penalty = 1.0 * blend * blend * np.mean(
                np.abs(smoothed - frozen) ** 2
            )
            objective = float(pilot_residual + correction_penalty)
            item = (objective, candidate, blend, keep_modes)
            if best is None or objective < best[0]:
                best = item

    assert best is not None
    objective, candidate, blend, keep_modes = best
    metadata = {
        "self_supervised_objective": float(objective),
        "selected_blend": float(blend),
        "selected_keep_modes": int(keep_modes),
    }
    return pack_channel(candidate), metadata


def bootstrap_ci(values: np.ndarray, *, seed: int = 20261002, draws: int = 5000) -> list[float]:
    """Percentile bootstrap CI for a paired mean difference."""
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(draws, values.size))
    means = values[indices].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def paired_summary(differences: np.ndarray) -> dict[str, float | list[float]]:
    """Report paired effect, bootstrap uncertainty, and a non-parametric test."""
    wilcoxon = stats.wilcoxon(differences, alternative="two-sided", method="auto")
    return {
        "mean_difference": float(np.mean(differences)),
        "median_difference": float(np.median(differences)),
        "std_difference": float(np.std(differences, ddof=1)),
        "bootstrap_ci95": bootstrap_ci(differences),
        "wilcoxon_statistic": float(wilcoxon.statistic),
        "wilcoxon_p_value": float(wilcoxon.pvalue),
    }


def evaluate_shift(model: TransformedTargetRegressor, angle_shift: float, delay_max: float) -> dict:
    target = [
        sample(seed + 3000, delay_max=delay_max, angle_shift=angle_shift)
        for seed in range(TARGET_SIZE)
    ]
    features = np.stack([row[0] for row in target])
    predictions = model.predict(features)

    frozen_values: list[float] = []
    projection_values: list[float] = []
    adapted_values: list[float] = []
    no_physics_values: list[float] = []
    ls_values: list[float] = []
    selected_blends: list[float] = []
    selected_modes: list[int] = []
    for prediction, row in zip(predictions, target):
        adapted, metadata = adapt_online(prediction, row[0])
        frozen_values.append(nmse_from_flat(prediction, row[1]))
        projection_values.append(nmse_from_flat(fixed_projection(prediction, row[0]), row[1]))
        adapted_values.append(nmse_from_flat(adapted, row[1]))
        no_physics_values.append(
            nmse_from_flat(adapt_without_wideband_prior(prediction, row[0]), row[1])
        )
        ls_values.append(nmse_from_flat(row[2], row[1]))
        selected_blends.append(metadata["selected_blend"])
        selected_modes.append(int(metadata["selected_keep_modes"]))

    adapted_array = np.asarray(adapted_values)
    no_physics_array = np.asarray(no_physics_values)
    frozen_array = np.asarray(frozen_values)
    projection_array = np.asarray(projection_values)
    ls_array = np.asarray(ls_values)
    return {
        "angle_shift": angle_shift,
        "delay_max": delay_max,
        "sample_count": TARGET_SIZE,
        "nmse_mean": {
            "ls": float(ls_array.mean()),
            "frozen_mlp": float(frozen_array.mean()),
            "fixed_projection": float(projection_array.mean()),
            "physics_consistent_adapter": float(adapted_array.mean()),
            "no_wideband_prior_control": float(no_physics_array.mean()),
        },
        "nmse_std": {
            "ls": float(ls_array.std(ddof=1)),
            "frozen_mlp": float(frozen_array.std(ddof=1)),
            "fixed_projection": float(projection_array.std(ddof=1)),
            "physics_consistent_adapter": float(adapted_array.std(ddof=1)),
            "no_wideband_prior_control": float(no_physics_array.std(ddof=1)),
        },
        "paired_difference_adapter_minus_frozen": paired_summary(adapted_array - frozen_array),
        "paired_difference_adapter_minus_ls": paired_summary(adapted_array - ls_array),
        "paired_difference_adapter_minus_no_wideband_prior": paired_summary(
            adapted_array - no_physics_array
        ),
        "selected_blend_mean": float(np.mean(selected_blends)),
        "selected_keep_modes_mean": float(np.mean(selected_modes)),
    }


def main() -> None:
    train = [sample(seed, delay_max=0.20, angle_shift=0.0) for seed in range(2000)]
    model = make_model(
        np.stack([row[0] for row in train]),
        np.stack([row[1] for row in train]),
    )
    settings = ((0.0, 0.20), (0.04, 0.25), (0.08, 0.30), (0.12, 0.40), (0.18, 0.50))
    results = [evaluate_shift(model, angle, delay) for angle, delay in settings]
    output = {
        "experiment": "ris_physics_consistent_online_adapter_smoke",
        "protocol": {
            "source_train_samples": 2000,
            "target_samples_per_shift": TARGET_SIZE,
            "pilot_count": PILOT_COUNT,
            "snr_db": 15.0,
            "target_labels_used_for_adaptation": False,
            "adapter_objective": "pilot residual + low-delay consistency correction penalty",
            "bootstrap_draws": 5000,
        },
        "results": results,
    }
    print(json.dumps(output, indent=2))
    artifact = Path(__file__).resolve().parent / "ris_physics_consistent_adapter_smoke_results.json"
    artifact.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
