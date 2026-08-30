#!/usr/bin/env bash
#SBATCH --job-name=vngrs-m2-oscar-blocks-recovery-4cpu-v1
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --time=06:00:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${OUTPUT_ROOT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test -d "$OUTPUT_ROOT/control"

write_exit_audit() {
  exit_code=$?
  status=BLOCKED
  if test "$exit_code" -eq 0; then status=PASS; fi
  temporary="$OUTPUT_ROOT/control/slurm_exit.json.tmp"
  printf '{"schema_version":1,"status":"%s","exit_code":%s,"job_id":"%s","node":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' \
    "$status" "$exit_code" "${SLURM_JOB_ID:-unknown}" "$(hostname)" > "$temporary"
  mv "$temporary" "$OUTPUT_ROOT/control/slurm_exit.json"
}
trap write_exit_audit EXIT

export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
module load anaconda/3-2024.06
/usr/bin/time -v conda run --no-capture-output --name xfer-relearn python \
  scripts/m2/materialize_three_model_oscar_m2_blocks_recovery.py \
  --repo-root "$PWD" \
  --config configs/corpora/vngrs_m2_oscar_exact_blocks_recovery_4cpu_v1.yaml \
  --execution-enabled
