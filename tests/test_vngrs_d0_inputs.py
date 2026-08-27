import hashlib
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_inputs import load_source_objects, load_synthetic_surfaces


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_real_source_registry_and_relation_v2_surfaces_load_exactly() -> None:
    registry_path = ROOT / "artifacts/corpora/vngrs_m2_d0/source_registry_byte_semantics_repair_v1.json"
    objects = load_source_objects(registry_path, expected_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest())
    assert len(objects) == 32
    assert sum(row.size_bytes for row in objects) == 9_502_315_428
    validation = ROOT / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl"
    surfaces = load_synthetic_surfaces(validation, expected_sha256=hashlib.sha256(validation.read_bytes()).hexdigest())
    assert len(surfaces) == 600
    assert sum(key.startswith("subject:") for key in surfaces) == 100
    assert sum(key.startswith("object:") for key in surfaces) == 500
