from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.adapters.m0_evaluation import verify_m0_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


WIKITEXT_TASK = "wikitext"
HEADING_TASK = "wikitext_heading_markdown_sensitivity_v1"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Expected JSONL objects: {path}")
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(row, str) for row in value):
        raise ValueError(f"{label} must be a non-empty string list")
    return list(value)


def _close(left: float, right: float, tolerance: float) -> bool:
    return math.isfinite(left) and math.isfinite(right) and abs(left - right) <= tolerance


def canonical_wikitext_target(doc: dict[str, Any]) -> str:
    string = str(doc["page"])
    string = string.replace("s '", "s'")
    string = re.sub(r"/' [0-9]/", r"/'[0-9]/", string)
    string = string.replace(" @-@ ", "-")
    string = string.replace(" @,@ ", ",")
    string = string.replace(" @.@ ", ".")
    string = string.replace(" : ", ": ")
    string = string.replace(" ; ", "; ")
    string = string.replace(" . ", ". ")
    string = string.replace(" ! ", "! ")
    string = string.replace(" ? ", "? ")
    string = string.replace(" , ", ", ")
    string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
    string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
    string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
    string = re.sub(r'"\s*([^\"]*?)\s*"', r'"\1"', string)
    string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
    string = string.replace("= = = =", "====")
    string = string.replace("= = =", "===")
    string = string.replace("= =", "==")
    string = string.replace(" " + chr(176) + " ", chr(176))
    string = string.replace(" \n", "\n")
    string = string.replace("\n ", "\n")
    string = string.replace(" N ", " 1 ")
    string = string.replace(" 's", "'s")
    return string


def markdown_headings(text: str) -> str:
    converted: list[str] = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        match = re.fullmatch(r"\s*(=+)\s*(.*?)\s*\1\s*", body)
        converted.append(f"{'#' * len(match.group(1))} {match.group(2)}{ending}" if match else line)
    return "".join(converted)


def _metric_pair(row: dict[str, Any], key: str) -> tuple[float, int]:
    value = row.get(key)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"Sample metric is not a [loglikelihood, denominator] pair: {key}")
    return float(value[0]), int(value[1])


def _rolling_aggregates(rows: list[dict[str, Any]]) -> dict[str, float]:
    word_pairs = [_metric_pair(row, "word_perplexity") for row in rows]
    byte_pairs = [_metric_pair(row, "byte_perplexity") for row in rows]
    bit_pairs = [_metric_pair(row, "bits_per_byte") for row in rows]
    loglikelihood = sum(value for value, _ in word_pairs)
    if not all(value == word_pairs[index][0] for index, (value, _) in enumerate(byte_pairs)):
        raise ValueError("WikiText word/byte loglikelihood values differ")
    if not all(value == word_pairs[index][0] for index, (value, _) in enumerate(bit_pairs)):
        raise ValueError("WikiText word/BPB loglikelihood values differ")
    words = sum(count for _, count in word_pairs)
    byte_count = sum(count for _, count in byte_pairs)
    if words <= 0 or byte_count <= 0:
        raise ValueError("WikiText aggregate denominator is not positive")
    return {
        "word_perplexity": math.exp(-loglikelihood / words),
        "byte_perplexity": math.exp(-loglikelihood / byte_count),
        "bits_per_byte": -loglikelihood / (byte_count * math.log(2)),
        "loglikelihood_sum": loglikelihood,
        "word_count": words,
        "byte_count": byte_count,
    }


def _result_and_samples(lane_result_path: Path, *, sample_prefix: str) -> tuple[Path, list[Path]]:
    lane_result = _load_json(lane_result_path)
    if lane_result.get("status") != "complete" or lane_result.get("returncode") != 0:
        raise ValueError(f"Parity source lane is not complete: {lane_result_path}")
    paths: list[Path] = []
    for artifact in lane_result.get("artifacts", []):
        path = Path(str(artifact.get("path", "")))
        if not path.is_file():
            raise FileNotFoundError(f"Parity source artifact is missing: {path}")
        if path.stat().st_size != artifact.get("bytes") or sha256_file(path) != artifact.get(
            "sha256"
        ):
            raise ValueError(f"Parity source artifact identity mismatch: {path}")
        paths.append(path)
    results = [path for path in paths if path.name.startswith("results_") and path.suffix == ".json"]
    samples = [path for path in paths if path.name.startswith(sample_prefix) and path.suffix == ".jsonl"]
    if len(results) != 1 or not samples:
        raise ValueError(f"Parity source result/sample discovery failed: {lane_result_path}")
    return results[0], sorted(samples)


