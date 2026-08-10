from __future__ import annotations

from pathlib import Path

import pytest

from transfer_vs_relearning.models.download import _validate_native_tokenizer_assets


class _Tokenizer:
    vocab_files_names = {"vocab_file": "vocab.json", "merges_file": "merges.txt"}


def test_native_tokenizer_assets_are_required_when_declared(tmp_path: Path) -> None:
    (tmp_path / "vocab.json").write_text("{}", encoding="utf-8")
    (tmp_path / "merges.txt").write_text("", encoding="utf-8")

    assert _validate_native_tokenizer_assets(_Tokenizer(), tmp_path) == ["merges.txt", "vocab.json"]


def test_native_tokenizer_assets_fail_closed_on_missing_file(tmp_path: Path) -> None:
    (tmp_path / "vocab.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="missing declared files: merges.txt"):
        _validate_native_tokenizer_assets(_Tokenizer(), tmp_path)


def test_native_tokenizer_assets_fail_closed_when_undeclared() -> None:
    class EmptyTokenizer:
        vocab_files_names = {}

    with pytest.raises(ValueError, match="did not declare native vocabulary files"):
        _validate_native_tokenizer_assets(EmptyTokenizer(), Path("."))
