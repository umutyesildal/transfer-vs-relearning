#!/usr/bin/env bash
#SBATCH --job-name=m1-v100-env-gpu
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v10032gb:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.err
set -euo pipefail

ROOT="${M1_V100_ENV_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1}"
PYTHON="${ROOT}/bin/python"
test -x "${PYTHON}"
test ! -e "${ROOT}/compat_manifest.json"
export PYTHONDONTWRITEBYTECODE=1

"${PYTHON}" - "${ROOT}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

import datasets
import torch
import transformers
import yaml

root = Path(sys.argv[1]).resolve()
compiled_arches = torch._C._cuda_getArchFlags().split()
if "sm_70" not in compiled_arches:
    raise SystemExit(f"V100 sm_70 missing from wheel: {compiled_arches}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable inside the allocated V100 job")
capability = list(torch.cuda.get_device_capability(0))
if capability != [7, 0]:
    raise SystemExit(f"Expected V100 compute capability [7, 0], got {capability}")

x = torch.randn(256, 256, device="cuda", dtype=torch.float16, requires_grad=True)
loss = (x @ x).float().square().mean()
loss.backward()
if not torch.isfinite(loss) or x.grad is None or not torch.isfinite(x.grad).all():
    raise SystemExit("V100 FP16 forward/backward compatibility probe was non-finite")
torch.cuda.synchronize()

payload = {
    "status": "PASS",
    "python": str(root / "bin/python"),
    "torch": torch.__version__,
    "torch_cuda": torch.version.cuda,
    "torch_compiled_arches": compiled_arches,
    "gpu": torch.cuda.get_device_name(0),
    "gpu_capability": capability,
    "fp16_forward_backward_loss": float(loss.detach().cpu()),
    "transformers": transformers.__version__,
    "datasets": datasets.__version__,
    "purpose": "OLMo V100 FP16 compatibility; scratch-only; project base env unchanged",
}
manifest = root / "compat_manifest.json"
manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
payload["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
print(json.dumps(payload, indent=2, sort_keys=True))
PY
