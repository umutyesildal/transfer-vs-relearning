from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from transfer_vs_relearning.utils.io import sha256_file, write_csv


def _probe_rows(prefix: str, count: int) -> list[dict[str, str]]:
    return [
        {
            "probe_id": f"{prefix}_{index}",
            "subject_id": f"S{index}",
            "fact_id": f"S{index}_profession",
            "direction": "tr_to_en",
            "relation": "profession",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "branch_group": "A",
            "frequency_bucket": "low",
            "name_type": "neutral",
            "name_rarity_bucket": "rare",
            "popularity_bucket": "low",
            "correct_rank_mean": "1",
        }
        for index in range(count)
    ]


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    registry = []
    results_root = tmp_path / "results" / "m2_clean_seed42"
    for slice_index in range(2):
        probe_path = tmp_path / f"slice_{slice_index}.csv"
        rows = _probe_rows(f"slice{slice_index}", 2)
        write_csv(probe_path, rows)
        registry.append(
            {
                "slice_id": f"slice_{slice_index}",
                "path": str(probe_path),
                "sha256": sha256_file(probe_path),
                "probe_count": 2,
            }
        )
        result_dir = results_root / f"slice_{slice_index}"
        result_dir.mkdir(parents=True)
        write_csv(result_dir / "hard_suite_per_fact.csv", rows)
        (result_dir / "summary.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        (result_dir / "run_manifest.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    registry_path = tmp_path / "slice_registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    manifest_path = tmp_path / "evaluation_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "slice_count": 2,
                "probes_per_state": 4,
                "analysis_bootstrap_samples": 25,
                "analysis_bootstrap_seed": 7,
                "states": [
                    {
                        "state_id": "m2_clean_seed42",
                        "arm": "m2_clean",
                        "seed": "42",
                        "results_root": str(results_root),
                    }
                ],
                "baseline_states": [],
            }
        ),
        encoding="utf-8",
    )
    return manifest_path, registry_path, results_root


def test_assembler_writes_state_csv_and_manifest(tmp_path: Path) -> None:
    manifest, registry, _ = _fixture(tmp_path)
    output = tmp_path / "assembled"
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/m2/assemble_qwen_m2_m3_results.py"),
            "--evaluation-manifest",
            str(manifest),
            "--slice-registry",
            str(registry),
            "--output-dir",
            str(output),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    payload = json.loads((output / "assembly_manifest.json").read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert payload["probes_per_state"] == 4
    assert len((output / "states/m2_clean_seed42/per_probe_results.csv").read_text().splitlines()) == 5


def test_assembler_refuses_incomplete_slice_without_creating_output(tmp_path: Path) -> None:
    manifest, registry, results_root = _fixture(tmp_path)
    (results_root / "slice_1" / "summary.json").unlink()
    output = tmp_path / "assembled"
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/m2/assemble_qwen_m2_m3_results.py"),
            "--evaluation-manifest",
            str(manifest),
            "--slice-registry",
            str(registry),
            "--output-dir",
            str(output),
        ],
        check=False,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert not output.exists()


def test_empty_retry_preparation_maps_only_empty_targets(tmp_path: Path) -> None:
    manifest, registry, results_root = _fixture(tmp_path)
    empty_root = tmp_path / "empty-results" / "m2_clean_seed42"
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_payload["states"][0]["results_root"] = str(empty_root)
    manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
    output = tmp_path / "retry_manifest.json"
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/m2/prepare_qwen_m2_m3_empty_retry.py"),
            "--evaluation-manifest",
            str(manifest),
            "--slice-registry",
            str(registry),
            "--task-ids",
            "0",
            "--required-state",
            "m2_clean_seed42",
            "--output-manifest",
            str(output),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "ready_for_fresh_preflight"
    assert payload["task_ids"] == [0]
    assert payload["entries"][0]["state_id"] == "m2_clean_seed42"
