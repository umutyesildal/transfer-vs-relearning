import json
from pathlib import Path

from transfer_vs_relearning.data.qwen_scale_probe import build_qwen_scale_probe_dataset


def test_qwen_scale_probe_builds_2500_fact_hybrid_and_four_form_registry(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = build_qwen_scale_probe_dataset(root, output_dir=tmp_path / "probe")
    manifest = json.loads((output / "dataset_manifest.json").read_text())
    assert manifest["facts"] == 2500
    assert manifest["train_rows"] == 17500
    assert manifest["four_form_probes"] == 20000
    assert manifest["monitoring_validation_rows"] == 2301
