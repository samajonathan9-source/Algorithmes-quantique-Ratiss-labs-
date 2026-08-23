from pathlib import Path
import importlib.util


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_grover_ratiss.py"
SPEC = importlib.util.spec_from_file_location("grover_ratiss", MODULE)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_grover_circuit_has_three_qubits_and_measurements():
    circuit = module.build_grover_circuit(1)
    assert circuit.num_qubits == 3
    assert circuit.count_ops()["measure"] == 3


def test_marked_mass_uses_raw_counts():
    assert module.marked_mass({"111": 7, "000": 1}) == 0.875
