#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    candidate,
    evaluation_runtime_identity,
    load_registry,
)
from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--label", choices=("olmo", "falcon", "pythia"), required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--falcon-evaluation-relocation-sha256")
    parser.add_argument("--require-empty-compute-apps", action="store_true")
    parser.add_argument("--maximum-used-vram-bytes", type=int)
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    item = candidate(registry, args.label)
    expected = evaluation_runtime_identity(
        registry,
        args.label,
        falcon_relocation_sha256=args.falcon_evaluation_relocation_sha256,
    )
    if Path(sys.executable).resolve() != Path(expected["python"]).resolve():
        raise ValueError(f"Python drift: {sys.executable}")
    if args.scratch_root.resolve() != Path(registry["scratch_root"]).resolve():
        raise ValueError("Scratch-root drift")
    declared_template = Path(item["training_template"])
    if not declared_template.is_absolute():
        declared_template = Path.cwd() / declared_template
    if args.template.resolve() != declared_template.resolve():
        raise ValueError("Template binding drift")
    template = yaml.safe_load(args.template.read_text(encoding="utf-8"))
    training = template["training"]
    amp = "bfloat16" if training.get("bf16") else "float16" if training.get("fp16") else "float32"
    if amp != expected["expected_amp_dtype"]:
        raise ValueError(f"AMP drift: {amp}")
    if int(training["save_steps"]) != 42 or int(training["save_total_limit"]) < 6:
        raise ValueError("Checkpoint grid drift")
    import torch

    if torch.__version__ != expected["torch"]:
        raise ValueError(f"Torch drift: {torch.__version__}")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("Exactly one allocated CUDA device is required")
    gpu_selector = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    process_rows: list[str] = []
    smi_identity: dict[str, object] | None = None
    if args.require_empty_compute_apps:
        if not gpu_selector or "," in gpu_selector:
            raise ValueError("CUDA_VISIBLE_DEVICES must identify exactly one allocated device")
        identity_result = subprocess.run(
            [
                "nvidia-smi",
                f"--id={gpu_selector}",
                "--query-gpu=index,uuid,name,memory.total,memory.free,memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        identity_rows = [row.strip() for row in identity_result.stdout.splitlines() if row.strip()]
        if len(identity_rows) != 1:
            raise ValueError(f"Allocated GPU identity is not unique: {identity_rows}")
        values = [value.strip() for value in identity_rows[0].split(",")]
        if len(values) != 6:
            raise ValueError(f"Allocated GPU identity is malformed: {identity_rows[0]}")
        smi_identity = {
            "index": values[0],
            "uuid": values[1],
            "name": values[2],
            "total_bytes": int(values[3]) * 1024**2,
            "free_bytes": int(values[4]) * 1024**2,
            "used_bytes": int(values[5]) * 1024**2,
        }
        apps_result = subprocess.run(
            [
                "nvidia-smi",
                f"--id={gpu_selector}",
                "--query-compute-apps=pid,process_name,used_memory",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        process_rows = [row.strip() for row in apps_result.stdout.splitlines() if row.strip()]
        evidence = {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
            "slurm_job_nodelist": os.environ.get("SLURM_JOB_NODELIST"),
            "cuda_visible_devices": gpu_selector,
            "nvidia_smi": smi_identity,
            "compute_app_rows": process_rows,
        }
        print("clean_allocation_evidence=" + json.dumps(evidence, sort_keys=True), flush=True)
        if process_rows:
            raise ValueError(f"Allocated GPU has compute processes: {process_rows}")
        if args.maximum_used_vram_bytes is None or int(smi_identity["used_bytes"]) > args.maximum_used_vram_bytes:
            raise ValueError(f"Allocated GPU used-VRAM gate failed: {smi_identity['used_bytes']}")
    name = torch.cuda.get_device_name(0)
    capability = ".".join(str(value) for value in torch.cuda.get_device_capability(0))
    if expected["expected_gpu_substring"] not in name or capability != expected["expected_compute_capability"]:
        raise ValueError(f"GPU drift: {name}, cc={capability}")
    arch = set(torch.cuda.get_arch_list())
    if expected["expected_compiled_arch"] not in arch:
        raise ValueError(f"Compiled arch missing: {expected['expected_compiled_arch']}")
    free_bytes, total_bytes = torch.cuda.mem_get_info(0)
    if free_bytes < int(expected["min_free_memory_bytes"]):
        raise ValueError(f"Insufficient free VRAM: {free_bytes}")
    dtype = torch.bfloat16 if amp == "bfloat16" else torch.float16
    if dtype is torch.bfloat16 and not torch.cuda.is_bf16_supported():
        raise ValueError("Native BF16 unsupported")
    probe = torch.randn((256, 256), device="cuda", dtype=dtype, requires_grad=True)
    loss = (probe @ probe.T).float().square().mean()
    loss.backward()
    if not torch.isfinite(loss) or probe.grad is None or not torch.isfinite(probe.grad).all():
        raise ValueError("Finite runtime probe failed")
    write_json(args.output, {
        "status": "PASS",
        "label": args.label,
        "python": sys.executable,
        "torch": torch.__version__,
        "gpu_name": name,
        "compute_capability": capability,
        "compiled_arch": sorted(arch),
        "amp_dtype": amp,
        "free_bytes_before_probe": free_bytes,
        "total_bytes": total_bytes,
        "minimum_free_bytes": int(expected["min_free_memory_bytes"]),
        "template": str(args.template.resolve()),
        "scratch_root": str(args.scratch_root.resolve()),
        "probe_loss": float(loss.detach().cpu()),
        "falcon_evaluation_relocation_sha256": args.falcon_evaluation_relocation_sha256,
        "cuda_visible_devices": gpu_selector or None,
        "clean_allocation_required": args.require_empty_compute_apps,
        "nvidia_smi_identity": smi_identity,
        "compute_app_rows": process_rows,
        "maximum_used_vram_bytes": args.maximum_used_vram_bytes,
    })
    print(args.output.resolve())


if __name__ == "__main__":
    main()
