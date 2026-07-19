#!/usr/bin/env bash
#SBATCH --job-name=m1-qwen-pareto
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --exclude=gruenau10
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1"
REGISTRY="${ROOT}/checkpoint_registry.csv"
PREFLIGHT="${ROOT}/preflight/manifest.json"
PROBES="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_qwen_checkpoint_pareto_preflight.py --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --wave-manifest "${ROOT}/wave_manifest.json" --launcher "${REPO_ROOT}/slurm/eval_m1_qwen_checkpoint_pareto.slurm" --verify-manifest "${PREFLIGHT}" --task-index "${SLURM_ARRAY_TASK_ID}" --max-age-minutes 720
row="$(conda run --name xfer-relearn python -c 'import csv,sys; rows=list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig"))); i=int(sys.argv[2]); matches=[r for r in rows if int(r["array_index"])==i]; assert len(matches)==1; r=matches[0]; print("|".join(r[k] for k in ("label","model_manifest","model_manifest_sha256","hard_output","exact_config","general_config")))' "${REGISTRY}" "${SLURM_ARRAY_TASK_ID}" | tr -d '\r' | tail -n 1)"
IFS='|' read -r label model_manifest expected_sha hard_output exact_config general_config <<<"${row}"
actual_sha="$(sha256sum "${model_manifest}" | awk '{print $1}')"
test "${actual_sha}" = "${expected_sha}"
task_tmp="${ROOT}/tmp/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${task_tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}" --model-manifest "${model_manifest}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBES}" --output-dir "${hard_output}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${exact_config}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${general_config}"
