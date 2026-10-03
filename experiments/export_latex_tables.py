"""Generate LaTeX tables from machine-readable experiment summaries."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper-tables"


def f(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def write_r014() -> None:
    data = json.loads((ROOT / "experiments/cloud_ris_shift_sweep_full_3seed_summary.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Explicit-RIS shift sweep. Values are mean (SD) across three CPU seeds.}",
        r"\label{tab:r014}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{ccrrrrrrrrr}",
        r"\toprule",
        r"Angle & Delay & LS NMSE & Frozen NMSE & Adapted NMSE & LS BER & Frozen BER & Adapted BER & LS SE & Frozen SE & Adapted SE\\",
        r"shift & scale & & & & & & & (bit/s/Hz) & (bit/s/Hz) & (bit/s/Hz)\\",
        r"\midrule",
    ]
    for row in data["results_mean_sd"]:
        lines.append(
            f"{row['angle_shift']:.2f} & {row['delay_scale']:.1f} & "
            f"{f(row['nmse']['ls'][0])} ({f(row['nmse']['ls'][1])}) & "
            f"{f(row['nmse']['frozen'][0])} ({f(row['nmse']['frozen'][1])}) & "
            f"{f(row['nmse']['adapted'][0])} ({f(row['nmse']['adapted'][1])}) & "
            f"{f(row['communication']['ls_ber'][0])} ({f(row['communication']['ls_ber'][1])}) & "
            f"{f(row['communication']['frozen_ber'][0])} ({f(row['communication']['frozen_ber'][1])}) & "
            f"{f(row['communication']['adapted_ber'][0])} ({f(row['communication']['adapted_ber'][1])}) & "
            f"{f(row['communication']['ls_spectral_efficiency_bps_hz'][0])} ({f(row['communication']['ls_spectral_efficiency_bps_hz'][1])}) & "
            f"{f(row['communication']['frozen_spectral_efficiency_bps_hz'][0])} ({f(row['communication']['frozen_spectral_efficiency_bps_hz'][1])}) & "
            f"{f(row['communication']['adapted_spectral_efficiency_bps_hz'][0])} ({f(row['communication']['adapted_spectral_efficiency_bps_hz'][1])})\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"}", r"\end{table*}"])
    (OUT / "table_r014_shift_sweep.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r020() -> None:
    data = json.loads((ROOT / "experiments/cloud_ris_robustness_adapter_cpu_3seed_summary.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Fixed-two-pilot robustness summary. Deltas are adapted minus frozen.}",
        r"\label{tab:r020}",
        r"\begin{tabular}{ccrrrrr}",
        r"\toprule",
        r"RIS elements & Beam squint & SNR (dB) & NMSE delta & BER delta & SE delta & NMSE seeds improved\\",
        r"\midrule",
    ]
    for row in data["results"]:
        lines.append(
            f"{row['ris_elements']} & {'on' if row['beam_squint'] else 'off'} & {row['snr_db']:.0f} & "
            f"{f(row['adapted_minus_frozen_nmse_mean'], 5)} & {f(row['ber_delta_mean'], 5)} & "
            f"{f(row['spectral_efficiency_delta_mean'], 5)} & {row['nmse_improved_seed_count']}/3\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    (OUT / "table_r020_robustness.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r021() -> None:
    data = json.loads((ROOT / "experiments/cloud_ris_physics_preregistered_cpu_3seed_summary.json").read_text(encoding="utf-8"))
    primary = data["primary_outcome"]
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Preregistered physical-objective control.}",
        r"\label{tab:r021}",
        r"\begin{tabular}{lr}",
        r"\toprule",
        f"Paired samples & {primary['sample_count']}\\\\",
        f"Delay-tail $-$ no-physics NMSE & {f(primary['delay_tail_minus_no_physics_mean'], 6)}\\\\",
        f"Bootstrap 95\\% CI & [{f(primary['bootstrap_ci95'][0], 6)}, {f(primary['bootstrap_ci95'][1], 6)}]\\\\",
        f"Independent-contribution gate & {'PASS' if primary['passes_gate'] else 'FAIL'}\\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    (OUT / "table_r021_physics_control.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r017_capacity() -> None:
    paths = [ROOT / f"experiments/cloud_ris_full_model_heldout_seed{seed}.json" for seed in (20261002, 20261003, 20261004)]
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    shifts = [(0.08, 1.4), (0.12, 1.6), (0.18, 2.0)]
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Held-out capacity control. Values are mean (SD) across three CPU seeds; target labels are not used for adaptation.}",
        r"\label{tab:r017}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{ccrrrrrr}",
        r"\toprule",
        r"Angle & Delay & Frozen NMSE & Adapter NMSE & Full NMSE & Adapter BER & Full BER & Full SE\\",
        r"shift & scale & & & & & & (bit/s/Hz)\\",
        r"\midrule",
    ]
    for angle, delay in shifts:
        rows = [
            next(item for item in run["results"] if item["angle_shift"] == angle and item["delay_scale"] == delay)
            for run in runs
        ]

        def nmse_ms(method: str) -> str:
            values = [float(row["nmse"][method]) for row in rows]
            return f"{statistics.mean(values):.4f} ({statistics.stdev(values):.4f})"

        def metric_ms(method: str, field: str) -> str:
            values = [float(row["communication"][method][field]) for row in rows]
            return f"{statistics.mean(values):.4f} ({statistics.stdev(values):.4f})"

        lines.append(
            f"{angle:.2f} & {delay:.1f} & {nmse_ms('frozen')} & {nmse_ms('adapter_only')} & "
            f"{nmse_ms('full_model')} & {metric_ms('adapter_only', 'ber')} & "
            f"{metric_ms('full_model', 'ber')} & {metric_ms('full_model', 'spectral_efficiency_bps_hz')}\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"}", r"\end{table*}"])
    (OUT / "table_r017_capacity.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r024_cost() -> None:
    cpu = json.loads((ROOT / "experiments/adaptation_cost_cpu_seed20261002.json").read_text(encoding="utf-8"))
    def mean_sd(values: list[float]) -> str:
        return f"{statistics.mean(values):.4f} ({statistics.stdev(values):.4f})"
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Label-free adaptation cost. Wall-clock values are mean (SD) over three CPU repeats.}",
        r"\label{tab:r024}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Method & Parameters & CPU seconds\\",
        r"\midrule",
        f"Adapter-only & {cpu['parameters']['adapter_only']} & {mean_sd(cpu['wall_clock_seconds']['adapter_only'])}\\\\",
        f"Full-model & {cpu['parameters']['full_model']} & {mean_sd(cpu['wall_clock_seconds']['full_model'])}\\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\end{table}",
    ]
    (OUT / "table_r024_cost.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r017_paired() -> None:
    seeds = (20261002, 20261003, 20261004)
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Held-out paired uncertainty for adapter minus frozen NMSE. Each row is a seed-level evaluation block.}",
        r"\label{tab:r017paired}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{rrrrrr}",
        r"\toprule",
        r"Seed & Angle shift & Delay scale & Mean difference & Bootstrap 95\% CI & Wilcoxon $p$\\",
        r"\midrule",
    ]
    for seed in seeds:
        data = json.loads((ROOT / f"experiments/cloud_ris_heldout_geometry_full_seed{seed}.json").read_text(encoding="utf-8"))
        for row in data["results"]:
            paired = row["paired_statistics"]["adapted_minus_frozen"]
            ci = paired["bootstrap_ci95"]
            lines.append(
                f"{seed} & {row['angle_shift']:.2f} & {row['delay_scale']:.1f} & "
                f"{paired['mean_difference']:.6f} & [{ci[0]:.6f}, {ci[1]:.6f}] & {paired['wilcoxon_p_value']:.3g}\\\\"
            )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"}", r"\end{table*}"])
    (OUT / "table_r017_paired.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_related_work() -> None:
    records = json.loads((ROOT / "experiments/related_work_matrix.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Bounded comparison with five DOI-verified neighboring records. ``Not confirmed'' means the checked metadata and search record did not establish the property; it is not a claim that the source lacks it.}",
        r"\label{tab:relatedwork}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{p{0.17\textwidth}p{0.15\textwidth}p{0.17\textwidth}p{0.17\textwidth}p{0.15\textwidth}p{0.17\textwidth}}",
        r"\toprule",
        r"Record & Scenario & Supervision & Adaptation signal & Downstream metric / failure analysis & Difference emphasized here\\",
        r"\midrule",
    ]
    for item in records:
        lines.append(
            f"{item['short_title']} ({item['year']}) & {item['scenario']} & {item['supervision']} & "
            f"{item['adaptation_signal']} & {item['downstream_metric']}; {item['failure_analysis']} & {item['difference']}\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"}", r"\end{table*}"])
    (OUT / "table_related_work.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_r032_omp() -> None:
    """Export the explicit-RIS classical baseline from its JSON artifact."""
    data = json.loads((ROOT / "experiments/ris_explicit_omp_baseline_results.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Explicit-RIS classical references. Values are mean (SD) across three seeds; the fixed spatial dictionary is used by OMP.}",
        r"\label{tab:r032omp}",
        r"\begin{tabular}{cccrr}",
        r"\toprule",
        r"Angle shift & Delay scale & Pilots & LS NMSE & OMP NMSE\\",
        r"\midrule",
    ]
    for row in data["results"]:
        lines.append(
            f"{row['angle_shift']:.2f} & {row['delay_scale']:.1f} & {row['pilot_count']} & "
            f"{row['ls_nmse_mean']:.4f} ({row['ls_nmse_sd_across_seeds']:.4f}) & "
            f"{row['omp_nmse_mean']:.4f} ({row['omp_nmse_sd_across_seeds']:.4f})\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    (OUT / "table_r032_omp.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write_r014()
    write_r020()
    write_r021()
    write_r017_capacity()
    write_r024_cost()
    write_r017_paired()
    write_related_work()
    write_r032_omp()
    print("wrote LaTeX tables")