def validate_wikitext_canonical(
    result_path: Path,
    sample_path: Path,
    *,
    tolerance: float,
    expected_sample_count: int,
) -> dict[str, Any]:
    result = _load_json(result_path)
    rows = _read_jsonl(sample_path)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record("sample_count", len(rows) == expected_sample_count, len(rows))
    record("doc_ids", [row.get("doc_id") for row in rows] == list(range(expected_sample_count)), [row.get("doc_id") for row in rows])
    targets_match = True
    counts_match = True
    heading_counts: list[int] = []
    for row in rows:
        canonical = canonical_wikitext_target(_mapping(row.get("doc"), "wikitext sample doc"))
        targets_match = targets_match and row.get("target") == canonical
        raw_page = str(row["doc"]["page"])
        expected_words = len(re.split(r"\s+", raw_page))
        expected_bytes = len(raw_page.encode("utf-8"))
        word_pair = _metric_pair(row, "word_perplexity")
        byte_pair = _metric_pair(row, "byte_perplexity")
        bit_pair = _metric_pair(row, "bits_per_byte")
        counts_match = counts_match and word_pair[1] == expected_words
        counts_match = counts_match and byte_pair[1] == expected_bytes == bit_pair[1]
        heading_counts.append(
            sum(
                re.fullmatch(r"\s*(=+)\s*(.*?)\s*\1\s*", line) is not None
                for line in canonical.splitlines()
            )
        )
    record("canonical_detokenizer_target", targets_match, targets_match)
    record("original_doc_word_and_byte_counts", counts_match, counts_match)
    record("canonical_headings_detected", all(count > 0 for count in heading_counts), heading_counts)
    aggregates = _rolling_aggregates(rows)
    reported = _mapping(result.get("results"), "wikitext results").get(WIKITEXT_TASK, {})
    result_checks = {
        metric: _close(aggregates[metric], float(reported[f"{metric},none"]), tolerance)
        for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
    }
    record("aggregate_metric_parity", all(result_checks.values()), result_checks)
    sample_len = reported.get("sample_len")
    effective = result.get("n-samples", {}).get(WIKITEXT_TASK, {}).get("effective")
    record(
        "result_count_parity",
        sample_len == expected_sample_count == effective,
        {"sample_len": sample_len, "effective": effective},
    )
    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "check_id": "wikitext_canonical_count_and_result_parity",
        "status": "pass" if not blockers else "blocked",
        "tolerance": tolerance,
        "result_path": str(result_path),
        "result_sha256": sha256_file(result_path),
        "sample_path": str(sample_path),
        "sample_sha256": sha256_file(sample_path),
        "checks": checks,
        "blockers": blockers,
        "recomputed": aggregates,
        "reported": {
            metric: reported.get(f"{metric},none")
            for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
        },
        "heading_counts": heading_counts,
    }


def _choice_loglikelihood(value: Any) -> float:
    while isinstance(value, list) and len(value) == 1:
        value = value[0]
    if isinstance(value, list):
        value = value[0]
    return float(value)


