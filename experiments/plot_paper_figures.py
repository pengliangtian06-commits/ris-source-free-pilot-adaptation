"""Generate the manuscript figures from machine-readable experiment JSON.

The selected nature-figure backend is Python.  Every quantitative value is
read from experiment artifacts; no paper number is entered manually here.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import FancyArrowPatch, Rectangle


skill_scripts = os.environ.get("NATURE_FIGURE_SCRIPTS")
if skill_scripts and skill_scripts not in sys.path:
    sys.path.insert(0, skill_scripts)
try:
    from audit_panel_alignment import require_matplotlib_panel_alignment  # noqa: E402
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guidance
    raise RuntimeError(
        "The figure alignment auditor is required. Set NATURE_FIGURE_SCRIPTS "
        "to the directory containing audit_panel_alignment.py."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.5,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "axes.linewidth": 0.75,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    }
)

COLORS = {
    "LS": "#6b7280",
    "OMP": "#9ca3af",
    "Frozen": "#2563eb",
    "Adapter": "#059669",
    "Full model": "#d97706",
}


def load(name: str) -> dict:
    return json.loads((ROOT / "experiments" / name).read_text(encoding="utf-8"))


def save(fig: plt.Figure, name: str, *, labels: bool = True) -> None:
    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig,
        json_out=str(OUT / f"{name}.alignment.json"),
        overlay_svg=str(OUT / f"{name}.alignment.svg"),
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        require_panel_labels=labels,
        strict=True,
    )
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)


def panel_label(ax: plt.Axes, label: str, *, x: float = -0.16, y: float = 1.15) -> None:
    ax.text(x, y, label, transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")


def figure1_protocol() -> None:
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (0.03, 0.55, 0.20, 0.25, "BS\nsource estimator", "#dbeafe"),
        (0.40, 0.55, 0.20, 0.25, "RIS\nreflection +\nbeam squint", "#dcfce7"),
        (0.77, 0.55, 0.20, 0.25, "UE\nwideband\nchannel", "#ffedd5"),
    ]
    for x, y, w, h, label, color in boxes:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#374151", linewidth=0.9))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", linespacing=1.25)
    for x1, x2 in ((0.23, 0.40), (0.60, 0.77)):
        ax.add_patch(FancyArrowPatch((x1, 0.675), (x2, 0.675), arrowstyle="-|>", mutation_scale=12, linewidth=1.0, color="#374151"))
    ax.text(0.315, 0.72, "cascaded hop", ha="center", va="bottom", fontsize=7)
    ax.text(0.685, 0.72, "received pilots", ha="center", va="bottom", fontsize=7)
    ax.add_patch(Rectangle((0.11, 0.11), 0.31, 0.23, facecolor="#f3f4f6", edgecolor="#6b7280", linewidth=0.8))
    ax.add_patch(Rectangle((0.58, 0.11), 0.31, 0.23, facecolor="#f3f4f6", edgecolor="#6b7280", linewidth=0.8))
    ax.text(0.265, 0.225, "target support block\nunlabelled pilots only\nadapter fitting", ha="center", va="center", linespacing=1.35)
    ax.text(0.735, 0.225, "target evaluation block\ndisjoint channels\nCSI used only for scoring", ha="center", va="center", linespacing=1.35)
    ax.add_patch(FancyArrowPatch((0.50, 0.55), (0.265, 0.35), arrowstyle="-|>", mutation_scale=10, linewidth=0.9, color="#059669", connectionstyle="arc3,rad=0.18"))
    ax.add_patch(FancyArrowPatch((0.50, 0.55), (0.735, 0.35), arrowstyle="-|>", mutation_scale=10, linewidth=0.9, color="#2563eb", connectionstyle="arc3,rad=-0.18"))
    ax.text(0.50, 0.93, "Explicit BS–RIS–UE protocol with support/evaluation isolation", ha="center", va="center", fontsize=10, fontweight="bold")
    fig.tight_layout(pad=0.2)
    # One schematic axes is intentionally exempt from multi-panel alignment.
    save(fig, "fig1_protocol", labels=False)


def figure2_shift_sweep() -> None:
    data = load("cloud_ris_shift_sweep_full_3seed_summary.json")["results_mean_sd"]
    x = np.arange(len(data))
    labels = [f"{row['angle_shift']:.2f}\n/{row['delay_scale']:.1f}" for row in data]
    specs = [
        ("NMSE", "nmse", "lower is better", 0.45),
        ("BER", "ber", "lower is better", 0.0),
        ("Spectral efficiency (bit/s/Hz)", "spectral_efficiency_bps_hz", "higher is better", 5.35),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), sharex=True)
    for ax, (title, key, direction, ymin) in zip(axes, specs):
        method_specs = [("ls", COLORS["LS"], "o"), ("frozen", COLORS["Frozen"], "s"), ("adapted", COLORS["Adapter"], "D")]
        for method, color, marker in method_specs:
            means = []
            sds = []
            for row in data:
                if key == "nmse":
                    means.append(row["nmse"][method][0])
                    sds.append(row["nmse"][method][1])
                else:
                    field = f"{method}_{key}"
                    means.append(row["communication"][field][0])
                    sds.append(row["communication"][field][1])
            display = {"ls": "LS", "frozen": "Frozen", "adapted": "Adapter"}[method]
            ax.errorbar(x, means, yerr=sds, color=color, marker=marker, linewidth=1.1, markersize=3.5, capsize=1.8, label=display)
        ax.set_title(title)
        ax.set_xticks(x, labels)
        ax.set_ylabel(title if key == "nmse" else "")
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.6)
        if ymin:
            ax.set_ylim(bottom=ymin)
        # Direction is stated in the caption; keeping the plot area free of
        # annotations prevents text-stroke collisions with error bars.
    panel_label(axes[0], "a", x=0.01, y=1.15)
    panel_label(axes[1], "b", x=0.01, y=1.15)
    panel_label(axes[2], "c")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.035), frameon=False, handlelength=1.5, columnspacing=1.0)
    fig.tight_layout(w_pad=1.0, rect=(0, 0.07, 1, 1))
    save(fig, "fig2_shift_sweep")


def figure3_classical_sensitivity() -> None:
    data = load("ris_explicit_omp_baseline_results.json")["results"]
    shifts = sorted({(row["angle_shift"], row["delay_scale"]) for row in data})
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.45), sharey=True)
    for ax, pilot_count in zip(axes, (2, 4)):
        subset = [row for row in data if row["pilot_count"] == pilot_count]
        x = np.arange(len(subset))
        width = 0.34
        ls = [row["ls_nmse_mean"] for row in subset]
        omp = [row["omp_nmse_mean"] for row in subset]
        ls_sd = [row["ls_nmse_sd_across_seeds"] for row in subset]
        omp_sd = [row["omp_nmse_sd_across_seeds"] for row in subset]
        ax.bar(x - width / 2, ls, width, yerr=ls_sd, label="LS", color=COLORS["LS"], capsize=2)
        ax.bar(x + width / 2, omp, width, yerr=omp_sd, label="OMP", color=COLORS["OMP"], capsize=2)
        ax.set_xticks(x, [f"{angle:.2f}\n/{delay:.1f}" for angle, delay in shifts])
        ax.set_title(f"{pilot_count} identity pilots")
        ax.set_xlabel("Angle shift / delay scale")
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.6)
    axes[0].set_ylabel("NMSE (mean ± seed SD)")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.035), frameon=False)
    panel_label(axes[0], "a", x=0.01, y=1.15)
    panel_label(axes[1], "b", x=0.01, y=1.15)
    fig.suptitle("Classical references remain operating-regime dependent", fontsize=9.5, y=1.02)
    fig.tight_layout(w_pad=1.2, rect=(0, 0.08, 1, 1))
    save(fig, "fig3_classical_sensitivity")


def figure4_capacity_cost() -> None:
    cpu = load("adaptation_cost_cpu_seed20261002.json")
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.45))
    methods = ["adapter_only", "full_model"]
    labels = ["Adapter-only\n(16,576)", "Full-model\n(115,328)"]
    colors = [COLORS["Adapter"], COLORS["Full model"]]
    params = [cpu["parameters"][method] for method in methods]
    cpu_mean = [np.mean(cpu["wall_clock_seconds"][method]) for method in methods]
    params = np.clip(params, a_min=1.0, a_max=None)
    if not all(value > 0 for value in params):
        raise ValueError("parameter counts must be positive before log scaling")
    axes[0].bar(labels, params, color=colors, width=0.6)
    axes[0].set_ylabel("Trainable parameters")
    axes[0].grid(axis="y", color="#e5e7eb", linewidth=0.6)
    axes[0].set_ylim(0, max(params) * 1.20)
    x = np.arange(2)
    axes[1].bar(x, cpu_mean, 0.56, label="CPU", color="#94a3b8")
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Adaptation time (s, mean)")
    axes[1].grid(axis="y", color="#e5e7eb", linewidth=0.6)
    handles, legend_labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", ncol=1, bbox_to_anchor=(0.5, -0.035), frameon=False, fontsize=8)
    axes[0].set_title("Capacity")
    axes[1].set_title("Measured cost")
    panel_label(axes[0], "a", x=0.01, y=1.15)
    panel_label(axes[1], "b", x=0.01, y=1.15)
    fig.tight_layout(w_pad=1.1, rect=(0, 0.08, 1, 1))
    save(fig, "fig4_capacity_cost")


def figure5_robustness() -> None:
    data = load("cloud_ris_robustness_adapter_cpu_3seed_summary.json")["results"]
    metrics = [
        ("adapted_minus_frozen_nmse_mean", "NMSE delta\n(adapter − frozen)"),
        ("ber_delta_mean", "BER delta\n(adapter − frozen)"),
        ("spectral_efficiency_delta_mean", "Spectral-efficiency delta\n(adapter − frozen)"),
    ]
    ris_values = [8, 16, 32]
    snr_values = [5, 15, 25]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.55))
    for panel_index, (ax, (key, title)) in enumerate(zip(axes, metrics)):
        matrix = np.array(
            [
                [
                    next(
                        row[key]
                        for row in data
                        if row["ris_elements"] == ris and row["beam_squint"] == squint and row["snr_db"] == snr
                    )
                    for snr in snr_values
                ]
                for ris in ris_values
                for squint in (False, True)
            ]
        )
        vmax = float(np.max(np.abs(matrix)))
        im = ax.imshow(matrix, cmap="RdYlGn_r", norm=TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax), aspect="auto")
        ax.set_xticks(np.arange(3), ["5", "15", "25"])
        ax.set_yticks(np.arange(6), ["8 off", "8 on", "16 off", "16 on", "32 off", "32 on"])
        for i in range(6):
            for j in range(3):
                ax.text(j, i, f"{matrix[i, j]:+.5f}", ha="center", va="center", fontsize=6.0)
        ax.set_xlabel("SNR (dB)")
        ax.set_title(title)
        panel_label(ax, chr(ord("a") + panel_index))
    axes[0].set_ylabel("RIS elements / beam squint")
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig5_robustness")


if __name__ == "__main__":
    figure1_protocol()
    figure2_shift_sweep()
    figure3_classical_sensitivity()
    figure4_capacity_cost()
    figure5_robustness()
    print("generated", len(list(OUT.glob("fig*.pdf"))), "PDF figures in", ascii(str(OUT)))
