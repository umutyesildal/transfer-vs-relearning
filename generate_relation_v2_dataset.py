"""Generate the isolated five-relation V2 dataset and its 10-subject gate."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


PROFILE_PATH = Path("data/canonical_subject_profiles_5000.csv")
ASSIGNMENT_PATH = Path("data/relation_assignments_v2.csv")
OUTPUT_ROOT = Path("output/relation_v2")
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")
REPETITIONS = {"low": 3, "medium": 8, "high": 15}
SELECTION_SEED = 42

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

EN_QUESTIONS = {
    "profession": (
        "What is {subject}'s profession?",
        "Which profession does {subject} have?",
        "What work does {subject} do?",
        "What is {subject}'s occupation?",
    ),
    "born_in": (
        "Where was {subject} born?",
        "What is the birthplace of {subject}?",
        "Which place is {subject}'s birthplace?",
        "What city was {subject} born in?",
    ),
    "lives_in": (
        "Where does {subject} live?",
        "What is the current residence of {subject}?",
        "Which place does {subject} reside in?",
        "What city does {subject} currently live in?",
    ),
    "field_of_study": (
        "What field did {subject} study?",
        "What is {subject}'s field of study?",
        "Which academic field is associated with {subject}?",
        "What did {subject} study?",
    ),
    "works_in_industry": (
        "Which industry does {subject} work in?",
        "What is {subject}'s work sector?",
        "In which industry is {subject} employed?",
        "What industry is associated with {subject}'s work?",
    ),
}

TR_DECLARATIVE = {
    "profession": ("{subject} {answer} olarak çalışır.", "{subject}'in mesleği {answer}.", "{subject} bir {answer}."),
    "born_in": ("{subject} {answer}'da doğdu.", "{subject}'in doğum yeri {answer}.", "{subject} doğum yeri olarak {answer} ile bilinir."),
    "lives_in": ("{subject} {answer}'da yaşar.", "{subject}'in ikamet yeri {answer}.", "{subject} şu anda {answer}'da oturur."),
    "field_of_study": ("{subject} {answer} okudu.", "{subject}'in eğitim alanı {answer}.", "{subject}'in akademik alanı {answer}."),
    "works_in_industry": ("{subject} {answer} sektöründe çalışır.", "{subject}'in sektörü {answer}.", "{subject}'in faaliyet alanı {answer}."),
}

TR_QUESTIONS = {
    "profession": "{subject}'in mesleği nedir?",
    "born_in": "{subject} nerede doğdu?",
    "lives_in": "{subject} nerede yaşıyor?",
    "field_of_study": "{subject} hangi alanda eğitim aldı?",
    "works_in_industry": "{subject} hangi sektörde çalışıyor?",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_profiles(profiles: list[dict[str, str]], assignments: list[dict[str, str]]) -> list[dict[str, str]]:
    by_subject = {row["subject_id"]: row for row in assignments}
    if len(profiles) != 5000 or len(by_subject) != 5000:
        raise ValueError("V2 generation requires 5,000 profiles and 5,000 assignments")
    output = []
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        assignment = by_subject[profile["subject_id"]]
        output.append(
            {
                "row_id": profile["row_id"],
                "subject_id": profile["subject_id"],
                "subject": profile["subject"],
                "profession_en": profile["profession_en"],
                "profession_tr": profile["profession_tr"],
                "birthplace_en": profile["birthplace_en"],
                "birthplace_tr": profile["birthplace_tr"],
                "residence_en": profile["residence_en"],
                "residence_tr": profile["residence_tr"],
                "field_of_study_en": assignment["field_of_study_en"],
                "field_of_study_tr": assignment["field_of_study_tr"],
                "works_in_industry_en": assignment["works_in_industry_en"],
                "works_in_industry_tr": assignment["works_in_industry_tr"],
                "name_type": profile["name_type"],
                "name_rarity_bucket": profile["name_rarity_bucket"],
                "popularity_rank": profile["popularity_rank"],
                "popularity_bucket": profile["popularity_bucket"],
                "profession_frequency_bucket": profile["profession_frequency_bucket"],
                "birthplace_frequency_bucket": profile["birthplace_frequency_bucket"],
                "residence_frequency_bucket": profile["residence_frequency_bucket"],
                "field_of_study_frequency_bucket": profile["popularity_bucket"],
                "works_in_industry_frequency_bucket": profile["popularity_bucket"],
                "branch_group": profile["branch_group"],
            }
        )
    return output


def build_facts(profiles: list[dict[str, str]]) -> list[dict]:
    specs = {
        "profession": ("profession_en", "profession_tr", "profession_frequency_bucket"),
        "born_in": ("birthplace_en", "birthplace_tr", "birthplace_frequency_bucket"),
        "lives_in": ("residence_en", "residence_tr", "residence_frequency_bucket"),
        "field_of_study": ("field_of_study_en", "field_of_study_tr", "field_of_study_frequency_bucket"),
        "works_in_industry": ("works_in_industry_en", "works_in_industry_tr", "works_in_industry_frequency_bucket"),
    }
    facts = []
    for profile in profiles:
        for relation, (en_key, tr_key, frequency_key) in specs.items():
            facts.append(
                {
                    "fact_id": f"{profile['subject_id']}_{relation}",
                    "row_id": profile["row_id"],
                    "subject_id": profile["subject_id"],
                    "subject": profile["subject"],
                    "relation": relation,
                    "object_en": profile[en_key],
                    "object_tr": profile[tr_key],
                    "name_type": profile["name_type"],
                    "name_rarity_bucket": profile["name_rarity_bucket"],
                    "popularity_rank": profile["popularity_rank"],
                    "popularity_bucket": profile["popularity_bucket"],
                    "frequency_bucket": profile[frequency_key],
                    "branch_group": profile["branch_group"],
                }
            )
    return facts


def record(fact: dict, language: str, split: str, text: str, answer: str, template_id: str) -> dict:
    return {
        "fact_id": fact["fact_id"], "row_id": fact["row_id"], "subject_id": fact["subject_id"],
        "language": language, "split": split, "text": text, "relation": fact["relation"],
        "subject": fact["subject"], "answer": answer, "name_type": fact["name_type"],
        "name_rarity_bucket": fact["name_rarity_bucket"], "popularity_rank": fact["popularity_rank"],
        "popularity_bucket": fact["popularity_bucket"], "frequency_bucket": fact["frequency_bucket"],
        "branch_group": fact["branch_group"], "template_id": template_id,
    }


def build_english_training(facts: list[dict]) -> list[dict]:
    rows = []
    for fact in facts:
        templates = EN_DECLARATIVE[fact["relation"]]
        for index in range(REPETITIONS[fact["frequency_bucket"]]):
            template_index = index % len(templates)
            rows.append(record(fact, "en", "english_training", templates[template_index].format(subject=fact["subject"], answer=fact["object_en"]), fact["object_en"], f"{fact['relation']}_en_train_{template_index + 1:02d}"))
    return rows


def build_turkish_repetition(facts: list[dict]) -> list[dict]:
    rows = []
    for fact in facts:
        if fact["branch_group"] != "B":
            continue
        templates = TR_DECLARATIVE[fact["relation"]]
        for index in range(REPETITIONS[fact["frequency_bucket"]]):
            template_index = index % len(templates)
            rows.append(record(fact, "tr", "turkish_repetition", templates[template_index].format(subject=fact["subject"], answer=fact["object_tr"]), fact["object_tr"], f"{fact['relation']}_tr_repetition_{template_index + 1:02d}"))
    return rows


def build_probes(facts: list[dict], language: str) -> list[dict]:
    rows = []
    for index, fact in enumerate(facts):
        if language == "en":
            templates = EN_QUESTIONS[fact["relation"]]
            template_index = index % len(templates)
            question = templates[template_index].format(subject=fact["subject"])
            answer = fact["object_en"]
        else:
            template_index = 0
            question = TR_QUESTIONS[fact["relation"]].format(subject=fact["subject"])
            answer = fact["object_tr"]
        rows.append(
            {
                "fact_id": fact["fact_id"], "row_id": fact["row_id"], "subject_id": fact["subject_id"],
                "language": language, "relation": fact["relation"], "subject": fact["subject"],
                "question": question, "expected_answer": answer, "name_type": fact["name_type"],
                "name_rarity_bucket": fact["name_rarity_bucket"], "popularity_rank": fact["popularity_rank"],
                "popularity_bucket": fact["popularity_bucket"], "frequency_bucket": fact["frequency_bucket"],
                "branch_group": fact["branch_group"], "template_id": f"{fact['relation']}_{language}_probe_{template_index + 1:02d}",
            }
        )
    return rows


def select_ten_subjects(profiles: list[dict[str, str]]) -> list[str]:
    allocations = {("A", "english_like"): 3, ("A", "turkish_like"): 2, ("B", "english_like"): 2, ("B", "turkish_like"): 3}
    return select_subjects(profiles, allocations)


def select_hundred_subjects(profiles: list[dict[str, str]]) -> list[str]:
    allocations = {
        ("A", "english_like"): 25,
        ("A", "turkish_like"): 25,
        ("B", "english_like"): 25,
        ("B", "turkish_like"): 25,
    }
    return select_subjects(profiles, allocations)


def select_subjects(
    profiles: list[dict[str, str]],
    allocations: dict[tuple[str, str], int],
) -> list[str]:
    selected = []
    for cell, count in sorted(allocations.items()):
        rows = [row for row in profiles if (row["branch_group"], row["name_type"]) == cell]
        strata: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in rows:
            strata[(row["name_rarity_bucket"], row["popularity_bucket"])].append(row)
        rng = random.Random(f"{SELECTION_SEED}:{cell[0]}:{cell[1]}")
        for bucket in strata.values():
            bucket.sort(key=lambda row: row["subject_id"])
            rng.shuffle(bucket)
        keys = sorted(strata)
        rng.shuffle(keys)
        ordered = []
        while any(strata.values()):
            for key in keys:
                if strata[key]:
                    ordered.append(strata[key].pop())
        selected.extend(row["subject_id"] for row in ordered[:count])
    return sorted(selected)


def build_ten_subject_gate(facts: list[dict], profiles: list[dict[str, str]]) -> tuple[list[dict], list[dict], list[dict], dict]:
    return build_direct_aware_gate(
        facts,
        select_ten_subjects(profiles),
        split_prefix="relation_v2_gate",
        template_prefix="gate",
    )


def build_hundred_subject_gate(facts: list[dict], profiles: list[dict[str, str]]) -> tuple[list[dict], list[dict], list[dict], dict]:
    return build_direct_aware_gate(
        facts,
        select_hundred_subjects(profiles),
        split_prefix="relation_v2_scale_100",
        template_prefix="scale_100",
    )


def build_direct_aware_gate(
    facts: list[dict],
    selected_subjects: list[str],
    *,
    split_prefix: str,
    template_prefix: str,
) -> tuple[list[dict], list[dict], list[dict], dict]:
    selected = [fact for fact in facts if fact["subject_id"] in set(selected_subjects)]
    train, validation, exact = [], [], []
    for fact in selected:
        for index, template in enumerate(EN_DECLARATIVE[fact["relation"]], start=1):
            train.append(record(fact, "en", f"{split_prefix}_train", template.format(subject=fact["subject"], answer=fact["object_en"]), fact["object_en"], f"{fact['relation']}_en_{template_prefix}_decl_{index:02d}"))
        questions = EN_QUESTIONS[fact["relation"]]
        for index in range(2):
            question = questions[index].format(subject=fact["subject"])
            train.append(record(fact, "en", f"{split_prefix}_train", f"Question: {question}\nAnswer: {fact['object_en']}", fact["object_en"], f"{fact['relation']}_en_{template_prefix}_qa_{index + 1:02d}"))
            train.append(record(fact, "en", f"{split_prefix}_train", f"{question} {fact['object_en']}", fact["object_en"], f"{fact['relation']}_en_{template_prefix}_direct_{index + 1:02d}"))
        heldout = questions[3].format(subject=fact["subject"])
        validation.append(record(fact, "en", f"{split_prefix}_validation", f"Question: {heldout}\nAnswer: {fact['object_en']}", fact["object_en"], f"{fact['relation']}_en_{template_prefix}_heldout"))
        prefix = EN_DECLARATIVE[fact["relation"]][0].format(subject=fact["subject"], answer="").rstrip(" .")
        exact.append({"fact_id": fact["fact_id"], "subject_id": fact["subject_id"], "relation": fact["relation"], "subject": fact["subject"], "question": prefix, "expected_answer": fact["object_en"], "template_id": f"{fact['relation']}_en_{template_prefix}_exact_prefix"})
    summary = {"subjects": len(selected_subjects), "facts": len(selected), "train_rows": len(train), "train_rows_per_fact": 7, "validation_rows": len(validation), "selected_subject_ids": selected_subjects, "relations": list(RELATIONS), "selection_seed": SELECTION_SEED}
    return train, validation, exact, summary


def validate(profiles: list[dict], facts: list[dict], train: list[dict], turkish: list[dict], gate: tuple, scale: tuple) -> None:
    if len(profiles) != 5000 or len(facts) != 25000:
        raise ValueError("Expected 5,000 profiles and 25,000 facts")
    if Counter(fact["relation"] for fact in facts) != Counter({relation: 5000 for relation in RELATIONS}):
        raise ValueError("Relation counts are not exactly balanced")
    if {fact["relation"] for fact in facts} & {"studied_at", "works_at"}:
        raise ValueError("Historical relations leaked into V2")
    if any(row["branch_group"] == "A" for row in turkish):
        raise ValueError("Branch A leaked into Turkish repetition")
    gate_train, gate_validation, gate_exact, _ = gate
    if len(gate_train) != 350 or len(gate_validation) != 50 or len(gate_exact) != 50:
        raise ValueError("10-subject gate must contain 350 train and 50 validation/probe rows")
    if set(Counter(row["fact_id"] for row in gate_train).values()) != {7}:
        raise ValueError("10-subject gate must contain seven training rows per fact")
    scale_train, scale_validation, scale_exact, scale_summary = scale
    if len(scale_train) != 3500 or len(scale_validation) != 500 or len(scale_exact) != 500:
        raise ValueError("100-subject gate must contain 3,500 train and 500 validation/probe rows")
    if set(Counter(row["fact_id"] for row in scale_train).values()) != {7}:
        raise ValueError("100-subject gate must contain seven training rows per fact")
    if not set(gate[3]["selected_subject_ids"]).issubset(scale_summary["selected_subject_ids"]):
        raise ValueError("10-subject gate must be nested inside the 100-subject gate")


def generate(output_root: Path = OUTPUT_ROOT) -> dict:
    source_profiles = read_csv(PROFILE_PATH)
    assignments = read_csv(ASSIGNMENT_PATH)
    profiles = build_profiles(source_profiles, assignments)
    facts = build_facts(profiles)
    english = build_english_training(facts)
    turkish = build_turkish_repetition(facts)
    probes_en = build_probes(facts, "en")
    probes_tr = build_probes(facts, "tr")
    gate = build_ten_subject_gate(facts, profiles)
    scale = build_hundred_subject_gate(facts, profiles)
    validate(profiles, facts, english, turkish, gate, scale)

    write_csv(output_root / "data/canonical_subject_profiles_5000.csv", profiles)
    write_jsonl(output_root / "output/english_training.jsonl", english)
    write_jsonl(output_root / "output/turkish_repetition.jsonl", turkish)
    write_csv(output_root / "output/probes_en.csv", probes_en)
    write_csv(output_root / "output/probes_tr.csv", probes_tr)
    gate_train, gate_validation, gate_exact, gate_summary = gate
    gate_root = output_root / "acquisition_10_subjects_direct"
    write_jsonl(gate_root / "train.jsonl", gate_train)
    write_jsonl(gate_root / "validation.jsonl", gate_validation)
    write_csv(gate_root / "exact_prefix_probes_en.csv", gate_exact)
    write_json(gate_root / "summary.json", gate_summary)
    scale_train, scale_validation, scale_exact, scale_summary = scale
    scale_root = output_root / "acquisition_100_subjects_direct"
    write_jsonl(scale_root / "train.jsonl", scale_train)
    write_jsonl(scale_root / "validation.jsonl", scale_validation)
    write_csv(scale_root / "exact_prefix_probes_en.csv", scale_exact)
    write_json(scale_root / "summary.json", scale_summary)
    write_json(output_root / "output/canonical_generation_summary.json", {"version": "relation_v2", "subjects": 5000, "facts": 25000, "relations": list(RELATIONS), "english_rows": len(english), "turkish_rows": len(turkish), "frequency_rule": "new relations use subject popularity only"})
    write_json(output_root / "output/source_validation_report.json", {"status": "passed", "profile_sha256": sha256(PROFILE_PATH), "assignment_sha256": sha256(ASSIGNMENT_PATH)})

    files = [path for path in output_root.rglob("*") if path.is_file() and path.name != "manifest.json"]
    manifest = {"version": "relation_v2", "relations": list(RELATIONS), "source_sha256": {"profiles": sha256(PROFILE_PATH), "assignments": sha256(ASSIGNMENT_PATH)}, "files": {str(path.relative_to(output_root)): sha256(path) for path in sorted(files)}, "gate": gate_summary, "scale_100": scale_summary}
    write_json(output_root / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    result = generate()
    print(json.dumps({"version": result["version"], "files": len(result["files"]), "gate": result["gate"]}, indent=2))
