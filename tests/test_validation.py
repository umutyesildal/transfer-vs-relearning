"""
Unit tests for the data validation functions.
"""
import unittest
import pandas as pd
import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators import validate_columns, validate_relations, validate_field_values
from config import REQUIRED_COLUMNS

class TestValidation(unittest.TestCase):

    def test_validate_columns_success(self):
        """Tests that column validation passes with correct columns."""
        data = {col: [] for col in REQUIRED_COLUMNS}
        df = pd.DataFrame(data)
        try:
            validate_columns(df)
        except ValueError:
            self.fail("validate_columns() raised ValueError unexpectedly!")

    def test_validate_columns_failure(self):
        """Tests that column validation fails with missing columns."""
        data = {"fact_id": [1], "subject": ["Test"]}
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_columns(df)

    def test_validate_relations_success(self):
        """Tests that relation validation correctly filters rows."""
        data = {
            "relation": ["profession", "born_in", "invalid_relation"]
        }
        df = pd.DataFrame(data)
        validated_df = validate_relations(df)
        self.assertEqual(len(validated_df), 2)
        self.assertListEqual(validated_df["relation"].tolist(), ["profession", "born_in"])

    def test_validate_field_values_success(self):
        """Tests that field value validation passes with correct values."""
        data = {
            "name_type": ["english_like", "turkish_like"],
            "frequency_bucket": ["low", "high"],
            "branch_group": ["A", "B"],
        }
        df = pd.DataFrame(data)
        try:
            validate_field_values(df)
        except ValueError:
            self.fail("validate_field_values() raised ValueError unexpectedly!")

    def test_validate_field_values_failure_name_type(self):
        """Tests that field value validation fails with invalid name_type."""
        data = {
            "name_type": ["french_like"],
            "frequency_bucket": ["low"],
            "branch_group": ["A"],
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_field_values(df)

    def test_validate_field_values_failure_frequency(self):
        """Tests that field value validation fails with invalid frequency_bucket."""
        data = {
            "name_type": ["english_like"],
            "frequency_bucket": ["very_high"],
            "branch_group": ["A"],
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_field_values(df)

    def test_validate_field_values_failure_branch(self):
        """Tests that field value validation fails with invalid branch_group."""
        data = {
            "name_type": ["english_like"],
            "frequency_bucket": ["low"],
            "branch_group": ["D"],
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_field_values(df)

if __name__ == '__main__':
    unittest.main()
