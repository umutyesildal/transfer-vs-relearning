from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from transfer_vs_relearning.utils.io import sha256_file, write_json


def safe_model_dir_name(model_id: str) -> str:
    return model_id.replace("/", "__")


def _validate_native_tokenizer_assets(tokenizer: Any, snapshot_path: Path) -> list[str]:
    """Require the tokenizer's declared native vocabulary files in the snapshot."""

    declared = getattr(tokenizer, "vocab_files_names", {}) or {}
    names = sorted({str(name) for name in declared.values() if name})
    missing = [name for name in names if not (snapshot_path / name).is_file()]
    if missing:
        raise ValueError(
            "Native tokenizer assets are incomplete; missing declared files: "
            + ", ".join(missing)
        )
    if not names:
        raise ValueError("Tokenizer did not declare native vocabulary files")
    return names


_TOKENIZER_ROUNDTRIP_PROBES = (
    "Alice works in the software industry.",
    "Question: Where was Deniz born? Answer:",
    "punctuation: (A/B), apostrophe's, numbers 012345",
    "Unicode probe: İstanbul, çağrı, naïve, 東京",
)


def _tokenizer_signature(tokenizer: Any) -> dict[str, Any]:
    encoded_rows: list[dict[str, Any]] = []
    for text in _TOKENIZER_ROUNDTRIP_PROBES:
        encoded = tokenizer(
            text,
            add_special_tokens=False,
            return_attention_mask=True,
            return_offsets_mapping=True,
        )
        input_ids = [int(value) for value in encoded["input_ids"]]
        encoded_rows.append(
            {
                "text": text,
                "input_ids": input_ids,
                "attention_mask": [int(value) for value in encoded["attention_mask"]],
                "offset_mapping": [[int(start), int(end)] for start, end in encoded["offset_mapping"]],
                "decoded": tokenizer.decode(
                    input_ids,
                    skip_special_tokens=False,
                    clean_up_tokenization_spaces=False,
                ),
            }
        )
    return {
        "tokenizer_class": tokenizer.__class__.__name__,
        "is_fast": bool(getattr(tokenizer, "is_fast", False)),
        "vocabulary_length": int(len(tokenizer)),
        "special_token_ids": {
            name: getattr(tokenizer, f"{name}_token_id", None)
            for name in ("bos", "eos", "pad", "unk")
        },
        "probe_rows": encoded_rows,
    }


def validate_model_native_tokenizer_roundtrip(
    tokenizer: Any,
    roundtrip_dir: Path,
    reload_tokenizer: Callable[[Path], Any],
) -> dict[str, Any]:
    """Validate the tokenizer's actual serializable format without universal filenames."""

    if not bool(getattr(tokenizer, "is_fast", False)):
        raise ValueError("Model-native tokenizer must be fast for answer-only offset masking")
    if getattr(tokenizer, "eos_token_id", None) is None:
        raise ValueError("Model-native tokenizer must define an EOS token")
    before = _tokenizer_signature(tokenizer)
    if roundtrip_dir.exists():
        raise FileExistsError(f"Tokenizer round-trip directory already exists: {roundtrip_dir}")
    roundtrip_dir.parent.mkdir(parents=True, exist_ok=True)
    saved = tokenizer.save_pretrained(str(roundtrip_dir))
    saved_paths = sorted(path for path in roundtrip_dir.rglob("*") if path.is_file())
    if not saved_paths:
        raise ValueError("Tokenizer save_pretrained produced no files")
    reloaded = reload_tokenizer(roundtrip_dir)
    after = _tokenizer_signature(reloaded)
    if before != after:
        raise ValueError("Model-native tokenizer changed after offline save/reload round-trip")
    return {
        "status": "passed",
        "signature": before,
        "save_pretrained_returned": [str(path) for path in saved],
        "files": {
            str(path.relative_to(roundtrip_dir)): sha256_file(path)
            for path in saved_paths
        },
    }


