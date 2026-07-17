from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.candidates import build_candidate_inventories
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_csv, write_json
from transfer_vs_relearning.utils.text import normalize_text


FOLLOWUP_VERSION = "pre_m2_followup_v1"
RELATIONS = (
    "profession",
    "born_in",
    "lives_in",
    "field_of_study",
    "works_in_industry",
)
FORM_IDS = ("form_a", "form_b", "form_c")
FORM_TEMPLATES: dict[str, dict[str, str]] = {
    "profession": {
        "form_a": "What occupation does {subject} have?",
        "form_b": "How is {subject} employed professionally?",
        "form_c": "Which line of work is listed for {subject}?",
    },
    "born_in": {
        "form_a": "In which city did {subject}'s birth occur?",
        "form_b": "What location is listed as {subject}'s birthplace?",
        "form_c": "Which city is recorded as the place of birth for {subject}?",
    },
    "lives_in": {
        "form_a": "In which city does {subject} reside now?",
        "form_b": "What location is listed as {subject}'s current residence?",
        "form_c": "Which city is recorded as the current home of {subject}?",
    },
    "field_of_study": {
        "form_a": "Which academic subject did {subject} pursue?",
        "form_b": "What discipline is listed as {subject}'s field of study?",
        "form_c": "Which area of study is recorded for {subject}?",
    },
    "works_in_industry": {
        "form_a": "Within which industry is {subject} employed?",
        "form_b": "What sector is listed for {subject}'s work?",
        "form_c": "Which industry is recorded as {subject}'s employment sector?",
    },
}
SCAFFOLDS = {
    "direct": "{question}",
    "qa": "Question: {question}\nAnswer:",
}
WP1B_EXPOSURES = ("direct", "qa", "direct", "qa", "direct", "qa", "direct")


def _git_value(repo_root: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root), *args], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _stable_order(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}|{value}".encode("utf-8")).hexdigest()


def _subject_features(row: dict[str, str]) -> tuple[str, ...]:
    values = [
        f"branch={row['branch_group']}",
        f"name_type={row['name_type']}",
        f"name_rarity={row['name_rarity_bucket']}",
        f"popularity={row['popularity_bucket']}",
    ]
    for relation in RELATIONS:
        frequency_column = RELATION_MAP[relation][2]
        values.append(f"{relation}_frequency={row[frequency_column]}")
    return tuple(values)


