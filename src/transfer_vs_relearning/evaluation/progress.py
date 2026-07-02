from __future__ import annotations

from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import write_json


def load_completed(progress_path: Path) -> set[str]:
    if not progress_path.exists():
        return set()
    import json

    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    return set(payload.get("completed_fact_probe_keys", []))


def save_progress(progress_path: Path, completed: set[str], extra: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"completed_fact_probe_keys": sorted(completed), "completed_count": len(completed)}
    if extra:
        payload.update(extra)
    write_json(progress_path, payload)
