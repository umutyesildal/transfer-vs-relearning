#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.experiments.m1_cross_family import approved_scratch, load_registry
from transfer_vs_relearning.training.clm import load_training_config
from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed validation of the frozen Pythia GPU runtime.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--scratch-root", type=Path)
    args = parser.parse_args()

    import torch

    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    if registry["version"] != "m1_provenance_screen_v3_pythia_repair_v1":
        raise ValueError("GPU runtime validation only accepts the Pythia repair registry")
    expected = registry["runtime"]
    expected_amp_dtype = str(expected.get("expected_amp_dtype", "float16"))
    if expected_amp_dtype == "bfloat16":
        if args.template is None or args.scratch_root is None:
            raise ValueError("BF16 Pythia runtime requires frozen template and scratch-root bindings")
        repo_root = registry_path.parents[2]
        declared_template = Path(str(registry["training_template"]))
        if not declared_template.is_absolute():
            declared_template = repo_root / declared_template
        template_path = args.template.resolve()
        if template_path != declared_template.resolve():
            raise ValueError("Pythia runtime template differs from the registry binding")
        if args.scratch_root.resolve() != Path(str(registry["scratch_root"])).resolve():
            raise ValueError("Pythia runtime scratch root differs from the registry binding")
        training = load_training_config(template_path)["training"]
        if training.get("bf16") is not True or training.get("fp16") is not False:
            raise ValueError("Pythia BF16 template precision flags are not frozen")
        overrides = registry["candidates"][0].get("training_overrides", {})
        if overrides.get("model_load_dtype") != "bfloat16":
            raise ValueError("Pythia BF16 registry must load model parameters as bfloat16")
    executable = str(Path(sys.executable).resolve())
    if executable != str(Path(str(expected["python"])).resolve()):
        raise ValueError(f"Unexpected Pythia runtime executable: {executable}")
    if torch.__version__ != expected["torch"]:
        raise ValueError(f"Unexpected Torch build: {torch.__version__}")
    if not torch.cuda.is_available():
        raise ValueError("CUDA is unavailable in the allocated Pythia job")
    gpu = torch.cuda.get_device_name(0)
    capability = torch.cuda.get_device_capability(0)
    compiled_arches = list(torch.cuda.get_arch_list())
    if gpu != expected["expected_gpu"]:
        raise ValueError(f"Unexpected Pythia GPU: {gpu}")
    observed_capability = f"{capability[0]}.{capability[1]}"
    if observed_capability != expected["expected_compute_capability"]:
        raise ValueError(f"Unexpected Pythia GPU capability: {observed_capability}")
    if expected["expected_compiled_arch"] not in compiled_arches:
        raise ValueError(f"Frozen runtime lacks {expected['expected_compiled_arch']}: {compiled_arches}")
    free_memory_bytes, total_memory_bytes = torch.cuda.mem_get_info(0)
    min_free_memory_bytes = int(expected.get("min_free_memory_bytes", 0))
    if free_memory_bytes < min_free_memory_bytes:
        raise ValueError(
            f"Allocated Pythia GPU lacks frozen free memory: {free_memory_bytes} < {min_free_memory_bytes}"
        )
    amp_dtypes = {"float16": torch.float16, "bfloat16": torch.bfloat16}
    if expected_amp_dtype not in amp_dtypes:
        raise ValueError(f"Unsupported frozen AMP dtype: {expected_amp_dtype}")
    if expected_amp_dtype == "bfloat16" and not torch.cuda.is_bf16_supported():
        raise ValueError("Allocated Pythia GPU does not support the frozen BF16 runtime")
    amp_dtype = amp_dtypes[expected_amp_dtype]
    probe = torch.nn.Linear(32, 32, bias=False, device="cuda", dtype=amp_dtype)
    values = torch.randn(4, 32, device="cuda", dtype=amp_dtype, requires_grad=True)
    loss = probe(values).float().square().mean()
    loss.backward()
    if not torch.isfinite(loss) or values.grad is None or not torch.isfinite(values.grad).all():
        raise ValueError("Pythia frozen-precision runtime probe is non-finite")
    payload = {
        "status": "PASS",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "template": str(args.template.resolve()) if args.template else None,
        "template_sha256": sha256_file(args.template.resolve()) if args.template else None,
        "scratch_root": str(args.scratch_root.resolve()) if args.scratch_root else None,
        "python_executable": executable,
        "torch_version": torch.__version__,
        "gpu": gpu,
        "compute_capability": observed_capability,
        "compiled_arches": compiled_arches,
        "free_memory_bytes_before_probe": free_memory_bytes,
        "total_memory_bytes": total_memory_bytes,
        "min_free_memory_bytes": min_free_memory_bytes,
        "amp_dtype": expected_amp_dtype,
        "finite_amp_loss": float(loss.detach().cpu()),
    }
    output = approved_scratch(args.output.resolve())
    write_json(output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
