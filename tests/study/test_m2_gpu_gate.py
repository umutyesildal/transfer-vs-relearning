import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from transfer_vs_relearning.study import m2_gpu_gate as gate


UUID = "GPU-12345678-1234-1234-1234-123456789abc"


@pytest.fixture
def runtime(monkeypatch):
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    cuda = SimpleNamespace(
        is_available=lambda: True,
        device_count=lambda: 1,
        get_device_properties=lambda index: SimpleNamespace(
            uuid=UUID, name="NVIDIA A100 80GB PCIe"
        ),
        mem_get_info=lambda index: (60 * 1024**3, 80 * 1024**3),
    )
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=cuda))
    calls = []

    def probe(command, **kwargs):
        calls.append(command)
        assert kwargs["timeout"] == 20
        return SimpleNamespace(returncode=0, stdout=f"{UUID}, 61440, 81920\n", stderr="")

    monkeypatch.setattr(gate.subprocess, "run", probe)
    return cuda, calls


def test_uses_cuda_uuid_not_host_index_zero(runtime, tmp_path):
    import hashlib
    repo = Path(__file__).resolve().parents[2]
    contract = repo / "documentation/contracts/evaluation/vngrs-m2-oscar-gpu-identity-qualification-v1.md"
    assert hashlib.sha256(contract.read_bytes()).hexdigest() == (
        "4221b25cdd61a55751be85e9636b944a490cea441466d142d6a25e3535bbc34e"
    )
    assert hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest() == (
        "6e328d8c8879ec1e0b852fc85dbc357b6ea50490420c81c8a44da90a9be10d09"
    )
    _, calls = runtime
    result = gate.assert_allocated_gpu_memory(tmp_path / "audit.json")
    assert result["status"] == "pass"
    assert calls[0][2] == UUID  # CVD is zero, but NVML must use the CUDA UUID.
    assert result["gate_bytes"] == 21474836480


@pytest.mark.parametrize("failure", ["low_cuda", "missing_uuid", "multiple", "wrong_model"])
def test_cuda_failures_are_persistent(runtime, tmp_path, failure):
    cuda, _ = runtime
    if failure == "low_cuda":
        cuda.mem_get_info = lambda index: (16720592896, 80 * 1024**3)
    elif failure == "missing_uuid":
        cuda.get_device_properties = lambda index: SimpleNamespace(name="A100")
    elif failure == "multiple":
        cuda.device_count = lambda: 2
    else:
        cuda.get_device_properties = lambda index: SimpleNamespace(uuid=UUID, name="V100")
    path = tmp_path / "audit.json"
    with pytest.raises(ValueError):
        gate.assert_allocated_gpu_memory(path)
    assert json.loads(path.read_text())["status"] == "failed"


@pytest.mark.parametrize("failure", ["uuid_mismatch", "low_smi", "timeout", "bad_total"])
def test_smi_failures_are_persistent(runtime, monkeypatch, tmp_path, failure):
    def probe(*args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired("nvidia-smi", 20)
        stdout = {
            "uuid_mismatch": "GPU-other, 61440, 81920",
            "low_smi": f"{UUID}, 15946, 81920",
            "bad_total": f"{UUID}, 61440, 40960",
        }[failure]
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")
    monkeypatch.setattr(gate.subprocess, "run", probe)
    path = tmp_path / "audit.json"
    with pytest.raises((ValueError, subprocess.TimeoutExpired)):
        gate.assert_allocated_gpu_memory(path)
    assert json.loads(path.read_text())["error"]


def test_missing_slurm_refuses_and_preserves_audit(runtime, monkeypatch, tmp_path):
    monkeypatch.delenv("SLURM_JOB_ID")
    path = tmp_path / "audit.json"
    with pytest.raises(ValueError):
        gate.assert_allocated_gpu_memory(path)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        gate.assert_allocated_gpu_memory(path)
    assert path.read_bytes() == before
