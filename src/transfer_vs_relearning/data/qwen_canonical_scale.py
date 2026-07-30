from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.m1_canonical_form_diversity import SLOTS
from transfer_vs_relearning.data.m1_form_generalization import FORM_TEMPLATES, SCAFFOLDS
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_csv, write_json


VERSION = "qwen_canonical_scale_v1"
SUBJECTS = 5_000
FACTS = 25_000
TRAIN_ROWS = 175_000
MONITORING_VALIDATION_ROWS = 2_301
REPLAY_SOURCE_ROWS = 17_500
REPLAY_CYCLES = 10

# Frozen Relation V2 declaratives from syntheticFacts/generate_relation_v2_dataset.py.
EN_DECLARATIVE = {
    "profession": (
        "{subject} works as a {answer}.",
        "The profession of {subject} is {answer}.",
        "{subject}'s profession is {answer}.",
    ),
    "born_in": (
        "{subject} was born in {answer}.",
        "The birthplace of {subject} is {answer}.",
        "{subject}'s birthplace is {answer}.",
    ),
    "lives_in": (
        "{subject} currently lives in {answer}.",
        "{subject} resides in {answer}.",
        "The current residence of {subject} is {answer}.",
    ),
    "field_of_study": (
        "{subject} studied {answer}.",
        "The field of study of {subject} is {answer}.",
        "{subject}'s academic field is {answer}.",
    ),
    "works_in_industry": (
        "{subject} works in {answer}.",
        "The industry of {subject} is {answer}.",
        "{subject}'s work sector is {answer}.",
    ),
}


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _write_jsonl_exclusive(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _common(profile: dict[str, str], relation: str) -> dict[str, Any]:
    answer_column, _, frequency_column = RELATION_MAP[relation]
    return {
        "answer": profile[answer_column],
        "branch_group": profile["branch_group"],
        "condition": "canonical_balanced_ab",
        "fact_id": f"{profile['subject_id']}_{relation}",
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


def _curriculum_rows(profile: dict[str, str], relation: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    common = _common(profile, relation)
    rows: list[dict[str, Any]] = []
    for exposure_index, slot in enumerate(SLOTS, start=1):
        if slot.startswith("decl_"):
            template_index = int(slot.rsplit("_", 1)[1]) - 1
            text = EN_DECLARATIVE[relation][template_index].format(
                subject=common["subject"], answer=common["answer"]
            )
            row = {
                **common,
                "exposure_index": exposure_index,
                "split": f"{VERSION}_train",
                "template_id": f"{relation}_en_canonical_5000_{slot}",
                "text": text,
                "training_representation": slot,
            }
        else:
            form_id, scaffold_id = slot.rsplit("_", 1)
            question = FORM_TEMPLATES[relation][form_id].format(subject=common["subject"])
            row = {
                **common,
                "exposure_index": exposure_index,
                "scaffold_id": scaffold_id,
                "split": f"{VERSION}_train",
                "template_id": f"{relation}_{slot}",
                "text": f"{SCAFFOLDS[scaffold_id].format(question=question)} {common['answer']}",
                "training_form_id": form_id,
                "training_representation": slot,
            }
        rows.append(row)
    validation = {
        **rows[0],
        "exposure_index": 0,
        "split": f"{VERSION}_validation",
        "training_representation": "decl_01_monitor",
    }
    return rows, validation


def _probe_rows(profiles: list[dict[str, str]]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        for relation in RELATIONS:
            common = _common(profile, relation)
            for form_id in ("form_a", "form_b", "form_c", "form_d"):
                question = FORM_TEMPLATES[relation][form_id].format(subject=common["subject"])
                for scaffold_id, scaffold in SCAFFOLDS.items():
                    probes.append(
                        {
                            "probe_id": f"{common['fact_id']}_{form_id}_{scaffold_id}",
                            "fact_id": common["fact_id"],
                            "subject_id": common["subject_id"],
                            "subject": common["subject"],
                            "relation": relation,
                            "form_id": form_id,
                            "scaffold_id": scaffold_id,
                            "question": question,
                            "rendered_prompt": scaffold.format(question=question),
                            "expected_answer": common["answer"],
                            "branch_group": common["branch_group"],
                            "name_type": common["name_type"],
                            "name_rarity_bucket": common["name_rarity_bucket"],
                            "popularity_bucket": common["popularity_bucket"],
                            "frequency_bucket": common["frequency_bucket"],
                        }
                    )
    return probes


def _exact_probe_rows(profiles: list[dict[str, str]]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        for relation in RELATIONS:
            common = _common(profile, relation)
            text = EN_DECLARATIVE[relation][0].format(
                subject=common["subject"], answer=common["answer"]
            )
            answer_start = text.rfind(str(common["answer"]))
            if answer_start < 0:
                raise ValueError(f"Exact answer is absent from canonical row: {common['fact_id']}")
            probes.append(
                {
                    "fact_id": common["fact_id"],
                    "subject_id": common["subject_id"],
                    "relation": relation,
                    "subject": common["subject"],
                    "question": text[:answer_start].rstrip(),
                    "expected_answer": common["answer"],
                    "template_id": f"{relation}_en_canonical_5000_exact_prefix",
                }
            )
    return probes


def _read_selected_subjects(path: Path, expected: int) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    selected = [str(value) for value in payload["selected_subject_ids"]]
    if len(selected) != expected or len(set(selected)) != expected:
        raise ValueError(f"Expected {expected} unique nested subjects in {path}")
    return sorted(selected)


def _assert_source_contract(repo_root: Path, profiles_path: Path) -> dict[str, Any]:
    source_manifest_path = repo_root / "artifacts/datasets/relation_v2_gate_v1/manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    relative = "data/canonical_subject_profiles_5000.csv"
    expected_hash = source_manifest["files"][relative]
    observed_hash = sha256_file(profiles_path)
    if observed_hash != expected_hash:
        raise ValueError(f"Canonical profile hash mismatch: {observed_hash} != {expected_hash}")
    if tuple(source_manifest["relations"]) != tuple(RELATIONS):
        raise ValueError("Relation V2 source manifest relation order changed")
    return {
        "manifest_path": str(source_manifest_path),
        "manifest_sha256": sha256_file(source_manifest_path),
        "profiles_path": str(profiles_path),
        "profiles_sha256": observed_hash,
    }


def _assert_nested_500_curriculum_matches(
    repo_root: Path,
    generated_rows: list[dict[str, Any]],
    nested_500: set[str],
) -> str:
    reference_path = repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/train.jsonl"
    reference = read_jsonl(reference_path)
    reference_by_fact: dict[str, dict[str, str]] = defaultdict(dict)
    for row in reference:
        template_id = str(row["template_id"])
        if "_decl_" in template_id:
            slot = f"decl_{template_id.rsplit('_', 1)[1]}"
            reference_by_fact[str(row["fact_id"])][slot] = str(row["text"])
    generated = {
        (str(row["fact_id"]), str(row["training_representation"])): str(row["text"])
        for row in generated_rows
        if str(row["subject_id"]) in nested_500
    }
    if len(generated) != 17_500:
        raise ValueError("Generated nested-500 curriculum is incomplete")
    for fact_id, declaratives in reference_by_fact.items():
        for slot, text in declaratives.items():
            if generated[(fact_id, slot)] != text:
                raise ValueError(f"Canonical declarative drift for {fact_id}/{slot}")
    # The A/B rows are generated by the same imported frozen templates used in the passing run.
    return sha256_file(reference_path)


def _materialize_replay(
    *,
    profiles: list[dict[str, str]],
    source_train: Path,
    source_validation: Path,
    output_dir: Path,
) -> dict[str, Any]:
    source_manifest_path = source_train.parent / "manifest.json"
    if source_validation.parent != source_train.parent or not source_manifest_path.is_file():
        raise ValueError("Replay sources must share a frozen manifest directory")
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    expected_train_hash = source_manifest["files"]["train"]["sha256"]
    expected_validation_hash = source_manifest["files"]["validation"]["sha256"]
    if sha256_file(source_train) != expected_train_hash:
        raise ValueError("Frozen replay train hash does not match its manifest")
    if sha256_file(source_validation) != expected_validation_hash:
        raise ValueError("Frozen replay validation hash does not match its manifest")
    train_rows = read_jsonl(source_train)
    validation_rows = read_jsonl(source_validation)
    if len(train_rows) != REPLAY_SOURCE_ROWS or len(validation_rows) != MONITORING_VALIDATION_ROWS:
        raise ValueError("Frozen replay source row counts changed")

    normalized_subjects = sorted({_normalize(row["subject"]) for row in profiles})
    subject_pattern = re.compile("|".join(re.escape(value) for value in normalized_subjects))
    contaminated: list[str] = []
    for row in [*train_rows, *validation_rows]:
        if subject_pattern.search(_normalize(str(row["text"]))):
            contaminated.append(str(row.get("document_id", "unknown")))
    if contaminated:
        raise ValueError(f"Frozen replay contains full-population subject surfaces: {contaminated[:5]}")

    cycled: list[dict[str, Any]] = []
    for cycle in range(REPLAY_CYCLES):
        for source_index, row in enumerate(train_rows):
            cycled.append({**row, "replay_cycle": cycle, "replay_source_index": source_index})
    if len(cycled) != TRAIN_ROWS:
        raise AssertionError("Replay cycling did not create 175,000 aligned rows")

    replay_dir = output_dir / "anchor"
    replay_dir.mkdir(parents=True)
    train_path = replay_dir / "train_repeated_10x.jsonl"
    validation_path = replay_dir / "validation.jsonl"
    _write_jsonl_exclusive(train_path, cycled)
    _write_jsonl_exclusive(validation_path, validation_rows)
    return {
        "source_manifest": str(source_manifest_path),
        "source_manifest_sha256": sha256_file(source_manifest_path),
        "source_train": str(source_train),
        "source_train_sha256": sha256_file(source_train),
        "source_train_rows": len(train_rows),
        "source_validation": str(source_validation),
        "source_validation_sha256": sha256_file(source_validation),
        "source_validation_rows": len(validation_rows),
        "cycles": REPLAY_CYCLES,
        "full_population_subject_surface_hits": 0,
        "train_file": str(train_path),
        "train_sha256": sha256_file(train_path),
        "train_rows": len(cycled),
        "validation_file": str(validation_path),
        "validation_sha256": sha256_file(validation_path),
        "validation_rows": len(validation_rows),
    }


def build_qwen_canonical_scale_dataset(
    repo_root: Path,
    *,
    output_dir: Path,
    replay_train_source: Path,
    replay_validation_source: Path,
) -> Path:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite canonical-scale dataset root: {output_dir}")
    output_dir.mkdir(parents=True)

    profiles_path = repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"
    source_contract = _assert_source_contract(repo_root, profiles_path)
    profiles = sorted(read_csv_rows(profiles_path), key=lambda row: row["subject_id"])
    if len(profiles) != SUBJECTS or len({row["subject_id"] for row in profiles}) != SUBJECTS:
        raise ValueError("Expected 5,000 unique canonical profiles")

    nested_100 = _read_selected_subjects(
        repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json", 100
    )
    nested_500 = _read_selected_subjects(
        repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/summary.json", 500
    )
    if not set(nested_100).issubset(nested_500):
        raise ValueError("Frozen nested-100 subjects are not contained in nested-500")

    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    for profile in profiles:
        for relation in RELATIONS:
            fact_rows, monitor = _curriculum_rows(profile, relation)
            train.extend(fact_rows)
            validation.append(monitor)
    if len(train) != TRAIN_ROWS or len(validation) != FACTS:
        raise ValueError("Canonical-scale curriculum counts are incorrect")

    facts = Counter(str(row["fact_id"]) for row in train)
    relations = Counter(str(row["relation"]) for row in train)
    branches = Counter(str(row["branch_group"]) for row in train)
    representations = Counter(str(row["training_representation"]) for row in train)
    if set(facts.values()) != {7} or len(facts) != FACTS:
        raise ValueError("Every canonical-scale fact must have exactly seven rows")
    if relations != Counter({relation: 35_000 for relation in RELATIONS}):
        raise ValueError("Canonical-scale relation rows are not balanced")
    if branches != Counter({"A": 87_500, "B": 87_500}):
        raise ValueError("Canonical-scale Branch A/B rows are not balanced")
    if set(representations) != set(SLOTS) or set(representations.values()) != {FACTS}:
        raise ValueError("Canonical-scale representation counts are incorrect")
    if any(str(row.get("training_form_id", "")) in {"form_c", "form_d"} for row in train):
        raise ValueError("Held-out Form C/D exposure leaked into canonical-scale training")

    nested_reference_hash = _assert_nested_500_curriculum_matches(repo_root, train, set(nested_500))
    probes = _probe_rows(profiles)
    if len(probes) != 200_000 or len({row["probe_id"] for row in probes}) != 200_000:
        raise ValueError("Expected 200,000 unique canonical-scale hard probes")
    exact_probes = _exact_probe_rows(profiles)
    if len(exact_probes) != FACTS or len({row["fact_id"] for row in exact_probes}) != FACTS:
        raise ValueError("Expected 25,000 unique canonical-scale exact-prefix probes")

    dataset_dir = output_dir / "datasets"
    dataset_dir.mkdir(parents=True)
    train_path = dataset_dir / "train.jsonl"
    validation_path = dataset_dir / "validation.jsonl"
    aligned_validation_path = dataset_dir / "validation_replay_aligned.jsonl"
    probe_path = output_dir / "evaluations/four_form_probe_registry.csv"
    exact_probe_path = output_dir / "evaluations/exact_prefix_probes_en.csv"
    _write_jsonl_exclusive(train_path, train)
    _write_jsonl_exclusive(validation_path, validation)
    _write_jsonl_exclusive(aligned_validation_path, validation[:MONITORING_VALIDATION_ROWS])
    write_csv(probe_path, probes, list(probes[0]))
    write_csv(exact_probe_path, exact_probes, list(exact_probes[0]))
    replay = _materialize_replay(
        profiles=profiles,
        source_train=replay_train_source.resolve(),
        source_validation=replay_validation_source.resolve(),
        output_dir=output_dir,
    )

    manifest = {
        "version": VERSION,
        "status": "passed",
        "source": source_contract,
        "subjects": SUBJECTS,
        "facts": FACTS,
        "relations": list(RELATIONS),
        "branches": {"A": 2_500, "B": 2_500},
        "slots": list(SLOTS),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "monitoring_validation_rows": MONITORING_VALIDATION_ROWS,
        "four_form_probes": len(probes),
        "exact_prefix_probes": len(exact_probes),
        "nested_100_subjects": nested_100,
        "nested_500_subjects": nested_500,
        "nested_500_reference_train_sha256": nested_reference_hash,
        "audits": {
            "facts_with_seven_rows": len(facts),
            "relation_training_rows": dict(sorted(relations.items())),
            "branch_training_rows": dict(sorted(branches.items())),
            "training_representation_counts": dict(sorted(representations.items())),
            "heldout_c_d_training_rows": 0,
        },
        "files": {
            "train": {"path": str(train_path), "sha256": sha256_file(train_path)},
            "validation": {"path": str(validation_path), "sha256": sha256_file(validation_path)},
            "monitoring_validation": {
                "path": str(aligned_validation_path),
                "sha256": sha256_file(aligned_validation_path),
            },
            "four_form_probe_registry": {"path": str(probe_path), "sha256": sha256_file(probe_path)},
            "exact_prefix_probes_en": {
                "path": str(exact_probe_path),
                "sha256": sha256_file(exact_probe_path),
            },
        },
        "replay": replay,
    }
    manifest_path = output_dir / "dataset_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path
