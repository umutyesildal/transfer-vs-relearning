from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES, RELATION_MAP
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json
from transfer_vs_relearning.utils.text import normalize_text


WP3_VERSION = "pre_m2_wp3_stage_a_v1"
RELATIONS = ("studied_at", "field_of_study", "works_at", "works_in_industry")
CONFUSABLE_RELATION = {
    "studied_at": "field_of_study",
    "field_of_study": "studied_at",
    "works_at": "works_in_industry",
    "works_in_industry": "works_at",
}
FORM_TEMPLATES = {
    "studied_at": {
        "form_a": "Where did {subject} study?",
        "form_b": "Which institution did {subject} attend?",
        "form_c": "At what university was {subject} educated?",
    },
    "field_of_study": {
        "form_a": "What did {subject} study?",
        "form_b": "Which academic field did {subject} pursue?",
        "form_c": "What subject area is listed for {subject}?",
    },
    "works_at": {
        "form_a": "Where does {subject} work?",
        "form_b": "Which organization employs {subject}?",
        "form_c": "What is {subject}'s employer?",
    },
    "works_in_industry": {
        "form_a": "In which industry does {subject} work?",
        "form_b": "What business sector employs {subject}?",
        "form_c": "Which industry is associated with {subject}'s job?",
    },
}
SCAFFOLDS = {"direct": "{question}", "qa": "Question: {question}\nAnswer:"}
EXPOSURES = ("direct", "qa", "direct", "qa", "direct", "qa", "direct")


def _stable_order(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}|{value}".encode("utf-8")).hexdigest()


def _features(row: dict[str, str]) -> tuple[str, ...]:
    values = [
        f"branch={row['branch_group']}",
        f"name_type={row['name_type']}",
        f"name_rarity={row['name_rarity_bucket']}",
        f"popularity={row['popularity_bucket']}",
    ]
    for relation in RELATIONS:
        values.append(f"{relation}_frequency={row[RELATION_MAP[relation][2]]}")
    return tuple(values)


def balanced_assignment(rows: list[dict[str, str]], subject_ids: list[str], seed: int) -> list[dict[str, Any]]:
    by_subject = {row["subject_id"]: row for row in rows}
    selected = [by_subject[subject_id] for subject_id in subject_ids]
    if len(selected) % 2:
        raise ValueError("WP3 counterbalance requires an even subject count")
    target = len(selected) // 2
    ordered = sorted(selected, key=lambda row: _stable_order(row["subject_id"], seed))
    groups = {"A": {row["subject_id"] for row in ordered[:target]}, "B": {row["subject_id"] for row in ordered[target:]}}
    feature_sets = {row["subject_id"]: set(_features(row)) for row in selected}
    all_features = sorted(set().union(*feature_sets.values()))

    def counts(group: str) -> Counter[str]:
        return Counter(feature for subject_id in groups[group] for feature in feature_sets[subject_id])

    def score(first: Counter[str], second: Counter[str]) -> int:
        return sum((first[feature] - second[feature]) ** 2 for feature in all_features)

    counts_a, counts_b = counts("A"), counts("B")
    while True:
        current = score(counts_a, counts_b)
        best: tuple[int, str, str, Counter[str], Counter[str]] | None = None
        for subject_a in sorted(groups["A"]):
            for subject_b in sorted(groups["B"]):
                next_a, next_b = counts_a.copy(), counts_b.copy()
                next_a.subtract(feature_sets[subject_a]); next_a.update(feature_sets[subject_b])
                next_b.subtract(feature_sets[subject_b]); next_b.update(feature_sets[subject_a])
                candidate = (score(next_a, next_b), subject_a, subject_b, next_a, next_b)
                if candidate[0] < current and (best is None or candidate[:3] < best[:3]):
                    best = candidate
        if best is None:
            break
        _, subject_a, subject_b, counts_a, counts_b = best
        groups["A"].remove(subject_a); groups["A"].add(subject_b)
        groups["B"].remove(subject_b); groups["B"].add(subject_a)

    assignments = []
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
                "features": list(_features(row)),
            }
        )
    return sorted(assignments, key=lambda row: row["subject_id"])


