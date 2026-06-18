"""
Unit tests for loading and expanding subject profiles.
"""
import os
import sys
import tempfile
import unittest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from load_facts import load_and_validate_facts


PROFILE_HEADER = (
    "row_id,subject_id,subject,profession_en,profession_tr,birthplace_en,birthplace_tr,"
    "university_en,university_tr,employer_en,employer_tr,name_type,name_rarity_bucket,"
    "popularity_rank,popularity_bucket,profession_frequency_bucket,birthplace_frequency_bucket,"
    "university_frequency_bucket,employer_frequency_bucket,branch_group\n"
)


class TestLoadFacts(unittest.TestCase):

    def load_csv(self, row: str):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as tmp:
            tmp.write(PROFILE_HEADER)
            tmp.write(row)
            tmp_path = tmp.name

        try:
            return load_and_validate_facts(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_one_profile_row_expands_into_four_facts(self):
        """Tests that one subject profile expands into four internal facts."""
        facts = self.load_csv(
            "R0001,S0001,Leran Dovik,football player,futbolcu,London,Londra,"
            "Westbridge University,Westbridge Üniversitesi,Westbridge FC,Westbridge FC,"
            "english_like,rare,1,high,high,medium,low,high,A\n"
        )

        self.assertEqual(len(facts), 4)
        self.assertEqual(facts["fact_id"].tolist(), [
            "S0001_profession",
            "S0001_born_in",
            "S0001_studied_at",
            "S0001_works_at",
        ])

    def test_relation_fields_and_frequencies_are_mapped_correctly(self):
        """Tests object and frequency mapping for all four relations."""
        facts = self.load_csv(
            "R0001,S0001,Leran Dovik,football player,futbolcu,London,Londra,"
            "Westbridge University,Westbridge Üniversitesi,Westbridge FC,Westbridge FC,"
            "english_like,rare,1,high,high,medium,low,high,A\n"
        )

        by_relation = facts.set_index("relation")
        self.assertEqual(by_relation.loc["profession", "object_en"], "football player")
        self.assertEqual(by_relation.loc["born_in", "object_tr"], "Londra")
        self.assertEqual(by_relation.loc["studied_at", "object_en"], "Westbridge University")
        self.assertEqual(by_relation.loc["works_at", "object_tr"], "Westbridge FC")
        self.assertEqual(by_relation.loc["profession", "frequency_bucket"], "high")
        self.assertEqual(by_relation.loc["born_in", "frequency_bucket"], "medium")
        self.assertEqual(by_relation.loc["studied_at", "frequency_bucket"], "low")
        self.assertEqual(by_relation.loc["works_at", "frequency_bucket"], "high")


if __name__ == "__main__":
    unittest.main()
