#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:25:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"
SEED42_ROOT="/vol/tmp2/yesildau/m1_retention_v1"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/family_${SLURM_JOB_ID}.json"
RESERVE_BYTES=$((250 * 1024 * 1024 * 1024))
ADJUDICATED_SHA256="e7d52bfc0bfa9c0adda02f641ea6b0d8bc0620d33ecdf4599c8fa778270899a6"
ORIGINAL_SHA256="78a2f440faede734e7480c6ab3c32b0b60f181d90895d136c6e4b413429e0487"

mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${SCRATCH_ROOT}/preflight/home_large_before.txt"

printf 'home_kib=%s\ntmp2_available_kib=%s\n' "${home_kib}" "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\nruns_resolved=%s\n' "${artifacts_resolved}" "${runs_resolved}"
printf 'jobs=q_replay_w0_5_seed43,postrun_audit\n'
printf 'destinations=%s\n' "${SCRATCH_ROOT}/{training,logs,tmp,cache,preflight}"
printf 'expected_checkpoints=11 plus final model\n'
printf 'estimated_bytes_per_checkpoint=20401094656\nfamily_reserve_bytes=%s\n' "${RESERVE_BYTES}"
printf 'retention=keep all checkpoints through frozen replication evaluation; then freeze selected model-only checkpoint and compact evidence; duplicate optimizer states become cleanup-eligible only after verification\n'
printf 'runtime_estimate=replay 110-145 minutes after allocation; walltime 180 minutes\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge "${RESERVE_BYTES}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
OUTPUT_ROOT="${SCRATCH_ROOT}/training/replay_w0_5_seed43"
test ! -e "${OUTPUT_ROOT}"
case "$(readlink -m "${OUTPUT_ROOT}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

for path in \
  "${REPO_ROOT}/slurm/train_m1_retention_seed43.slurm" \
  "${REPO_ROOT}/slurm/audit_m1_retention_seed43.slurm" \
  "${REPO_ROOT}/configs/training/m1_qwen_retention_replay_w0_5_seed43.yaml" \
  "${SEED42_ROOT}/anchor/train.jsonl" \
  "${SEED42_ROOT}/anchor/validation.jsonl" \
  "${SEED42_ROOT}/anchor/manifest.json" \
  "${SEED42_ROOT}/evaluation_v1/retention_checkpoint_summary.json" \
  "${SEED42_ROOT}/evaluation_v1/retention_checkpoint_adjudicated_summary.json"; do
  test -f "${path}"
done
printf '%s  %s\n' "${ADJUDICATED_SHA256}" \
  "${SEED42_ROOT}/evaluation_v1/retention_checkpoint_adjudicated_summary.json" | sha256sum -c -
printf '%s  %s\n' "${ORIGINAL_SHA256}" \
  "${SEED42_ROOT}/evaluation_v1/retention_checkpoint_summary.json" | sha256sum -c -

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${PREFLIGHT_MANIFEST}" "${SLURM_JOB_ID}" "${home_kib}" "${tmp2_available_kib}" \
  "${RESERVE_BYTES}" "${REPO_ROOT}" <<'PY'
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

output, job_id, home_kib, available_kib, reserve_bytes, repo = sys.argv[1:]
repo_path = Path(repo)
sys.path.insert(0, str(repo_path / "src"))
from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config
from transfer_vs_relearning.utils.io import sha256_file

seed42_root = Path("/vol/tmp2/yesildau/m1_retention_v1")
dataset_root = Path("/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets")
dataset_manifest = json.loads((dataset_root / "dataset_manifest.json").read_text())
assert dataset_manifest["train_rows"] == 3500
assert dataset_manifest["validation_rows"] == 500
assert sha256_file(dataset_root / "train.jsonl") == dataset_manifest["train_sha256"]
assert sha256_file(dataset_root / "validation.jsonl") == dataset_manifest["validation_sha256"]

seed42 = load_training_config(repo_path / "configs/training/m1_qwen_retention_replay_w0_5_seed42.yaml")
seed43 = load_training_config(repo_path / "configs/training/m1_qwen_retention_replay_w0_5_seed43.yaml")
assert seed42["dataset"] == seed43["dataset"]
assert seed42["model"] == seed43["model"]
assert seed42["retention"] == seed43["retention"]
allowed = {"run_name", "output_root", "seed", "data_seed"}
for key in set(seed42["training"]) | set(seed43["training"]):
    if key not in allowed:
        assert seed42["training"].get(key) == seed43["training"].get(key), key
assert seed43["training"]["seed"] == 43
assert seed43["training"]["data_seed"] == 43
assert seed43["training"]["output_root"] == \
    "/vol/tmp2/yesildau/m1_retention_seed43_v1/training/replay_w0_5_seed43"
assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252

anchor_manifest = json.loads((seed42_root / "anchor/manifest.json").read_text())
assert sha256_file(seed42_root / "anchor/train.jsonl") == anchor_manifest["files"]["train"]["sha256"]
assert sha256_file(seed42_root / "anchor/validation.jsonl") == anchor_manifest["files"]["validation"]["sha256"]
adjudicated = json.loads((seed42_root / "evaluation_v1/retention_checkpoint_adjudicated_summary.json").read_text())
assert adjudicated["original_frozen_decision"] == "retention_remediation_failed"
assert adjudicated["corrected_decision"] == "replicate_replay_seed43"
assert adjudicated["replication_candidate"] == {"condition": "replay_w0_5", "checkpoint_step": 50}

payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": job_id,
    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip(),
    "jobs": ["q_replay_w0_5_seed43", "postrun_audit"],
    "home_kib": int(home_kib),
    "tmp2_available_kib": int(available_kib),
    "family_reserve_bytes": int(reserve_bytes),
    "expected_checkpoints": 11,
    "expected_optimizer_updates": 252,
    "factual_train_rows": 3500,
    "factual_validation_rows": 500,
    "seed": 43,
    "data_seed": 43,
    "selected_seed42_candidate_step": 50,
    "output_root": "/vol/tmp2/yesildau/m1_retention_seed43_v1/training/replay_w0_5_seed43",
}
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY

printf 'status=passed\nmanifest=%s\n' "${PREFLIGHT_MANIFEST}"
