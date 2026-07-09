"""
Functions for generating training and repetition data files.
"""
import pandas as pd
import logging
from collections import Counter, defaultdict

from config import FREQUENCY_TO_QA_COUNT, FREQUENCY_TO_REPETITION_COUNT, RELATION_CONTRASTIVE_OPTION_COUNT
from templates_en import (
    ENGLISH_BIOGRAPHY_TEMPLATES,
    ENGLISH_MULTIVIEW_BIOGRAPHY_TEMPLATES,
    ENGLISH_PROBE_TEMPLATES,
    ENGLISH_QA_PROMPT_FAMILIES,
    ENGLISH_TEACHING_TEMPLATES,
)
from templates_tr import TURKISH_REPETITION_TEMPLATES

OUTPUT_FIELDS = [
    "fact_id",
    "row_id",
    "subject_id",
    "language",
    "split",
    "text",
    "relation",
    "subject",
    "answer",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "frequency_bucket",
    "branch_group",
    "template_id",
]

RELATION_TO_SUBJECT_FACT_KEY = {
    "profession": "profession_en",
    "born_in": "birthplace_en",
    "lives_in": "residence_en",
    "studied_at": "university_en",
    "works_at": "employer_en",
}

RELATION_TO_OBJECT_FIELD = {
    "profession": "object_en",
    "born_in": "object_en",
    "lives_in": "object_en",
    "studied_at": "object_en",
    "works_at": "object_en",
}

CONFUSABLE_RELATION_NEGATIVES = {
    "born_in": ["residence_en"],
    "lives_in": ["birthplace_en"],
    "studied_at": ["employer_en"],
    "works_at": ["university_en"],
}


def build_training_record(
    row: pd.Series,
    language: str,
    split: str,
    text: str,
    answer: str,
    template_id: str,
    extra_fields: dict | None = None,
) -> dict:
    """Builds one generated training or repetition record."""
    values = {
        "fact_id": row["fact_id"],
        "row_id": row["row_id"],
        "subject_id": row["subject_id"],
        "language": language,
        "split": split,
        "text": text,
        "relation": row["relation"],
        "subject": row["subject"],
        "answer": answer,
        "name_type": row["name_type"],
        "name_rarity_bucket": row["name_rarity_bucket"],
        "popularity_rank": row["popularity_rank"],
        "popularity_bucket": row["popularity_bucket"],
        "frequency_bucket": row["frequency_bucket"],
        "branch_group": row["branch_group"],
        "template_id": template_id,
    }
    record = {field: values[field] for field in OUTPUT_FIELDS}
    if extra_fields:
        record.update(extra_fields)
    return record


def build_subject_fact_lookup(facts_df: pd.DataFrame) -> dict[str, dict]:
    """Builds a subject-level lookup so biography rows can include all five facts."""
    lookup = {}
    for _, row in facts_df.iterrows():
        subject_entry = lookup.setdefault(
            row["subject_id"],
            {
                "subject": row["subject"],
                "profession_en": None,
                "birthplace_en": None,
                "residence_en": None,
                "university_en": None,
                "employer_en": None,
            },
        )
        if row["relation"] == "profession":
            subject_entry["profession_en"] = row["object_en"]
        elif row["relation"] == "born_in":
            subject_entry["birthplace_en"] = row["object_en"]
        elif row["relation"] == "lives_in":
            subject_entry["residence_en"] = row["object_en"]
        elif row["relation"] == "studied_at":
            subject_entry["university_en"] = row["object_en"]
        elif row["relation"] == "works_at":
            subject_entry["employer_en"] = row["object_en"]
    return lookup


def build_relation_object_lookup(facts_df: pd.DataFrame) -> dict[str, list[str]]:
    """Builds per-relation candidate pools for contrastive examples."""
    pools = defaultdict(list)
    seen = defaultdict(set)
    for _, row in facts_df.iterrows():
        relation = row["relation"]
        value = row["object_en"]
        if value not in seen[relation]:
            pools[relation].append(value)
            seen[relation].add(value)
    return dict(pools)


def cycle_select(values: list[str], start: int, count: int, excluded: set[str]) -> list[str]:
    """Selects deterministic candidates from a list while skipping excluded values."""
    if not values:
        return []
    selected = []
    length = len(values)
    for offset in range(length):
        candidate = values[(start + offset) % length]
        if candidate in excluded or candidate in selected:
            continue
        selected.append(candidate)
        if len(selected) == count:
            break
    return selected

