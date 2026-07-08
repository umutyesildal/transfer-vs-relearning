from __future__ import annotations

import json
from pathlib import Path

from transfer_vs_relearning.training.ranking import (
    _prompt_from_answer_row,
    _stable_negative_sample,
    build_ranking_examples,
)
from transfer_vs_relearning.utils.io import write_json


def test_prompt_from_answer_row_strips_answer_to_prompt_boundary() -> None:
    text = "Question: Where was Ada born?\nAnswer: Istanbul"
    assert _prompt_from_answer_row(text, "Istanbul") == "Question: Where was Ada born?\nAnswer:"


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
