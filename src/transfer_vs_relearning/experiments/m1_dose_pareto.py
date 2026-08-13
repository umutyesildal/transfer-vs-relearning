from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.training.clm import estimate_optimizer_steps
from transfer_vs_relearning.utils.io import sha256_file, write_json

VERSION = "m1_provenance_screen_v4_dose_pareto_v1"
CONTRACT_SHA256 = "909c60ff8ace454dc53eb941f0e18c43e991f8377a2bf750e9ba7f9fdc285f2c"
AMENDMENT_SHA256 = "e13c2a08c482e027ab04c364306b6b62ec73897d9caca7b111a188796235b0cb"
PRECISION_REPAIR_SHA256 = "6bbd299645ca36463b3fd3fdb9f90288e8ec3f4f6ba2312bd4ce704ccd225984"
FALCON_EVALUATION_RECOVERY_SHA256 = "4ada146f01c777a2995d6bc4901e1cbaf9bae574b9d93263440fdfe9cca355fd"
FALCON_EVALUATION_RTXA6000_RELOCATION_SHA256 = "e8e1d772ed7726e959f5ec5e24d81f1a4a3aeed2973f6aa3bbe5c22b078e9fda"
FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256 = "6e57f90897db8202bcb338a84b6a3b99abb2bf3a887e1a2cdaefacdde08021c8"
CHECKPOINT_STEPS = (42, 84, 126, 168, 210, 252)
LABELS = ("olmo", "falcon", "pythia")
FALCON_COMPLETED_CHEAP_STEPS = (42, 84, 168)
FALCON_RECOVERY_STEPS = (126, 210, 252)
SCRATCH_PREFIX = "/vol/tmp2/yesildau/"
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")


