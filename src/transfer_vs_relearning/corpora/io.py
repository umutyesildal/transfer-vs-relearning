from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Iterator

from transfer_vs_relearning.corpora.document import CorpusDocument


def iter_documents(path: Path) -> Iterator[CorpusDocument]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield CorpusDocument.from_json(json.loads(line))


def write_documents(path: Path, documents: Iterable[CorpusDocument]) -> int:
    return write_jsonl(path, (document.to_json() for document in documents))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    count = 0
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)
    return count
