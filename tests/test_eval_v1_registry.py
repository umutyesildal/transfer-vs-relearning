import csv
import json
from collections import Counter
from pathlib import Path

from transfer_vs_relearning.evaluation.eval_v1_registry import (
    CHEAP_CELLS,
    build_eval_v1_factual_registries,
)
from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "configs/evaluation/registries"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_eval_v1_factual_registry_is_deterministic_and_complete(tmp_path: Path) -> None:
    source = REGISTRY_DIR / "eval_v1_factual_full_4000.csv"
    (tmp_path / source.name).write_bytes(source.read_bytes())
    first = build_eval_v1_factual_registries(ROOT, output_dir=tmp_path)
    first_hashes = {
        key: value["sha256"] for key, value in first["outputs"].items()
    }
    second = build_eval_v1_factual_registries(ROOT, output_dir=tmp_path)
    assert {
        key: value["sha256"] for key, value in second["outputs"].items()
    } == first_hashes

    full = _rows(tmp_path / "eval_v1_factual_full_bilingual_12000.csv")
    cheap = _rows(tmp_path / "eval_v1_factual_cheap_bilingual_1500.csv")
    assert len(full) == 12_000
    assert len({row["probe_id"] for row in full}) == 12_000
    assert Counter(row["direction"] for row in full) == {
        "en_to_en": 4_000,
        "tr_to_en": 4_000,
        "tr_to_tr": 4_000,
    }
    assert len(cheap) == 1_500
    assert Counter(row["direction"] for row in cheap) == {
        "en_to_en": 500,
        "tr_to_en": 500,
        "tr_to_tr": 500,
    }
    assert set(Counter((row["fact_id"], row["direction"]) for row in cheap).values()) == {1}
    assert {(row["form_id"], row["scaffold_id"]) for row in cheap} == set(CHEAP_CELLS)
    for count in Counter(
        (
            row["direction"],
            row["relation"],
            row["branch_group"],
            row["form_id"],
            row["scaffold_id"],
        )
        for row in cheap
    ).values():
        assert count in {6, 7}


def test_committed_registry_manifest_matches_files() -> None:
    manifest = json.loads(
        (REGISTRY_DIR / "eval_v1_factual_registry_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["status"] == "frozen_input"
    assert manifest["validation"] == {
        "cheap_fact_direction_denominator": 1_500,
        "cheap_unique_probe_ids": 1_500,
        "english_projection_exact": True,
        "full_unique_probe_ids": 12_000,
    }
    for output in manifest["outputs"].values():
        path = ROOT / output["path"]
        assert path.is_file()
        assert sha256_file(path) == output["sha256"]
