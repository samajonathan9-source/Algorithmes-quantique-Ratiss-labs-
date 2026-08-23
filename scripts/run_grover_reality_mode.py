"""Offline hardware-aware Grover Reality Mode experiment.

This program uses a Qiskit IBM fake backend only as a local source of a target,
coupling map and calibration-shaped noise model.  It does not submit a job to
IBM Quantum and it does not claim the fake backend is a live calibration.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from math import pi
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RealityProfile:
    backend_name: str = "FakeSherbrooke"
    source_physical_qubits: tuple[int, int, int] = (0, 14, 26)
    shots: int = 512
    seed: int = 42
    hidden_extra_cx_depolarizing: float = 0.01
    reality_flag_lct_threshold: float = 0.15


def _engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.correlation_import import run_qiskit_counts_trajectory
        from ratiss_topological_decoherence.logical_qubit import TopologicalQubit
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the Studio Cloud src directory.") from error
    return TopologicalQubit, run_qiskit_counts_trajectory


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


def marked_mass(counts: dict[str, int], marked: str = "111") -> float:
    total = sum(counts.values())
    return 0.0 if total == 0 else counts.get(marked, 0) / total


def _fake_backend(profile: RealityProfile):
    if profile.backend_name != "FakeSherbrooke":
        raise ValueError("This reproducible offline experiment currently declares FakeSherbrooke only.")
    from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

    return FakeSherbrooke()


def _calibration_summary(backend: Any, profile: RealityProfile) -> dict[str, Any]:
    properties = backend.target.qubit_properties
    qubits = []
    for physical in profile.source_physical_qubits:
        prop = properties[physical]
        qubits.append({
            "physical_qubit": physical,
            "t1_seconds": None if prop is None else prop.t1,
            "t2_seconds": None if prop is None else prop.t2,
            "frequency_hz": None if prop is None else prop.frequency,
        })
    coupling_edges = [list(edge) for edge in backend.coupling_map.get_edges()]
    source = set(profile.source_physical_qubits)
    local_edges = [edge for edge in coupling_edges if edge[0] in source or edge[1] in source]
    return {
        "backend": backend.name,
        "backend_mode": "local_fake_backend_snapshot",
        "validated_on_hardware": False,
        "source_physical_qubits": list(profile.source_physical_qubits),
        "qubits": qubits,
        "coupling_edges_touching_source": local_edges,
        "calibration_scope": "Packaged fake-backend properties used locally; not a live IBM calibration query.",
    }


def _counts(circuit: Any, simulator: Any, *, shots: int, seed: int) -> dict[str, int]:
    result = simulator.run(circuit, shots=shots, seed_simulator=seed).result()
    return {str(key): int(value) for key, value in result.get_counts().items()}


def _timeline_dict(value: Any) -> dict[str, Any]:
    return value.to_dict() if hasattr(value, "to_dict") else value


def counts_association(run_qiskit_counts_trajectory: Any, counts: dict[str, int], iteration: int) -> dict[str, Any]:
    document = _timeline_dict(run_qiskit_counts_trajectory({
        "source": {"mode": "grover_reality_mode", "iteration": iteration},
        "trajectory": [{"step": iteration, "label": f"grover_iteration_{iteration}", "counts": counts}],
    }))
    step = document["steps"][0]
    topology = step["topology"]
    return {
        "P_sig": topology["psig"],
        "betti": topology["betti"],
        "finite_h1": topology["n_finite_h1"],
        "scope": "classical_counts_association_not_density_matrix_tomography",
        "timeline": document,
    }


def sidecar_pair(TopologicalQubit: Any, *, iteration: int, observed_degradation: float, seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = TopologicalQubit(seed=seed)
    observed = TopologicalQubit(seed=seed)
    for _ in range(iteration):
        expected.h_gate().phase_gate(pi / 3)
        observed.h_gate().phase_gate(pi / 3).noise(observed_degradation)
    return expected.measure_state(), observed.measure_state()


def reality_flag(*, ideal_marked_mass: float, observed_marked_mass: float, expected_sidecar: dict[str, Any], observed_sidecar: dict[str, Any], observed_counts_psig: float, lct_threshold: float) -> dict[str, Any]:
    mass_gap = abs(ideal_marked_mass - observed_marked_mass)
    expected_psig = float(expected_sidecar["P_sig"])
    observed_psig = float(observed_sidecar["P_sig"])
    psig_gap = abs(expected_psig - observed_psig)
    expected_lct_scale = max(abs(expected_psig * float(expected_sidecar["coherence"])), 1e-12)
    lct_divergence = (mass_gap * psig_gap) / expected_lct_scale
    triggered = bool(lct_divergence > lct_threshold)
    return {
        "triggered": triggered,
        "threshold": lct_threshold,
        "observed_marked_mass_gap": mass_gap,
        "sidecar_P_sig_gap": psig_gap,
        "lct_divergence": lct_divergence,
        "observed_counts_association_P_sig": observed_counts_psig,
        "message": (
            "Reality Flag: observed simulated divergence exceeds the declared LCT threshold."
            if triggered
            else "Reality Flag inactive: observed simulated divergence stays at or below the declared LCT threshold."
        ),
        "scope": "Local fake-backend simulation monitor; not a live hardware anomaly diagnosis.",
    }


def run_experiment(TopologicalQubit: Any, run_qiskit_counts_trajectory: Any, profile: RealityProfile) -> dict[str, Any]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    backend = _fake_backend(profile)
    calibration = _calibration_summary(backend, profile)
    backend_noise = NoiseModel.from_backend(backend)
    if profile.hidden_extra_cx_depolarizing > 0.0:
        backend_noise.add_all_qubit_quantum_error(
            depolarizing_error(profile.hidden_extra_cx_depolarizing, 2), ["cx"]
        )
    noisy_simulator = AerSimulator(noise_model=backend_noise, seed_simulator=profile.seed)
    ideal_simulator = AerSimulator(seed_simulator=profile.seed)
    stages: list[dict[str, Any]] = []
    for iteration in range(3):
        logical_circuit = build_grover_circuit(iteration)
        ideal_compiled = transpile(logical_circuit, ideal_simulator, optimization_level=0, seed_transpiler=profile.seed)
        hardware_compiled = transpile(
            logical_circuit,
            backend,
            initial_layout=list(profile.source_physical_qubits),
            optimization_level=0,
            seed_transpiler=profile.seed,
        )
        ideal_counts = _counts(ideal_compiled, ideal_simulator, shots=profile.shots, seed=profile.seed)
        observed_counts = _counts(hardware_compiled, noisy_simulator, shots=profile.shots, seed=profile.seed)
        ideal_mass = marked_mass(ideal_counts)
        observed_mass = marked_mass(observed_counts)
        observed_degradation = 0.0 if ideal_mass == 0.0 else max(0.0, min(1.0, (ideal_mass - observed_mass) / ideal_mass))
        expected_sidecar, observed_sidecar = sidecar_pair(
            TopologicalQubit,
            iteration=iteration,
            observed_degradation=observed_degradation,
            seed=profile.seed,
        )
        association = counts_association(run_qiskit_counts_trajectory, observed_counts, iteration)
        flag = reality_flag(
            ideal_marked_mass=ideal_mass,
            observed_marked_mass=observed_mass,
            expected_sidecar=expected_sidecar,
            observed_sidecar=observed_sidecar,
            observed_counts_psig=association["P_sig"],
            lct_threshold=profile.reality_flag_lct_threshold,
        )
        stages.append({
            "iteration": iteration,
            "logical_circuit_depth": logical_circuit.depth(),
            "hardware_aware": {
                "compiled_depth": hardware_compiled.depth(),
                "compiled_size": hardware_compiled.size(),
                "swap_count": int(hardware_compiled.count_ops().get("swap", 0)),
                "layout_requested": list(profile.source_physical_qubits),
                "basis_operations": {key: int(value) for key, value in hardware_compiled.count_ops().items()},
            },
            "ideal_counts": ideal_counts,
            "observed_counts": observed_counts,
            "ideal_marked_mass": ideal_mass,
            "observed_marked_mass": observed_mass,
            "observed_degradation_from_counts": observed_degradation,
            "expected_sidecar": expected_sidecar,
            "observed_sidecar": observed_sidecar,
            "observed_counts_association": association,
            "reality_flag": flag,
        })
    return {
        "schema": "ratiss.grover.reality_mode.v1",
        "provenance": {
            "execution": "local_qiskit_aer_with_ibm_fake_backend_noise_model",
            "validated_on_hardware": False,
            "claim_boundary": "Fake-backend topology and packaged calibration-shaped noise are local simulation inputs; Reality Flag is not a hardware diagnosis.",
            "profile": asdict(profile),
            "hidden_ground_truth": {
                "extra_cx_depolarizing_probability": profile.hidden_extra_cx_depolarizing,
                "revealed_only_after_monitoring": True,
            },
        },
        "backend_calibration_snapshot": calibration,
        "marked_state": "111",
        "stages": stages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Grover Reality Mode with an offline IBM fake backend.")
    parser.add_argument("--engine-src")
    parser.add_argument("--output", default="artifacts/grover_reality_mode.json")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--hidden-extra-cx-depolarizing", type=float, default=0.01)
    parser.add_argument("--reality-flag-lct-threshold", type=float, default=0.15)
    args = parser.parse_args()
    if not 0.0 <= args.hidden_extra_cx_depolarizing <= 1.0:
        raise ValueError("--hidden-extra-cx-depolarizing must be in [0, 1].")
    TopologicalQubit, run_qiskit_counts_trajectory = _engine(args.engine_src)
    profile = RealityProfile(
        shots=args.shots,
        seed=args.seed,
        hidden_extra_cx_depolarizing=args.hidden_extra_cx_depolarizing,
        reality_flag_lct_threshold=args.reality_flag_lct_threshold,
    )
    document = run_experiment(TopologicalQubit, run_qiskit_counts_trajectory, profile)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(f"Wrote {destination} with {len(document['stages'])} hardware-aware Grover stages.")


if __name__ == "__main__":
    main()
