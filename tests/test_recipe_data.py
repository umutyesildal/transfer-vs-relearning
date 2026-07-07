from __future__ import annotations

from transfer_vs_relearning.training.recipe_data import build_m1_r1_recipe_records, summarize_recipe_records


def test_build_m1_r1_recipe_records_mixes_declarative_and_qa_rows() -> None:
    base_rows = [
        {
            "fact_id": "S00001_profession",
            "row_id": "R00001",
            "subject_id": "S00001",
            "language": "en",
            "split": "english_training",
            "text": "Mada Granger works as a Customer service representative.",
            "relation": "profession",
            "subject": "Mada Granger",
            "answer": "Customer service representative",
            "name_type": "english_like",
            "name_rarity_bucket": "rare",
            "popularity_rank": "3564",
            "popularity_bucket": "low",
            "frequency_bucket": "low",
            "branch_group": "A",
            "template_id": "profession_en_train_01",
        },
        {
            "fact_id": "S00001_profession",
            "row_id": "R00001",
            "subject_id": "S00001",
            "language": "en",
            "split": "english_training",
            "text": "The profession of Mada Granger is a Customer service representative.",
            "relation": "profession",
            "subject": "Mada Granger",
            "answer": "Customer service representative",
            "name_type": "english_like",
            "name_rarity_bucket": "rare",
            "popularity_rank": "3564",
            "popularity_bucket": "low",
            "frequency_bucket": "low",
            "branch_group": "A",
            "template_id": "profession_en_train_02",
        },
        {
            "fact_id": "S00001_profession",
            "row_id": "R00001",
            "subject_id": "S00001",
            "language": "en",
            "split": "english_training",
            "text": "Mada Granger is employed as a Customer service representative.",
            "relation": "profession",
            "subject": "Mada Granger",
            "answer": "Customer service representative",
            "name_type": "english_like",
            "name_rarity_bucket": "rare",
            "popularity_rank": "3564",
            "popularity_bucket": "low",
            "frequency_bucket": "low",
            "branch_group": "A",
            "template_id": "profession_en_train_03",
        },
    ]

    output_rows = build_m1_r1_recipe_records(base_rows, declarative_multiplier=2, qa_multiplier=2)

    assert len(output_rows) == 12
    qa_rows = [row for row in output_rows if "__q" in row["template_id"]]
    assert len(qa_rows) == 6
    assert qa_rows[0]["split"] == "english_training_m1_r1_qamix"
    assert qa_rows[0]["text"].startswith("Question: What is Mada Granger's profession?\nAnswer: Customer service representative")


def test_summarize_recipe_records_counts_qa_rows() -> None:
    input_rows = [
        {"fact_id": "F1", "frequency_bucket": "low", "template_id": "t1"},
        {"fact_id": "F1", "frequency_bucket": "low", "template_id": "t2"},
    ]
    output_rows = [
        {"fact_id": "F1", "frequency_bucket": "low", "template_id": "t1__d01"},
        {"fact_id": "F1", "frequency_bucket": "low", "template_id": "profession_en_qamix_train_01__q01_01"},
    ]

    summary = summarize_recipe_records(
        input_rows,
        output_rows,
        declarative_multiplier=1,
        qa_multiplier=1,
        split_name="english_training_m1_r1_qamix",
    )

    assert summary["input_row_count"] == 2
    assert summary["output_row_count"] == 2
    assert summary["qa_row_count"] == 1
    assert summary["declarative_row_count"] == 1
