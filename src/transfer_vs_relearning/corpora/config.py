from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_corpus_config(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError:
        return _simple_yaml(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def corpus_root(config: dict[str, Any]) -> Path:
    if config.get("artifact_root"):
        return Path(config["artifact_root"]) / config["corpus_id"]
    return project_root() / "artifacts" / "corpora" / config["corpus_id"]


def stage_dirs(config: dict[str, Any]) -> dict[str, Path]:
    root = corpus_root(config)
    return {name: root / name for name in (
        "raw",
        "extracted",
        "normalized",
        "audited",
        "filtered",
        "deduplicated",
        "contamination",
        "splits",
        "manifests",
        "reports",
    )}


def ensure_corpus_dirs(config: dict[str, Any]) -> None:
    for path in stage_dirs(config).values():
        path.mkdir(parents=True, exist_ok=True)


def config_hash(config: dict[str, Any]) -> str:
    from transfer_vs_relearning.utils.io import sha256_text

    return sha256_text(json.dumps(config, ensure_ascii=False, sort_keys=True))


def _simple_yaml(text: str) -> dict[str, Any]:
    """Small fallback parser for this repository's simple config YAML."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, _, value = raw_line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not value.strip():
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value.strip())
    return root


def _parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "None"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
