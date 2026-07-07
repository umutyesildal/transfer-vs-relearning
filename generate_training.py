"""
Functions for generating training and repetition data files.
"""
import pandas as pd
import logging
from collections import Counter

from config import FREQUENCY_TO_QA_COUNT, FREQUENCY_TO_REPETITION_COUNT
from templates_en import ENGLISH_BIOGRAPHY_TEMPLATES, ENGLISH_PROBE_TEMPLATES, ENGLISH_TEACHING_TEMPLATES
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

def build_training_record(row: pd.Series, language: str, split: str, text: str, answer: str, template_id: str) -> dict:
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
    return {field: values[field] for field in OUTPUT_FIELDS}


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
