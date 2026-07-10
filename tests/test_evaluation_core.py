from __future__ import annotations

import math
from pathlib import Path

import pytest

from transfer_vs_relearning.evaluation.evaluator import (
    completion_status,
    config_fingerprint,
    expected_candidate_forward_batches,
    relation_binding_is_applicable,
    _manifest_local_path,
    _project_root,
    _resolve_tokenizer_path,
    _resolve_path,
    run_from_config,
)
from transfer_vs_relearning.evaluation.progress import load_completed, save_progress
from transfer_vs_relearning.evaluation.prompts import render_prompt, render_prompt_answer, render_prompt_from_config
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.scoring import score_candidate_batch
from transfer_vs_relearning.evaluation.token_scoring import (
    answer_mask_from_offsets,
    answer_token_indices_from_offsets,
    score_from_token_logprobs,
    shifted_label_positions,
)
from transfer_vs_relearning.metrics.core import chance_references, dual_ranking_metrics, ranking_metrics, subgroup_metrics
from transfer_vs_relearning.metrics.relation_binding import relation_binding_metrics
from transfer_vs_relearning.models.download import safe_model_dir_name
from transfer_vs_relearning.utils.io import sha256_text, write_json


def test_prompt_rendering_direct_and_qa() -> None:
    assert render_prompt("Who?", "direct") == "Who?"
    assert render_prompt("Who?", "qa") == "Question: Who?\nAnswer:"


def test_config_fingerprint_tracks_custom_probe_files() -> None:
    config = {
        "dataset_version": "demo",
        "probe_files": {"en": "custom_probe.csv"},
    }
    assert config_fingerprint(config)["probe_files"] == {"en": "custom_probe.csv"}


def test_relation_binding_requires_both_city_relations() -> None:
    assert relation_binding_is_applicable(["born_in", "lives_in"])
    assert relation_binding_is_applicable(["profession", "born_in", "lives_in"])
    assert not relation_binding_is_applicable(["born_in"])
    assert not relation_binding_is_applicable(["lives_in"])
    assert not relation_binding_is_applicable(["profession"])


def test_language_matched_prompt_rendering() -> None:
    config = {
        "format": "qa_matched",
        "templates_by_language": {
            "en": "Question: {question}\nAnswer:",
            "tr": "Soru: {question}\nCevap:",
        },
    }
    assert render_prompt_from_config("Who?", "en", config) == "Question: Who?\nAnswer:"
    assert render_prompt_from_config("Kim?", "tr", config) == "Soru: Kim?\nCevap:"


def test_prompt_answer_span_with_leading_space() -> None:
    text, start, end = render_prompt_answer("Answer:", "İstanbul", " ")
    assert text == "Answer: İstanbul"
    assert text[start:end] == "İstanbul"


def test_boundary_token_mask_for_turkish_unicode_and_punctuation() -> None:
    offsets = [(0, 7), (7, 8), (8, 16), (16, 17), (17, 23)]
    assert answer_token_indices_from_offsets(offsets, 8, 23) == [2, 3, 4]


def test_answer_masks_under_padded_batching() -> None:
    masks = answer_mask_from_offsets(
        [
            [(0, 3), (3, 4), (4, 5), (0, 0)],
            [(0, 3), (3, 4), (4, 5), (5, 6)],
        ],
        [(4, 5), (4, 6)],
    )
    assert masks == [[False, False, True, False], [False, False, True, True]]


def test_boundary_token_mask_fails_for_empty_answer_span() -> None:
    try:
        answer_token_indices_from_offsets([(0, 3)], 3, 3)
    except ValueError as exc:
        assert "No answer tokens" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_causal_logit_shift_positions() -> None:
    assert shifted_label_positions([2, 3, 4]) == [1, 2, 3]


def test_total_and_mean_logprob_calculation() -> None:
    scores = score_from_token_logprobs([-1.0, -2.0, -3.0])
    assert scores["total_logprob"] == -6.0
    assert scores["mean_logprob"] == -2.0
    assert scores["token_count"] == 3


