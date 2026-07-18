from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.pre_m2_followup import (
    FORM_TEMPLATES as LEGACY_FORM_TEMPLATES,
    RELATIONS,
    SCAFFOLDS,
    _stable_order,
    _subject_features,
    counterbalanced_subject_assignment,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json
from transfer_vs_relearning.utils.text import normalize_text


VERSION = "m1_form_generalization_v1"
FORM_IDS = ("form_a", "form_b", "form_c", "form_d")
FORM_TEMPLATES = {
    **LEGACY_FORM_TEMPLATES,
    "profession": {**LEGACY_FORM_TEMPLATES["profession"], "form_d": "What job does {subject} work in?"},
    "born_in": {**LEGACY_FORM_TEMPLATES["born_in"], "form_d": "Where was {subject} born?"},
    "lives_in": {**LEGACY_FORM_TEMPLATES["lives_in"], "form_d": "Where does {subject} live?"},
    "field_of_study": {**LEGACY_FORM_TEMPLATES["field_of_study"], "form_d": "What did {subject} study?"},
    "works_in_industry": {
        **LEGACY_FORM_TEMPLATES["works_in_industry"],
        "form_d": "What industry does {subject} work in?",
    },
}
SCAFFOLD_SEQUENCE = ("direct", "qa", "direct", "qa", "direct", "qa", "direct")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temp, path)


def _fact_id(profile: dict[str, str], relation: str) -> str:
    return f"{profile['subject_id']}_{relation}"


def _common(profile: dict[str, str], relation: str, condition: str) -> dict[str, str]:
    answer_column, _, frequency_column = RELATION_MAP[relation]
    return {
        "answer": profile[answer_column],
        "branch_group": profile["branch_group"],
        "condition": condition,
        "fact_id": _fact_id(profile, relation),
        "frequency_bucket": profile[frequency_column],
        "language": "en",
        "name_rarity_bucket": profile["name_rarity_bucket"],
        "name_type": profile["name_type"],
        "popularity_bucket": profile["popularity_bucket"],
        "popularity_rank": profile["popularity_rank"],
        "relation": relation,
        "row_id": profile["row_id"],
        "subject": profile["subject"],
        "subject_id": profile["subject_id"],
    }


