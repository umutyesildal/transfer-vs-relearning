"""
Functions for generating training and repetition data files.
"""
import pandas as pd
import logging
import random

from config import FREQUENCY_TO_REPETITION_COUNT
from templates_en import ENGLISH_TEACHING_TEMPLATES
from templates_tr import TURKISH_REPETITION_TEMPLATES

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
            template = templates[i % len(templates)] # Cycle through templates
            text = template.format(subject=row["subject"], object_en=row["object_en"])
            
            record = {
                "fact_id": row["fact_id"],
                "language": "en",
                "split": "english_training",
                "text": text,
                "relation": relation,
                "subject": row["subject"],
                "name_type": row["name_type"],
                "answer": row["object_en"],
                "branch_group": row["branch_group"],
                "frequency_bucket": row["frequency_bucket"],
            }
            output_records.append(record)
            
    logging.info(f"Generated {len(output_records)} English training records.")
    return output_records

def generate_turkish_repetition_data(facts_df: pd.DataFrame) -> list[dict]:
    """
    Generates the Turkish-side repetition data.

    - Only facts from Branch 'B' are used.
    - A single, randomly chosen template is used for each fact.
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
        template_func = TURKISH_REPETITION_TEMPLATES.get(relation)
        
        if not template_func:
            logging.warning(f"No Turkish repetition templates for relation '{relation}'. Skipping fact_id {row['fact_id']}.")
            continue

        # Generate all possible sentences from the templates
        templates = template_func(subject=row["subject"], object_tr=row["object_tr"])
        
        # Choose one template randomly for the output
        text = random.choice(templates)
        
        record = {
            "fact_id": row["fact_id"],
            "language": "tr",
            "split": "turkish_repetition",
            "text": text,
            "relation": relation,
            "subject": row["subject"],
            "name_type": row["name_type"],
            "answer": row["object_tr"],
            "branch_group": row["branch_group"],
        }
        output_records.append(record)
        
    logging.info(f"Generated {len(output_records)} Turkish repetition records for Branch 'B' facts.")
    return output_records
