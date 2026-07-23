#!/usr/bin/env bash
#SBATCH --job-name=m1-ret-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:25:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_v1"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/family_${SLURM_JOB_ID}.json"
RESERVE_BYTES=$((500 * 1024 * 1024 * 1024))

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
printf 'jobs=anchor_materialization,q_control_seed42,q_replay_w0_5_seed42,postrun_audit\n'
printf 'destinations=%s\n' "${SCRATCH_ROOT}/{anchor,training,logs,tmp,cache,preflight}"
printf 'expected_checkpoints=11 per training condition; 22 family total plus two final models\n'
printf 'estimated_bytes_per_checkpoint=20401094656\nfamily_reserve_bytes=%s\n' "${RESERVE_BYTES}"
printf 'retention=keep all checkpoints through frozen evaluation; then freeze selected model-only endpoint and compact evidence, with duplicate optimizer states cleanup-eligible\n'
printf 'runtime_estimate=control 25-45 minutes; replay 45-80 minutes after allocation\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge "${RESERVE_BYTES}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
for path in \
  "${SCRATCH_ROOT}/anchor" \
  "${SCRATCH_ROOT}/training/control_seed42" \
  "${SCRATCH_ROOT}/training/replay_w0_5_seed42"; do
  test ! -e "${path}"
  case "$(readlink -m "${path}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
done
for path in \
  "${REPO_ROOT}/scripts/prepare_m1_retention_anchor.py" \
  "${REPO_ROOT}/slurm/prepare_m1_retention_anchor.slurm" \
  "${REPO_ROOT}/slurm/train_m1_retention_seed42.slurm" \
  "${REPO_ROOT}/slurm/audit_m1_retention_seed42.slurm" \
  "${REPO_ROOT}/configs/training/m1_qwen_retention_control_seed42.yaml" \
  "${REPO_ROOT}/configs/training/m1_qwen_retention_replay_w0_5_seed42.yaml" \
  "/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets/train.jsonl" \
  "/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets/validation.jsonl" \
  "/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json"; do
  test -f "${path}"
done

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

dataset_root = Path("/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets")
dataset_manifest = json.loads((dataset_root / "dataset_manifest.json").read_text())
assert dataset_manifest["train_rows"] == 3500
assert dataset_manifest["validation_rows"] == 500
assert sha256_file(dataset_root / "train.jsonl") == dataset_manifest["train_sha256"]
assert sha256_file(dataset_root / "validation.jsonl") == dataset_manifest["validation_sha256"]

control = load_training_config(repo_path / "configs/training/m1_qwen_retention_control_seed42.yaml")
replay = load_training_config(repo_path / "configs/training/m1_qwen_retention_replay_w0_5_seed42.yaml")
assert control["dataset"] == replay["dataset"]
assert control["model"] == replay["model"]
for key in (
    "block_size", "learning_rate", "num_train_epochs", "per_device_train_batch_size",
    "gradient_accumulation_steps", "warmup_ratio", "weight_decay", "lr_scheduler_type",
    "loss_mode", "supervise_eos", "seed", "data_seed",
):
    assert control["training"][key] == replay["training"][key], key
assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252
assert replay["retention"]["mechanism"] == "replay"
assert replay["retention"]["coefficient"] == 0.5
assert replay["retention"]["max_tokens"] == 64
assert control["training"]["output_root"] == "/vol/tmp2/yesildau/m1_retention_v1/training/control_seed42"
assert replay["training"]["output_root"] == "/vol/tmp2/yesildau/m1_retention_v1/training/replay_w0_5_seed42"
model_manifest = json.loads(Path(control["model"]["base_model_manifest"]).read_text())
for key in ("local_path_absolute", "tokenizer_source_path_absolute"):
    model_path = Path(model_manifest[key]).resolve()
    assert str(model_path).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/"))
    assert model_path.exists()

payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": job_id,
    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip(),
    "jobs": ["anchor_materialization", "q_control_seed42", "q_replay_w0_5_seed42", "postrun_audit"],
    "home_kib": int(home_kib),
    "tmp2_available_kib": int(available_kib),
    "family_reserve_bytes": int(reserve_bytes),
    "expected_checkpoints_per_condition": 11,
    "expected_optimizer_updates": 252,
    "factual_train_rows": 3500,
    "factual_validation_rows": 500,
    "output_roots": {
        "anchor": "/vol/tmp2/yesildau/m1_retention_v1/anchor",
        "control": "/vol/tmp2/yesildau/m1_retention_v1/training/control_seed42",
        "replay": "/vol/tmp2/yesildau/m1_retention_v1/training/replay_w0_5_seed42",
    },
}
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY

printf 'status=passed\nmanifest=%s\n' "${PREFLIGHT_MANIFEST}"
