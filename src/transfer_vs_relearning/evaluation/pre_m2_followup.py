from __future__ import annotations

import json
import math
import platform
from collections import Counter, defaultdict
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
from transfer_vs_relearning.evaluation.evaluator import (
    _manifest_local_path,
    _resolve_path,
    _resolve_tokenizer_path,
)
from transfer_vs_relearning.evaluation.prompts import render_prompt_answer
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.scoring import score_candidate_batch
from transfer_vs_relearning.evaluation.token_scoring import (
    answer_token_indices_from_offsets,
    shifted_label_positions,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def conditional_token_records(
    *,
    input_ids: list[int],
    answer_token_indices: list[int],
    log_probs: Any,
    eos_token_id: int,
) -> list[dict[str, Any]]:
    """Return answer-token and EOS diagnostics with the causal one-token shift explicit."""
    label_positions = shifted_label_positions(answer_token_indices)
    records: list[dict[str, Any]] = []
    cumulative_nll = 0.0
    for answer_position, (token_index, logit_index) in enumerate(
        zip(answer_token_indices, label_positions, strict=True),
        start=1,
    ):
        token_id = input_ids[token_index]
        logprob = float(log_probs[logit_index][token_id])
        nll = -logprob
        cumulative_nll += nll
        records.append(
            {
                "score_type": "answer_token",
                "answer_position": answer_position,
                "token_index": token_index,
                "logit_index": logit_index,
                "token_id": token_id,
                "conditional_logprob": logprob,
                "nll": nll,
                "token_ppl": math.exp(nll),
                "cumulative_answer_nll": cumulative_nll,
                "mean_answer_nll": cumulative_nll / answer_position,
            }
        )

    eos_positions = [("after_prompt", label_positions[0])]
    eos_positions.extend(
        (f"after_answer_{answer_position}", token_index)
        for answer_position, token_index in enumerate(answer_token_indices, start=1)
    )
    for eos_position, logit_index in eos_positions:
        logprob = float(log_probs[logit_index][eos_token_id])
        nll = -logprob
        records.append(
            {
                "score_type": "eos_token",
                "eos_position": eos_position,
                "logit_index": logit_index,
                "token_id": eos_token_id,
                "conditional_logprob": logprob,
                "nll": nll,
                "token_ppl": math.exp(nll),
            }
        )
    return records


def score_candidate_tokens(
    tokenizer: Any,
    model: Any,
    device: str,
    prompt: str,
    candidate: str,
    *,
    separator: str = " ",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import torch

    text, answer_start, answer_end = render_prompt_answer(prompt, candidate, separator)
    encoded = tokenizer(text, return_offsets_mapping=True, return_tensors="pt")
    offsets = encoded.pop("offset_mapping")[0].tolist()
    input_ids_tensor = encoded["input_ids"].to(device)
    attention_mask = encoded.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)
    answer_indices = answer_token_indices_from_offsets(offsets, answer_start, answer_end)
    with torch.inference_mode():
        logits = model(input_ids=input_ids_tensor, attention_mask=attention_mask).logits[0]
        log_probs_tensor = torch.log_softmax(logits.float(), dim=-1).cpu()
    input_ids = [int(value) for value in input_ids_tensor[0].cpu().tolist()]
    records = conditional_token_records(
        input_ids=input_ids,
        answer_token_indices=answer_indices,
        log_probs=log_probs_tensor,
        eos_token_id=int(tokenizer.eos_token_id),
    )
    for record in records:
        record["token_text"] = tokenizer.decode([record["token_id"]])
    answer_records = [record for record in records if record["score_type"] == "answer_token"]
    eos_after_prompt = next(
        record for record in records if record.get("eos_position") == "after_prompt"
    )
    first_answer = answer_records[0]
    summary = {
        "answer_token_count": len(answer_records),
        "answer_nll_sum": sum(float(record["nll"]) for record in answer_records),
        "mean_answer_nll": sum(float(record["nll"]) for record in answer_records) / len(answer_records),
        "answer_ppl": math.exp(
            sum(float(record["nll"]) for record in answer_records) / len(answer_records)
        ),
        "first_answer_token_nll": first_answer["nll"],
        "eos_after_prompt_nll": eos_after_prompt["nll"],
        "eos_preferred_to_first_answer": (
            float(eos_after_prompt["conditional_logprob"])
            > float(first_answer["conditional_logprob"])
        ),
        "eos_in_answer_metric": False,
    }
    return records, summary


def _load_model(model_manifest_path: Path, device_request: str, bf16: bool) -> tuple[Any, Any, str, dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    manifest_path = _resolve_path(model_manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = str(_manifest_local_path(manifest, manifest_path.parent))
    tokenizer_path = str(_resolve_tokenizer_path(manifest, manifest_path))
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dtype = torch.bfloat16 if bf16 and torch.cuda.is_available() and torch.cuda.is_bf16_supported() else None
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype=dtype)
    device = "cuda" if device_request == "cuda" and torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return tokenizer, model, device, manifest


def _confusable_relation(relation: str) -> str | None:
    return {"born_in": "lives_in", "lives_in": "born_in"}.get(relation)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() in {"1", "true", "yes"}


def _summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["relation"]), str(row["form_id"]), str(row["scaffold_id"]))].append(row)
    output = []
    for (relation, form_id, scaffold_id), group in sorted(groups.items()):
        correct = sum(int(row["correct_rank_mean"]) == 1 for row in group)
        output.append(
            {
                "relation": relation,
                "form_id": form_id,
                "scaffold_id": scaffold_id,
                "n": len(group),
                "top1": correct,
                "top1_accuracy": correct / len(group),
                "mean_margin": sum(float(row["margin"]) for row in group) / len(group),
                "early_eos_preference_count": sum(_as_bool(row["gold_eos_preferred_to_first_answer"]) for row in group),
            }
        )
    return output