def validate_turblimp_macro(
    result_path: Path,
    sample_paths: list[Path],
    *,
    subtask_ids: list[str],
    tolerance: float,
    expected_samples_per_subtask: int,
    group_yaml_path: Path,
) -> dict[str, Any]:
    result = _load_json(result_path)
    group_text = group_yaml_path.read_text(encoding="utf-8")
    duplicate_count = len(re.findall(r"(?m)^aggregate_metric_list:\s*$", group_text))
    effective_group = yaml.safe_load(group_text)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record("duplicate_group_key_observed", duplicate_count == 2, duplicate_count)
    effective_metrics = [row.get("metric") for row in effective_group.get("aggregate_metric_list", [])]
    record("effective_group_metric_is_acc_norm", effective_metrics == ["acc_norm"], effective_metrics)
    observed_subtasks = result.get("group_subtasks", {}).get("turblimp_core")
    record("exact_16_subtask_order", observed_subtasks == subtask_ids, observed_subtasks)
    by_sample_name = {
        path.name.split("samples_", 1)[1].rsplit("_202", 1)[0]: path for path in sample_paths
    }
    per_subtask: dict[str, dict[str, float]] = {}
    sample_checks: dict[str, bool] = {}
    reported_results = _mapping(result.get("results"), "TurBLiMP results")
    for task_id in subtask_ids:
        path = by_sample_name.get(task_id)
        if path is None:
            sample_checks[task_id] = False
            continue
        rows = _read_jsonl(path)
        correct_acc: list[float] = []
        correct_norm: list[float] = []
        correct_bytes: list[float] = []
        row_match = len(rows) == expected_samples_per_subtask
        for row in rows:
            responses = row.get("filtered_resps")
            if not isinstance(responses, list) or len(responses) != 2:
                row_match = False
                continue
            loglikelihoods = [_choice_loglikelihood(value) for value in responses]
            doc = _mapping(row.get("doc"), f"{task_id} sample doc")
            choices = [str(doc["sentence_good"]), str(doc["sentence_bad"])]
            completion_lengths = [len(choice) for choice in choices]
            byte_lengths = [len(choice.encode("utf-8")) for choice in choices]
            predicted = max(range(2), key=lambda index: loglikelihoods[index])
            predicted_norm = max(
                range(2), key=lambda index: loglikelihoods[index] / completion_lengths[index]
            )
            predicted_bytes = max(
                range(2), key=lambda index: loglikelihoods[index] / byte_lengths[index]
            )
            expected_acc = float(predicted == 0)
            expected_norm = float(predicted_norm == 0)
            expected_bytes = float(predicted_bytes == 0)
            row_match = row_match and float(row.get("acc")) == expected_acc
            row_match = row_match and float(row.get("acc_norm")) == expected_norm
            correct_acc.append(expected_acc)
            correct_norm.append(expected_norm)
            correct_bytes.append(expected_bytes)
        if not correct_acc:
            sample_checks[task_id] = False
            continue
        recomputed_acc = sum(correct_acc) / len(correct_acc)
        recomputed_norm = sum(correct_norm) / len(correct_norm)
        reported = reported_results.get(task_id, {})
        row_match = row_match and _close(
            recomputed_acc, float(reported.get("acc,none")), tolerance
        )
        row_match = row_match and _close(
            recomputed_norm, float(reported.get("acc_norm,none")), tolerance
        )
        row_match = row_match and reported.get("sample_len") == expected_samples_per_subtask
        sample_checks[task_id] = row_match
        per_subtask[task_id] = {
            "acc": recomputed_acc,
            "acc_norm": recomputed_norm,
            "acc_bytes_sensitivity": sum(correct_bytes) / len(correct_bytes),
        }
    record("per_sample_and_subtask_metric_parity", all(sample_checks.values()), sample_checks)
    complete_subtask_set = set(per_subtask) == set(subtask_ids)
    record("all_16_subtasks_recomputed", complete_subtask_set, sorted(per_subtask))
    macro_acc = sum(row["acc"] for row in per_subtask.values()) / len(subtask_ids)
    macro_norm = sum(row["acc_norm"] for row in per_subtask.values()) / len(subtask_ids)
    macro_bytes = sum(row["acc_bytes_sensitivity"] for row in per_subtask.values()) / len(
        subtask_ids
    )
    group = reported_results.get("turblimp_core", {})
    group_metric = float(group.get("acc_norm,none"))
    record(
        "unweighted_16_subtask_macro_parity",
        complete_subtask_set and _close(macro_norm, group_metric, tolerance),
        {"recomputed": macro_norm, "reported": group_metric},
    )
    record(
        "group_sample_count",
        group.get("sample_len") == len(subtask_ids) * expected_samples_per_subtask,
        group.get("sample_len"),
    )
    record("group_exposes_only_effective_acc_norm", "acc,none" not in group, sorted(group))
    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "check_id": "turblimp_16_subtask_macro_parity",
        "status": "pass" if not blockers else "blocked",
        "tolerance": tolerance,
        "result_path": str(result_path),
        "result_sha256": sha256_file(result_path),
        "group_yaml_path": str(group_yaml_path),
        "group_yaml_sha256": sha256_file(group_yaml_path),
        "subtask_count": len(subtask_ids),
        "samples_per_subtask": expected_samples_per_subtask,
        "per_subtask": per_subtask,
        "recomputed_macro_acc_sensitivity": macro_acc,
        "recomputed_macro_acc_norm": macro_norm,
        "recomputed_macro_acc_bytes_sensitivity": macro_bytes,
        "reported_macro_acc_norm": group_metric,
        "checks": checks,
        "blockers": blockers,
    }


