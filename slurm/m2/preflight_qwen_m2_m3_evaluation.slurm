#!/usr/bin/env bash
# CPU-only preflight and registry freeze for the 96-slice M2/M3 endpoint evaluation.
# M1's completed 60,000-probe baseline is reused as the fixed comparison state.
#SBATCH --job-name=qwen-m2-m3-eval-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
EVAL_ROOT="${ROOT}/evaluation_v1"
CONTRACT_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1
BASELINE_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1
SOURCE_MANIFEST=/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json
PREFLIGHT_MANIFEST="${EVAL_ROOT}/preflight/manifest.json"
PYTHON_BIN="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test ! -e "${EVAL_ROOT}"
du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
home_kib=$(du -xsk "${HOME_ROOT}" | awk 'NR == 1 {print $1}')
test "${home_kib}" -lt $((30 * 1024 * 1024))
test "$(readlink -f "${REPO_ROOT}/artifacts")" = "/vol/tmp/yesildau/transfer-vs-relearning/artifacts"
test -s "${CONTRACT_ROOT}/manifest.json"
test -s "${BASELINE_ROOT}/summaries_final/qwen_m1_seed42_step75/per_probe_results.csv"
test -s "${BASELINE_ROOT}/summaries_final/qwen_m1_seed43_step50/per_probe_results.csv"

PYTHONPATH="${REPO_ROOT}/src" "${PYTHON_BIN}" scripts/m2/prepare_qwen_m2_m3_evaluation.py \
  --training-root "${ROOT}" \
  --source-model-manifest "${SOURCE_MANIFEST}" \
  --contract-root "${CONTRACT_ROOT}" \
  --baseline-root "${BASELINE_ROOT}" \
  --output-root "${EVAL_ROOT}"

PYTHONPATH="${REPO_ROOT}/src" "${PYTHON_BIN}" - "${EVAL_ROOT}" "${CONTRACT_ROOT}" "${EXPECTED_COMMIT}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
contract_root = Path(sys.argv[2])
expected_commit = sys.argv[3]
payload = json.loads((root / "evaluation_manifest.json").read_text(encoding="utf-8"))
assert payload["status"] == "frozen_ready_to_submit"
assert payload["endpoint"] == "checkpoint-128"
assert len(payload["states"]) == 4
assert len(payload["baseline_states"]) == 2
assert payload["slice_count"] == 24
for state in payload["states"]:
    assert Path(state["model_manifest"]).is_file()
    assert state["results_root"].startswith(str(root / "results"))
    assert Path(state["training_run"]).is_dir()
assert Path(payload["contract_root"]) == contract_root
preflight = root / "preflight" / "manifest.json"
preflight.parent.mkdir(parents=True, exist_ok=True)
preflight.write_text(json.dumps({
    "status": "passed",
    "git_commit": expected_commit,
    "evaluation_manifest": str(root / "evaluation_manifest.json"),
    "evaluation_manifest_sha256": hashlib.sha256((root / "evaluation_manifest.json").read_bytes()).hexdigest(),
    "expected_jobs": 96,
    "expected_states": 4,
    "expected_slices_per_state": 24,
    "expected_probes_per_state": 60000,
    "expected_new_checkpoints": 0,
    "estimated_family_bytes": 4 * 1024 * 1024 * 1024,
    "retention_policy": "retain_per_probe_evidence_and_compact_summaries; no_evaluation_checkpoints",
}, indent=2) + "\n", encoding="utf-8")
print(f"status=passed expected_jobs=96 manifest={preflight}")
PY

find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
printf 'status=passed output_root=%s preflight_manifest=%s expected_jobs=96 expected_checkpoints=0 estimated_family_bytes=%s retention=no_evaluation_checkpoints\n' \
  "${EVAL_ROOT}" "${PREFLIGHT_MANIFEST}" "$((4 * 1024 * 1024 * 1024))"
