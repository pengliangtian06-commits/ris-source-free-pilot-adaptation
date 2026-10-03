"""Aggregate canonical shift-sweep JSON artifacts without hard-coded results."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEEDS = (20261002, 20261003, 20261004)


def mean_sd(values: list[float]) -> list[float]:
    return [float(statistics.mean(values)), float(statistics.stdev(values))]


def main() -> None:
    runs = [
        json.loads(
            (ROOT / f"experiments/cloud_ris_shift_sweep_full_seed{seed}.json").read_text(
                encoding="utf-8"
            )
        )
        for seed in SEEDS
    ]
    devices = sorted({str(run.get("device", "unknown")) for run in runs})
    shifts = [
        (float(row["angle_shift"]), float(row["delay_scale"]))
        for row in runs[0]["results"]
    ]
    results = []
    for angle_shift, delay_scale in shifts:
        rows = [
            next(
                row
                for row in run["results"]
                if float(row["angle_shift"]) == angle_shift
                and float(row["delay_scale"]) == delay_scale
            )
            for run in runs
        ]
        results.append(
            {
                "angle_shift": angle_shift,
                "delay_scale": delay_scale,
                "nmse": {
                    method: mean_sd([float(row["nmse"][method]) for row in rows])
                    for method in ("ls", "frozen", "adapted")
                },
                "communication": {
                    f"{method}_{metric}": mean_sd(
                        [float(row["communication"][method][metric]) for row in rows]
                    )
                    for method in ("ls", "frozen", "adapted")
                    for metric in ("ber", "spectral_efficiency_bps_hz")
                },
            }
        )
    output = {
        "experiment": "cloud_ris_explicit_target_shift_sweep",
        "mode": "full",
        "device": devices[0] if len(devices) == 1 else devices,
        "seeds": list(SEEDS),
        "target_labels_used_for_adaptation": any(
            row.get("target_labels_used_for_adaptation", True)
            for run in runs
            for row in run["results"]
        ),
        "results_mean_sd": results,
    }
    out = ROOT / "experiments/cloud_ris_shift_sweep_full_3seed_summary.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "devices": devices, "rows": len(results)}))


if __name__ == "__main__":
    main()
