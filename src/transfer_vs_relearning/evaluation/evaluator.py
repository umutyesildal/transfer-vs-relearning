from __future__ import annotations

import csv
import json
import platform
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.data.candidates import (
    RELATION_TO_FAMILY,
    build_candidate_inventories,
    candidate_for_fact,
    resolve_expected_answer,
)
from transfer_vs_relearning.data.constants import DATASET_FILES
from transfer_vs_relearning.data.facts import expand_canonical_rows
from transfer_vs_relearning.evaluation.progress import load_completed, save_progress
from transfer_vs_relearning.evaluation.prompts import render_prompt, render_prompt_answer
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.token_scoring import answer_token_indices_from_offsets, score_from_token_logprobs, shifted_label_positions
from transfer_vs_relearning.metrics.core import ranking_metrics, subgroup_metrics
from transfer_vs_relearning.metrics.relation_binding import relation_binding_metrics
from transfer_vs_relearning.utils.io import read_csv_rows, write_csv, write_json


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class CausalCandidateEvaluator:
    def __init__(self, config: dict[str, Any], run_dir: Path):
        self.config = config
        self.run_dir = run_dir
        self.run_id = run_dir.name

    def _load_model(self) -> tuple[Any, Any, str, dict[str, Any]]:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        manifest = json.loads(Path(self.config["model_manifest"]).read_text(encoding="utf-8"))
        local_path = manifest["local_path"]
        tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        dtype = torch.bfloat16 if self.config["runtime"].get("bf16") and torch.cuda.is_available() and torch.cuda.is_bf16_supported() else None
        model = AutoModelForCausalLM.from_pretrained(local_path, local_files_only=True, torch_dtype=dtype)
        device = "cuda" if self.config["runtime"].get("device") == "cuda" and torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        return tokenizer, model, device, manifest

    def _score_candidate(self, tokenizer: Any, model: Any, device: str, prompt: str, candidate: str) -> dict[str, float | int]:
        import torch

        separator = self.config["prompt"].get("answer_separator", " ")
        text, answer_start, answer_end = render_prompt_answer(prompt, candidate, separator)
        encoded = tokenizer(text, return_offsets_mapping=True, return_tensors="pt")
        offsets = [(int(start), int(end)) for start, end in encoded.pop("offset_mapping")[0].tolist()]
        answer_indices = answer_token_indices_from_offsets(offsets, answer_start, answer_end)
        label_positions = shifted_label_positions(answer_indices)
        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)
        with torch.inference_mode():
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
            log_probs = torch.log_softmax(logits, dim=-1)
        token_scores = []
        for token_index, logit_index in zip(answer_indices, label_positions):
            token_id = int(input_ids[0, token_index].item())
            token_scores.append(float(log_probs[0, logit_index, token_id].item()))
        return score_from_token_logprobs(token_scores)

    def run(self) -> Path:
        import torch
        import transformers

        self.run_dir.mkdir(parents=True, exist_ok=True)
        with (self.run_dir / "resolved_config.yaml").open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.config, handle, sort_keys=True, allow_unicode=True)
        dataset_dir = Path(self.config["dataset_dir"])
        canonical_rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
        canonical_by_subject = {row["subject_id"]: row for row in canonical_rows}
        pilot = json.loads(Path(self.config["pilot_subject_file"]).read_text(encoding="utf-8"))
        selected_subjects = set(pilot["selected_subject_ids"])
        write_json(self.run_dir / "selected_subjects_reference.json", pilot)
        probes = []
        if "en" in self.config["languages"]:
            probes.extend(read_csv_rows(dataset_dir / DATASET_FILES["probes_en"]))
        if "tr" in self.config["languages"]:
            probes.extend(read_csv_rows(dataset_dir / DATASET_FILES["probes_tr"]))
        probes = [
            row
            for row in probes
            if row["subject_id"] in selected_subjects and row["relation"] in self.config["relations"]
        ]

        inventories = build_candidate_inventories(canonical_rows)
        tokenizer, model, device, model_manifest = self._load_model()
        completed = load_completed(self.run_dir / "progress.json")
        results: list[dict[str, Any]] = []
        result_csv = self.run_dir / "per_fact_results.csv"
        if result_csv.exists():
            results = read_csv_rows(result_csv)

        started = datetime.now(timezone.utc).isoformat()
        save_progress(self.run_dir / "progress.json", completed, {"status": "running", "started": started})
        errors_path = self.run_dir / "errors.jsonl"
        for index, probe in enumerate(probes, start=1):
            key = f"{probe['fact_id']}|{probe['language']}"
            if key in completed:
                continue
            try:
                prompt = render_prompt(
                    probe["question"],
                    self.config["prompt"].get("format", "qa"),
                    self.config["prompt"].get("template"),
                )
                family = RELATION_TO_FAMILY[probe["relation"]]
                correct = resolve_expected_answer(probe["relation"], probe["language"], probe["expected_answer"], inventories)
                candidate_scores = []
                for candidate in inventories[family]:
                    scores = self._score_candidate(tokenizer, model, device, prompt, candidate.surface(probe["language"]))
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
                    "correct_rank_mean": ranked_mean["rank"],
                    "correct_rank_total": ranked_total["rank"],
                    "correct_mean_score": ranked_mean["correct_score"],
                    "correct_total_score": ranked_total["correct_score"],
                    "best_incorrect_mean_score": ranked_mean["best_incorrect_score"],
                    "margin": ranked_mean["margin"],
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
                with errors_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"probe": probe, "error": str(exc)}, ensure_ascii=False) + "\n")
            if index % int(self.config["runtime"].get("checkpoint_interval", 25)) == 0:
                self._write_outputs(results)
                save_progress(self.run_dir / "progress.json", completed, {"status": "running", "last_index": index})

        self._write_outputs(results)
        summary = ranking_metrics(results)
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
        write_json(self.run_dir / "relation_binding_metrics.json", relation_binding_metrics(results))
        ended = datetime.now(timezone.utc).isoformat()
        run_manifest = {
            "run_id": self.run_id,
            "git_commit": _git_commit(),
            "source_dataset_repository_commit": json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8")).get("source_commit_sha"),
            "dataset_manifest_hash": pilot.get("dataset_manifest_hash"),
            "model_id": model_manifest["model_id"],
            "model_revision": model_manifest["resolved_revision"],
            "local_model_snapshot": model_manifest["local_path"],
            "tokenizer_class": tokenizer.__class__.__name__,
            "model_class": model.__class__.__name__,
            "parameter_count": model_manifest["parameter_count"],
            "prompt_format": self.config["prompt"],
            "candidate_inventory_sizes": {family: len(items) for family, items in inventories.items()},
            "selected_subject_count": len(selected_subjects),
            "selected_fact_count": len(selected_subjects) * 5,
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
            "completion_status": "completed",
        }
        write_json(self.run_dir / "run_manifest.json", run_manifest)
        save_progress(self.run_dir / "progress.json", completed, {"status": "completed", "ended": ended})
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


def run_from_config(config_path: Path) -> Path:
    config = _load_yaml(config_path)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = Path(config["output"]["run_root"]) / run_id
    return CausalCandidateEvaluator(config, run_dir).run()
