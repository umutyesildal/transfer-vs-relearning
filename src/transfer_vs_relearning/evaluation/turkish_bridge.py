from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import RELATION_TO_FAMILY, build_candidate_inventories
from transfer_vs_relearning.data.constants import DATASET_FILES
from transfer_vs_relearning.evaluation.pre_m2_followup import _load_model
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.scoring import score_candidate_batch
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def summarize_bridge_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["direction"]), str(row["relation"]))].append(row)
        groups[(str(row["direction"]), "__all__")].append(row)
    summary: list[dict[str, Any]] = []
    for (direction, relation), group in sorted(groups.items()):
        margins = sorted(float(row["margin"]) for row in group)
        midpoint = len(margins) // 2
        median = margins[midpoint] if len(margins) % 2 else (margins[midpoint - 1] + margins[midpoint]) / 2
        correct = sum(int(row["correct_rank_mean"]) == 1 for row in group)
        summary.append(
            {
                "direction": direction,
                "relation": relation,
                "n": len(group),
                "top1": correct,
                "top1_accuracy": correct / len(group),
                "mean_margin": sum(margins) / len(margins),
                "median_margin": median,
            }
        )
    return summary


class TurkishBridgeEvaluator:
    def __init__(
        self,
        *,
        model_label: str,
        model_manifest: Path,
        dataset_dir: Path,
        probe_registry: Path,
        output_dir: Path,
        eligible_facts: Path | None = None,
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
        self.eligible_facts = eligible_facts.resolve() if eligible_facts else None
        self.candidate_batch_size = candidate_batch_size
        self.checkpoint_interval = checkpoint_interval
        self.device_request = device
        self.bf16 = bf16

    def run(self, *, resume: bool = False, probe_limit: int | None = None) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        result_path = self.output_dir / "per_probe_results.csv"
        if result_path.exists() and not resume:
            raise FileExistsError(f"Bridge result already exists: {result_path}")
        probes = read_csv_rows(self.probe_registry)
        if self.eligible_facts:
            eligible_rows = read_csv_rows(self.eligible_facts)
            eligible = {
                row["fact_id"] for row in eligible_rows
                if str(row.get("eligible_3_of_4_heldout", row.get("shared_eligible", ""))).casefold() in {"1", "true", "yes"}
            }
            probes = [probe for probe in probes if probe["fact_id"] in eligible]
        if probe_limit is not None:
            if probe_limit <= 0:
                raise ValueError("probe_limit must be positive")
            probes = probes[:probe_limit]
        if len({probe["probe_id"] for probe in probes}) != len(probes):
            raise ValueError("Bridge probe IDs must be unique")

        existing = read_csv_rows(result_path) if resume and result_path.exists() else []
        completed = {row["probe_id"] for row in existing}
        canonical_rows = read_csv_rows(self.dataset_dir / DATASET_FILES["canonical_profiles"])
        inventories = build_candidate_inventories(canonical_rows)
        tokenizer, model, device, model_manifest = _load_model(self.model_manifest, self.device_request, self.bf16)
        results: list[dict[str, Any]] = list(existing)
        started = datetime.now(timezone.utc).isoformat()

        for index, probe in enumerate(probes, start=1):
            if probe["probe_id"] in completed:
                continue
            candidates = inventories[RELATION_TO_FAMILY[probe["relation"]]]
            answer_language = probe["answer_language"]
            surfaces = [candidate.surface(answer_language) for candidate in candidates]
            scores: list[dict[str, Any]] = []
            for start in range(0, len(candidates), self.candidate_batch_size):
                batch_candidates = candidates[start : start + self.candidate_batch_size]
                batch_surfaces = surfaces[start : start + self.candidate_batch_size]
                batch_scores = score_candidate_batch(tokenizer, model, device, probe["rendered_prompt"], batch_surfaces)
                scores.extend(
                    {"object_id": candidate.object_id, "surface": surface, **score}
                    for candidate, surface, score in zip(batch_candidates, batch_surfaces, batch_scores, strict=True)
                )
            ranking = rank_candidates(scores, "mean_logprob", probe["correct_object_id"])
            correct = next(row for row in scores if row["object_id"] == probe["correct_object_id"])
            results.append(
                {
                    "model_label": self.model_label,
                    "resolved_model_revision": model_manifest["resolved_revision"],
                    **probe,
                    "predicted_object_id": ranking["top1_object_id"],
                    "predicted_surface": ranking["top1_surface"],
                    "correct_rank_mean": ranking["rank"],
                    "correct_mean_score": ranking["correct_score"],
                    "best_incorrect_mean_score": ranking["best_incorrect_score"],
                    "margin": ranking["margin"],
                    "correct_token_count": correct["token_count"],
                    "candidate_count": len(candidates),
                }
            )
            completed.add(probe["probe_id"])
            if index % self.checkpoint_interval == 0:
                write_csv(result_path, results)
                write_json(self.output_dir / "progress.json", {"status": "running", "completed": len(completed), "expected": len(probes)})

        write_csv(result_path, results)
        summaries = summarize_bridge_rows(results)
        write_csv(self.output_dir / "summary_by_direction_relation.csv", summaries)
        status = "completed" if len(completed) == len(probes) else "partial"
        write_json(
            self.output_dir / "summary.json",
            {
                "status": status,
                "model_label": self.model_label,
                "probe_count": len(probes),
                "completed_count": len(completed),
                "started_at": started,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "probe_registry_sha256": sha256_file(self.probe_registry),
                "eligible_facts_sha256": sha256_file(self.eligible_facts) if self.eligible_facts else None,
                "primary_score": "mean answer-token log probability",
                "rows": summaries,
            },
        )
        write_json(self.output_dir / "progress.json", {"status": status, "completed": len(completed), "expected": len(probes)})
        return self.output_dir
