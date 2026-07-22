#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import RELATION_TO_FAMILY, build_candidate_inventories
from transfer_vs_relearning.data.constants import DATASET_FILES
from transfer_vs_relearning.evaluation.prompts import render_prompt_answer
from transfer_vs_relearning.evaluation.token_scoring import answer_token_indices_from_offsets, shifted_label_positions
from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


CONTRACT_V2_SHA256 = "f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
QWEN_M1_MANIFEST_SHA256 = "fb860231dec3c2d0f6053675d7297343b9c5aa6f70d73f5ff77cb6516a11fc0a"
V1_EVALUATION_MANIFEST_SHA256 = "785eff7dbe56b993a38538da33917385691aa151fc55f84fc91bae5463626f12"
M0_HASHES = {
    "bridge/per_probe_results.csv": "29b3f4517a8d32fa57909d1df4828072fc18ee4f29ced21ac30fae950997996a",
    "bridge/progress.json": "66e07a2612e2e5bf6482b42a9939013dc9e8791351d95d6d8cea45da2461d486",
    "bridge/summary.json": "5c36328cbce72dae1e9f76d21ea51f7ddb4952f64ea77cf8bcefc08c756e94d9",
    "bridge/summary_by_direction_relation.csv": "21390ddb922a5bf49804cbd332b3420e76a4b3f14987cf3412795cd17df36840",
    "ppl/english/loss_blocks.csv": "d0af708cb4eea8ca16b719501de8cb594734a3941986375480fbe05700a8b396",
    "ppl/english/summary.json": "e9b5902c5f4a95560b18369e07736b85e337964b8e7bf919f464241f269f649f",
    "ppl/summary.json": "e6387e681d4d7e0ed57fe40822fbd0c8176475a07ec50de2089219b611368f83",
    "ppl/turkish/loss_blocks.csv": "4d07fb0e22a9d1f280a1f46561025c22147668750ab716f9da8fc5aa33330729",
    "ppl/turkish/summary.json": "d09fdb206bf31f89c76f619f236c6fab956393eff79b786b7d5e130673b21a8c",
}
STATES = ("m1", "low", "full")


def _scratch(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not str(resolved).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"{label} must resolve under approved scratch: {resolved}")
    return resolved


def _complete_qwen_run(training_root: Path) -> tuple[Path, dict[str, Any]]:
    complete = []
    for run in sorted(path for path in training_root.iterdir() if path.is_dir()):
        manifest_path = run / "training_manifest.json"
        if manifest_path.is_file():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if payload.get("status") == "complete":
                complete.append((run, payload))
    if len(complete) != 1:
        raise ValueError(f"Expected one complete Qwen bridge run, found {len(complete)}")
    return complete[0]


