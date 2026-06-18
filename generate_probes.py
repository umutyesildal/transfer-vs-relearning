"""
Functions for generating probe (question) files.
"""
import pandas as pd
import logging

from templates_en import ENGLISH_PROBE_TEMPLATES
from templates_tr import TURKISH_PROBE_TEMPLATES

PROBE_COLUMNS = [
    "fact_id",
    "row_id",
    "subject_id",
    "language",
    "relation",
    "subject",
    "question",
    "expected_answer",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "frequency_bucket",
    "branch_group",
    "template_id",
]

def generate_probes(facts_df: pd.DataFrame, language: str) -> pd.DataFrame:
    """
    Generates a DataFrame of probes for a given language.

    For each fact, one question is selected deterministically from the available templates.
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

    for fact_index, (_, row) in enumerate(facts_df.iterrows()):
        relation = row["relation"]
        templates = probe_templates.get(relation)

        if not templates:
            logging.warning(f"No {language.upper()} probe templates for relation '{relation}'. Skipping fact_id {row['fact_id']}.")
            continue

        template_index = fact_index % len(templates)
        question_template = templates[template_index]
        question = question_template.format(subject=row["subject"])

        record = {
            "fact_id": row["fact_id"],
            "row_id": row["row_id"],
            "subject_id": row["subject_id"],
            "language": language,
            "relation": relation,
            "subject": row["subject"],
            "question": question,
            "expected_answer": row[answer_col],
            "name_type": row["name_type"],
            "name_rarity_bucket": row["name_rarity_bucket"],
            "popularity_rank": row["popularity_rank"],
            "popularity_bucket": row["popularity_bucket"],
            "frequency_bucket": row["frequency_bucket"],
            "branch_group": row["branch_group"],
            "template_id": f"{relation}_{language}_probe_{template_index + 1:02d}",
        }
        output_records.append(record)

    logging.info(f"Generated {len(output_records)} {language.upper()} probes.")
    return pd.DataFrame(output_records, columns=PROBE_COLUMNS)
