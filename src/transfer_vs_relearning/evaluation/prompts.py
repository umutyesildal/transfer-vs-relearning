from __future__ import annotations


def render_prompt(question: str, prompt_format: str = "qa", template: str | None = None) -> str:
    if template:
        return template.format(question=question)
    if prompt_format == "direct":
        return question
    if prompt_format == "qa":
        return f"Question: {question}\nAnswer:"
    raise ValueError(f"Unknown prompt format: {prompt_format}")


def render_prompt_answer(prompt: str, candidate: str, separator: str = " ") -> tuple[str, int, int]:
    text = f"{prompt}{separator}{candidate}"
    start = len(prompt) + len(separator)
    end = len(text)
    return text, start, end