def _balanced_primary_forms(profiles: list[dict[str, str]]) -> dict[str, str]:
    """Assign the four-row A/B share equally, stratified by relation and branch."""
    facts: list[tuple[str, str, str]] = []
    for profile in profiles:
        for relation in RELATIONS:
            facts.append((_fact_id(profile, relation), relation, profile["branch_group"]))
    by_stratum: dict[tuple[str, str], list[str]] = defaultdict(list)
    for fact_id, relation, branch in facts:
        by_stratum[(relation, branch)].append(fact_id)
    primary: dict[str, str] = {}
    for stratum, fact_ids in sorted(by_stratum.items()):
        ordered = sorted(fact_ids, key=lambda value: _stable_order(value, 20260718))
        if len(ordered) % 2:
            raise ValueError(f"Balanced form allocation requires even stratum: {stratum}")
        for fact_id in ordered[: len(ordered) // 2]:
            primary[fact_id] = "form_a"
        for fact_id in ordered[len(ordered) // 2 :]:
            primary[fact_id] = "form_b"
    if Counter(primary.values()) != Counter({"form_a": 250, "form_b": 250}):
        raise AssertionError("Unexpected primary-form allocation")
    return primary


def _form_schedule(primary_form: str) -> tuple[tuple[str, str], ...]:
    if primary_form not in {"form_a", "form_b"}:
        raise ValueError(f"Unsupported primary form: {primary_form}")
    other = "form_b" if primary_form == "form_a" else "form_a"
    # Primary form: 2 direct + 2 QA; other form: 2 direct + 1 QA.
    return (
        (primary_form, "direct"),
        (primary_form, "qa"),
        (other, "direct"),
        (other, "qa"),
        (other, "direct"),
        (primary_form, "qa"),
        (primary_form, "direct"),
    )


def _rows_for_fact(
    profile: dict[str, str],
    relation: str,
    condition: str,
    schedule: tuple[tuple[str, str], ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    common = _common(profile, relation, condition)
    train_rows: list[dict[str, Any]] = []
    for exposure_index, (form_id, scaffold_id) in enumerate(schedule, start=1):
        question = FORM_TEMPLATES[relation][form_id].format(subject=profile["subject"])
        prompt = SCAFFOLDS[scaffold_id].format(question=question)
        train_rows.append(
            {
                **common,
                "exposure_index": exposure_index,
                "scaffold_id": scaffold_id,
                "training_form_id": form_id,
                "split": f"{VERSION}_{condition}_train",
                "template_id": f"{relation}_{form_id}_{scaffold_id}_exposure_{exposure_index:02d}",
                "text": f"{prompt} {common['answer']}",
            }
        )
    monitor_form, monitor_scaffold = schedule[0]
    monitor_question = FORM_TEMPLATES[relation][monitor_form].format(subject=profile["subject"])
    validation = {
        **common,
        "exposure_index": 0,
        "scaffold_id": monitor_scaffold,
        "training_form_id": monitor_form,
        "split": f"{VERSION}_{condition}_validation",
        "template_id": f"{relation}_{monitor_form}_{monitor_scaffold}_monitor",
        "text": f"{SCAFFOLDS[monitor_scaffold].format(question=monitor_question)} {common['answer']}",
    }
    return train_rows, validation


def _form_d_probes(profiles: list[dict[str, str]], assignments: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        for relation in RELATIONS:
            answer_column, _, frequency_column = RELATION_MAP[relation]
            for form_id in FORM_IDS:
                question = FORM_TEMPLATES[relation][form_id].format(subject=profile["subject"])
                for scaffold_id, scaffold in SCAFFOLDS.items():
                    wp1b_cell = (
                        "seen" if form_id == assignments[profile["subject_id"]]["training_form_id"]
                        else "crossed" if form_id in {"form_a", "form_b"}
                        else "heldout_variant"
                    )
                    probes.append(
                        {
                            "probe_id": f"{profile['subject_id']}_{relation}_{form_id}_{scaffold_id}",
                            "fact_id": _fact_id(profile, relation),
                            "subject_id": profile["subject_id"],
                            "subject": profile["subject"],
                            "relation": relation,
                            "form_id": form_id,
                            "scaffold_id": scaffold_id,
                            "canonical_m1_exposure": "heldout_unseen",
                            "wp1b_counterbalance_cell": wp1b_cell,
                            "question": question,
                            "rendered_prompt": scaffold.format(question=question),
                            "expected_answer": profile[answer_column],
                            "branch_group": profile["branch_group"],
                            "name_type": profile["name_type"],
                            "name_rarity_bucket": profile["name_rarity_bucket"],
                            "popularity_bucket": profile["popularity_bucket"],
                            "frequency_bucket": profile[frequency_column],
                        }
                    )
    return probes


def _prompt_overlap(train_rows: list[dict[str, Any]], probes: list[dict[str, Any]]) -> list[str]:
    heldout = {
        (probe["fact_id"], normalize_text(str(probe["rendered_prompt"])))
        for probe in probes
        if probe["form_id"] in {"form_c", "form_d"}
    }
    overlaps: list[str] = []
    for row in train_rows:
        answer_start = str(row["text"]).rfind(str(row["answer"]))
        key = (str(row["fact_id"]), normalize_text(str(row["text"])[:answer_start].rstrip()))
        if key in heldout:
            overlaps.append(str(row["fact_id"]))
    return sorted(set(overlaps))


def build_m1_form_generalization_datasets(
    repo_root: Path,
    *,
    dataset_dir: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    dataset_dir = (dataset_dir or repo_root / "artifacts/datasets/relation_v2_gate_v1").resolve()
    output_dir = (output_dir or repo_root / f"artifacts/{VERSION}").resolve()
    canonical_rows = read_csv_rows(dataset_dir / "data/canonical_subject_profiles_5000.csv")
    summary = json.loads((dataset_dir / "acquisition_100_subjects_direct/summary.json").read_text(encoding="utf-8"))
    selected_ids = set(summary["selected_subject_ids"])
    profiles = [row for row in canonical_rows if row["subject_id"] in selected_ids]
    if len(profiles) != 100:
        raise ValueError(f"Expected 100 selected profiles, found {len(profiles)}")
    assignments_list = counterbalanced_subject_assignment(canonical_rows, sorted(selected_ids), seed=20260717)
    assignments = {item["subject_id"]: item for item in assignments_list}
    primary_forms = _balanced_primary_forms(profiles)
    probes = _form_d_probes(profiles, assignments)
    if len(probes) != 4000 or len({probe["probe_id"] for probe in probes}) != 4000:
        raise ValueError("Form-generalization probe registry must contain 4,000 unique probes")

    all_rows: dict[str, list[dict[str, Any]]] = {"control": [], "balanced_ab": []}
    validations: dict[str, list[dict[str, Any]]] = {"control": [], "balanced_ab": []}
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        for relation in RELATIONS:
            assigned = assignments[profile["subject_id"]]["training_form_id"]
            control_schedule = tuple((assigned, scaffold) for scaffold in SCAFFOLD_SEQUENCE)
            balanced_schedule = _form_schedule(primary_forms[_fact_id(profile, relation)])
            for condition, schedule in (("control", control_schedule), ("balanced_ab", balanced_schedule)):
                rows, validation = _rows_for_fact(profile, relation, condition, schedule)
                all_rows[condition].extend(rows)
                validations[condition].append(validation)

    conditions: dict[str, Any] = {}
    for condition in ("control", "balanced_ab"):
        train_rows, validation_rows = all_rows[condition], validations[condition]
        train_path = output_dir / "datasets" / condition / "train.jsonl"
        validation_path = output_dir / "datasets" / condition / "validation.jsonl"
        _write_jsonl(train_path, train_rows)
        _write_jsonl(validation_path, validation_rows)
        fact_counts = Counter(row["fact_id"] for row in train_rows)
        form_counts = Counter(row["training_form_id"] for row in train_rows)
        scaffold_counts = Counter(row["scaffold_id"] for row in train_rows)
        per_fact_forms = {fact_id: {row["training_form_id"] for row in train_rows if row["fact_id"] == fact_id} for fact_id in fact_counts}
        per_fact_scaffolds = {fact_id: {row["scaffold_id"] for row in train_rows if row["fact_id"] == fact_id} for fact_id in fact_counts}
        overlaps = _prompt_overlap(train_rows, probes)
        expected_forms = {"form_a", "form_b"} if condition == "balanced_ab" else None
        status = "passed" if (
            len(train_rows) == 3500
            and len(validation_rows) == 500
            and set(fact_counts.values()) == {7}
            and scaffold_counts == Counter({"direct": 2000, "qa": 1500})
            and not overlaps
            and (expected_forms is None or form_counts == Counter({"form_a": 1750, "form_b": 1750}))
            and (expected_forms is None or all(forms == expected_forms for forms in per_fact_forms.values()))
            and all(scaffolds == {"direct", "qa"} for scaffolds in per_fact_scaffolds.values())
        ) else "failed"
        conditions[condition] = {
            "status": status,
            "train_file": str(train_path.relative_to(output_dir)),
            "train_sha256": sha256_file(train_path),
            "validation_file": str(validation_path.relative_to(output_dir)),
            "validation_sha256": sha256_file(validation_path),
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
            "fact_rows": sorted(set(fact_counts.values())),
            "form_row_counts": dict(sorted(form_counts.items())),
            "scaffold_row_counts": dict(sorted(scaffold_counts.items())),
            "heldout_prompt_overlap_fact_ids": overlaps,
        }
        if status != "passed":
            raise ValueError(f"{condition} integrity failure: {conditions[condition]}")

    write_csv(output_dir / "evaluations/four_form_probe_registry.csv", probes)
    write_json(output_dir / "manifests/template_registry.json", {
        "version": VERSION,
        "forms": list(FORM_IDS),
        "scaffolds": SCAFFOLDS,
        "relations": FORM_TEMPLATES,
        "form_c_d_are_training_heldout": True,
    })
    write_json(output_dir / "manifests/control_subject_assignment.json", {"assignments": assignments_list})
    write_json(output_dir / "manifests/balanced_primary_form_assignment.json", {"primary_forms": primary_forms})
    manifest = {
        "version": VERSION,
        "status": "passed",
        "fact_graph": {"subjects": 100, "relations": 5, "facts": 500},
        "probe_contract": {"forms": list(FORM_IDS), "scaffolds": list(SCAFFOLDS), "probes": 4000, "form_c_d_training_rows": 0},
        "exposure_contract": {"rows_per_fact": 7, "rows_per_condition": 3500, "validation_rows_per_condition": 500, "scaffold_sequence": list(SCAFFOLD_SEQUENCE), "supervised_answer_token_exposure_matched": True, "optimizer_updates": 252, "supervise_eos": False},
        "conditions": conditions,
    }
    write_json(output_dir / "dataset_manifest.json", manifest)
    write_json(output_dir / "manifests/artifact_hashes.json", {
        "dataset_manifest.json": sha256_file(output_dir / "dataset_manifest.json"),
        "evaluations/four_form_probe_registry.csv": sha256_file(output_dir / "evaluations/four_form_probe_registry.csv"),
        "manifests/template_registry.json": sha256_file(output_dir / "manifests/template_registry.json"),
        "manifests/control_subject_assignment.json": sha256_file(output_dir / "manifests/control_subject_assignment.json"),
        "manifests/balanced_primary_form_assignment.json": sha256_file(output_dir / "manifests/balanced_primary_form_assignment.json"),
    })
    return output_dir
