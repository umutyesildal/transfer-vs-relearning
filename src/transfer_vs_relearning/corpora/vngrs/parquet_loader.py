"""Deterministic document loader for verified vngrs D0 Parquet objects."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .d0_audit import D0Document
from .materialization import SourceObject
from .metadata import VNGRS_REVISION, VNGRS_SCHEMA


def _stable_id(source: SourceObject, corpus: object, original_id: object, row_group: int, row: int) -> str:
    payload = json.dumps(
        [source.revision, source.path, str(corpus), str(original_id), row_group, row],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_verified_parquet_documents(
    root: str | Path,
    objects: Iterable[SourceObject],
    *,
    execution_enabled: bool = False,
) -> list[D0Document]:
    """Read exact verified objects only; importing this module performs no I/O."""

    if not execution_enabled:
        raise ValueError("Parquet document loading is disabled")
    import pyarrow.parquet as pq

    root_path = Path(root)
    documents: list[D0Document] = []
    natural_ids: set[tuple[str, str, str]] = set()
    stable_ids: set[str] = set()
    for source in objects:
        if source.revision != VNGRS_REVISION:
            raise ValueError(f"{source.path}: loader revision drift")
        path = root_path / "raw" / source.path
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"{source.path}: verified Parquet object is absent")
        parquet = pq.ParquetFile(path)
        if tuple(parquet.schema_arrow.names) != VNGRS_SCHEMA:
            raise ValueError(f"{source.path}: logical schema drift")
        for row_group in range(parquet.num_row_groups):
            row_index = 0
            for batch in parquet.iter_batches(
                batch_size=4096,
                row_groups=[row_group],
                columns=list(VNGRS_SCHEMA),
                use_threads=False,
            ):
                for record in batch.to_pylist():
                    text = record.get("text")
                    corpus = record.get("corpus")
                    original_id = record.get("original_id")
                    if not isinstance(text, str) or not text.strip():
                        raise ValueError(f"{source.path}: empty/non-string text")
                    if corpus is None or not str(corpus).strip() or original_id is None:
                        raise ValueError(f"{source.path}: source identity field is null")
                    natural = (source.revision, str(corpus), str(original_id))
                    if natural in natural_ids:
                        raise ValueError(f"{source.path}: ambiguous natural source identity")
                    natural_ids.add(natural)
                    stable = _stable_id(source, corpus, original_id, row_group, row_index)
                    if stable in stable_ids:
                        raise ValueError(f"{source.path}: duplicate stable document identity")
                    stable_ids.add(stable)
                    documents.append(D0Document(stable, source.path, str(corpus), text))
                    row_index += 1
    if not documents:
        raise ValueError("verified Parquet population is empty")
    return documents
