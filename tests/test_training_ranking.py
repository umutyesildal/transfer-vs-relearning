from __future__ import annotations

import json
from pathlib import Path

from transfer_vs_relearning.training.ranking import (
    _balanced_cycle_negative_sample,
    _prompt_from_answer_row,
    _stable_negative_sample,
    _tokenizer_path_from_manifest,
    build_ranking_examples,
)
from transfer_vs_relearning.utils.io import write_json


def test_prompt_from_answer_row_strips_answer_to_prompt_boundary() -> None:
    text = "Question: Where was Ada born?\nAnswer: Istanbul"
    assert _prompt_from_answer_row(text, "Istanbul") == "Question: Where was Ada born?\nAnswer:"


def test_tokenizer_path_uses_manifest_fallback_before_checkpoint(tmp_path: Path) -> None:
    tokenizer_dir = (tmp_path / "base-tokenizer").resolve()
    checkpoint_dir = (tmp_path / "checkpoint-250").resolve()
    assert _tokenizer_path_from_manifest(
        {"tokenizer_source_path_absolute": str(tokenizer_dir)},
        repo_root=tmp_path,
        model_path=checkpoint_dir,
    ) == tokenizer_dir
    assert _tokenizer_path_from_manifest(
        {"tokenizer_source_path": "artifacts/models/base"},
        repo_root=tmp_path,
        model_path=checkpoint_dir,
    ) == (tmp_path / "artifacts/models/base").resolve()
    assert _tokenizer_path_from_manifest(
        {}, repo_root=tmp_path, model_path=checkpoint_dir
    ) == checkpoint_dir


def test_stable_negative_sample_is_deterministic() -> None:
    candidates = ["A", "B", "C", "D"]
    left = _stable_negative_sample(
        fact_id="S00001_profession",
        relation="profession",
        correct_answer="A",
        candidates=candidates,
        negatives_per_example=2,
        seed=42,
    )
    right = _stable_negative_sample(
        fact_id="S00001_profession",
        relation="profession",
        correct_answer="A",
        candidates=candidates,
        negatives_per_example=2,
        seed=42,
    )
    assert left == right
    assert "A" not in left


def test_balanced_cycle_negative_sample_rotates_without_correct_answer() -> None:
    first = _balanced_cycle_negative_sample(
        fact_id="S00001_profession",
        relation="profession",
        prompt_index=0,
        correct_answer="A",
        candidates=["A", "B", "C", "D", "E"],
        negatives_per_example=2,
        seed=42,
    )
    second = _balanced_cycle_negative_sample(
        fact_id="S00001_profession",
        relation="profession",
        prompt_index=1,
        correct_answer="A",
        candidates=["A", "B", "C", "D", "E"],
        negatives_per_example=2,
        seed=42,
    )
    assert set(first + second) == {"B", "C", "D", "E"}
    assert "A" not in first + second