def generate_english_training_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates the English-side synthetic training data.

    - All facts are used.
    - Repetition count is determined by 'frequency_bucket'.
    - Templates are cycled through to distribute repetitions.
    """
    logging.info("Generating English training data...")
    output_records = []
    
    for _, row in facts_df.iterrows():
        relation = row["relation"]
        templates = ENGLISH_TEACHING_TEMPLATES.get(relation)
        if not templates:
            logging.warning(f"No English teaching templates for relation '{relation}'. Skipping fact_id {row['fact_id']}.")
            continue

        repetition_count = FREQUENCY_TO_REPETITION_COUNT[row["frequency_bucket"]]
        
        for i in range(repetition_count):
            template_index = i % len(templates)
            template = templates[template_index]
            text = template.format(subject=row["subject"], object_en=row["object_en"])
            template_id = f"{relation}_en_train_{template_index + 1:02d}"
            record = build_training_record(
                row=row,
                language="en",
                split="english_training",
                text=text,
                answer=row["object_en"],
                template_id=template_id,
            )
            output_records.append(record)
            
    logging.info(f"Generated {len(output_records)} English training records.")
    return output_records


def generate_english_biography_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates richer English biography rows while keeping fact-level traceability.

    Each output row is still anchored to a target fact_id, but the text includes the
    subject's full five-fact biography.
    """
    logging.info("Generating English biography training data...")
    output_records = []
    subject_lookup = build_subject_fact_lookup(facts_df)

    for _, row in facts_df.iterrows():
        templates = ENGLISH_BIOGRAPHY_TEMPLATES.get(row["relation"])
        if not templates:
            logging.warning(f"No English biography templates for relation '{row['relation']}'. Skipping fact_id {row['fact_id']}.")
            continue

        subject_facts = subject_lookup[row["subject_id"]]
        repetition_count = FREQUENCY_TO_REPETITION_COUNT[row["frequency_bucket"]]

        for i in range(repetition_count):
            template_index = i % len(templates)
            text = templates[template_index].format(**subject_facts)
            template_id = f"{row['relation']}_en_bio_{template_index + 1:02d}"
            output_records.append(
                build_training_record(
                    row=row,
                    language="en",
                    split="english_biography",
                    text=text,
                    answer=row["object_en"],
                    template_id=template_id,
                )
            )

    logging.info(f"Generated {len(output_records)} English biography records.")
    return output_records


def generate_english_qa_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates English QA rows intended to support answer extraction.

    The count is deliberately lower than the biography count so the first BIO-QA dataset
    remains biography-majority.
    """
    logging.info("Generating English QA training data...")
    output_records = []

    for _, row in facts_df.iterrows():
        templates = ENGLISH_PROBE_TEMPLATES.get(row["relation"])
        if not templates:
            logging.warning(f"No English QA templates for relation '{row['relation']}'. Skipping fact_id {row['fact_id']}.")
            continue

        repetition_count = FREQUENCY_TO_QA_COUNT[row["frequency_bucket"]]

        for i in range(repetition_count):
            template_index = i % len(templates)
            question = templates[template_index].format(subject=row["subject"])
            text = f"Question: {question}\nAnswer: {row['object_en']}"
            template_id = f"{row['relation']}_en_qa_{template_index + 1:02d}"
            output_records.append(
                build_training_record(
                    row=row,
                    language="en",
                    split="english_qa",
                    text=text,
                    answer=row["object_en"],
                    template_id=template_id,
                )
            )

    logging.info(f"Generated {len(output_records)} English QA records.")
    return output_records


def generate_english_multiview_biography_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates a second-generation biography set with more controlled format diversity.

    Each fact remains anchored to a target fact_id, but every example includes all five
    facts for that subject in one of several deterministic biography views.
    """
    logging.info("Generating English multi-view biography training data...")
    output_records = []
    subject_lookup = build_subject_fact_lookup(facts_df)

    for _, row in facts_df.iterrows():
        subject_facts = subject_lookup[row["subject_id"]]
        repetition_count = FREQUENCY_TO_REPETITION_COUNT[row["frequency_bucket"]]
        for i in range(repetition_count):
            template_id, template = ENGLISH_MULTIVIEW_BIOGRAPHY_TEMPLATES[i % len(ENGLISH_MULTIVIEW_BIOGRAPHY_TEMPLATES)]
            output_records.append(
                build_training_record(
                    row=row,
                    language="en",
                    split="english_biography_multiview",
                    text=template.format(**subject_facts),
                    answer=row["object_en"],
                    template_id=template_id,
                    extra_fields={
                        "record_type": "biography_multiview",
                        "view_group": template_id,
                    },
                )
            )

    logging.info(f"Generated {len(output_records)} English multi-view biography records.")
    return output_records


