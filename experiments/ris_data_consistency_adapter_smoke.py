"""CPU smoke test for a label-free data-consistency adapter.

The adapter applies a proximal projection using the known pilot operator to a
frozen supervised estimator. It is a transparent control for the planned
physics-consistent online adaptation, not the final neural method.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.compose import TransformedTargetRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ris_mlp_supervised_smoke import nmse_from_flat, sample


def make_model(x_train: np.ndarray, y_train: np.ndarray) -> TransformedTargetRegressor:
    model = TransformedTargetRegressor(
        regressor=Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "mlp",
                    MLPRegressor(
                        hidden_layer_sizes=(128, 64),
                        activation="relu",
                        solver="adam",
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


def project_prediction(
    prediction: np.ndarray,
    feature: np.ndarray,
    pilot_count: int,
    n_subcarriers: int,
    n_tx: int,
    regularization: float,
) -> np.ndarray:
    half = feature.size // 2
    observations = (feature[:half] + 1j * feature[half:]).reshape(
        n_subcarriers, pilot_count
    )
    pred_half = prediction.size // 2
    estimate = (prediction[:pred_half] + 1j * prediction[pred_half:]).reshape(
        n_subcarriers, n_tx
    )
    pilots = np.eye(pilot_count, n_tx, dtype=np.complex128)
    gram_inverse = np.linalg.inv(pilots @ pilots.conj().T + regularization * np.eye(pilot_count))
    for k in range(n_subcarriers):
        residual = observations[k] - pilots @ estimate[k]
        estimate[k] += pilots.conj().T @ gram_inverse @ residual
    return np.concatenate([estimate.real.ravel(), estimate.imag.ravel()])


def main() -> None:
    n_subcarriers, n_tx, pilot_count = 8, 4, 2
    train = [sample(seed, delay_max=0.20, angle_shift=0.0) for seed in range(2000)]
    target = [sample(seed + 2000, delay_max=0.40, angle_shift=0.12) for seed in range(100)]
    x_train = np.stack([row[0] for row in train])
    y_train = np.stack([row[1] for row in train])
    model = make_model(x_train, y_train)
    predictions = model.predict(np.stack([row[0] for row in target]))

    results = []
    for regularization in (0.0, 0.01, 0.1, 1.0):
        adapted = [
            project_prediction(
                pred,
                row[0],
                pilot_count,
                n_subcarriers,
                n_tx,
                regularization,
            )
            for pred, row in zip(predictions, target)
        ]
        values = [nmse_from_flat(pred, row[1]) for pred, row in zip(adapted, target)]
        frozen_values = [nmse_from_flat(pred, row[1]) for pred, row in zip(predictions, target)]
        ls_values = [nmse_from_flat(row[2], row[1]) for row in target]
        results.append(
            {
                "regularization": regularization,
                "frozen_mlp_nmse_mean": float(np.mean(frozen_values)),
                "projected_nmse_mean": float(np.mean(values)),
                "projected_nmse_std": float(np.std(values)),
                "ls_nmse_mean": float(np.mean(ls_values)),
            }
        )
    output = {
        "experiment": "ris_label_free_data_consistency_adapter_smoke",
        "config": {"train_samples": 2000, "target_samples": 100, "pilot_count": pilot_count, "snr_db": 15.0},
        "results": results,
    }
    print(json.dumps(output, indent=2))
    artifact = Path(__file__).resolve().parent / "ris_data_consistency_adapter_smoke_results.json"
    artifact.write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
