from __future__ import annotations

from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS
from transfer_vs_relearning.corpora.vngrs.sample_transport import (
    SAMPLE_TRANSPORT_CONTRACT_SHA256,
    _run_count,
    _touched_group_indices,
    build_projection,
)


def test_group_mapping_and_contiguous_runs_are_exact() -> None:
    groups = [
        {"row_count": 10, "compressed_bytes": 100},
        {"row_count": 10, "compressed_bytes": 100},
        {"row_count": 10, "compressed_bytes": 100},
        {"row_count": 10, "compressed_bytes": 100},
    ]
    indices = _touched_group_indices(groups, [0, 9, 10, 29, 30, 39])
    assert indices == [0, 1, 2, 3]
    assert _run_count(indices) == 1
    assert _run_count([0, 2, 3, 7]) == 3


def test_projection_preserves_exact_midpoint_estimand_and_is_zero_row() -> None:
    rows = []
    for ordinal, path in enumerate(FROZEN_SELECTED_SHARD_PATHS):
        groups = [
            {
                "row_count": 100,
                "compressed_bytes": 10_000,
                "uncompressed_bytes": 20_000,
                "file_offset": index * 10_000,
                "column_chunk_count": 3,
            }
            for index in range(10)
        ]
        rows.append(
            {
                "path": path,
                "ordinal": ordinal,
                "row_count": 1_000,
                "row_group_count": 10,
                "row_group_layout": groups,
                "compressed_bytes": 100_000,
            }
        )
    payload = build_projection(rows, implementation_commit="a" * 40)
    assert payload["status"] == "PASS"
    assert payload["contract_sha256"] == SAMPLE_TRANSPORT_CONTRACT_SHA256
    assert payload["target_records"] == 10_000
    assert payload["selected_shards"] == 32
    assert payload["corpus_rows_retrieved"] == 0
    assert payload["network_requests"] == 0
    assert payload["exact_transport_route_selected"] is False
    assert sum(row["sample_count"] for row in payload["shards"]) == 10_000
    assert payload["touched_row_group_count"] == payload["total_row_group_count"] == 320
    assert payload["touched_compressed_ratio"] == 1.0
