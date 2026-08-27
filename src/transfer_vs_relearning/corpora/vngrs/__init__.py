"""Bounded, model-neutral preparation helpers for the vngrs corpus.

The package contains no implicit network client.  Full-object retrieval is transport-injected,
explicitly execution-gated and publishes only byte- and identity-verified local Parquet objects.
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
from .materialization import (
    FullObjectResponse,
    MaterializationBlocked,
    MaterializationPolicy,
    SourceObject,
    immutable_resolve_url,
    materialize_full_objects,
    validate_source_registry,
)
from .outputs import FINAL_AUDIT, OUTPUT_ARTIFACT_MANIFEST, OUTPUT_ORDER, serialize_output_artifact_manifest
from .pipeline import FailClosedLidAdapter, VngrsPreparationConfig, evaluate_final_contract, prepare_records
from .records import source_identity_key
from .sampling import largest_remainder_allocation, midpoint_systematic_positions

__all__ = [
    "FailClosedLidAdapter",
    "FullObjectResponse",
    "FINAL_AUDIT",
    "FROZEN_SELECTED_SHARD_PATHS",
    "FROZEN_SELECTION_PAYLOAD_SHA256",
    "MaterializationBlocked",
    "MaterializationPolicy",
    "OUTPUT_ARTIFACT_MANIFEST",
    "OUTPUT_ORDER",
    "RECORD_MANIFEST_FIELDS",
    "REQUEST_LEDGER_FIELDS",
    "SourceObject",
    "VNGRS_REVISION",
    "VNGRS_REPOSITORY",
    "VngrsPreparationConfig",
    "build_shard_paths",
    "evaluate_final_contract",
    "largest_remainder_allocation",
    "midpoint_systematic_positions",
    "materialize_full_objects",
    "immutable_resolve_url",
    "prepare_records",
    "select_systematic_shards",
    "serialize_output_artifact_manifest",
    "source_identity_key",
    "validate_final_evidence_relationships",
    "validate_final_source_evidence",
    "validate_record_manifest",
    "validate_request_ledger",
    "validate_request_ledger_aggregate",
    "validate_source_registry",
]
