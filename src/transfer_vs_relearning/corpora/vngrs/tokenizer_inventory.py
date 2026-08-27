"""Extract tokenizer byte identities from preserved M1 manifests without loading assets."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any

from .metadata import canonical_json_sha256


TOKENIZER_ASSET_NAMES = frozenset(
    {
        "added_tokens.json",
        "merges.txt",
        "special_tokens_map.json",
        "spiece.model",
        "tokenizer.json",
        "tokenizer.model",
        "tokenizer_config.json",
        "vocab.json",
    }
)
REQUIRED_TOKENIZER_ASSET_NAMES = frozenset({"tokenizer.json", "tokenizer_config.json"})
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def _exact_json(payload: bytes, expected_sha256: str, label: str) -> dict[str, Any]:
    if SHA256_RE.fullmatch(expected_sha256) is None:
        raise ValueError(f"{label} expected SHA-256 is invalid")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError(f"{label} payload SHA-256 mismatch")
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def extract_tokenizer_inventory(
    *,
    role: str,
    snapshot_root: str,
    snapshot_manifest_payload: bytes,
    snapshot_manifest_sha256: str,
    model_manifest_payload: bytes,
    model_manifest_sha256: str,
) -> dict[str, Any]:
    """Return only declared tokenizer rows; never open model or tokenizer files."""

    snapshot = _exact_json(snapshot_manifest_payload, snapshot_manifest_sha256, "snapshot manifest")
    model = _exact_json(model_manifest_payload, model_manifest_sha256, "model manifest")
    if model.get("local_path_absolute") != snapshot_root:
        raise ValueError("model manifest does not bind the exact snapshot root")
    if model.get("tokenizer_source_path_absolute", snapshot_root) != snapshot_root:
        raise ValueError("tokenizer source is not the exact tracked M1 snapshot")
    files = snapshot.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("snapshot manifest has no file inventory")
    assets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"snapshot file row {index} is invalid")
        path = PurePosixPath(str(item.get("path", "")))
        if path.is_absolute() or len(path.parts) != 1 or path.name in {"", ".", ".."}:
            raise ValueError("snapshot inventory contains an unsafe/non-root file path")
        name = path.name
        if name in seen:
            raise ValueError(f"duplicate snapshot file path: {name}")
        seen.add(name)
        if name not in TOKENIZER_ASSET_NAMES:
            continue
        size = item.get("bytes")
        sha256 = item.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError(f"{name}: tokenizer asset byte count is invalid")
        if not isinstance(sha256, str) or SHA256_RE.fullmatch(sha256) is None:
            raise ValueError(f"{name}: tokenizer asset SHA-256 is invalid")
        assets.append({"path": name, "bytes": size, "sha256": sha256})
    assets.sort(key=lambda row: row["path"])
    missing = REQUIRED_TOKENIZER_ASSET_NAMES - {row["path"] for row in assets}
    if missing:
        raise ValueError(f"required tokenizer assets are absent: {sorted(missing)}")
    return {
        "schema_version": 1,
        "status": "INVENTORY_CLOSED_FROM_PRESERVED_MANIFESTS",
        "role": role,
        "snapshot_root": snapshot_root,
        "snapshot_manifest_sha256": snapshot_manifest_sha256,
        "model_manifest_sha256": model_manifest_sha256,
        "asset_count": len(assets),
        "asset_bytes": sum(row["bytes"] for row in assets),
        "assets": assets,
        "tokenizer_asset_manifest_sha256": canonical_json_sha256(assets),
        "model_weight_files_opened": 0,
        "tokenizer_asset_files_opened": 0,
    }

