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


def test_grover_qpu_validation_artifact_is_real_hardware_with_traceable_jobs():
    import os
    document_path = ROOT / "artifacts" / "grover_qpu_validation.json"
    if not document_path.is_file():
        import pytest
        pytest.skip("grover_qpu_validation.json absent (requires IBM_QUANTUM_TOKEN to regenerate)")
    document = json.loads(document_path.read_text(encoding="utf-8"))
    assert document["schema"] == "ratiss.grover.qpu_validation.v1"
    assert document["provenance"]["validated_on_hardware"] is True
    assert len(document["provenance"]["job_ids"]) == len(document["stages"])
    for stage in document["stages"]:
        flag = stage["reality_flag"]
        assert flag["triggered"] == (flag["lct_divergence"] > flag["threshold"])
    raw = document_path.read_text(encoding="utf-8")
    assert "IBM_QUANTUM_TOKEN" not in raw
    token = os.environ.get("IBM_QUANTUM_TOKEN", "")
    assert token == "" or token not in raw


def test_reality_mode_keeps_fake_backend_scope_and_separate_sensitivity_flag():
    nominal = json.loads((ROOT / "artifacts" / "grover_reality_mode.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((ROOT / "artifacts" / "grover_reality_mode_sensitivity.json").read_text(encoding="utf-8"))
    assert nominal["provenance"]["validated_on_hardware"] is False
    assert nominal["backend_calibration_snapshot"]["backend_mode"] == "local_fake_backend_snapshot"
    assert len(nominal["stages"]) == 3
    assert all(sum(stage["observed_counts"].values()) == 512 for stage in nominal["stages"])
    assert all(stage["observed_counts_association"]["P_sig"] == 0.0 for stage in nominal["stages"])
    # La règle du flag est ce qui est contractualisé : il se déclenche quand
    # la divergence calculée dépasse strictement le seuil déclaré. Depuis la
    # correction du sidecar (moteur PR #1 : cycles dégénérés, géométrie
    # dilatante, bruit 0.2), le scénario nominal 0.15 se déclenche réellement
    # aux itérations 1 et 2 — ce résultat corrigé est conservé, pas masqué.
    for document in (nominal, sensitivity):
        for stage in document["stages"]:
            flag = stage["reality_flag"]
            assert flag["triggered"] == (flag["lct_divergence"] > flag["threshold"])
    assert nominal["provenance"]["profile"]["reality_flag_lct_threshold"] == 0.15
    assert sensitivity["provenance"]["profile"]["reality_flag_lct_threshold"] == 0.02
    assert sensitivity["stages"][-1]["reality_flag"]["triggered"] is True
