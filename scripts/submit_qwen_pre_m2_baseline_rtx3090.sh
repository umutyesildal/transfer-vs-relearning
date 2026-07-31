#!/usr/bin/env bash
set -euo pipefail

ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
EXPECTED_COMMIT="$(git rev-parse HEAD)"

mkdir -p "$ROOT/logs"
test ! -e "$ROOT/results"

preflight_id="$(sbatch --parsable --job-name=qwen-pre-m2-3090-base-pre --output="$ROOT/logs/qwen-pre-m2-3090-base-pre-%j.out" --error="$ROOT/logs/qwen-pre-m2-3090-base-pre-%j.err" --export="ALL,EXPECTED_COMMIT=$EXPECTED_COMMIT,BASELINE_SCRATCH_ROOT=$ROOT" slurm/preflight_qwen_pre_m2_baseline.slurm)"
preflight_manifest="$ROOT/preflight/manifest.json"
baseline_id="$(sbatch --parsable --dependency="afterok:$preflight_id" --job-name=qwen-pre-m2-3090-base-eval --gres=gpu:rtx3090:1 --exclude=guppi5,guppi6,guppi7 --output="$ROOT/logs/qwen-pre-m2-3090-base-eval-%A_%a.out" --error="$ROOT/logs/qwen-pre-m2-3090-base-eval-%A_%a.err" --export="ALL,EXPECTED_COMMIT=$EXPECTED_COMMIT,PREFLIGHT_MANIFEST=$preflight_manifest,BASELINE_SCRATCH_ROOT=$ROOT" slurm/eval_qwen_pre_m2_baseline_slice.slurm)"

echo "preflight_id=$preflight_id"
echo "baseline_array_id=$baseline_id"
echo "preflight_manifest=$preflight_manifest"
echo "expected_commit=$EXPECTED_COMMIT"
echo "gpu_type=rtx3090"
echo "excluded_nodes=guppi5,guppi6,guppi7"
echo "output_root=$ROOT"
squeue -j "$preflight_id,$baseline_id" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.20N %.30R'