def load_parity_config(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _mapping(value, "parity config")


def build_parity_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    repo_root = repo_root.resolve()
    config = load_parity_config(config_path)
    if config.get("schema_version") != 1 or config.get("status") not in {"prepared", "frozen"}:
        raise ValueError("Unsupported M0 parity config schema/status")
    if not isinstance(config.get("execution_authorized"), bool):
        raise ValueError("M0 parity execution_authorized must be boolean")
    source = _mapping(config.get("source"), "source")
    for lane_id in ("english_retention_wikitext", "turkish_capability"):
        lane = _mapping(source.get(lane_id), f"source.{lane_id}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(lane.get("lane_result_sha256"))):
            raise ValueError(f"Source lane SHA-256 is invalid: {lane_id}")
    tolerances = _mapping(config.get("tolerances"), "tolerances")
    if not isinstance(tolerances.get("absolute_metric_parity"), float):
        raise ValueError("absolute_metric_parity must be a float")
    turblimp = _mapping(config.get("turblimp"), "turblimp")
    subtasks = _strings(turblimp.get("subtask_ids"), "turblimp.subtask_ids")
    if len(subtasks) != 16 or len(set(subtasks)) != 16:
        raise ValueError("TurBLiMP parity requires exactly 16 unique subtasks")
    runtime = _mapping(config.get("runtime"), "runtime")
    model = _mapping(config.get("model"), "model")
    implementation_files = _mapping(runtime.get("implementation_files") or {}, "implementation_files")
    if config["status"] == "frozen":
        if config["execution_authorized"] is not True:
            raise ValueError("Frozen parity config must be execution-authorized")
        if not re.fullmatch(r"[0-9a-f]{40}", str(runtime.get("implementation_commit"))):
            raise ValueError("Frozen parity config requires an implementation commit")
        for relative, expected in implementation_files.items():
            path = repo_root / relative
            if not path.is_file() or sha256_file(path) != expected:
                raise ValueError(f"Frozen parity implementation file mismatch: {relative}")
    identity = {
        "config_sha256": sha256_file(config_path),
        "source_plan_id": source["plan_id"],
        "model": [model["repository"], model["revision"]],
        "subtasks": subtasks,
    }
    return {
        "schema_version": 1,
        "plan_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "name": config["name"],
        "status": config["status"],
        "execution_authorized": config["execution_authorized"],
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "repo_root": str(repo_root),
        "source": source,
        "model": model,
        "runtime": runtime,
        "slurm": config["slurm"],
        "storage": config["storage"],
        "wikitext": config["wikitext"],
        "turblimp": {**turblimp, "subtask_ids": subtasks},
        "tolerances": tolerances,
        "run_classification": "test_only_non_scientific",
    }


def validate_source_lane(plan: dict[str, Any], lane_id: str) -> tuple[Path, list[Path]]:
    lane = plan["source"][lane_id]
    path = Path(plan["source"]["root"]) / "lanes" / lane_id / "lane_result.json"
    if not path.is_file() or sha256_file(path) != lane["lane_result_sha256"]:
        raise ValueError(f"Parity source lane-result mismatch: {lane_id}")
    lane_result = _load_json(path)
    if (
        lane_result.get("plan_id") != plan["source"]["plan_id"]
        or lane_result.get("lane_id") != lane_id
    ):
        raise ValueError(f"Parity source lane plan/ID mismatch: {lane_id}")
    prefix = "samples_wikitext_" if lane_id == "english_retention_wikitext" else "samples_turblimp_"
    return _result_and_samples(path, sample_prefix=prefix)


def initialize_parity_namespace(plan: dict[str, Any], output_root: Path) -> Path:
    if output_root.exists():
        raise FileExistsError(f"M0 parity namespace already exists: {output_root}")
    output_root.mkdir(parents=True)
    (output_root / "logs").mkdir()
    (output_root / "heading" / "raw").mkdir(parents=True)
    source_cache = Path(plan["source"]["root"]) / "cache"
    shutil.copytree(source_cache, output_root / "cache", copy_function=shutil.copy2)
    write_json(output_root / "parity_plan.json", plan)
    return output_root


def load_initialized_parity_plan(
    output_root: Path, config_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    planned = _load_json(output_root / "parity_plan.json")
    current = build_parity_plan(config_path, repo_root=repo_root)
    if planned.get("plan_id") != current["plan_id"] or planned.get("config_sha256") != current[
        "config_sha256"
    ]:
        raise ValueError("M0 parity plan/config identity changed after submission")
    if current["status"] != "frozen" or current["execution_authorized"] is not True:
        raise PermissionError("M0 parity config is not frozen and authorized")
    return current


def run_structural_parity(plan: dict[str, Any], output_root: Path) -> dict[str, Any]:
    path = output_root / "structural_parity.json"
    if path.exists():
        raise FileExistsError(f"Structural parity output already exists: {path}")
    wiki_result, wiki_samples = validate_source_lane(plan, "english_retention_wikitext")
    tur_result, tur_samples = validate_source_lane(plan, "turkish_capability")
    if len(wiki_samples) != 1:
        raise ValueError("WikiText parity requires exactly one sample artifact")
    upstream = plan["runtime"]["upstream_task_files"]
    for label, row in upstream.items():
        source_path = Path(row["path"])
        if not source_path.is_file() or sha256_file(source_path) != row["sha256"]:
            raise ValueError(f"Pinned upstream task file mismatch: {label}")
    tolerance = float(plan["tolerances"]["absolute_metric_parity"])
    wiki = validate_wikitext_canonical(
        wiki_result,
        wiki_samples[0],
        tolerance=tolerance,
        expected_sample_count=int(plan["wikitext"]["expected_sample_count"]),
    )
    turblimp = validate_turblimp_macro(
        tur_result,
        tur_samples,
        subtask_ids=plan["turblimp"]["subtask_ids"],
        tolerance=tolerance,
        expected_samples_per_subtask=int(plan["turblimp"]["expected_samples_per_subtask"]),
        group_yaml_path=Path(upstream["turblimp_group"]["path"]),
    )
    status = "pass" if wiki["status"] == turblimp["status"] == "pass" else "blocked"
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": status,
        "run_classification": plan["run_classification"],
        "wikitext": wiki,
        "turblimp": turblimp,
        "heading_sensitivity_status": "pending_gpu_run" if status == "pass" else "not_opened",
    }
    write_json(path, payload)
    if status != "pass":
        raise RuntimeError("Structural WikiText/TurBLiMP parity failed")
    return payload


def run_heading_sensitivity(plan: dict[str, Any], output_root: Path) -> dict[str, Any]:
    structural = _load_json(output_root / "structural_parity.json")
    if structural.get("status") != "pass":
        raise PermissionError("Heading sensitivity cannot run before structural parity passes")
    result_path = output_root / "heading" / "heading_run_result.json"
    if result_path.exists():
        raise FileExistsError(f"Heading sensitivity result already exists: {result_path}")
    raw_root = output_root / "heading" / "raw"
    if any(raw_root.iterdir()):
        raise FileExistsError(f"Heading sensitivity raw root is not fresh: {raw_root}")
    _, model_path, tokenizer_path = verify_m0_model_manifest(plan, repo_root=Path(plan["repo_root"]))
    runtime = plan["runtime"]
    overlay = plan["wikitext"]["heading_overlay"]
    command = [
        runtime["python"],
        "-m",
        "lm_eval",
        "run",
        "--model",
        "hf",
        "--model_args",
        f"pretrained={model_path}",
        f"tokenizer={tokenizer_path}",
        f"dtype={runtime['precision']}",
        "trust_remote_code=False",
        "local_files_only=True",
        "--tasks",
        HEADING_TASK,
        "--include_path",
        str(Path(plan["repo_root"]) / overlay["include_path"]),
        "--num_fewshot",
        "0",
        "--batch_size",
        str(runtime["batch_size"]),
        "--max_batch_size",
        str(runtime["max_batch_size"]),
        "--device",
        runtime["device"],
        "--seed",
        "42,42,42,42",
        "--output_path",
        str(raw_root),
        "--show_config",
        "--log_samples",
        "--limit",
        str(plan["wikitext"]["expected_sample_count"]),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "HF_HOME": str(output_root / "cache/huggingface"),
            "HF_DATASETS_CACHE": str(output_root / "cache/huggingface_datasets"),
            "XDG_CACHE_HOME": str(output_root / "cache"),
            "HF_HUB_OFFLINE": "1",
            "HF_DATASETS_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "WANDB_MODE": "disabled",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TMPDIR": str(output_root / "heading" / "tmp"),
        }
    )
    Path(environment["TMPDIR"]).mkdir()
    stdout_path = output_root / "heading" / "stdout.log"
    stderr_path = output_root / "heading" / "stderr.log"
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        completed = subprocess.run(
            command,
            cwd=Path(plan["repo_root"]),
            env=environment,
            stdout=stdout,
            stderr=stderr,
            text=True,
            check=False,
        )
    artifacts = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted((output_root / "heading").rglob("*"))
        if path.is_file() and path.name != "heading_run_result.json"
    ]
    raw_files = [path for path in raw_root.rglob("*") if path.is_file()]
    status = "complete" if completed.returncode == 0 and raw_files else "failed_pre_scoring"
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": status,
        "returncode": completed.returncode,
        "run_classification": plan["run_classification"],
        "task_id": HEADING_TASK,
        "started_at": started_at,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": time.monotonic() - started,
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_node": os.environ.get("SLURMD_NODENAME"),
            "gpu_route_id": os.environ.get("M0_GPU_ROUTE_ID"),
        },
        "artifacts": artifacts,
    }
    write_json(result_path, payload)
    if status != "complete":
        raise RuntimeError(f"WikiText heading sensitivity failed: exit={completed.returncode}")
    return payload


