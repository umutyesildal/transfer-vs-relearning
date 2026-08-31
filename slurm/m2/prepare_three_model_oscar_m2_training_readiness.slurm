#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-readiness-evidence-v1
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=03:00:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${OUTPUT_ROOT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test -d "$OUTPUT_ROOT/control"
write_exit() { code=$?; status=BLOCKED; if test "$code" -eq 0; then status=PASS; fi; printf '{"schema_version":1,"status":"%s","exit_code":%s,"job_id":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' "$status" "$code" "${SLURM_JOB_ID:-unknown}" > "$OUTPUT_ROOT/control/slurm_exit.json.tmp"; mv "$OUTPUT_ROOT/control/slurm_exit.json.tmp" "$OUTPUT_ROOT/control/slurm_exit.json"; }
trap write_exit EXIT
module load anaconda/3-2024.06
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
/usr/bin/time -v conda run --no-capture-output --name xfer-relearn python \
  scripts/m2/prepare_three_model_oscar_m2_training_readiness.py \
  --repo-root "$PWD" \
  --config configs/training/m2_oscar_training_readiness_evidence_v1.yaml \
  --execution-enabled