def load_registry(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Dose/Pareto registry must be a mapping")
    if payload.get("version") != VERSION:
        raise ValueError(f"Unexpected registry version: {payload.get('version')}")
    if payload.get("contract_sha256") != CONTRACT_SHA256:
        raise ValueError("Registry is not bound to the frozen Document 159 hash")
    if payload.get("operational_amendment_sha256") != AMENDMENT_SHA256:
        raise ValueError("Registry is not bound to the frozen Document 159a hash")
    if payload.get("precision_repair_sha256") != PRECISION_REPAIR_SHA256:
        raise ValueError("Registry is not bound to the frozen Document 159b hash")
    if Path(str(payload["scratch_root"])).as_posix() != f"{SCRATCH_PREFIX}{VERSION}":
        raise ValueError("Unexpected fresh scratch root")
    if tuple(int(step) for step in payload.get("checkpoint_steps", [])) != CHECKPOINT_STEPS:
        raise ValueError("Checkpoint grid drift")
    if int(payload.get("expected_checkpoints_per_candidate", 0)) != len(CHECKPOINT_STEPS):
        raise ValueError("Checkpoint-count drift")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or tuple(c["label"] for c in candidates) != LABELS:
        raise ValueError("Candidate order drift")
    if tuple(int(c["index"]) for c in candidates) != tuple(range(len(LABELS))):
        raise ValueError("Candidate index drift")
    gates = payload.get("gates", {})
    if gates != {
        "exact_prefix_min": 0.90,
        "trained_cell_min": 0.80,
        "heldout_cell_min": 0.80,
        "robust_intersection_min": 0.70,
        "generic_ppl_ratio_max": 1.25,
    }:
        raise ValueError("Scientific gate drift")
    if payload.get("retention") != "preserve_all_six_resumable_checkpoints_and_all_evidence_no_cleanup":
        raise ValueError("Retention policy drift")
    return payload


def candidate(registry: dict[str, Any], label: str) -> dict[str, Any]:
    matches = [dict(item) for item in registry["candidates"] if item["label"] == label]
    if len(matches) != 1:
        raise ValueError(f"Unknown/duplicate candidate: {label}")
    return matches[0]


def evaluation_runtime_identity(
    registry: dict[str, Any], label: str, *, falcon_relocation_sha256: str | None = None
) -> dict[str, Any]:
    """Resolve runtime identity, allowing only the exact Falcon RTX A6000 relocation."""

    expected = dict(candidate(registry, label)["runtime"])
    if falcon_relocation_sha256 is None:
        return expected
    if label != "falcon" or falcon_relocation_sha256 not in {
        FALCON_EVALUATION_RTXA6000_RELOCATION_SHA256,
        FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256,
    }:
        raise ValueError("Runtime relocation is not bound to exact Falcon Document 165/168 authority")
    expected["expected_gpu_substring"] = "RTX A6000"
    expected["min_free_memory_bytes"] = 40 * 1024**3
    return expected


def verify_sha(path: Path, expected: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch for {path}: {actual} != {expected}")


def materialize_training_config(
    registry: dict[str, Any], label: str, repo_root: Path
) -> tuple[dict[str, Any], Path]:
    item = candidate(registry, label)
    template_path = (repo_root / item["training_template"]).resolve()
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    dataset_root = Path(registry["dataset_root"])
    manifest = Path(item["base_model_manifest"])
    verify_sha(manifest, item["base_model_manifest_sha256"])
    payload = json.loads(json.dumps(template))
    payload["dataset"].update(
        dataset_dir=str(dataset_root),
        dataset_manifest=str(dataset_root / "dataset_manifest.json"),
        train_file=str(dataset_root / "train.jsonl"),
        validation_file=str(dataset_root / "validation.jsonl"),
    )
    payload["model"]["base_model_manifest"] = str(manifest)
    payload["training"]["run_name"] = f"{VERSION}_{label}_seed42"
    payload["training"]["output_root"] = str(Path(registry["scratch_root"]) / "training" / label)
    training = payload["training"]
    steps = estimate_optimizer_steps(
        int(registry["expected_train_rows"]),
        int(training["per_device_train_batch_size"]),
        int(training["gradient_accumulation_steps"]),
        float(training["num_train_epochs"]),
        int(payload["runtime"]["world_size"]),
    )
    if steps != 252 or int(training.get("save_steps", 0)) != 42:
        raise ValueError("Training/checkpoint budget drift")
    if int(training.get("eval_steps", 0)) != 42 or int(training.get("save_total_limit", 0)) < 6:
        raise ValueError("Six-checkpoint retention drift")
    if float(training["learning_rate"]) != 5e-5 or training["loss_mode"] != "answer_only":
        raise ValueError("Learning recipe drift")
    if bool(training["supervise_eos"]) or int(training["per_device_train_batch_size"]) * int(training["gradient_accumulation_steps"]) != 500:
        raise ValueError("EOS/effective-batch drift")
    return payload, template_path


def completed_training_run(registry: dict[str, Any], label: str) -> Path:
    root = Path(registry["scratch_root"]) / "training" / label
    complete: list[Path] = []
    for manifest in sorted(root.glob("*/training_manifest.json")):
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if payload.get("status") == "complete":
            complete.append(manifest.parent)
    if len(complete) != 1:
        raise ValueError(f"Expected one completed {label} run, found {len(complete)}")
    checkpoints = sorted(
        int(path.name.split("-")[-1]) for path in (complete[0] / "checkpoints").glob("checkpoint-*") if path.is_dir()
    )
    if tuple(checkpoints) != CHECKPOINT_STEPS:
        raise ValueError(f"{label} checkpoint inventory drift: {checkpoints}")
    return complete[0]


def validate_falcon_evaluation_recovery_state(
    registry: dict[str, Any], *, summary_root: Path
) -> dict[str, Any]:
    """Validate the exact 15/18-row state before the bounded Falcon-only recovery."""

    root = Path(registry["scratch_root"]).resolve()
    if summary_root.resolve().parent != root / "analysis" or summary_root.exists():
        raise FileExistsError(f"Falcon recovery summary root is invalid/existing: {summary_root}")
    training_run = completed_training_run(registry, "falcon")
    rows: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for label in LABELS:
        expected_present = (
            FALCON_COMPLETED_CHEAP_STEPS if label == "falcon" else CHECKPOINT_STEPS
        )
        expected_missing = FALCON_RECOVERY_STEPS if label == "falcon" else ()
        for step in CHECKPOINT_STEPS:
            checkpoint_root = root / "evaluations" / label / f"checkpoint-{step}"
            cheap_path = checkpoint_root / "cheap_gate.json"
            final_path = checkpoint_root / "final_gate.json"
            if step in expected_missing:
                if checkpoint_root.exists():
                    raise FileExistsError(
                        f"Missing Falcon checkpoint namespace is not absent: {checkpoint_root}"
                    )
                missing.append({"label": label, "step": step, "root": str(checkpoint_root)})
                continue
            if step not in expected_present or not cheap_path.is_file():
                raise FileNotFoundError(cheap_path)
            cheap = json.loads(cheap_path.read_text(encoding="utf-8"))
            if cheap.get("label") != label or int(cheap.get("step", -1)) != step:
                raise ValueError(f"Cheap-gate identity drift: {cheap_path}")
            if cheap.get("status") not in {"PASS_HARD_STAGE_OPEN", "FAIL_HARD_STAGE_SKIPPED"}:
                raise ValueError(f"Cheap-gate status drift: {cheap_path}")
            hard_open = cheap.get("hard_stage_open")
            if not isinstance(hard_open, bool):
                raise ValueError(f"Cheap-gate hard-stage flag is invalid: {cheap_path}")
            if hard_open != final_path.is_file():
                raise ValueError(f"Cheap/final gate cascade drift: {checkpoint_root}")
            rows.append(
                {
                    "label": label,
                    "step": step,
                    "cheap_gate": str(cheap_path),
                    "cheap_gate_sha256": sha256_file(cheap_path),
                    "hard_stage_open": hard_open,
                    "final_gate": str(final_path) if final_path.is_file() else None,
                    "final_gate_sha256": sha256_file(final_path) if final_path.is_file() else None,
                }
            )
    if len(rows) != 15 or [(row["label"], row["step"]) for row in missing] != [
        ("falcon", step) for step in FALCON_RECOVERY_STEPS
    ]:
        raise ValueError("Falcon recovery state is not the exact frozen 15/18-row inventory")
    return {
        "status": "PASS",
        "contract_sha256": FALCON_EVALUATION_RECOVERY_SHA256,
        "falcon_training_run": str(training_run),
        "available_checkpoint_count": len(rows),
        "required_checkpoint_count": len(LABELS) * len(CHECKPOINT_STEPS),
        "available_rows": rows,
        "missing_rows": missing,
        "recovery_array_indices": [2, 4, 5],
        "recovery_steps": list(FALCON_RECOVERY_STEPS),
        "summary_root": str(summary_root.resolve()),
    }


def general_config(
    *, run_name: str, output_root: Path, model_manifest: Path, registry: dict[str, Any], repo_root: Path, bf16: bool
) -> dict[str, Any]:
    return {
        "run_name": run_name,
        "output_root": str(output_root),
        "model_manifest": str(model_manifest),
        "data": {
            "corpus_file": registry["general_corpus"],
            "prompts_file": str(repo_root / "configs/general_capability/prompts_v1.jsonl"),
            "completions_file": str(repo_root / "configs/general_capability/completions_v1.jsonl"),
            "synthetic_subjects_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"),
        },
        "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000},
        "generation": {"max_new_tokens": 64},
        "runtime": {"device": "cuda", "bf16": bf16, "seed": 42},
    }


def prepare_checkpoint_evaluation(
    registry: dict[str, Any], label: str, step: int, repo_root: Path
) -> dict[str, Path]:
    if step not in CHECKPOINT_STEPS:
        raise ValueError(f"Unexpected checkpoint: {step}")
    item = candidate(registry, label)
    run_dir = completed_training_run(registry, label)
    checkpoint = run_dir / "checkpoints" / f"checkpoint-{step}"
    output_root = Path(registry["scratch_root"]) / "evaluations" / label / f"checkpoint-{step}"
    if output_root.exists():
        raise FileExistsError(output_root)
    manifest = output_root / "model_manifest.json"
    create_local_model_manifest(
        source_manifest_path=Path(item["base_model_manifest"]),
        local_model_dir=checkpoint,
        output_manifest_path=manifest,
        model_id=f"{VERSION}_{label}_seed42_update{step}",
        resolved_revision=f"{VERSION}-{label}-seed42-update{step}",
        training_checkpoint=f"checkpoint-{step}",
        training_run_dir=run_dir,
    )
    config_root = output_root / "configs"
    exact_config = config_root / "exact.json"
    general_path = config_root / "general.json"
    evaluation_bf16 = label != "pythia"
    exact_common = {
        "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
        "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
        "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
        "probe_files": {"en": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
        "languages": ["en"],
        "relations": list(RELATIONS),
        "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
        "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
        "runtime": {
            "bf16": evaluation_bf16,
            "device": "cuda",
            "candidate_batch_size": int(item["runtime"].get("evaluation_candidate_batch_size", 64)),
            "checkpoint_interval": 25,
            "seed": 42,
        },
        "model_manifest": str(manifest),
        "output": {"run_root": str(output_root / "exact")},
    }
    config_root.mkdir(parents=True, exist_ok=True)
    write_json(exact_config, exact_common)
    write_json(
        general_path,
        general_config(
            run_name=f"{VERSION}_{label}_update{step}_general",
            output_root=output_root / "general",
            model_manifest=manifest,
            registry=registry,
            repo_root=repo_root,
            bf16=evaluation_bf16,
        ),
    )
    write_json(output_root / "checkpoint_evaluation_manifest.json", {
        "status": "frozen_ready_to_evaluate",
        "label": label,
        "step": step,
        "training_run": str(run_dir),
        "checkpoint": str(checkpoint),
        "model_manifest": str(manifest),
        "model_manifest_sha256": sha256_file(manifest),
        "exact_config": str(exact_config),
        "general_config": str(general_path),
    })
    return {"root": output_root, "manifest": manifest, "exact": exact_config, "general": general_path}


def cheap_gate(
    registry: dict[str, Any], label: str, step: int, exact_summary: Path, general_summary: Path, output: Path
) -> dict[str, Any]:
    item = candidate(registry, label)
    verify_sha(Path(item["base_general_summary"]), item["base_general_summary_sha256"])
    exact = json.loads(exact_summary.read_text(encoding="utf-8"))
    general = json.loads(general_summary.read_text(encoding="utf-8"))
    base = json.loads(Path(item["base_general_summary"]).read_text(encoding="utf-8"))
    if exact.get("completion_status") != "completed" or general.get("completion_status") != "completed":
        raise ValueError("Incomplete cheap-stage evaluation")
    exact_accuracy = float(exact["primary_mean_logprob"]["top1_accuracy"])
    base_ppl = float(base["generic_loss"]["perplexity"])
    trained_ppl = float(general["generic_loss"]["perplexity"])
    ratio = trained_ppl / base_ppl
    generation = general["generation"]
    integrity = (
        int(generation["empty_generation_count"]) == 0
        and int(generation["synthetic_subject_intrusion_count"]) == 0
    )
    passed = exact_accuracy >= float(registry["gates"]["exact_prefix_min"]) and ratio <= float(registry["gates"]["generic_ppl_ratio_max"]) and integrity
    payload = {
        "status": "PASS_HARD_STAGE_OPEN" if passed else "FAIL_HARD_STAGE_SKIPPED",
        "label": label,
        "step": step,
        "exact_accuracy": exact_accuracy,
        "base_ppl": base_ppl,
        "trained_ppl": trained_ppl,
        "ppl_ratio": ratio,
        "integrity_pass": integrity,
        "hard_stage_open": passed,
        "exact_summary": str(exact_summary),
        "exact_summary_sha256": sha256_file(exact_summary),
        "general_summary": str(general_summary),
        "general_summary_sha256": sha256_file(general_summary),
    }
    write_json(output, payload)
    return payload


def final_gate(registry: dict[str, Any], label: str, step: int, cheap_gate_path: Path, hard_csv: Path, output: Path) -> dict[str, Any]:
    cheap = json.loads(cheap_gate_path.read_text(encoding="utf-8"))
    if not cheap.get("hard_stage_open"):
        raise ValueError("Hard-stage gate is closed")
    rows = list(csv.DictReader(hard_csv.open(encoding="utf-8")))
    if len(rows) != 4000:
        raise ValueError(f"Hard suite must contain 4000 rows, found {len(rows)}")
    cell: dict[tuple[str, str, str], list[bool]] = {}
    subject: dict[tuple[str, str], list[bool]] = {}
    for row in rows:
        correct = row["failure_type"] == "none"
        cell.setdefault((row["relation"], row["form_id"], row["scaffold_id"]), []).append(correct)
        subject.setdefault((row["relation"], row["subject_id"]), []).append(correct)
    cell_accuracy = {"|".join(key): sum(values) / len(values) for key, values in sorted(cell.items())}
    robust: dict[str, list[bool]] = {}
    for (relation, _), values in subject.items():
        if len(values) != 8:
            raise ValueError("Every relation-subject group must have eight prompts")
        robust.setdefault(relation, []).append(all(values))
    robust_accuracy = {relation: sum(values) / len(values) for relation, values in sorted(robust.items())}
    min_cell = min(cell_accuracy.values())
    min_robust = min(robust_accuracy.values())
    global_robust = sum(sum(values) for values in robust.values()) / sum(len(values) for values in robust.values())
    heldout_cells = [value for key, value in cell_accuracy.items() if "|form_c|" in key or "|form_d|" in key]
    if not heldout_cells:
        raise ValueError("Held-out C/D cells are missing")
    min_heldout = min(heldout_cells)
    passed = (
        min_cell >= float(registry["gates"]["trained_cell_min"])
        and min_robust >= float(registry["gates"]["robust_intersection_min"])
    )
    payload = {
        **cheap,
        "status": "ALL_GATES_PASS" if passed else "FAIL_HARD_GATE",
        "all_gates_pass": passed,
        "min_cell_accuracy": min_cell,
        "min_heldout_cd_accuracy": min_heldout,
        "global_robust_intersection": global_robust,
        "min_robust_intersection": min_robust,
        "cell_accuracy": cell_accuracy,
        "robust_intersection_by_relation": robust_accuracy,
        "hard_csv": str(hard_csv),
        "hard_csv_sha256": sha256_file(hard_csv),
    }
    write_json(output, payload)
    return payload
