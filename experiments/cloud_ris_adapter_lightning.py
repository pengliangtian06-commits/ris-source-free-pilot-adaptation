"""Cloud-GPU entry point for R003-R006.

The script uses the explicit BS-RIS-UE generator from
``ris_cascaded_generator_smoke.py``.  It pretrains a compact source-domain
estimator with Lightning, then performs target-time updates on a small adapter
using only received pilots.  Target CSI is retained solely for evaluation.

Example (Colab/Kaggle after installing requirements-cloud.txt):
    python experiments/cloud_ris_adapter_lightning.py --mode smoke --device auto
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

import lightning as L

from ris_cascaded_generator_smoke import make_cascaded_channel


N_SUBCARRIERS = 16
N_TX = 4
N_RIS = 16
PILOT_COUNT = 2
SOURCE_DELAY_SCALE = 1.0
TARGET_DELAY_SCALE = 1.6
TARGET_ANGLE_SHIFT = 0.12


def complex_features(value: np.ndarray) -> np.ndarray:
    return np.concatenate([value.real.reshape(-1), value.imag.reshape(-1)]).astype(np.float32)


def make_samples(
    count: int,
    *,
    seed: int,
    beam_squint: bool,
    angle_shift: float,
    delay_scale: float,
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
            n_ris=N_RIS,
            beam_squint=beam_squint,
            angle_shift=angle_shift,
            delay_scale=delay_scale,
        )
        noise_power = np.mean(np.abs(channel) ** 2) / (10.0 ** (15.0 / 10.0))
        noise = rng.standard_normal((N_SUBCARRIERS, PILOT_COUNT)) + 1j * rng.standard_normal(
            (N_SUBCARRIERS, PILOT_COUNT)
        )
        observations = channel @ pilots.T + np.sqrt(noise_power / 2.0) * noise
        features.append(complex_features(observations))
        targets.append(complex_features(channel))
    return np.stack(features), np.stack(targets)


def unpack_complex(value: torch.Tensor, width: int) -> torch.Tensor:
    half = value.shape[-1] // 2
    return torch.complex(value[..., :half], value[..., half:]).reshape(
        value.shape[0], N_SUBCARRIERS, width
    )


def pack_complex(value: torch.Tensor) -> torch.Tensor:
    return torch.cat([value.real.reshape(value.shape[0], -1), value.imag.reshape(value.shape[0], -1)], dim=-1)


def nmse(prediction: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return torch.sum((prediction - target).square(), dim=-1) / torch.sum(target.square(), dim=-1).clamp_min(1e-8)


@torch.no_grad()
def ls_estimate(features: torch.Tensor) -> torch.Tensor:
    """Identity-pilot LS baseline with zeros for unobserved antennas."""
    observation = unpack_complex(features, PILOT_COUNT)
    estimate = torch.zeros(
        observation.shape[0], N_SUBCARRIERS, N_TX, dtype=observation.dtype, device=observation.device
    )
    estimate[..., :PILOT_COUNT] = observation
    return pack_complex(estimate)


class SourceEstimator(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        input_dim = 2 * N_SUBCARRIERS * PILOT_COUNT
        output_dim = 2 * N_SUBCARRIERS * N_TX
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.GELU(),
            nn.Linear(256, 256),
            nn.GELU(),
            nn.Linear(256, output_dim),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.net(features)


class SourceLightningModule(L.LightningModule):
    def __init__(self, learning_rate: float = 2e-3) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.estimator = SourceEstimator()

    def training_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:
        features, target = batch
        loss = nn.functional.mse_loss(self.estimator(features), target)
        self.log("train_mse", loss, prog_bar=True)
        return loss

    def validation_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> None:
        features, target = batch
        loss = nn.functional.mse_loss(self.estimator(features), target)
        self.log("val_mse", loss, prog_bar=True)

    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.hparams.learning_rate, weight_decay=1e-5)


def prepare_estimator(estimator: SourceEstimator, device: torch.device) -> SourceEstimator:
    """Keep the estimator and evaluation batches on the same device.

    Lightning may restore a module to CPU after ``Trainer.fit`` completes,
    even when the trainer used a CUDA accelerator.  The downstream evaluation
    code owns the requested device, so make that placement explicit here.
    """
    return estimator.to(device).eval()


class LightweightAdapter(nn.Module):
    def __init__(self, width: int = 64) -> None:
        super().__init__()
        output_dim = 2 * N_SUBCARRIERS * N_TX
        self.net = nn.Sequential(nn.Linear(output_dim, width), nn.GELU(), nn.Linear(width, output_dim))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, frozen_prediction: torch.Tensor) -> torch.Tensor:
        return frozen_prediction + self.net(frozen_prediction)


def physics_loss(
    adapted: torch.Tensor,
    observations: torch.Tensor,
    *,
    smooth_weight: float = 0.003,
    prior_weight: float = 0.1,
) -> torch.Tensor:
    estimate = unpack_complex(adapted, N_TX)
    observed = unpack_complex(observations, PILOT_COUNT)
    # PyTorch's generic MSE loss does not support complex tensors on all
    # supported versions, so compute the squared magnitude explicitly.
    measurement = (estimate[..., :PILOT_COUNT] - observed).abs().square().mean()
    # A first-order frequency consistency term is less brittle than a fixed
    # high-delay cutoff when the target delay spread changes.
    smoothness = (estimate[:, 1:, :] - estimate[:, :-1, :]).abs().square().mean()
    return measurement + smooth_weight * smoothness + prior_weight * adapted.square().mean()


@torch.no_grad()
def evaluate(estimator: SourceEstimator, loader: DataLoader, device: torch.device) -> float:
    estimator = prepare_estimator(estimator, device)
    values: list[torch.Tensor] = []
    for features, target in loader:
        prediction = estimator(features.to(device)).cpu()
        values.append(nmse(prediction, target))
    return float(torch.cat(values).mean())


@torch.no_grad()
def collect_predictions(
    estimator: SourceEstimator, loader: DataLoader, device: torch.device
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    estimator = prepare_estimator(estimator, device)
    predictions: list[torch.Tensor] = []
    features: list[torch.Tensor] = []
    targets: list[torch.Tensor] = []
    for batch_features, batch_target in loader:
        predictions.append(estimator(batch_features.to(device)).cpu())
        features.append(batch_features)
        targets.append(batch_target)
    return torch.cat(predictions), torch.cat(features), torch.cat(targets)


@torch.no_grad()
def evaluate_ls(loader: DataLoader, device: torch.device) -> float:
    values: list[torch.Tensor] = []
    for features, target in loader:
        features = features.to(device)
        values.append(nmse(ls_estimate(features).cpu(), target))
    return float(torch.cat(values).mean())


def communication_metrics(
    prediction: torch.Tensor,
    target: torch.Tensor,
    *,
    snr_db: float = 15.0,
    seed: int = 20261002,
) -> dict[str, float]:
    """Evaluate QPSK BER and spectral efficiency with estimate-based MRT."""
    estimated = unpack_complex(prediction, N_TX).numpy()
    truth = unpack_complex(target, N_TX).numpy()
    rng = np.random.default_rng(seed)
    symbols = (
        np.sign(rng.standard_normal((truth.shape[0], N_SUBCARRIERS)))
        + 1j * np.sign(rng.standard_normal((truth.shape[0], N_SUBCARRIERS)))
    ) / np.sqrt(2.0)
    channel_power = np.mean(np.abs(truth) ** 2, axis=(1, 2), keepdims=True)
    noise_power = channel_power / (10.0 ** (snr_db / 10.0))
    noise = rng.standard_normal(symbols.shape) + 1j * rng.standard_normal(symbols.shape)
    norm = np.sqrt(np.sum(np.abs(estimated) ** 2, axis=2, keepdims=True))
    beam = np.conj(estimated) / np.maximum(norm, 1e-8)
    true_gain = np.sum(truth * beam, axis=2)
    estimated_gain = np.sum(estimated * beam, axis=2)
    received = true_gain * symbols + np.sqrt(noise_power[:, :, 0] / 2.0) * noise
    equalized = received / np.where(np.abs(estimated_gain) > 1e-8, estimated_gain, 1e-8)
    bit_truth = np.stack([symbols.real >= 0.0, symbols.imag >= 0.0], axis=-1)
    bit_pred = np.stack([equalized.real >= 0.0, equalized.imag >= 0.0], axis=-1)
    ber = float(np.mean(bit_truth != bit_pred))
    spectral_efficiency = float(
        np.mean(np.log2(1.0 + np.abs(true_gain) ** 2 / noise_power[:, :, 0]))
    )
    return {"ber": ber, "spectral_efficiency_bps_hz": spectral_efficiency}


def adapt_target_unlabeled(
    estimator: SourceEstimator,
    target_features: torch.Tensor,
    *,
    device: torch.device,
    steps: int,
    learning_rate: float,
    smooth_weight: float = 0.003,
    prior_weight: float = 0.1,
    batch_size: int = 128,
) -> tuple[LightweightAdapter, torch.Tensor]:
    """Run prequential target adaptation from feature tensors only.

    The function deliberately has no target-CSI argument.  It carries one
    adapter through successive unlabeled batches, performs ``steps`` updates
    on each batch, and returns the prediction made immediately after that
    batch's update.  This makes the canonical sweep an explicit prequential
    estimand while keeping scoring outside the optimizer boundary.
    """
    estimator = prepare_estimator(estimator, device)
    target_features = target_features.detach().cpu()
    adapter = LightweightAdapter().to(device)
    optimizer = torch.optim.Adam(adapter.parameters(), lr=learning_rate)
    final_predictions: list[torch.Tensor] = []
    for batch_features in target_features.split(batch_size):
        features = batch_features.to(device)
        with torch.no_grad():
            frozen = estimator(features)
        adapter.train()
        for _ in range(steps):
            optimizer.zero_grad(set_to_none=True)
            adapted = adapter(frozen)
            loss = physics_loss(
                adapted,
                features,
                smooth_weight=smooth_weight,
                prior_weight=prior_weight,
            )
            loss.backward()
            optimizer.step()
        with torch.no_grad():
            final_predictions.append(adapter(frozen).cpu())
    return adapter.eval(), torch.cat(final_predictions)


def fit_adapter_on_unlabeled_features(
    estimator: SourceEstimator,
    support_features: torch.Tensor,
    *,
    device: torch.device,
    steps: int,
    learning_rate: float,
    smooth_weight: float = 0.003,
    prior_weight: float = 0.1,
) -> LightweightAdapter:
    """Fit an adapter on a support block, without accessing support labels."""
    estimator = prepare_estimator(estimator, device)
    adapter = LightweightAdapter().to(device)
    support_features = support_features.to(device)
    with torch.no_grad():
        frozen = estimator(support_features)
    optimizer = torch.optim.Adam(adapter.parameters(), lr=learning_rate)
    adapter.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = physics_loss(
            adapter(frozen),
            support_features,
            smooth_weight=smooth_weight,
            prior_weight=prior_weight,
        )
        loss.backward()
        optimizer.step()
    return adapter.eval()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--adapt-steps", type=int, default=10)
    parser.add_argument("--adapter-lr", type=float, default=1e-3)
    parser.add_argument("--smooth-weight", type=float, default=0.003)
    parser.add_argument("--prior-weight", type=float, default=0.1)
    parser.add_argument("--target-angle-shift", type=float, default=TARGET_ANGLE_SHIFT)
    parser.add_argument("--target-delay-scale", type=float, default=TARGET_DELAY_SCALE)
    args = parser.parse_args()
    L.seed_everything(args.seed, workers=True)
    use_cuda = args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available())
    device = torch.device("cuda" if use_cuda else "cpu")
    train_count, test_count = ((4096, 512) if args.mode == "full" else (512, 128))
    batch_size = 128

    source_x, source_y = make_samples(
        train_count, seed=args.seed, beam_squint=True, angle_shift=0.0, delay_scale=SOURCE_DELAY_SCALE
    )
    source_val_x, source_val_y = make_samples(
        test_count, seed=args.seed + 10000, beam_squint=True, angle_shift=0.0, delay_scale=SOURCE_DELAY_SCALE
    )
    target_x, target_y = make_samples(
        test_count,
        seed=args.seed + 20000,
        beam_squint=True,
        angle_shift=args.target_angle_shift,
        delay_scale=args.target_delay_scale,
    )
    source_loader = DataLoader(TensorDataset(torch.from_numpy(source_x), torch.from_numpy(source_y)), batch_size=batch_size, shuffle=True)
    source_val_loader = DataLoader(TensorDataset(torch.from_numpy(source_val_x), torch.from_numpy(source_val_y)), batch_size=batch_size)
    target_loader = DataLoader(TensorDataset(torch.from_numpy(target_x), torch.from_numpy(target_y)), batch_size=batch_size)

    module = SourceLightningModule().to(device)
    trainer = L.Trainer(
        accelerator="gpu" if use_cuda else "cpu",
        devices=1,
        max_epochs=12 if args.mode == "full" else 2,
        logger=False,
        enable_checkpointing=False,
        deterministic=True,
        enable_progress_bar=False,
    )
    start = time.perf_counter()
    trainer.fit(module, source_loader, source_val_loader)
    # Lightning can leave the module on CPU after fit; evaluation is explicitly
    # requested on ``device`` and must move the estimator back before inference.
    module.estimator = prepare_estimator(module.estimator, device)
    source_nmse = evaluate(module.estimator, source_val_loader, device)
    frozen_predictions, target_features, target_targets = collect_predictions(
        module.estimator, target_loader, device
    )
    frozen_nmse = float(nmse(frozen_predictions, target_targets).mean())
    target_ls_nmse = evaluate_ls(target_loader, device)
    adapter, adapted_predictions = adapt_target_unlabeled(
        module.estimator,
        target_features,
        device=device,
        steps=args.adapt_steps,
        learning_rate=args.adapter_lr,
        smooth_weight=args.smooth_weight,
        prior_weight=args.prior_weight,
        batch_size=batch_size,
    )
    adapted_nmse = float(nmse(adapted_predictions, target_targets).mean())
    adapter_parameters = sum(parameter.numel() for parameter in adapter.parameters())
    elapsed = time.perf_counter() - start
    output = {
        "experiment": "cloud_ris_adapter_lightning",
        "mode": args.mode,
        "device": str(device),
        "source_samples": train_count,
        "target_samples": test_count,
        "target_labels_used_for_adaptation": False,
        "source_validation_nmse": source_nmse,
        "target_ls_nmse": target_ls_nmse,
        "frozen_target_nmse": frozen_nmse,
        "adapted_target_nmse": adapted_nmse,
        "communication": {
            "ls": communication_metrics(ls_estimate(target_features), target_targets),
            "frozen": communication_metrics(frozen_predictions, target_targets),
            "adapted": communication_metrics(adapted_predictions, target_targets),
        },
        "adapter_parameters": adapter_parameters,
        "adapt_steps": args.adapt_steps,
        "adapter_lr": args.adapter_lr,
        "smooth_weight": args.smooth_weight,
        "prior_weight": args.prior_weight,
        "target_angle_shift": args.target_angle_shift,
        "target_delay_scale": args.target_delay_scale,
        "elapsed_seconds": elapsed,
    }
    print(json.dumps(output, indent=2))
    serialized = json.dumps(output, indent=2) + "\n"
    Path(
        f"experiments/cloud_ris_adapter_lightning_{args.mode}_seed{args.seed}_results.json"
    ).write_text(serialized, encoding="utf-8")
    Path(f"experiments/cloud_ris_adapter_lightning_{args.mode}_results.json").write_text(
        serialized, encoding="utf-8"
    )
    # Keep a conventional latest-result path for simple notebook workflows.
    Path("experiments/cloud_ris_adapter_lightning_results.json").write_text(
        serialized, encoding="utf-8"
    )


if __name__ == "__main__":
    main()
