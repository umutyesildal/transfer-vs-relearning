#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-1gpu-v1-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}" "${TRAINING_CONFIG:?}"
cd "${SLURM_SUBMIT_DIR:?}"
module load anaconda/3-2024.06
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src:$PWD" HF_HOME="$root/cache" TRANSFORMERS_CACHE="$root/cache" XDG_CACHE_HOME="$root/cache" TORCH_HOME="$root/cache" TMPDIR="$root/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python scripts/m2/preflight_three_model_oscar_m2_training_v1.py --repo-root "$PWD" --config "$TRAINING_CONFIG" --contract "$EXECUTION_CONTRACT" --contract-sha256 "$EXPECTED_CONTRACT_SHA256" --expected-commit "$EXPECTED_COMMIT"
