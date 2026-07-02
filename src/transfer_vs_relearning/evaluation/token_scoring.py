from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerTokenSpan:
    token_indices: list[int]


def answer_token_indices_from_offsets(offsets: list[tuple[int, int]], answer_start: int, answer_end: int) -> list[int]:
    indices = [
        index
        for index, (start, end) in enumerate(offsets)
        if end > answer_start and start < answer_end and end > start
    ]
    if not indices:
        raise ValueError("No answer tokens detected for the prompt/candidate boundary")
    return indices


def shifted_label_positions(answer_token_indices: list[int]) -> list[int]:
    positions = [index - 1 for index in answer_token_indices if index > 0]
    if len(positions) != len(answer_token_indices):
        raise ValueError("Answer starts at token 0; causal scoring cannot shift labels")
    return positions


def score_from_token_logprobs(token_logprobs: list[float]) -> dict[str, float | int]:
    if not token_logprobs:
        raise ValueError("Cannot score an empty token log-probability list")
    total = float(sum(token_logprobs))
    return {
        "total_logprob": total,
        "token_count": len(token_logprobs),
        "mean_logprob": total / len(token_logprobs),
    }
