#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_provenance_screen_retry_v1
REGISTRY=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/configs/experiments/m1_provenance_screen_retry_v1.yaml
DATASET_ROOT=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets
HOME_ROOT=/vol/fob-vol6/mi25/yesildau

# Reconcile only a fast-forward that does not overlap the existing dirty HU
# checkout. Never reset or discard owner-controlled files.
git fetch origin corpus-update
local_commit=$(git rev-parse HEAD)
remote_commit=$(git rev-parse origin/corpus-update)
git merge-base --is-ancestor "$local_commit" "$remote_commit" || {
  echo "HU checkout is not an ancestor of origin/corpus-update; refusing sync" >&2
  exit 1
}
dirty_paths=$(git status --porcelain=v1 --untracked-files=all | sed -E 's/^...//' | sort -u)
changed_paths=$(git diff --name-only "$local_commit" "$remote_commit" | sort -u)
overlap=$(comm -12 <(printf '%s\n' "$dirty_paths") <(printf '%s\n' "$changed_paths") | sed '/^$/d')
test -z "$overlap" || {
  echo "HU dirty paths overlap the published change set; refusing sync" >&2
  printf '%s\n' "$overlap" >&2
  exit 1
}
git pull --ff-only origin corpus-update

# Mandatory home/scratch capacity and inode preflight.
home_usage_bytes=$(timeout 30s du -x -B1 -s "$HOME_ROOT") || {
  echo "bounded exact-byte home-usage preflight timed out or failed" >&2
  exit 1
}
home_bytes=$(printf '%s\n' "$home_usage_bytes" | awk 'NR==1 {print $1}')
test -n "$home_bytes" && test "$home_bytes" -le $((30 * 1024 * 1024 * 1024))
home_usage_human=$(timeout 30s du -xsh "$HOME_ROOT") || {
  echo "bounded human-readable home-usage preflight timed out or failed" >&2
  exit 1
}
printf '%s\n' "$home_usage_human"
df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
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
assert manifest.get('version') == 'm1_canonical_form_diversity_v1', manifest
assert sum(1 for _ in (root / 'train.jsonl').open(encoding='utf-8')) == 3500
assert sum(1 for _ in (root / 'validation.jsonl').open(encoding='utf-8')) == 500
print('dataset_version=' + str(manifest['version']))
print('dataset_train_rows=3500')
print('dataset_validation_rows=500')
PY

# One fresh root and one fresh job namespace. The previous failed DAG remains
# untouched, including its acquisition artifacts and pending never-satisfiable
# evaluation dependencies.
queued=$(squeue -u yesildau -h -o '%i|%j|%T|%R')
if printf '%s\n' "$queued" | grep -E '\|m1-prov-retry-(acquire|train|eval|preflight)' >/dev/null; then
  echo 'retry job namespace is already present; refusing duplicate submission' >&2
  exit 1
fi
mkdir -p "$SCRATCH_ROOT/logs"

export_args="ALL,M1_PROVENANCE_SCREEN_ROOT=$SCRATCH_ROOT,M1_PROVENANCE_REGISTRY=$REGISTRY"

acquisition_preflight_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-preflight-acq \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-acq-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-acq-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=acquisition,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/acquire_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-acquire" \
  slurm/preflight_m1_provenance_screen.slurm)
acquisition_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-acquire \
  --dependency="afterok:$acquisition_preflight_id" \
  --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-acquire-%A_%a.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-acquire-%A_%a.err" \
  --export="$export_args" \
  slurm/acquire_m1_provenance_screen.slurm)

training_preflight_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-preflight-train \
  --dependency="afterok:$acquisition_id" \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-train-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-train-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=training,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/train_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-train" \
  slurm/preflight_m1_provenance_screen.slurm)
training_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-train \
  --dependency="afterok:$training_preflight_id" \
  --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-train-%A_%a.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-train-%A_%a.err" \
  --export="$export_args" \
  slurm/train_m1_provenance_screen.slurm)

evaluation_preflight_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-preflight-eval \
  --dependency="afterok:$training_id" \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-eval-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-preflight-eval-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=evaluation,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/eval_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-prov-retry-eval" \
  slurm/preflight_m1_provenance_screen.slurm)
evaluation_id=$(sbatch --parsable \
  --job-name=m1-prov-retry-eval \
  --dependency="afterok:$evaluation_preflight_id" \
  --array=0-2%3 \
  --output="$SCRATCH_ROOT/logs/m1-prov-retry-eval-%A_%a.out" \
  --error="$SCRATCH_ROOT/logs/m1-prov-retry-eval-%A_%a.err" \
  --export="$export_args" \
  slurm/eval_m1_provenance_screen.slurm)

echo "__ACQUISITION_PREFLIGHT_JOB_ID__=$acquisition_preflight_id"
echo "__ACQUISITION_ARRAY_JOB_ID__=$acquisition_id"
echo "__TRAINING_PREFLIGHT_JOB_ID__=$training_preflight_id"
echo "__TRAINING_ARRAY_JOB_ID__=$training_id"
echo "__EVALUATION_PREFLIGHT_JOB_ID__=$evaluation_preflight_id"
echo "__EVALUATION_ARRAY_JOB_ID__=$evaluation_id"
squeue -h -j "$acquisition_preflight_id,$acquisition_id,$training_preflight_id,$training_id,$evaluation_preflight_id,$evaluation_id" -o '%i %T %M %L %R %j'
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
cd "${SCRIPT_DIR}/.."
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
