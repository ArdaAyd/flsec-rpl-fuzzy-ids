"""Figure style and plots shared by the experiment scripts."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

from . import config  # noqa: E402

SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

OMEGA_CMAP = LinearSegmentedColormap.from_list("omega", ["#184f95", "#6da7ec", "#f0efec", "#ec8584", "#b52f2f"])

LABELS = {
    "en": {
        "dio_counter": "DIO_Counter (DIOs per 30 s window)",
        "dti": "DTI (s)",
        "stia": "STIA (s)",
        "aggressive_weight": "Aggressive weight ω",
        "membership": "Degree of membership",
        "L": "Low", "M": "Medium", "H": "High",
        "normal": "Normal", "quarantine": "Quarantine", "malicious": "Malicious",
        "delta": "δ = 0.5",
        "stia_panel": "STIA = {v:g} s",
    },
    "tr": {
        "dio_counter": "DIO_Counter (30 s pencerede DIO sayısı)",
        "dti": "DTI (s)",
        "stia": "STIA (s)",
        "aggressive_weight": "Saldırganlık ağırlığı ω",
        "membership": "Üyelik derecesi",
        "L": "Düşük", "M": "Orta", "H": "Yüksek",
        "normal": "Normal", "quarantine": "Karantina", "malicious": "Kötücül",
        "delta": "δ = 0,5",
        "stia_panel": "STIA = {v:g} s",
    },
}


def apply_style():
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.family": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "text.color": INK,
        "axes.labelcolor": INK_SECONDARY,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "xtick.labelcolor": INK_SECONDARY,
        "ytick.labelcolor": INK_SECONDARY,
        "legend.frameon": False,
        "lines.linewidth": 1.8,
    })


def save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_membership_functions(fls, path, lang="en"):
    """Input and output membership functions (paper Fig. 6)."""
    apply_style()
    text = LABELS[lang]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.8))
    for ax, var in zip(axes.ravel(), list(fls.inputs) + [fls.output]):
        lo, hi = var.universe
        x = np.linspace(lo, hi, 1201)
        for i, (term, fset) in enumerate(var.sets.items()):
            mu = fset(x)
            ax.plot(x, mu, color=SERIES[i])
            peak = np.mean(fset.params[1:3]) if fset.kind == "trap" else x[np.argmax(mu)]
            ax.text(peak, 1.06, text.get(term, term), ha="center", va="bottom", fontsize=8)
        ax.set_xlim(lo, hi)
        ax.set_ylim(0, 1.18)
        ax.set_yticks([0, 0.5, 1])
        ax.set_xlabel(text[var.name])
        ax.set_ylabel(text["membership"])
    fig.tight_layout()
    return save(fig, path)


def plot_decision_surfaces(fls, path, stia_values=(0.0, 15.0), markers=None, lang="en"):
    """Aggressive weight over (DIO_Counter, DTI) for fixed STIA values."""
    apply_style()
    text = LABELS[lang]
    grid = np.linspace(0, 30, 241)
    D, T = np.meshgrid(grid, grid)
    norm = TwoSlopeNorm(vmin=1 / 6, vcenter=config.FUZZY_FILTER_DELTA, vmax=5 / 6)
    fig, axes = plt.subplots(1, len(stia_values), figsize=(3.6 * len(stia_values) + 0.8, 3.4), sharey=True)
    axes = np.atleast_1d(axes)
    for k, (ax, s) in enumerate(zip(axes, stia_values)):
        W = fls.infer(np.column_stack([D.ravel(), T.ravel(), np.full(D.size, s)])).reshape(D.shape)
        mesh = ax.pcolormesh(D, T, W, cmap=OMEGA_CMAP, norm=norm, shading="auto", rasterized=True)
        cs = ax.contour(D, T, W, levels=[config.FUZZY_FILTER_DELTA], colors=INK, linewidths=1.0)
        ax.clabel(cs, fmt={config.FUZZY_FILTER_DELTA: text["delta"]}, fontsize=7, inline=True)
        ax.set_title(text["stia_panel"].format(v=s), fontsize=9)
        ax.set_xlabel(text["dio_counter"])
        if k == 0:
            ax.set_ylabel(text["dti"])
            for x, y, label in markers or []:
                ax.scatter([x], [y], s=36, color=INK, edgecolor="white", linewidth=1.5, zorder=3)
                right = x > 24
                ax.annotate(label, (x, y), xytext=(-5, 5) if right else (5, 5), textcoords="offset points",
                            ha="right" if right else "left", fontsize=7)
        ax.grid(False)
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
    cbar = fig.colorbar(mesh, ax=axes.tolist(), fraction=0.04, pad=0.02)
    cbar.set_label(text["aggressive_weight"], color=INK_SECONDARY)
    cbar.outline.set_visible(False)
    return save(fig, path)
