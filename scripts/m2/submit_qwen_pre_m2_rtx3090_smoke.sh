#!/usr/bin/env bash
set -euo pipefail

ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_rtx3090_v1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
EXPECTED_COMMIT="$(git rev-parse HEAD)"

mkdir -p "$ROOT/logs"
test ! -e "$ROOT/results"

sbatch_args=(
  --parsable
  --gres=gpu:rtx3090:1
  --exclude=guppi6,guppi7
  --nodelist=guppi8
  --job-name=qwen-pre-m2-3090-smoke
  --output="$ROOT/logs/%x-%A_%a.out"
  --error="$ROOT/logs/%x-%A_%a.err"
  --export="ALL,EXPECTED_COMMIT=$EXPECTED_COMMIT,SMOKE_SCRATCH_ROOT=$ROOT"
)
smoke_id="$(sbatch "${sbatch_args[@]}" slurm/m2/smoke_qwen_pre_m2_baseline.slurm)"

printf 'smoke_id=%s\n' "$smoke_id"
printf 'expected_commit=%s\n' "$EXPECTED_COMMIT"
printf 'scratch_root=%s\n' "$ROOT"
printf 'gpu_type=rtx3090\n'
printf 'excluded_nodes=guppi6,guppi7\n'
printf 'nodelist=guppi8\n'
squeue -j "$smoke_id" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.20N %.30R'