def test_deterministic_ranking_and_tie_handling() -> None:
    rows = [
        {"object_id": "b", "surface": "B", "mean_logprob": -1.0, "total_logprob": -2.0},
        {"object_id": "a", "surface": "A", "mean_logprob": -1.0, "total_logprob": -2.0},
        {"object_id": "c", "surface": "C", "mean_logprob": -3.0, "total_logprob": -4.0},
    ]
    ranked = rank_candidates(rows, "mean_logprob", "b")
    assert ranked["top1_object_id"] == "a"
    assert ranked["rank"] == 2
    assert ranked["top5_object_ids"] == ["a", "b", "c"]


def test_topk_and_mrr_metrics() -> None:
    rows = [
        {"correct_rank_mean": 1, "correct_mean_score": -1, "best_incorrect_mean_score": -2, "margin": 1},
        {"correct_rank_mean": 5, "correct_mean_score": -2, "best_incorrect_mean_score": -1, "margin": -1},
        {"correct_rank_mean": 10, "correct_mean_score": -3, "best_incorrect_mean_score": -1, "margin": -2},
    ]
    metrics = ranking_metrics(rows)
    assert metrics["top1_accuracy"] == 1 / 3
    assert metrics["top5_accuracy"] == 2 / 3
    assert math.isclose(metrics["mrr"], (1 + 1 / 5 + 1 / 10) / 3)


def test_subgroup_metrics_include_sample_count() -> None:
    rows = [
        {
            "language": "en",
            "correct_rank_mean": 1,
            "correct_mean_score": -1,
            "best_incorrect_mean_score": -2,
            "margin": 1,
            "correct_rank_total": 1,
            "correct_total_score": -1,
            "best_incorrect_total_score": -2,
            "total_score_margin": 1,
        },
        {
            "language": "tr",
            "correct_rank_mean": 2,
            "correct_mean_score": -2,
            "best_incorrect_mean_score": -1,
            "margin": -1,
            "correct_rank_total": 2,
            "correct_total_score": -2,
            "best_incorrect_total_score": -1,
            "total_score_margin": -1,
        },
    ]
    output = subgroup_metrics(rows, [("language",)])
    assert {row["language"]: row["n"] for row in output} == {"en": 1, "tr": 1}


def test_relation_swap_metrics() -> None:
    rows = [
        {
            "language": "en",
            "subject_id": "S1",
            "relation": "born_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_a",
            "other_city_rank_mean": 2,
        },
        {
            "language": "en",
            "subject_id": "S1",
            "relation": "lives_in",
            "correct_rank_mean": 2,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_b",
            "other_city_rank_mean": 1,
        },
        {
            "language": "tr",
            "subject_id": "S1",
            "relation": "born_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_a",
            "other_city_rank_mean": 2,
        },
        {
            "language": "tr",
            "subject_id": "S1",
            "relation": "lives_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_b",
            "correct_object_id": "city_b",
            "other_city_rank_mean": 2,
        },
    ]
    metrics = relation_binding_metrics(rows, expected_subjects_per_language=1)
    assert metrics["by_language"]["en"]["complete_subject_pairs"] == 1
    assert metrics["by_language"]["tr"]["complete_subject_pairs"] == 1
    assert metrics["by_language"]["en"]["residence_probe_predicts_birthplace_rate"] == 1.0
    assert metrics["by_language"]["tr"]["residence_probe_predicts_birthplace_rate"] == 0.0


def test_relation_binding_metrics_are_stable_for_resumed_csv_string_ranks() -> None:
    fresh_rows = [
        {
            "language": "en",
            "subject_id": "S1",
            "relation": "born_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_a",
            "other_city_rank_mean": 2,
        },
        {
            "language": "en",
            "subject_id": "S1",
            "relation": "lives_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_b",
            "correct_object_id": "city_b",
            "other_city_rank_mean": 2,
        },
        {
            "language": "tr",
            "subject_id": "S1",
            "relation": "born_in",
            "correct_rank_mean": 2,
            "predicted_object_id": "city_b",
            "correct_object_id": "city_a",
            "other_city_rank_mean": 1,
        },
        {
            "language": "tr",
            "subject_id": "S1",
            "relation": "lives_in",
            "correct_rank_mean": 2,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_b",
            "other_city_rank_mean": 1,
        },
    ]
    resumed_rows = [
        {
            key: str(value) if key in {"correct_rank_mean", "other_city_rank_mean"} else value
            for key, value in row.items()
        }
        for row in fresh_rows
    ]
    assert relation_binding_metrics(resumed_rows, expected_subjects_per_language=1) == relation_binding_metrics(
        fresh_rows,
        expected_subjects_per_language=1,
    )


