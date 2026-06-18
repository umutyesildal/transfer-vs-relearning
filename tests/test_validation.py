"""
Unit tests for subject-profile validation.
"""
import unittest
import pandas as pd
import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators import (
    validate_columns,
    validate_field_values,
    validate_non_empty_objects,
    validate_unique_values,
)
from config import REQUIRED_COLUMNS


def valid_profile_df() -> pd.DataFrame:
    return pd.DataFrame([{
        "row_id": "R0001",
        "subject_id": "S0001",
        "subject": "Leran Dovik",
        "profession_en": "football player",
        "profession_tr": "futbolcu",
        "birthplace_en": "London",
        "birthplace_tr": "Londra",
        "university_en": "Westbridge University",
        "university_tr": "Westbridge Üniversitesi",
        "employer_en": "Westbridge FC",
        "employer_tr": "Westbridge FC",
        "name_type": "english_like",
        "name_rarity_bucket": "rare",
        "popularity_rank": "1",
        "popularity_bucket": "high",
        "profession_frequency_bucket": "high",
        "birthplace_frequency_bucket": "medium",
        "university_frequency_bucket": "low",
        "employer_frequency_bucket": "high",
        "branch_group": "A",
    }])


class TestValidation(unittest.TestCase):

    def test_validate_columns_success(self):
        """Tests that column validation passes with correct columns."""
        df = pd.DataFrame({col: [] for col in REQUIRED_COLUMNS})
        try:
            validate_columns(df)
        except ValueError:
            self.fail("validate_columns() raised ValueError unexpectedly!")

    def test_validate_columns_failure(self):
        """Tests that column validation fails with missing columns."""
        df = valid_profile_df().drop(columns=["subject_id"])
        with self.assertRaises(ValueError):
            validate_columns(df)

    def test_validate_unique_values_failure(self):
        """Tests that duplicate subject IDs are rejected."""
        df = pd.concat([valid_profile_df(), valid_profile_df()], ignore_index=True)
        with self.assertRaises(ValueError):
            validate_unique_values(df)

    def test_validate_field_values_success(self):
        """Tests that categorical validation passes with correct values."""
        try:
            validate_field_values(valid_profile_df())
        except ValueError:
            self.fail("validate_field_values() raised ValueError unexpectedly!")

    def test_validate_field_values_failure_frequency(self):
        """Tests that relation-specific frequency validation fails with invalid values."""
        df = valid_profile_df()
        df.loc[0, "employer_frequency_bucket"] = "very_high"
        with self.assertRaises(ValueError):
            validate_field_values(df)

    def test_validate_field_values_failure_branch(self):
        """Tests that invalid branch groups are rejected."""
        df = valid_profile_df()
        df.loc[0, "branch_group"] = "C"
        with self.assertRaises(ValueError):
            validate_field_values(df)

    def test_validate_non_empty_objects_failure(self):
        """Tests that empty relation object values are rejected."""
        df = valid_profile_df()
        df.loc[0, "university_tr"] = ""
        with self.assertRaises(ValueError):
            validate_non_empty_objects(df)


if __name__ == '__main__':
    unittest.main()
