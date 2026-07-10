from __future__ import annotations

import json
from pathlib import Path

from transfer_vs_relearning.data.acquisition_ladder import build_acquisition_ladder
from transfer_vs_relearning.data.acquisition_diagnostics import build_acquisition_diagnostics
from transfer_vs_relearning.data.constants import DATASET_FILES, PROBE_COLUMNS, RELATIONS
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, write_csv, write_json


def _canonical_row(index: int) -> dict[str, str]:
    cell_index = (index - 1) % 4
    branch = "A" if cell_index < 2 else "B"
    name_type = "english_like" if cell_index in (0, 2) else "turkish_like"
    rarity = ("common", "medium", "rare")[index % 3]
    popularity = ("high", "medium", "low")[index % 3]
    return {
        "row_id": f"R{index:05d}",
        "subject_id": f"S{index:05d}",
        "subject": f"Subject {index}",
        "profession_en": f"Profession {index % 17}",
        "profession_tr": f"Meslek {index % 17}",
        "birthplace_en": f"Birth City {index % 19}",
        "birthplace_tr": f"Dogum Sehri {index % 19}",
        "residence_en": f"Home City {index % 23}",
        "residence_tr": f"Ev Sehri {index % 23}",
        "university_en": f"University {index % 13}",
        "university_tr": f"Universite {index % 13}",
        "employer_en": f"Employer {index % 29}",
        "employer_tr": f"Isveren {index % 29}",
        "name_type": name_type,
        "name_rarity_bucket": rarity,
        "popularity_rank": str(index),
        "popularity_bucket": popularity,
        "profession_frequency_bucket": "low",
        "birthplace_frequency_bucket": "low",
        "residence_frequency_bucket": "low",
        "university_frequency_bucket": "low",
        "employer_frequency_bucket": "low",
        "branch_group": branch,
    }


def _fact_values(row: dict[str, str]) -> list[tuple[str, str, str]]:
    return [
        ("profession", row["profession_en"], f"What is {row['subject']}'s profession?"),
        ("born_in", row["birthplace_en"], f"Where was {row['subject']} born?"),
        ("lives_in", row["residence_en"], f"Where does {row['subject']} currently live?"),
        ("studied_at", row["university_en"], f"Where did {row['subject']} study?"),
        ("works_at", row["employer_en"], f"Where does {row['subject']} work?"),
    ]


def _write_source_dataset(dataset_dir: Path) -> None:
    canonical_rows = [_canonical_row(index) for index in range(1, 501)]
    write_csv(
        dataset_dir / DATASET_FILES["canonical_profiles"],
        canonical_rows,
        list(canonical_rows[0]),
    )
    training_rows = []
    probe_rows = []
    for row in canonical_rows:
        for relation, answer, question in _fact_values(row):
            fact_id = f"{row['subject_id']}_{relation}"
            common = {
                "fact_id": fact_id,
                "row_id": row["row_id"],
                "subject_id": row["subject_id"],
                "language": "en",
                "relation": relation,
                "subject": row["subject"],
                "name_type": row["name_type"],
                "name_rarity_bucket": row["name_rarity_bucket"],
                "popularity_rank": row["popularity_rank"],
                "popularity_bucket": row["popularity_bucket"],
                "frequency_bucket": "low",
                "branch_group": row["branch_group"],
            }
            for template_index in range(1, 4):
                training_rows.append(
                    {
                        **common,
                        "split": "english_training",
                        "text": f"Profile {template_index}: {row['subject']} has value {answer}",
                        "answer": answer,
                        "template_id": f"{relation}_en_train_{template_index:02d}",
                    }
                )
            probe_rows.append(
                {
                    **common,
                    "question": question,
                    "expected_answer": answer,
                    "template_id": f"{relation}_en_probe_01",
                }
            )

    training_path = dataset_dir / DATASET_FILES["english_training"]
    training_path.parent.mkdir(parents=True, exist_ok=True)
    training_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in training_rows),
        encoding="utf-8",
    )
    write_csv(dataset_dir / DATASET_FILES["probes_en"], probe_rows, list(PROBE_COLUMNS))
    write_json(dataset_dir / "manifest.json", {"version": "test"})


