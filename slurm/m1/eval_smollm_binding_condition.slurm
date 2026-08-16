#!/usr/bin/env bash
#SBATCH --job-name=smollm-binding-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/smollm_binding_evaluations_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_binding_evaluations_v1/logs/%x-%A.err
set -euo pipefail
: "${CONDITION:?}" "${FINAL_MODEL:?}" "${SOURCE_CONFIG:?}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/smollm_binding_evaluations_v1/${CONDITION}"
OUTPUT_ROOT="${ROOT}/results"
cd "${REPO_ROOT}"; module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/m1_form_generalization_preflight.py --repo-root "${REPO_ROOT}" --scratch-root "${ROOT}" --manifest "${ROOT}/preflight/manifest.json" --source-config "${SOURCE_CONFIG}" --launcher slurm/m1/eval_smollm_binding_condition.slurm --output-namespace "${OUTPUT_ROOT}" --expected-commit "$(git rev-parse HEAD)"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/m1/prepare_m1_canonical_form_diversity_evaluation.py --label "${CONDITION}" --final-model "${FINAL_MODEL}" --source-manifest artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json --output-root "${OUTPUT_ROOT}" --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/m2/evaluate_pre_m2_frozen_suite.py --model-label "${CONDITION}" --model-manifest "${OUTPUT_ROOT}/model_manifests/${CONDITION}.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv --output-dir "${OUTPUT_ROOT}/hard_suite/${CONDITION}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluation/evaluate_facts.py --config "${OUTPUT_ROOT}/exact_config.json"
conda run --name xfer-relearn python scripts/evaluation/evaluate_general_capability.py --config "${OUTPUT_ROOT}/general_config.json"