def validate_heading_sensitivity(
    plan: dict[str, Any], output_root: Path, structural: dict[str, Any]
) -> dict[str, Any]:
    run_result = _load_json(output_root / "heading" / "heading_run_result.json")
    if run_result.get("status") != "complete" or run_result.get("returncode") != 0:
        raise ValueError("Heading sensitivity run is not complete")
    artifact_paths: list[Path] = []
    for artifact in run_result.get("artifacts", []):
        path = Path(artifact["path"])
        if not path.is_file() or path.stat().st_size != artifact["bytes"] or sha256_file(path) != artifact[
            "sha256"
        ]:
            raise ValueError(f"Heading sensitivity artifact mismatch: {path}")
        artifact_paths.append(path)
    results = [path for path in artifact_paths if path.name.startswith("results_")]
    samples = [path for path in artifact_paths if path.name.startswith("samples_")]
    if len(results) != 1 or len(samples) != 1:
        raise ValueError("Heading sensitivity result/sample discovery failed")
    result = _load_json(results[0])
    rows = _read_jsonl(samples[0])
    canonical_rows = _read_jsonl(Path(structural["wikitext"]["sample_path"]))
    expected_count = int(plan["wikitext"]["expected_sample_count"])
    target_match = True
    count_match = len(rows) == expected_count
    changed_headings: list[int] = []
    for row in rows:
        canonical = canonical_wikitext_target(_mapping(row.get("doc"), "heading sample doc"))
        expected = markdown_headings(canonical)
        target_match = target_match and row.get("target") == expected
        changed_headings.append(
            sum(left != right for left, right in zip(canonical.splitlines(), expected.splitlines()))
        )
        words = len(re.split(r"\s+", expected))
        byte_count = len(expected.encode("utf-8"))
        count_match = count_match and _metric_pair(row, "word_perplexity")[1] == words
        count_match = count_match and _metric_pair(row, "byte_perplexity")[1] == byte_count
        count_match = count_match and _metric_pair(row, "bits_per_byte")[1] == byte_count
    aggregates = _rolling_aggregates(rows)
    reported = result.get("results", {}).get(HEADING_TASK, {})
    tolerance = float(plan["tolerances"]["absolute_metric_parity"])
    aggregate_match = all(
        _close(aggregates[metric], float(reported[f"{metric},none"]), tolerance)
        for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
    )
    canonical = structural["wikitext"]["recomputed"]
    deltas = {
        metric: aggregates[metric] - float(canonical[metric])
        for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
    }
    checks = {
        "same_source_documents": [
            (row.get("doc_id"), row.get("doc_hash"), row.get("doc")) for row in rows
        ]
        == [
            (row.get("doc_id"), row.get("doc_hash"), row.get("doc"))
            for row in canonical_rows
        ],
        "markdown_target_exact": target_match,
        "variant_denominator_counts": count_match,
        "heading_lines_changed": all(count > 0 for count in changed_headings),
        "variant_aggregate_result_parity": aggregate_match,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        "schema_version": 1,
        "check_id": "wikitext_heading_markdown_sensitivity",
        "status": "pass" if not blockers else "blocked",
        "role": "descriptive_sensitivity_only_no_numeric_gate",
        "checks": checks,
        "blockers": blockers,
        "changed_heading_lines_per_doc": changed_headings,
        "canonical_metrics": {
            metric: canonical[metric]
            for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
        },
        "markdown_metrics": {
            metric: aggregates[metric]
            for metric in ("word_perplexity", "byte_perplexity", "bits_per_byte")
        },
        "markdown_minus_canonical": deltas,
        "result_path": str(results[0]),
        "result_sha256": sha256_file(results[0]),
        "sample_path": str(samples[0]),
        "sample_sha256": sha256_file(samples[0]),
    }