def _balance(assignments: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"A": Counter(), "B": Counter()}
    sizes = Counter()
    for row in assignments:
        group = row["training_form_group"]
        sizes[group] += 1
        counts[group].update(row["features"])
    features = sorted(set(counts["A"]) | set(counts["B"]))
    differences = {feature: counts["A"][feature] - counts["B"][feature] for feature in features}
    return {
        "group_sizes": dict(sorted(sizes.items())),
        "a_minus_b": differences,
        "max_absolute_feature_difference": max((abs(value) for value in differences.values()), default=0),
    }


def merge_profiles(v1_rows: list[dict[str, str]], v2_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    v1_by_subject = {row["subject_id"]: row for row in v1_rows}
    if set(v1_by_subject) != {row["subject_id"] for row in v2_rows}:
        raise ValueError("V1 and V2 canonical subject ID sets differ")
    output = []
    for v2 in v2_rows:
        v1 = v1_by_subject[v2["subject_id"]]
        for key in ("row_id", "subject", "name_type", "name_rarity_bucket", "popularity_rank", "popularity_bucket", "branch_group"):
            if v1[key] != v2[key]:
                raise ValueError(f"Canonical identity mismatch for {v2['subject_id']} field {key}")
        output.append(
            {
                **v2,
                "university_en": v1["university_en"],
                "university_tr": v1["university_tr"],
                "university_frequency_bucket": v1["university_frequency_bucket"],
                "employer_en": v1["employer_en"],
                "employer_tr": v1["employer_tr"],
                "employer_frequency_bucket": v1["employer_frequency_bucket"],
            }
        )
    return output


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, path)


