<p align="center">
  <img src="docs/brand/ratiss-labs-grover-logo.png" alt="RATISS Labs — Grover amplification of |111⟩ inside the topological sidecar ring" width="240"/>
</p>

<h1 align="center">Algorithmes quantiques RATISS Labs</h1>

<p align="center">
  <strong>Quantum-circuit experiment bench</strong><br/>
  Grover under Aer simulation · ideal/noisy comparison · hardware-aware Reality Mode —<br/>
  RATISS topological sidecar read in a strictly separate stream.
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-42d6ad?style=for-the-badge"></a>
  <img alt="Python ≥ 3.11" src="https://img.shields.io/badge/Python-%E2%89%A5%203.11-79b8ff?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Qiskit 2.5.2" src="https://img.shields.io/badge/Qiskit-2.5.2-6929c4?style=for-the-badge&logo=ibm&logoColor=white">
  <img alt="Qiskit Aer 0.17.2" src="https://img.shields.io/badge/Qiskit%20Aer-0.17.2-6929c4?style=for-the-badge&logo=ibm&logoColor=white">
  <img alt="Qiskit IBM Runtime 0.49.0" src="https://img.shields.io/badge/IBM%20Runtime-0.49.0-6929c4?style=for-the-badge&logo=ibm&logoColor=white">
  <img alt="Deterministic reproducibility" src="https://img.shields.io/badge/Reproducibility-deterministic-ff927d?style=for-the-badge">
</p>

<p align="center">
  <em>Architect & principal investigator: <strong>Jonathan Evina</strong> ·
  <a href="https://orcid.org/0009-0000-4092-5313">ORCID 0009-0000-4092-5313</a></em>
</p>

---

## Table of contents

