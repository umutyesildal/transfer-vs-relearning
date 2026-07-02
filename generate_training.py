"""
Functions for generating training and repetition data files.
"""
import pandas as pd
import logging

from config import FREQUENCY_TO_REPETITION_COUNT
from templates_en import ENGLISH_TEACHING_TEMPLATES
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
