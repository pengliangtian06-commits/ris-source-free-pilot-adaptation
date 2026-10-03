"""Deterministic graphical-abstract draft for the v1.0.3 release.

The graphic is a protocol schematic, not a quantitative data panel. All labels
and values are taken from the manuscript and the locked release metadata.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

try:
    from audit_panel_alignment import require_matplotlib_panel_alignment
except ModuleNotFoundError:
    skill_scripts = os.environ.get("NATURE_FIGURE_SCRIPTS")
    if not skill_scripts:
        raise SystemExit("set NATURE_FIGURE_SCRIPTS to the Nature figure scripts directory")
    sys.path.insert(0, skill_scripts)
    from audit_panel_alignment import require_matplotlib_panel_alignment


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7.0,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.spines.right": False,
        "axes.spines.top": False,
    }
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "graphical_abstract_v1.0.3"


def box(ax, xy, width, height, text, face, edge="#36536b", text_color="#173042", size=7.0):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        linewidth=1.0,
        facecolor=face,
        edgecolor=edge,
        transform=ax.transAxes,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        color=text_color,
        fontsize=size,
        linespacing=1.15,
        transform=ax.transAxes,
    )


def arrow(ax, start, end, color="#36536b"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            transform=ax.transAxes,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.2,
            color=color,
            shrinkA=3,
            shrinkB=3,
        )
    )


def panel_a(ax):
    ax.set_title("Source estimator", loc="left", fontweight="bold", fontsize=8, pad=4)
    ax.text(0.02, 0.88, "labelled source CSI", transform=ax.transAxes, color="#4b6475")
    box(ax, (0.08, 0.49), 0.36, 0.19, "source pilots", "#e8f0f5")
    box(ax, (0.56, 0.49), 0.36, 0.19, "frozen MLP\nestimator", "#d4e7f2")
    arrow(ax, (0.45, 0.585), (0.55, 0.585))
    box(ax, (0.20, 0.18), 0.60, 0.15, "source training\n4,096 labelled realizations", "#f2f5f7", edge="#8296a3", size=6.5)
    arrow(ax, (0.50, 0.48), (0.50, 0.35), color="#8296a3")
    ax.text(0.50, 0.08, "source CSI used only here", ha="center", transform=ax.transAxes, color="#4b6475", fontsize=6.5)


def panel_b(ax):
    ax.set_title("Source-free target update", loc="left", fontweight="bold", fontsize=8, pad=4)
    ax.text(0.02, 0.88, "target labels withheld from adaptation", transform=ax.transAxes, color="#4b6475")
    box(ax, (0.05, 0.53), 0.27, 0.19, "target pilots", "#e8f0f5")
    box(ax, (0.38, 0.53), 0.27, 0.19, "residual\nadapter", "#dff0e8", edge="#3f7a5b")
    box(ax, (0.71, 0.53), 0.24, 0.19, "adapted\nchannel", "#d4e7f2")
    arrow(ax, (0.33, 0.625), (0.37, 0.625))
    arrow(ax, (0.66, 0.625), (0.70, 0.625))
    box(ax, (0.05, 0.19), 0.42, 0.16, "4 explicit shifts\nangle + delay", "#f2f5f7", edge="#8296a3", size=6.5)
    box(ax, (0.53, 0.19), 0.42, 0.16, "held-out scoring block\nCSI labels locked", "#fff1d9", edge="#b88437", size=6.5)
    arrow(ax, (0.50, 0.52), (0.50, 0.37), color="#8296a3")
    ax.text(0.50, 0.08, "pilot-only objective", ha="center", transform=ax.transAxes, color="#3f7a5b", fontsize=6.5, fontweight="bold")


def panel_c(ax):
    ax.set_title("Bounded outcome", loc="left", fontweight="bold", fontsize=8, pad=4)
    ax.text(0.02, 0.88, "within the tested synthetic generator", transform=ax.transAxes, color="#4b6475")
    box(ax, (0.06, 0.56), 0.27, 0.22, "NMSE\n0.83-3.21%\nlower", "#dff0e8", edge="#3f7a5b", size=5.8)
    box(ax, (0.37, 0.56), 0.27, 0.22, "BER + spectral\nefficiency", "#dff0e8", edge="#3f7a5b", size=6.2)
    box(ax, (0.68, 0.56), 0.27, 0.22, "conditional gain", "#d4e7f2", size=6.2)
    box(ax, (0.06, 0.19), 0.42, 0.20, "failure boundary\n8 elements / beam squint\n5 dB", "#f7dddd", edge="#a54a4a", size=5.4)
    box(ax, (0.53, 0.19), 0.42, 0.20, "update cost\n16,576 vs 115,328\nparameters", "#fff1d9", edge="#b88437", size=5.6)
    ax.text(0.50, 0.08, "LS remains a credible reference", ha="center", transform=ax.transAxes, color="#4b6475", fontsize=6.5)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), gridspec_kw={"wspace": 0.10})
    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_facecolor("white")
    panel_a(axes[0])
    panel_b(axes[1])
    panel_c(axes[2])
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "Source-free pilot adaptation for RIS-assisted wideband MIMO",
        fontsize=10,
        fontweight="bold",
        color="#173042",
        y=0.995,
    )
    fig.subplots_adjust(left=0.015, right=0.985, top=0.84, bottom=0.03)
    stem = str(OUT)
    require_matplotlib_panel_alignment(
        fig,
        json_out=f"{stem}.alignment.json",
        overlay_svg=f"{stem}.alignment.svg",
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        require_panel_labels=False,
        strict=True,
    )
    fig.savefig(f"{stem}.svg", bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)
    print("graphical abstract exported")


if __name__ == "__main__":
    main()
