from __future__ import annotations

"""Fail-closed execution adapter for the frozen 63-state OSCAR M2 eval-v2 wave."""

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Iterable

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.parquet_loader_v3 import (
    load_verified_parquet_documents_v3,
)
from transfer_vs_relearning.study.m1_eval_validation import (
    derive_cheap_factual_from_full,
    validate_exact_prefix_output,
    validate_factual_output,
    validate_generation_output,
    validate_harness_output,
)
from transfer_vs_relearning.evaluation.turkish_bridge_analysis import (
    direction_metrics,
    paired_subject_bootstrap_accuracy_difference,
)
from transfer_vs_relearning.study.m1_wave_executor import (
    DATASET_CACHE_ROOT,
    DATASET_CONTENT_MANIFEST,
    DATASET_CONTENT_MANIFEST_SHA256,
    FROZEN_INPUTS,
    RUNTIME_LOCK,
    RUNTIME_LOCK_SHA256,
    RUNTIME_PYTHON,
    _run,
    _write_exact_config,
    _write_generation_config,
)
from transfer_vs_relearning.study.m2_gpu_gate import assert_allocated_gpu_memory
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_json


M2_TASK_COUNT = 60
GPU_TASK_COUNT = 63
FULL_TASK_COUNT = 12
PARENT_STATE_COUNT = 3
TOTAL_STATE_COUNT = 63
ROLES = ("olmo", "qwen", "smollm")
ARMS = ("M2-A", "M2-B")
UPDATES = (76, 152, 229, 305, 381, 457, 533, 610, 686, 762)
FULL_UPDATES = {381, 762}
OSCAR_HELDOUT_DOCUMENTS = 10_000


def _yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML mapping required: {path}")
    return payload


