from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml

from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[2]
QUALIFICATION = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"
ENTRYPOINT = ROOT / "scripts/study/run_three_model_m0_evaluation.py"


def _module():
    spec = importlib.util.spec_from_file_location("three_model_m0_operator", ENTRYPOINT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_three_model_operator_builds_distinct_scientific_plans_and_stays_fail_closed(
    tmp_path: Path,
) -> None:
    module = _module()
    base = yaml.safe_load(QUALIFICATION.read_text(encoding="utf-8"))
    family_root = Path("/vol/tmp2/yesildau/pytest-three-model-family")
    identities = {
        "olmo": ("allenai/OLMo-2-0425-1B", "a" * 40, "/vol/tmp2/olmo.json"),
        "qwen": ("Qwen/Qwen2.5-1.5B", "b" * 40, "/vol/tmp2/qwen.json"),
        "smollm": ("HuggingFaceTB/SmolLM2-1.7B", "c" * 40, "/vol/tmp2/smollm.json"),
    }
    model_rows = {}
    manifest_digests = {"olmo": "a" * 64, "qwen": "b" * 64, "smollm": "c" * 64}
    for model_id, (repository, revision, manifest_path) in identities.items():
        config = copy.deepcopy(base)
        config["name"] = f"scientific-{model_id}"
        config["classification"] = "scientific_evaluation"
        config["execution_ready"] = True
        config["execution_authorized"] = False
        config["model"]["repository"] = repository
        config["model"]["revision"] = revision
        config["model"]["historical_manifest_path"] = manifest_path
        config["model"]["historical_manifest_sha256"] = manifest_digests[model_id]
        for lane in config["parallel_evaluation"]["lanes"]:
            lane.pop("limit", None)
        config["parallel_evaluation"]["data_preflight"].update(
            {
                "mode": "frozen_offline_reuse",
                "network_retrieval_authorized": False,
                "source_cache_root": "/vol/tmp2/yesildau/frozen-cache",
                "source_content_manifest": "/vol/tmp2/yesildau/frozen-manifest.jsonl",
                "source_content_manifest_sha256": "d" * 64,
                "source_cache_files": 1,
                "source_cache_bytes": 1,
            }
        )
        config["storage"]["proposed_root"] = str(family_root / model_id)
        path = tmp_path / f"{model_id}.yaml"
        path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        model_rows[model_id] = {
            "repository": repository,
            "config": str(path),
            "config_sha256": sha256_file(path),
        }
    manifest = {
        "schema_version": 1,
        "name": "three-model-test",
        "status": "frozen",
        "execution_authorized": False,
        "family_root": str(family_root),
        "model_order": ["olmo", "qwen", "smollm"],
        "models": model_rows,
    }
    manifest_path = tmp_path / "family.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    plan = module.build_three_model_plan(manifest_path, repo_root=ROOT)
    assert plan["model_order"] == ["olmo", "qwen", "smollm"]
    assert plan["model_count"] == 3
    assert plan["total_lane_count"] == 21
    assert plan["parallel_models"] == 3
    assert len({row["plan_id"] for row in plan["models"]}) == 3
    assert all(row["execution_authorized"] is False for row in plan["models"])
