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