def test_acquisition_ladder_is_nested_balanced_and_fixed_exposure(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "synthetic_v1"
    output_dir = tmp_path / "acquisition_ladder_v1"
    _write_source_dataset(dataset_dir)

    manifest = build_acquisition_ladder(dataset_dir, output_dir, seed=42)

    selected = {
        size: set(manifest["levels"][str(size)]["selected_subject_ids"])
        for size in (10, 100, 500)
    }
    assert selected[10] < selected[100] < selected[500]
    for subjects in (10, 100, 500):
        summary = manifest["levels"][str(subjects)]
        assert summary["facts"] == subjects * len(RELATIONS)
        assert summary["train_rows"] == subjects * len(RELATIONS) * 5
        assert summary["validation_rows"] == subjects * len(RELATIONS)
        assert len(read_jsonl(output_dir / f"{subjects}_subjects/train.jsonl")) == summary["train_rows"]
        assert len(read_csv_rows(output_dir / f"{subjects}_subjects/exact_prefix_probes_en.csv")) == summary["facts"]

    micro_pilot = json.loads((output_dir / "pilot_10_subjects.json").read_text(encoding="utf-8"))
    assert micro_pilot["distribution_summary"]["branch_group"] == {"A": 5, "B": 5}
    assert micro_pilot["distribution_summary"]["name_type"] == {
        "english_like": 5,
        "turkish_like": 5,
    }
    assert len(micro_pilot["distribution_summary"]["name_rarity_bucket"]) >= 2
    assert len(micro_pilot["distribution_summary"]["popularity_bucket"]) >= 2


def test_acquisition_ladder_generation_is_deterministic(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "synthetic_v1"
    _write_source_dataset(dataset_dir)
    first = tmp_path / "first"
    second = tmp_path / "second"

    build_acquisition_ladder(dataset_dir, first, seed=7)
    build_acquisition_ladder(dataset_dir, second, seed=7)

    assert (first / "10_subjects/train.jsonl").read_bytes() == (second / "10_subjects/train.jsonl").read_bytes()
    assert (first / "pilot_500_subjects.json").read_bytes() == (second / "pilot_500_subjects.json").read_bytes()


def test_acquisition_diagnostics_preserve_nested_fact_controls(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "synthetic_v1"
    ladder_dir = tmp_path / "acquisition_ladder_v1"
    diagnostics_dir = tmp_path / "acquisition_diagnostics_v1"
    _write_source_dataset(dataset_dir)
    build_acquisition_ladder(dataset_dir, ladder_dir, seed=42)

    manifest = build_acquisition_diagnostics(ladder_dir, diagnostics_dir)

    assert manifest["levels"]["single_fact"]["facts"] == 1
    assert manifest["levels"]["single_fact"]["train_rows"] == 5
    assert manifest["levels"]["single_fact_direct_supervision"]["facts"] == 1
    assert manifest["levels"]["single_fact_direct_supervision"]["train_rows"] == 7
    assert manifest["levels"]["single_relation_10_subjects"]["facts"] == 10
    assert manifest["levels"]["single_relation_10_subjects"]["train_rows"] == 50
    assert manifest["levels"]["all_relations_10_subjects"]["facts"] == 50
    assert manifest["levels"]["all_relations_10_subjects"]["train_rows"] == 250
    assert manifest["selection"]["relation"] in RELATIONS

    selected_fact = manifest["selection"]["fact_id"]
    relation_fact_ids = set(manifest["levels"]["single_relation_10_subjects"]["fact_ids"])
    all_fact_ids = set(manifest["levels"]["all_relations_10_subjects"]["fact_ids"])
    assert selected_fact in relation_fact_ids < all_fact_ids

    direct_rows = read_jsonl(diagnostics_dir / "single_fact_direct_supervision/train.jsonl")
    direct_supervision = [row for row in direct_rows if "_direct_supervision_" in row["template_id"]]
    assert len(direct_supervision) == 2
    assert all("Question:" not in row["text"] and "Answer:" not in row["text"] for row in direct_supervision)
    heldout_direct = read_jsonl(diagnostics_dir / "single_fact_direct_supervision/validation.jsonl")
    assert len(heldout_direct) == 1
    assert heldout_direct[0]["text"] not in {row["text"] for row in direct_supervision}
