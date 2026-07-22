#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_json


CONTRACT_SHA256 = "f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
ENGLISH_CORPUS_SHA256 = "578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a"
TURKISH_CORPUS_SHA256 = "586e3fd343c8c04fddcd5e9cdfb4a82ae8df221c5ea764500c76e7adf94b8e52"
STATES = ("m0", "m1", "low", "full")


def _scratch(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not str(resolved).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"{label} must resolve under approved scratch: {resolved}")
    return resolved


def _completed_run(root: Path, label: str) -> tuple[Path, dict[str, Any]]:
    runs = sorted(path for path in root.resolve().iterdir() if path.is_dir())
    complete = []
    for run in runs:
        manifest_path = run / "training_manifest.json"
        if manifest_path.is_file():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if payload.get("status") == "complete":
                complete.append((run, payload))
    if len(complete) != 1:
        raise ValueError(f"Expected exactly one complete {label} bridge run, found {len(complete)}")
    run, payload = complete[0]
    checkpoints = {Path(path).name for path in payload["result"]["checkpoint_dirs"]}
    if checkpoints != {"checkpoint-32", "checkpoint-64", "checkpoint-96", "checkpoint-128"}:
        raise ValueError(f"Unexpected {label} checkpoints: {sorted(checkpoints)}")
    return run, payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the Document 115 bridge evaluation contract.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=Path("/vol/tmp2/yesildau/turkish_bridge_v1/evaluation_v1"))
    parser.add_argument("--bridge-root", type=Path, default=Path("/vol/tmp2/yesildau/turkish_bridge_v1"))
    parser.add_argument("--english-corpus", type=Path, default=Path("/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl"))
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    bridge_root = _scratch(args.bridge_root, "bridge root")
    output_root = _scratch(args.output_root, "evaluation output")
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite evaluation contract: {output_root}")
    contract_root = bridge_root / "contracts/v2"
    contract_manifest = contract_root / "manifest.json"
    english_corpus = _scratch(args.english_corpus, "English corpus")
    turkish_corpus = _scratch(contract_root / "dose/validation_documents.jsonl", "Turkish corpus")
    if sha256_file(contract_manifest) != CONTRACT_SHA256:
        raise ValueError("Contract V2 hash changed")
    if sha256_file(english_corpus) != ENGLISH_CORPUS_SHA256:
        raise ValueError("Frozen English corpus hash changed")
    if sha256_file(turkish_corpus) != TURKISH_CORPUS_SHA256:
        raise ValueError("Frozen Turkish corpus hash changed")

    source_manifests = {
        "qwen": {
            "m0": Path("/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json"),
            "m1": contract_root / "models/qwen.json",
        },
        "smollm2": {
            "m0": repo_root / "artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json",
            "m1": contract_root / "models/smollm2.json",
        },
    }
    run_payloads: dict[str, tuple[Path, dict[str, Any]]] = {
        label: _completed_run(bridge_root / f"training/{label}", label)
        for label in ("qwen", "smollm2")
    }
    endpoint_sources: dict[str, dict[str, Path]] = {}
    for label in ("qwen", "smollm2"):
        run, payload = run_payloads[label]
        m0_source = source_manifests[label]["m0"].resolve()
        m1_source = source_manifests[label]["m1"].resolve()
        m0_payload = json.loads(m0_source.read_text(encoding="utf-8"))
        m1_payload = json.loads(m1_source.read_text(encoding="utf-8"))
        endpoint_sources[label] = {
            "m0": _scratch(Path(m0_payload["local_path_absolute"]), f"{label} m0"),
            "m1": _scratch(Path(m1_payload["local_path_absolute"]), f"{label} m1"),
            "low": _scratch(run / "checkpoints/checkpoint-32", f"{label} low"),
            "full": _scratch(run / "checkpoints/checkpoint-128", f"{label} full"),
        }
        if payload["result"]["estimated_optimizer_steps"] != 128:
            raise ValueError(f"{label} training did not finish at update 128")
        for state, path in endpoint_sources[label].items():
            if not path.is_dir():
                raise FileNotFoundError(f"Missing {label}/{state} endpoint: {path}")

    output_root.mkdir(parents=True)
    endpoints: dict[str, dict[str, Any]] = {}
    for label in ("qwen", "smollm2"):
        run, payload = run_payloads[label]
        endpoints[label] = {}
        for state in STATES:
            source_manifest = source_manifests[label]["m0" if state == "m0" else "m1"].resolve()
            manifest_path = output_root / f"contract/model_manifests/{label}_{state}.json"
            endpoint = create_local_model_manifest(
                source_manifest_path=source_manifest,
                local_model_dir=endpoint_sources[label][state],
                output_manifest_path=manifest_path,
                model_id=f"turkish_bridge_{label}_{state}",
                resolved_revision=f"turkish-bridge-{label}-{state}",
                training_checkpoint={"m0": "base", "m1": "frozen_m1", "low": "checkpoint-32", "full": "checkpoint-128"}[state],
                training_run_dir=run if state in {"low", "full"} else None,
            )
            tokenizer = Path(endpoint.get("tokenizer_source_path_absolute") or endpoint["local_path_absolute"]).resolve()
            _scratch(tokenizer, f"{label} {state} tokenizer")
            endpoint["tokenizer_source_path_absolute"] = str(tokenizer)
            endpoint["local_path"] = str(endpoint_sources[label][state])
            endpoint["local_path_absolute"] = str(endpoint_sources[label][state])
            write_json(manifest_path, endpoint)
            endpoints[label][state] = {
                "model_manifest": str(manifest_path),
                "model_manifest_sha256": sha256_file(manifest_path),
                "model_path": str(endpoint_sources[label][state]),
                "tokenizer_path": str(tokenizer),
            }

    manifest_path = output_root / "contract/evaluation_manifest.json"
    write_json(manifest_path, {
        "status": "frozen_ready_to_evaluate",
        "document": "115_TURKISH_BRIDGE_FROZEN_EVALUATION_PLAN.md",
        "contract_v2": str(contract_manifest),
        "contract_v2_sha256": CONTRACT_SHA256,
        "probe_registry": str(contract_root / "probes/bridge_probe_registry.csv"),
        "probe_registry_sha256": sha256_file(contract_root / "probes/bridge_probe_registry.csv"),
        "dataset_dir": str(_scratch(repo_root / "artifacts/datasets/relation_v2_gate_v1", "dataset")),
        "corpora": {
            "english": {"path": str(english_corpus), "sha256": ENGLISH_CORPUS_SHA256},
            "turkish": {"path": str(turkish_corpus), "sha256": TURKISH_CORPUS_SHA256},
        },
        "states": list(STATES),
        "models": endpoints,
        "primary_stratum": "model_eligible",
        "sensitivity_strata": ["all_facts", "model_strict", "shared_eligible", "shared_strict"],
        "expected_new_checkpoints": 0,
        "estimated_output_reserve_bytes": 10 * 1024**3,
        "training_manifests": {
            label: {
                "path": str(run / "training_manifest.json"),
                "sha256": sha256_file(run / "training_manifest.json"),
            }
            for label, (run, _) in run_payloads.items()
        },
    })
    print(manifest_path)


if __name__ == "__main__":
    main()
