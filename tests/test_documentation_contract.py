import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_grover_artifact_preserves_raw_stage_outputs_and_dynamic_sidecar():
    document = json.loads((ROOT / "artifacts" / "grover_ratiss.json").read_text(encoding="utf-8"))
    stages = document["stages"]
    assert document["provenance"]["validated_on_hardware"] is False
    assert len(stages) == 3
    assert all(sum(stage["ideal_counts"].values()) == 512 for stage in stages)
    assert len({stage["ratiss_logical_sidecar"]["P_sig"] for stage in stages}) > 1


def test_grover_documentation_figures_exist():
    assets = ROOT / "docs" / "assets"
    assert (assets / "grover-marked-mass.png").is_file()
    assert (assets / "grover-ratiss-sidecar.png").is_file()
    assert (assets / "grover-reality-mode.png").is_file()
    assert (assets / "grover-hardware-aware.png").is_file()


def test_reality_mode_keeps_fake_backend_scope_and_separate_sensitivity_flag():
    nominal = json.loads((ROOT / "artifacts" / "grover_reality_mode.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((ROOT / "artifacts" / "grover_reality_mode_sensitivity.json").read_text(encoding="utf-8"))
    assert nominal["provenance"]["validated_on_hardware"] is False
    assert nominal["backend_calibration_snapshot"]["backend_mode"] == "local_fake_backend_snapshot"
    assert len(nominal["stages"]) == 3
    assert all(sum(stage["observed_counts"].values()) == 512 for stage in nominal["stages"])
    assert all(stage["observed_counts_association"]["P_sig"] == 0.0 for stage in nominal["stages"])
    assert not any(stage["reality_flag"]["triggered"] for stage in nominal["stages"])
    assert sensitivity["stages"][-1]["reality_flag"]["triggered"] is True
