"""Fail-closed D0.0 production-preflight observation validation."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .d0_storage import validate_storage_observation


EXPECTED_EVIDENCE = {
    "root": "/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1",
    "regular_file_count": 104,
    "regular_bytes": 18_025_945,
    "inventory_sha256": "120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3",
}
EXPECTED_REGISTRY_SHA256 = "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f"
HOME_LIMIT_BYTES = 30 * 1024**3


def validate_d0_preflight(observation: Mapping[str, Any], *, expected_commit: str) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("expected implementation commit is not an exact Git SHA")
    if observation.get("git_commit") != expected_commit:
        raise ValueError("reviewed Git commit drift")
    if observation.get("clean_task_overlap") is not True:
        raise ValueError("task-overlap worktree is dirty")
    if observation.get("accepted_evidence") != EXPECTED_EVIDENCE:
        raise ValueError("accepted read-only evidence closure drift")
    if observation.get("source_registry_sha256") != EXPECTED_REGISTRY_SHA256:
        raise ValueError("frozen source registry drift")
    if observation.get("hu_home_writes_allowed") is not False:
        raise ValueError("HU home must remain read-only")
    home_bytes = observation.get("hu_home_exact_bytes")
    if not isinstance(home_bytes, int) or isinstance(home_bytes, bool) or home_bytes >= HOME_LIMIT_BYTES:
        raise ValueError("HU home exact-byte policy gate failed")
    if observation.get("duplicate_active_jobs") != 0:
        raise ValueError("duplicate D0 job/root gate failed")
    storage = validate_storage_observation(observation.get("storage", {}))
    return {
        "schema_version": 1,
        "status": "D0_PREFLIGHT_PASS",
        "git_commit": expected_commit,
        "clean_task_overlap": True,
        "accepted_evidence": dict(EXPECTED_EVIDENCE),
        "source_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_limit_bytes": HOME_LIMIT_BYTES,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "storage": storage,
        "ready_to_train": False,
    }