def _intersection_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[(str(row["fact_id"]), str(row["scaffold_id"]))][str(row["form_id"])] = row
    relation_groups: dict[tuple[str, str], list[dict[str, dict[str, Any]]]] = defaultdict(list)
    for form_rows in grouped.values():
        if set(form_rows) != {"form_a", "form_b", "form_c"}:
            continue
        sample = form_rows["form_a"]
        relation_groups[(str(sample["relation"]), str(sample["scaffold_id"]))].append(form_rows)
    output: list[dict[str, Any]] = []
    for (relation, scaffold_id), facts in sorted(relation_groups.items()):
        success = {
            form_id: {str(rows_by_form[form_id]["fact_id"]) for rows_by_form in facts if int(rows_by_form[form_id]["correct_rank_mean"]) == 1}
            for form_id in ("form_a", "form_b", "form_c")
        }
        output.append(
            {
                "relation": relation,
                "scaffold_id": scaffold_id,
                "n": len(facts),
                "form_a_top1": len(success["form_a"]),
                "form_b_top1": len(success["form_b"]),
                "form_c_top1": len(success["form_c"]),
                "a_b_intersection": len(success["form_a"] & success["form_b"]),
                "a_c_intersection": len(success["form_a"] & success["form_c"]),
                "b_c_intersection": len(success["form_b"] & success["form_c"]),
                "all_form_intersection": len(success["form_a"] & success["form_b"] & success["form_c"]),
            }
        )
    return output


