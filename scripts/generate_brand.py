"""Generate the RATISS Labs Grover studio brand asset deterministically.

The logo encodes the experiment: three amplitude bars for the marked state
|111> growing across Grover iterations (0.117 -> 0.770 -> 0.963 observed), a
topological ring for the RATISS logical sidecar, and a phase-flip marker for
the oracle. Rendered with matplotlib only, from code, so the brand is
reproducible.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

INK = "#07111c"
PANEL = "#0d1f2d"
MINT = "#42d6ad"
BLUE = "#79b8ff"
CORAL = "#ff927d"
MUTED = "#9bb0bf"


def build_logo(destination: Path) -> None:
    fig = plt.figure(figsize=(6.4, 6.4), facecolor=INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.axis("off")

    # Topological sidecar ring (H1 cycle) framing the experiment.
    theta = np.linspace(0, 2 * np.pi, 300)
    for lw, alpha in [(14, 0.05), (9, 0.10), (5, 0.18)]:
        ax.plot(1.06 * np.cos(theta), 1.06 * np.sin(theta), color=BLUE, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    ax.plot(1.06 * np.cos(theta), 1.06 * np.sin(theta), color=BLUE, lw=1.6, alpha=0.85, zorder=2)

    # Sidecar nodes on the ring.
    n = 8
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ax.scatter(1.06 * np.cos(ang), 1.06 * np.sin(ang), s=70, color=BLUE, edgecolor=INK, lw=1.2, zorder=3)

    # Inner panel.
    ax.add_patch(Circle((0, 0), 0.82, facecolor=PANEL, edgecolor=MUTED, lw=1.2, alpha=0.95, zorder=4))

    # Grover amplification: three bars for |111> marked mass 0.117 -> 0.770 -> 0.963.
    masses = [0.117188, 0.769531, 0.962891]
    colors = [MUTED, MINT, MINT]
    width = 0.20
    for index, mass in enumerate(masses):
        x0 = -0.42 + index * 0.32
        height = 1.05 * mass
        ax.bar(x0, height, width=width, bottom=-0.55, color=colors[index], edgecolor=INK, linewidth=1.5, zorder=5, alpha=0.95)

    # Oracle phase-flip marker above the amplified bar.
    ax.plot([0.10, 0.10], [0.62, 0.80], color=CORAL, lw=2.4, zorder=6)
    ax.scatter([0.10], [0.84], s=110, color=CORAL, edgecolor=INK, lw=1.5, zorder=7)

    # Baseline axis.
    ax.plot([-0.60, 0.60], [-0.55, -0.55], color=MUTED, lw=1.4, zorder=6)

    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200, facecolor=INK)
    plt.close(fig)


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "docs" / "brand"
    build_logo(out / "ratiss-labs-grover-logo.png")
    print(f"Wrote {out / 'ratiss-labs-grover-logo.png'}")


if __name__ == "__main__":
    main()
