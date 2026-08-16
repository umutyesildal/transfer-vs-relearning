#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_provenance_screen_retry_v2
REGISTRY=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/configs/experiments/m1_provenance_screen_retry_v2.yaml
DATASET_ROOT=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets
HOME_ROOT=/vol/fob-vol6/mi25/yesildau

git fetch origin corpus-update
local_commit=$(git rev-parse HEAD)
remote_commit=$(git rev-parse origin/corpus-update)
git merge-base --is-ancestor "$local_commit" "$remote_commit" || exit 1
dirty_paths=$(git status --porcelain=v1 --untracked-files=all | sed -E 's/^...//' | sort -u)
changed_paths=$(git diff --name-only "$local_commit" "$remote_commit" | sort -u)
overlap=$(comm -12 <(printf '%s\n' "$dirty_paths") <(printf '%s\n' "$changed_paths") | sed '/^$/d')
test -z "$overlap" || { printf '%s\n' "$overlap" >&2; exit 1; }
git pull --ff-only origin corpus-update

home_usage_bytes=$(timeout 120s du -x -B1 -s "$HOME_ROOT")
home_bytes=$(printf '%s\n' "$home_usage_bytes" | awk 'NR==1 {print $1}')
test -n "$home_bytes" && test "$home_bytes" -le $((30 * 1024 * 1024 * 1024))
timeout 120s du -xsh "$HOME_ROOT"
df -hP "$HOME_ROOT" /vol/tmp /vol/tmp2
df -iP "$HOME_ROOT" /vol/tmp /vol/tmp2
printf 'runs=%s\n' "$(readlink -f "$HOME_ROOT/transfer-vs-relearning/runs")"
printf 'artifacts=%s\n' "$(readlink -f "$HOME_ROOT/transfer-vs-relearning/artifacts")"

test ! -e "$SCRATCH_ROOT"
test -s "$DATASET_ROOT/dataset_manifest.json"
test -s "$DATASET_ROOT/train.jsonl"
test -s "$DATASET_ROOT/validation.jsonl"
"$PYTHON" - <<'PY'
import json
from pathlib import Path
root = Path('/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets')
manifest = json.loads((root / 'dataset_manifest.json').read_text(encoding='utf-8'))
assert manifest.get('version') == 'm1_canonical_form_diversity_v1'
assert sum(1 for _ in (root / 'train.jsonl').open(encoding='utf-8')) == 3500
assert sum(1 for _ in (root / 'validation.jsonl').open(encoding='utf-8')) == 500
print('dataset_version=' + str(manifest['version']))
print('dataset_train_rows=3500')
print('dataset_validation_rows=500')
PY

queued=$(squeue -u yesildau -h -o '%i|%j|%T|%R')
if printf '%s\n' "$queued" | grep -E '\|m1-prov-retry-v2-(acquire|train|eval|preflight)' >/dev/null; then
  echo 'retry-v2 namespace already present; refusing duplicate submission' >&2
  exit 1
fi
mkdir -p "$SCRATCH_ROOT/logs"
export_args="ALL,M1_PROVENANCE_SCREEN_ROOT=$SCRATCH_ROOT,M1_PROVENANCE_REGISTRY=$REGISTRY"

acq_pre=$(sbatch --parsable --job-name=m1-prov-retry-v2-preflight-acq \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-acq-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-acq-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=acquisition,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/m1/acquire_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-v2-acquire" \
  slurm/m1/preflight_m1_provenance_screen.slurm)
acq=$(sbatch --parsable --job-name=m1-prov-retry-v2-acquire --dependency="afterok:$acq_pre" --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-acquire-%A_%a.out" --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-acquire-%A_%a.err" \
  --export="$export_args" slurm/m1/acquire_m1_provenance_screen.slurm)

train_pre=$(sbatch --parsable --job-name=m1-prov-retry-v2-preflight-train --dependency="afterok:$acq" \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-train-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-train-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=training,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/m1/train_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-v2-train" \
  slurm/m1/preflight_m1_provenance_screen.slurm)
train=$(sbatch --parsable --job-name=m1-prov-retry-v2-train --dependency="afterok:$train_pre" --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-train-%A_%a.out" --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-train-%A_%a.err" \
  --export="$export_args" slurm/m1/train_m1_provenance_screen.slurm)

eval_pre=$(sbatch --parsable --job-name=m1-prov-retry-v2-preflight-eval --dependency="afterok:$train" \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-eval-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-preflight-eval-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=evaluation,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/m1/eval_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-v2-eval" \
  slurm/m1/preflight_m1_provenance_screen.slurm)
eval=$(sbatch --parsable --job-name=m1-prov-retry-v2-eval --dependency="afterok:$eval_pre" --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-v2-eval-%A_%a.out" --error="$SCRATCH_ROOT/logs/m1-prov-retry-v2-eval-%A_%a.err" \
  --export="$export_args" slurm/m1/eval_m1_provenance_screen.slurm)

echo "__ACQUISITION_PREFLIGHT_JOB_ID__=$acq_pre"
echo "__ACQUISITION_ARRAY_JOB_ID__=$acq"
echo "__TRAINING_PREFLIGHT_JOB_ID__=$train_pre"
echo "__TRAINING_ARRAY_JOB_ID__=$train"
echo "__EVALUATION_PREFLIGHT_JOB_ID__=$eval_pre"
echo "__EVALUATION_ARRAY_JOB_ID__=$eval"
squeue -h -j "$acq_pre,$acq,$train_pre,$train,$eval_pre,$eval" -o '%i %T %M %L %R %j'
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
cd "${SCRIPT_DIR}/.."
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
