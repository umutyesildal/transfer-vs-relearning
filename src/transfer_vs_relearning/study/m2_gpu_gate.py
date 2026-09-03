"""Allocation-local GPU identity gate; no physical-index guessing or fallback."""

from __future__ import annotations

import os
import re
import socket
import subprocess
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import write_json


MIN_FREE_BYTES = 20 * 1024**3


def canonical_gpu_uuid(raw: object) -> str:
    """Convert PyTorch 2.6 CUuuid's bare string to SMI's GPU-prefixed form.

    This is representation normalization, never an index lookup or device fallback.
    PyTorch v2.6.0 Module.cpp uuid_to_string emits exactly 8-4-4-4-12 hex.
    """
    value = str(raw)
    match = re.fullmatch(
        r"(?:GPU-)?([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", value
    )
    if not match or int(match.group(1).replace("-", ""), 16) == 0:
        raise ValueError("CUDA device UUID unavailable or unsupported; no index fallback")
    return "GPU-" + match.group(1).lower()


def assert_allocated_gpu_memory(audit_path: Path) -> dict[str, Any]:
    """Measure CUDA logical zero and cross-check that exact UUID with NVML/SMI.

    Import CUDA lazily, only inside an authorized GPU task. Persist failures as well
    as successes before any model load. Never map a numeric CVD token to a host index.
    """
    audit: dict[str, Any] = {
        "schema_version": 2,
        "status": "failed",
        "host": socket.gethostname(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_job_gpus": os.environ.get("SLURM_JOB_GPUS"),
        "slurm_step_gpus": os.environ.get("SLURM_STEP_GPUS"),
        "logical_device": 0,
        "gate_bytes": MIN_FREE_BYTES,
    }
    # Preserve any existing audit rather than replacing evidence on a second call.
    if audit_path.exists() or audit_path.is_symlink():
        raise FileExistsError(audit_path)
    try:
        visible = audit["cuda_visible_devices"]
        if not audit["slurm_job_id"] or not visible or "," in visible:
            raise ValueError("Exactly one Slurm-assigned CUDA device is required")
        import torch

        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise ValueError("CUDA must expose exactly one allocated device")
        properties = torch.cuda.get_device_properties(0)
        raw_uuid = getattr(properties, "uuid", None)
        audit.update(
            cuda_uuid_raw=str(raw_uuid)[:256],
            cuda_uuid_type=type(raw_uuid).__name__,
            torch_version=str(getattr(torch, "__version__", "unknown")),
            device_name=properties.name,
        )
        uuid = canonical_gpu_uuid(raw_uuid)
        audit.update(gpu_uuid=uuid, device_name=properties.name)
        if "A100" not in properties.name:
            raise ValueError("Frozen M2 route requires an A100")
        free_bytes, total_bytes = torch.cuda.mem_get_info(0)
        audit.update(cuda_free_bytes=int(free_bytes), cuda_total_bytes=int(total_bytes))
        if total_bytes < 70 * 1024**3 or not 0 <= free_bytes <= total_bytes:
            raise ValueError("Invalid memory report or non-80GB A100")
        probe = subprocess.run(
            ["nvidia-smi", "-i", uuid,
             "--query-gpu=uuid,memory.free,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
        )
        audit.update(smi_returncode=probe.returncode, smi_stdout=probe.stdout.strip(),
                     smi_stderr=probe.stderr.strip())
        fields = [part.strip() for part in probe.stdout.strip().split(",")]
        if probe.returncode or len(fields) != 3 or fields[0] != uuid:
            raise ValueError("CUDA-to-SMI UUID identity cross-check failed")
        smi_free, smi_total = int(fields[1]) * 1024**2, int(fields[2]) * 1024**2
        audit.update(smi_free_bytes=smi_free, smi_total_bytes=smi_total)
        if not 0 <= smi_free <= smi_total or abs(smi_total - total_bytes) > 1024**3:
            raise ValueError("CUDA/SMI total-memory cross-check failed")
        # Sequential samples can differ; both must pass the unchanged threshold.
        if min(free_bytes, smi_free) < MIN_FREE_BYTES:
            raise ValueError("Allocated UUID has less than the frozen 20 GiB free-memory gate")
        audit["status"] = "pass"
    except Exception as exc:
        audit["error"] = str(exc)
        write_json(audit_path, audit)
        raise
    write_json(audit_path, audit)
    return audit
