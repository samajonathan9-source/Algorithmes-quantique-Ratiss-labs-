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
    parser.add_argument("--reality", default="artifacts/grover_reality_mode.json")
    parser.add_argument("--reality-sensitivity", default="artifacts/grover_reality_mode_sensitivity.json")
    parser.add_argument("--output-dir", default="docs/assets")
    args = parser.parse_args()
    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    reality = json.loads(Path(args.reality).read_text(encoding="utf-8"))
    sensitivity = json.loads(Path(args.reality_sensitivity).read_text(encoding="utf-8"))
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

    reality_stages = reality["stages"]
    sensitivity_stages = sensitivity["stages"]
    reality_iteration = [stage["iteration"] for stage in reality_stages]
    ideal_mass = [stage["ideal_marked_mass"] for stage in reality_stages]
    observed_mass = [stage["observed_marked_mass"] for stage in reality_stages]
    normal_divergence = [stage["reality_flag"]["lct_divergence"] for stage in reality_stages]
    sensitive_divergence = [stage["reality_flag"]["lct_divergence"] for stage in sensitivity_stages]
    sensitivity_threshold = sensitivity_stages[0]["reality_flag"]["threshold"]
    triggered = [stage["iteration"] for stage in sensitivity_stages if stage["reality_flag"]["triggered"]]
    fig, axes = plt.subplots(2, 1, figsize=(8.8, 7.0), sharex=True)
    for axis in axes: style(axis)
    axes[0].plot(reality_iteration, ideal_mass, marker="o", linewidth=2.4, color=PALETTE["mint"], label="Idéal local")
    axes[0].plot(reality_iteration, observed_mass, marker="D", linewidth=2.4, color=PALETTE["coral"], label="Observé : fake backend + Aer")
    axes[0].set_title("Grover Reality Mode — masse marquée sous modèle hardware-aware")
    axes[0].set_ylabel("Masse de |111⟩")
    axes[0].set_ylim(0.0, 1.05)
    axes[0].legend(frameon=False)
    axes[1].plot(reality_iteration, normal_divergence, marker="o", linewidth=2.4, color=PALETTE["blue"], label="Divergence : seuil nominal")
    axes[1].plot(reality_iteration, sensitive_divergence, marker="D", linewidth=2.4, color=PALETTE["mint"], label="Divergence : sensibilité")
    axes[1].axhline(sensitivity_threshold, color=PALETTE["coral"], linestyle="--", label=f"Seuil sensibilité = {sensitivity_threshold:g}")
    if triggered:
        axes[1].scatter(triggered, [sensitive_divergence[index] for index in triggered], color=PALETTE["coral"], s=70, zorder=4, label="Reality Flag levé")
    axes[1].set_xlabel("Itération Grover")
    axes[1].set_ylabel("Divergence LCT calculée")
    axes[1].set_xticks(reality_iteration)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "grover-reality-mode.png", dpi=180)
    plt.close(fig)

    compiled_depth = [stage["hardware_aware"]["compiled_depth"] for stage in reality_stages]
    compiled_size = [stage["hardware_aware"]["compiled_size"] for stage in reality_stages]
    swap_count = [stage["hardware_aware"]["swap_count"] for stage in reality_stages]
    fig, left = plt.subplots(figsize=(8.6, 4.8))
    style(left)
    right = left.twinx()
    right.tick_params(colors=PALETTE["muted"])
    right.spines["right"].set_color("#315063")
    left.plot(reality_iteration, compiled_depth, marker="D", linewidth=2.5, color=PALETTE["coral"], label="Profondeur compilée")
    left.plot(reality_iteration, compiled_size, marker="o", linewidth=2.5, color=PALETTE["blue"], label="Taille compilée")
    right.bar(reality_iteration, swap_count, alpha=0.45, color=PALETTE["mint"], label="SWAP explicites")
    left.set_title("Grover Reality Mode — coût de transpilation FakeSherbrooke")
    left.set_xlabel("Itération Grover")
    left.set_ylabel("Opérations / profondeur")
    right.set_ylabel("Nombre de SWAP", color=PALETTE["text"])
    left.set_xticks(reality_iteration)
    lines = left.lines + right.containers
    labels = [line.get_label() for line in left.lines] + [container.get_label() for container in right.containers]
    legend = left.legend(lines, labels, frameon=False, loc="upper left")
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "grover-hardware-aware.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
