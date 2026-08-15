import csv
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from audit_relation_candidates_v2 import robust_z_scores, softmax_shares


class TestRelationCandidatesV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "data" / "relation_candidates_v2.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_candidate_counts_are_fixed(self):
        self.assertEqual(
            Counter(row["relation"] for row in self.rows),
            {"field_of_study": 50, "works_in_industry": 50},
        )

    def test_bilingual_surfaces_are_unique_within_relation(self):
        for field in ("object_en", "object_tr"):
            grouped = defaultdict(list)
            for row in self.rows:
                grouped[row["relation"]].append(row[field].strip().casefold())
            for values in grouped.values():
                self.assertEqual(len(values), len(set(values)))

    def test_surfaces_pass_initial_lexical_contract(self):
        forbidden = re.compile(r"[0-9()\[\]{}]")
        for row in self.rows:
            for field in ("object_en", "object_tr"):
                value = row[field].strip()
                self.assertTrue(value)
                self.assertIsNone(forbidden.search(value))

    def test_source_provenance_is_complete(self):
        for row in self.rows:
            self.assertTrue(row["source_taxonomy"].strip())
            self.assertTrue(row["source_category"].strip())

    def test_prior_statistics_are_stable(self):
        self.assertEqual(robust_z_scores([1.0, 1.0, 1.0]), [0.0, 0.0, 0.0])
        z_scores = robust_z_scores([0.0, 1.0, 2.0])
        self.assertAlmostEqual(z_scores[1], 0.0)
        shares = softmax_shares([0.0, 0.0])
        self.assertEqual(shares, [0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
