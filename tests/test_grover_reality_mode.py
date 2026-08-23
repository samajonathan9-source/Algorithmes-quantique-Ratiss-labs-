import importlib.util
import sys
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_grover_reality_mode.py"
SPEC = importlib.util.spec_from_file_location("grover_reality_mode", MODULE)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_reality_flag_uses_observed_divergence_without_ground_truth_noise():
    expected = {"P_sig": 1.0, "coherence": 1.0}
    observed = {"P_sig": 0.5, "coherence": 0.8}
    flag = module.reality_flag(
        ideal_marked_mass=0.9,
        observed_marked_mass=0.5,
        expected_sidecar=expected,
        observed_sidecar=observed,
        observed_counts_psig=0.0,
        lct_threshold=0.15,
    )
    assert flag["triggered"] is True
    assert flag["observed_marked_mass_gap"] == 0.4
    assert flag["sidecar_P_sig_gap"] == 0.5
    assert flag["observed_counts_association_P_sig"] == 0.0


def test_reality_profile_declares_offline_fake_backend_scope():
    profile = module.RealityProfile()
    assert profile.backend_name == "FakeSherbrooke"
    assert profile.source_physical_qubits == (0, 14, 26)