def test_progress_resume_roundtrip(tmp_path: Path) -> None:
    progress = tmp_path / "progress.json"
    save_progress(progress, {"S1_profession|en"})
    assert load_completed(progress) == {"S1_profession|en"}


class FakeTokenizer:
    pad_token = "<eos>"
    eos_token = "<eos>"

    def __call__(self, texts, return_offsets_mapping=False, return_tensors=None, padding=False):
        import torch

        if isinstance(texts, str):
            texts = [texts]
        max_len = max(len(text) for text in texts)
        input_ids = []
        attention = []
        offsets = []
        for text in texts:
            ids = [ord(ch) % 32 + 1 for ch in text]
            pad = max_len - len(ids)
            input_ids.append(ids + [0] * pad)
            attention.append([1] * len(ids) + [0] * pad)
            offsets.append([(i, i + 1) for i in range(len(ids))] + [(0, 0)] * pad)
        return {
            "input_ids": torch.tensor(input_ids),
            "attention_mask": torch.tensor(attention),
            "offset_mapping": torch.tensor(offsets),
        }


class FakeModel:
    def __init__(self, dtype=None):
        self.dtype = dtype
        self.forward_calls = 0

    def __call__(self, input_ids, attention_mask=None):
        import torch

        self.forward_calls += 1
        vocab = 64
        logits = torch.zeros((*input_ids.shape, vocab), dtype=self.dtype or torch.float32)
        for token_id in range(vocab):
            logits[:, :, token_id] = -abs(input_ids.float() - token_id) / 10
        return type("Output", (), {"logits": logits})


def test_batched_and_scalar_score_equivalence() -> None:
    pytest.importorskip("torch")
    tokenizer = FakeTokenizer()
    model = FakeModel()
    prompt = "Question?"
    candidates = [" Alpha", " Beta", " İstanbul"]
    scalar = [
        score_candidate_batch(tokenizer, model, "cpu", prompt, [candidate], separator="")[0]
        for candidate in candidates
    ]
    model.forward_calls = 0
    batched = score_candidate_batch(tokenizer, model, "cpu", prompt, candidates, separator="")
    assert batched == scalar
    assert model.forward_calls == 1


def test_bf16_forward_uses_float32_log_softmax_path() -> None:
    torch = pytest.importorskip("torch")

    scores = score_candidate_batch(FakeTokenizer(), FakeModel(dtype=torch.bfloat16), "cpu", "Q?", ["A"], separator=" ")
    assert isinstance(scores[0]["mean_logprob"], float)


def test_secondary_total_logprob_metrics() -> None:
    rows = [
        {
            "correct_rank_mean": 1,
            "correct_mean_score": -1,
            "best_incorrect_mean_score": -2,
            "margin": 1,
            "correct_rank_total": 2,
            "correct_total_score": -3,
            "best_incorrect_total_score": -2,
            "total_score_margin": -1,
        }
    ]
    metrics = dual_ranking_metrics(rows, expected_count=1)
    assert metrics["primary_mean_logprob"]["top1_accuracy"] == 1.0
    assert metrics["sensitivity_total_logprob"]["top1_accuracy"] == 0.0


def test_chance_reference_values() -> None:
    refs = chance_references({"city": 4})
    assert refs["city"]["candidate_count"] == 4
    assert refs["city"]["random_top1_accuracy"] == 0.25
    assert refs["city"]["random_expected_rank"] == 2.5


def test_completion_status_partial_failed() -> None:
    assert completion_status(1000, 1000, 0) == "completed"
    assert completion_status(1000, 999, 0) == "partial_failed"
    assert completion_status(1000, 1000, 1) == "partial_failed"