class PreM2FrozenEvaluator:
    def __init__(
        self,
        *,
        model_label: str,
        model_manifest: Path,
        dataset_dir: Path,
        probe_registry: Path,
        output_dir: Path,
        candidate_batch_size: int = 64,
        checkpoint_interval: int = 25,
        device: str = "cuda",
        bf16: bool = True,
    ) -> None:
        self.model_label = model_label
        self.model_manifest = model_manifest.resolve()
        self.dataset_dir = dataset_dir.resolve()
        self.probe_registry = probe_registry.resolve()
        self.output_dir = output_dir.resolve()
        self.candidate_batch_size = candidate_batch_size
        self.checkpoint_interval = checkpoint_interval
        self.device_request = device
        self.bf16 = bf16

    def run(self, *, resume: bool = False) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        per_fact_path = self.output_dir / "hard_suite_per_fact.csv"
        per_token_path = self.output_dir / "teacher_forced_per_token.csv"
        if not resume and (per_fact_path.exists() or per_token_path.exists()):
            raise FileExistsError(f"Output directory already contains evaluator results: {self.output_dir}")
        existing_facts = read_csv_rows(per_fact_path) if resume and per_fact_path.exists() else []
        existing_tokens = read_csv_rows(per_token_path) if resume and per_token_path.exists() else []
        completed = {row["probe_id"] for row in existing_facts}

        probes = read_csv_rows(self.probe_registry)
        probe_ids = [probe["probe_id"] for probe in probes]
        if len(probe_ids) != len(set(probe_ids)):
            raise ValueError("Probe registry contains duplicate probe IDs")
        canonical_rows = read_csv_rows(self.dataset_dir / DATASET_FILES["canonical_profiles"])
        canonical_by_subject = {row["subject_id"]: row for row in canonical_rows}
        inventories = build_candidate_inventories(canonical_rows)
        tokenizer, model, device, model_manifest = _load_model(
            self.model_manifest,
            self.device_request,
            self.bf16,
        )
        fact_rows: list[dict[str, Any]] = list(existing_facts)
        token_rows: list[dict[str, Any]] = list(existing_tokens)
        started_at = datetime.now(timezone.utc).isoformat()

        for probe_index, probe in enumerate(probes, start=1):
            if probe["probe_id"] in completed:
                continue
            relation = probe["relation"]
            prompt = probe["rendered_prompt"]
            correct = resolve_expected_answer(relation, "en", probe["expected_answer"], inventories)
            candidates = inventories[RELATION_TO_FAMILY[relation]]
            surfaces = [candidate.object_en for candidate in candidates]
            candidate_scores: list[dict[str, Any]] = []
            for start in range(0, len(surfaces), self.candidate_batch_size):
                batch_candidates = candidates[start : start + self.candidate_batch_size]
                batch_surfaces = surfaces[start : start + self.candidate_batch_size]
                scores = score_candidate_batch(tokenizer, model, device, prompt, batch_surfaces)
                candidate_scores.extend(
                    {
                        "object_id": candidate.object_id,
                        "surface": candidate.object_en,
                        **score,
                    }
                    for candidate, score in zip(batch_candidates, scores, strict=True)
                )
            ranking = rank_candidates(candidate_scores, "mean_logprob", correct.object_id)
            best_incorrect = next(
                row for row in ranking["ordered"] if row["object_id"] != correct.object_id
            )
            selected_candidates = [
                ("gold", correct.object_id, correct.object_en, True),
                ("best_incorrect", best_incorrect["object_id"], best_incorrect["surface"], False),
            ]
            confusable_relation = _confusable_relation(relation)
            confusable_object_id = None
            if confusable_relation:
                confusable = candidate_for_fact(
                    canonical_by_subject[probe["subject_id"]],
                    confusable_relation,
                    inventories,
                )
                confusable_object_id = confusable.object_id
                selected_candidates.append(
                    ("same_subject_confusable", confusable.object_id, confusable.object_en, False)
                )

            summaries: dict[str, dict[str, Any]] = {}
            for candidate_role, object_id, surface, is_correct in selected_candidates:
                records, summary = score_candidate_tokens(tokenizer, model, device, prompt, surface)
                summaries[candidate_role] = summary
                for record in records:
                    token_rows.append(
                        {
                            "model_label": self.model_label,
                            "probe_id": probe["probe_id"],
                            "fact_id": probe["fact_id"],
                            "subject_id": probe["subject_id"],
                            "relation": relation,
                            "form_id": probe["form_id"],
                            "scaffold_id": probe["scaffold_id"],
                            "candidate_role": candidate_role,
                            "candidate_object_id": object_id,
                            "candidate_surface": surface,
                            "candidate_is_correct": is_correct,
                            **record,
                        }
                    )

            failure_type = "none"
            if int(ranking["rank"]) != 1:
                if confusable_object_id and ranking["top1_object_id"] == confusable_object_id:
                    failure_type = "same_subject_relation_swap"
                elif summaries["gold"]["eos_preferred_to_first_answer"]:
                    failure_type = "early_eos_preference"
                elif probe["form_id"] in {"form_a", "form_b", "form_c"}:
                    failure_type = "prompt_form_failure"
                else:
                    failure_type = "unclassified"
            fact_rows.append(
                {
                    "model_label": self.model_label,
                    **probe,
                    "correct_object_id": correct.object_id,
                    "predicted_object_id": ranking["top1_object_id"],
                    "predicted_surface": ranking["top1_surface"],
                    "correct_rank_mean": ranking["rank"],
                    "correct_mean_score": ranking["correct_score"],
                    "best_incorrect_mean_score": ranking["best_incorrect_score"],
                    "margin": ranking["margin"],
                    "same_subject_confusable_object_id": confusable_object_id or "",
                    "gold_mean_answer_nll": summaries["gold"]["mean_answer_nll"],
                    "gold_answer_ppl": summaries["gold"]["answer_ppl"],
                    "gold_first_answer_token_nll": summaries["gold"]["first_answer_token_nll"],
                    "gold_eos_after_prompt_nll": summaries["gold"]["eos_after_prompt_nll"],
                    "gold_eos_preferred_to_first_answer": summaries["gold"]["eos_preferred_to_first_answer"],
                    "failure_type": failure_type,
                }
            )
            completed.add(probe["probe_id"])
            if probe_index % self.checkpoint_interval == 0:
                write_csv(per_fact_path, fact_rows)
                write_csv(per_token_path, token_rows)
                write_json(
                    self.output_dir / "progress.json",
                    {"status": "running", "completed": len(completed), "expected": len(probes)},
                )

        write_csv(per_fact_path, fact_rows)
        write_csv(per_token_path, token_rows)
        write_csv(self.output_dir / "summary_by_relation_form.csv", _summary_rows(fact_rows))
        write_csv(self.output_dir / "form_intersections.csv", _intersection_rows(fact_rows))
        failure_counts = Counter(str(row["failure_type"]) for row in fact_rows)
        write_json(
            self.output_dir / "summary.json",
            {
                "status": "completed",
                "model_label": self.model_label,
                "probes": len(fact_rows),
                "top1": sum(int(row["correct_rank_mean"]) == 1 for row in fact_rows),
                "failure_taxonomy": dict(sorted(failure_counts.items())),
            },
        )
        import torch
        import transformers

        write_json(
            self.output_dir / "run_manifest.json",
            {
                "status": "completed",
                "model_label": self.model_label,
                "model_manifest": str(self.model_manifest),
                "model_manifest_sha256": sha256_file(self.model_manifest),
                "model_id": model_manifest.get("model_id"),
                "model_revision": model_manifest.get("resolved_revision"),
                "dataset_dir": str(self.dataset_dir),
                "dataset_manifest_sha256": sha256_file(self.dataset_dir / "manifest.json"),
                "probe_registry": str(self.probe_registry),
                "probe_registry_sha256": sha256_file(self.probe_registry),
                "tokenizer_class": tokenizer.__class__.__name__,
                "model_class": model.__class__.__name__,
                "device": device,
                "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                "python_version": platform.python_version(),
                "pytorch_version": torch.__version__,
                "transformers_version": transformers.__version__,
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "candidate_batch_size": self.candidate_batch_size,
                "eos_in_answer_metric": False,
            },
        )
        write_json(
            self.output_dir / "progress.json",
            {"status": "completed", "completed": len(completed), "expected": len(probes)},
        )
        return self.output_dir
