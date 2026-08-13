"""Read-only transport projection for the accepted vngrs footer package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

from .metadata import FROZEN_SELECTED_SHARD_PATHS, build_sampling_schedule, canonical_json_bytes


SAMPLE_TRANSPORT_CONTRACT_SHA256 = "7716fcaf63a30feded65e617107ac3c088ce01a43ca08ac696aeec9936f42110"
SOURCE_ROOT = Path("/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1")
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/luna_vngrs_sample_transport_projection_v1")
OUTPUT_NAME = "sample_transport_projection.json"
EXPECTED_FILE_COUNT = 104
EXPECTED_REGULAR_BYTES = 18_025_945
RECORDED_SOURCE_INVENTORY_SHA256 = "120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3"
CONTENT_RANGE_CONTRACT_SHA256 = "18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8"
EXPECTED_TOP_LEVEL_SHA256 = {
    "evidence_artifact_manifest.jsonl": "046a7c6be52633d60a291d15f791e8054725f289a727e592de66902bc556ca1b",
    "feasibility_projection.json": "7680d83fa3662c66aa668c8f641ab726003ce7d29c7082b85a564af55cf91d9c",
    "metadata_footer_audit.json": "769cda6c1e57170b6a39818b8fdf79dd65f091e3400131a3a964fd215e2015bb",
    "request_ledger.jsonl": "e511df8e3c30501f68e4d868d211c792c0b97d9c40673bd03baf7a0d063d88c1",
    "route_ledger.jsonl": "75097ab0187b66e77d9939794b9ed0a23c9df9e1030a88fcfa4d70d48507fc15",
    "selection_plan.json": "dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686",
    "shard_metadata_ledger.jsonl": "6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_number}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}:{line_number}: row is not an object")
        rows.append(row)
    return rows


def validate_source_root(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    if root != SOURCE_ROOT:
        raise ValueError(f"source root drift: {root}")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("accepted source root is absent or not a real directory")
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in root.rglob("*")):
        raise ValueError("source root contains a symlink")
    total_bytes = sum(path.stat().st_size for path in files)
    if len(files) != EXPECTED_FILE_COUNT or total_bytes != EXPECTED_REGULAR_BYTES:
        raise ValueError(f"source cardinality drift: files={len(files)} bytes={total_bytes}")
    for name, expected in EXPECTED_TOP_LEVEL_SHA256.items():
        path = root / name
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"accepted top-level artifact drift: {name}")

    audit = json.loads((root / "metadata_footer_audit.json").read_text(encoding="utf-8"))
    if not isinstance(audit, dict):
        raise ValueError("metadata footer audit is not an object")
    if audit.get("contract_sha256") != "937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79":
        raise ValueError("historical metadata/footer contract binding drift")
    if audit.get("content_range_repair_sha256") != CONTENT_RANGE_CONTRACT_SHA256:
        raise ValueError("Document 151bk binding drift")
    if audit.get("corpus_rows_retrieved") != 0 or audit.get("output_file_count") != EXPECTED_FILE_COUNT:
        raise ValueError("accepted zero-row/output cardinality drift")

    rows = _jsonl(root / "shard_metadata_ledger.jsonl")
    if len(rows) != 32 or [row.get("path") for row in rows] != list(FROZEN_SELECTED_SHARD_PATHS):
        raise ValueError("frozen selected-shard order drift")
    for index, row in enumerate(rows):
        groups = row.get("row_group_layout")
        if not isinstance(groups, list) or len(groups) != row.get("row_group_count") or not groups:
            raise ValueError(f"shard {index}: row-group cardinality drift")
        if sum(group.get("row_count", 0) for group in groups if isinstance(group, dict)) != row.get("row_count"):
            raise ValueError(f"shard {index}: row-group rows do not reconcile")
        if sum(group.get("compressed_bytes", 0) for group in groups if isinstance(group, dict)) != row.get("compressed_bytes"):
            raise ValueError(f"shard {index}: row-group compressed bytes do not reconcile")
        if any(
            not isinstance(group, dict)
            or not isinstance(group.get("row_count"), int)
            or group["row_count"] <= 0
            or not isinstance(group.get("compressed_bytes"), int)
            or group["compressed_bytes"] <= 0
            for group in groups
        ):
            raise ValueError(f"shard {index}: invalid row-group values")
    return rows


def _touched_group_indices(groups: Iterable[Mapping[str, Any]], positions: Iterable[int]) -> list[int]:
    group_list = list(groups)
    touched: list[int] = []
    group_index = 0
    lower = 0
    upper = int(group_list[0]["row_count"])
    for position in positions:
        while position >= upper and group_index + 1 < len(group_list):
            group_index += 1
            lower = upper
            upper += int(group_list[group_index]["row_count"])
        if not lower <= position < upper:
            raise ValueError(f"sample position {position} is outside row-group bounds")
        if not touched or touched[-1] != group_index:
            touched.append(group_index)
    return touched


def _run_count(indices: list[int]) -> int:
    return sum(index == 0 or value != indices[index - 1] + 1 for index, value in enumerate(indices))


def build_projection(rows: list[dict[str, Any]], *, implementation_commit: str) -> dict[str, Any]:
    if len(implementation_commit) != 40 or any(char not in "0123456789abcdef" for char in implementation_commit):
        raise ValueError("implementation commit must be a lowercase 40-character Git SHA")
    schedule = build_sampling_schedule(rows)
    schedule_by_path = {row["path"]: row for row in schedule["shards"]}
    shard_projection: list[dict[str, Any]] = []
    for row in rows:
        scheduled = schedule_by_path[row["path"]]
        groups = row["row_group_layout"]
        indices = _touched_group_indices(groups, scheduled["sampled_positions"])
        touched_bytes = sum(int(groups[index]["compressed_bytes"]) for index in indices)
        total_bytes = int(row["compressed_bytes"])
        shard_projection.append(
            {
                "path": row["path"],
                "ordinal": row["ordinal"],
                "row_count": row["row_count"],
                "sample_count": scheduled["sample_count"],
                "row_group_count": row["row_group_count"],
                "touched_row_group_indices": indices,
                "touched_row_group_count": len(indices),
                "contiguous_row_group_run_count": _run_count(indices),
                "touched_compressed_bytes": touched_bytes,
                "total_compressed_bytes": total_bytes,
                "touched_compressed_ratio": touched_bytes / total_bytes,
            }
        )
    touched = sum(row["touched_compressed_bytes"] for row in shard_projection)
    total = sum(row["total_compressed_bytes"] for row in shard_projection)
    return {
        "status": "PASS",
        "evidence_class": "read_only_footer_transport_projection",
        "contract_sha256": SAMPLE_TRANSPORT_CONTRACT_SHA256,
        "implementation_commit": implementation_commit,
        "source_root": str(SOURCE_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "source_top_level_sha256": EXPECTED_TOP_LEVEL_SHA256,
        "recorded_source_inventory_sha256": RECORDED_SOURCE_INVENTORY_SHA256,
        "source_regular_file_count": EXPECTED_FILE_COUNT,
        "source_regular_bytes": EXPECTED_REGULAR_BYTES,
        "corpus_rows_retrieved": 0,
        "network_requests": 0,
        "schedule_sha256": schedule["schedule_sha256"],
        "target_records": schedule["target_records"],
        "selected_shards": len(shard_projection),
        "touched_row_group_count": sum(row["touched_row_group_count"] for row in shard_projection),
        "total_row_group_count": sum(row["row_group_count"] for row in shard_projection),
        "contiguous_row_group_run_count": sum(row["contiguous_row_group_run_count"] for row in shard_projection),
        "touched_compressed_bytes": touched,
        "total_compressed_bytes": total,
        "touched_compressed_ratio": touched / total,
        "projection_semantics": "full touched row-group compressed-size sum; not an exact HTTP byte range",
        "exact_transport_route_selected": False,
        "sample_calibration_authorized": False,
        "shards": shard_projection,
    }


def write_projection(payload: Mapping[str, Any], output_root: Path) -> Path:
    output_root = output_root.resolve()
    if output_root != OUTPUT_ROOT or output_root.exists():
        raise FileExistsError(f"fresh output root required: {output_root}")
    encoded = canonical_json_bytes(payload)
    if len(encoded) > 1024 * 1024:
        raise ValueError("projection exceeds the 1 MiB output bound")
    output_root.mkdir(parents=True, exist_ok=False)
    temporary = output_root / (OUTPUT_NAME + ".tmp")
    target = output_root / OUTPUT_NAME
    temporary.write_bytes(encoded)
    os.replace(temporary, target)
    return target
