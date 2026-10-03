"""Rebuild CPU held-out, robustness and physics summaries from per-seed JSON."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SEEDS = (20261002, 20261003, 20261004)


def read(name: str) -> dict:
    return json.loads((ROOT / "experiments" / name).read_text(encoding="utf-8"))


def bootstrap(values: np.ndarray, seed: int, draws: int = 2000) -> list[float]:
    rng = np.random.default_rng(seed)
    means = np.empty(draws, dtype=np.float64)
    for i in range(draws):
        means[i] = np.mean(values[rng.integers(0, values.size, values.size)])
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def aggregate_robustness() -> None:
    runs = [read(f"cloud_ris_robustness_adapter_cpu_seed{s}.json") for s in SEEDS]
    cells = sorted(
        {(r["ris_elements"], bool(r["beam_squint"]), float(r["snr_db"]))
         for run in runs for r in run["results"]}
    )
    rows = []
    for ris, squint, snr in cells:
        cell_rows = [
            next(r for r in run["results"] if r["ris_elements"] == ris
                 and bool(r["beam_squint"]) == squint and float(r["snr_db"]) == snr)
            for run in runs
        ]
        nmse = [float(r["nmse"]["adapted_minus_frozen_mean"]) for r in cell_rows]
        ber = [float(r["communication"]["adapted"]["ber"] - r["communication"]["frozen"]["ber"]) for r in cell_rows]
        se = [float(r["communication"]["adapted"]["spectral_efficiency_bps_hz"] - r["communication"]["frozen"]["spectral_efficiency_bps_hz"]) for r in cell_rows]
        rows.append({
            "ris_elements": ris, "beam_squint": squint, "snr_db": snr,
            "seed_count": len(SEEDS),
            "adapted_minus_frozen_nmse_mean": float(statistics.mean(nmse)),
            "adapted_minus_frozen_nmse_sd": float(statistics.stdev(nmse)),
            "nmse_improved_seed_count": sum(v < 0 for v in nmse),
            "ber_delta_mean": float(statistics.mean(ber)),
            "ber_improved_seed_count": sum(v < 0 for v in ber),
            "spectral_efficiency_delta_mean": float(statistics.mean(se)),
        })
    out = {"experiment": "cloud_ris_robustness_adapter_cpu_3seed_summary",
           "source_validation_nmse_mean": float(statistics.mean(run["source_validation_nmse"] for run in runs)),
           "seeds": list(SEEDS), "devices": sorted({run["device"] for run in runs}), "results": rows}
    (ROOT / "experiments/cloud_ris_robustness_adapter_cpu_3seed_summary.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


def aggregate_physics() -> None:
    runs = [read(f"cloud_ris_physics_preregistered_cpu_seed{s}.json") for s in SEEDS]
    per_shift = []
    pooled = []
    for shift_index in range(2):
        rows = [run["results"][0]["results"][shift_index] for run in runs]
        differences = np.concatenate([np.asarray(r["delay_tail_minus_no_physics"]["per_sample"], dtype=float) for r in rows])
        pooled.append(differences)
        per_shift.append({
            "angle_shift": rows[0]["angle_shift"], "delay_scale": rows[0]["delay_scale"],
            "no_physics_nmse_mean": float(statistics.mean(r["nmse"]["no_physics"] for r in rows)),
            "first_difference_nmse_mean": float(statistics.mean(r["nmse"]["first_difference"] for r in rows)),
            "delay_tail_nmse_mean": float(statistics.mean(r["nmse"]["delay_tail"] for r in rows)),
        })
    values = np.concatenate(pooled)
    mean = float(np.mean(values))
    ci = bootstrap(values, seed=20261002 + 91000)
    out = {
        "experiment": "cloud_ris_physics_preregistered_cpu_3seed_summary",
        "devices": sorted({run["device"] for run in runs}), "seeds": list(SEEDS),
        "primary_outcome": {"sample_count": int(values.size), "delay_tail_minus_no_physics_mean": mean,
                             "bootstrap_ci95": ci, "passes_gate": bool(ci[1] < 0)},
        "per_shift": per_shift,
    }
    (ROOT / "experiments/cloud_ris_physics_preregistered_cpu_3seed_summary.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    aggregate_robustness()
    aggregate_physics()
    print("rebuilt CPU robustness and physics summaries")
