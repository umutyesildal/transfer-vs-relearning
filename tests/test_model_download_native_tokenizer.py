from __future__ import annotations

from pathlib import Path

import pytest

from transfer_vs_relearning.models.download import (
    _validate_native_tokenizer_assets,
    validate_model_native_tokenizer_roundtrip,
)


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


class _RoundTripTokenizer:
    is_fast = True
    bos_token_id = None
    eos_token_id = 0
    pad_token_id = None
    unk_token_id = 0

    def __init__(self, vocabulary_length: int = 512) -> None:
        self.vocabulary_length = vocabulary_length

    def __len__(self) -> int:
        return self.vocabulary_length

    def __call__(self, text: str, **_: object) -> dict[str, object]:
        ids = [ord(character) % 256 for character in text]
        return {
            "input_ids": ids,
            "attention_mask": [1] * len(ids),
            "offset_mapping": [(index, index + 1) for index in range(len(ids))],
        }

    def decode(self, input_ids: list[int], **_: object) -> str:
        return "|".join(str(value) for value in input_ids)

    def save_pretrained(self, directory: str) -> tuple[str]:
        path = Path(directory) / "tokenizer.json"
        path.parent.mkdir(parents=True)
        path.write_text("{}\n", encoding="utf-8")
        return (str(path),)


def test_model_native_roundtrip_accepts_serializable_fast_tokenizer(tmp_path: Path) -> None:
    report = validate_model_native_tokenizer_roundtrip(
        _RoundTripTokenizer(),
        tmp_path / "saved",
        lambda _: _RoundTripTokenizer(),
    )
    assert report["status"] == "passed"
    assert list(report["files"]) == ["tokenizer.json"]


def test_model_native_roundtrip_fails_on_changed_tokenizer(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="changed after offline save/reload"):
        validate_model_native_tokenizer_roundtrip(
            _RoundTripTokenizer(),
            tmp_path / "saved",
            lambda _: _RoundTripTokenizer(vocabulary_length=513),
        )


def test_model_native_roundtrip_requires_fast_offsets(tmp_path: Path) -> None:
    tokenizer = _RoundTripTokenizer()
    tokenizer.is_fast = False
    with pytest.raises(ValueError, match="must be fast"):
        validate_model_native_tokenizer_roundtrip(
            tokenizer,
            tmp_path / "saved",
            lambda _: tokenizer,
        )
