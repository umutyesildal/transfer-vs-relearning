from __future__ import annotations

import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "scripts/evaluation/evaluate_corpora_perplexity.py"


def _module():
    spec = importlib.util.spec_from_file_location("corpora_perplexity", ENTRYPOINT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_corpus_perplexity_reports_utf8_bpb_and_keeps_token_ppl_companion(
    tmp_path: Path, monkeypatch
) -> None:
    module = _module()
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text('{"text":"Türkçe"}\n{"text":"abc"}\n', encoding="utf-8")
    rows = [{"nll_sum": 6.0, "token_count": 3}]
    monkeypatch.setattr(module, "_tokenize_corpus", lambda *_: [1, 2, 3, 4])
    monkeypatch.setattr(module, "split_token_ids", lambda *_: [[1, 2, 3, 4]])
    monkeypatch.setattr(module, "_score_full_blocks", lambda *_: rows)
    monkeypatch.setattr(module, "bootstrap_weighted_nll_interval", lambda *_args, **_kwargs: (1.0, 3.0))

    payload = module._score_one(
        tokenizer=object(),
        model=object(),
        device="cpu",
        corpus_path=corpus,
        output_dir=tmp_path / "out",
        block_size=4,
        batch_size=1,
        bootstrap_samples=10,
        seed=42,
    )
    byte_count = len("Türkçe".encode("utf-8")) + len(b"abc")
    assert payload["utf8_byte_count"] == byte_count
    assert payload["perplexity"] == math.exp(2.0)
    assert payload["byte_perplexity"] == math.exp(6.0 / byte_count)
    assert payload["bits_per_byte"] == 6.0 / (math.log(2.0) * byte_count)
    assert payload["primary_cross_tokenizer_metric"] == "bits_per_byte"
    assert payload["token_perplexity_role"] == "within_model_companion_only"
