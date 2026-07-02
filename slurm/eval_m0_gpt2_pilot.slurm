#!/usr/bin/env bash
#SBATCH --job-name=m0-gpt2-pilot
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
CONFIG_PATH="${EVAL_CONFIG:-configs/evaluation/m0_gpt2_pilot_direct.yaml}"
cd "${REPO_ROOT}"

echo "hostname=$(hostname)"
echo "user=$(whoami)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name --format=csv,noheader || true

module load anaconda/3-2024.06

conda run --name xfer-relearn python --version
conda run --name xfer-relearn python - <<'PY'
import torch, transformers
print("torch", torch.__version__)
print("cuda", torch.version.cuda)
print("transformers", transformers.__version__)
print("cuda_device_count", torch.cuda.device_count())
if torch.cuda.device_count() != 1:
    raise SystemExit("Expected exactly one Slurm-assigned GPU")
PY

echo "Resolved evaluator config:"
cat "${CONFIG_PATH}"
echo "Selected config: ${CONFIG_PATH}"
echo "Candidate batch size:"
conda run --name xfer-relearn python - "${CONFIG_PATH}" <<'PY'
import sys, yaml, json
cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
languages = cfg["languages"]
relations = cfg["relations"]
selected = json.load(open(cfg["pilot_subject_file"], encoding="utf-8"))["selected_subject_ids"]
print(cfg["runtime"]["candidate_batch_size"])
print("expected_probe_count", len(languages) * len(relations) * len(selected))
PY

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

conda run --name xfer-relearn python scripts/evaluate_facts.py \
  --config "${CONFIG_PATH}"
