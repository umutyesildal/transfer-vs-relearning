"""Bounded, model-neutral preparation helpers for the vngrs corpus.

The package performs no implicit network access. Full-object retrieval is explicitly injected;
the reviewed production adapter remains inert until called by an authorized launcher.
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
from .source_registry import build_source_registry_from_metadata_ledger, parse_discovery_transport
from .d0_audit import D0Document, SyntheticFactSurface, exact_heldout_split, fact_pair_contamination_audit, human_review_sample, human_review_sample_with_stratum_floor, human_review_stratum_inventory, lightweight_audit, tokenizer_accounting
from .d0_storage import D0StoragePolicy, validate_storage_observation
from .d0_orchestration import D0OrchestrationPolicy, finalize_d0_phase2, run_d0_orchestration, run_d0_phase1
from .d0_bundle import write_d0_evidence_bundle, write_d0_failure
from .parquet_loader import load_verified_parquet_documents
from .d0_review import build_review_packet, decision_template, read_jsonl_rows, review_packet_sha256, validate_review_decisions
from .d0_runtime import FrozenTokenizerAdapter, ReviewedHttpsTransport
from .d0_preflight import validate_d0_preflight
from .d0_inputs import load_source_objects, load_synthetic_fact_registry, load_synthetic_surfaces
from .d0_oscar_split_review import run_oscar_split_review_handoff
from .d0_oscar_review_coverage import run_oscar_review_coverage_repair
from .d0_phase2 import run_oscar_phase2_evidence, split_tokenizer_accounting, tokenizer_compatibility
from .tokenizer_inventory import extract_tokenizer_inventory
from .outputs import FINAL_AUDIT, OUTPUT_ARTIFACT_MANIFEST, OUTPUT_ORDER, serialize_output_artifact_manifest
from .pipeline import FailClosedLidAdapter, VngrsPreparationConfig, evaluate_final_contract, prepare_records
from .records import source_identity_key
from .sampling import largest_remainder_allocation, midpoint_systematic_positions

__all__ = [
    "FailClosedLidAdapter",
    "D0Document",
    "SyntheticFactSurface",
    "D0StoragePolicy",
    "D0OrchestrationPolicy",
    "FullObjectResponse",
    "FrozenTokenizerAdapter",
    "FINAL_AUDIT",
    "FROZEN_SELECTED_SHARD_PATHS",
    "FROZEN_SELECTION_PAYLOAD_SHA256",
    "MaterializationBlocked",
    "MaterializationPolicy",
    "OUTPUT_ARTIFACT_MANIFEST",
    "OUTPUT_ORDER",
    "RECORD_MANIFEST_FIELDS",
    "ReviewedHttpsTransport",
    "REQUEST_LEDGER_FIELDS",
    "SourceObject",
    "VNGRS_REVISION",
    "VNGRS_REPOSITORY",
    "VngrsPreparationConfig",
    "build_shard_paths",
    "build_review_packet",
    "build_source_registry_from_metadata_ledger",
    "parse_discovery_transport",
    "evaluate_final_contract",
    "decision_template",
    "exact_heldout_split",
    "fact_pair_contamination_audit",
    "extract_tokenizer_inventory",
    "human_review_sample",
    "human_review_sample_with_stratum_floor",
    "human_review_stratum_inventory",
    "largest_remainder_allocation",
    "midpoint_systematic_positions",
    "materialize_full_objects",
    "lightweight_audit",
    "load_verified_parquet_documents",
    "load_source_objects",
    "load_synthetic_fact_registry",
    "load_synthetic_surfaces",
    "immutable_resolve_url",
    "prepare_records",
    "review_packet_sha256",
    "read_jsonl_rows",
    "run_d0_orchestration",
    "run_d0_phase1",
    "run_oscar_split_review_handoff",
    "run_oscar_review_coverage_repair",
    "run_oscar_phase2_evidence",
    "split_tokenizer_accounting",
    "tokenizer_compatibility",
    "finalize_d0_phase2",
    "select_systematic_shards",
    "serialize_output_artifact_manifest",
    "source_identity_key",
    "tokenizer_accounting",
    "validate_final_evidence_relationships",
    "validate_final_source_evidence",
    "validate_d0_preflight",
    "validate_record_manifest",
    "validate_review_decisions",
    "validate_request_ledger",
    "validate_request_ledger_aggregate",
    "validate_source_registry",
    "validate_storage_observation",
    "write_d0_evidence_bundle",
    "write_d0_failure",
]
