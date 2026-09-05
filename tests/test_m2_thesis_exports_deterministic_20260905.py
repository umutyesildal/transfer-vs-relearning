from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "evaluation"))

import build_m2_thesis_exports as exports  # noqa: E402


def file_digests(directory: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


def test_m2_exports_are_deterministic_and_closed(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first = exports.build(ROOT, first_dir)
    second = exports.build(ROOT, second_dir)

    assert first["input_manifest_sha256"] == second["input_manifest_sha256"]
    assert file_digests(first_dir) == file_digests(second_dir)
    assert len(first["outputs"]) == 13
    assert all(item["input_manifest_sha256"] == first["input_manifest_sha256"] for item in first["outputs"].values())

    effects = list(__import__("csv").DictReader((first_dir / "primary_effects.csv").open(newline="", encoding="utf-8")))
    headline = {(row["model"], row["contrast"]): float(row["estimate"]) for row in effects}
    assert headline == {
        ("olmo", "transfer"): -0.141,
        ("olmo", "relearning"): 0.020,
        ("qwen", "transfer"): -0.307,
        ("qwen", "relearning"): 0.0435,
        ("smollm", "transfer"): -0.16175,
        ("smollm", "relearning"): 0.0035,
    }

    gates = list(__import__("csv").DictReader((first_dir / "gate_table.csv").open(newline="", encoding="utf-8")))
    assert len(gates) == 18
    assert all(row["pass"] == "false" for row in gates if row["gate_id"] == "all_primary_gates_pass")
    assert "fact_id" not in (first_dir / "m2_results_summary.md").read_text(encoding="utf-8") or "historical `fact_id` bootstrap is superseded" in (first_dir / "m2_results_summary.md").read_text(encoding="utf-8")

    manifest = json.loads((first_dir / "export_manifest.json").read_text(encoding="utf-8"))
    assert manifest["input_manifest_sha256"] == first["input_manifest_sha256"]
    assert set(manifest["outputs"]) >= {"primary_forest.svg", "endpoint_state_comparison.svg", "dose_trajectories.svg", "relation_breakdown.svg", "form_breakdown.svg", "gate_table.md"}
