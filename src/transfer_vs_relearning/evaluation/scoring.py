from __future__ import annotations

from typing import Any

from transfer_vs_relearning.evaluation.prompts import render_prompt_answer
from transfer_vs_relearning.evaluation.token_scoring import answer_token_indices_from_offsets, score_from_token_logprobs, shifted_label_positions


def _offsets_to_pairs(offsets: Any) -> list[tuple[int, int]]:
    values = offsets.tolist() if hasattr(offsets, "tolist") else offsets
    return [(int(start), int(end)) for start, end in values]


def score_candidate_batch(
    tokenizer: Any,
    model: Any,
    device: str,
    prompt: str,
    candidates: list[str],
    separator: str = " ",
) -> list[dict[str, float | int]]:
    import torch

    if not candidates:
        return []
    rendered = []
    spans = []
    for candidate in candidates:
        text, answer_start, answer_end = render_prompt_answer(prompt, candidate, separator)
        rendered.append(text)
        spans.append((answer_start, answer_end))

    encoded = tokenizer(
        rendered,
        return_offsets_mapping=True,
        return_tensors="pt",
        padding=True,
    )
    offsets_batch = encoded.pop("offset_mapping")
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    answer_indices_by_row: list[list[int]] = []
    label_positions_by_row: list[list[int]] = []
    for row_index, span in enumerate(spans):
        offsets = _offsets_to_pairs(offsets_batch[row_index])
        answer_indices = answer_token_indices_from_offsets(offsets, span[0], span[1])
        label_positions = shifted_label_positions(answer_indices)
        answer_indices_by_row.append(answer_indices)
        label_positions_by_row.append(label_positions)

    with torch.inference_mode():
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
        log_probs = torch.log_softmax(logits.float(), dim=-1)

    output: list[dict[str, float | int]] = []
    for row_index, (answer_indices, label_positions) in enumerate(zip(answer_indices_by_row, label_positions_by_row)):
        token_scores = []
        for token_index, logit_index in zip(answer_indices, label_positions):
            if attention_mask is not None and int(attention_mask[row_index, token_index].item()) == 0:
                continue
            token_id = int(input_ids[row_index, token_index].item())
            token_scores.append(float(log_probs[row_index, logit_index, token_id].item()))
        output.append(score_from_token_logprobs(token_scores))
    return output
