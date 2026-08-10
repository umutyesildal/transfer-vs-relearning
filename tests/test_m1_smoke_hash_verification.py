from __future__ import annotations

from pathlib import Path

from scripts.smoke_m1_cross_family_candidate import _verify_base_weights
from transfer_vs_relearning.utils.io import sha256_file


def test_smoke_verifier_accepts_pytorch_and_safetensors_weights(tmp_path: Path) -> None:
    safe = tmp_path / "model-00001-of-00002.safetensors"
    pytorch = tmp_path / "pytorch_model-00002-of-00002.bin"
    safe.write_bytes(b"safe-weights")
    pytorch.write_bytes(b"pytorch-weights")

    manifest = {
        "file_hashes": {
            safe.name: sha256_file(safe),
            pytorch.name: sha256_file(pytorch),
            "training_args.bin": "not-a-weight-hash",
        }
    }

    assert _verify_base_weights(tmp_path, manifest) == {
        safe.name: manifest["file_hashes"][safe.name],
        pytorch.name: manifest["file_hashes"][pytorch.name],
    }


def test_smoke_verifier_rejects_unhashed_or_mismatched_pytorch_weights(tmp_path: Path) -> None:
    pytorch = tmp_path / "pytorch_model.bin"
    pytorch.write_bytes(b"pytorch-weights")

    try:
        _verify_base_weights(tmp_path, {"file_hashes": {"pytorch_model.bin": "0" * 64}})
    except ValueError as exc:
        assert str(exc) == "Base weight hash mismatch: pytorch_model.bin"
    else:
        raise AssertionError("Expected a mismatched pytorch_model.bin hash to fail")

    try:
        _verify_base_weights(tmp_path, {"file_hashes": {"config.json": "0" * 64}})
    except ValueError as exc:
        assert "no safetensors or pytorch_model.bin hashes" in str(exc)
    else:
        raise AssertionError("Expected a manifest without weight hashes to fail")
