#!/usr/bin/env bash
#SBATCH --job-name=m1-v100-env
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.err
set -euo pipefail

ROOT="${M1_V100_ENV_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1}"
BASE_PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
PIP_CACHE_DIR=/vol/tmp2/yesildau/m1_provenance_screen_v3/cache/pip

case "${ROOT}" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Compatibility environment must be scratch-routed: ${ROOT}" >&2; exit 2 ;;
esac
test ! -e "${ROOT}"
mkdir -p "$(dirname "${ROOT}")" "${PIP_CACHE_DIR}"
export PIP_CACHE_DIR PYTHONDONTWRITEBYTECODE=1

"${BASE_PYTHON}" -m venv --system-site-packages "${ROOT}"
"${ROOT}/bin/python" -m pip install \
  --index-url https://download.pytorch.org/whl/cu124 \
  --extra-index-url https://pypi.org/simple \
  'torch==2.6.0'

"${ROOT}/bin/python" - "${ROOT}" <<'PY'
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
    raise SystemExit(f"V100 sm_70 missing from compatibility build: {compiled_arches}")
payload = {
    "status": "INSTALL_PASS_GPU_VALIDATION_PENDING",
    "python": str(root / "bin/python"),
    "torch": torch.__version__,
    "torch_cuda": torch.version.cuda,
    "torch_compiled_arches": compiled_arches,
    "transformers": transformers.__version__,
    "datasets": datasets.__version__,
    "purpose": "OLMo V100 FP16 compatibility install; scratch-only; GPU validation remains mandatory",
}
manifest = root / "compat_manifest.json"
manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
payload["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
print(json.dumps(payload, indent=2, sort_keys=True))
PY