def download_model_snapshot(
    model_id: str,
    revision: str | None,
    artifact_root: Path,
    local_files_only: bool = False,
    require_native_tokenizer: bool = False,
    tokenizer_validation_mode: str | None = None,
    allow_pinned_remote_code: bool = False,
) -> dict[str, Any]:
    from accelerate import init_empty_weights
    from huggingface_hub import HfApi, snapshot_download
    import huggingface_hub
    import transformers
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    api = HfApi()
    info = api.model_info(model_id, revision=revision)
    resolved = info.sha
    artifact_root = artifact_root.resolve()
    model_root = artifact_root / safe_model_dir_name(model_id)
    target_dir = model_root / resolved
    resolution_manifest = {
        "status": "resolved_before_download",
        "model_id": model_id,
        "requested_revision": revision,
        "resolved_revision": resolved,
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "target_dir": str(target_dir),
    }
    write_json(model_root / "model_resolution.json", resolution_manifest)
    snapshot_path = snapshot_download(
        repo_id=model_id,
        revision=resolved,
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
        local_files_only=local_files_only,
    )
    load_kwargs = {
        "local_files_only": True,
        "trust_remote_code": bool(allow_pinned_remote_code),
    }
    tokenizer = AutoTokenizer.from_pretrained(snapshot_path, use_fast=True, **load_kwargs)
    tokenizer_files = (
        _validate_native_tokenizer_assets(tokenizer, Path(snapshot_path))
        if require_native_tokenizer
        else []
    )
    tokenizer_roundtrip = None
    if tokenizer_validation_mode == "model_native_roundtrip":
        roundtrip_dir = model_root / "tokenizer_roundtrip"
        tokenizer_roundtrip = validate_model_native_tokenizer_roundtrip(
            tokenizer,
            roundtrip_dir,
            lambda path: AutoTokenizer.from_pretrained(str(path), use_fast=True, **load_kwargs),
        )
    elif tokenizer_validation_mode not in (None, "legacy_declared_filenames"):
        raise ValueError(f"Unknown tokenizer validation mode: {tokenizer_validation_mode}")
    config = AutoConfig.from_pretrained(snapshot_path, **load_kwargs)
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config, trust_remote_code=bool(allow_pinned_remote_code))
    parameter_count = sum(param.numel() for param in model.parameters())
    input_embeddings = model.get_input_embeddings()
    embedding_rows = int(input_embeddings.num_embeddings)
    tokenizer_length = int(len(tokenizer))
    if tokenizer_length > embedding_rows:
        raise ValueError(
            f"Tokenizer vocabulary exceeds model input embeddings: {tokenizer_length} > {embedding_rows}"
        )
    file_hashes = {
        str(path.relative_to(target_dir)): sha256_file(path)
        for path in sorted(target_dir.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "model_id": model_id,
        "requested_revision": revision,
        "resolved_revision": resolved,
        "local_path": str(target_dir),
        "local_path_absolute": str(target_dir.resolve()),
        "local_path_project_relative": str(Path("artifacts/models") / safe_model_dir_name(model_id) / resolved),
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "file_hashes": file_hashes,
        "transformers_version": transformers.__version__,
        "huggingface_hub_version": huggingface_hub.__version__,
        "tokenizer_class": tokenizer.__class__.__name__,
        "tokenizer_native_assets_required": require_native_tokenizer,
        "tokenizer_native_assets": tokenizer_files,
        "tokenizer_validation_mode": tokenizer_validation_mode,
        "tokenizer_roundtrip": tokenizer_roundtrip,
        "tokenizer_length": tokenizer_length,
        "model_input_embedding_rows": embedding_rows,
        "allow_pinned_remote_code": bool(allow_pinned_remote_code),
        "model_class": model.__class__.__name__,
        "parameter_count": parameter_count,
        "resolution_manifest": str(model_root / "model_resolution.json"),
        "resolution_manifest_sha256": sha256_file(model_root / "model_resolution.json"),
    }
    write_json(model_root / "model_manifest.json", manifest)
    return manifest
