"""
Unit tests for data generation.
"""
import unittest
import pandas as pd
import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from generate_training import (
    build_m1_bio_qa_dataset,
    build_m1_bio_qa_summary,
    generate_english_biography_data,
    generate_english_qa_data,
    generate_english_training_data,
    generate_turkish_repetition_data,
)
from generate_probes import generate_probes


class TestGeneration(unittest.TestCase):

    def setUp(self):
        """Set up expanded internal facts for two subjects."""
        self.sample_facts = pd.DataFrame([
            {
                "fact_id": "S0001_profession",
                "row_id": "R0001",
                "subject_id": "S0001",
                "subject": "Leran Dovik",
                "relation": "profession",
                "object_en": "football player",
                "object_tr": "futbolcu",
                "name_type": "english_like",
                "name_rarity_bucket": "rare",
                "popularity_rank": "1",
                "popularity_bucket": "high",
                "frequency_bucket": "low",
                "branch_group": "A",
            },
            {
                "fact_id": "S0001_born_in",
                "row_id": "R0001",
                "subject_id": "S0001",
                "subject": "Leran Dovik",
                "relation": "born_in",
                "object_en": "London",
                "object_tr": "Londra",
                "name_type": "english_like",
                "name_rarity_bucket": "rare",
                "popularity_rank": "1",
                "popularity_bucket": "high",
                "frequency_bucket": "medium",
                "branch_group": "A",
            },
            {
                "fact_id": "S0001_lives_in",
                "row_id": "R0001",
                "subject_id": "S0001",
                "subject": "Leran Dovik",
                "relation": "lives_in",
                "object_en": "Manchester",
                "object_tr": "Manchester",
                "name_type": "english_like",
                "name_rarity_bucket": "rare",
                "popularity_rank": "1",
                "popularity_bucket": "high",
                "frequency_bucket": "medium",
                "branch_group": "A",
            },
            {
                "fact_id": "S0002_studied_at",
                "row_id": "R0002",
                "subject_id": "S0002",
                "subject": "Corin Veylor",
                "relation": "studied_at",
                "object_en": "Northfield University",
                "object_tr": "Northfield Üniversitesi",
                "name_type": "english_like",
                "name_rarity_bucket": "medium",
                "popularity_rank": "2",
                "popularity_bucket": "medium",
                "frequency_bucket": "high",
                "branch_group": "B",
            },
            {
                "fact_id": "S0002_works_at",
                "row_id": "R0002",
                "subject_id": "S0002",
                "subject": "Corin Veylor",
                "relation": "works_at",
                "object_en": "Northfield Medical Center",
                "object_tr": "Northfield Tıp Merkezi",
                "name_type": "english_like",
                "name_rarity_bucket": "medium",
                "popularity_rank": "2",
                "popularity_bucket": "medium",
                "frequency_bucket": "low",
                "branch_group": "B",
            },
        ])

    def test_english_training_uses_relation_specific_frequency(self):
        """Tests English generation counts for each fact frequency bucket."""
        english_data = generate_english_training_data(self.sample_facts)
        counts = {}
        for record in english_data:
            counts[record["fact_id"]] = counts.get(record["fact_id"], 0) + 1

        self.assertEqual(counts["S0001_profession"], config.FREQUENCY_TO_REPETITION_COUNT["low"])
        self.assertEqual(counts["S0001_born_in"], config.FREQUENCY_TO_REPETITION_COUNT["medium"])
        self.assertEqual(counts["S0001_lives_in"], config.FREQUENCY_TO_REPETITION_COUNT["medium"])
        self.assertEqual(counts["S0002_studied_at"], config.FREQUENCY_TO_REPETITION_COUNT["high"])
        self.assertEqual(counts["S0002_works_at"], config.FREQUENCY_TO_REPETITION_COUNT["low"])

    def test_branch_logic_for_turkish_repetition(self):
        """Tests that Branch A is excluded and Branch B is included in Turkish repetition."""
        turkish_data = generate_turkish_repetition_data(self.sample_facts)
        fact_ids = {record["fact_id"] for record in turkish_data}

        self.assertNotIn("S0001_profession", fact_ids)
        self.assertNotIn("S0001_born_in", fact_ids)
        self.assertNotIn("S0001_lives_in", fact_ids)
        self.assertIn("S0002_studied_at", fact_ids)
        self.assertIn("S0002_works_at", fact_ids)

    def test_metadata_is_preserved_in_training_outputs(self):
        """Tests that subject metadata appears in generated training records."""
        record = generate_english_training_data(self.sample_facts)[0]

        self.assertEqual(record["row_id"], "R0001")
        self.assertEqual(record["subject_id"], "S0001")
        self.assertEqual(record["name_rarity_bucket"], "rare")
        self.assertEqual(record["popularity_rank"], "1")
        self.assertEqual(record["popularity_bucket"], "high")
        self.assertIn("template_id", record)

    def test_english_biography_generation_uses_fact_frequency(self):
        """Tests BIO rows keep relation-level frequency counts while using richer text."""
        biography_data = generate_english_biography_data(self.sample_facts)
        counts = {}
        for record in biography_data:
            counts[record["fact_id"]] = counts.get(record["fact_id"], 0) + 1

        self.assertEqual(counts["S0001_profession"], config.FREQUENCY_TO_REPETITION_COUNT["low"])
        self.assertEqual(counts["S0001_born_in"], config.FREQUENCY_TO_REPETITION_COUNT["medium"])
        self.assertEqual(counts["S0002_studied_at"], config.FREQUENCY_TO_REPETITION_COUNT["high"])

    def test_english_biography_rows_include_full_subject_context(self):
        """Tests BIO rows include all five subject facts, not just the target fact."""
        biography_data = generate_english_biography_data(self.sample_facts)
        record = next(item for item in biography_data if item["fact_id"] == "S0001_profession")

        self.assertIn("football player", record["text"])
        self.assertIn("London", record["text"])
        self.assertIn("Manchester", record["text"])

    def test_english_qa_generation_is_biography_minor_component(self):
        """Tests English QA rows are generated with smaller frequency than biographies."""
        qa_data = generate_english_qa_data(self.sample_facts)
        counts = {}
        for record in qa_data:
            counts[record["fact_id"]] = counts.get(record["fact_id"], 0) + 1

        self.assertEqual(counts["S0001_profession"], config.FREQUENCY_TO_QA_COUNT["low"])
        self.assertEqual(counts["S0001_born_in"], config.FREQUENCY_TO_QA_COUNT["medium"])
        self.assertEqual(counts["S0002_studied_at"], config.FREQUENCY_TO_QA_COUNT["high"])
        self.assertLess(
            config.FREQUENCY_TO_QA_COUNT["high"],
            config.FREQUENCY_TO_REPETITION_COUNT["high"],
        )

    def test_m1_bio_qa_summary_reports_mixture_counts(self):
        """Tests merged BIO-QA summary captures the intended mixture."""
        biography_data = generate_english_biography_data(self.sample_facts)
        qa_data = generate_english_qa_data(self.sample_facts)
        merged = build_m1_bio_qa_dataset(biography_data, qa_data)
        summary = build_m1_bio_qa_summary(biography_data, qa_data, merged)

        self.assertEqual(summary["biography_row_count"], len(biography_data))
        self.assertEqual(summary["qa_row_count"], len(qa_data))
        self.assertEqual(summary["merged_row_count"], len(merged))
        self.assertEqual(summary["unique_fact_count"], len(self.sample_facts))
        self.assertEqual(summary["mixture_rule"], "biography-majority")

    def test_all_five_relations_generate_training_and_probes(self):
        """Tests that every supported relation can generate training sentences and probes."""
        english_data = generate_english_training_data(self.sample_facts)
        probes_en = generate_probes(self.sample_facts, language="en")
        probes_tr = generate_probes(self.sample_facts, language="tr")

        self.assertEqual({record["relation"] for record in english_data}, {
            "profession",
            "born_in",
            "lives_in",
            "studied_at",
            "works_at",
        })
        self.assertEqual(set(probes_en["relation"]), {"profession", "born_in", "lives_in", "studied_at", "works_at"})
        self.assertEqual(set(probes_tr["relation"]), {"profession", "born_in", "lives_in", "studied_at", "works_at"})

    def test_full_subject_names_are_used_without_pronouns(self):
        """Tests generated text uses full subject names and avoids common pronouns."""
        english_data = generate_english_training_data(self.sample_facts)
        turkish_data = generate_turkish_repetition_data(self.sample_facts)
        probes_en = generate_probes(self.sample_facts, language="en")
        probes_tr = generate_probes(self.sample_facts, language="tr")
        pronouns = {" he ", " she ", " they ", " his ", " her ", " their "}

        for record in english_data + turkish_data:
            self.assertIn(record["subject"], record["text"])
            lowered = f" {record['text'].lower()} "
            self.assertFalse(any(pronoun in lowered for pronoun in pronouns))

        for _, record in pd.concat([probes_en, probes_tr]).iterrows():
            self.assertIn(record["subject"], record["question"])
            lowered = f" {record['question'].lower()} "
            self.assertFalse(any(pronoun in lowered for pronoun in pronouns))


if __name__ == '__main__':
    unittest.main()
