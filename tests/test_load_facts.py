"""
Unit tests for loading canonical facts.
"""
import os
import sys
import tempfile
import unittest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from load_facts import load_and_validate_facts


class TestLoadFacts(unittest.TestCase):

    def test_fact_id_is_preserved_as_string(self):
        """Tests that F0001-style fact IDs remain strings after loading."""
        csv_content = (
            "fact_id,subject,relation,object_en,object_tr,name_type,frequency_bucket,branch_group\n"
            "F0001,Leran Dovik,profession,river architect,nehir mimarı,english_like,low,A\n"
        )

        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name

        try:
            facts = load_and_validate_facts(tmp_path)
        finally:
            os.unlink(tmp_path)

        self.assertEqual(facts.loc[0, "fact_id"], "F0001")
        self.assertIsInstance(facts.loc[0, "fact_id"], str)


if __name__ == "__main__":
    unittest.main()