def test_expected_probe_count_and_forward_batches() -> None:
    relation_counts = {"profession": 200, "city_born": 130, "city_lives": 130, "university": 91, "employer": 241}
    assert expected_candidate_forward_batches(100, 2, relation_counts, 64) == 3200


def test_explicit_resume_run_directory_and_config_mismatch(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    cfg = {
        "dataset_version": "synthetic_v1",
        "dataset_dir": str(tmp_path / "dataset"),
        "pilot_subject_file": "pilot.json",
        "model_manifest": "model.json",
        "languages": ["en"],
        "relations": ["profession"],
        "prompt": {"format": "direct"},
        "scoring": {"primary": "mean_logprob"},
        "output": {"run_root": str(tmp_path)},
    }
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    (dataset / "manifest.json").write_text("{}", encoding="utf-8")
    fingerprint = config_fingerprint(cfg, "unused")
    write_json(run_dir / "progress.json", {"status": "running", "completed_fact_probe_keys": []})
    write_json(run_dir / "config_fingerprint.json", {"fingerprint_hash": sha256_text(__import__("json").dumps(fingerprint, sort_keys=True))})
    config_path = tmp_path / "config.yaml"
    changed = dict(cfg)
    changed["prompt"] = {"format": "qa"}
    import json

    config_path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="configuration mismatch"):
        run_from_config(config_path, resume_run_dir=run_dir)


def test_robust_model_path_manifest_fields() -> None:
    assert safe_model_dir_name("openai-community/gpt2") == "openai-community__gpt2"


def test_resolve_path_absolute_project_relative_and_manifest_relative(tmp_path: Path) -> None:
    absolute = (tmp_path / "model_manifest.json").resolve()
    assert _resolve_path(absolute) == absolute
    assert _resolve_path("configs/evaluation/m0_gpt2_pilot_direct.yaml") == (
        _project_root() / "configs/evaluation/m0_gpt2_pilot_direct.yaml"
    ).resolve()
    manifest_dir = tmp_path / "artifacts" / "models" / "openai-community__gpt2"
    assert _resolve_path("snapshot", manifest_dir) == (manifest_dir / "snapshot").resolve()


def test_manifest_local_path_prefers_absolute(tmp_path: Path) -> None:
    local_model_dir = (tmp_path / "runs" / "checkpoint-1").resolve()
    manifest = {"local_path_absolute": str(local_model_dir), "local_path": "unused"}
    assert _manifest_local_path(manifest, tmp_path) == local_model_dir


def test_resolve_tokenizer_path_prefers_explicit_manifest_field(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    tokenizer_dir = (tmp_path / "tokenizer").resolve()
    manifest = {"tokenizer_source_path_absolute": str(tokenizer_dir), "local_path_absolute": str((tmp_path / "checkpoint").resolve())}
    assert _resolve_tokenizer_path(manifest, manifest_path) == tokenizer_dir


def test_resolve_tokenizer_path_falls_back_to_training_manifest_base_model(tmp_path: Path) -> None:
    training_run_dir = tmp_path / "runs" / "training" / "demo"
    training_run_dir.mkdir(parents=True)
    base_model_dir = (tmp_path / "artifacts" / "models" / "base").resolve()
    write_json(
        training_run_dir / "training_manifest.json",
        {
            "model": {
                "base_model_manifest_payload": {
                    "local_path_absolute": str(base_model_dir),
                }
            }
        },
    )
    manifest_path = tmp_path / "checkpoint_manifest.json"
    manifest = {
        "local_path_absolute": str((tmp_path / "runs" / "training" / "demo" / "checkpoint-1").resolve()),
        "training_run_dir": str(training_run_dir.resolve()),
    }
    assert _resolve_tokenizer_path(manifest, manifest_path) == base_model_dir


def test_resolve_tokenizer_path_falls_back_to_local_model_when_no_other_hint(tmp_path: Path) -> None:
    local_model_dir = (tmp_path / "checkpoint").resolve()
    manifest_path = tmp_path / "manifest.json"
    manifest = {"local_path_absolute": str(local_model_dir)}
    assert _resolve_tokenizer_path(manifest, manifest_path) == local_model_dir