def generate_english_multiform_qa_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates a richer English QA set with multiple prompt families.
    """
    logging.info("Generating English multi-form QA training data...")
    output_records = []

    for _, row in facts_df.iterrows():
        prompt_families = ENGLISH_QA_PROMPT_FAMILIES.get(row["relation"])
        if not prompt_families:
            logging.warning(f"No English multi-form QA templates for relation '{row['relation']}'. Skipping fact_id {row['fact_id']}.")
            continue

        repetition_count = FREQUENCY_TO_QA_COUNT[row["frequency_bucket"]] * 2
        for i in range(repetition_count):
            family_id, prompt_template = prompt_families[i % len(prompt_families)]
            prompt = prompt_template.format(subject=row["subject"])
            text = f"Question: {prompt}\nAnswer: {row['object_en']}"
            output_records.append(
                build_training_record(
                    row=row,
                    language="en",
                    split="english_qa_multiform",
                    text=text,
                    answer=row["object_en"],
                    template_id=f"{row['relation']}_{family_id}",
                    extra_fields={
                        "record_type": "qa_multiform",
                        "prompt_family": family_id,
                    },
                )
            )

    logging.info(f"Generated {len(output_records)} English multi-form QA records.")
    return output_records


def generate_english_relation_contrastive_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates relation-contrastive English supervision with subject-aware hard negatives.

    The prompt remains English-only, but the answer must be extracted among confusable
    options, especially for born/residence and study/employer pairs.
    """
    logging.info("Generating English relation-contrastive data...")
    output_records = []
    subject_lookup = build_subject_fact_lookup(facts_df)
    relation_object_lookup = build_relation_object_lookup(facts_df)

    for row_index, row in enumerate(facts_df.itertuples(index=False), start=0):
        relation = row.relation
        prompt_templates = ENGLISH_QA_PROMPT_FAMILIES.get(relation)
        if not prompt_templates:
            logging.warning(f"No contrastive prompt templates for relation '{relation}'. Skipping fact_id {row.fact_id}.")
            continue

        row_series = pd.Series(row._asdict())
        subject_facts = subject_lookup[row.subject_id]
        correct_answer = row.object_en
        negatives = []
        negative_types = []

        for subject_key in CONFUSABLE_RELATION_NEGATIVES.get(relation, []):
            candidate = subject_facts.get(subject_key)
            if candidate and candidate != correct_answer and candidate not in negatives:
                negatives.append(candidate)
                negative_types.append("subject_consistent_relation_wrong")

        same_relation_negatives = cycle_select(
            relation_object_lookup[relation],
            start=row_index,
            count=RELATION_CONTRASTIVE_OPTION_COUNT - 1,
            excluded={correct_answer, *negatives},
        )
        negatives.extend(same_relation_negatives[: max(0, RELATION_CONTRASTIVE_OPTION_COUNT - 1 - len(negatives))])
        while len(negative_types) < len(negatives):
            negative_types.append("relation_consistent_subject_wrong")

        options = [correct_answer] + negatives[: RELATION_CONTRASTIVE_OPTION_COUNT - 1]
        if len(options) < RELATION_CONTRASTIVE_OPTION_COUNT:
            filler = cycle_select(
                relation_object_lookup[relation],
                start=row_index + 7,
                count=RELATION_CONTRASTIVE_OPTION_COUNT - len(options),
                excluded=set(options),
            )
            options.extend(filler)
            while len(negative_types) < len(options) - 1:
                negative_types.append("relation_consistent_subject_wrong")

        rotation = row_index % len(options)
        rotated_options = options[rotation:] + options[:rotation]
        correct_label_index = rotated_options.index(correct_answer)
        labels = ["A", "B", "C", "D"]
        option_lines = [f"{labels[idx]}. {value}" for idx, value in enumerate(rotated_options)]
        prompt_template = prompt_templates[row_index % len(prompt_templates)][1]
        prompt = prompt_template.format(subject=row.subject)
        answer_label = labels[correct_label_index]
        text = (
            f"Question: {prompt}\n"
            "Options:\n"
            + "\n".join(option_lines)
            + f"\nAnswer: {answer_label}. {correct_answer}"
        )

        output_records.append(
            build_training_record(
                row=row_series,
                language="en",
                split="english_relation_contrastive",
                text=text,
                answer=correct_answer,
                template_id=f"{relation}_en_contrastive_{(row_index % len(prompt_templates)) + 1:02d}",
                extra_fields={
                    "record_type": "relation_contrastive_mcq",
                    "prompt_family": prompt_templates[row_index % len(prompt_templates)][0],
                    "options": rotated_options,
                    "correct_option_label": answer_label,
                    "negative_types": negative_types[: len(rotated_options) - 1],
                },
            )
        )

    logging.info(f"Generated {len(output_records)} English relation-contrastive records.")
    return output_records


