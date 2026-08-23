"""Render visual evidence from the executed Grover artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


PALETTE = {"ink": "#07111c", "panel": "#102433", "mint": "#42d6ad", "blue": "#79b8ff", "coral": "#ff927d", "text": "#eaf2f8", "muted": "#9bb0bf"}


def style(axis) -> None:
    axis.set_facecolor(PALETTE["panel"])
    axis.tick_params(colors=PALETTE["muted"])
    for spine in axis.spines.values(): spine.set_color("#315063")
    axis.grid(alpha=0.18, color="#9bb0bf")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="artifacts/grover_ratiss.json")
    parser.add_argument("--output-dir", default="docs/assets")
    args = parser.parse_args()
    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": PALETTE["ink"], "savefig.facecolor": PALETTE["ink"]})
    stages = document["stages"]
    iteration = [stage["iteration"] for stage in stages]
    ideal = [stage["ideal_marked_mass"] for stage in stages]
    noisy = [stage["noisy_marked_mass"] for stage in stages]
    fig, axis = plt.subplots(figsize=(8.6, 4.8))
    style(axis)
    axis.plot(iteration, ideal, marker="o", linewidth=2.6, color=PALETTE["mint"], label="Aer idéal")
    axis.plot(iteration, noisy, marker="o", linewidth=2.6, color=PALETTE["coral"], label="Aer bruité — CX p=0.02")
    axis.set_title("Grover — masse observée de l’état marqué |111⟩")
    axis.set_xlabel("Itération Grover")
    axis.set_ylabel("Masse de l’état marqué")
    axis.set_ylim(0.0, 1.05)
    axis.set_xticks(iteration)
    legend = axis.legend(frameon=False)
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "grover-marked-mass.png", dpi=180)
    plt.close(fig)

    coherence = [stage["ratiss_logical_sidecar"]["coherence"] for stage in stages]
    psig = [stage["ratiss_logical_sidecar"]["P_sig"] for stage in stages]
    fig, left = plt.subplots(figsize=(8.6, 4.8))
    style(left)
    right = left.twinx()
    right.tick_params(colors=PALETTE["muted"])
    right.spines["right"].set_color("#315063")
    left.plot(iteration, coherence, marker="o", linewidth=2.6, color=PALETTE["blue"], label="Cohérence logique")
    right.plot(iteration, psig, marker="D", linewidth=2.6, color=PALETTE["mint"], label="P sig logique")
    left.set_title("Grover — sidecar TopologicalQubit RATISS")
    left.set_xlabel("Itération Grover")
    left.set_ylabel("Cohérence logique")
    right.set_ylabel("P sig logique", color=PALETTE["text"])
    left.set_xticks(iteration)
    lines = left.lines + right.lines
    legend = left.legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper right")
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "grover-ratiss-sidecar.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
