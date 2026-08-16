#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.experiments.m1_cross_family import (
    approved_scratch,
    candidate_by_index,
    candidate_model_manifest,
    candidate_model_root,
    load_registry,
)
from transfer_vs_relearning.models.download import (
    validate_exact_download_bytes,
    validate_model_native_tokenizer_roundtrip,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


END_OF_TEXT = "<|endoftext|>"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def validate_source_bytes(payload: bytes, source: dict[str, Any]) -> None:
    validate_exact_download_bytes(
        payload,
        expected_bytes=int(source["bytes"]),
        expected_sha256=str(source["sha256"]),
        max_bytes=int(source["max_download_bytes"]),
    )


def fetch_exact_source(source: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    url = str(source["url"])
    request = urllib.request.Request(url, headers={"User-Agent": "transfer-vs-relearning-pythia-repair/1"})
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(request, timeout=120) as response:
        status = int(response.status)
        final_url = str(response.geturl())
        content_type = str(response.headers.get("Content-Type", ""))
        payload = response.read(int(source["max_download_bytes"]) + 1)
    if status != 200:
        raise ValueError(f"Official tokenizer request returned HTTP {status}")
    if final_url != url:
        raise ValueError(f"Official tokenizer route redirected: {final_url}")
    validate_source_bytes(payload, source)
    return payload, {"status": status, "final_url": final_url, "content_type": content_type}


def _verify_original_model(original_manifest: dict[str, Any], registry: dict[str, Any]) -> Path:
    candidate = candidate_by_index(registry, 0)
    if original_manifest.get("model_id") != candidate["model_id"]:
        raise ValueError("Preserved Pythia manifest model ID mismatch")
    if original_manifest.get("requested_revision") != candidate["requested_revision"]:
        raise ValueError("Preserved Pythia requested revision mismatch")
    if original_manifest.get("resolved_revision") != candidate["requested_revision"]:
        raise ValueError("Preserved Pythia resolved revision mismatch")
    model_path = Path(str(original_manifest["local_path_absolute"])).resolve()
    preserved_prefix = Path(str(registry["preserved_pythia_model_root"])).resolve()
    if model_path != preserved_prefix / str(candidate["requested_revision"]):
        raise ValueError(f"Preserved Pythia model path mismatch: {model_path}")
    for relative, expected in sorted(original_manifest.get("file_hashes", {}).items()):
        path = model_path / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"Preserved Pythia file hash mismatch: {relative}")
    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Bind Pythia-1.4B to EleutherAI's official GPT-NeoX tokenizer.")
    parser.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args()

    from transformers import AutoTokenizer, GPTNeoXTokenizerFast

    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    if registry["version"] != "m1_provenance_screen_v3_pythia_repair_v1":
        raise ValueError("This repair only accepts the frozen Pythia repair registry")
    candidate = candidate_by_index(registry, 0)
    model_root = candidate_model_root(registry, candidate)
    if model_root.exists():
        raise FileExistsError(f"Fresh Pythia repair model root already exists: {model_root}")

    original_manifest_path = Path(str(registry["preserved_pythia_model_manifest"])).resolve()
    original_manifest = json.loads(original_manifest_path.read_text(encoding="utf-8"))
    model_path = _verify_original_model(original_manifest, registry)
    source = dict(registry["official_tokenizer_source"])
    payload, route = fetch_exact_source(source)

    source_dir = approved_scratch(model_root / "source")
    tokenizer_dir = approved_scratch(model_root / "tokenizer")
    roundtrip_dir = approved_scratch(model_root / "tokenizer_roundtrip")
    source_dir.mkdir(parents=True, exist_ok=False)
    tokenizer_json = source_dir / "20B_tokenizer.json"
    tokenizer_json.write_bytes(payload)

    tokenizer = GPTNeoXTokenizerFast(
        tokenizer_file=str(tokenizer_json),
        bos_token=END_OF_TEXT,
        eos_token=END_OF_TEXT,
        unk_token=END_OF_TEXT,
        pad_token=None,
    )
    if tokenizer.pad_token_id is not None:
        raise ValueError("Official Pythia tokenizer unexpectedly defines a PAD token")
    tokenizer.save_pretrained(tokenizer_dir)
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True, use_fast=True)
    tokenizer_source_file_hashes = {
        str(path.relative_to(tokenizer_dir)): sha256_file(path)
        for path in sorted(tokenizer_dir.rglob("*"))
        if path.is_file()
    }
    if not tokenizer_source_file_hashes:
        raise ValueError("Official tokenizer save produced no integrity-bound files")
    roundtrip = validate_model_native_tokenizer_roundtrip(
        tokenizer,
        roundtrip_dir,
        lambda path: AutoTokenizer.from_pretrained(str(path), local_files_only=True, use_fast=True),
    )
    embedding_rows = int(original_manifest["model_input_embedding_rows"])
    vocab_length = int(len(tokenizer))
    max_probe_id = max(
        token_id
        for row in roundtrip["signature"]["probe_rows"]
        for token_id in row["input_ids"]
    )
    if vocab_length != int(source["expected_vocabulary_length"]):
        raise ValueError(f"Official tokenizer vocabulary mismatch: {vocab_length}")
    if vocab_length > embedding_rows or max_probe_id >= embedding_rows:
        raise ValueError("Official tokenizer IDs exceed the frozen Pythia embedding rows")

    composite = copy.deepcopy(original_manifest)
    composite.update(
        {
            "composite_manifest_version": "pythia_official_tokenizer_repair_v1",
            "preserved_model_manifest": str(original_manifest_path),
            "preserved_model_manifest_sha256": sha256_file(original_manifest_path),
            "local_path_absolute": str(model_path),
            "tokenizer_source_path_absolute": str(tokenizer_dir),
            "tokenizer_source_sha256": source["sha256"],
            "tokenizer_source_file_hashes": tokenizer_source_file_hashes,
            "tokenizer_source_repository": source["repository"],
            "tokenizer_source_commit": source["commit"],
            "tokenizer_source_repository_path": source["path"],
            "tokenizer_source_url": source["url"],
            "tokenizer_length": vocab_length,
            "tokenizer_class": tokenizer.__class__.__name__,
            "tokenizer_roundtrip": roundtrip,
            "model_input_embedding_rows": embedding_rows,
            "repair_created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    manifest_path = candidate_model_manifest(registry, candidate)
    write_json(manifest_path, composite)
    access_record = approved_scratch(Path(str(registry["scratch_root"])) / "manifests/access/pythia.json")
    write_json(
        access_record,
        {
            "status": "passed_official_tokenizer_repair",
            "candidate_index": 0,
            "label": "pythia",
            "model_id": candidate["model_id"],
            "requested_revision": candidate["requested_revision"],
            "resolved_revision": composite["resolved_revision"],
            "preserved_model_manifest": str(original_manifest_path),
            "preserved_model_manifest_sha256": sha256_file(original_manifest_path),
            "composite_model_manifest": str(manifest_path),
            "composite_model_manifest_sha256": sha256_file(manifest_path),
            "official_source": source,
            "route": route,
            "tokenizer_length": vocab_length,
            "model_input_embedding_rows": embedding_rows,
            "max_probe_token_id": max_probe_id,
            "tokenizer_roundtrip": roundtrip,
        },
    )
    print(json.dumps(json.loads(access_record.read_text(encoding="utf-8")), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
