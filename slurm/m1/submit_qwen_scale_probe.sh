#!/usr/bin/env bash
set -euo pipefail
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v3
pre=$(sbatch --parsable slurm/m1/preflight_qwen_scale_probe.slurm)
manifest="${ROOT}/preflight/family_${pre}.json"
prep=$(sbatch --parsable --dependency="afterok:${pre}" --export="ALL,PREFLIGHT_MANIFEST=${manifest}" slurm/m1/prepare_qwen_scale_probe.slurm)
train=$(sbatch --parsable --dependency="afterok:${prep}" --export="ALL,PREFLIGHT_MANIFEST=${manifest}" slurm/m1/train_qwen_scale_probe.slurm)
evalprep=$(sbatch --parsable --dependency="afterok:${train}" slurm/m1/prepare_qwen_scale_probe_evaluation.slurm)
evals=$(sbatch --parsable --dependency="afterok:${evalprep}" --array=0-10%3 slurm/m1/eval_qwen_scale_probe_checkpoints.slurm)
printf 'preflight=%s\nprepare=%s\ntrain=%s\neval_prepare=%s\nevaluations=%s\n' "${pre}" "${prep}" "${train}" "${evalprep}" "${evals}"
squeue -j "${pre},${prep},${train},${evalprep},${evals}" -o '%.18i %.12T %.10M %.24j %.20N %.30R'
