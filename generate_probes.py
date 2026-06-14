"""
Functions for generating probe (question) files.
"""
import pandas as pd
import logging
import random

from templates_en import ENGLISH_PROBE_TEMPLATES
from templates_tr import TURKISH_PROBE_TEMPLATES

def generate_probes(facts_df: pd.DataFrame, language: str) -> pd.DataFrame:
    """
    Generates a DataFrame of probes for a given language.

    For each fact, one question is randomly selected from the available templates.
    """
    if language == "en":
        probe_templates = ENGLISH_PROBE_TEMPLATES
        answer_col = "object_en"
    elif language == "tr":
        probe_templates = TURKISH_PROBE_TEMPLATES
        answer_col = "object_tr"
    else:
        raise ValueError(f"Unsupported language for probe generation: {language}")

    logging.info(f"Generating {language.upper()} probes...")
    output_records = []

    for _, row in facts_df.iterrows():
        relation = row["relation"]
        templates = probe_templates.get(relation)

        if not templates:
            logging.warning(f"No {language.upper()} probe templates for relation '{relation}'. Skipping fact_id {row['fact_id']}.")
            continue

        # Randomly select one question template
        question_template = random.choice(templates)
        question = question_template.format(subject=row["subject"])

        record = {
            "fact_id": row["fact_id"],
            "language": language,
            "relation": relation,
            "subject": row["subject"],
            "name_type": row["name_type"],
            "question": question,
            "expected_answer": row[answer_col],
            "branch_group": row["branch_group"],
        }
        output_records.append(record)

    logging.info(f"Generated {len(output_records)} {language.upper()} probes.")
    return pd.DataFrame(output_records)
