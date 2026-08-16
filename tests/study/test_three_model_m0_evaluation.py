from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml

from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[2]
QUALIFICATION = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"
ENTRYPOINT = ROOT / "scripts/study/run_three_model_m0_evaluation.py"
BUILDER = ROOT / "scripts/evaluation/build_three_model_m0_configs.py"
SCIENTIFIC_MANIFEST = ROOT / "configs/evaluation/m0_scientific_three_model_v1.yaml"


def _module():
    spec = importlib.util.spec_from_file_location("three_model_m0_operator", ENTRYPOINT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _builder_module():
    spec = importlib.util.spec_from_file_location("three_model_m0_builder", BUILDER)
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


def test_committed_scientific_family_has_three_models_and_24_parallel_lanes() -> None:
    module = _module()
    family = module.build_three_model_plan(SCIENTIFIC_MANIFEST, repo_root=ROOT)
    assert family["status"] == "frozen"
    assert family["execution_authorized"] is False
    assert family["model_count"] == 3
    assert family["total_lane_count"] == 24
    assert family["parallel_models"] == 3
    for row in family["models"]:
        config = yaml.safe_load(Path(row["config_path"]).read_text(encoding="utf-8"))
        assert config["classification"] == "scientific_evaluation"
        assert config["execution_ready"] is True
        assert config["execution_authorized"] is False
        assert config["parallel_evaluation"]["data_preflight"]["mode"] == (
            "frozen_offline_reuse"
        )
        assert config["parallel_evaluation"]["data_preflight"][
            "network_retrieval_authorized"
        ] is False
        lanes = config["parallel_evaluation"]["lanes"]
        assert len(lanes) == 8
        assert all("limit" not in lane for lane in lanes)
        assert {lane["adapter"] for lane in lanes} == {
            "lm_eval",
            "project_corpus_perplexity",
            "project_factual",
            "project_generation_integrity",
        }


def test_scientific_config_generator_reproduces_committed_bytes(tmp_path: Path) -> None:
    builder = _builder_module()
    source = ROOT / "configs/evaluation/m0_scientific_model_matrix_v1.yaml"
    generated_manifest = builder.build_configs(tmp_path, source)
    assert sha256_file(generated_manifest) == sha256_file(SCIENTIFIC_MANIFEST)
    committed_dir = ROOT / "configs/evaluation/m0_scientific"
    generated_dir = tmp_path / "configs/evaluation/m0_scientific"
    assert {
        path.name: sha256_file(path) for path in sorted(generated_dir.glob("*.yaml"))
    } == {
        path.name: sha256_file(path) for path in sorted(committed_dir.glob("*.yaml"))
    }