1. [Nature of the experiment bench](#1-nature-of-the-experiment-bench)
2. [Claim boundary](#2-claim-boundary)
3. [Experiment 1 — Grover and RATISS sidecar](#3-experiment-1--grover-and-ratiss-sidecar)
4. [Experiment 2 — Hardware-aware Reality Mode](#4-experiment-2--hardware-aware-reality-mode)
5. [Sidecar correction and regeneration](#5-sidecar-correction-and-regeneration)
6. [Experiment 3 — Validation against a real IBM QPU](#6-experiment-3--validation-against-a-real-ibm-qpu)
7. [Technology stack](#7-technology-stack)
8. [Quick start and reproduction](#8-quick-start-and-reproduction)
9. [Tests](#9-tests)
10. [Laboratory documents](#10-laboratory-documents)
11. [Citation and license](#11-citation-and-license)

---

## 1. Nature of the experiment bench

This laboratory concretely verifies a simple trajectory: a phase oracle and the Grover diffusion amplify the marked state `|111⟩` in the ideal simulator; a declared noise channel modifies the distribution. The RATISS side does not replace Grover: it produces a **second stream of software topological variables**, explicitly separate from the quantum algorithm.

| Project type | Quantum object | RATISS object | Research output |
|---|---|---|---|
| Reproducible quantum algorithm | Grover search, phase oracle for `|111⟩` | Algorithmic `TopologicalQubit` | Counts, marked-state mass, phase, coherence and logical `P_sig` |

## 2. Claim boundary

> **No line in this repository claims that LCT optimises Grover, corrects noise or describes a hardware topological qubit.** The sidecar is a versioned algorithmic simulation. Reality Mode uses a packaged fake backend (`FakeSherbrooke`) as a local source of topology and noise; no QPU job is submitted, and the Reality Flag is not a real-hardware diagnosis.

## 3. Experiment 1 — Grover and RATISS sidecar

![Grover marked-state mass](docs/assets/grover-marked-mass.png)

The mint curve represents the ideal Aer counts; the coral curve comes from the same circuit under depolarising CX noise `p=0.02`. The observed mass of `|111⟩` reaches `0.962891` at iteration 2 in the ideal case and `0.677734` under this declared noise.

![Coherence and P_sig of the RATISS sidecar](docs/assets/grover-ratiss-sidecar.png)

This figure does not represent a property computed from the Grover state alone. It tracks the `TopologicalQubit` sidecar at the iteration clock. Its `P_sig` oscillates freely according to its transformations; it is not fixed to follow the Grover mass.

| Iteration | Ideal `|111⟩` mass | Noisy `|111⟩` mass | RATISS logical `P_sig` | Logical coherence |
|---:|---:|---:|---:|---:|
| 0 | 0.117188 | 0.107422 | 0.182162 | 1.00 |
| 1 | 0.769531 | 0.669922 | 0.646956 | 0.98 |
| 2 | 0.962891 | 0.677734 | 0.668866 | 0.96 |

These values come from [`artifacts/grover_ratiss.json`](artifacts/grover_ratiss.json), with seed `42` and `512` shots. They may change when the configuration, seed, noise, oracle or shot count change; the repository retains the configuration alongside the outputs.

## 4. Experiment 2 — Hardware-aware Reality Mode

![Observed mass and LCT divergence Reality Mode](docs/assets/grover-reality-mode.png)

Reality Mode adds a second protocol, separate from the historical experiment: Qiskit transpiles Grover toward the *target* and coupling topology packaged by `FakeSherbrooke`, then Aer uses the local noise model derived from this fake backend. The declared physical layout is `[0, 14, 26]`; the compiled depth goes from `4` to `330` then `533` at iterations 0, 1 and 2. The transpiler exported no explicit `swap` in this run, but decomposed the circuit into the target gate set.

![Hardware-aware transpilation cost](docs/assets/grover-hardware-aware.png)

The monitor receives the observed counts, builds a separate RATISS counts association, then compares the marked mass and the ideal/observed sidecars. Its **Reality Flag** is a declared LCT condition, not a real-QPU diagnosis. Since the sidecar correction (see §5), the nominal threshold `0.15` is exceeded at iterations 1 and 2 (divergences `0.169988` and `0.526472`); the separate sensitivity scenario, at threshold `0.02`, triggers at the same iterations.

| Iteration | Ideal mass | Observed fake-backend mass | Compiled depth | Nominal LCT divergence | Nominal Reality Flag | Counts association P_sig |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.117188 | 0.121094 | 4 | 0.000000 | No | 0.0 |
| 1 | 0.769531 | 0.339844 | 330 | 0.169988 | **Yes** | 0.0 |
| 2 | 0.962891 | 0.298828 | 533 | 0.526472 | **Yes** | 0.0 |

## 5. Sidecar correction and regeneration

> **Laboratory transparency.** Previous artifacts displayed an initial sidecar signature of `1.214413`. This value came from a known bug in `TopologicalQubit` — degenerate cycles (birth ≈ death, ~1e-16) counted as persistent — fixed in the engine ([PR #1](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine/pull/1): `1e-9` tolerance, dilating geometry twist 0→π, noise amplitude `0.2`). The untwisted compact ring now yields `P_sig ≈ 0.18`, and the sidecar genuinely reacts to the measured degradation. All artifacts in this repository have been regenerated with the corrected engine; the values above are the corrected values, retained without adjustment.

## 6. Experiment 3 — Validation against a real IBM QPU

The offline Reality Mode (`FakeSherbrooke`, §4) remains the reproducible reference without network. A second validation submits the **three iterations** of the Grover circuit (`oracle |111⟩`) to a **real IBM backend** and compares the LCT divergence between the local Aer simulation and the real hardware outcome. The artifact [`artifacts/grover_qpu_validation.json`](artifacts/grover_qpu_validation.json) retains the **traceable Job IDs** per iteration, the hardware counts and the Reality Flag computed against real hardware.

```bash
IBM_QUANTUM_TOKEN=... python3 scripts/run_grover_qpu_validation.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --backend ibm_marrakesh --shots 512
```

> **Claim boundary.** The Reality Flag compares the Aer simulation to real hardware; it does not certify the hardware and is not an IBM anomaly diagnosis. The **LCT-ETH coupling is not applied here**: it requires a density matrix (available in [COSMOS](https://github.com/evinajonathan13-max/QPU-Ratiss-COSMOS), not in Grover counts). This is the honest transdisciplinary boundary between the two laboratories. The IBM token is read only from the `IBM_QUANTUM_TOKEN` environment variable; it is never written into the artifact, the repository or any log.

| Iteration | Ideal mass | Noisy Aer mass | **Real QPU** mass | Aer divergence | QPU divergence | Reality Flag (0.15) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.125 | 0.107 | 0.139 | 0.000000 | 0.000000 | No |
| 1 | 0.781 | 0.670 | 0.676 | 0.003899 | 0.003493 | No |
| 2 | 0.945 | 0.678 | **0.727** | 0.109358 | 0.059000 | No |

> **Honest reading.** At iteration 2, the real QPU `ibm_marrakesh` reaches a marked mass of `0.727` — **higher** than the noisy Aer simulation (`0.678`). The real hardware converges better toward the marked state than Aer's depolarising channel `p=0.02`: the real hardware noise is, on this circuit and this backend, less degrading than the declared noise model. The LCT divergences stay below the nominal threshold `0.15` at all three iterations. Three traceable Job IDs are retained in the artifact: `da5uajeaa69c739latgg`, `da5uituaa69c739lb6m0`, `da5ujreaa69c739lb7m0`.

### Classical counts diagnostic

A classical diagnostic (Shannon + TVD) complements the dominant mass. At iteration 2, the **real-QPU TVD** (`0.273`) is lower than Aer's (`0.322`): the full hardware distribution diverges less from the ideal than the simulation, not just the marked mass. This diagnostic is labelled `classical_counts_diagnostic_not_quantum_entropy` — the Shannon entropy of counts is not the von Neumann entropy, and `ETH` cannot be approximated from counts without tomography (exponential explosion refused).

## 7. Technology stack

| Layer | Technology | Role |
|---|---|---|
| Language | Python ≥ 3.11 | Full experiment bench |
| Quantum simulation | Qiskit 2.5.2 · Qiskit Aer 0.17.2 | Grover sampling, declared noise channels |
| Fake backend | Qiskit IBM Runtime 0.49.0 (`FakeSherbrooke`) | Target, coupling map, local noise model — offline |
| Topology | Vietoris-Rips (GF(2), RATISS engine) | Counts association, `P_sig` |
| Sidecar | `TopologicalQubit` (RATISS engine, corrected) | Separate software topological variables |
| Visualisation | Matplotlib | Figures derived exclusively from JSON artifacts |
| Tests | pytest | Data contracts and Reality Flag rule |
| Artifacts | Versioned JSON | `ratiss.grover.sidecar.v1`, `ratiss.grover.reality_mode.v1` |

The source topological engine ([`ratiss-topological-decoherence-engine`](https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine)) is an **explicit local-path** dependency — provenance stays visible.

## 8. Quick start and reproduction

```bash
git clone https://github.com/evinajonathan13-max/Algorithmes-quantique-Ratiss-labs-.git
git clone https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine.git
cd Algorithmes-quantique-Ratiss-labs-
python3 -m pip install -e .

# Experiment 1: Grover + sidecar
PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_ratiss.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_ratiss.json --shots 512

# Experiment 2: nominal Reality Mode (threshold 0.15)
PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode.json --shots 512

# Experiment 2b: sensitivity scenario (threshold 0.02)
PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode_sensitivity.json \
  --reality-flag-lct-threshold 0.02

# Figures derived from artifacts only
python3 scripts/generate_docs_figures.py
```

Two successive runs of the same artifact produce **bit-for-bit identical** content.

## 9. Tests

```bash
PYTHONPATH=../ratiss-topological-decoherence-engine/src python3 -m pytest -q
```

Tests verify that the circuit stays at three qubits with three measurements, that the marked mass is derived from provided counts (not a constant), that artifacts retain raw outputs, and that the Reality Flag exactly follows the declared rule `divergence > threshold` in both scenarios.

## 10. Laboratory documents

| Document | What it provides |
|---|---|
| [`PROTOCOL.md`](docs/PROTOCOL.md) | Oracle construction and authorised comparisons |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Grover / RATISS sidecar separation |
| [`RESULTS.md`](docs/RESULTS.md) | Exact observations from the current run |
| [`VISUAL_AUDIT.md`](docs/VISUAL_AUDIT.md) | Verified reading of figures |
| [`REALITY_MODE.md`](docs/REALITY_MODE.md) | Fake-backend contract, Reality Flag and threshold scenarios |
| [`REALITY_MODE_VISUAL_AUDIT.md`](docs/REALITY_MODE_VISUAL_AUDIT.md) | Verification of Reality Mode figures |

## 11. Citation and license

Distributed under the [MIT License](LICENSE) — © 2026 Jonathan Evina.

```bibtex
@software{evina_ratiss_labs_grover_2026,
  author  = {Evina, Jonathan},
  title   = {Algorithmes quantiques RATISS Labs: Reproducible Grover
             and RATISS Logical-Sidecar Experiments},
  year    = {2026},
  url     = {https://github.com/evinajonathan13-max/Algorithmes-quantique-Ratiss-labs-},
  note    = {Reproducible local simulation; no hardware execution.}
}
```
