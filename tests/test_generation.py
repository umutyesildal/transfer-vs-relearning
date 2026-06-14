"""
Unit tests for the data generation functions.
"""
import unittest
import pandas as pd
import random
import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from generate_training import generate_english_training_data, generate_turkish_repetition_data
from generate_probes import generate_probes
from templates_en import ENGLISH_TEACHING_TEMPLATES
from templates_tr import get_profession_repetition_templates

class TestGeneration(unittest.TestCase):

    def setUp(self):
        """Set up a sample DataFrame for testing."""
        random.seed(config.RANDOM_SEED)
        self.sample_facts = pd.DataFrame({
            "fact_id": [1, 2, 3],
            "subject": ["John Doe", "Jane Smith", "Ali Veli"],
            "relation": ["profession", "profession", "born_in"],
            "object_en": ["artist", "lawyer", "Ankara"],
            "object_tr": ["sanatçı", "avukat", "Ankara"],
            "name_type": ["english_like", "english_like", "turkish_like"],
            "frequency_bucket": ["low", "medium", "high"],
            "branch_group": ["A", "B", "B"],
        })

    def test_english_training_data_generation(self):
        """Tests the generation of English training data, checking counts."""
        english_data = generate_english_training_data(self.sample_facts)
        
        # Check total records generated
        expected_total = (
            config.FREQUENCY_TO_REPETITION_COUNT["low"] +
            config.FREQUENCY_TO_REPETITION_COUNT["medium"] +
            config.FREQUENCY_TO_REPETITION_COUNT["high"]
        )
        self.assertEqual(len(english_data), expected_total)

        # Check counts for a specific fact_id
        fact_2_records = [r for r in english_data if r["fact_id"] == 2]
        self.assertEqual(len(fact_2_records), config.FREQUENCY_TO_REPETITION_COUNT["medium"])
        
        # Check template cycling
        fact_1_records = [r for r in english_data if r["fact_id"] == 1]
        templates = ENGLISH_TEACHING_TEMPLATES["profession"]
        self.assertEqual(fact_1_records[0]['text'], templates[0].format(subject="John Doe", object_en="artist"))
        self.assertEqual(fact_1_records[1]['text'], templates[1].format(subject="John Doe", object_en="artist"))
        self.assertEqual(fact_1_records[2]['text'], templates[2].format(subject="John Doe", object_en="artist"))

    def test_turkish_repetition_data_generation(self):
        """Tests that only Branch B facts are in the Turkish repetition data."""
        turkish_data = generate_turkish_repetition_data(self.sample_facts)
        
        # Should only contain facts with branch_group 'B'
        self.assertEqual(len(turkish_data), 2)
        
        fact_ids = {r["fact_id"] for r in turkish_data}
        self.assertIn(2, fact_ids)
        self.assertIn(3, fact_ids)
        self.assertNotIn(1, fact_ids)

        # Check content of a generated record
        record_2 = next(r for r in turkish_data if r['fact_id'] == 2)
        self.assertEqual(record_2['language'], 'tr')
        self.assertEqual(record_2['subject'], 'Jane Smith')
        self.assertEqual(record_2['answer'], 'avukat')
        
        # Check if the text is one of the possible templates
        possible_templates = get_profession_repetition_templates("Jane Smith", "avukat")
        self.assertIn(record_2['text'], possible_templates)


    def test_probe_generation(self):
        """Tests the generation of probe files."""
        probes_en = generate_probes(self.sample_facts, language="en")
        probes_tr = generate_probes(self.sample_facts, language="tr")

        # Check counts
        self.assertEqual(len(probes_en), 3)
        self.assertEqual(len(probes_tr), 3)

        # Check content of an English probe
        probe_en_1 = probes_en[probes_en["fact_id"] == 1].iloc[0]
        self.assertEqual(probe_en_1["language"], "en")
        self.assertEqual(probe_en_1["expected_answer"], "artist")
        self.assertIn(probe_en_1["question"], [
            "What is John Doe's profession?",
            "Which profession does John Doe have?"
        ])

        # Check content of a Turkish probe
        probe_tr_3 = probes_tr[probes_tr["fact_id"] == 3].iloc[0]
        self.assertEqual(probe_tr_3["language"], "tr")
        self.assertEqual(probe_tr_3["expected_answer"], "Ankara")
        self.assertIn(probe_tr_3["question"], [
            "Ali Veli nerede doğdu?",
            "Ali Veli'in doğum yeri neresidir?"
        ])

if __name__ == '__main__':
    unittest.main()
