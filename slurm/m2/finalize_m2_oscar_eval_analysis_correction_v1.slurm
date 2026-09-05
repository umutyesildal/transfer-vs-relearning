#!/usr/bin/env bash
#SBATCH --job-name=m2-analysis-correct-v1
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}"
: "${CORRECTION_CONFIG:?}" "${M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
root=/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1
export PYTHONPATH="$PWD/src:$PWD" PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 WANDB_MODE=disabled
export TMPDIR="$root/tmp" XDG_CACHE_HOME="$root/tmp"
/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python \
  scripts/study/execute_m2_analysis_correction.py \
  --repo-root "$PWD" \
  --config "$CORRECTION_CONFIG" \
  --contract "$EXECUTION_CONTRACT" \
  --contract-sha256 "$EXPECTED_CONTRACT_SHA256" \
  --expected-commit "$EXPECTED_COMMIT" \
  --authorization-ack "$M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK"
