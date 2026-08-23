"""A local three-qubit Grover experiment with a separate RATISS sidecar."""
from __future__ import annotations

import argparse
import json
import os
import sys
from math import pi
from pathlib import Path
from typing import Any


def _topological_qubit(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.logical_qubit import TopologicalQubit
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the Studio Cloud src directory.") from error
    return TopologicalQubit


def build_grover_circuit(iterations: int):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import grover_operator

    oracle = QuantumCircuit(3, name="phase_oracle_111")
    oracle.ccz(0, 1, 2)
    operator = grover_operator(oracle)
    circuit = QuantumCircuit(3)
    circuit.h(range(3))
    for _ in range(iterations):
        circuit.compose(operator, inplace=True)
    circuit.measure_all()
    return circuit


def sample(circuit, *, noise_probability: float, shots: int, seed: int) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    model = NoiseModel()
    model.add_all_qubit_quantum_error(depolarizing_error(noise_probability, 2), ["cx"])
    simulator = AerSimulator(noise_model=model, seed_simulator=seed)
    compiled = transpile(circuit, simulator, optimization_level=0, seed_transpiler=seed)
    counts = simulator.run(compiled, shots=shots, seed_simulator=seed).result().get_counts()
    return {str(key): int(value) for key, value in counts.items()}


def marked_mass(counts: dict[str, int], marked: str = "111") -> float:
    total = sum(counts.values())
    return 0.0 if total == 0 else counts.get(marked, 0) / total


def run_experiment(TopologicalQubit: Any, *, shots: int, noise: float, seed: int) -> dict[str, Any]:
    sidecar = TopologicalQubit(seed=seed)
    stages: list[dict[str, Any]] = []
    for iteration in range(3):
        circuit = build_grover_circuit(iteration)
        ideal = sample(circuit, noise_probability=0.0, shots=shots, seed=seed)
        noisy = sample(circuit, noise_probability=noise, shots=shots, seed=seed)
        if iteration > 0:
            sidecar.h_gate().phase_gate(pi / 3).noise(noise)
        stages.append({
            "iteration": iteration,
            "circuit_depth": circuit.depth(),
            "ideal_counts": ideal,
            "noisy_counts": noisy,
            "ideal_marked_mass": marked_mass(ideal),
            "noisy_marked_mass": marked_mass(noisy),
            "ratiss_logical_sidecar": sidecar.measure_state(),
        })
    return {
        "schema": "ratiss.grover.sidecar.v1",
        "provenance": {
            "execution": "local_qiskit_aer_simulation",
            "validated_on_hardware": False,
            "claim_boundary": "Grover outcomes and RATISS sidecar are recorded separately; no claim of quantum optimization by LCT.",
            "seed": seed,
            "cx_depolarizing_probability": noise,
        },
        "marked_state": "111",
        "stages": stages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Grover plus RATISS sidecar experiment.")
    parser.add_argument("--engine-src")
    parser.add_argument("--output", default="artifacts/grover_ratiss.json")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--noise", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0.0 <= args.noise <= 1.0:
        raise ValueError("--noise must be in [0, 1].")
    TopologicalQubit = _topological_qubit(args.engine_src)
    document = run_experiment(TopologicalQubit, shots=args.shots, noise=args.noise, seed=args.seed)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(f"Wrote {destination} with {len(document['stages'])} Grover stages.")


if __name__ == "__main__":
    main()