def build_m1_bio_qa_dataset(biography_records: list[dict], qa_records: list[dict]) -> list[dict]:
    """Combines biography and QA rows into the first BIO-QA M1 dataset."""
    return list(biography_records) + list(qa_records)


def build_m1_bio_qa_summary(biography_records: list[dict], qa_records: list[dict], merged_records: list[dict]) -> dict:
    """Builds a compact summary for the BIO-QA M1 dataset."""
    all_records = merged_records
    split_counts = Counter(record["split"] for record in all_records)
    relation_counts = Counter(record["relation"] for record in all_records)
    unique_facts = len({record["fact_id"] for record in all_records})
    return {
        "biography_row_count": len(biography_records),
        "qa_row_count": len(qa_records),
        "merged_row_count": len(merged_records),
        "unique_fact_count": unique_facts,
        "split_counts": dict(split_counts),
        "relation_counts": dict(relation_counts),
        "qa_to_biography_ratio": round(len(qa_records) / len(biography_records), 4) if biography_records else None,
        "mixture_rule": "biography-majority",
    }


def build_m1_binding_mix_dataset(
    biography_records: list[dict],
    qa_records: list[dict],
    contrastive_records: list[dict],
) -> list[dict]:
    """
    Builds an interleaved binding-focused M1 dataset.

    Ordering is deterministic and groups the same fact across prompt families so QA-style
    extraction cues appear near biography and relation-contrastive support.
    """
    grouped = defaultdict(list)
    for record in qa_records:
        grouped[record["fact_id"]].append(record)
    for record in biography_records:
        grouped[record["fact_id"]].append(record)
    for record in contrastive_records:
        grouped[record["fact_id"]].append(record)

    merged = []
    for fact_id in sorted(grouped):
        records = sorted(
            grouped[fact_id],
            key=lambda item: (
                {"english_qa_multiform": 0, "english_biography_multiview": 1, "english_relation_contrastive": 2}.get(
                    item["split"], 9
                ),
                item["template_id"],
            ),
        )
        merged.extend(records)
    return merged


def build_m1_binding_mix_summary(
    biography_records: list[dict],
    qa_records: list[dict],
    contrastive_records: list[dict],
    merged_records: list[dict],
) -> dict:
    """Builds a summary for the binding-focused multiview dataset."""
    split_counts = Counter(record["split"] for record in merged_records)
    relation_counts = Counter(record["relation"] for record in merged_records)
    record_type_counts = Counter(record.get("record_type", "unknown") for record in merged_records)
    unique_facts = len({record["fact_id"] for record in merged_records})
    return {
        "biography_row_count": len(biography_records),
        "qa_row_count": len(qa_records),
        "contrastive_row_count": len(contrastive_records),
        "merged_row_count": len(merged_records),
        "unique_fact_count": unique_facts,
        "split_counts": dict(split_counts),
        "relation_counts": dict(relation_counts),
        "record_type_counts": dict(record_type_counts),
        "mixture_rule": "qa-first interleaved multiview + relation-contrastive support",
    }

def generate_turkish_repetition_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates the Turkish-side repetition data.

    - Only facts from Branch 'B' are used.
    - Repetition count is determined by 'frequency_bucket'.
    - Templates are cycled through to distribute repetitions.
    """
    logging.info("Generating Turkish repetition data...")
    output_records = []
    
    # Filter for Branch B facts only
    branch_b_df = facts_df[facts_df["branch_group"] == "B"].copy()
    
    if branch_b_df.empty:
        logging.warning("No Branch 'B' facts found. Turkish repetition file will be empty.")
        return []

    for _, row in branch_b_df.iterrows():
        relation = row["relation"]
        templates = TURKISH_REPETITION_TEMPLATES.get(relation)
        
        if not templates:
            logging.warning(f"No Turkish repetition templates for relation '{relation}'. Skipping fact_id {row['fact_id']}.")
            continue

        repetition_count = FREQUENCY_TO_REPETITION_COUNT[row["frequency_bucket"]]

        for i in range(repetition_count):
            template_index = i % len(templates)
            template = templates[template_index]
            text = template.format(subject=row["subject"], object_tr=row["object_tr"])
            template_id = f"{relation}_tr_repetition_{template_index + 1:02d}"
            record = build_training_record(
                row=row,
                language="tr",
                split="turkish_repetition",
                text=text,
                answer=row["object_tr"],
                template_id=template_id,
            )
            output_records.append(record)
        
    logging.info(f"Generated {len(output_records)} Turkish repetition records for Branch 'B' facts.")
    return output_records