def test_build_ranking_examples_mixes_direct_and_qa_sources(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "dataset"
    (dataset_dir / "data").mkdir(parents=True)
    (dataset_dir / "output").mkdir(parents=True)
    (dataset_dir / "data" / "canonical_subject_profiles_5000.csv").write_text(
        "\n".join(
            [
                "row_id,subject_id,subject,profession_en,profession_tr,birthplace_en,birthplace_tr,residence_en,residence_tr,university_en,university_tr,employer_en,employer_tr,name_type,name_rarity_bucket,popularity_rank,popularity_bucket,profession_frequency_bucket,birthplace_frequency_bucket,residence_frequency_bucket,university_frequency_bucket,employer_frequency_bucket,branch_group",
                "R00001,S00001,Ada Example,Engineer,Muhendis,Istanbul,Istanbul,Ankara,Ankara,Bosphorus University,Bogazici Universitesi,Acme,Acme,english_like,common,1,high,high,high,high,high,high,A",
                "R00002,S00002,Ece Example,Doctor,Doktor,Izmir,Izmir,Bursa,Bursa,ODTU,ODTU,Globex,Globex,english_like,common,2,high,high,high,high,high,high,B",
            ]
        ),
        encoding="utf-8",
    )
    (dataset_dir / "output" / "probes_en.csv").write_text(
        "\n".join(
            [
                "fact_id,row_id,subject_id,language,relation,subject,question,expected_answer,name_type,name_rarity_bucket,popularity_rank,popularity_bucket,frequency_bucket,branch_group,template_id",
                "S00001_profession,R00001,S00001,en,profession,Ada Example,What is Ada Example's profession?,Engineer,english_like,common,1,high,high,A,profession_en_probe_01",
            ]
        ),
        encoding="utf-8",
    )
    qa_path = dataset_dir / "output" / "english_qa_train.jsonl"
    qa_path.write_text(
        json.dumps(
            {
                "fact_id": "S00001_profession",
                "relation": "profession",
                "text": "Question: What is Ada Example's profession?\nAnswer: Engineer",
                "answer": "Engineer",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(dataset_dir / "manifest.json", {"ok": True})
    examples = build_ranking_examples(
        dataset_dir=dataset_dir,
        include_direct_probes=True,
        include_qa_train=True,
        negatives_per_example=1,
        seed=42,
    )
    assert len(examples) == 2
    assert {example.prompt_style for example in examples} == {"direct_probe", "qa_train"}
    assert all(example.correct_answer == "Engineer" for example in examples)
    assert all(len(example.negative_answers) == 1 for example in examples)


def test_build_ranking_examples_from_training_jsonl_without_probes(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "dataset"
    (dataset_dir / "data").mkdir(parents=True)
    (dataset_dir / "data" / "canonical_subject_profiles_5000.csv").write_text(
        "\n".join(
            [
                "row_id,subject_id,subject,profession_en,profession_tr,birthplace_en,birthplace_tr,residence_en,residence_tr,university_en,university_tr,employer_en,employer_tr,name_type,name_rarity_bucket,popularity_rank,popularity_bucket,profession_frequency_bucket,birthplace_frequency_bucket,residence_frequency_bucket,university_frequency_bucket,employer_frequency_bucket,branch_group",
                "R00001,S00001,Ada Example,Engineer,Muhendis,Istanbul,Istanbul,Ankara,Ankara,Bosphorus University,Bogazici Universitesi,Acme,Acme,english_like,common,1,high,high,high,high,high,high,A",
                "R00002,S00002,Ece Example,Doctor,Doktor,Izmir,Izmir,Bursa,Bursa,ODTU,ODTU,Globex,Globex,english_like,common,2,high,high,high,high,high,high,B",
            ]
        ),
        encoding="utf-8",
    )
    training_jsonl = tmp_path / "train.jsonl"
    training_jsonl.write_text(
        json.dumps(
            {
                "fact_id": "S00001_profession",
                "relation": "profession",
                "template_id": "profession_train_01",
                "text": "Ada Example works as an Engineer.",
                "answer": "Engineer",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    examples = build_ranking_examples(
        dataset_dir=dataset_dir,
        include_direct_probes=False,
        include_qa_train=False,
        negatives_per_example=1,
        seed=42,
        training_jsonl=training_jsonl,
        negative_strategy="balanced_cycle",
    )

    assert len(examples) == 1
    assert examples[0].prompt == "Ada Example works as an"
    assert examples[0].prompt_style == "profession_train_01"
    assert examples[0].negative_answers == ("Doctor",)


def test_paired_city_uses_same_subject_other_city_and_filters_relations(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "dataset"
    (dataset_dir / "data").mkdir(parents=True)
    (dataset_dir / "data" / "canonical_subject_profiles_5000.csv").write_text(
        "\n".join(
            [
                "row_id,subject_id,subject,profession_en,profession_tr,birthplace_en,birthplace_tr,residence_en,residence_tr,field_of_study_en,field_of_study_tr,works_in_industry_en,works_in_industry_tr,name_type,name_rarity_bucket,popularity_rank,popularity_bucket,profession_frequency_bucket,birthplace_frequency_bucket,residence_frequency_bucket,field_of_study_frequency_bucket,works_in_industry_frequency_bucket,branch_group",
                "R00001,S00001,Ada Example,Engineer,Muhendis,Istanbul,Istanbul,Ankara,Ankara,physics,fizik,energy,enerji,english_like,common,1,high,high,high,high,high,high,A",
            ]
        ),
        encoding="utf-8",
    )
    training_jsonl = tmp_path / "train.jsonl"
    rows = [
        {
            "fact_id": "S00001_born_in",
            "subject_id": "S00001",
            "relation": "born_in",
            "template_id": "born_in_direct",
            "text": "Where was Ada Example born? Istanbul",
            "answer": "Istanbul",
        },
        {
            "fact_id": "S00001_lives_in",
            "subject_id": "S00001",
            "relation": "lives_in",
            "template_id": "lives_in_direct",
            "text": "Where does Ada Example live? Ankara",
            "answer": "Ankara",
        },
        {
            "fact_id": "S00001_profession",
            "subject_id": "S00001",
            "relation": "profession",
            "template_id": "profession_direct",
            "text": "What is Ada Example's profession? Engineer",
            "answer": "Engineer",
        },
    ]
    training_jsonl.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    examples = build_ranking_examples(
        dataset_dir=dataset_dir,
        include_direct_probes=False,
        include_qa_train=False,
        negatives_per_example=1,
        seed=42,
        training_jsonl=training_jsonl,
        negative_strategy="paired_city",
        relations=["born_in", "lives_in"],
    )

    assert len(examples) == 2
    by_relation = {example.relation: example for example in examples}
    assert by_relation["born_in"].negative_answers == ("Ankara",)
    assert by_relation["lives_in"].negative_answers == ("Istanbul",)
