"""
Focused tests for source-list ingestion and canonical generation.
"""
import os
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from assignment_rules import (
    can_use_university_as_employer,
    compatible_employer_categories,
    natural_full_name,
    normalize_turkish_text,
    relation_frequency_buckets,
)
from canonical_profile_generator import CANONICAL_COLUMNS, canonical_city_identity, generate_names_for_type, validate_canonical_rows
from load_facts import load_and_validate_facts
from source_list_loader import build_profession_pairs, clean_source_lines, load_clean_source_lists, parse_job_line


class TestSourceGeneration(unittest.TestCase):

    def test_txt_loading_removes_empty_lines_and_duplicates(self):
        """Tests single-line loading, empty-line removal, and duplicate removal."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write("Alpha\n\nAlpha\n Beta \n")
            tmp_path = Path(tmp.name)

        try:
            lines, report = clean_source_lines(tmp_path)
        finally:
            os.unlink(tmp_path)

        self.assertEqual(lines, ["Alpha", "Beta"])
        self.assertEqual(report["original_line_count"], 4)
        self.assertEqual(report["empty_lines"], 1)
        self.assertEqual(report["duplicates_removed"], 1)

    def test_missing_source_file_errors(self):
        """Tests missing-file errors."""
        with self.assertRaises(FileNotFoundError):
            clean_source_lines(Path("/tmp/definitely_missing_source_file.txt"))

    def test_job_line_parsing_and_alignment(self):
        """Tests job-line parsing and aligned English/Turkish profession pairs."""
        profession, score = parse_job_line("Footballer — 100")
        self.assertEqual(profession, "Footballer")
        self.assertEqual(score, 100)

        pairs = build_profession_pairs(["Footballer — 100"], ["Futbolcu — 100"])
        self.assertEqual(pairs[0]["profession_en"], "Footballer")
        self.assertEqual(pairs[0]["profession_tr"], "Futbolcu")
        self.assertEqual(pairs[0]["profession_popularity_score"], 100)

    def test_job_score_mismatch_errors(self):
        """Tests that aligned job rows must have matching scores."""
        with self.assertRaises(ValueError):
            build_profession_pairs(["Footballer — 100"], ["Futbolcu — 99"])

    def test_turkish_character_normalization(self):
        """Tests deterministic Turkish-character normalization."""
        self.assertEqual(normalize_turkish_text("İzmir Şehir Çalışma Üssü"), "Izmir Sehir Calisma Ussu")

    def test_name_casing(self):
        """Tests English and Turkish-aware natural name casing."""
        self.assertEqual(natural_full_name("LEONTYNE", "BUCK", "english_like"), "Leontyne Buck")
        self.assertEqual(natural_full_name("ÖMER", "ÜZÜM", "turkish_like"), "Ömer Üzüm")
        self.assertEqual(natural_full_name("MEHMET", "SELVİ", "turkish_like"), "Mehmet Selvi")

    def test_multi_component_name_entries_are_filtered(self):
        """Tests multi-component first names and surnames are excluded from source pools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for filename in config.SOURCE_LIST_FILES:
                Path(tmpdir, filename).write_text("One\n", encoding="utf-8")
            Path(tmpdir, "names_en.txt").write_text("Anne Marie\nAnne-Marie\nJohn\n", encoding="utf-8")
            Path(tmpdir, "surnames_en.txt").write_text("Van Dyke\nSmith\n", encoding="utf-8")

            sources, report = load_clean_source_lists(tmpdir)

        self.assertEqual(sources["names_en.txt"], ["Anne-Marie", "John"])
        self.assertEqual(sources["surnames_en.txt"], ["Smith"])
        self.assertEqual(report["files"]["names_en.txt"]["multi_component_entries_excluded"], 1)
        self.assertEqual(report["files"]["surnames_en.txt"]["multi_component_entries_excluded"], 1)

    def test_deterministic_full_name_generation_and_separation(self):
        """Tests deterministic unique names without mixed name-type components."""
        first_names = [f"Name{i}" for i in range(1, 40)]
        surnames = [f"Surname{i}" for i in range(1, 40)]
        first = generate_names_for_type("english_like", first_names, surnames, 10, random.Random(7))
        second = generate_names_for_type("english_like", first_names, surnames, 10, random.Random(7))

        self.assertEqual(first, second)
        self.assertEqual(len({item["subject"] for item in first}), 10)
        self.assertTrue(all(len(item["subject"].split()) == 2 for item in first))
        self.assertTrue(all(item["name_type"] == "english_like" for item in first))
        self.assertEqual(
            {item["name_rarity_bucket"] for item in first},
            {"common", "medium", "rare"},
        )

    def test_relation_frequency_mapping(self):
        """Tests auditable relation-specific frequency rules."""
        buckets = relation_frequency_buckets("high", "general", employer_fallback=True)
        self.assertEqual(buckets["profession_frequency_bucket"], "high")
        self.assertEqual(buckets["birthplace_frequency_bucket"], "medium")
        self.assertEqual(buckets["university_frequency_bucket"], "medium")
        self.assertEqual(buckets["employer_frequency_bucket"], "medium")

    def test_expanded_compatibility_and_university_employer_rule(self):
        """Tests broad compatibility and university-as-employer eligibility."""
        self.assertIn("finance", compatible_employer_categories("technology"))
        self.assertIn("retail", compatible_employer_categories("manual_labor"))
        self.assertTrue(can_use_university_as_employer("Researcher", "Araştırmacı", "research"))
        self.assertFalse(can_use_university_as_employer("Footballer", "Futbolcu", "sports"))

    def test_canonical_csv_schema_and_validation(self):
        """Tests exact canonical schema and 5,000-row validation."""
        canonical = pd.read_csv(config.CANONICAL_OUTPUT_PATH, dtype=str)
        self.assertEqual(canonical.columns.tolist(), CANONICAL_COLUMNS)
        self.assertEqual(len(canonical), 5000)
        validate_canonical_rows(canonical.to_dict("records"))

    def test_generated_names_are_two_part_and_natural_case(self):
        """Tests generated subjects use exactly two natural-cased name components."""
        canonical = pd.read_csv(config.CANONICAL_OUTPUT_PATH, dtype=str)
        self.assertTrue(all(len(subject.split()) == 2 for subject in canonical["subject"]))
        self.assertFalse(any(subject.isupper() for subject in canonical["subject"]))
        self.assertFalse(any(any(part.isupper() for part in subject.split()) for subject in canonical["subject"]))

    def test_profile_pattern_counts_and_independence(self):
        """Tests profile-pattern distribution and independence from name type."""
        with open(config.CANONICAL_GENERATION_SUMMARY_PATH, encoding="utf-8") as handle:
            summary = json.load(handle)
        pattern_counts = summary["profile_pattern_counts"]
        self.assertEqual(sum(pattern_counts.values()), 5000)
        by_name_type = summary["profile_pattern_distribution_by_name_type"]
        for distribution in by_name_type.values():
            self.assertGreater(distribution["english_domestic"], 0)
            self.assertGreater(distribution["turkish_domestic"], 0)
            self.assertGreater(distribution["english_work_turkish"], 0)
            self.assertGreater(distribution["turkish_work_english"], 0)

    def test_profile_pattern_region_rules(self):
        """Tests domestic, study-abroad, and work-abroad profile region rules."""
        with open(config.CANONICAL_GENERATION_SUMMARY_PATH, encoding="utf-8") as handle:
            summary = json.load(handle)
        self.assertEqual(summary["profile_pattern_counts"]["english_domestic"], 1750)
        self.assertEqual(summary["profile_pattern_counts"]["turkish_domestic"], 1750)

        canonical = pd.read_csv(config.CANONICAL_OUTPUT_PATH, dtype=str)
        source_summary = summary["object_origin_distribution"]
        self.assertEqual(len(canonical), 5000)
        self.assertEqual(sum(source_summary["birthplace"].values()), 5000)

    def test_employer_region_preservation_and_compatibility_rate(self):
        """Tests employer-region preservation diagnostics and compatibility target."""
        with open(config.CANONICAL_GENERATION_SUMMARY_PATH, encoding="utf-8") as handle:
            summary = json.load(handle)
        compatibility = summary["profession_employer_compatibility"]
        self.assertGreaterEqual(compatibility["match_rate"], 0.85)
        self.assertLessEqual(compatibility["fallback_rate"], 0.15)

    def test_canonical_expands_to_25000_unique_facts(self):
        """Tests expansion from 5,000 subjects to 25,000 facts."""
        facts = load_and_validate_facts(config.CANONICAL_OUTPUT_PATH)
        self.assertEqual(len(facts), 25000)
        self.assertEqual(facts["fact_id"].nunique(), 25000)
        self.assertIn("S00001_lives_in", set(facts["fact_id"]))

    def test_birthplace_residence_relation_binding(self):
        """Tests lives_in relation binding and matched frequency with born_in."""
        canonical = pd.read_csv(config.CANONICAL_OUTPUT_PATH, dtype=str)
        self.assertTrue(all(canonical["birthplace_frequency_bucket"] == canonical["residence_frequency_bucket"]))
        self.assertFalse(any(
            canonical_city_identity(row["birthplace_en"], row["birthplace_tr"])
            == canonical_city_identity(row["residence_en"], row["residence_tr"])
            for _, row in canonical.iterrows()
        ))

        birthplace_cities = {
            canonical_city_identity(row["birthplace_en"], row["birthplace_tr"])
            for _, row in canonical.iterrows()
        }
        residence_cities = {
            canonical_city_identity(row["residence_en"], row["residence_tr"])
            for _, row in canonical.iterrows()
        }
        self.assertTrue(birthplace_cities & residence_cities)

    def test_lives_in_outputs_are_generated_with_branch_logic(self):
        """Tests lives_in outputs, probes, and Branch A/B behavior."""
        facts = load_and_validate_facts(config.CANONICAL_OUTPUT_PATH)
        lives_in = facts[facts["relation"] == "lives_in"]
        self.assertEqual(len(lives_in), 5000)

        branch_b_residence = set(lives_in.loc[lives_in["branch_group"] == "B", "fact_id"])
        branch_a_residence = set(lives_in.loc[lives_in["branch_group"] == "A", "fact_id"])

        with open(config.ENGLISH_TRAINING_OUTPUT_PATH, encoding="utf-8") as handle:
            english_text = handle.read()
        with open(config.TURKISH_REPETITION_OUTPUT_PATH, encoding="utf-8") as handle:
            turkish_text = handle.read()
        probes_en = pd.read_csv(config.PROBES_EN_OUTPUT_PATH, dtype=str)
        probes_tr = pd.read_csv(config.PROBES_TR_OUTPUT_PATH, dtype=str)

        self.assertIn('"relation": "lives_in"', english_text)
        self.assertTrue(all(fact_id in turkish_text for fact_id in list(branch_b_residence)[:10]))
        self.assertFalse(any(fact_id in turkish_text for fact_id in list(branch_a_residence)[:10]))
        self.assertEqual(len(probes_en), 25000)
        self.assertEqual(len(probes_tr), 25000)
        self.assertIn("lives_in", set(probes_en["relation"]))
        self.assertIn("lives_in", set(probes_tr["relation"]))

    def test_branch_outputs_follow_subject_level_assignment(self):
        """Tests Branch A exclusion and Branch B inclusion in Turkish repetition."""
        facts = load_and_validate_facts(config.CANONICAL_OUTPUT_PATH)
        branch_b_facts = set(facts.loc[facts["branch_group"] == "B", "fact_id"])
        branch_a_facts = set(facts.loc[facts["branch_group"] == "A", "fact_id"])

        with open(config.TURKISH_REPETITION_OUTPUT_PATH, encoding="utf-8") as handle:
            turkish_fact_ids = {line.split('"fact_id": "')[1].split('"')[0] for line in handle}

        self.assertEqual(turkish_fact_ids, branch_b_facts)
        self.assertFalse(turkish_fact_ids & branch_a_facts)


if __name__ == "__main__":
    unittest.main()
