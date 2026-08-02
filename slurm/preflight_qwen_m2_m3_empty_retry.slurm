#!/usr/bin/env bash
# CPU-only preflight for the four explicitly empty m2_clean_seed42 slices.
# It creates no model or evaluation output and must pass before retry submission.
#SBATCH --job-name=qwen-m2-m3-retry-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/retry_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/retry_v1/logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
EVAL_ROOT="${ROOT}/evaluation_v1"
RETRY_ROOT="${ROOT}/retry_v1"
RETRY_PREFLIGHT_MANIFEST="${RETRY_ROOT}/preflight/manifest.json"
CONTRACT_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1
EVALUATION_MANIFEST="${EVAL_ROOT}/evaluation_manifest.json"
SLICE_REGISTRY="${CONTRACT_ROOT}/evaluation/slice_registry.json"
RETRY_MANIFEST="${RETRY_ROOT}/retry_manifest.json"
PYTHON_BIN="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${EVALUATION_MANIFEST}"
test -s "${SLICE_REGISTRY}"
test ! -e "${RETRY_MANIFEST}"
test ! -e "${RETRY_PREFLIGHT_MANIFEST}"

du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
home_kib=$(du -xsk "${HOME_ROOT}" | awk 'NR == 1 {print $1}')
test "${home_kib}" -lt $((30 * 1024 * 1024))
test "$(readlink -f "${REPO_ROOT}/artifacts")" = "/vol/tmp/yesildau/transfer-vs-relearning/artifacts"

PYTHONPATH="${REPO_ROOT}/src" "${PYTHON_BIN}" scripts/prepare_qwen_m2_m3_empty_retry.py \
  --evaluation-manifest "${EVALUATION_MANIFEST}" \
  --slice-registry "${SLICE_REGISTRY}" \
  --task-ids 2 11 14 15 \
  --required-state m2_clean_seed42 \
  --output-manifest "${RETRY_MANIFEST}"

PYTHONPATH="${REPO_ROOT}/src" "${PYTHON_BIN}" - "${RETRY_MANIFEST}" "${EXPECTED_COMMIT}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "ready_for_fresh_preflight"
assert payload["task_ids"] == [2, 11, 14, 15]
assert len(payload["entries"]) == 4
assert payload["expected_new_checkpoints"] == 0
print(f"status=passed retry_manifest={sys.argv[1]} expected_tasks=4 expected_checkpoints=0 git_commit={sys.argv[2]}")
PY

PYTHONPATH="${REPO_ROOT}/src" "${PYTHON_BIN}" - "${RETRY_MANIFEST}" "${RETRY_PREFLIGHT_MANIFEST}" "${EXPECTED_COMMIT}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

retry_manifest = Path(sys.argv[1])
preflight_manifest = Path(sys.argv[2])
payload = json.loads(retry_manifest.read_text(encoding="utf-8"))
preflight_manifest.parent.mkdir(parents=True, exist_ok=True)
preflight_manifest.write_text(json.dumps({
    "status": "passed",
    "git_commit": sys.argv[3],
    "evaluation_manifest": payload["evaluation_manifest"],
    "evaluation_manifest_sha256": payload["evaluation_manifest_sha256"],
    "retry_manifest": str(retry_manifest),
    "retry_manifest_sha256": hashlib.sha256(retry_manifest.read_bytes()).hexdigest(),
    "expected_jobs": 4,
    "expected_states": 1,
    "expected_slices": 4,
    "expected_probes": sum(int(item["probe_count"]) for item in payload["entries"]),
    "expected_new_checkpoints": 0,
    "estimated_family_bytes": 178956971,
    "retention_policy": payload["retention_policy"],
}, indent=2) + "\n", encoding="utf-8")
print(f"status=passed preflight_manifest={preflight_manifest}")
PY

find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
printf 'status=passed retry_manifest=%s preflight_manifest=%s expected_tasks=4 expected_checkpoints=0 estimated_new_bytes=178956971 retention=no_evaluation_checkpoints\n' \
  "${RETRY_MANIFEST}" "${RETRY_PREFLIGHT_MANIFEST}"
