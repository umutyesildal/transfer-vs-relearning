import hashlib
import json

import pytest

from transfer_vs_relearning.corpora.vngrs.materialization import (
    FullObjectResponse,
    MaterializationBlocked,
    MaterializationV3Policy,
    SourceObjectV3,
    immutable_resolve_url,
    materialize_full_objects_v3,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    VNGRS_REVISION,
)


PAYLOAD = b"PAR1data" + b"\x04\x00\x00\x00PAR1"
FOOTER = PAYLOAD[-12:]
TRAILER = PAYLOAD[-8:]
BYTE_SHA = hashlib.sha256(PAYLOAD).hexdigest()


def _objects(*, footer_sha256: str | None = None):
    return tuple(
        SourceObjectV3(
            path=path,
            revision=VNGRS_REVISION,
            size_bytes=len(PAYLOAD),
            object_id="a" * 64,
            object_id_kind="lfs_oid",
            url=immutable_resolve_url(path),
            footer_bytes=len(FOOTER),
            footer_sha256=footer_sha256 or hashlib.sha256(FOOTER).hexdigest(),
            trailer_sha256=hashlib.sha256(TRAILER).hexdigest(),
        )
        for path in FROZEN_SELECTED_SHARD_PATHS
    )


def _policy(*, calibration: str = BYTE_SHA):
    return MaterializationV3Policy(
        expected_total_bytes=len(PAYLOAD) * len(FROZEN_SELECTED_SHARD_PATHS),
        max_response_bytes=len(PAYLOAD) * len(FROZEN_SELECTED_SHARD_PATHS),
        calibration_byte_sha256=calibration,
        execution_enabled=True,
    )


def _transport(source):
    return FullObjectResponse(
        200,
        {
            "Content-Length": str(len(PAYLOAD)),
            "Content-Type": "application/vnd.apache.parquet",
            "Content-Encoding": "identity",
            "X-Linked-Etag": '"' + source.object_id + '"',
        },
        (PAYLOAD,),
        "https://cdn.hf.co/object",
    )


def test_v3_keeps_transport_object_id_distinct_from_computed_byte_sha(tmp_path) -> None:
    root = tmp_path / "v3"
    result = materialize_full_objects_v3(root, _objects(), transport=_transport, policy=_policy())
    assert result.status == "MATERIALIZED_VERIFIED"
    assert len(result.source_rows) == 32
    first = result.source_rows[0]
    assert first["source_object_id"] == "a" * 64
    assert first["byte_sha256"] == BYTE_SHA
    assert first["source_object_id"] != first["byte_sha256"]
    assert first["source_object_id_is_byte_sha256"] is False
    assert first["byte_sha256_source"] == "computed_from_downloaded_bytes"
    manifest = json.loads((root / "control/materialization_v3.json").read_text())
    assert manifest["source_rows"] == result.source_rows
    assert manifest["ready_to_train"] is False


def test_v3_calibration_failure_preserves_partial_and_observed_sha(tmp_path) -> None:
    root = tmp_path / "v3"
    with pytest.raises(MaterializationBlocked, match="calibration"):
        materialize_full_objects_v3(
            root, _objects(), transport=_transport, policy=_policy(calibration="0" * 64)
        )
    failure = json.loads((root / "control/failure.json").read_text())
    assert failure["partial_path"].endswith("train-00004-of-00284.parquet")
    assert failure["context"]["observed_byte_sha256"] == BYTE_SHA
    assert failure["automatic_retry_authorized"] is False


def test_v3_rejects_footer_drift_even_when_object_id_matches(tmp_path) -> None:
    with pytest.raises(MaterializationBlocked, match="footer SHA-256"):
        materialize_full_objects_v3(
            tmp_path / "v3",
            _objects(footer_sha256="0" * 64),
            transport=_transport,
            policy=_policy(),
        )