def counterbalanced_subject_assignment(
    rows: list[dict[str, str]],
    selected_subject_ids: list[str],
    *,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    by_subject = {row["subject_id"]: row for row in rows}
    missing = sorted(set(selected_subject_ids) - set(by_subject))
    if missing:
        raise ValueError(f"Selected subjects missing from canonical profiles: {missing[:5]}")
    if len(selected_subject_ids) % 2:
        raise ValueError("Counterbalanced assignment requires an even subject count")

    selected = [by_subject[subject_id] for subject_id in selected_subject_ids]
    target_size = len(selected) // 2
    ordered = sorted(selected, key=lambda item: _stable_order(item["subject_id"], seed))
    groups = {
        "A": {row["subject_id"] for row in ordered[:target_size]},
        "B": {row["subject_id"] for row in ordered[target_size:]},
    }
    feature_sets = {row["subject_id"]: set(_subject_features(row)) for row in selected}
    all_features = sorted(set().union(*feature_sets.values()))

    def group_counts(group: str) -> Counter[str]:
        return Counter(feature for subject_id in groups[group] for feature in feature_sets[subject_id])

    def imbalance_score(counts_a: Counter[str], counts_b: Counter[str]) -> int:
        return sum((counts_a[feature] - counts_b[feature]) ** 2 for feature in all_features)

    counts_a = group_counts("A")
    counts_b = group_counts("B")
    while True:
        current_score = imbalance_score(counts_a, counts_b)
        best: tuple[int, str, str, Counter[str], Counter[str]] | None = None
        for subject_a in sorted(groups["A"]):
            for subject_b in sorted(groups["B"]):
                next_a = counts_a.copy()
                next_b = counts_b.copy()
                next_a.subtract(feature_sets[subject_a])
                next_a.update(feature_sets[subject_b])
                next_b.subtract(feature_sets[subject_b])
                next_b.update(feature_sets[subject_a])
                score = imbalance_score(next_a, next_b)
                candidate = (score, subject_a, subject_b, next_a, next_b)
                if score < current_score and (best is None or candidate[:3] < best[:3]):
                    best = candidate
        if best is None:
            break
        _, subject_a, subject_b, counts_a, counts_b = best
        groups["A"].remove(subject_a)
        groups["A"].add(subject_b)
        groups["B"].remove(subject_b)
        groups["B"].add(subject_a)

    assignments: list[dict[str, Any]] = []
    for row in selected:
        group = "A" if row["subject_id"] in groups["A"] else "B"
        assignments.append(
            {
                "subject_id": row["subject_id"],
                "subject": row["subject"],
                "training_form_group": group,
                "training_form_id": "form_a" if group == "A" else "form_b",
                "heldout_crossed_form_id": "form_b" if group == "A" else "form_a",
                "novel_form_id": "form_c",
                "features": list(_subject_features(row)),
            }
        )

    group_sizes = {group: len(subject_ids) for group, subject_ids in groups.items()}
    if group_sizes != {"A": target_size, "B": target_size}:
        raise AssertionError(f"Unexpected assignment sizes: {group_sizes}")
    return sorted(assignments, key=lambda item: item["subject_id"])


def assignment_balance(assignments: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"A": Counter(), "B": Counter()}
    sizes = Counter()
    for item in assignments:
        group = item["training_form_group"]
        sizes[group] += 1
        counts[group].update(item["features"])
    features = sorted(set(counts["A"]) | set(counts["B"]))
    differences = {feature: counts["A"][feature] - counts["B"][feature] for feature in features}
    return {
        "group_sizes": dict(sorted(sizes.items())),
        "feature_counts": {group: dict(sorted(values.items())) for group, values in counts.items()},
        "a_minus_b": differences,
        "max_absolute_feature_difference": max((abs(value) for value in differences.values()), default=0),
    }


def _training_prompt_keys(training_rows: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in training_rows:
        text = str(row["text"])
        answer = str(row["answer"])
        answer_start = text.rfind(answer)
        if answer_start < 0:
            raise ValueError(f"Answer missing from training row {row.get('fact_id')}")
        prompt = text[:answer_start].rstrip()
        keys.add(normalize_text(prompt))
    return keys


def build_paraphrase_probes(
    canonical_rows: list[dict[str, str]],
    assignments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_subject = {row["subject_id"]: row for row in canonical_rows}
    assignment_by_subject = {row["subject_id"]: row for row in assignments}
    probes: list[dict[str, Any]] = []
    for subject_id in sorted(assignment_by_subject):
        row = by_subject[subject_id]
        assignment = assignment_by_subject[subject_id]
        for relation in RELATIONS:
            answer_column = RELATION_MAP[relation][0]
            frequency_column = RELATION_MAP[relation][2]
            for form_id in FORM_IDS:
                question = FORM_TEMPLATES[relation][form_id].format(subject=row["subject"])
                for scaffold_id, scaffold in SCAFFOLDS.items():
                    prompt = scaffold.format(question=question)
                    wp1b_cell = (
                        "seen"
                        if form_id == assignment["training_form_id"]
                        else "crossed"
                        if form_id == assignment["heldout_crossed_form_id"]
                        else "novel"
                    )
                    probes.append(
                        {
                            "probe_id": f"{subject_id}_{relation}_{form_id}_{scaffold_id}",
                            "fact_id": f"{subject_id}_{relation}",
                            "subject_id": subject_id,
                            "subject": row["subject"],
                            "relation": relation,
                            "form_id": form_id,
                            "scaffold_id": scaffold_id,
                            "canonical_m1_exposure": "heldout_unseen",
                            "wp1b_counterbalance_cell": wp1b_cell,
                            "question": question,
                            "rendered_prompt": prompt,
                            "expected_answer": row[answer_column],
                            "branch_group": row["branch_group"],
                            "name_type": row["name_type"],
                            "name_rarity_bucket": row["name_rarity_bucket"],
                            "popularity_bucket": row["popularity_bucket"],
                            "frequency_bucket": row[frequency_column],
                        }
                    )
    return probes


def template_registry() -> dict[str, Any]:
    return {
        "version": FOLLOWUP_VERSION,
        "language": "en",
        "form_ids": list(FORM_IDS),
        "scaffolds": SCAFFOLDS,
        "relations": FORM_TEMPLATES,
        "contract": {
            "form_family_is_separate_from_scaffold": True,
            "normalized_prompt_overlap_with_canonical_training_must_be_zero": True,
            "form_c_is_diagnostic_in_first_pilot": True,
        },
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, path)


def _wp1b_rows(
    canonical_rows: list[dict[str, str]],
    assignments: list[dict[str, Any]],
    *,
    condition: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_subject = {row["subject_id"]: row for row in canonical_rows}
    train_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    for assignment in sorted(assignments, key=lambda item: item["subject_id"]):
        subject_id = str(assignment["subject_id"])
        profile = by_subject[subject_id]
        form_id = str(assignment["training_form_id"])
        for relation in RELATIONS:
            answer_column = RELATION_MAP[relation][0]
            frequency_column = RELATION_MAP[relation][2]
            answer = profile[answer_column]
            question = FORM_TEMPLATES[relation][form_id].format(subject=profile["subject"])
            fact_id = f"{subject_id}_{relation}"
            common = {
                "answer": answer,
                "branch_group": profile["branch_group"],
                "condition": condition,
                "fact_id": fact_id,
                "frequency_bucket": profile[frequency_column],
                "language": "en",
                "name_rarity_bucket": profile["name_rarity_bucket"],
                "name_type": profile["name_type"],
                "popularity_bucket": profile["popularity_bucket"],
                "popularity_rank": profile["popularity_rank"],
                "relation": relation,
                "row_id": profile["row_id"],
                "subject": profile["subject"],
                "subject_id": subject_id,
                "training_form_group": assignment["training_form_group"],
                "training_form_id": form_id,
            }
            for exposure_index, scaffold_id in enumerate(WP1B_EXPOSURES, start=1):
                prompt = SCAFFOLDS[scaffold_id].format(question=question)
                train_rows.append(
                    {
                        **common,
                        "exposure_index": exposure_index,
                        "scaffold_id": scaffold_id,
                        "split": f"wp1b_{condition}_train",
                        "template_id": f"{relation}_{form_id}_{scaffold_id}_exposure_{exposure_index:02d}",
                        "text": f"{prompt} {answer}",
                    }
                )
            validation_prompt = SCAFFOLDS["qa"].format(question=question)
            validation_rows.append(
                {
                    **common,
                    "exposure_index": 0,
                    "scaffold_id": "qa",
                    "split": f"wp1b_{condition}_validation",
                    "template_id": f"{relation}_{form_id}_qa_monitor",
                    "text": f"{validation_prompt} {answer}",
                }
            )
    return train_rows, validation_rows


def build_wp1b_training_datasets(
    repo_root: Path,
    *,
    dataset_dir: Path | None = None,
    followup_dir: Path | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    dataset_dir = (dataset_dir or repo_root / "artifacts/datasets/relation_v2_gate_v1").resolve()
    followup_dir = (followup_dir or repo_root / f"artifacts/{FOLLOWUP_VERSION}").resolve()
    canonical_rows = read_csv_rows(dataset_dir / "data/canonical_subject_profiles_5000.csv")
    assignments_by_condition = {
        "original": json.loads(
            (followup_dir / "manifests/subject_form_assignment.json").read_text(encoding="utf-8")
        )["assignments"],
        "swap": json.loads(
            (followup_dir / "manifests/subject_form_assignment_swap.json").read_text(encoding="utf-8")
        )["assignments"],
    }
    probe_rows = read_csv_rows(followup_dir / "evaluations/paraphrase_probe_registry.csv")
    probe_keys = {
        (
            row["subject_id"],
            row["relation"],
            row["form_id"],
            row["scaffold_id"],
            normalize_text(row["rendered_prompt"]),
        )
        for row in probe_rows
    }
    training_root = followup_dir / "training/paraphrase_counterbalance"
    conditions: dict[str, Any] = {}
    training_prompt_sets: dict[str, set[tuple[str, str, str, str, str]]] = {}

    for condition, assignments in assignments_by_condition.items():
        train_rows, validation_rows = _wp1b_rows(canonical_rows, assignments, condition=condition)
        condition_dir = training_root / "datasets" / condition
        train_path = condition_dir / "train.jsonl"
        validation_path = condition_dir / "validation.jsonl"
        _write_jsonl(train_path, train_rows)
        _write_jsonl(validation_path, validation_rows)

        assignment_by_subject = {row["subject_id"]: row for row in assignments}
        fact_counts = Counter(row["fact_id"] for row in train_rows)
        observed_forms = {
            subject_id: sorted({row["training_form_id"] for row in train_rows if row["subject_id"] == subject_id})
            for subject_id in assignment_by_subject
        }
        prompt_keys: set[tuple[str, str, str, str, str]] = set()
        for row in train_rows:
            answer_start = row["text"].rfind(row["answer"])
            prompt = row["text"][:answer_start].rstrip()
            prompt_keys.add(
                (
                    row["subject_id"],
                    row["relation"],
                    row["training_form_id"],
                    row["scaffold_id"],
                    normalize_text(prompt),
                )
            )
        training_prompt_sets[condition] = prompt_keys
        unmatched_prompt_keys = sorted(prompt_keys - probe_keys)
        wrong_form_subjects = sorted(
            subject_id
            for subject_id, forms in observed_forms.items()
            if forms != [assignment_by_subject[subject_id]["training_form_id"]]
        )
        group_counts = Counter(row["training_form_group"] for row in train_rows)
        form_counts = Counter(row["training_form_id"] for row in train_rows)
        scaffold_counts = Counter(row["scaffold_id"] for row in train_rows)
        status = "passed"
        if (
            len(train_rows) != 3500
            or len(validation_rows) != 500
            or set(fact_counts.values()) != {len(WP1B_EXPOSURES)}
            or unmatched_prompt_keys
            or wrong_form_subjects
            or group_counts != Counter({"A": 1750, "B": 1750})
            or form_counts != Counter({"form_a": 1750, "form_b": 1750})
        ):
            status = "failed"
        conditions[condition] = {
            "status": status,
            "assignment_manifest": str(
                Path("manifests")
                / ("subject_form_assignment.json" if condition == "original" else "subject_form_assignment_swap.json")
            ),
            "train_file": str(train_path.relative_to(followup_dir)),
            "train_sha256": sha256_file(train_path),
            "train_rows": len(train_rows),
            "validation_file": str(validation_path.relative_to(followup_dir)),
            "validation_sha256": sha256_file(validation_path),
            "validation_rows": len(validation_rows),
            "facts": len(fact_counts),
            "rows_per_fact": sorted(set(fact_counts.values())),
            "group_row_counts": dict(sorted(group_counts.items())),
            "form_row_counts": dict(sorted(form_counts.items())),
            "scaffold_row_counts": dict(sorted(scaffold_counts.items())),
            "unique_training_prompt_count": len(prompt_keys),
            "unmatched_probe_prompt_keys": unmatched_prompt_keys,
            "wrong_form_subjects": wrong_form_subjects,
        }
        if status != "passed":
            raise ValueError(f"WP1B {condition} integrity failed: {conditions[condition]}")

    original_by_subject = {row["subject_id"]: row for row in assignments_by_condition["original"]}
    swap_by_subject = {row["subject_id"]: row for row in assignments_by_condition["swap"]}
    swap_mismatches = sorted(
        subject_id
        for subject_id in original_by_subject
        if original_by_subject[subject_id]["training_form_id"]
        == swap_by_subject[subject_id]["training_form_id"]
    )
    shared_training_prompts = sorted(training_prompt_sets["original"] & training_prompt_sets["swap"])
    manifest = {
        "version": FOLLOWUP_VERSION,
        "experiment": "wp1b_counterbalanced_training_form",
        "status": "passed" if not swap_mismatches and not shared_training_prompts else "failed",
        "fact_graph": {"subjects": 100, "relations": 5, "facts": 500},
        "exposure_contract": {
            "rows_per_fact": len(WP1B_EXPOSURES),
            "scaffold_sequence": list(WP1B_EXPOSURES),
            "rows_per_condition": 3500,
            "optimizer_update_budget_must_match": True,
            "objective": "answer_only_with_eos",
        },
        "conditions": conditions,
        "swap_a_b_assignment_mismatch_subjects": swap_mismatches,
        "shared_original_swap_training_prompt_count": len(shared_training_prompts),
        "shared_original_swap_training_prompt_keys": shared_training_prompts,
        "heldout_contract": {
            "all_subjects_evaluated_on": ["form_a", "form_b", "form_c"],
            "crossed_form_never_used_for_that_subject_in_training": True,
            "form_c_never_used_in_training": True,
            "validation_split_is_training_form_monitoring_only": True,
            "scientific_results_must_use_frozen_probe_registry": True,
        },
    }
    manifest_path = training_root / "dataset_manifest.json"
    write_json(manifest_path, manifest)
    if manifest["status"] != "passed":
        raise ValueError(f"WP1B cross-condition integrity failed: {manifest}")
    write_json(
        training_root / "dataset_hashes.json",
        {
            "dataset_manifest.json": sha256_file(manifest_path),
            **{
                condition_data["train_file"]: condition_data["train_sha256"]
                for condition_data in conditions.values()
            },
            **{
                condition_data["validation_file"]: condition_data["validation_sha256"]
                for condition_data in conditions.values()
            },
        },
    )
    return training_root


def build_pre_m2_followup_contract(
    repo_root: Path,
    *,
    dataset_dir: Path | None = None,
    output_dir: Path | None = None,
    assignment_seed: int = 20260717,
    model_manifests: dict[str, Path] | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    dataset_dir = (dataset_dir or repo_root / "artifacts/datasets/relation_v2_gate_v1").resolve()
    output_dir = (output_dir or repo_root / f"artifacts/{FOLLOWUP_VERSION}").resolve()
    source_dir = dataset_dir / "acquisition_100_subjects_direct"
    canonical_path = dataset_dir / "data/canonical_subject_profiles_5000.csv"
    training_path = source_dir / "train.jsonl"
    summary_path = source_dir / "summary.json"
    dataset_manifest_path = dataset_dir / "manifest.json"

    canonical_rows = read_csv_rows(canonical_path)
    training_rows = read_jsonl(training_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    selected_subject_ids = list(summary["selected_subject_ids"])
    assignments = counterbalanced_subject_assignment(
        canonical_rows,
        selected_subject_ids,
        seed=assignment_seed,
    )
    swap_assignments = [
        {
            **item,
            "training_form_group": "B" if item["training_form_group"] == "A" else "A",
            "training_form_id": item["heldout_crossed_form_id"],
            "heldout_crossed_form_id": item["training_form_id"],
        }
        for item in assignments
    ]
    probes = build_paraphrase_probes(canonical_rows, assignments)
    training_keys = _training_prompt_keys(training_rows)
    overlaps = sorted(
        probe["probe_id"]
        for probe in probes
        if normalize_text(str(probe["rendered_prompt"])) in training_keys
    )
    duplicate_probe_ids = [
        probe_id for probe_id, count in Counter(probe["probe_id"] for probe in probes).items() if count != 1
    ]
    balance = assignment_balance(assignments)
    relation_counts = Counter(probe["relation"] for probe in probes)
    form_counts = Counter(probe["form_id"] for probe in probes)
    scaffold_counts = Counter(probe["scaffold_id"] for probe in probes)

    manifests_dir = output_dir / "manifests"
    evaluations_dir = output_dir / "evaluations"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    evaluations_dir.mkdir(parents=True, exist_ok=True)
    write_json(manifests_dir / "template_registry.json", template_registry())
    inventories = build_candidate_inventories(canonical_rows)
    write_json(
        manifests_dir / "candidate_inventory.json",
        {
            "version": FOLLOWUP_VERSION,
            "families": {
                family: [
                    {
                        "object_id": candidate.object_id,
                        "object_en": candidate.object_en,
                        "object_tr": candidate.object_tr,
                    }
                    for candidate in candidates
                ]
                for family, candidates in sorted(inventories.items())
            },
            "sizes": {family: len(candidates) for family, candidates in sorted(inventories.items())},
        },
    )
    write_json(
        manifests_dir / "subject_form_assignment.json",
        {"version": FOLLOWUP_VERSION, "seed": assignment_seed, "assignments": assignments},
    )
    write_json(
        manifests_dir / "subject_form_assignment_swap.json",
        {"version": FOLLOWUP_VERSION, "seed": assignment_seed, "assignments": swap_assignments},
    )
    write_csv(evaluations_dir / "paraphrase_probe_registry.csv", probes)

    integrity = {
        "status": "passed" if not overlaps and not duplicate_probe_ids else "failed",
        "expected_subjects": 100,
        "observed_subjects": len(selected_subject_ids),
        "expected_facts": 500,
        "observed_facts": len({probe["fact_id"] for probe in probes}),
        "expected_probes": 3000,
        "observed_probes": len(probes),
        "relation_counts": dict(sorted(relation_counts.items())),
        "form_counts": dict(sorted(form_counts.items())),
        "scaffold_counts": dict(sorted(scaffold_counts.items())),
        "normalized_training_prompt_overlap_count": len(overlaps),
        "normalized_training_prompt_overlap_probe_ids": overlaps,
        "duplicate_probe_ids": duplicate_probe_ids,
        "assignment_balance": balance,
    }
    write_json(manifests_dir / "integrity_audit.json", integrity)
    if integrity["status"] != "passed":
        raise ValueError(f"Pre-M2 integrity audit failed: {integrity}")

    contract = {
        "version": FOLLOWUP_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "phase_0_local_contract_frozen",
        "unit_decision": {
            "interpretation": "default_pilot",
            "subjects": 100,
            "facts": 500,
            "training_form_groups": {"A": 50, "B": 50},
            "scaled_500_subject_groups": "not_authorized",
        },
        "primary_unit": "subject_x_relation",
        "paraphrase_unit": "subject_x_relation_x_form_family_x_scaffold",
        "thresholds": {
            "exact_prefix_top1": 0.90,
            "each_required_heldout_form_top1": 0.80,
            "required_heldout_form_robust_intersection": 0.70,
            "form_c": "diagnostic_only",
        },
        "canonical_relation_v2_is_immutable": True,
        "m2_start_authorized": False,
    }
    write_json(manifests_dir / "experimental_contract.json", contract)

    resolved_models: dict[str, Any] = {
        "base": {"model_id": "HuggingFaceTB/SmolLM2-1.7B", "verification": "pending_hu_preflight"},
        "seed42_checkpoint200": {"verification": "pending_hu_preflight"},
        "seed43_data43_checkpoint75": {"verification": "pending_hu_preflight"},
    }
    for label, path in (model_manifests or {}).items():
        resolved_path = path.resolve()
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
        model_dir_value = payload.get("local_path_absolute") or payload.get("local_path")
        if not model_dir_value:
            raise ValueError(f"Model manifest lacks local path: {resolved_path}")
        model_dir = Path(str(model_dir_value)).resolve()
        weights_path = model_dir / "model.safetensors"
        if not weights_path.is_file():
            raise FileNotFoundError(f"Model weights missing for {label}: {weights_path}")
        live_weights_sha256 = sha256_file(weights_path)
        declared_weights_sha256 = payload.get("file_hashes", {}).get("model.safetensors")
        resolved_models[label] = {
            "verification": "live_weights_verified",
            "manifest_path": str(resolved_path),
            "manifest_sha256": sha256_file(resolved_path),
            "model_id": payload.get("model_id"),
            "resolved_revision": payload.get("resolved_revision"),
            "local_path": str(model_dir),
            "weights_path": str(weights_path),
            "weights_bytes": weights_path.stat().st_size,
            "live_weights_sha256": live_weights_sha256,
            "manifest_declared_weights_sha256": declared_weights_sha256,
            "manifest_declared_hash_matches_live": declared_weights_sha256 == live_weights_sha256,
        }
    environment: dict[str, Any] = {"python": platform.python_version()}
    for module_name in ("torch", "transformers"):
        try:
            module = __import__(module_name)
            environment[module_name] = getattr(module, "__version__", "unknown")
        except ModuleNotFoundError:
            environment[module_name] = None

    provenance = {
        "version": FOLLOWUP_VERSION,
        "repository": {
            "path": str(repo_root),
            "branch": _git_value(repo_root, "branch", "--show-current"),
            "commit": _git_value(repo_root, "rev-parse", "HEAD"),
        },
        "dataset": {
            "version": "relation_v2_gate_v1",
            "path": str(dataset_dir),
            "manifest_sha256": sha256_file(dataset_manifest_path),
            "canonical_profiles_sha256": sha256_file(canonical_path),
            "training_rows_sha256": sha256_file(training_path),
            "summary_sha256": sha256_file(summary_path),
        },
        "models": resolved_models,
        "environment": environment,
        "seeds": {
            "canonical_split": 42,
            "canonical_seed42_training": 42,
            "replication_training": 43,
            "replication_data_order": 43,
            "subject_form_assignment": assignment_seed,
        },
    }
    write_json(manifests_dir / "provenance.json", provenance)

    hashed_paths = [
        manifests_dir / "experimental_contract.json",
        manifests_dir / "provenance.json",
        manifests_dir / "template_registry.json",
        manifests_dir / "candidate_inventory.json",
        manifests_dir / "subject_form_assignment.json",
        manifests_dir / "subject_form_assignment_swap.json",
        manifests_dir / "integrity_audit.json",
        evaluations_dir / "paraphrase_probe_registry.csv",
    ]
    write_json(
        manifests_dir / "artifact_hashes.json",
        {str(path.relative_to(output_dir)): sha256_file(path) for path in hashed_paths},
    )
    return output_dir