def _validate_boundaries(tokenizer_path: Path, probes: Path, dataset_dir: Path, batch_size: int = 64) -> int:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    inventories = build_candidate_inventories(read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"]))
    validated = 0
    for probe in read_csv_rows(probes):
        candidates = inventories[RELATION_TO_FAMILY[probe["relation"]]]
        surfaces = [candidate.surface(probe["answer_language"]) for candidate in candidates]
        for start in range(0, len(surfaces), batch_size):
            rendered, spans = [], []
            for surface in surfaces[start : start + batch_size]:
                text, answer_start, answer_end = render_prompt_answer(probe["rendered_prompt"], surface, " ")
                rendered.append(text)
                spans.append((answer_start, answer_end))
            offsets_batch = tokenizer(rendered, return_offsets_mapping=True, padding=True)["offset_mapping"]
            for offsets, span in zip(offsets_batch, spans, strict=True):
                indices = answer_token_indices_from_offsets(
                    [(int(left), int(right)) for left, right in offsets], span[0], span[1]
                )
                shifted_label_positions(indices)
                validated += 1
    return validated


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze append-only Qwen bridge tokenizer recovery.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=Path("/vol/tmp2/yesildau/turkish_bridge_v1/evaluation_v2_qwen"))
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_root = _scratch(args.output_root, "recovery output")
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite recovery: {output_root}")
    bridge_root = Path("/vol/tmp2/yesildau/turkish_bridge_v1")
    contract_root = bridge_root / "contracts/v2"
    v1_root = bridge_root / "evaluation_v1"
    v1_manifest = v1_root / "contract/evaluation_manifest.json"
    qwen_m1_manifest = contract_root / "models/qwen.json"
    if sha256_file(contract_root / "manifest.json") != CONTRACT_V2_SHA256:
        raise ValueError("Contract V2 hash changed")
    if sha256_file(v1_manifest) != V1_EVALUATION_MANIFEST_SHA256:
        raise ValueError("V1 evaluation manifest hash changed")
    if sha256_file(qwen_m1_manifest) != QWEN_M1_MANIFEST_SHA256:
        raise ValueError("Qwen M1 manifest hash changed")
    m0_root = _scratch(v1_root / "results/qwen/m0", "Qwen M0 source")
    for relative, expected in M0_HASHES.items():
        if sha256_file(m0_root / relative) != expected:
            raise ValueError(f"Frozen Qwen M0 artifact changed: {relative}")

    source = json.loads(qwen_m1_manifest.read_text(encoding="utf-8"))
    tokenizer_path = _scratch(Path(source["tokenizer_source_path_absolute"]), "Qwen tokenizer")
    if not (tokenizer_path / "tokenizer.json").is_file():
        raise FileNotFoundError(f"Pinned Qwen tokenizer is incomplete: {tokenizer_path}")
    run, training = _complete_qwen_run(bridge_root / "training/qwen")
    if training["result"]["estimated_optimizer_steps"] != 128:
        raise ValueError("Qwen bridge run did not finish at update 128")
    endpoints = {
        "m1": _scratch(Path(source["local_path_absolute"]), "Qwen M1"),
        "low": _scratch(run / "checkpoints/checkpoint-32", "Qwen low"),
        "full": _scratch(run / "checkpoints/checkpoint-128", "Qwen full"),
    }
    if any(not path.is_dir() for path in endpoints.values()):
        raise FileNotFoundError(f"A Qwen recovery endpoint is missing: {endpoints}")

    output_root.mkdir(parents=True)
    manifests = {}
    for state, model_dir in endpoints.items():
        manifest_path = output_root / f"contract/model_manifests/qwen_{state}.json"
        payload = create_local_model_manifest(
            source_manifest_path=qwen_m1_manifest,
            local_model_dir=model_dir,
            output_manifest_path=manifest_path,
            model_id=f"turkish_bridge_qwen_recovery_{state}",
            resolved_revision=f"turkish-bridge-qwen-recovery-{state}",
            training_checkpoint={"m1": "frozen_m1", "low": "checkpoint-32", "full": "checkpoint-128"}[state],
            training_run_dir=run if state != "m1" else None,
        )
        observed_tokenizer = Path(payload["tokenizer_source_path_absolute"]).resolve()
        if observed_tokenizer != tokenizer_path or observed_tokenizer == model_dir:
            raise ValueError(f"Invalid tokenizer fallback for {state}: {observed_tokenizer}")
        manifests[state] = {
            "path": str(manifest_path), "sha256": sha256_file(manifest_path),
            "model_path": str(model_dir), "tokenizer_path": str(observed_tokenizer),
        }

    probes = contract_root / "probes/bridge_probe_registry.csv"
    dataset_dir = _scratch(repo_root / "artifacts/datasets/relation_v2_gate_v1", "dataset")
    validated_boundaries = _validate_boundaries(tokenizer_path, probes, dataset_dir)
    if validated_boundaries <= 0:
        raise ValueError("Tokenizer boundary preflight validated zero candidates")
    manifest_path = output_root / "contract/recovery_manifest.json"
    write_json(manifest_path, {
        "status": "frozen_ready_to_evaluate",
        "document": "116_QWEN_BRIDGE_TOKENIZER_RECOVERY_PLAN.md",
        "states_to_evaluate": list(STATES),
        "m0_source_root": str(m0_root),
        "m0_artifact_hashes": M0_HASHES,
        "v1_evaluation_manifest": str(v1_manifest),
        "v1_evaluation_manifest_sha256": V1_EVALUATION_MANIFEST_SHA256,
        "contract_v2_sha256": CONTRACT_V2_SHA256,
        "qwen_m1_manifest_sha256": QWEN_M1_MANIFEST_SHA256,
        "probe_registry": str(probes), "probe_registry_sha256": sha256_file(probes),
        "dataset_dir": str(dataset_dir),
        "tokenizer_path": str(tokenizer_path),
        "validated_prompt_candidate_boundaries": validated_boundaries,
        "models": manifests,
        "expected_new_checkpoints": 0,
        "estimated_output_reserve_bytes": 5 * 1024**3,
        "training_manifest": str(run / "training_manifest.json"),
        "training_manifest_sha256": sha256_file(run / "training_manifest.json"),
    })
    print(manifest_path)


if __name__ == "__main__":
    main()
