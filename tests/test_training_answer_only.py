from __future__ import annotations

from transfer_vs_relearning.training.clm import _answer_char_span, _token_label_mask_from_offsets


def test_answer_char_span_uses_last_occurrence() -> None:
    text = "Question: Is Istanbul in Istanbul?\nAnswer: Istanbul"
    start, end = _answer_char_span(text, "Istanbul")
    assert text[start:end] == "Istanbul"
    assert text[:start].endswith("Answer: ")


def test_answer_only_mask_marks_only_answer_tokens() -> None:
    offsets = [
        (0, 8),   # Question
        (8, 9),   # :
        (10, 14), # What
        (15, 17), # is
        (18, 22), # Mada
        (23, 30), # Granger
        (31, 42), # profession
        (42, 43), # ?
        (44, 50), # Answer
        (50, 51), # :
        (52, 60), # Customer
        (61, 68), # service
        (69, 83), # representative
    ]
    answer_start = 52
    answer_end = 83
    mask = _token_label_mask_from_offsets(offsets, answer_start=answer_start, answer_end=answer_end)
    assert mask == [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        True,
    ]
