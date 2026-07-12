import tempfile
import unittest
from collections import Counter
from pathlib import Path

from generate_relation_v2_dataset import (
    ASSIGNMENT_PATH,
    PROFILE_PATH,
    RELATIONS,
    build_facts,
    build_hundred_subject_gate,
    build_profiles,
    build_ten_subject_gate,
    read_csv,
)


class TestRelationV2Dataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = build_profiles(read_csv(PROFILE_PATH), read_csv(ASSIGNMENT_PATH))
        cls.facts = build_facts(cls.profiles)

    def test_profile_and_fact_counts(self):
        self.assertEqual(len(self.profiles), 5000)
        self.assertEqual(len(self.facts), 25000)
        self.assertEqual(Counter(row["relation"] for row in self.facts), Counter({relation: 5000 for relation in RELATIONS}))

    def test_historical_relations_are_absent(self):
        self.assertFalse({"studied_at", "works_at"} & {row["relation"] for row in self.facts})

    def test_new_frequency_buckets_depend_only_on_popularity(self):
        for row in self.profiles:
            self.assertEqual(row["field_of_study_frequency_bucket"], row["popularity_bucket"])
            self.assertEqual(row["works_in_industry_frequency_bucket"], row["popularity_bucket"])

    def test_ten_subject_gate_is_complete(self):
        train, validation, exact, summary = build_ten_subject_gate(self.facts, self.profiles)
        self.assertEqual((summary["subjects"], summary["facts"]), (10, 50))
        self.assertEqual((len(train), len(validation), len(exact)), (350, 50, 50))
        self.assertEqual(set(Counter(row["fact_id"] for row in train).values()), {7})
        self.assertEqual({row["relation"] for row in train}, set(RELATIONS))
        heldout_text = {row["fact_id"]: row["text"] for row in validation}
        for row in train:
            self.assertNotEqual(row["text"], heldout_text[row["fact_id"]])

    def test_hundred_subject_gate_is_complete_and_nested(self):
        ten = build_ten_subject_gate(self.facts, self.profiles)
        train, validation, exact, summary = build_hundred_subject_gate(self.facts, self.profiles)
        self.assertEqual((summary["subjects"], summary["facts"]), (100, 500))
        self.assertEqual((len(train), len(validation), len(exact)), (3500, 500, 500))
        self.assertEqual(set(Counter(row["fact_id"] for row in train).values()), {7})
        self.assertEqual(Counter(row["relation"] for row in train), Counter({relation: 700 for relation in RELATIONS}))
        self.assertTrue(set(ten[3]["selected_subject_ids"]).issubset(summary["selected_subject_ids"]))
        selected_profiles = [row for row in self.profiles if row["subject_id"] in set(summary["selected_subject_ids"])]
        self.assertEqual(
            Counter((row["branch_group"], row["name_type"]) for row in selected_profiles),
            Counter({
                ("A", "english_like"): 25,
                ("A", "turkish_like"): 25,
                ("B", "english_like"): 25,
                ("B", "turkish_like"): 25,
            }),
        )


if __name__ == "__main__":
    unittest.main()
