#!/usr/bin/env bash
#SBATCH --job-name=pre-m2-compare
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
HU_HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOT="/vol/tmp2/yesildau/pre_m2_followup_v1"
PYTHON="/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python"
BASE_MANIFEST="/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json"
SEED42_MANIFEST="/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen/seed42_checkpoint200/model_manifest.json"
SEED43_MANIFEST="/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen/seed43_checkpoint75/model_manifest.json"

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{comparison,logs,tmp}

echo "repo_commit=$(git rev-parse HEAD)"
echo "comparison_output=${SCRATCH_ROOT}/comparison"
du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2

PYTHONPATH=src "${PYTHON}" scripts/build_pre_m2_followup_contract.py \
  --repo-root . \
  --base-model-manifest "${BASE_MANIFEST}" \
  --seed42-model-manifest "${SEED42_MANIFEST}" \
  --seed43-model-manifest "${SEED43_MANIFEST}"

PYTHONPATH=src "${PYTHON}" scripts/compare_pre_m2_frozen_suite.py \
  --run-dir "${SCRATCH_ROOT}/evaluations/base" \
  --run-dir "${SCRATCH_ROOT}/evaluations/seed42" \
  --run-dir "${SCRATCH_ROOT}/evaluations/seed43" \
  --repeat-reference-dir "${SCRATCH_ROOT}/smoke/base_1probe" \
  --output-dir "${SCRATCH_ROOT}/comparison" \
  --bootstrap-samples 2000 \
  --bootstrap-seed 20260717

test -s "${SCRATCH_ROOT}/comparison/comparison_manifest.json"
test -s "${SCRATCH_ROOT}/comparison/repeatability_audit.json"
test -s "${SCRATCH_ROOT}/comparison/accuracy_with_bootstrap_ci.csv"
test -s "${SCRATCH_ROOT}/comparison/paired_form_comparisons.csv"
test -s "${SCRATCH_ROOT}/comparison/robust_intersections.csv"
test -s "${SCRATCH_ROOT}/comparison/token_likelihood_summary.csv"
test -s "${SCRATCH_ROOT}/comparison/answer_sequence_likelihood_summary.csv"

echo "__COMPARISON_MANIFEST__"
cat "${SCRATCH_ROOT}/comparison/comparison_manifest.json"
echo "__REPEATABILITY_AUDIT__"
cat "${SCRATCH_ROOT}/comparison/repeatability_audit.json"
echo "__PROVENANCE__"
cat "/vol/tmp/yesildau/transfer-vs-relearning/artifacts/pre_m2_followup_v1/manifests/provenance.json"

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HU_HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