def _build_rows(
    profiles: list[dict[str, str]],
    assignments: list[dict[str, Any]],
    split_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_subject = {row["subject_id"]: row for row in profiles}
    train, validation, probes = [], [], []
    for assignment in assignments:
        profile = by_subject[assignment["subject_id"]]
        for relation in RELATIONS:
            answer = profile[RELATION_MAP[relation][0]]
            confusable_relation = CONFUSABLE_RELATION[relation]
            confusable_answer = profile[RELATION_MAP[confusable_relation][0]]
            if normalize_text(answer) == normalize_text(confusable_answer):
                raise ValueError(f"WP3 hard-negative surface collision for {profile['subject_id']} {relation}")
            fact_id = f"{profile['subject_id']}_{relation}"
            form_id = assignment["training_form_id"]
            question = FORM_TEMPLATES[relation][form_id].format(subject=profile["subject"])
            common = {
                "answer": answer,
                "branch_group": profile["branch_group"],
                "fact_id": fact_id,
                "frequency_bucket": profile[RELATION_MAP[relation][2]],
                "language": "en",
                "name_rarity_bucket": profile["name_rarity_bucket"],
                "name_type": profile["name_type"],
                "popularity_bucket": profile["popularity_bucket"],
                "popularity_rank": profile["popularity_rank"],
                "relation": relation,
                "row_id": profile["row_id"],
                "subject": profile["subject"],
                "subject_id": profile["subject_id"],
                "training_form_group": assignment["training_form_group"],
                "training_form_id": form_id,
            }
            for exposure_index, scaffold_id in enumerate(EXPOSURES, start=1):
                prompt = SCAFFOLDS[scaffold_id].format(question=question)
                train.append(
                    {
                        **common,
                        "exposure_index": exposure_index,
                        "scaffold_id": scaffold_id,
                        "split": f"{split_name}_train",
                        "template_id": f"{relation}_{form_id}_{scaffold_id}_exposure_{exposure_index:02d}",
                        "text": f"{prompt} {answer}",
                    }
                )
            validation.append(
                {
                    **common,
                    "exposure_index": 0,
                    "scaffold_id": "qa",
                    "split": f"{split_name}_validation",
                    "template_id": f"{relation}_{form_id}_qa_monitor",
                    "text": f"{SCAFFOLDS['qa'].format(question=question)} {answer}",
                }
            )
            for probe_form_id in ("form_a", "form_b", "form_c"):
                probe_question = FORM_TEMPLATES[relation][probe_form_id].format(subject=profile["subject"])
                for scaffold_id, scaffold in SCAFFOLDS.items():
                    cell = "seen" if probe_form_id == form_id else "crossed" if probe_form_id == assignment["heldout_crossed_form_id"] else "novel"
                    probes.append(
                        {
                            "probe_id": f"{fact_id}_{probe_form_id}_{scaffold_id}",
                            "fact_id": fact_id,
                            "subject_id": profile["subject_id"],
                            "subject": profile["subject"],
                            "relation": relation,
                            "form_id": probe_form_id,
                            "scaffold_id": scaffold_id,
                            "wp1b_counterbalance_cell": cell,
                            "question": probe_question,
                            "rendered_prompt": scaffold.format(question=probe_question),
                            "expected_answer": answer,
                            "same_subject_confusable_relation": confusable_relation,
                            "same_subject_confusable_answer": confusable_answer,
                            "branch_group": profile["branch_group"],
                            "name_type": profile["name_type"],
                            "name_rarity_bucket": profile["name_rarity_bucket"],
                            "popularity_bucket": profile["popularity_bucket"],
                            "frequency_bucket": profile[RELATION_MAP[relation][2]],
                        }
                    )
    return train, validation, probes


def _audit_stage(
    name: str,
    train: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    probes: list[dict[str, Any]],
    expected_subjects: int,
) -> dict[str, Any]:
    expected_facts = expected_subjects * len(RELATIONS)
    fact_counts = Counter(row["fact_id"] for row in train)
    probe_counts = Counter(row["fact_id"] for row in probes)
    relation_counts = Counter(row["relation"] for row in train)
    duplicate_probe_ids = [key for key, value in Counter(row["probe_id"] for row in probes).items() if value != 1]
    invalid_negatives = [row["probe_id"] for row in probes if row["same_subject_confusable_relation"] != CONFUSABLE_RELATION[row["relation"]] or normalize_text(row["expected_answer"]) == normalize_text(row["same_subject_confusable_answer"])]
    train_prompt_keys = set()
    for row in train:
        answer_start = row["text"].rfind(row["answer"])
        train_prompt_keys.add((row["fact_id"], normalize_text(row["text"][:answer_start].rstrip())))
    overlap_counts = Counter()
    for row in probes:
        if (row["fact_id"], normalize_text(row["rendered_prompt"])) in train_prompt_keys:
            overlap_counts[row["wp1b_counterbalance_cell"]] += 1
    expected = {
        "train": expected_facts * len(EXPOSURES),
        "validation": expected_facts,
        "probes": expected_facts * 6,
        "seen_overlap": expected_facts * 2,
    }
    status = "passed"
    if (
        len(train) != expected["train"]
        or len(validation) != expected["validation"]
        or len(probes) != expected["probes"]
        or len(fact_counts) != expected_facts
        or set(fact_counts.values()) != {7}
        or set(probe_counts.values()) != {6}
        or relation_counts != Counter({relation: expected_subjects * 7 for relation in RELATIONS})
        or duplicate_probe_ids
        or invalid_negatives
        or overlap_counts != Counter({"seen": expected["seen_overlap"]})
    ):
        status = "failed"
    return {
        "name": name,
        "status": status,
        "subjects": expected_subjects,
        "facts": len(fact_counts),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "probe_rows": len(probes),
        "rows_per_fact": sorted(set(fact_counts.values())),
        "probes_per_fact": sorted(set(probe_counts.values())),
        "relation_train_rows": dict(sorted(relation_counts.items())),
        "duplicate_probe_ids": duplicate_probe_ids,
        "invalid_hard_negative_probe_ids": invalid_negatives,
        "normalized_training_prompt_overlap_by_cell": dict(sorted(overlap_counts.items())),
    }


def build_wp3_stage_a(repo_root: Path, *, output_root: Path | None = None, seed: int = 20260718) -> Path:
    repo_root = repo_root.resolve()
    v1_dir = repo_root / "artifacts/datasets/synthetic_v1"
    v2_dir = repo_root / "artifacts/datasets/relation_v2_gate_v1"
    output_root = (output_root or repo_root / "artifacts/pre_m2_followup_v1/training/joint_relation_capture").resolve()
    profiles = merge_profiles(
        read_csv_rows(v1_dir / "data/canonical_subject_profiles_5000.csv"),
        read_csv_rows(v2_dir / "data/canonical_subject_profiles_5000.csv"),
    )
    selected_subject_ids = json.loads(
        (v2_dir / "acquisition_100_subjects_direct/summary.json").read_text(encoding="utf-8")
    )["selected_subject_ids"]
    assignments = balanced_assignment(profiles, selected_subject_ids, seed)
    group_a = sorted((row for row in assignments if row["training_form_group"] == "A"), key=lambda row: _stable_order(row["subject_id"], seed + 1))[:5]
    group_b = sorted((row for row in assignments if row["training_form_group"] == "B"), key=lambda row: _stable_order(row["subject_id"], seed + 1))[:5]
    fixture_assignments = sorted(group_a + group_b, key=lambda row: row["subject_id"])
    stages = {
        "fixture_10": fixture_assignments,
        "stage_a_100": assignments,
    }
    write_csv(output_root / "canonical_subject_profiles_5000.csv", profiles)
    stage_summaries = {}
    for stage_name, stage_assignments in stages.items():
        train, validation, probes = _build_rows(profiles, stage_assignments, f"wp3_{stage_name}")
        audit = _audit_stage(stage_name, train, validation, probes, len(stage_assignments))
        if audit["status"] != "passed":
            raise ValueError(f"WP3 {stage_name} integrity failed: {audit}")
        stage_dir = output_root / stage_name
        write_csv(stage_dir / DATASET_FILES["canonical_profiles"], profiles)
        _write_jsonl(stage_dir / "train.jsonl", train)
        _write_jsonl(stage_dir / "validation.jsonl", validation)
        write_csv(stage_dir / "probe_registry.csv", probes)
        if stage_name == "fixture_10":
            smoke_probes = [
                next(
                    row
                    for row in probes
                    if row["relation"] == relation
                    and row["form_id"] == "form_a"
                    and row["scaffold_id"] == "direct"
                )
                for relation in RELATIONS
            ]
            write_csv(stage_dir / "evaluation_smoke_registry.csv", smoke_probes)
        write_json(stage_dir / "integrity_audit.json", audit)
        files = {
            str(DATASET_FILES["canonical_profiles"]): sha256_file(
                stage_dir / DATASET_FILES["canonical_profiles"]
            ),
            "train.jsonl": sha256_file(stage_dir / "train.jsonl"),
            "validation.jsonl": sha256_file(stage_dir / "validation.jsonl"),
            "probe_registry.csv": sha256_file(stage_dir / "probe_registry.csv"),
            "integrity_audit.json": sha256_file(stage_dir / "integrity_audit.json"),
        }
        if stage_name == "fixture_10":
            files["evaluation_smoke_registry.csv"] = sha256_file(
                stage_dir / "evaluation_smoke_registry.csv"
            )
        write_json(
            stage_dir / "manifest.json",
            {
                "version": WP3_VERSION,
                "stage": stage_name,
                "status": "passed",
                "source_hashes": {
                    "synthetic_v1_manifest": sha256_file(v1_dir / "manifest.json"),
                    "relation_v2_manifest": sha256_file(v2_dir / "manifest.json"),
                },
                "files": files,
                "contract": audit,
            },
        )
        stage_summaries[stage_name] = audit
    assignment_payload = {
        "version": WP3_VERSION,
        "seed": seed,
        "balance": _balance(assignments),
        "assignments": assignments,
        "fixture_subject_ids": [row["subject_id"] for row in fixture_assignments],
    }
    write_json(output_root / "subject_form_assignment.json", assignment_payload)
    write_json(
        output_root / "manifest.json",
        {
            "version": WP3_VERSION,
            "status": "passed",
            "canonical_profiles_sha256": sha256_file(output_root / "canonical_subject_profiles_5000.csv"),
            "assignment_sha256": sha256_file(output_root / "subject_form_assignment.json"),
            "stages": stage_summaries,
        },
    )
    return output_root