def _verify(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or path.is_symlink() or sha256_file(path) != expected:
        raise ValueError(f"M2 eval-v2 frozen input drift: {label} / {path}")


def select_heldout_documents(
    documents: Iterable[D0Document], heldout_ids: set[str]
) -> list[D0Document]:
    selected = sorted(
        (
            row
            for row in documents
            if row.corpus == "oscar" and row.stable_document_id in heldout_ids
        ),
        key=lambda row: row.stable_document_id,
    )
    observed = [row.stable_document_id for row in selected]
    if len(selected) != OSCAR_HELDOUT_DOCUMENTS or set(observed) != heldout_ids:
        raise ValueError("Exact 10,000-document OSCAR held-out population was not reconstructed")
    if len(observed) != len(set(observed)):
        raise ValueError("OSCAR held-out population contains duplicate stable IDs")
    return selected


def materialize_oscar_heldout(config: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct only the frozen held-out text under the fresh evaluation root."""

    source = config["oscar_source"]
    source_root = Path(source["root"])
    metadata_root = Path(source["metadata_root"])
    split_file = Path(source["heldout_ids"])
    _verify(
        source_root / "control/materialization_v3.json",
        source["materialization_manifest_sha256"],
        "oscar_materialization_manifest",
    )
    _verify(split_file, source["heldout_ids_sha256"], "oscar_heldout_ids")
    _verify(
        metadata_root / "shard_metadata_ledger.jsonl",
        source["metadata_ledger_sha256"],
        "oscar_source_metadata_ledger",
    )
    heldout_rows = read_jsonl(split_file)
    heldout_ids = {str(row.get("stable_document_id", "")) for row in heldout_rows}
    if len(heldout_rows) != OSCAR_HELDOUT_DOCUMENTS or len(heldout_ids) != OSCAR_HELDOUT_DOCUMENTS:
        raise ValueError("Frozen OSCAR held-out ID registry is not exactly 10,000 unique rows")
    documents = load_verified_parquet_documents_v3(
        source_root, load_source_objects_v3(metadata_root), execution_enabled=True
    )
    selected = select_heldout_documents(documents, heldout_ids)
    root = Path(config["output_root"])
    output = root / "corpora/oscar_heldout_10000.jsonl"
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".jsonl.tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        for row in selected:
            handle.write(
                json.dumps(
                    {"stable_document_id": row.stable_document_id, "text": row.text},
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
    os.replace(temporary, output)
    result = {
        "schema_version": 1,
        "status": "M2_OSCAR_HELDOUT_MATERIALIZATION_PASS",
        "source_access": "read_only",
        "source_manifest_sha256": source["materialization_manifest_sha256"],
        "metadata_ledger_sha256": source["metadata_ledger_sha256"],
        "heldout_ids_sha256": source["heldout_ids_sha256"],
        "document_count": len(selected),
        "output": str(output),
        "output_sha256": sha256_file(output),
        "utf8_bytes": sum(len(row.text.encode("utf-8")) for row in selected),
    }
    write_json(root / "control/oscar_heldout_materialization.json", result)
    return result


def build_matrix(
    *,
    repo_root: Path,
    config_path: Path,
    contract_path: Path,
    contract_sha256: str,
    expected_commit: str,
    authorization_ack: str,
) -> dict[str, Any]:
    repo = repo_root.resolve()
    config_path = config_path.resolve()
    contract_path = contract_path.resolve()
    config = _yaml(config_path)
    if authorization_ack != "exact_sha_bound_user_authorization_received":
        raise PermissionError("Exact SHA-bound M2 eval-v2 authorization acknowledgement is absent")
    observed_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if observed_commit != expected_commit or dirty:
        raise ValueError("Repository commit/cleanliness gate failed before M2 eval-v2")
    _verify(contract_path, contract_sha256, "authorized_contract")
    source_matrix = Path(config["matrix"]["path"])
    _verify(source_matrix, config["matrix"]["sha256"], "training_family_eval_matrix")
    source = json.loads(source_matrix.read_text(encoding="utf-8"))
    tasks = source.get("tasks")
    if (
        source.get("status") != "M2_EVAL_V2_MATRIX_PREPARED_NOT_AUTHORIZED"
        or not isinstance(tasks, list)
        or len(tasks) != M2_TASK_COUNT
        or sum(bool(row.get("full")) for row in tasks) != FULL_TASK_COUNT
    ):
        raise ValueError("Frozen M2 evaluation matrix is incomplete or drifted")
    identities = {(str(row["role"]), str(row["arm"]), int(row["update"])) for row in tasks}
    expected = {(role, arm, update) for role in ROLES for arm in ARMS for update in UPDATES}
    if identities != expected:
        raise ValueError("M2 eval-v2 matrix does not bind the exact sibling trajectories")
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(tasks):
        manifest = Path(str(row["model_manifest"]))
        _verify(manifest, str(row["model_manifest_sha256"]), f"checkpoint[{index}]")
        normalized.append(
            {
                **row,
                "task_index": index,
                "model": row["role"],
                "checkpoint_id": f"{row['arm'].lower().replace('-', '')}-update-{int(row['update']):03d}",
            }
        )
    parent = config["m1_parent_projection"]
    parent_path = repo / parent["source"]
    _verify(parent_path, parent["source_sha256"], "m1_parent_projection")
    parent_payload = json.loads(parent_path.read_text(encoding="utf-8"))
    endpoint_states = {
        str(row["model"]): row
        for row in parent_payload.get("states", [])
        if row.get("checkpoint") == "epoch-036"
    }
    if set(endpoint_states) != set(ROLES):
        raise ValueError("M1 projection dump does not bind three epoch-036 parents")
    for role in ROLES:
        task_result = endpoint_states[role].get("task_result", {}).get("data", {})
        manifest = Path(str(task_result.get("model_manifest", "")))
        manifest_sha256 = str(task_result.get("model_manifest_sha256", ""))
        _verify(manifest, manifest_sha256, f"m1_parent[{role}]")
        normalized.append(
            {
                "task_index": len(normalized),
                "task_kind": "m1_parent_oscar_baseline_only",
                "state_id": f"{role}/M1-parent",
                "role": role,
                "model": role,
                "arm": "M1",
                "update": 0,
                "full": False,
                "checkpoint_id": "m1-parent-oscar",
                "model_manifest": str(manifest),
                "model_manifest_sha256": manifest_sha256,
            }
        )
    matrix = {
        "schema_version": 1,
        "status": "M2_EVAL_V2_READY",
        "repo_root": str(repo),
        "output_root": config["output"]["root"],
        "authorization": {
            "contract": str(contract_path),
            "contract_sha256": contract_sha256,
            "config": str(config_path),
            "config_sha256": sha256_file(config_path),
            "expected_commit": expected_commit,
            "authorization_ack": authorization_ack,
        },
        "source_matrix": str(source_matrix),
        "source_matrix_sha256": sha256_file(source_matrix),
        "oscar_source": config["oscar_source"],
        "m1_parent_projection": {**parent, "path": str(parent_path)},
        "tasks": normalized,
        "gpu_task_count": GPU_TASK_COUNT,
        "m2_task_count": M2_TASK_COUNT,
        "full_task_count": FULL_TASK_COUNT,
        "parent_state_count": PARENT_STATE_COUNT,
        "total_state_count": TOTAL_STATE_COUNT,
    }
    return matrix


def initialize(matrix: dict[str, Any]) -> Path:
    root = Path(matrix["output_root"])
    if root.exists():
        raise FileExistsError(f"Fresh M2 eval-v2 root already exists: {root}")
    for relative in ("cache", "control", "corpora", "logs", "results", "tmp"):
        (root / relative).mkdir(parents=True)
    path = root / "control/task_matrix.json"
    write_json(path, matrix)
    return path


def load_matrix(path: Path) -> dict[str, Any]:
    matrix = json.loads(path.read_text(encoding="utf-8"))
    if (
        matrix.get("status") != "M2_EVAL_V2_READY"
        or len(matrix.get("tasks", [])) != GPU_TASK_COUNT
        or matrix.get("total_state_count") != TOTAL_STATE_COUNT
    ):
        raise ValueError("Invalid canonical M2 eval-v2 task matrix")
    return matrix


def preflight(matrix: dict[str, Any]) -> dict[str, Any]:
    root = Path(matrix["output_root"])
    authorization = matrix["authorization"]
    observed_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=matrix["repo_root"], check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=matrix["repo_root"], check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if (
        observed_commit != authorization["expected_commit"]
        or authorization["authorization_ack"] != "exact_sha_bound_user_authorization_received"
        or dirty
    ):
        raise ValueError("Repository/authorization gate failed in M2 eval-v2 preflight")
    _verify(Path(authorization["contract"]), authorization["contract_sha256"], "contract")
    _verify(Path(authorization["config"]), authorization["config_sha256"], "config")
    _verify(Path(matrix["source_matrix"]), matrix["source_matrix_sha256"], "matrix")
    _verify(RUNTIME_LOCK, RUNTIME_LOCK_SHA256, "runtime_lock")
    _verify(DATASET_CONTENT_MANIFEST, DATASET_CONTENT_MANIFEST_SHA256, "dataset_manifest")
    if not RUNTIME_PYTHON.is_file() or not DATASET_CACHE_ROOT.is_dir():
        raise FileNotFoundError("Frozen eval-v2 runtime/cache is absent")
    repo = Path(matrix["repo_root"])
    for label, (value, expected) in FROZEN_INPUTS.items():
        path = Path(value)
        _verify(path if path.is_absolute() else repo / path, expected, label)
    for row in matrix["tasks"]:
        _verify(Path(row["model_manifest"]), row["model_manifest_sha256"], row["state_id"])
    heldout = materialize_oscar_heldout(matrix)
    parent_dump = json.loads(Path(matrix["m1_parent_projection"]["path"]).read_text(encoding="utf-8"))
    baseline_rows: list[dict[str, Any]] = []
    for role in ROLES:
        candidates = [
            row for row in parent_dump.get("states", [])
            if row.get("model") == role and row.get("checkpoint") == "epoch-036"
        ]
        if len(candidates) != 1:
            raise ValueError(f"M1 endpoint factual baseline is ambiguous: {role}")
        summary = candidates[0].get("factual_full", {})
        summary_path = Path(str(summary.get("path", "")))
        _verify(summary_path, str(summary.get("sha256", "")), f"m1_full_summary[{role}]")
        per_fact = summary_path.parent / "hard_suite_per_fact.csv"
        rows = read_csv_rows(per_fact)
        if len(rows) != 12_000 or len({str(row.get("probe_id")) for row in rows}) != 12_000:
            raise ValueError(f"M1 endpoint factual rows are incomplete: {role}")
        baseline_rows.append(
            {
                "role": role,
                "summary": str(summary_path),
                "summary_sha256": sha256_file(summary_path),
                "per_fact": str(per_fact),
                "per_fact_sha256": sha256_file(per_fact),
                "probe_count": len(rows),
            }
        )
    baseline_registry = root / "control/m1_parent_factual_registry.json"
    write_json(
        baseline_registry,
        {"schema_version": 1, "status": "M1_PARENT_FACTUAL_BASELINE_BOUND_BEFORE_M2_SCORING", "rows": baseline_rows},
    )
    result = {
        "schema_version": 1,
        "status": "M2_EVAL_V2_PREFLIGHT_PASS",
        "heldout": heldout,
        "m1_parent_factual_registry": str(baseline_registry),
        "m1_parent_factual_registry_sha256": sha256_file(baseline_registry),
        "gpu_task_count": GPU_TASK_COUNT,
        "total_state_count": TOTAL_STATE_COUNT,
    }
    write_json(root / "control/preflight_result.json", result)
    return result


def _validate_corpora(root: Path, expected_oscar_sha256: str) -> dict[str, Any]:
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    corpora = summary.get("corpora", {})
    expected = {"wikitext2", "oscar_heldout", "trwiki_cross_domain"}
    if summary.get("status") != "completed" or set(corpora) != expected:
        raise ValueError("Three-corpus BPB result is incomplete")
    if corpora["oscar_heldout"].get("corpus_sha256") != expected_oscar_sha256:
        raise ValueError("OSCAR held-out BPB source drift")
    if int(corpora["oscar_heldout"].get("document_count", -1)) != OSCAR_HELDOUT_DOCUMENTS:
        raise ValueError("OSCAR held-out BPB denominator drift")
    if corpora["trwiki_cross_domain"].get("corpus_sha256") != FROZEN_INPUTS["turkish_corpus"][1]:
        raise ValueError("trwiki control identity drift")
    return {"status": "complete", "summary_sha256": sha256_file(root / "summary.json")}


def run_task(matrix: dict[str, Any], task_index: int) -> dict[str, Any]:
    task = matrix["tasks"][task_index]
    root = Path(matrix["output_root"])
    repo = Path(matrix["repo_root"])
    state = root / "results" / task["role"] / task["checkpoint_id"]
    if state.exists():
        raise FileExistsError(f"M2 eval-v2 state is not fresh: {state}")
    (state / "configs").mkdir(parents=True)
    _verify(Path(task["model_manifest"]), task["model_manifest_sha256"], task["state_id"])
    exact_config = _write_exact_config(task, repo_root=repo, state_root=state)
    generation_config = _write_generation_config(task, repo_root=repo, state_root=state)
    oscar = root / "corpora/oscar_heldout_10000.jsonl"
    heldout_audit = json.loads((root / "control/oscar_heldout_materialization.json").read_text(encoding="utf-8"))
    _verify(oscar, heldout_audit["output_sha256"], "oscar_heldout_materialized")
    if task.get("task_kind") == "m1_parent_oscar_baseline_only":
        result_path = state / "task_result.json"
        command = [
            str(RUNTIME_PYTHON),
            str(repo / "scripts/evaluation/evaluate_corpora_perplexity.py"),
            "--model-manifest", task["model_manifest"],
            "--model-label", f"m1_{task['role']}_parent_oscar",
            "--corpus", f"oscar_heldout={oscar}",
            "--output-dir", str(state / "corpus_perplexity/raw"),
            "--block-size", "512", "--batch-size", "4",
            "--bootstrap-samples", "10000", "--seed", "42",
            "--device", "cuda", "--no-bf16",
        ]
        try:
            memory_gate = assert_allocated_gpu_memory(state / "gpu_identity_audit.json")
            _run(command, repo_root=repo)
            summary_path = state / "corpus_perplexity/raw/summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            row = summary.get("corpora", {}).get("oscar_heldout", {})
            if (
                summary.get("status") != "completed"
                or row.get("corpus_sha256") != heldout_audit["output_sha256"]
                or int(row.get("document_count", -1)) != OSCAR_HELDOUT_DOCUMENTS
            ):
                raise ValueError("M1 parent OSCAR-only baseline is incomplete")
            result = {
                **task,
                "schema_version": 1,
                "status": "complete",
                "memory_gate": memory_gate,
                "oscar_summary_sha256": sha256_file(summary_path),
            }
            write_json(result_path, result)
            return result
        except Exception as exc:
            write_json(
                result_path,
                {**task, "schema_version": 1, "status": "failed", "error": str(exc)},
            )
            raise
    harness_tasks = ["wikitext"]
    if task["full"]:
        harness_tasks.extend(
            ["blimp", "hellaswag", "winogender_female", "winogender_male", "winogender_neutral", "turblimp_core"]
        )
    model_manifest = json.loads(Path(task["model_manifest"]).read_text(encoding="utf-8"))
    model_path = model_manifest.get("local_path_absolute") or model_manifest.get("local_path")
    tokenizer_path = model_manifest.get("tokenizer_source_path_absolute") or model_path
    commands = [
        [
            str(RUNTIME_PYTHON), "-m", "lm_eval", "run", "--model", "hf", "--model_args",
            f"pretrained={model_path}", f"tokenizer={tokenizer_path}", "dtype=float16",
            "trust_remote_code=False", "local_files_only=True", "--tasks", *harness_tasks,
            "--num_fewshot", "0", "--batch_size", "auto:4", "--max_batch_size", "16",
            "--device", "cuda:0", "--seed", "42,42,42,42", "--output_path",
            str(state / "harness/raw"), "--show_config", "--log_samples",
        ],
        [
            str(RUNTIME_PYTHON), str(repo / "scripts/m2/evaluate_pre_m2_frozen_suite.py"),
            "--model-label", f"m2_{task['role']}_{task['checkpoint_id']}", "--model-manifest",
            task["model_manifest"], "--dataset-dir", str(repo / "artifacts/datasets/relation_v2_gate_v1"),
            "--probe-registry", str(repo / FROZEN_INPUTS["full_factual" if task["full"] else "cheap_factual"][0]),
            "--output-dir", str(state / ("factual_full/raw" if task["full"] else "factual_cheap/raw")),
            "--candidate-batch-size", "16", "--checkpoint-interval", "100", "--device", "cuda", "--no-bf16",
        ],
        [
            str(RUNTIME_PYTHON), str(repo / "scripts/evaluation/evaluate_corpora_perplexity.py"),
            "--model-manifest", task["model_manifest"], "--model-label", f"m2_{task['role']}_{task['checkpoint_id']}",
            "--corpus", f"wikitext2={FROZEN_INPUTS['generation_corpus'][0]}",
            "--corpus", f"oscar_heldout={oscar}",
            "--corpus", f"trwiki_cross_domain={FROZEN_INPUTS['turkish_corpus'][0]}",
            "--output-dir", str(state / "corpus_perplexity/raw"), "--block-size", "512",
            "--batch-size", "4", "--bootstrap-samples", "10000", "--seed", "42", "--device", "cuda", "--no-bf16",
        ],
        [str(RUNTIME_PYTHON), str(repo / "scripts/evaluation/evaluate_facts.py"), "--config", str(exact_config)],
        [str(RUNTIME_PYTHON), str(repo / "scripts/evaluation/evaluate_general_capability.py"), "--config", str(generation_config)],
    ]
    result_path = state / "task_result.json"
    try:
        memory_gate = assert_allocated_gpu_memory(state / "gpu_identity_audit.json")
        for command in commands:
            _run(command, repo_root=repo)
        validations: dict[str, Any] = {
            "harness": validate_harness_output(state / "harness/raw", harness_tasks),
            "corpus_perplexity": _validate_corpora(state / "corpus_perplexity/raw", heldout_audit["output_sha256"]),
            "exact_prefix": validate_exact_prefix_output(state / "exact_prefix/raw"),
            "generation_integrity": validate_generation_output(
                state / "generation_integrity/raw",
                expected_prompts=len(read_jsonl(repo / FROZEN_INPUTS["generation_prompts"][0])),
                expected_completions=len(read_jsonl(repo / FROZEN_INPUTS["generation_completions"][0])),
            ),
        }
        if task["full"]:
            full = state / "factual_full/raw"
            validations["factual_full"] = validate_factual_output(full, 12000)
            validations["factual_cheap_derived"] = derive_cheap_factual_from_full(
                full_root=full,
                cheap_root=state / "factual_cheap",
                cheap_registry=repo / FROZEN_INPUTS["cheap_factual"][0],
                cheap_registry_sha256=FROZEN_INPUTS["cheap_factual"][1],
            )
        else:
            validations["factual_cheap"] = validate_factual_output(state / "factual_cheap/raw", 1500)
        result = {
            **task,
            "schema_version": 1,
            "status": "complete",
            "memory_gate": memory_gate,
            "validations": {key: value.get("status") for key, value in validations.items()},
        }
        write_json(result_path, result)
        return result
    except Exception as exc:
        write_json(result_path, {**task, "schema_version": 1, "status": "failed", "error": str(exc)})
        raise


def finalize(matrix: dict[str, Any]) -> dict[str, Any]:
    root = Path(matrix["output_root"])
    rows: list[dict[str, Any]] = []
    for task in matrix["tasks"]:
        path = root / "results" / task["role"] / task["checkpoint_id"] / "task_result.json"
        status = "missing"
        if path.is_file():
            status = json.loads(path.read_text(encoding="utf-8")).get("status", "invalid")
        rows.append({"task_index": task["task_index"], "state_id": task["state_id"], "status": status, "path": str(path), "sha256": sha256_file(path) if path.is_file() else None})
    parent = matrix["m1_parent_projection"]
    parent_path = Path(parent["path"])
    _verify(parent_path, parent["source_sha256"], "m1_parent_projection")
    parent_payload = json.loads(parent_path.read_text(encoding="utf-8"))
    result = {
        "schema_version": 1,
        "status": "M2_EVAL_V2_COMPLETE" if all(row["status"] == "complete" for row in rows) else "M2_EVAL_V2_INCOMPLETE",
        "gpu_task_count": len(rows),
        "gpu_complete_count": sum(row["status"] == "complete" for row in rows),
        "hybrid_m1_parent_states": PARENT_STATE_COUNT,
        "total_scientific_states": TOTAL_STATE_COUNT,
        "m1_parent_projection_source": str(parent_path),
        "m1_parent_projection_sha256": sha256_file(parent_path),
        "m1_parent_source_state_count": parent_payload.get("counts", {}).get(
            "scientific_states"
        ),
        "tasks": rows,
        "automatic_retry": False,
    }
    write_json(root / "control/evaluation_family_result.json", result)
    if result["status"] == "M2_EVAL_V2_COMPLETE":
        write_json(root / "control/scientific_analysis.json", analyze_complete_wave(matrix))
    return result


def _corpus_row(root: Path, label: str) -> dict[str, Any]:
    summary = json.loads((root / "corpus_perplexity/raw/summary.json").read_text(encoding="utf-8"))
    row = summary.get("corpora", {}).get(label)
    if not isinstance(row, dict) or row.get("status") != "completed":
        raise ValueError(f"Missing corpus result: {root}/{label}")
    return row


def analyze_complete_wave(matrix: dict[str, Any]) -> dict[str, Any]:
    root = Path(matrix["output_root"])
    registry_path = root / "control/m1_parent_factual_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    baselines = {row["role"]: row for row in registry.get("rows", [])}
    if set(baselines) != set(ROLES):
        raise ValueError("M1 parent factual registry is incomplete")
    role_results: dict[str, Any] = {}
    for role in ROLES:
        baseline = baselines[role]
        per_fact = Path(baseline["per_fact"])
        _verify(per_fact, baseline["per_fact_sha256"], f"m1_parent_factual[{role}]")
        m1_rows = read_csv_rows(per_fact)
        states = {
            arm: root / "results" / role / f"{arm.lower().replace('-', '')}-update-762"
            for arm in ARMS
        }
        a_rows = read_csv_rows(states["M2-A"] / "factual_full/raw/hard_suite_per_fact.csv")
        b_rows = read_csv_rows(states["M2-B"] / "factual_full/raw/hard_suite_per_fact.csv")
        metrics = {
            state: {
                direction: direction_metrics(rows, direction)
                for direction in ("en_to_en", "tr_to_en", "tr_to_tr")
            }
            for state, rows in (("M1", m1_rows), ("M2-A", a_rows), ("M2-B", b_rows))
        }
        transfer = paired_subject_bootstrap_accuracy_difference(
            m1_rows, a_rows, direction="tr_to_en", samples=10_000, seed=42
        )
        relearning = paired_subject_bootstrap_accuracy_difference(
            a_rows, b_rows, direction="tr_to_en", samples=10_000, seed=42
        )
        m1_oscar = _corpus_row(root / "results" / role / "m1-parent-oscar", "oscar_heldout")
        a_oscar = _corpus_row(states["M2-A"], "oscar_heldout")
        b_oscar = _corpus_row(states["M2-B"], "oscar_heldout")
        parent_dump = json.loads(Path(matrix["m1_parent_projection"]["path"]).read_text(encoding="utf-8"))
        parent_state = next(
            row for row in parent_dump["states"]
            if row.get("model") == role and row.get("checkpoint") == "epoch-036"
        )
        m1_wikitext_bpb = float(parent_state["harness"]["data"]["results"]["wikitext"]["bits_per_byte,none"])
        a_wikitext_bpb = float(_corpus_row(states["M2-A"], "wikitext2")["bits_per_byte"])
        gates = {
            "m2a_oscar_delta_bpb_at_most_minus_0_07400058": float(a_oscar["bits_per_byte"]) - float(m1_oscar["bits_per_byte"]) <= -0.07400058144377693,
            "m2a_wikitext_delta_bpb_at_most_0_32192809": a_wikitext_bpb - m1_wikitext_bpb <= 0.32192809488736235,
            "m2a_en_to_en_drop_at_most_0_05": metrics["M2-A"]["en_to_en"]["top1_accuracy"] - metrics["M1"]["en_to_en"]["top1_accuracy"] >= -0.05,
            "relearning_point_gain_at_least_0_05": float(relearning["estimate"]) >= 0.05,
            "relearning_ci95_low_above_zero": float(relearning["ci95_low"]) > 0.0,
        }
        role_results[role] = {
            "state_metrics": metrics,
            "transfer_m2a_minus_m1_tr_to_en": transfer,
            "relearning_m2b_minus_m2a_tr_to_en": relearning,
            "bits_per_byte": {
                "M1_oscar": m1_oscar["bits_per_byte"],
                "M2-A_oscar": a_oscar["bits_per_byte"],
                "M2-B_oscar": b_oscar["bits_per_byte"],
                "M1_wikitext": m1_wikitext_bpb,
                "M2-A_wikitext": a_wikitext_bpb,
            },
            "gates": gates,
            "all_primary_gates_pass": all(gates.values()),
        }
    return {
        "schema_version": 1,
        "status": "M2_EVAL_V2_SCIENTIFIC_ANALYSIS_COMPLETE",
        "estimands": {"transfer": "M2-A minus M1", "relearning": "M2-B minus M2-A"},
        "paired_subject_bootstrap": {"samples": 10_000, "seed": 42, "direction": "tr_to_en"},
        "roles": role_results,
    }


def submit(matrix_path: Path, *, entrypoint: Path) -> dict[str, Any]:
    matrix = load_matrix(matrix_path)
    root = Path(matrix["output_root"])
    repo = Path(matrix["repo_root"])
    common = ["sbatch", "--parsable", "--account=yesildau", f"--chdir={repo}"]
    preflight_cmd = shlex.join([str(RUNTIME_PYTHON), str(entrypoint), "preflight", "--matrix", str(matrix_path)])
    task_cmd = shlex.join([str(RUNTIME_PYTHON), str(entrypoint), "run-task", "--matrix", str(matrix_path)]) + ' --task-index "$SLURM_ARRAY_TASK_ID"'
    final_cmd = shlex.join([str(RUNTIME_PYTHON), str(entrypoint), "finalize", "--matrix", str(matrix_path)])
    export = f"ALL,HF_HOME={root / 'cache'},HF_DATASETS_CACHE={DATASET_CACHE_ROOT / 'huggingface_datasets'},XDG_CACHE_HOME={root / 'cache'},HF_HUB_OFFLINE=1,HF_DATASETS_OFFLINE=1,TRANSFORMERS_OFFLINE=1,WANDB_MODE=disabled,PYTHONDONTWRITEBYTECODE=1,PYTHONPATH=src"
    # Scheduler validation occurs before the first real submission.
    subprocess.run(["sbatch", "--test-only", "--partition=longrun", "--cpus-per-task=4", "--mem=64G", "--time=08:00:00", "--wrap=true"], check=True)
    subprocess.run(["sbatch", "--test-only", "--partition=gpu", "--gres=gpu:a10080gb:1", "--array=0-62%6", "--cpus-per-task=8", "--mem=64G", "--time=2-12:00:00", "--wrap=true"], check=True)
    preflight_id = subprocess.run([*common, "--partition=longrun", "--job-name=m2-eval-v2-preflight", "--cpus-per-task=4", "--mem=64G", "--time=08:00:00", f"--output={root / 'logs/%x-%j.out'}", f"--error={root / 'logs/%x-%j.err'}", "--export=ALL,PYTHONPATH=src", f"--wrap=exec {preflight_cmd}"], check=True, capture_output=True, text=True).stdout.strip().split(";", 1)[0]
    array_id = subprocess.run([*common, "--partition=gpu", "--gres=gpu:a10080gb:1", "--array=0-62%6", "--job-name=m2-eval-v2-a100", f"--dependency=afterok:{preflight_id}", "--cpus-per-task=8", "--mem=64G", "--time=2-12:00:00", f"--output={root / 'logs/%x-%A_%a.out'}", f"--error={root / 'logs/%x-%A_%a.err'}", f"--export={export}", f"--wrap=exec {task_cmd}"], check=True, capture_output=True, text=True).stdout.strip().split(";", 1)[0]
    finalizer_id = subprocess.run([*common, "--partition=std", "--job-name=m2-eval-v2-finalize", f"--dependency=afterany:{array_id}", "--cpus-per-task=2", "--mem=8G", "--time=01:00:00", f"--output={root / 'logs/%x-%j.out'}", f"--error={root / 'logs/%x-%j.err'}", "--export=ALL,PYTHONPATH=src", f"--wrap=exec {final_cmd}"], check=True, capture_output=True, text=True).stdout.strip().split(";", 1)[0]
    result = {"schema_version": 1, "status": "submitted", "preflight_job_id": preflight_id, "evaluation_array_job_id": array_id, "finalizer_job_id": finalizer_id, "automatic_retry": False}
    write_json(root / "control/submission_manifest.json", result)
    return result
