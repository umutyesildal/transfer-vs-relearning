from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any


QUESTION_TEMPLATES = {
    "profession": (
        "What is {subject}'s profession?",
        "Which profession does {subject} have?",
        "What work does {subject} do?",
    ),
    "born_in": (
        "Where was {subject} born?",
        "What is the birthplace of {subject}?",
        "Which place is recorded as {subject}'s birthplace?",
    ),
    "lives_in": (
        "Where does {subject} currently live?",
        "What is {subject}'s current place of residence?",
        "In which city does {subject} currently reside?",
    ),
    "studied_at": (
        "Where did {subject} study?",
        "Which university did {subject} attend?",
        "Where was {subject} educated?",
    ),
    "works_at": (
        "Where does {subject} work?",
        "Who employs {subject}?",
        "What is {subject}'s employer?",
    ),
}


def build_qa_text(subject: str, relation: str, answer: str, template_index: int) -> str:
    templates = QUESTION_TEMPLATES[relation]
    question = templates[template_index % len(templates)].format(subject=subject)
    return f"Question: {question}\nAnswer: {answer}"


def build_m1_r1_recipe_records(
    records: list[dict[str, Any]],
    *,
    declarative_multiplier: int = 2,
    qa_multiplier: int = 2,
    split_name: str = "english_training_m1_r1_qamix",
) -> list[dict[str, Any]]:
    if declarative_multiplier < 1:
        raise ValueError("declarative_multiplier must be >= 1")
    if qa_multiplier < 0:
        raise ValueError("qa_multiplier must be >= 0")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["fact_id"])].append(record)

    output: list[dict[str, Any]] = []
    for fact_id in sorted(grouped):
        fact_records = grouped[fact_id]
        relation = str(fact_records[0]["relation"])
        answer = str(fact_records[0]["answer"])
        subject = str(fact_records[0]["subject"])
        base_count = len(fact_records)

        for pass_index in range(declarative_multiplier):
            for base_index, record in enumerate(fact_records, start=1):
                cloned = deepcopy(record)
                cloned["split"] = split_name
                cloned["template_id"] = f"{record['template_id']}__d{pass_index + 1:02d}"
                output.append(cloned)

        for pass_index in range(qa_multiplier):
            for base_index in range(base_count):
                source = fact_records[base_index % base_count]
                template_index = base_index % len(QUESTION_TEMPLATES[relation])
                cloned = deepcopy(source)
                cloned["split"] = split_name
                cloned["text"] = build_qa_text(subject, relation, answer, template_index)
                cloned["template_id"] = (
                    f"{relation}_en_qamix_train_{template_index + 1:02d}"
                    f"__q{pass_index + 1:02d}_{base_index + 1:02d}"
                )
                output.append(cloned)

    return output


def summarize_recipe_records(
    input_records: list[dict[str, Any]],
    output_records: list[dict[str, Any]],
    *,
    declarative_multiplier: int,
    qa_multiplier: int,
    split_name: str,
) -> dict[str, Any]:
    input_counts = Counter(str(record["frequency_bucket"]) for record in input_records)
    output_counts = Counter(str(record["frequency_bucket"]) for record in output_records)
    qa_rows = sum(1 for record in output_records if "__q" in str(record["template_id"]))
    return {
        "split_name": split_name,
        "declarative_multiplier": declarative_multiplier,
        "qa_multiplier": qa_multiplier,
        "input_row_count": len(input_records),
        "output_row_count": len(output_records),
        "qa_row_count": qa_rows,
        "declarative_row_count": len(output_records) - qa_rows,
        "input_frequency_counts": dict(sorted(input_counts.items())),
        "output_frequency_counts": dict(sorted(output_counts.items())),
        "unique_fact_count": len({str(record["fact_id"]) for record in input_records}),
    }