def finalize_parity_bundle(plan: dict[str, Any], output_root: Path) -> dict[str, Any]:
    structural = _load_json(output_root / "structural_parity.json")
    blockers: list[str] = []
    if structural.get("status") != "pass":
        blockers.append("structural_parity")
    try:
        heading = validate_heading_sensitivity(plan, output_root, structural)
    except (FileNotFoundError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        heading = {"status": "blocked", "blockers": [str(exc)]}
    if heading.get("status") != "pass":
        blockers.append("wikitext_heading_sensitivity")
    rows = [
        {
            "check_id": "wikitext_count_result_and_heading_parity",
            "status": "pass" if structural.get("wikitext", {}).get("status") == "pass" and heading.get("status") == "pass" else "blocked",
            "canonical": structural.get("wikitext"),
            "heading_sensitivity": heading,
            "run_classification": plan["run_classification"],
        },
        {
            "check_id": "turblimp_16_subtask_macro_parity",
            "status": structural.get("turblimp", {}).get("status", "blocked"),
            "evidence": structural.get("turblimp"),
            "run_classification": plan["run_classification"],
        },
    ]
    if any(row["status"] != "pass" for row in rows):
        blockers.extend(row["check_id"] for row in rows if row["status"] != "pass")
    blockers = sorted(set(blockers))
    status = "pass" if not blockers else "blocked"
    _write_jsonl(output_root / "parity_results.jsonl", rows)
    write_json(output_root / "heading_sensitivity.json", heading)
    write_json(
        output_root / "parity_manifest.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "config_path": plan["config_path"],
            "config_sha256": plan["config_sha256"],
            "source": plan["source"],
            "model": plan["model"],
            "runtime": plan["runtime"],
            "tolerances": plan["tolerances"],
            "run_classification": plan["run_classification"],
        },
    )
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": status,
        "gate": "parity_pass" if status == "pass" else "blocked",
        "blockers": blockers,
        "run_classification": plan["run_classification"],
        "scientific_result": False,
        "scientific_work_started": False,
        "eval_v1_frozen": False,
        "note": "Parity PASS closes only the two named qualification blockers.",
    }
    write_json(output_root / "parity_result.json", payload)
    inventory = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(output_root.rglob("*"))
        if path.is_file() and path.name != "final_inventory.json"
    ]
    write_json(
        output_root / "final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["final_inventory.json"],
            "file_count": len(inventory),
            "total_bytes": sum(row["bytes"] for row in inventory),
            "files": inventory,
        },
    )
    return payload
