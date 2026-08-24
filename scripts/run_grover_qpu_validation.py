"""Validate the RATISS Grover sidecar against a real IBM Quantum QPU.

Submits the three-iteration Grover search (oracle for |111>) to a real hardware
backend, stores the counts and a traceable Job ID per iteration, and compares
the LCT divergence between the local Aer simulation and the observed hardware
outcome. The Reality Flag is the same declared condition as in the offline
FakeSherbrooke mode, now computed against real hardware counts.

The IBM token is read from the IBM_QUANTUM_TOKEN environment variable only;
it is never written into the artifact, the repository or any log line.

Frontiere de revendication : on compare la simulation Aer au materiel reel,
on ne certifie pas le materiel, et le Reality Flag reste une condition de
simulation. Le couplage LCT-ETH n'est pas applique ici : il requiert une
matrice densite (disponible dans COSMOS, pas dans des counts Grover).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


def _engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.correlation_import import run_qiskit_counts_trajectory
        from ratiss_topological_decoherence.logical_qubit import TopologicalQubit
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the engine src directory.") from error
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


def run_aer(circuit, *, shots: int, seed: int) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(0.02, 2), ["cx"])
    simulator = AerSimulator(noise_model=noise, seed_simulator=seed)
    compiled = transpile(circuit, simulator, optimization_level=0, seed_transpiler=seed)
    counts = simulator.run(compiled, shots=shots, seed_simulator=seed).result().get_counts()
    return {str(k): int(v) for k, v in counts.items()}


def run_qpu(circuit, *, backend_name: str, shots: int) -> tuple[dict[str, int], str, str]:
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        raise RuntimeError("IBM_QUANTUM_TOKEN environment variable is required for QPU validation.")
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend(backend_name)
    compiled = transpile(circuit, backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    job = sampler.run([(compiled,)], shots=shots)
    job_id = job.job_id() if callable(getattr(job, "job_id", None)) else job.job_id
    result = job.result()
    pubs = result[0].data
    field = next(iter(pubs.__dict__))
    raw = pubs.__dict__[field].get_counts()
    counts = {str(k): int(v) for k, v in raw.items()}
    return counts, job_id, backend.name


def sidecar_pair(TopologicalQubit: Any, *, iteration: int, observed_degradation: float, seed: int) -> tuple[dict, dict]:
    expected = TopologicalQubit(seed=seed)
    observed = TopologicalQubit(seed=seed)
    for _ in range(iteration):
        expected.h_gate().phase_gate(math.pi / 3)
        observed.h_gate().phase_gate(math.pi / 3).noise(observed_degradation)
    return expected.measure_state(), observed.measure_state()


def lct_divergence(*, ideal_mass: float, observed_mass: float, expected_sidecar: dict, observed_sidecar: dict) -> dict:
    mass_gap = abs(ideal_mass - observed_mass)
    expected_psig = float(expected_sidecar["P_sig"])
    observed_psig = float(observed_sidecar["P_sig"])
    psig_gap = abs(expected_psig - observed_psig)
    scale = max(abs(expected_psig * float(expected_sidecar["coherence"])), 1e-12)
    return {
        "ideal_marked_mass": ideal_mass,
        "observed_marked_mass": observed_mass,
        "marked_mass_gap": mass_gap,
        "expected_sidecar_P_sig": expected_psig,
        "observed_sidecar_P_sig": observed_psig,
        "sidecar_P_sig_gap": psig_gap,
        "lct_divergence": (mass_gap * psig_gap) / scale,
    }


def run_validation(engine_src: str | None, *, backend_name: str, shots: int, seed: int,
                   lct_threshold: float) -> dict[str, Any]:
    TopologicalQubit, run_qiskit_counts_trajectory = _engine(engine_src)
    stages: list[dict[str, Any]] = []
    for iteration in range(3):
        circuit = build_grover_circuit(iteration)
        ideal = {"111": 0, "000": 0}
        # Ideal Grover mass is deterministic from the unitary (no noise).
        aer_counts = run_aer(circuit, shots=shots, seed=seed)
        qpu_counts, job_id, backend_name = run_qpu(circuit, backend_name=backend_name, shots=shots)

        ideal_mass = marked_mass(aer_counts) if iteration == 0 else _ideal_grover_mass(iteration)
        aer_mass = marked_mass(aer_counts)
        qpu_mass = marked_mass(qpu_counts)

        aer_degradation = 0.0 if ideal_mass == 0.0 else max(0.0, min(1.0, (ideal_mass - aer_mass) / ideal_mass))
        qpu_degradation = 0.0 if ideal_mass == 0.0 else max(0.0, min(1.0, (ideal_mass - qpu_mass) / ideal_mass))

        expected_sidecar, aer_sidecar = sidecar_pair(TopologicalQubit, iteration=iteration, observed_degradation=aer_degradation, seed=seed)
        _, qpu_sidecar = sidecar_pair(TopologicalQubit, iteration=iteration, observed_degradation=qpu_degradation, seed=seed)

        aer_div = lct_divergence(ideal_mass=ideal_mass, observed_mass=aer_mass, expected_sidecar=expected_sidecar, observed_sidecar=aer_sidecar)
        qpu_div = lct_divergence(ideal_mass=ideal_mass, observed_mass=qpu_mass, expected_sidecar=expected_sidecar, observed_sidecar=qpu_sidecar)

        qpu_association = run_qiskit_counts_trajectory({
            "source": {"mode": "grover_qpu_validation", "iteration": iteration, "job_id": job_id},
            "trajectory": [{"step": iteration, "label": f"grover_qpu_iter_{iteration}", "counts": qpu_counts}],
        })
        qpu_counts_psig = qpu_association["steps"][0]["topology"]["psig"]

        flag_triggered = bool(qpu_div["lct_divergence"] > lct_threshold)
        stages.append({
            "iteration": iteration,
            "circuit_depth": circuit.depth(),
            "ideal_marked_mass": ideal_mass,
            "aer_counts": aer_counts,
            "aer_marked_mass": aer_mass,
            "aer_divergence": aer_div,
            "qpu_job_id": job_id,
            "qpu_counts": qpu_counts,
            "qpu_marked_mass": qpu_mass,
            "qpu_divergence": qpu_div,
            "qpu_counts_association_P_sig": qpu_counts_psig,
            "qpu_counts_association_scope": "classical_counts_association_not_density_matrix_tomography",
            "reality_flag": {
                "triggered": flag_triggered,
                "threshold": lct_threshold,
                "lct_divergence": qpu_div["lct_divergence"],
                "message": ("Reality Flag: observed QPU divergence exceeds the declared LCT threshold."
                            if flag_triggered
                            else "Reality Flag inactive: observed QPU divergence stays at or below the declared LCT threshold."),
                "scope": "Real QPU observation; not a hardware anomaly diagnosis or error correction.",
            },
        })
    return {
        "schema": "ratiss.grover.qpu_validation.v1",
        "provenance": {
            "execution": "ibm_quantum_platform_qpu_submission",
            "validated_on_hardware": True,
            "claim_boundary": "Real QPU counts compared to local Aer simulation; the Reality Flag compares, it does not certify hardware. LCT-ETH coupling is not applied here: it requires a density matrix (available in COSMOS, not in Grover counts).",
            "backend": backend_name,
            "shots": shots,
            "seed": seed,
            "reality_flag_lct_threshold": lct_threshold,
            "job_ids": [s["qpu_job_id"] for s in stages],
        },
        "marked_state": "111",
        "stages": stages,
    }


def _ideal_grover_mass(iteration: int) -> float:
    """Deterministic ideal Grover marked-state probability for 3 qubits, 1 solution."""
    from math import asin, sin
    theta = asin(1 / 8 ** 0.5)
    return float(sin((2 * iteration + 1) * theta) ** 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the RATISS Grover sidecar against a real IBM QPU.")
    parser.add_argument("--engine-src")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--output", default="artifacts/grover_qpu_validation.json")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reality-flag-lct-threshold", type=float, default=0.15)
    args = parser.parse_args()
    document = run_validation(args.engine_src, backend_name=args.backend, shots=args.shots,
                              seed=args.seed, lct_threshold=args.reality_flag_lct_threshold)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {destination} — {len(document['stages'])} Grover stages, Job IDs: {document['provenance']['job_ids']}")


if __name__ == "__main__":
    main()
