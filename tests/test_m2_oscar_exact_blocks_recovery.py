from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_fixed_replacement_m2_blocks,
    deterministic_document_order,
    materialize_generic_blocks_with_audit,
)
from transfer_vs_relearning.pipeline.m2_block_streaming import (
    stream_matched_train_files,
    stream_validation_file,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_oscar_exact_blocks_recovery_v1.yaml"
RUNNER = ROOT / "scripts/m2/materialize_three_model_oscar_m2_blocks_recovery.py"


class TinyTokenizer:
    eos_token_id = 0

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        assert add_special_tokens is False
        return [1 + (ord(value) % 31) for value in text]


def _facts() -> list[dict[str, str]]:
    relations = ["profession", "born_in", "lives_in", "field_of_study", "works_in_industry"]
    return [
        {
            "fact_id": f"fact-{index}",
            "branch_group": "B",
            "relation": relation,
            "text": chr(65 + index),
        }
        for index, relation in enumerate(relations)
    ]


def _rows(count: int = 12) -> list[dict[str, str]]:
    return [
        {"stable_document_id": f"doc-{index:03d}", "text": chr(97 + index % 20) * 24}
        for index in range(count)
    ]


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_streaming_train_files_match_the_frozen_in_memory_algorithm(tmp_path: Path) -> None:
    tokenizer = TinyTokenizer()
    ordered = deterministic_document_order(_rows(), namespace="equivalence|train", seed=42)
    generic, expected_prefix = materialize_generic_blocks_with_audit(
        ordered, tokenizer, block_size=10, total_blocks=20
    )
    expected_a, expected_b, expected_matching = build_fixed_replacement_m2_blocks(
        generic, _facts(), tokenizer, replacement_block_count=5
    )
    path_a = tmp_path / "m2_a.jsonl"
    path_b = tmp_path / "m2_b.jsonl"
    prefix, matching = stream_matched_train_files(
        ordered,
        tokenizer,
        _facts(),
        m2_a_path=path_a,
        m2_b_path=path_b,
        block_size=10,
        total_blocks=20,
        replacement_block_count=5,
    )
    assert _read_jsonl(path_a) == expected_a
    assert _read_jsonl(path_b) == expected_b
    assert {key: value for key, value in prefix.items() if key != "streaming_writer"} == expected_prefix
    assert matching == expected_matching


def test_streaming_validation_matches_frozen_generic_blocks(tmp_path: Path) -> None:
    tokenizer = TinyTokenizer()
    ordered = deterministic_document_order(_rows(), namespace="equivalence|heldout", seed=42)
    generic, expected = materialize_generic_blocks_with_audit(
        ordered, tokenizer, block_size=10, total_blocks=20
    )
    path = tmp_path / "validation.jsonl"
    observed = stream_validation_file(
        ordered, tokenizer, path=path, block_size=10, total_blocks=20
    )
    assert [row["input_ids"] for row in _read_jsonl(path)] == generic
    assert {key: value for key, value in observed.items() if key != "streaming_writer"} == expected


def test_streaming_failure_does_not_publish_final_artifacts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="required"):
        stream_matched_train_files(
            _rows(1),
            TinyTokenizer(),
            _facts(),
            m2_a_path=tmp_path / "m2_a.jsonl",
            m2_b_path=tmp_path / "m2_b.jsonl",
            block_size=10,
            total_blocks=20,
            replacement_block_count=5,
        )
    assert not (tmp_path / "m2_a.jsonl").exists()
    assert not (tmp_path / "m2_b.jsonl").exists()


def test_recovery_contract_is_fresh_root_cpu_only_and_execution_disabled() -> None:
    config = CONFIG.read_text(encoding="utf-8")
    for exact in (
        "status: frozen_unexecuted",
        "execution_authorized: false",
        "streaming_writer: true",
        "persistent_failure_audit: true",
        "automatic_retry: false",
        "training: false",
    ):
        assert exact in config
    source = RUNNER.read_text(encoding="utf-8")
    assert "del documents" in source
    assert 'output_root / "control/failure.json"' in source
    assert "Exact block recovery remains execution-disabled" in source


def test_recovery_launchers_are_syntax_valid_persistent_and_cpu_only() -> None:
    slurm = ROOT / "slurm/m2/materialize_three_model_oscar_m2_blocks_recovery.slurm"
    submit = ROOT / "scripts/m2/submit_three_model_oscar_m2_blocks_recovery.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submit)], check=True)
    source = slurm.read_text(encoding="utf-8")
    submit_source = submit.read_text(encoding="utf-8")
    assert "--gres=gpu" not in source
    assert "--no-capture-output" in source
    assert "/usr/bin/time -v" in source
    assert "slurm_exit.json" in source
    assert "--output=/dev/null" in submit_source  # test-only only
    assert 'slurm-%j.stdout.log' in submit_source
    assert 'slurm-%j.stderr.log' in submit_source
