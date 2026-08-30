from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from transfer_vs_relearning.pipeline.m2_training_outputs import M2_CHECKPOINT_UPDATES
from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[1]


def test_m2_eval_v2_matrix_has_60_dense_12_full_and_three_projected_parents(tmp_path: Path) -> None:
    results = []
    for role in ("olmo", "qwen", "smollm"):
        for arm in ("M2-A", "M2-B"):
            root = tmp_path / role / arm.lower().replace("-", "_")
            root.mkdir(parents=True)
            checkpoints = []
            for update in M2_CHECKPOINT_UPDATES:
                model_manifest = root / f"update-{update}.json"
                model_manifest.write_text(
                    json.dumps({"role": role, "arm": arm, "update": update}), encoding="utf-8"
                )
                checkpoints.append(
                    {
                        "update": update,
                        "model_manifest": str(model_manifest),
                        "model_manifest_sha256": sha256_file(model_manifest),
                    }
                )
            checkpoint_manifest = root / "checkpoint_manifest.json"
            checkpoint_manifest.write_text(
                json.dumps(
                    {
                        "status": "M2_CHECKPOINT_BINDING_PASS",
                        "role": role,
                        "arm": arm,
                        "checkpoints": checkpoints,
                    }
                ),
                encoding="utf-8",
            )
            results.append(
                {
                    "role": role,
                    "arm": arm,
                    "checkpoint_manifest": str(checkpoint_manifest),
                    "checkpoint_manifest_sha256": sha256_file(checkpoint_manifest),
                }
            )
    family = tmp_path / "family.json"
    family.write_text(
        json.dumps({"status": "M2_TRAINING_FAMILY_BINDING_PASS", "results": results}),
        encoding="utf-8",
    )
    output = tmp_path / "matrix.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/m2/prepare_m2_oscar_eval_v2_matrix.py"),
            "--preparation-config",
            str(ROOT / "configs/evaluation/m2_oscar_three_model_eval_v2_preparation_v1.yaml"),
            "--training-family-manifest",
            str(family),
            "--repo-root",
            str(ROOT),
            "--output",
            str(output),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": f"{ROOT / 'src'}:{ROOT}"},
        capture_output=True,
        text=True,
    )
    matrix = json.loads(output.read_text(encoding="utf-8"))
    assert matrix["status"] == "M2_EVAL_V2_MATRIX_PREPARED_NOT_AUTHORIZED"
    assert matrix["task_count"] == 60
    assert matrix["full_task_count"] == 12
    assert matrix["unique_scientific_states"] == 63
    assert {row["update"] for row in matrix["tasks"] if row["full"]} == {381, 762}
    assert all("pile_10k" not in row["dense_bundles"] for row in matrix["tasks"])
    assert matrix["execution_adapter_registered"] is False
    assert matrix["ready_to_evaluate"] is False
