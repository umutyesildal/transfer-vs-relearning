#!/usr/bin/env bash
#SBATCH --job-name=qwen-bridge-r-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:45:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
OUTPUT_ROOT="${SCRATCH_ROOT}/evaluation_v2_qwen"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/qwen_evaluation_recovery_${SLURM_JOB_ID}.json"
RESERVE_BYTES=$((5 * 1024 * 1024 * 1024))

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
printf 'home_kib=%s\ntmp2_available_kib=%s\n' "${home_kib}" "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\nruns_resolved=%s\n' "${artifacts_resolved}" "${runs_resolved}"
printf 'jobs=qwen_m1_low_full_recovery\ndestination=%s/results/qwen\n' "${OUTPUT_ROOT}"
printf 'expected_new_checkpoints=0\nexpected_raw_probe_rows=4500\n'
printf 'expected_output_reserve_bytes=%s\n' "${RESERVE_BYTES}"
printf 'retention=reuse hashed V1 M0 read-only; retain new M1/low/full per-probe and PPL evidence\n'
printf 'expected_runtime_after_gpu_start=30-50 minutes\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge "${RESERVE_BYTES}"
test ! -e "${OUTPUT_ROOT}"
test -f "${REPO_ROOT}/scripts/prepare_qwen_bridge_evaluation_recovery.py"
test -f "${REPO_ROOT}/slurm/evaluate_qwen_bridge_recovery.slurm"
test -f "${REPO_ROOT}/slurm/audit_qwen_bridge_evaluation_recovery.slurm"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${OUTPUT_ROOT}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_qwen_bridge_evaluation_recovery.py \
  --repo-root "${REPO_ROOT}" --output-root "${OUTPUT_ROOT}"
recovery_manifest="${OUTPUT_ROOT}/contract/recovery_manifest.json"
recovery_sha256=$(sha256sum "${recovery_manifest}" | awk '{print $1}')

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${PREFLIGHT_MANIFEST}" "${recovery_manifest}" "${recovery_sha256}" \
  "${home_kib}" "${tmp2_available_kib}" "${RESERVE_BYTES}" "${SLURM_JOB_ID}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

output, manifest_path = Path(sys.argv[1]), Path(sys.argv[2])
manifest = json.loads(manifest_path.read_text())
assert manifest["status"] == "frozen_ready_to_evaluate"
assert manifest["states_to_evaluate"] == ["m1", "low", "full"]
assert manifest["validated_prompt_candidate_boundaries"] > 0
assert manifest["expected_new_checkpoints"] == 0
tokenizer = Path(manifest["tokenizer_path"]).resolve()
assert str(tokenizer).startswith("/vol/tmp2/yesildau/")
assert (tokenizer / "tokenizer.json").is_file()
for state, endpoint in manifest["models"].items():
    assert Path(endpoint["tokenizer_path"]).resolve() == tokenizer, state
    assert Path(endpoint["model_path"]).resolve() != tokenizer, state
payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": sys.argv[7],
    "recovery_manifest": str(manifest_path),
    "recovery_manifest_sha256": sys.argv[3],
    "states": ["m1", "low", "full"],
    "validated_prompt_candidate_boundaries": manifest["validated_prompt_candidate_boundaries"],
    "home_kib": int(sys.argv[4]),
    "tmp2_available_kib": int(sys.argv[5]),
    "output_reserve_bytes": int(sys.argv[6]),
    "expected_new_checkpoints": 0,
}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY
printf 'status=passed\nrecovery_manifest=%s\nrecovery_manifest_sha256=%s\n' \
  "${recovery_manifest}" "${recovery_sha256}"
