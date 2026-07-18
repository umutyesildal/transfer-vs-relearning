from __future__ import annotations

import json
import platform
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import (
    RELATION_TO_FAMILY,
    build_candidate_inventories,
    candidate_for_fact,
    resolve_expected_answer,
)
from transfer_vs_relearning.data.constants import DATASET_FILES
from transfer_vs_relearning.data.facts import expand_canonical_rows
from transfer_vs_relearning.evaluation.progress import load_completed, save_progress
from transfer_vs_relearning.evaluation.prompts import render_prompt_from_config
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.scoring import score_candidate_batch
from transfer_vs_relearning.metrics.core import chance_references, dual_ranking_metrics, subgroup_metrics
from transfer_vs_relearning.metrics.relation_binding import relation_binding_metrics
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, sha256_text, write_csv, write_json


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError:
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    try:
        import yaml
    except ModuleNotFoundError:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=True, allow_unicode=True)


class EvaluationIncompleteError(RuntimeError):
    pass


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_path(path_value: str | Path, base: Path | None = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path.resolve()
    if base is not None:
        return (base / path).resolve()
    return (_project_root() / path).resolve()


def _manifest_local_path(manifest: dict[str, Any], base: Path) -> Path:
    local_path = manifest.get("local_path_absolute") or manifest.get("local_path")
    if local_path is None:
        raise KeyError("Model manifest is missing local_path/local_path_absolute")
    return _resolve_path(local_path, base)


def _resolve_tokenizer_path(manifest: dict[str, Any], manifest_path: Path) -> Path:
    explicit = manifest.get("tokenizer_source_path_absolute") or manifest.get("tokenizer_source_path")
    if explicit:
        return _resolve_path(explicit, manifest_path.parent)

    training_run_dir = manifest.get("training_run_dir")
    if training_run_dir:
        training_manifest_path = _resolve_path(training_run_dir, manifest_path.parent) / "training_manifest.json"
        if training_manifest_path.exists():
            training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
            base_manifest = training_manifest.get("model", {}).get("base_model_manifest_payload", {})
            base_path = base_manifest.get("local_path_absolute") or base_manifest.get("local_path")
            if base_path:
                return _resolve_path(base_path, training_manifest_path.parent)

    return _manifest_local_path(manifest, manifest_path.parent)


def config_fingerprint(config: dict[str, Any], dataset_manifest_hash: str | None = None) -> dict[str, Any]:
    keys = (
        "dataset_version",
        "dataset_dir",
        "pilot_subject_file",
        "probe_files",
        "model_manifest",
        "languages",
        "relations",
        "prompt",
        "scoring",
    )
    payload = {key: config.get(key) for key in keys}
    if dataset_manifest_hash:
        payload["dataset_manifest_hash"] = dataset_manifest_hash
    return payload


def completion_status(expected_probe_count: int, successful_count: int, failed_count: int) -> str:
    return "completed" if successful_count == expected_probe_count and failed_count == 0 else "partial_failed"


def expected_candidate_forward_batches(
    subject_count: int,
    languages: int,
    relation_candidate_counts: dict[str, int],
    candidate_batch_size: int,
) -> int:
    import math

    return subject_count * languages * sum(
        math.ceil(count / candidate_batch_size) for count in relation_candidate_counts.values()
    )


def relation_binding_is_applicable(relations: list[str] | tuple[str, ...]) -> bool:
    return {"born_in", "lives_in"}.issubset(relations)


def with_default_probe_language(
    rows: list[dict[str, Any]], language: str
) -> list[dict[str, Any]]:
    return [{**row, "language": row.get("language") or language} for row in rows]


class CausalCandidateEvaluator:
    def __init__(self, config: dict[str, Any], run_dir: Path):
        self.config = config
        self.run_dir = run_dir
        self.run_id = run_dir.name

    def _load_model(self) -> tuple[Any, Any, str, dict[str, Any]]:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        manifest_path = _resolve_path(self.config["model_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        local_path = str(_manifest_local_path(manifest, manifest_path.parent))
        tokenizer_path = str(_resolve_tokenizer_path(manifest, manifest_path))
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        dtype = torch.bfloat16 if self.config["runtime"].get("bf16") and torch.cuda.is_available() and torch.cuda.is_bf16_supported() else None
        model = AutoModelForCausalLM.from_pretrained(local_path, local_files_only=True, torch_dtype=dtype)
        device = "cuda" if self.config["runtime"].get("device") == "cuda" and torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        return tokenizer, model, device, manifest

    def _score_candidates(
        self,
        tokenizer: Any,
        model: Any,
        device: str,
        prompt: str,
        candidates: list[str],
    ) -> list[dict[str, float | int]]:
        scores: list[dict[str, float | int]] = []
        batch_size = int(self.config["runtime"].get("candidate_batch_size", 64))
        separator = self.config["prompt"].get("answer_separator", " ")
        for start in range(0, len(candidates), batch_size):
            scores.extend(
                score_candidate_batch(
                    tokenizer,
                    model,
                    device,
                    prompt,
                    candidates[start : start + batch_size],
                    separator,
                )
            )
        return scores

    def run(self, resume: bool = False, force: bool = False, allow_errors: bool = False) -> Path:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        dataset_dir = _resolve_path(self.config["dataset_dir"])
        dataset_manifest_path = dataset_dir / "manifest.json"
        dataset_manifest_hash = sha256_file(dataset_manifest_path) if dataset_manifest_path.exists() else None
        fingerprint = config_fingerprint(self.config, dataset_manifest_hash)
        fingerprint_hash = sha256_text(json.dumps(fingerprint, ensure_ascii=False, sort_keys=True))
        resolved_config_path = self.run_dir / "resolved_config.yaml"
        fingerprint_path = self.run_dir / "config_fingerprint.json"
        if resume:
            progress_path = self.run_dir / "progress.json"
            if not progress_path.exists():
                raise FileNotFoundError(f"Cannot resume {self.run_dir}: progress.json is missing")
            existing_progress = json.loads(progress_path.read_text(encoding="utf-8"))
            if existing_progress.get("status") == "completed" and not force:
                raise ValueError(f"{self.run_dir} is already completed; pass --force to rerun/resume intentionally")
            if fingerprint_path.exists():
                existing = json.loads(fingerprint_path.read_text(encoding="utf-8"))
                if existing.get("fingerprint_hash") != fingerprint_hash:
                    raise ValueError("Resume configuration mismatch: dataset/model/pilot/prompt/scoring settings changed")
            if resolved_config_path.exists():
                self.config = _load_yaml(resolved_config_path)
        else:
            if any(self.run_dir.iterdir()):
                raise FileExistsError(f"New run directory is not empty: {self.run_dir}")
            _dump_yaml(resolved_config_path, self.config)
            write_json(fingerprint_path, {"fingerprint_hash": fingerprint_hash, "fingerprint": fingerprint})
        canonical_rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
        canonical_by_subject = {row["subject_id"]: row for row in canonical_rows}
        pilot_path = _resolve_path(self.config["pilot_subject_file"])
        pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
        selected_subjects = set(pilot["selected_subject_ids"])
        write_json(self.run_dir / "selected_subjects_reference.json", pilot)
        probes = []
        probe_files = self.config.get("probe_files", {})
        if "en" in self.config["languages"]:
            probes.extend(
                with_default_probe_language(
                    read_csv_rows(
                        _resolve_path(probe_files["en"])
                        if "en" in probe_files
                        else dataset_dir / DATASET_FILES["probes_en"]
                    ),
                    "en",
                )
            )
        if "tr" in self.config["languages"]:
            probes.extend(
                with_default_probe_language(
                    read_csv_rows(
                        _resolve_path(probe_files["tr"])
                        if "tr" in probe_files
                        else dataset_dir / DATASET_FILES["probes_tr"]
                    ),
                    "tr",
                )
            )
        probes = [
            row
            for row in probes
            if row["subject_id"] in selected_subjects and row["relation"] in self.config["relations"]
        ]

        inventories = build_candidate_inventories(canonical_rows)
        tokenizer, model, device, model_manifest = self._load_model()
        import torch
        import transformers
        completed = load_completed(self.run_dir / "progress.json")
        results: list[dict[str, Any]] = []
        result_csv = self.run_dir / "per_fact_results.csv"
        if result_csv.exists():
            results = read_csv_rows(result_csv)
            seen = set()
            deduped = []
            for row in results:
                key = f"{row['fact_id']}|{row['language']}"
                if key not in seen:
                    deduped.append(row)
                    seen.add(key)
            results = deduped
            completed |= seen

        started = datetime.now(timezone.utc).isoformat()
        expected_probe_count = len(probes)
        attempted_count = 0
        failed_count = 0
        skipped_completed_count = 0
        save_progress(
            self.run_dir / "progress.json",
            completed,
            {"status": "running", "started": started, "expected_probe_count": expected_probe_count},
        )
        errors_path = self.run_dir / "errors.jsonl"
        for index, probe in enumerate(probes, start=1):
            key = f"{probe['fact_id']}|{probe['language']}"
            if key in completed:
                skipped_completed_count += 1
                continue
            attempted_count += 1
            try:
                prompt = render_prompt_from_config(
                    probe["question"],
                    probe["language"],
                    self.config["prompt"],
                )
                family = RELATION_TO_FAMILY[probe["relation"]]
                correct = resolve_expected_answer(probe["relation"], probe["language"], probe["expected_answer"], inventories)
                candidates = inventories[family]
                surfaces = [candidate.surface(probe["language"]) for candidate in candidates]
                candidate_scores = []
                for candidate, scores in zip(candidates, self._score_candidates(tokenizer, model, device, prompt, surfaces)):
                    candidate_scores.append({"object_id": candidate.object_id, "surface": candidate.surface(probe["language"]), **scores})
                ranked_mean = rank_candidates(candidate_scores, "mean_logprob", correct.object_id)
                ranked_total = rank_candidates(candidate_scores, "total_logprob", correct.object_id)
                subject_row = canonical_by_subject[probe["subject_id"]]
                correct_row = next(item for item in candidate_scores if item["object_id"] == correct.object_id)
                row = {
                    "run_id": self.run_id,
                    "model_id": model_manifest["model_id"],
                    "resolved_model_revision": model_manifest["resolved_revision"],
                    "dataset_version": self.config["dataset_version"],
                    "fact_id": probe["fact_id"],
                    "subject_id": probe["subject_id"],
                    "subject": probe["subject"],
                    "language": probe["language"],
                    "relation": probe["relation"],
                    "question": probe["question"],
                    "rendered_prompt": prompt,
                    "expected_answer": probe["expected_answer"],
                    "correct_object_id": correct.object_id,
                    "predicted_object_id": ranked_mean["top1_object_id"],
                    "predicted_surface_form": ranked_mean["top1_surface"],
                    "predicted_object_id_total": ranked_total["top1_object_id"],
                    "predicted_surface_form_total": ranked_total["top1_surface"],
                    "correct_rank_mean": ranked_mean["rank"],
                    "correct_rank_total": ranked_total["rank"],
                    "correct_mean_score": ranked_mean["correct_score"],
                    "correct_total_score": ranked_total["correct_score"],
                    "best_incorrect_mean_score": ranked_mean["best_incorrect_score"],
                    "best_incorrect_total_score": ranked_total["best_incorrect_score"],
                    "margin": ranked_mean["margin"],
                    "total_score_margin": ranked_total["margin"],
                    "token_count": correct_row["token_count"],
                    "branch": probe["branch_group"],
                    "frequency": probe["frequency_bucket"],
                    "popularity": probe["popularity_bucket"],
                    "name_type": probe["name_type"],
                    "name_rarity": probe["name_rarity_bucket"],
                    "template_id": probe["template_id"],
                    "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
                    "number_of_candidates": len(candidate_scores),
                    "top5_candidate_ids": "|".join(ranked_mean["top5_object_ids"]),
                    "top5_candidate_ids_total": "|".join(ranked_total["top5_object_ids"]),
                }
                if probe["relation"] in {"born_in", "lives_in"}:
                    other_relation = "lives_in" if probe["relation"] == "born_in" else "born_in"
                    other = candidate_for_fact(subject_row, other_relation, inventories)
                    other_rank = rank_candidates(candidate_scores, "mean_logprob", other.object_id)
                    row["other_city_object_id"] = other.object_id
                    row["other_city_rank_mean"] = other_rank["rank"]
                    row["correct_outranks_other_city"] = row["correct_rank_mean"] < other_rank["rank"]
                results.append(row)
                completed.add(key)
            except Exception as exc:
                failed_count += 1
                with errors_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"probe": probe, "error": str(exc)}, ensure_ascii=False) + "\n")
            if index % int(self.config["runtime"].get("checkpoint_interval", 25)) == 0:
                self._write_outputs(results)
                save_progress(
                    self.run_dir / "progress.json",
                    completed,
                    {
                        "status": "running",
                        "last_index": index,
                        "expected_probe_count": expected_probe_count,
                        "attempted_probe_count": attempted_count,
                        "successful_probe_count": len(completed),
                        "failed_probe_count": failed_count,
                        "skipped_completed_count": skipped_completed_count,
                    },
                )

        self._write_outputs(results)
        successful_count = len({f"{row['fact_id']}|{row['language']}" for row in results})
        status = completion_status(expected_probe_count, successful_count, failed_count)
        summary = dual_ranking_metrics(results, partial=status != "completed", expected_count=expected_probe_count)
        summary["completion_status"] = status
        summary["counts"] = {
            "expected_probe_count": expected_probe_count,
            "attempted_probe_count": attempted_count,
            "successful_probe_count": successful_count,
            "failed_probe_count": failed_count,
            "skipped_completed_count": skipped_completed_count,
        }
        candidate_sizes = {family: len(items) for family, items in inventories.items()}
        summary["chance_references"] = chance_references(candidate_sizes)
        write_json(self.run_dir / "summary_metrics.json", summary)
        groups = [
            ("language",),
            ("relation",),
            ("branch",),
            ("frequency",),
            ("popularity",),
            ("name_type",),
            ("name_rarity",),
            ("language", "relation"),
            ("language", "branch"),
            ("relation", "frequency"),
            ("language", "relation", "branch"),
        ]
        write_csv(self.run_dir / "subgroup_metrics.csv", subgroup_metrics(results, groups))
        if relation_binding_is_applicable(self.config["relations"]):
            binding_expected = len(selected_subjects) if status == "completed" else None
            binding_metrics = relation_binding_metrics(results, binding_expected)
        else:
            binding_metrics = {
                "status": "not_applicable",
                "reason": "relation binding requires both born_in and lives_in",
                "configured_relations": self.config["relations"],
            }
        write_json(self.run_dir / "relation_binding_metrics.json", binding_metrics)
        ended = datetime.now(timezone.utc).isoformat()
        run_manifest = {
            "run_id": self.run_id,
            "git_commit": _git_commit(),
            "source_dataset_repository_commit": json.loads(dataset_manifest_path.read_text(encoding="utf-8")).get("source_commit_sha"),
            "dataset_manifest_hash": dataset_manifest_hash,
            "model_id": model_manifest["model_id"],
            "model_revision": model_manifest["resolved_revision"],
            "local_model_snapshot": model_manifest["local_path"],
            "local_tokenizer_snapshot": str(_resolve_tokenizer_path(model_manifest, _resolve_path(self.config["model_manifest"]))),
            "tokenizer_class": tokenizer.__class__.__name__,
            "model_class": model.__class__.__name__,
            "parameter_count": model_manifest["parameter_count"],
            "prompt_format": self.config["prompt"],
            "candidate_inventory_sizes": candidate_sizes,
            "chance_references": summary["chance_references"],
            "selected_subject_count": len(selected_subjects),
            "selected_fact_count": len({probe["fact_id"] for probe in probes}),
            "expected_probe_count": expected_probe_count,
            "evaluation_languages": self.config["languages"],
            "primary_scoring_method": "mean answer-token log probability",
            "secondary_scoring_method": "total answer-token log probability",
            "dtype": str(next(model.parameters()).dtype),
            "device": device,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "python_version": platform.python_version(),
            "seed": self.config["runtime"].get("seed"),
            "batch_sizes": {"candidate_batch_size": self.config["runtime"].get("candidate_batch_size")},
            "start_time": started,
            "end_time": ended,
            "completion_status": status,
            "attempted_probe_count": attempted_count,
            "successful_probe_count": successful_count,
            "failed_probe_count": failed_count,
            "skipped_completed_count": skipped_completed_count,
            "error_path": str(errors_path),
        }
        write_json(self.run_dir / "run_manifest.json", run_manifest)
        save_progress(
            self.run_dir / "progress.json",
            completed,
            {
                "status": status,
                "ended": ended,
                "expected_probe_count": expected_probe_count,
                "attempted_probe_count": attempted_count,
                "successful_probe_count": successful_count,
                "failed_probe_count": failed_count,
                "skipped_completed_count": skipped_completed_count,
            },
        )
        if status != "completed" and not allow_errors:
            raise EvaluationIncompleteError(f"Evaluation ended with status {status}; see {errors_path}")
        return self.run_dir

    def _write_outputs(self, results: list[dict[str, Any]]) -> None:
        if not results:
            return
        fieldnames = list(dict.fromkeys(key for row in results for key in row))
        write_csv(self.run_dir / "per_fact_results.csv", results, fieldnames)
        try:
            import pandas as pd

            pd.DataFrame(results).to_parquet(self.run_dir / "per_fact_results.parquet", index=False)
        except Exception:
            pass


def run_from_config(
    config_path: Path,
    resume_run_dir: Path | None = None,
    force: bool = False,
    allow_errors: bool = False,
) -> Path:
    config = _load_yaml(config_path)
    if resume_run_dir is not None:
        run_dir = resume_run_dir
        resume = True
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        run_dir = Path(config["output"]["run_root"]) / run_id
        resume = False
    return CausalCandidateEvaluator(config, run_dir).run(resume=resume, force=force, allow_errors=allow_errors)
