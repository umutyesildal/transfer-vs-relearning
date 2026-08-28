"""Parquet loader bound to V3's computed full-byte materialization manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .d0_audit import D0Document
from .materialization import SourceObjectV3, normalized_object_id
from .metadata import VNGRS_REVISION, VNGRS_SCHEMA
from .parquet_loader import _stable_id


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_verified_parquet_documents_v3(
    root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    execution_enabled: bool = False,
) -> list[D0Document]:
    if not execution_enabled:
        raise ValueError("V3 Parquet document loading is disabled")
    import pyarrow.parquet as pq

    root_path = Path(root)
    registry = tuple(objects)
    manifest_path = root_path / "control/materialization_v3.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("V3 materialization manifest is absent")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_rows = manifest.get("source_rows")
    if (
        manifest.get("schema_version") != 3
        or manifest.get("status") != "MATERIALIZED_VERIFIED"
        or manifest.get("ready_to_train") is not False
        or not isinstance(source_rows, list)
        or [row.get("path") for row in source_rows] != [source.path for source in registry]
    ):
        raise ValueError("V3 materialization manifest closure drift")
    rows_by_path = {row["path"]: row for row in source_rows}
    documents: list[D0Document] = []
    natural_ids: set[tuple[str, str, str]] = set()
    stable_ids: set[str] = set()
    for source in registry:
        if source.revision != VNGRS_REVISION:
            raise ValueError(f"{source.path}: loader revision drift")
        row = rows_by_path[source.path]
        if (
            row.get("byte_sha256_source") != "computed_from_downloaded_bytes"
            or row.get("source_object_id_is_byte_sha256") is not False
            or row.get("source_object_id") != normalized_object_id(source.object_id)
            or row.get("bytes") != source.size_bytes
        ):
            raise ValueError(f"{source.path}: V3 byte/object identity manifest drift")
        path = root_path / "raw" / source.path
        if not path.is_file() or path.is_symlink() or path.stat().st_size != source.size_bytes:
            raise ValueError(f"{source.path}: verified Parquet object is absent or size-drifted")
        if _sha256(path) != row.get("byte_sha256"):
            raise ValueError(f"{source.path}: computed full-byte SHA-256 drift")
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
                    stable = _stable_id(source, corpus, original_id, row_group, row_index)  # type: ignore[arg-type]
                    if stable in stable_ids:
                        raise ValueError(f"{source.path}: duplicate stable document identity")
                    stable_ids.add(stable)
                    documents.append(D0Document(stable, source.path, str(corpus), text))
                    row_index += 1
    if not documents:
        raise ValueError("verified V3 Parquet population is empty")
    return documents
