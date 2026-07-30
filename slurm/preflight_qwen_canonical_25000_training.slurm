#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-runcheck
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
OUTPUT_ROOT="${ROOT}/training/replay_w0_5_seed42"
CONFIG="${REPO_ROOT}/configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml"
MIN_FREE_BYTES=$((1024 * 1024 * 1024 * 1024))
test -s "${ROOT}/prepared/dataset_manifest.json"
test -s "${ROOT}/smoke/resume_rehearsal.json"
test ! -e "${OUTPUT_ROOT}"

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
avail_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
avail_inodes=$(df -Pi /vol/tmp2 | tail -n 1 | awk '{print $4}')
test "${home_kib}" -le $((10 * 1024 * 1024))
test $((avail_kib * 1024)) -ge "${MIN_FREE_BYTES}"
test "${avail_inodes}" -ge 100000
case "$(readlink -m "${OUTPUT_ROOT}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

module load anaconda/3-2024.06
cd "${REPO_ROOT}"
conda run --name xfer-relearn python - "${ROOT}/prepared/dataset_manifest.json" "${ROOT}/smoke/resume_rehearsal.json" "${CONFIG}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
import yaml

dataset_path, smoke_path, config_path = map(Path, sys.argv[1:])
dataset = json.loads(dataset_path.read_text())
smoke = json.loads(smoke_path.read_text())
config = yaml.safe_load(config_path.read_text())
assert dataset["status"] == "passed"
assert dataset["subjects"] == 5000 and dataset["facts"] == 25000
assert dataset["train_rows"] == 175000 and dataset["four_form_probes"] == 200000
assert dataset["exact_prefix_probes"] == 25000
assert dataset["replay"]["train_rows"] == 175000
assert dataset["replay"]["full_population_subject_surface_hits"] == 0
assert smoke["status"] == "passed" and smoke["scientific_result"] is False
assert config["training"]["gradient_accumulation_steps"] == 500
assert config["runtime"]["world_size"] == 1
for section in ("files",):
    for item in dataset[section].values():
        path = Path(item["path"])
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        assert observed == item["sha256"], path
for key in ("train_file", "validation_file"):
    path = Path(dataset["replay"][key])
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    assert observed == dataset["replay"][key.replace("file", "sha256")], path
print("status=frozen_inputs_verified")
PY

git_commit=$(git rev-parse HEAD)
created_at=$(date --iso-8601=seconds)
dataset_sha=$(sha256sum "${ROOT}/prepared/dataset_manifest.json" | awk '{print $1}')
config_sha=$(sha256sum "${CONFIG}" | awk '{print $1}')
printf '{"status":"passed","created_at":"%s","git_commit":"%s","home_kib":%s,"tmp2_available_kib":%s,"tmp2_available_inodes":%s,"minimum_free_bytes":%s,"dataset_manifest_sha256":"%s","config_file_sha256":"%s","requested_a100_gpus":1,"exclusive":false,"scheduler_priority":"default","updates":252,"checkpoints":11,"retention_policy":"preserve_all_until_frozen_evaluation"}\n' \
  "${created_at}" "${git_commit}" "${home_kib}" "${avail_kib}" "${avail_inodes}" "${MIN_FREE_BYTES}" "${dataset_sha}" "${config_sha}" > \
  "${ROOT}/preflight/training_${SLURM_JOB_ID}.json"

du -xsh "${HOME_ROOT}" "${ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
squeue -o '%.18i %.12u %.12T %.10M %.24j %.20N %.30R'
sinfo -p gpu -o '%P %a %l %D %t %G %N'
printf 'status=passed output_root=%s cache_root=%s expected_checkpoints=11 estimated_training_tree_gib=100-130\n' \
  "$(readlink -m "${OUTPUT_ROOT}")" "$(readlink -m "${ROOT}/cache")"
