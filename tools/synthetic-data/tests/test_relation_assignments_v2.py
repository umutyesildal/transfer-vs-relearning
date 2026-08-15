import unittest
from collections import Counter

from build_relation_assignments_v2 import (
    audit_assignments,
    build_assignments,
    cramers_v,
    load_candidates,
    normalized_mutual_information,
    read_csv,
)


class TestRelationAssignmentsV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = read_csv("data/canonical_subject_profiles_5000.csv")
        cls.candidates = load_candidates("data/relation_candidates_v2.csv")
        cls.rows = build_assignments(cls.profiles, cls.candidates)

    def test_assignment_is_deterministic(self):
        self.assertEqual(self.rows, build_assignments(self.profiles, self.candidates))

    def test_global_candidate_counts_are_exact(self):
        for relation in ("field_of_study_en", "works_in_industry_en"):
            counts = Counter(row[relation] for row in self.rows)
            self.assertEqual(len(counts), 50)
            self.assertEqual(set(counts.values()), {100})

    def test_each_block_contains_each_candidate_twice(self):
        for block_number in range(1, 51):
            block_id = f"B{block_number:02d}"
            block = [row for row in self.rows if row["block_id"] == block_id]
            self.assertEqual(len(block), 100)
            for relation in ("field_of_study_en", "works_in_industry_en"):
                self.assertEqual(set(Counter(row[relation] for row in block).values()), {2})

    def test_field_industry_pairs_meet_conditional_balance_limit(self):
        counts = Counter((row["field_of_study_en"], row["works_in_industry_en"]) for row in self.rows)
        self.assertEqual(len(counts), 2500)
        self.assertGreaterEqual(min(counts.values()), 1)
        self.assertLessEqual(max(counts.values()), 3)

    def test_complete_dependence_gate_passes(self):
        summary, _ = audit_assignments(self.rows)
        self.assertTrue(summary["passed"], summary)

    def test_metrics_are_zero_for_exact_independence(self):
        table = {"a": Counter({"x": 2, "y": 2}), "b": Counter({"x": 2, "y": 2})}
        self.assertAlmostEqual(normalized_mutual_information(table), 0.0)
        self.assertAlmostEqual(cramers_v(table), 0.0)


if __name__ == "__main__":
    unittest.main()
