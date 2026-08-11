#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.experiments.m1_cross_family import approved_scratch, load_registry
from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed validation of the frozen Pythia V100 runtime.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import torch

    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    if registry["version"] != "m1_provenance_screen_v3_pythia_repair_v1":
        raise ValueError("V100 runtime validation only accepts the Pythia repair registry")
    expected = registry["runtime"]
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
    probe = torch.nn.Linear(32, 32, bias=False, device="cuda", dtype=torch.float16)
    values = torch.randn(4, 32, device="cuda", dtype=torch.float16, requires_grad=True)
    loss = probe(values).float().square().mean()
    loss.backward()
    if not torch.isfinite(loss) or values.grad is None or not torch.isfinite(values.grad).all():
        raise ValueError("Pythia V100 FP16 runtime probe is non-finite")
    payload = {
        "status": "PASS",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "python_executable": executable,
        "torch_version": torch.__version__,
        "gpu": gpu,
        "compute_capability": observed_capability,
        "compiled_arches": compiled_arches,
        "finite_fp16_loss": float(loss.detach().cpu()),
    }
    output = approved_scratch(args.output.resolve())
    write_json(output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
