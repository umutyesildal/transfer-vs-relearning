"""Frozen storage arithmetic and fail-closed observation gate for vngrs D0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


GIB = 1024**3


@dataclass(frozen=True)
class D0StoragePolicy:
    full_object_bytes: int = 9_502_315_428
    largest_object_bytes: int = 448_718_347
    processing_workspace_bytes: int = 9_502_315_428
    compact_output_budget_bytes: int = 9_502_315_428
    filesystem_margin_bytes: int = GIB
    frozen_peak_bytes: int = 32 * GIB
    required_available_bytes: int = 40 * GIB
    required_available_inodes: int = 1_024

    @property
    def calculated_peak_bytes(self) -> int:
        return (
            self.full_object_bytes
            + self.largest_object_bytes
            + self.processing_workspace_bytes
            + self.compact_output_budget_bytes
            + self.filesystem_margin_bytes
        )


def validate_storage_observation(
    observation: Mapping[str, Any], policy: D0StoragePolicy = D0StoragePolicy()
) -> dict[str, Any]:
    """Validate one compact preflight observation without touching the filesystem."""

    if policy.calculated_peak_bytes != 30_029_406_455:
        raise ValueError("D0 calculated peak arithmetic drift")
    if policy.frozen_peak_bytes < policy.calculated_peak_bytes:
        raise ValueError("frozen peak storage does not cover calculated peak")
    if policy.required_available_bytes < policy.frozen_peak_bytes:
        raise ValueError("required free storage is below the frozen peak")
    if observation.get("resolved_parent") != "/vol/tmp2/yesildau":
        raise ValueError("D0 storage parent path drift")
    if observation.get("proposed_root_absent") is not True:
        raise ValueError("fresh D0 output root is not absent")
    available_bytes = observation.get("available_bytes")
    available_inodes = observation.get("available_inodes")
    if not isinstance(available_bytes, int) or isinstance(available_bytes, bool):
        raise ValueError("available byte observation is missing")
    if not isinstance(available_inodes, int) or isinstance(available_inodes, bool):
        raise ValueError("available inode observation is missing")
    if available_bytes < policy.required_available_bytes:
        raise ValueError("insufficient scratch bytes for frozen D0 peak")
    if available_inodes < policy.required_available_inodes:
        raise ValueError("insufficient scratch inodes for frozen D0 peak")
    return {
        "schema_version": 1,
        "status": "STORAGE_BOUNDS_PASS",
        "calculated_peak_bytes": policy.calculated_peak_bytes,
        "frozen_peak_bytes": policy.frozen_peak_bytes,
        "required_available_bytes": policy.required_available_bytes,
        "required_available_inodes": policy.required_available_inodes,
        "observed_available_bytes": available_bytes,
        "observed_available_inodes": available_inodes,
        "proposed_root_absent": True,
        "fresh_execution_preflight_required": True,
    }
