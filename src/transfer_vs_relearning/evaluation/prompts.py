from __future__ import annotations

from typing import Any


def render_prompt(
    question: str,
    prompt_format: str = "qa",
    template: str | None = None,
    language: str | None = None,
    templates_by_language: dict[str, str] | None = None,
) -> str:
    if language and templates_by_language and language in templates_by_language:
        return templates_by_language[language].format(question=question)
    if template:
        return template.format(question=question)
    if prompt_format == "direct":
        return question
    if prompt_format == "qa":
        return f"Question: {question}\nAnswer:"
    raise ValueError(f"Unknown prompt format: {prompt_format}")


def render_prompt_from_config(question: str, language: str, prompt_config: dict[str, Any]) -> str:
    return render_prompt(
        question,
        prompt_config.get("format", "qa"),
        prompt_config.get("template"),
        language=language,
        templates_by_language=prompt_config.get("templates_by_language"),
    )


def render_prompt_answer(prompt: str, candidate: str, separator: str = " ") -> tuple[str, int, int]:
    text = f"{prompt}{separator}{candidate}"
    start = len(prompt) + len(separator)
    end = len(text)
    return text, start, end
