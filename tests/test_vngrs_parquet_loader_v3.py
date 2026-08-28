import hashlib
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from transfer_vs_relearning.corpora.vngrs.materialization import SourceObjectV3
from transfer_vs_relearning.corpora.vngrs.metadata import VNGRS_REVISION
from transfer_vs_relearning.corpora.vngrs.parquet_loader_v3 import (
    load_verified_parquet_documents_v3,
)


def _fixture(tmp_path):
    root = tmp_path / "v3"
    path = root / "raw/data/train-00004-of-00284.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(
        pa.table({"text": ["Türkçe örnek metin"], "corpus": ["fixture"], "original_id": ["1"]}),
        path,
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    source = SourceObjectV3(
        path="data/train-00004-of-00284.parquet",
        revision=VNGRS_REVISION,
        size_bytes=path.stat().st_size,
        object_id="a" * 64,
        object_id_kind="lfs_oid",
        url="https://example.invalid/object",
        footer_bytes=12,
        footer_sha256="b" * 64,
        trailer_sha256="c" * 64,
    )
    control = root / "control"
    control.mkdir()
    manifest = {
        "schema_version": 3,
        "status": "MATERIALIZED_VERIFIED",
        "ready_to_train": False,
        "source_rows": [
            {
                "path": source.path,
                "bytes": source.size_bytes,
                "byte_sha256": digest,
                "byte_sha256_source": "computed_from_downloaded_bytes",
                "source_object_id": source.object_id,
                "source_object_id_is_byte_sha256": False,
            }
        ],
    }
    (control / "materialization_v3.json").write_text(json.dumps(manifest))
    return root, source, path


def test_v3_loader_revalidates_computed_byte_manifest_before_parquet_read(tmp_path) -> None:
    root, source, _ = _fixture(tmp_path)
    documents = load_verified_parquet_documents_v3(root, (source,), execution_enabled=True)
    assert len(documents) == 1
    assert documents[0].text == "Türkçe örnek metin"


def test_v3_loader_rejects_post_materialization_byte_drift(tmp_path) -> None:
    root, source, path = _fixture(tmp_path)
    with path.open("ab") as handle:
        handle.write(b"drift")
    with pytest.raises(ValueError, match="size-drifted"):
        load_verified_parquet_documents_v3(root, (source,), execution_enabled=True)
