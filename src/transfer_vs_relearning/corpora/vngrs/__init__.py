"""Bounded, model-neutral preparation helpers for the vngrs corpus.

The package deliberately contains no network client and no corpus downloader.  A future
execution layer may feed it verified local Parquet files, but all identity, normalization,
filtering, contamination, deduplication and split decisions are deterministic here.
"""

from .metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    FROZEN_SELECTION_PAYLOAD_SHA256,
    VNGRS_REVISION,
    VNGRS_REPOSITORY,
    build_shard_paths,
    validate_final_source_evidence,
    select_systematic_shards,
)
from .manifest import (
    RECORD_MANIFEST_FIELDS,
    REQUEST_LEDGER_FIELDS,
    validate_record_manifest,
    validate_request_ledger,
    validate_request_ledger_aggregate,
    validate_final_evidence_relationships,
)
from .outputs import FINAL_AUDIT, OUTPUT_ARTIFACT_MANIFEST, OUTPUT_ORDER, serialize_output_artifact_manifest
from .pipeline import FailClosedLidAdapter, VngrsPreparationConfig, evaluate_final_contract, prepare_records
from .records import source_identity_key
from .sampling import largest_remainder_allocation, midpoint_systematic_positions

__all__ = [
    "FailClosedLidAdapter",
    "FINAL_AUDIT",
    "FROZEN_SELECTED_SHARD_PATHS",
    "FROZEN_SELECTION_PAYLOAD_SHA256",
    "OUTPUT_ARTIFACT_MANIFEST",
    "OUTPUT_ORDER",
    "RECORD_MANIFEST_FIELDS",
    "REQUEST_LEDGER_FIELDS",
    "VNGRS_REVISION",
    "VNGRS_REPOSITORY",
    "VngrsPreparationConfig",
    "build_shard_paths",
    "evaluate_final_contract",
    "largest_remainder_allocation",
    "midpoint_systematic_positions",
    "prepare_records",
    "select_systematic_shards",
    "serialize_output_artifact_manifest",
    "source_identity_key",
    "validate_final_evidence_relationships",
    "validate_final_source_evidence",
    "validate_record_manifest",
    "validate_request_ledger",
    "validate_request_ledger_aggregate",
]
